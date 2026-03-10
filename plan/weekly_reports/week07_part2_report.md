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
