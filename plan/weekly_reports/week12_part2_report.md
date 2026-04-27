# Project Part 2 - Weekly Progress Report - Week 12 (Apr 16, 2026)

> **Course**: Special CS Topic - Cloud Computing, Section 026
> **Student**: Chen Li (Solo)
> **Project**: Decentralized Health Monitoring System

---

## Work Completed This Week

1. **Built the dashboard** (`dashboard/`). The server (`server.py`) joins the P2P mesh as `role="dashboard"` *and* serves an HTTP/WebSocket front-end via `aiohttp`. The two halves share state through a small `Broadcaster` class that keeps a set of connected WebSocket clients and a rolling 200-event history. Three handlers — `on_sensor`, `on_anomaly`, `on_bc` — wrap inbound envelopes into JSON frames and fan them out to every connected browser.

2. **Built the dashboard front-end** (`dashboard/public/`): an `index.html` with five KPI tiles (HR / body temp / SpO₂ / running anomaly count / running on-chain count), a heart-rate sparkline rendered to `<canvas>`, a peer panel listing all live `PeerNode`s, an anomaly table, and a blockchain table whose `tx_hash` cells are linked to `https://sepolia.etherscan.io/tx/<hash>`. The WebSocket client auto-reconnects every 2 s, so a server restart does not require a browser refresh.

3. **Ran the first full end-to-end integration session** (2026-04-18 to 2026-04-19). Five PowerShell terminals: bootstrap → IoT → ML → BC → dashboard. The system ran for several hours, accumulating ~130 transactions on the Sepolia contract. Captured seven screenshots (`01_dashboard_fullview.png` through `07_etherscan_tx_success.png`) covering the dashboard, the five terminals, the Etherscan contract page, two pre-fix out-of-gas examples, the deployment transaction, and a representative post-fix successful `logAnomaly`.

4. **Wrote §1–§4 of the Final Report**:
   - §1 Introduction (motivation, goals, contributions, report structure)
   - §2 Related Work (centralised IoT platforms, P2P overlays, blockchain for healthcare, unsupervised anomaly detection)
   - §3 System Design and Architecture (the five roles, the message protocol, the trust model, the public-chain rationale, and §3.6 disclosing the BTP / py-libp2p substitution)
   - §4 Implementation Details (P2P framework, IoT simulator, ML pipeline, smart contract, BC submitter, dashboard)

5. **Set up the AWS S3 bucket** `chenli-cloud-final-2026` (us-east-1, block-all-public-access). Created an IAM user `cloud-final-app` with `AmazonS3FullAccess` for the BC node. The bucket is empty at this point — the archival code lands in Week 13.

---

## Planned Work for Next Week (Week 13 - Apr 23)

1. Wire the AWS S3 archival path into `bc_node.py` so every anomaly's raw JSON is stored off-chain before its hash is anchored on chain.
2. Move the trained Isolation Forest artefact to S3; modify `ml_node.py` to download it at startup.
3. Run a cloud-services rehearsal exercising every cloud component simultaneously.
4. Write §5 (Evaluation), §6 (Discussion), §7 (Conclusion) of the Final Report.
5. Generate the Final Presentation deck.

---

## Issues Encountered

- The Glassfish-compose dependency-condition `service_healthy` required adjusting the MySQL healthcheck timeout — the default 30 s was too aggressive on a fresh AWS EC2 t2.small. Raised to 60 s, problem solved.

---

## Key Learnings

- Writing the report's §3 (System Design) *before* §4 (Implementation) is the right order even though §4 contains "everything that's true". §3 forces you to argue about trust models and Web2/Web3 boundaries in the abstract; that argument is what convinces a reviewer the §4 implementation is the right shape.
- The "12-second click time" from anomaly to clickable Etherscan link is dominated by the Sepolia block time. Off-chain pipeline (sensor → ML → BC submission) is well under a second; the chain itself is the latency-determining hop.
