"""
One-shot helper: upload models/anomaly_model.joblib to S3.

Usage (from part2-health-monitor/ml-model/):
    python upload_model_to_s3.py --bucket cl5725-health-monitor-anomalies

Reads AWS credentials from ml-model/.env (or boto3 default chain) and uploads
to s3://<bucket>/models/anomaly_model.joblib. Prints the s3:// URI to set as
MODEL_S3_URI on the ml node.
"""
from __future__ import annotations
import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

THIS_DIR = Path(__file__).parent
MODEL_PATH = THIS_DIR / "models" / "anomaly_model.joblib"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bucket", required=True, help="target S3 bucket name")
    ap.add_argument("--key", default="models/anomaly_model.joblib",
                    help="S3 key (default: models/anomaly_model.joblib)")
    ap.add_argument("--model", default=str(MODEL_PATH),
                    help="local model path (default: models/anomaly_model.joblib)")
    args = ap.parse_args()

    load_dotenv(THIS_DIR / ".env")

    src = Path(args.model)
    if not src.exists():
        print(f"FATAL: model not found at {src}. Run train_model.py first.")
        sys.exit(1)

    try:
        import boto3
    except ImportError:
        print("FATAL: boto3 not installed. Run: pip install boto3")
        sys.exit(1)

    region = os.environ.get("AWS_REGION", "us-east-1")
    client = boto3.client("s3", region_name=region)

    size = src.stat().st_size
    print(f"Uploading {src} ({size:,} bytes) -> s3://{args.bucket}/{args.key} ...")
    client.upload_file(str(src), args.bucket, args.key)
    uri = f"s3://{args.bucket}/{args.key}"
    print(f"OK. Set this in ml-model/.env to use it from ml_node:")
    print(f"  MODEL_S3_URI={uri}")


if __name__ == "__main__":
    main()
