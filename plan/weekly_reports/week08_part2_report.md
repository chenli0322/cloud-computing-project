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
