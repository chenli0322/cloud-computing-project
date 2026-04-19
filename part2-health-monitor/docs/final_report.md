# A Decentralized Health Monitoring System on a Hybrid Web2/Web3 Cloud Architecture

**Li Chen** (NetID: cl5725) — *New York University*
*Special CS Topic — Cloud Computing (Section 026)*
*Instructor: Prof. Jean-Claude Franchitti*
*Spring 2026 Final Report*

---

## Abstract

We present a decentralized health monitoring system that combines four cloud-computing paradigms into a single end-to-end pipeline: a broker-less peer-to-peer (P2P) overlay, simulated Internet-of-Things (IoT) wearables, a machine-learning (ML) anomaly detector, and an Ethereum smart contract deployed on the public Sepolia test network. The system follows a hybrid Web2 + Web3 design: raw physiological data flows in real time over a Web2 socket-based P2P network, while only the cryptographic *fingerprint* (a SHA-256 hash) of each ML-flagged anomaly is written to the blockchain, providing a tamper-evident audit log without the latency and cost of putting raw data on-chain. A browser dashboard aggregates live sensor traces, ML verdicts, peer-network state, and confirmed on-chain transactions through a single WebSocket feed. We deployed the system on Ethereum Sepolia (contract `0x8998…283B`) and verified end-to-end operation: over 120 real transactions were submitted, with successful `logAnomaly` calls mined into blocks such as `10687475`-`10687479`. The report documents the design, the engineering challenges encountered in running against a live public blockchain (nonce serialisation, gas-limit tuning, RPC rate-limits), and how each paradigm contributes to the overall guarantee.

**Keywords:** Cloud Computing, Peer-to-Peer, IoT, Machine Learning, Blockchain, Ethereum, Smart Contract, Hybrid Web2/Web3.

---

## 1. Introduction

### 1.1 Motivation

Remote health monitoring is one of the fastest-growing application domains of cloud computing. Wearable devices now capture heart rate, body temperature, and blood-oxygen saturation continuously, and cloud back-ends are expected to detect clinically meaningful anomalies in real time. The dominant architecture today is centralised: every device streams raw readings to a single cloud service (e.g. AWS IoT Core, Azure IoT Hub, Google Cloud IoT) which performs storage, analytics and alerting. This design has two well-documented weaknesses. First, a single logical service is a single point of trust — the provider can in principle alter or silently lose the historical record that insurers, regulators and patients rely on. Second, a single logical service is a single point of failure — when it goes down, every downstream consumer goes down with it.

A natural response is to *decentralise* the architecture: distribute the processing across independent peers that can exchange data directly, and anchor the audit trail in a shared log that no single party can rewrite. Doing so, however, requires combining several paradigms that are normally taught separately — peer-to-peer networking, IoT data acquisition, cloud-side machine learning, and blockchain smart contracts. The purpose of this project is to investigate how these four pieces fit together in a single, practical end-to-end system for health data, and to measure what the resulting hybrid architecture actually costs and delivers when run against a live public cloud and a live public blockchain.

### 1.2 Goals

This project was guided by five concrete engineering goals:

- **G1.** Build a true P2P overlay with no broker and no central coordinator, in which every participant can send a message to every other participant. A leader (*master*) is elected dynamically from among the live peers.
- **G2.** Simulate a wearable IoT device that publishes realistic physiological readings and occasionally injects anomalies, so the ML pipeline can be exercised without real hardware.
- **G3.** Train an unsupervised anomaly detector (Isolation Forest) on synthetic "healthy" data and use it as a service that labels each live reading in real time.
- **G4.** Write a Solidity smart contract that accepts anomaly hashes, deploy it to the public Sepolia testnet, and submit every ML-flagged anomaly as a real, signed, gas-paying transaction from a Python peer. This is the step that earns the project its "public cloud" and "real blockchain" classifications.
- **G5.** Expose the entire running system through a single web dashboard so that a non-technical viewer can watch sensor data, ML verdicts, peer membership and confirmed on-chain transactions side-by-side in real time.

### 1.3 Contributions

