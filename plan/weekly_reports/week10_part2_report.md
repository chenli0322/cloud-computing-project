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
