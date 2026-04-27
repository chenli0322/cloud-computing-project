"""
Blockchain P2P node.

Listens for MSG_ANOMALY from the P2P network.  For each anomaly:

  1. Uploads the full raw anomaly JSON to AWS S3
     (s3://$ANOMALY_S3_BUCKET/anomalies/<eventHash>.json) so an external
     auditor can later fetch the complete record, recompute its SHA-256,
     and verify it matches the on-chain hash.
  2. Submits HealthLog.logAnomaly() on Sepolia with the SHA-256 hash
     plus the device id and a short anomaly-kind string.
  3. Waits for inclusion, then broadcasts MSG_BC_LOGGED carrying the
     tx hash, block number, gas used, AND the S3 URI of the off-chain
     archive, so the Dashboard can render both the on-chain link and the
     off-chain raw record.

Requires env vars (via blockchain/.env):
    SEPOLIA_RPC_URL          Infura/Alchemy https endpoint
    PRIVATE_KEY              wallet that pays gas
    HEALTHLOG_ADDRESS        deployed contract address (or read from deployment.json)
    AWS_ACCESS_KEY_ID        IAM user with PutObject on the bucket
    AWS_SECRET_ACCESS_KEY    "
    AWS_REGION               default us-east-1
    ANOMALY_S3_BUCKET        target bucket (e.g. cl5725-health-monitor-anomalies)

If S3 env vars are missing the BC node still runs — it just skips the
archival step and logs a warning.  This keeps local development unblocked.
"""
from __future__ import annotations
import argparse
import asyncio
import json
import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware

sys.path.insert(0, str(Path(__file__).parent.parent / "p2p-network"))
from peer_node import PeerNode
from message import Envelope, MSG_ANOMALY, MSG_BC_LOGGED

THIS_DIR = Path(__file__).parent
DEPLOYMENT_PATH = THIS_DIR / "deployment.json"


class S3Archiver:
    """Uploads raw anomaly JSON to S3 before on-chain submission.

    The bucket name is read from ANOMALY_S3_BUCKET; the AWS credentials
    come from standard boto3 resolution (env vars, IAM role, ~/.aws/credentials).
    If boto3 isn't installed or the bucket env var isn't set, archival is
    silently disabled and the BC node continues without it.
    """

    def __init__(self):
        self.bucket = os.environ.get("ANOMALY_S3_BUCKET")
        self.region = os.environ.get("AWS_REGION", "us-east-1")
        self.client = None
        if not self.bucket:
            return
        try:
            import boto3
            self.client = boto3.client("s3", region_name=self.region)
        except ImportError:
            print("[bc] boto3 not installed; S3 archival disabled.")
            self.client = None
        except Exception as e:
            print(f"[bc] S3 client init failed: {e}; archival disabled.")
            self.client = None

    @property
    def enabled(self) -> bool:
        return self.client is not None and self.bucket is not None

    async def archive(self, ev: dict) -> str | None:
        """Upload the raw anomaly JSON; return the s3:// URI or None on failure."""
        if not self.enabled:
            return None
        event_hash_hex = ev.get("hash", "")
        if event_hash_hex.startswith("0x"):
            key_stem = event_hash_hex[2:]
        else:
            key_stem = event_hash_hex
        key = f"anomalies/{key_stem}.json"
        body = json.dumps(ev, sort_keys=True, separators=(",", ":")).encode("utf-8")

        def _put():
            self.client.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=body,
                ContentType="application/json",
            )

        try:
            await asyncio.to_thread(_put)
            return f"s3://{self.bucket}/{key}"
        except Exception as e:
            print(f"[bc] S3 archive failed for {key_stem[:12]}: {e}")
            return None


def _load_deployment() -> tuple[str, list]:
    """Return (contract_address, abi)."""
    load_dotenv(THIS_DIR / ".env")
    addr = os.environ.get("HEALTHLOG_ADDRESS") or ""
    abi = None
    if DEPLOYMENT_PATH.exists():
        with open(DEPLOYMENT_PATH) as f:
            d = json.load(f)
            addr = addr or d["address"]
            abi = d.get("abi")
    if not addr:
        raise RuntimeError(
            "HealthLog contract address not found. Deploy first "
            "(see blockchain/README.md), or set HEALTHLOG_ADDRESS in .env."
        )
    if abi is None:
        abi_path = THIS_DIR / "artifacts" / "contracts" / "HealthLog.sol" / "HealthLog.json"
        if not abi_path.exists():
            raise RuntimeError(
                f"ABI file not found at {abi_path}. Run `npx hardhat compile`."
            )
        with open(abi_path) as f:
            abi = json.load(f)["abi"]
    return Web3.to_checksum_address(addr), abi


def _make_web3() -> tuple[Web3, object]:
    """Return (w3, account)."""
    rpc = os.environ["SEPOLIA_RPC_URL"]
    pk = os.environ["PRIVATE_KEY"]
    if pk.startswith("0x"):
        pk = pk[2:]
    w3 = Web3(Web3.HTTPProvider(rpc))
    w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
    acct = w3.eth.account.from_key(pk)
    return w3, acct


