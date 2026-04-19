"""
ML P2P node.

Loads the trained IsolationForest; on every MSG_SENSOR received from the
P2P network, predicts anomaly vs normal and, if anomaly, broadcasts
MSG_ANOMALY to all peers directly (the BC node and Dashboard will react).
"""
from __future__ import annotations
import argparse
import asyncio
import hashlib
import json
import sys
import time
from pathlib import Path

import joblib
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent / "p2p-network"))
from peer_node import PeerNode
from message import Envelope, MSG_SENSOR, MSG_ANOMALY

MODEL_PATH = Path(__file__).parent / "models" / "anomaly_model.joblib"


def event_hash(payload: dict) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return "0x" + hashlib.sha256(raw).hexdigest()


async def _main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, required=True)
    ap.add_argument("--bootstrap", default="127.0.0.1:9000")
    ap.add_argument("--model", default=str(MODEL_PATH))
    args = ap.parse_args()

    if not Path(args.model).exists():
        print(f"Model not found at {args.model}. "
              f"Run `python train_model.py` first.")
        return

    clf = joblib.load(args.model)
    node = PeerNode(
        host=args.host, port=args.port, role="ml",
        node_id=f"ml-{args.port}", bootstrap=args.bootstrap,
    )

    async def on_sensor(env: Envelope):
        r = env.payload
        x = np.array([[r["heart_rate"], r["body_temp"], r["spo2"]]])
        pred = clf.predict(x)[0]       # -1 anomaly, +1 normal
        score = float(clf.decision_function(x)[0])
        if pred == -1:
            anomaly_event = {
                "device_id": r.get("device_id", "unknown"),
                "ts": r.get("ts", time.time()),
                "heart_rate": r["heart_rate"],
                "body_temp": r["body_temp"],
                "spo2": r["spo2"],
                "score": round(score, 4),
                "source_iot_node": env.sender_id,
            }
            anomaly_event["hash"] = event_hash(anomaly_event)
            node.log.info(
                "ANOMALY detected  HR=%.1f T=%.2f SpO2=%.1f score=%.3f",
                r["heart_rate"], r["body_temp"], r["spo2"], score,
            )
            await node.broadcast(MSG_ANOMALY, anomaly_event)

    node.on(MSG_SENSOR, on_sensor)
    await node.start()


if __name__ == "__main__":
    try:
        asyncio.run(_main())
    except KeyboardInterrupt:
        pass
