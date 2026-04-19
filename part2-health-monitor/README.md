# Part 2: Decentralized Health Monitoring System

> **Course**: Special CS Topic - Cloud Computing, Section 026
> **Professor**: Jean-Claude Franchitti
> **Student**: Chen Li (Solo)

---

## Overview

A decentralized health monitoring platform combining IoT, Machine Learning, and Blockchain
technologies over a true peer-to-peer network (no broker).

### Architecture

```
┌────────────────────────────────────────────────────────────────┐
│              P2P Network (pure socket, no broker)              │
│                                                                │
│   ┌─────────────┐     ┌─────────────┐     ┌─────────────┐      │
│   │  IoT Node   │ <-> │   ML Node   │ <-> │   BC Node   │      │
│   │ sensor sim  │     │ IsolationFst│     │HealthLog.sol│      │
│   │ → Azure IoT │     │   anomaly   │     │ → Sepolia   │      │
│   │    Hub      │     │  detection  │     │   testnet   │      │
│   └─────────────┘     └─────────────┘     └─────────────┘      │
│                                                                │
│   Bootstrap nodes always-on for discovery (seed nodes)         │
│   Any node can become master; master election on failover      │
└────────────────────────────────────────────────────────────────┘
                               ↓
                      ┌────────────────┐
                      │ Web Dashboard  │
                      │ (real-time WS) │
                      └────────────────┘
```

### Technology Stack

| Layer | Technology | Cloud |
|-------|-----------|-------|
| IoT | Python MQTT + simulated sensors | Azure IoT Hub |
| ML | scikit-learn IsolationForest | (local) |
| Blockchain | Solidity + Hardhat | Ethereum Sepolia testnet (via Infura) |
| P2P | Python asyncio + TCP sockets (custom, no broker) | - |
| Dashboard | HTML + WebSocket | - |
| Compute | AWS EC2 (node hosting), S3 (raw data) | AWS |

### Cloud Platforms (≥ 2 per spec)

1. **AWS** (Part 1 ArchNav + Part 2 node hosting + S3 storage)
2. **Ethereum Sepolia testnet** (public blockchain cloud, per Prof. guidance 4/16)
3. **Azure** (IoT Hub for sensor ingestion)

### Three PaaS

1. **IoT** — Azure IoT Hub + MQTT protocol
2. **ML** — sklearn anomaly detection
3. **Blockchain** — Ethereum smart contracts (hybrid Web2+Web3, only hashes on-chain)

### Hybrid Web2 + Web3 design

- **On-chain**: event hash + timestamp (immutable audit trail)
- **Off-chain**: raw sensor data, ML predictions, UI state (P2P + S3)

---

## Folder Structure

```
part2-health-monitor/
├── README.md                   # (this file)
├── requirements.txt            # Python deps
├── docs/
│   ├── architecture.puml       # PlantUML architecture diagram
│   └── design_notes.md
├── p2p-network/                # True P2P framework
│   ├── peer_node.py            # Main peer implementation
│   ├── bootstrap_node.py       # Seed/bootstrap node
│   ├── message.py              # Message format & routing
│   └── election.py             # Master election
├── iot-simulator/
│   ├── sensor_simulator.py
│   ├── mqtt_publisher.py
│   └── iot_node.py             # IoT P2P node wrapper
├── ml-model/
│   ├── train_model.py
│   ├── predict.py
│   ├── ml_node.py              # ML P2P node wrapper
│   ├── data/
│   └── models/
├── blockchain/
│   ├── contracts/HealthLog.sol
│   ├── scripts/deploy.js
│   ├── hardhat.config.js
│   └── bc_node.py              # BC P2P node wrapper
├── dashboard/
│   ├── index.html
│   ├── app.js
│   └── server.py               # WebSocket bridge
└── screenshots/
```

---

## Running (end-to-end)

```bash
# Terminal 1: bootstrap node
python p2p-network/bootstrap_node.py --port 9000

# Terminal 2: IoT node
python iot-simulator/iot_node.py --bootstrap localhost:9000 --port 9001

# Terminal 3: ML node
python ml-model/ml_node.py --bootstrap localhost:9000 --port 9002

# Terminal 4: BC node
python blockchain/bc_node.py --bootstrap localhost:9000 --port 9003

# Terminal 5: Dashboard
python dashboard/server.py --bootstrap localhost:9000 --port 8080
# open http://localhost:8080
```