def _classify_anomaly(ev: dict) -> str:
    hr = ev.get("heart_rate", 0)
    bt = ev.get("body_temp", 0)
    sp = ev.get("spo2", 0)
    if hr >= 120:
        return "hr_high"
    if hr <= 50:
        return "hr_low"
    if bt >= 38.0:
        return "temp_high"
    if sp <= 92:
        return "spo2_low"
    return "multi_metric"


class NonceManager:
    """Serializes on-chain submissions so we never reuse a nonce."""
    def __init__(self, w3: Web3, address: str):
        self.w3 = w3
        self.address = address
        self.lock = asyncio.Lock()
        self.next_nonce: int | None = None

    async def get_nonce(self) -> int:
        if self.next_nonce is None:
            self.next_nonce = await asyncio.to_thread(
                self.w3.eth.get_transaction_count, self.address, "pending"
            )
        n = self.next_nonce
        self.next_nonce += 1
        return n

    def rollback(self):
        if self.next_nonce is not None and self.next_nonce > 0:
            self.next_nonce -= 1


async def _submit(w3: Web3, acct, contract, ev: dict, nonces: "NonceManager") -> dict:
    """Submit the anomaly hash to the chain, return receipt summary."""
    event_hash_hex = ev["hash"]
    if event_hash_hex.startswith("0x"):
        eh_bytes = bytes.fromhex(event_hash_hex[2:])
    else:
        eh_bytes = bytes.fromhex(event_hash_hex)
    device_id = ev.get("device_id", "unknown")
    kind = _classify_anomaly(ev)

    # Acquire nonce under a lock so parallel calls don't collide.
    async with nonces.lock:
        nonce = await nonces.get_nonce()

    def _send(nonce_val: int):
        tx = contract.functions.logAnomaly(eh_bytes, device_id, kind).build_transaction(
            {
                "from": acct.address,
                "nonce": nonce_val,
                "gas": 250_000,
                "maxFeePerGas": w3.to_wei("5", "gwei"),
                "maxPriorityFeePerGas": w3.to_wei("1", "gwei"),
                "chainId": 11155111,
            }
        )
        signed = w3.eth.account.sign_transaction(tx, acct.key)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
        rcpt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=180)
        return tx_hash.hex(), rcpt

    try:
        tx_hash, rcpt = await asyncio.to_thread(_send, nonce)
    except Exception:
        nonces.rollback()
        raise
    if int(rcpt.status) != 1:
        raise RuntimeError(f"tx reverted: {tx_hash} block={rcpt.blockNumber}")
    return {
        "tx_hash": tx_hash if tx_hash.startswith("0x") else "0x" + tx_hash,
        "block_number": rcpt.blockNumber,
        "gas_used": rcpt.gasUsed,
        "status": int(rcpt.status),
        "anomaly_kind": kind,
        "event_hash": event_hash_hex,
        "device_id": device_id,
        "ts_submitted": time.time(),
    }


async def _main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, required=True)
    ap.add_argument("--bootstrap", default="127.0.0.1:9000")
    args = ap.parse_args()

    load_dotenv(THIS_DIR / ".env")
    addr, abi = _load_deployment()
    w3, acct = _make_web3()
    contract = w3.eth.contract(address=addr, abi=abi)
    print(f"[bc] wallet={acct.address}")
    print(f"[bc] contract={addr}")
    bal = w3.eth.get_balance(acct.address)
    print(f"[bc] balance={w3.from_wei(bal, 'ether')} ETH")

    node = PeerNode(
        host=args.host, port=args.port, role="bc",
        node_id=f"bc-{args.port}", bootstrap=args.bootstrap,
    )
    nonces = NonceManager(w3, acct.address)
    archiver = S3Archiver()
    if archiver.enabled:
        print(f"[bc] S3 archival enabled: bucket={archiver.bucket} region={archiver.region}")
    else:
        print("[bc] S3 archival disabled (set ANOMALY_S3_BUCKET in .env to enable)")

    # Simple de-dup across restarts (in-memory).
    seen: set[str] = set()

    async def on_anomaly(env: Envelope):
        ev = env.payload
        h = ev.get("hash")
        if not h or h in seen:
            return
        seen.add(h)
        node.log.info("submitting anomaly %s to Sepolia ...", h[:16])
        try:
            # 1) Archive raw JSON to S3 first so the off-chain record exists
            #    *before* the on-chain hash is permanent.
            s3_uri = await archiver.archive(ev)
            if s3_uri:
                node.log.info("archived raw anomaly to %s", s3_uri)
            # 2) Submit hash to chain.
            summary = await _submit(w3, acct, contract, ev, nonces)
            if s3_uri:
                summary["s3_uri"] = s3_uri
            node.log.info(
                "on-chain block=%d tx=%s", summary["block_number"], summary["tx_hash"]
            )
            await node.broadcast(MSG_BC_LOGGED, summary)
        except Exception as e:
            node.log.error("submission failed: %s", e)

    node.on(MSG_ANOMALY, on_anomaly)
    await node.start()


if __name__ == "__main__":
    try:
        asyncio.run(_main())
    except KeyboardInterrupt:
        pass
