"""
Simulate a wearable health sensor.

Generates heart_rate (bpm), body_temp (°C), SpO2 (%) with realistic noise
and occasional injected anomalies for ML training / demo.
"""
from __future__ import annotations
import random
import time
from dataclasses import dataclass, asdict


@dataclass
class Reading:
    device_id: str
    ts: float
    heart_rate: float   # bpm
    body_temp: float    # °C
    spo2: float         # %
    is_anomaly_injected: bool = False

    def to_dict(self) -> dict:
        return asdict(self)


class SensorSimulator:
    """
    Nominal ranges (healthy adult at rest):
        HR      60-100 bpm
        Body T  36.1-37.2 °C
        SpO2    95-100 %

    With probability `anomaly_rate` emits clearly out-of-range values.
    """

    def __init__(
        self,
        device_id: str = "sim-device-001",
        anomaly_rate: float = 0.05,
        seed: int | None = None,
    ):
        self.device_id = device_id
        self.anomaly_rate = anomaly_rate
        self.rng = random.Random(seed)

    def sample(self) -> Reading:
        if self.rng.random() < self.anomaly_rate:
            kind = self.rng.choice(["hr_high", "hr_low", "temp_high", "spo2_low"])
            if kind == "hr_high":
                hr = self.rng.uniform(130, 180)
                bt = self.rng.gauss(36.8, 0.2)
                sp = self.rng.gauss(97.5, 0.8)
            elif kind == "hr_low":
                hr = self.rng.uniform(35, 45)
                bt = self.rng.gauss(36.5, 0.2)
                sp = self.rng.gauss(97.5, 0.8)
            elif kind == "temp_high":
                hr = self.rng.gauss(88, 4)
                bt = self.rng.uniform(38.5, 40.5)
                sp = self.rng.gauss(96, 1)
            else:  # spo2_low
                hr = self.rng.gauss(90, 4)
                bt = self.rng.gauss(37.1, 0.3)
                sp = self.rng.uniform(82, 90)
            injected = True
        else:
            hr = self.rng.gauss(75, 8)
            bt = self.rng.gauss(36.7, 0.25)
            sp = self.rng.gauss(98, 0.8)
            hr = max(40, min(130, hr))
            bt = max(35.5, min(38.0, bt))
            sp = max(90.0, min(100.0, sp))
            injected = False

        return Reading(
            device_id=self.device_id,
            ts=time.time(),
            heart_rate=round(hr, 1),
            body_temp=round(bt, 2),
            spo2=round(sp, 1),
            is_anomaly_injected=injected,
        )


if __name__ == "__main__":
    sim = SensorSimulator(anomaly_rate=0.1, seed=42)
    for _ in range(20):
        print(sim.sample().to_dict())
