"""
Train an IsolationForest anomaly detector on simulated health data.

Produces models/anomaly_model.joblib.
"""
from __future__ import annotations
import os
import sys
from pathlib import Path

import numpy as np
import joblib
from sklearn.ensemble import IsolationForest
from sklearn.metrics import classification_report

sys.path.insert(0, str(Path(__file__).parent.parent / "iot-simulator"))
from sensor_simulator import SensorSimulator  # noqa: E402


MODEL_DIR = Path(__file__).parent / "models"
DATA_DIR = Path(__file__).parent / "data"
MODEL_PATH = MODEL_DIR / "anomaly_model.joblib"


def build_dataset(n: int = 5000, anomaly_rate: float = 0.1, seed: int = 7):
    sim = SensorSimulator(anomaly_rate=anomaly_rate, seed=seed)
    X, y = [], []
    for _ in range(n):
        r = sim.sample()
        X.append([r.heart_rate, r.body_temp, r.spo2])
        y.append(1 if r.is_anomaly_injected else 0)
    return np.array(X, dtype=float), np.array(y, dtype=int)


def main():
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    print("Generating synthetic training set ...")
    X_train, y_train = build_dataset(n=5000, anomaly_rate=0.1, seed=7)
    X_test, y_test = build_dataset(n=1500, anomaly_rate=0.1, seed=99)
    np.savez(DATA_DIR / "dataset.npz",
             X_train=X_train, y_train=y_train, X_test=X_test, y_test=y_test)

    print("Training IsolationForest ...")
    clf = IsolationForest(
        n_estimators=200,
        contamination=0.1,
        random_state=42,
        n_jobs=-1,
    )
    clf.fit(X_train)

    # IsolationForest returns -1 for anomaly, +1 for normal
    pred = (clf.predict(X_test) == -1).astype(int)
    print(classification_report(y_test, pred, target_names=["normal", "anomaly"]))

    joblib.dump(clf, MODEL_PATH)
    print(f"Saved model -> {MODEL_PATH}")


if __name__ == "__main__":
    main()
