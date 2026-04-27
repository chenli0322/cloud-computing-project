# Part 2 — Decentralized Health Monitoring System

## Weekly Progress Reports — Spring 2026 Course Project

> **Course**: Special CS Topic — Cloud Computing, Section 026
> **Instructor**: Prof. Jean-Claude Franchitti
> **Student**: Chen Li (NetID: cl5725) — solo team
> **Repository**: <https://github.com/chenli0322/cloud-computing-project>

---

## Table of Contents

- [Project Part 2 - Weekly Progress Report - Week 5 (Feb 26, 2026)](#project-part-2---weekly-progress-report---week-5-feb-26-2026)
- [Project Part 2 - Weekly Progress Report - Week 6 (Mar 5, 2026)](#project-part-2---weekly-progress-report---week-6-mar-5-2026)
- [Project Part 2 - Weekly Progress Report - Week 7 (Mar 10, 2026)](#project-part-2---weekly-progress-report---week-7-mar-10-2026)
- [Project Part 2 - Weekly Progress Report - Week 8 (Mar 19, 2026)](#project-part-2---weekly-progress-report---week-8-mar-19-2026)
- [Project Part 2 - Weekly Progress Report - Week 9 (Mar 26, 2026)](#project-part-2---weekly-progress-report---week-9-mar-26-2026)
- [Project Part 2 - Weekly Progress Report - Week 10 (Apr 2, 2026)](#project-part-2---weekly-progress-report---week-10-apr-2-2026)
- [Project Part 2 - Weekly Progress Report - Week 11 (Apr 9, 2026)](#project-part-2---weekly-progress-report---week-11-apr-9-2026)
- [Project Part 2 - Weekly Progress Report - Week 12 (Apr 16, 2026)](#project-part-2---weekly-progress-report---week-12-apr-16-2026)
- [Project Part 2 - Weekly Progress Report - Week 13 (Apr 23, 2026)](#project-part-2---weekly-progress-report---week-13-apr-23-2026)

---

# Project Part 2 - Weekly Progress Report - Week 5 (Feb 26, 2026)

> **Course**: Special CS Topic - Cloud Computing, Section 026
> **Student**: Chen Li (Solo)
> **Project**: Decentralized Health Monitoring System

---

## Work Completed This Week

1. **Defined project concept**: Decentralized Health Monitoring System — an innovative cloud application that combines IoT, ML, and Blockchain technologies with a P2P architecture for real-time health data monitoring and anomaly detection.

2. **Identified 3 PaaS technologies**:
   - **IoT**: Simulated health sensors (heart rate, body temperature, SpO2) publishing data via MQTT to Azure IoT Hub
   - **AI/ML**: Anomaly detection model using scikit-learn (e.g., heart rate > 120 or < 50 triggers alert)
   - **Blockchain**: Ethereum smart contracts for immutable health event logging

3. **Planned multi-cloud deployment**:
   - **Azure**: IoT Hub (sensor data ingestion) + ML model hosting
   - **AWS**: EC2 (compute instances) + S3 (data storage)

4. **Designed P2P architecture**: Using libp2p / IPFS for decentralized health data distribution across multiple peer nodes.

5. **Created project directory structure**: Organized folders for iot-simulator, ml-model (with data/ and models/ subdirectories), blockchain (contracts/ and scripts/), p2p-network, and dashboard.

6. **Team composition**: Solo project (Chen Li). Will notify professor about solo status.

---

## Planned Work for Next Week (Week 6 - Mar 5)

1. Finalize team composition (confirm solo with professor)
2. Prepare midterm project proposal presentation (10-15 minutes):
   - System architecture diagram
   - Technology stack justification
   - Development timeline
   - Demo plan
3. Begin detailed system architecture design:
   - Data flow diagrams
   - Component interaction specifications
   - Cloud service selection rationale

---

## Issues Encountered

- Still searching for team members — may proceed as solo project. Professor confirmed solo is acceptable.

---

## Key Design Decisions

- Chose health monitoring as the domain due to strong alignment with course content (Sessions 3 and 5 covered healthcare IoT extensively).
- Selected Azure IoT Hub over AWS IoT Core for the primary IoT platform due to better MQTT support and integration with ML services.
- Planning to use simulated sensor data (not real hardware) to keep the project scope manageable while still demonstrating full pipeline functionality.
- P2P architecture adds genuine innovation beyond standard cloud deployment.

---

# Project Part 2 - Weekly Progress Report - Week 6 (Mar 5, 2026)

> **Course**: Special CS Topic - Cloud Computing, Section 026
> **Student**: Chen Li (Solo)
> **Project**: Decentralized Health Monitoring System

---

## Work Completed This Week

1. **Presented the Part 2 idea in the Midterm Proposal Presentation** (2026-03-05). The Part-2 portion of the deck described:
   - **Problem**: today's IoT health platforms are single-tenant, single-trust, and a single point of failure.
   - **Goal**: distribute processing across independent peers + anchor the audit log on a public chain so a verifier can detect tampering without trusting the operator.
   - **Architecture sketch** (six-slide version): three node types — IoT, ML, Blockchain — communicating over a P2P mesh; a separate dashboard.
   - **Three PaaS technologies**: IoT (Azure IoT Hub), ML (Isolation Forest), Blockchain (Ethereum smart contract).
   - **Two cloud platforms** (minimum per Session 5): Azure (IoT Hub) + AWS (storage + node hosting). The midterm proposal said the smart contract would run on a local Ganache; the instructor's later (Session 9) guidance moved this to Sepolia public testnet.

2. **Captured the instructor's feedback** for follow-up:
   - Bootstrap node looks like a single point of failure in the diagram → addressed in §6.6 of the Final Report and via peer-driven discovery in the implementation.
   - "Use BTP or libp2p for the P2P layer" → after Week 8 investigation, neither was production-ready; built an equivalent broker-less overlay (disclosed in §3.6 of the Final Report).

3. **No code work for Part 2 this week** — the focus was the proposal and the Part-1 install push. Part-2 implementation begins in Week 8.

---

## Planned Work for Next Week (Week 7 - Mar 12)

1. Continue the Part 1 install push — Part 2 implementation deferred to Week 8.
2. Begin reading the BTP and libp2p source repositories to evaluate suitability.

---

## Issues Encountered

- The midterm proposal claimed BTP would be used. This was based on the Session-5 lecture recommendation. Week-8 investigation found BTP's public repos are archived (last update 2018) and `py-libp2p` is alpha-quality. The substitution to a self-implemented equivalent overlay is documented in §3.6 of the Final Report.

---

## Key Learnings

- A midterm proposal is allowed to be wrong — the instructor explicitly said pivots are expected. What matters is that the deltas are *disclosed* in the final deliverable rather than papered over. The Final Report's §6.7 is built around that principle.
- "Two cloud platforms is enough" (instructor, Session 5) is liberating: it means the architecture can use Azure + AWS + Sepolia and still be over-spec, leaving room for the project to evolve.

---

# Project Part 2 - Weekly Progress Report - Week 7 (Mar 10, 2026)

> **Course**: Special CS Topic - Cloud Computing, Section 026
> **Student**: Chen Li (Solo)
> **Project**: Decentralized Health Monitoring System

---

## Work Completed This Week

1. **Focused entirely on Part 1 completion** — this week's effort was dedicated to finishing the Docker containerization and AWS cloud deployment of the ArchNav legacy application (Part 1). Part 2 development has not started yet.

2. **Reviewed P2P architecture requirements** — confirmed that the system must use true peer-to-peer communication (BTP or libp2p), not message brokers like Kafka or RabbitMQ (per Professor Franchitti's Session 5 guidance).

---

## Planned Work for Next Week (Week 8 - Mar 17)

1. **Research BTP P2P framework** — study the Python/Java implementations on GitHub, understand node discovery, direct messaging, and master election mechanisms
2. **Set up Azure IoT Hub** — create IoT Hub instance on Azure portal, register a simulated device
3. **Write IoT sensor simulator** — Python script generating heart rate, body temperature, and SpO2 data via MQTT
4. **Begin P2P node implementation** — bootstrap node and peer node with basic direct communication capability

---

## Issues Encountered

- No Part 2 issues this week — development has not started yet.
- Time constraint: Part 1 Docker debugging and cloud deployment took the full week.

---

## Key Design Decisions

- Part 2 development will begin next week now that Part 1 is fully deployed and documented.
- Will prioritize P2P framework selection (BTP vs libp2p) as the first task, since it is the architectural backbone of the entire system.
- Plan to use 3 PaaS technologies: IoT (Azure IoT Hub), ML (scikit-learn anomaly detection), Blockchain (Ethereum/Ganache smart contracts).

---

# Project Part 2 - Weekly Progress Report - Week 8 (Mar 19, 2026)

> **Course**: Special CS Topic - Cloud Computing, Section 026
> **Student**: Chen Li (Solo)
> **Project**: Decentralized Health Monitoring System

---

## Work Completed This Week

1. **Investigated the BTP framework** that the instructor recommended in Session 5. Found two GitHub repositories — Java and Python implementations — both archived since 2018, with no recent issues or pull requests. The Python implementation has substantial gaps (no leader-election primitive, only a partial peer-discovery layer). Conclusion: BTP cannot serve as a foundation for a working system in our timeline.

2. **Investigated `py-libp2p`** as the alternative the instructor mentioned. Latest release is `v0.2.x`, marked alpha; the Kademlia DHT implementation is incomplete and the project's documentation explicitly cautions against production use. Migrating to it would be a research effort, not a delivery.

3. **Decision made**: build an equivalent broker-less overlay in Python from first principles, satisfying the same architectural properties the instructor named (no central broker, peer-driven discovery, leader election). This decision is documented in §3.6 of the Final Report.

4. **Created the project skeleton** for Part 2 under `part2-health-monitor/`:
   - `p2p-network/` — will hold `peer_node.py`, `bootstrap_node.py`, `message.py`
   - `iot-simulator/`, `ml-model/`, `blockchain/`, `dashboard/` — placeholders for the four role implementations
   - `docs/` — design notes
   - `screenshots/` — for evaluation evidence

5. **Drafted the message protocol** — a 4-byte big-endian length prefix followed by a UTF-8 JSON object with `{type, sender_id, role, msg_id, ts, payload}`. The framing mirrors what countless production microservices use; there is no benefit to a custom binary format here.

---

## Planned Work for Next Week (Week 9 - Mar 26)

1. Implement `message.py` (envelope encoder/decoder, `read_envelope` / `write_envelope`).
2. Implement `peer_node.py` (TCP server, peer table, broadcast / send_to, bully election).
3. Implement `bootstrap_node.py` (just a `PeerNode` with `role="bootstrap"` and a fixed port).
4. Begin sketching the IoT simulator (synthetic sensor distributions for HR / body temp / SpO₂).

---

## Issues Encountered

- The midterm proposal claimed BTP would be the framework, which on closer inspection is not realistic. This is a legitimate substitution (the instructor named libp2p as equivalent) and will be disclosed openly in §3.6 of the report rather than papered over.

---

## Key Learnings

- "Use this framework" advice from class is best treated as "use this *kind* of framework" — the specific tool may not exist or may not be ready. The architectural properties (broker-less, gossip-discovery, leader election) are what actually matter, and they are easier to implement directly than to adopt a half-maintained library.
- A 4-byte length prefix + JSON is sufficient for a 5-node demo; chasing protobuf or msgpack at this scale is premature optimisation.

---

# Project Part 2 - Weekly Progress Report - Week 9 (Mar 26, 2026)

> **Course**: Special CS Topic - Cloud Computing, Section 026
> **Student**: Chen Li (Solo)
> **Project**: Decentralized Health Monitoring System

---

## Work Completed This Week

1. **Implemented `message.py`** (~70 lines). Defines `Envelope` (a `@dataclass` with `type`, `sender_id`, `role`, `msg_id`, `ts`, `payload`), the `to_bytes` encoder, `from_json` decoder, and the async helpers `read_envelope` / `write_envelope` that operate on `asyncio.StreamReader/StreamWriter` pairs. Reader rejects payloads above 8 MiB to prevent malformed-peer-induced unbounded allocations.

2. **Implemented `peer_node.py`** (~280 lines). A generic `PeerNode` class: opens a TCP server on `(host, port)`, maintains a `peers: dict[node_id -> (host, port)]` table and a `writers: dict[node_id -> StreamWriter]` table, supports `broadcast(msg_type, payload)` and `send_to(peer_id, msg_type, payload)`, and routes inbound envelopes through a `handlers: dict[msg_type -> coroutine]` registry. Includes a 15-second keepalive loop that broadcasts `MSG_PING` to flush dead sockets.

3. **Implemented bully-style master election** (`_start_election`): the candidate broadcasts `MSG_ELECT`, waits 2 s, and if no peer with a higher `node_id` has objected by then, broadcasts `MSG_MASTER` to claim the role. Election re-fires automatically when the current master disappears.

4. **Implemented `bootstrap_node.py`** as a thin wrapper around `PeerNode(role="bootstrap", node_id="bootstrap-0")` on a fixed port (default 9000). Crucial property: any `PeerNode` will answer an incoming `MSG_HELLO` with `MSG_PEERS` containing its current view of the membership — *not just the bootstrap node*. This is what makes the bootstrap a discovery aid rather than a single point of failure (the §6.6 answer to the midterm SPOF concern).

5. **Implemented `sensor_simulator.py`**: a `SensorSimulator` that produces clipped Gaussian readings around resting-adult ranges (HR ~ N(75, 8) clipped [40, 130], body temp ~ N(36.7, 0.25) clipped [35.5, 38.0], SpO₂ ~ N(98, 0.8) clipped [90, 100]), with a 5–8 % anomaly-injection probability that draws values from one of four pathological-range bands (`hr_high`, `hr_low`, `temp_high`, `spo2_low`). The injection flag is the ground-truth label used later for ML evaluation.

6. **Set up the Azure IoT Hub instance** `ChenLi-iot-final-2026.azure-devices.net` (free-tier F1) and registered the simulated device `sim-device-001`. Captured the device connection string for the IoT-node `.env`.

---

## Planned Work for Next Week (Week 10 - Apr 2)

1. Implement the IoT P2P node (`iot_node.py`) that drives the sensor simulator and broadcasts `MSG_SENSOR`.
2. Add the Azure IoT Hub MQTT/8883 bridge as an optional path inside the IoT node.
3. Train the Isolation Forest model (`train_model.py`).
4. Begin the smart-contract design (`HealthLog.sol`).

---

## Issues Encountered

- None this week. The decision to build the overlay from first principles is paying off: ~350 lines so far and every property the instructor named is testable in isolation.

---

## Key Learnings

- The bully algorithm is more than enough for a five-peer system. Pulling in Raft or Paxos at this scale would be ~1 000 LOC of dependency for behaviour the human eye can't distinguish from `_start_election`'s 20 lines.
- A canonical-JSON encoding (`sort_keys=True, separators=(",", ":")`) is what makes hashes deterministic across processes — this becomes a load-bearing decision in Week 10 when the ML node starts hashing anomaly events for on-chain anchoring.

---

# Project Part 2 - Weekly Progress Report - Week 10 (Apr 2, 2026)

> **Course**: Special CS Topic - Cloud Computing, Section 026
> **Student**: Chen Li (Solo)
> **Project**: Decentralized Health Monitoring System

---

## Work Completed This Week

1. **Implemented `iot_node.py`** that joins the P2P mesh as `role="iot"`, samples the sensor every `--interval` seconds (default 1.5 s), and broadcasts `MSG_SENSOR` envelopes. The node also publishes the *raw* reading to **Azure IoT Hub** over MQTT/8883 — this is the IoT-PaaS path. The bridge is implemented in `_maybe_azure_publisher` and is engaged when `AZURE_IOT_CONN_STR` is set in `iot-simulator/.env`.

2. **Implemented the SAS-token derivation** for Azure IoT Hub authentication (`HMAC-SHA256` over `<host>/devices/<device-id>` with the device's primary shared-access-key). The token is computed on the local machine — no Azure SDK dependency is needed beyond `paho-mqtt`. Refreshing the token is left to a future iteration; for the demo a 1-hour TTL is sufficient.

3. **Trained the Isolation Forest detector** in `train_model.py`: built two synthetic datasets (5 000 healthy training samples, 1 500 held-out test samples) using `SensorSimulator(anomaly_rate=0.1, seed=…)` so labels and features come from the same distribution but no leakage between train and test. Fitted with `n_estimators=200`, `contamination=0.1`, `random_state=42`. Reported on the test set:

   | Class       | Precision | Recall | F1   |
   |-------------|-----------|--------|------|
   | Normal      | 0.99      | 0.99   | 0.99 |
   | Anomaly     | 0.90      | 0.98   | 0.94 |
   | **Overall** | —         | —      | **0.99** |

4. **Implemented `ml_node.py`**: registers a single `MSG_SENSOR` handler that runs each reading through `clf.predict(...)` and `clf.decision_function(...)`. When the verdict is `-1`, the node assembles an *anomaly event* (raw reading + score + originating IoT node id + timestamp), computes a SHA-256 hash over the canonical-JSON serialisation of that event, attaches the hash, and broadcasts `MSG_ANOMALY`. The hash is what later gets anchored on chain.

5. **Drafted `HealthLog.sol`** (Solidity 0.8.24): an append-only registry with an `entries[]` array and an `indexOfHash` mapping for duplicate rejection. Single mutating function `logAnomaly(eventHash, deviceId, anomalyKind)`. Three view helpers (`exists`, `total`, `getEntry`) and one indexed event (`AnomalyLogged`). Compiled cleanly with the Hardhat toolchain (`npx hardhat compile`).

---

## Planned Work for Next Week (Week 11 - Apr 9)

1. Deploy `HealthLog.sol` to Sepolia using Hardhat.
2. Implement the BC submitter (`bc_node.py`): listen for `MSG_ANOMALY`, sign and submit `logAnomaly` to Sepolia, broadcast `MSG_BC_LOGGED` on confirmation.
3. Anticipate the nonce-collision and gas-limit issues that real-chain submission will surface.

---

## Issues Encountered

- The `paho-mqtt` library on Python 3.12 emits a `DeprecationWarning` for the legacy callback signatures; harmless but verbose. Suppressed in the Azure publisher path with a `warnings.filterwarnings` call.

---

## Key Learnings

- Isolation Forest gives you 99 %-accuracy / 98 %-recall on cleanly-separated synthetic data with no tuning. That is exactly what an unsupervised baseline should look like; if the numbers had been worse, the data is more likely the cause than the algorithm.
- The Azure IoT Hub MQTT path is a 30-line implementation if you write the SAS token by hand. The official Microsoft SDK adds 30 MB of dependencies for the same outcome.

---

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

---

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

---

# Project Part 2 - Weekly Progress Report - Week 13 (Apr 23, 2026)

> **Course**: Special CS Topic - Cloud Computing, Section 026
> **Student**: Chen Li (Solo)
> **Project**: Decentralized Health Monitoring System

---

## Work Completed This Week

This was the cloud-services rehearsal week. Every cloud component the system claims to use was actually exercised in a single coordinated run on **2026-04-26**, and the resulting evidence is what populates §5.7 of the Final Report.

1. **Implemented `S3Archiver` in `bc_node.py`**. Before any transaction touches the chain, the BC node uploads the full anomaly JSON to `s3://chenli-cloud-final-2026/anomalies/<event_hash>.json` using `boto3.client("s3").put_object(...)` with a deterministic canonical-JSON body. The successful S3 URI is attached to the outbound `MSG_BC_LOGGED` envelope so the dashboard can render it next to the Etherscan link, giving graders a one-click round-trip from on-chain entry to off-chain raw record.

2. **Moved the ML artefact to S3**. `ml-model/upload_model_to_s3.py` was used once to push `models/anomaly_model.joblib` (1.6 MiB) to `s3://chenli-cloud-final-2026/models/`. Modified `ml_node.py` to read `MODEL_S3_URI` from `.env`; when set, the node downloads the model via `boto3` at startup and `joblib.load`s it from a temp file. This makes the model artefact "on cloud" — training can happen anywhere, but the consumed artefact is always pulled from S3.

3. **Hardened the Azure IoT Hub bridge**. Rewrote `_maybe_azure_publisher` to load the connection string from `iot-simulator/.env`, log connection success / failure, emit a periodic running message-counter, and tolerate transient network drops. Verified end-to-end: the IoT node logged `azure: published 310 messages so far` during the rehearsal; the Azure portal's "Device-to-cloud messages" chart confirmed **634** total messages received that day (combining the rehearsal and a baseline-validation run).

4. **Ran the cloud-services rehearsal**. Five processes spun up; the system produced **18 confirmed Sepolia transactions** in blocks 10 739 301 → 10 739 320 (every one `Status: Success`), **29 anomaly archives in S3** (totalling 6 751 bytes), and **310** mirrored Azure IoT Hub messages. Cost: zero, paid with Sepolia testnet ETH and free-tier Azure / AWS quotas.

5. **Verified the audit chain end-to-end**. Pulled object `303d3f2164f169...0bad113a.json` from S3 with `boto3.client("s3").get_object(...)`; recomputed `sha256(canonical_json(payload_without_hash))` over the body; confirmed it matches `0x303d3f2164f169...0bad113a` — the same hash that was anchored at block `10739301` by transaction `0xe1ebf113bef9fd1f7fdc7d734f87da8b54d1c7fc724c7044da874965270e5b8b`. This is the concrete form of the tamper-evident guarantee claimed in §3.4 of the report: any external party can verify any anomaly record without trusting the operator.

6. **Wrote §5 (Evaluation), §6 (Discussion), §7 (Conclusion + Future Work) and References** of the Final Report. Added §6.6 "Addressing Midterm Feedback (Bootstrap SPOF)" with the three-layered argument that the bootstrap is not actually a single point of failure (off the data path, peer-driven discovery, multi-bootstrap support). Added §6.7 — a side-by-side table of every midterm proposal claim vs the delivered system, with the rationale for each delta. Final report is now 594 lines / ~9 600 words.

7. **Generated the Final Presentation deck** as `final-report/Cloud_Computing_Final_Presentation.pptx` using `python-pptx` from the script `generate_final_ppt.py`. Twenty-three slides total — one title slide, eight Part-1 slides, thirteen Part-2 slides, one closing — each with speaker notes.

8. **Captured five new screenshots** from the rehearsal: `08_azure_iot_hub_metrics.png`, `09_s3_bucket_anomalies_listing.png`, `10_s3_anomaly_json_content.png`, `11_etherscan_contract_154tx.png`, `12_etherscan_tx_success_detail.png`. These join the original seven from the integration session for a total of 12 evidence figures embedded in §5 of the report.

---

## Planned Work for Next Week (Week 14 - Final Demo)

1. Final-demo dry run against the live system.
2. Verify the EC2 instance is up, the Sepolia wallet has ≥0.01 ETH, the Azure subscription is active, and the S3 bucket is reachable.
3. Pre-open browser tabs (dashboard / Azure portal / S3 console / Etherscan contract / Etherscan single-tx).

---

## Issues Encountered

- The IAM user `cloud-final-app` initially had only `AmazonS3FullAccess`, which prevented the EC2 launcher script from working. Attached `AmazonEC2FullAccess` for the demo period; will revoke or delete the user after the grade is in.
- Local Python's stdout encoding (`gbk` on Windows) crashed when streaming Glassfish's apt-install output containing non-ASCII certificate names. Rerun with `python -u` and `errors='replace'` resolved it.

---

## Key Learnings

- "Audit-chain works end-to-end" is the single most powerful claim this project can demonstrate. Showing the verification *live* — pull from S3, recompute, match — converts an architectural diagram into a runnable proof. This is the killer slide of the Final Presentation.
- A free-tier S3 + free-tier Azure IoT Hub + Sepolia testnet ETH is enough to demonstrate a hybrid Web2/Web3 cloud architecture at zero real-money cost. The friction is entirely in the API plumbing, which is exactly where the educational value lives.

---

## Public URLs and Identifiers (for grading)

- **Live ArchNav (Part 1)**: `http://3.88.156.91:9999/archemy/faces/login.jspx`
- **HealthLog contract (Part 2)**: `0x89983910f6AE98Ea081356148B433cA3C6de283B` on Sepolia
  - <https://sepolia.etherscan.io/address/0x89983910f6AE98Ea081356148B433cA3C6de283B>
- **GitHub repository (both parts)**: <https://github.com/chenli0322/cloud-computing-project>
- **Audit-chain reference transaction**: `0xe1ebf113bef9fd1f7fdc7d734f87da8b54d1c7fc724c7044da874965270e5b8b` at block `10 739 301`

---

## Project Repository and Live Resources

- **GitHub repository (full source)**: <https://github.com/chenli0322/cloud-computing-project>
- **Final Report**: `part2-health-monitor/docs/final_report.md` (594 lines, 9 sections, 13 references)
- **Final Presentation deck**: `final-report/Cloud_Computing_Final_Presentation.pptx` (23 slides with speaker notes)
- **HealthLog smart contract (Sepolia)**: `0x89983910f6AE98Ea081356148B433cA3C6de283B`
  - Etherscan: <https://sepolia.etherscan.io/address/0x89983910f6AE98Ea081356148B433cA3C6de283B>
- **AWS S3 off-chain audit store**: `s3://chenli-cloud-final-2026/anomalies/`
- **Azure IoT Hub**: `ChenLi-iot-final-2026.azure-devices.net` (free-tier F1)
- **Audit-chain reference transaction**: `0xe1ebf113bef9fd1f7fdc7d734f87da8b54d1c7fc724c7044da874965270e5b8b` at block `10 739 301`

*End of weekly progress reports for Part 2.*
