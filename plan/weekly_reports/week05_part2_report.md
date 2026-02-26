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
