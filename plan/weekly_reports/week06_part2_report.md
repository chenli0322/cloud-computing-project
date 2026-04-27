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