The main contributions of this work are:

- A fully working hybrid Web2/Web3 implementation. Five roles (bootstrap, IoT, ML, BC, dashboard) cooperate over a single message bus, and anomalies that start as floating-point numbers in an IoT simulator end up as confirmed, block-included transactions on Ethereum Sepolia with no manual steps in between.
- A careful, measured treatment of the *engineering* cost of running against a real public blockchain — nonce management under concurrent submission, gas-limit tuning based on observed reverts, and rate-limiting from the free-tier RPC provider. These are rarely covered in coursework and are reported honestly in §7.
- A reproducible project layout and deployment workflow (`npx hardhat deploy`, four Python processes, one browser tab) that a grader can reconstruct in under ten minutes using only the repository, a funded Sepolia wallet, and an Infura project ID.

### 1.4 Report Structure

Section 2 surveys related work in decentralised health monitoring. Section 3 describes the overall system architecture. Section 4 presents the implementation of each of the five subsystems. Section 5 reports the deployment procedure and the end-to-end evaluation, including screenshots and on-chain evidence. Section 6 discusses engineering challenges and how they were resolved. Section 7 concludes and lists future work.

---

## 2. Related Work

The system built in this project sits at the intersection of four long-standing research threads. This section briefly surveys the parts of each thread that directly inform our design choices, and positions our contribution against them.

### 2.1 Centralised Cloud Architectures for IoT Health Data

Commercial platforms such as AWS IoT Core, Azure IoT Hub and Google Cloud IoT offer a mature, highly scalable template for IoT health monitoring: devices authenticate to a managed gateway using TLS and per-device SAS or X.509 credentials, publish telemetry over MQTT, and the gateway routes messages to cloud-side services (Kinesis, Event Hubs, Pub/Sub) that fan out to storage, analytics and dashboards. These platforms solve scale and operational reliability extremely well. Their weakness, for our purposes, is the *trust model*: every device, every reading, and every downstream analytic ultimately lives under a single administrative boundary. A tampered historical record is indistinguishable from a correct one to an external auditor. Our system keeps a compatible MQTT publisher path (the IoT simulator can optionally mirror readings to Azure IoT Hub for illustration) but does not rely on it as the system of record.

### 2.2 Peer-to-Peer Overlays

Classical P2P work — Chord (Stoica et al., 2001), Pastry (Rowstron & Druschel, 2001), Kademlia (Maymounkov & Mazières, 2002) — established that a logically flat network of equal peers can perform lookup, routing and membership without a central server. BitTorrent and Gnutella demonstrated the same idea at internet scale. More recent work on gossip-based dissemination (Demers et al., 1987; Birman et al., 1999) shows how messages can be reliably propagated across a mesh without a single source of truth.

For a five-node application, a full DHT is overkill. We therefore use a small, pragmatic design: a single *bootstrap* node serves only as a rendezvous for membership discovery, after which every peer opens a direct TCP connection to every other peer, and application messages are broadcast over that fully-connected mesh. Leader election among the live peers is solved by a simple bully algorithm (Garcia-Molina, 1982), which is adequate for the small peer counts envisaged and easy to demonstrate.

### 2.3 Blockchain for Healthcare Data

Using a blockchain as a tamper-evident audit log for healthcare is not new. MedRec (Ekblaw et al., 2016) proposed using Ethereum smart contracts to manage patient record access permissions. A large body of subsequent work explores on-chain consent management, drug supply-chain tracking, and clinical-trial auditing. A recurring practical lesson from these systems is that raw clinical data should never be placed on-chain directly, both because of privacy constraints (immutable storage of patient data is a regulatory problem) and because of gas economics (every byte is permanently replicated across every validator, at real monetary cost). The community-standard pattern is therefore *hash anchoring*: raw data is stored off-chain (IPFS, S3, local storage), and only a hash of the data is written on-chain as proof-of-existence. This pattern — popularised by Proof-of-Existence (Araoz, 2013) and used in countless notary-style applications since — is exactly the pattern we adopt.

### 2.4 Unsupervised Anomaly Detection for Physiological Signals

