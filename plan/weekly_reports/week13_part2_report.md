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
