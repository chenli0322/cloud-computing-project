# Project Part 2 - Weekly Progress Report - Week 11 (Apr 9, 2026)

> **Course**: Special CS Topic - Cloud Computing, Section 026
> **Student**: Chen Li (Solo)
> **Project**: Decentralized Health Monitoring System

---

## Work Completed This Week

1. **Configured Hardhat for Sepolia** in `blockchain/hardhat.config.js`: registered the `sepolia` network with the Infura RPC URL from `.env`, the deployer account derived from `PRIVATE_KEY`, and the optimizer (200 runs).

2. **Deployed `HealthLog.sol` to Sepolia** with `npx hardhat run scripts/deploy.js --network sepolia`. The deployment transaction `0x5a39da1f86c8ef281413ee7e2996e039a1b9de9ae6c2926923e07b038f3f7496` was mined into block `10687227` with `Status: Success`. Contract address: `0x89983910f6AE98Ea081356148B433cA3C6de283B`. Deployment cost: ~0.0007 ETH on Sepolia. The deployment artefact (address, ABI, deploy block) is written to `deployment.json` for the Python BC node to consume.

3. **Implemented `bc_node.py`**: subscribes to `MSG_ANOMALY`, classifies the anomaly into a short `kind` string (`hr_high`, `hr_low`, `temp_high`, `spo2_low`, `multi_metric`), and calls `HealthLog.logAnomaly(eventHash, deviceId, kind)` via `web3.py`. After the receipt is mined with `status == 1`, broadcasts `MSG_BC_LOGGED` carrying the tx hash, block number, gas used, and anomaly kind.

4. **Hit the predicted real-chain problems** during the first integration runs:
   - **Nonce collision under concurrent submission** — when two anomalies arrived within ~1 second, the second `eth_sendRawTransaction` was rejected with `nonce too low`. Two coroutines were both reading the same `pending` nonce from the RPC. Fixed by introducing a `NonceManager` class with an `asyncio.Lock` + a locally-cached `next_nonce` integer, plus a `rollback()` for failed local submissions.
   - **Out-of-gas reverts on `logAnomaly`** — the original 180 000 gas limit was below the actual cost (~166 000 gas including dynamic-string slots and event topics). Raised to 250 000 (~33 % headroom).
   - **maxFeePerGas waste** — initially set to 30 gwei, but Sepolia's actual base fee was 1–2 gwei. Lowered to 5 gwei. Per-tx cost dropped from ~0.000363 ETH to ~0.000167 ETH.

5. **Patched the dashboard-side bug** where reverted transactions were being shown as "logged on-chain" because the BC node was broadcasting `MSG_BC_LOGGED` on any returned receipt. Added an explicit `if int(rcpt.status) != 1: raise RuntimeError(...)` guard in `_submit`.

---

## Planned Work for Next Week (Week 12 - Apr 16)

1. Build the dashboard (HTML SPA + WebSocket bridge in `dashboard/server.py`).
2. Run the first end-to-end integration session against Sepolia.
3. Begin the Final Report's §3 (System Design) and §4 (Implementation).

---

## Issues Encountered

- All three of the engineering bugs above. Each is documented as §6.1 / §6.2 / §6.3 of the Final Report with symptom / diagnosis / fix narrative. Each was caught by running against the real public chain rather than a local Ganache simulator — exactly the value the instructor flagged when nudging us toward Sepolia in Session 9 (2026-04-16).

---

## Key Learnings

- Real public-chain submission is qualitatively different from local Ganache. Nonce semantics, EIP-1559 fee economics, and revert semantics all surface only when you pay real gas to a real node. The bugs in §6 of the report would not have appeared on a local simulator.
- A `NonceManager` is one of those abstractions where the right size is ~20 lines: a lock, a cached integer, an increment, a rollback. Anything bigger and you're over-engineering; anything smaller and you have a race.