Classical supervised classifiers require labelled examples of "abnormal" vital signs, which are expensive and heterogeneous to collect. Unsupervised methods side-step this by learning the shape of "normal" behaviour and flagging deviations. Isolation Forest (Liu, Ting & Zhou, 2008) is one of the most widely used such methods: it builds a small ensemble of random trees that isolate points by recursive partitioning, and scores each point by its average isolation depth. Points that are "easy to isolate" are anomalous. It is fast, requires almost no tuning, and tolerates high-dimensional inputs. We adopt it unchanged from the scikit-learn implementation.

### 2.5 Where This Project Fits

Most previous work focuses on one of these threads at a time: a P2P system, or a blockchain system, or an ML system. A small number of integration papers discuss two of them simultaneously (e.g., "blockchain + IoT"). What is comparatively rare — and what this project attempts — is a *single self-contained demonstration* in which a genuine P2P overlay, a live IoT stream, an online ML classifier, and a real public-chain smart contract all cooperate end-to-end, with an observable dashboard, in a form that can be reproduced from a student's laptop in an afternoon. Our contribution is therefore not any one technique in isolation, but an honest account of what it takes to make these four layers work together at the same time, including the engineering frictions (§6) that only appear at the seams.

---

## 3. System Design and Architecture

### 3.1 Architectural Overview

The system is organised as five cooperating *roles* that speak a single message protocol over a fully-connected P2P mesh. Each role is realised by an independent operating-system process and can be stopped or restarted without bringing the others down. Figure 1 summarises the data flow.

```
    ┌────────────────┐    MSG_SENSOR     ┌────────────────┐
    │  IoT simulator │ ────────────────▶ │   ML detector  │
    │  (role=iot)    │                   │   (role=ml)    │
    └────────────────┘                   └────────┬───────┘
            │                                     │ MSG_ANOMALY
            │                                     ▼
            │                            ┌────────────────┐
            │                            │  Blockchain    │
            │                            │  submitter     │
            │                            │  (role=bc)     │
            │                            └────────┬───────┘
            │                                     │ logAnomaly(…)
            │                                     ▼
            │                             ╔══════════════╗
            │                             ║   Ethereum   ║
            │                             ║   Sepolia    ║
            │                             ║  HealthLog   ║
            │                             ╚══════╤═══════╝
            │                                    │ MSG_BC_LOGGED
            │          ┌────────────────┐        │  (tx hash,block)
            └────────▶ │    Dashboard   │ ◀──────┘
                       │ (role=dashboard│
                       │  + WebSocket)  │
                       └────────┬───────┘
                                │ wss://…/ws
                                ▼
                             Browser UI

   Every arrow above the Sepolia line is a length-prefixed JSON
   message on the internal P2P overlay.  A separate bootstrap
   node (role=bootstrap) exists only for initial peer discovery
   and is otherwise invisible to the data plane.
```

**Figure 1.** *End-to-end data flow. Sensor readings travel right along the top row; ML verdicts branch down to the blockchain submitter; confirmed on-chain receipts loop back to the dashboard, which serves a browser UI over WebSocket.*

### 3.2 The Five Roles

1. **Bootstrap (`role=bootstrap`).** A single well-known peer whose only job is to accept incoming `MSG_HELLO` from new peers and reply with the current membership list. After a newcomer has this list it *never needs the bootstrap again*; all further communication goes peer-to-peer. The bootstrap is therefore a discovery aid, not a message broker.

2. **IoT simulator (`role=iot`).** Produces synthetic heart-rate, body-temperature and SpO₂ readings at a fixed cadence (default 1.5 s). With small probability each sample is replaced by an *injected* anomaly — a hypothermic body temperature, a tachycardic heart rate, a hypoxic SpO₂ — so that the ML pipeline can be exercised without waiting for a real medical event. Each reading is broadcast as `MSG_SENSOR`.

