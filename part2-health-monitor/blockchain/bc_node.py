"""
Blockchain P2P node.

Listens for MSG_ANOMALY from the P2P network.  For each anomaly, submits a
transaction to HealthLog.logAnomaly() on Sepolia, waits for inclusion, and
broadcasts MSG_BC_LOGGED with the tx hash so the Dashboard can display it.

Requires env vars (via blockchain/.env):
    SEPOLIA_RPC_URL
    PRIVATE_KEY
    HEALTHLOG_ADDRESS
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
            summary = await _submit(w3, acct, contract, ev, nonces)
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
