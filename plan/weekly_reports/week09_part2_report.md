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
