# NYU Cloud Computing Spring 2026 Course Project

> **Course**: Special CS Topic - Cloud Computing, Section 026
> **Professor**: Jean-Claude Franchitti
> **Student**: Chen Li (Solo)

---

## Project Overview

### Part 1: Legacy Application (ArchNav) Cloud Migration

Migrate the ArchNav legacy Java application to the cloud without modifying source code, using containerization (Docker) and cloud deployment.

**Original Tech Stack**:
- Java JDK 1.7.0_80
- Oracle JDeveloper 11.1.2.4.0 (ADF Framework)
- Glassfish 3.1.2 (Application Server, HTTP port 9999)
- MySQL 5.7 (Business Database, port 3306)
- Apache Fortress 2.0.0-RC1 (RBAC Security)
- ApacheDS 2.0.0-M23 (LDAP Directory, port 389)
- Apache Tomcat 8.5.11 (Fortress REST/Web, port 8080)

### Part 2: Decentralized Health Monitoring System

An innovative cloud application combining IoT, ML, and Blockchain with P2P architecture.

**Three PaaS Technologies**:
1. **IoT** - Simulated health sensors (heart rate, temperature, SpO2) via MQTT to Azure IoT Hub
2. **AI/ML** - Anomaly detection model using scikit-learn
3. **Blockchain** - Ethereum smart contracts for immutable health event logs

**Two Cloud Platforms**:
- **Azure**: IoT Hub + ML
- **AWS**: EC2 + S3

**P2P Architecture**: libp2p / IPFS for decentralized health data distribution

---

## Repository Structure

```
cloud-computing-project/
├── README.md
├── plan/
│   └── weekly_reports/
├── part1-migration/
│   ├── docs/
│   ├── docker/
│   └── screenshots/
├── part2-health-monitor/
│   ├── docs/
│   ├── iot-simulator/
│   ├── ml-model/
│   │   ├── data/
│   │   └── models/
│   ├── blockchain/
│   │   ├── contracts/
│   │   └── scripts/
│   ├── p2p-network/
│   ├── dashboard/
│   └── screenshots/
├── final-report/
└── midterm/
```

---

## Timeline

| Week | Milestone |
|------|-----------|
| W5 (2/26) | Environment setup, project planning |
| W6 (3/5) | Midterm Proposal Presentation |
| W7 (3/12) | Run legacy app locally, start Part 2 |
| W8 (3/19) | Architecture diagrams, ML model |
| W9 (3/26) | Containerize Part 1, Blockchain |
| W10 (4/2) | Cloud deployment, P2P integration |
| W11 (4/9) | Dashboard, integration testing |
| W12-13 (4/16-23) | Final report, presentation prep |
| W14 (4/30) | Final Presentation + Demo |
