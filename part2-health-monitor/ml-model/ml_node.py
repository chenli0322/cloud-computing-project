"""
ML P2P node.

Loads the trained IsolationForest; on every MSG_SENSOR received from the
P2P network, predicts anomaly vs normal and, if anomaly, broadcasts
MSG_ANOMALY to all peers directly (the BC node and Dashboard will react).

Model artifact is loaded from S3 if MODEL_S3_URI is set in the environment
(e.g. s3://cl5725-health-monitor-anomalies/models/anomaly_model.joblib);
otherwise it falls back to the local file at models/anomaly_model.joblib.
This satisfies the "ML on cloud" requirement: training happens on EC2,
the artifact is stored in S3, and inference loads it from S3 at startup.
"""
from __future__ import annotations
import argparse
import asyncio
import hashlib
import json
import os
import sys
import tempfile
import time
from pathlib import Path

import joblib
import numpy as np
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent / "p2p-network"))
from peer_node import PeerNode
from message import Envelope, MSG_SENSOR, MSG_ANOMALY

THIS_DIR = Path(__file__).parent
MODEL_PATH = THIS_DIR / "models" / "anomaly_model.joblib"


def event_hash(payload: dict) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return "0x" + hashlib.sha256(raw).hexdigest()


def _download_model_from_s3(s3_uri: str) -> Path:
    """Download s3://bucket/key to a temp file and return its path."""
    if not s3_uri.startswith("s3://"):
        raise ValueError(f"Not an s3 URI: {s3_uri}")
    rest = s3_uri[len("s3://"):]
    bucket, _, key = rest.partition("/")
    if not bucket or not key:
        raise ValueError(f"Malformed s3 URI: {s3_uri}")
    try:
        import boto3
    except ImportError:
        raise RuntimeError("boto3 not installed; pip install boto3")
    region = os.environ.get("AWS_REGION", "us-east-1")
    client = boto3.client("s3", region_name=region)
    tmp = Path(tempfile.gettempdir()) / f"anomaly_model_{int(time.time())}.joblib"
    print(f"[ml] downloading {s3_uri} -> {tmp}")
    client.download_file(bucket, key, str(tmp))
    return tmp


def _load_model() -> object:
    """Load the IsolationForest from S3 if MODEL_S3_URI is set, else local."""
    load_dotenv(THIS_DIR / ".env")
    s3_uri = os.environ.get("MODEL_S3_URI")
    if s3_uri:
        path = _download_model_from_s3(s3_uri)
    else:
        path = MODEL_PATH
        if not path.exists():
            raise FileNotFoundError(
                f"Model not found at {path}. "
                f"Either run `python train_model.py` to create it locally, "
                f"or set MODEL_S3_URI in ml-model/.env to load from S3."
            )
    print(f"[ml] loading model from {path}")
    return joblib.load(path)


async def _main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, required=True)
    ap.add_argument("--bootstrap", default="127.0.0.1:9000")
    args = ap.parse_args()

    try:
        clf = _load_model()
    except Exception as e:
        print(f"[ml] FATAL: {e}")
        return
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