3. **ML detector (`role=ml`).** Subscribes to `MSG_SENSOR`, runs each reading through a pre-trained Isolation Forest model, and broadcasts `MSG_ANOMALY` whenever the model's decision function falls below zero (the scikit-learn convention for "outlier"). The anomaly envelope carries the original reading, the model's score, and a SHA-256 *event hash* computed over the canonical-JSON representation of the reading. The hash is what later gets anchored on chain.

4. **Blockchain submitter (`role=bc`).** Subscribes to `MSG_ANOMALY`, classifies the anomaly into a short kind string (`hr_high`, `hr_low`, `temp_high`, `spo2_low`, `multi_metric`), and calls `HealthLog.logAnomaly(eventHash, deviceId, kind)` on the deployed contract using a funded Sepolia wallet. Once the transaction is mined with `status == 1`, it broadcasts `MSG_BC_LOGGED` carrying the transaction hash, block number and gas used, so downstream consumers can display it.

5. **Dashboard (`role=dashboard`).** Is both a normal P2P peer *and* an HTTP/WebSocket server. It subscribes to `MSG_SENSOR`, `MSG_ANOMALY`, `MSG_BC_LOGGED`, keeps a small rolling history, and fans everything out to connected browsers as JSON frames over `/ws`. The browser renders live KPIs, a heart-rate sparkline, a peer list, an anomaly table and a blockchain table whose transaction hashes link to Etherscan.

### 3.3 Message Protocol

All inter-process messages use the same wire format: a 4-byte big-endian length prefix followed by a UTF-8 JSON object with three fields — `msg_type`, `sender`, `payload`. This framing is deliberately boring (it is the same framing used by countless micro-services) and makes it easy to read a malformed message from a stream without losing sync. The message types used are summarised in Table 1.

| `msg_type`         | Producer            | Consumers              | Purpose                               |
|--------------------|---------------------|------------------------|---------------------------------------|
| `hello`            | any new peer        | bootstrap              | initial announce, ask for peer list   |
| `peers`            | bootstrap           | the newcomer           | reply with current membership         |
| `ping` / `pong`    | any                 | any                    | liveness check                        |
| `elect` / `master` | any                 | all                    | bully leader election                 |
| `sensor`           | IoT                 | ML, dashboard          | a raw reading                         |
| `anomaly`          | ML                  | BC, dashboard          | an ML-flagged reading + event hash    |
| `bc_logged`        | BC                  | dashboard              | confirmed on-chain receipt            |
| `dashboard_sub`    | dashboard           | —                      | reserved for future subscription ops  |

**Table 1.** *Message types carried by the internal P2P overlay. Only the top row of types (hello/peers/ping/pong/elect/master) is infrastructure; the bottom four carry application data.*

### 3.4 Trust and Data-Flow Model

The most important design decision in this project is *what crosses the Web2/Web3 boundary and what does not*:

- **Stays in Web2 (off-chain).** Raw sensor readings, peer membership, ML verdicts, dashboard WebSocket frames. These are high-volume and low-value-per-byte; paying gas for them would be absurd.
- **Crosses into Web3 (on-chain).** Only the SHA-256 hash of an anomaly event, together with the device identifier and a short kind label. A single transaction is ≤ 32 bytes of dynamic payload plus ~80 bytes of static fields — small enough to fit comfortably under our 250 000 gas limit.

This split yields a specific, auditable guarantee: any off-chain party holding a raw anomaly record can always *verify* it against the chain by re-computing the hash; any tampering with the off-chain record (by any party, including the hospital, the device vendor or a cloud operator) will break the hash comparison and be immediately detectable. The chain is therefore used as a *notary*, not as a database — which is what Ethereum is actually good at.

### 3.5 Why a Public Chain Rather Than a Private One

We deliberately target the public Ethereum test network (Sepolia), not a private Hyperledger or Besu deployment. Two reasons. First, a private chain operated by the same party that operates the hospital back-end gains no auditability over a regular centralised database: the operator still holds the keys. A public chain is validated by thousands of independent parties, and tampering requires attacking the entire network. Second, Sepolia forces the system to confront real-world engineering concerns — nonce contention under concurrent submission, gas economics, RPC provider rate limits — which are discussed honestly in §6 and which would have been hidden by a single-validator private chain.

---

