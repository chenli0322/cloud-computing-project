"""
IoT P2P node.

Runs a PeerNode with role="iot", periodically samples the simulated sensor,
and broadcasts MSG_SENSOR envelopes to all peers directly (no broker).

Optional: also publishes the raw reading to Azure IoT Hub via MQTT
(disabled unless AZURE_IOT_CONN_STR env var is set).
"""
from __future__ import annotations
import argparse
import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "p2p-network"))
sys.path.insert(0, str(Path(__file__).parent))

from peer_node import PeerNode
from message import MSG_SENSOR
from sensor_simulator import SensorSimulator


async def _publish_loop(node: PeerNode, sim: SensorSimulator, interval: float, azure_pub):
    while True:
        reading = sim.sample().to_dict()
        await node.broadcast(MSG_SENSOR, reading)
        if azure_pub is not None:
            try:
                azure_pub(reading)
            except Exception as e:
                node.log.warning("azure publish failed: %s", e)
        node.log.info(
            "sensor  HR=%.1f T=%.2f SpO2=%.1f  injected=%s",
            reading["heart_rate"], reading["body_temp"],
            reading["spo2"], reading["is_anomaly_injected"],
        )
        await asyncio.sleep(interval)


def _maybe_azure_publisher():
    """
    Returns a callable(reading_dict) -> None if AZURE_IOT_CONN_STR is set.
    We lazy-import because paho-mqtt may not be installed yet in dev.
    """
    conn = os.environ.get("AZURE_IOT_CONN_STR")
    if not conn:
        return None
    try:
        import json
        import ssl
        import paho.mqtt.client as mqtt
    except ImportError:
        print("paho-mqtt not installed; skipping Azure IoT Hub publishing.")
        return None

    # conn format: "HostName=xxx.azure-devices.net;DeviceId=dev;SharedAccessKey=..."
    parts = dict(kv.split("=", 1) for kv in conn.split(";"))
    host = parts["HostName"]
    device_id = parts["DeviceId"]

    import urllib.parse, hmac, hashlib, base64, time as _time

    def sas_token(uri, key, ttl=3600):
        expiry = int(_time.time()) + ttl
        to_sign = f"{urllib.parse.quote_plus(uri)}\n{expiry}"
        signed = base64.b64encode(
            hmac.new(base64.b64decode(key), to_sign.encode(), hashlib.sha256).digest()
        ).decode()
        return (
            f"SharedAccessSignature sr={urllib.parse.quote_plus(uri)}"
            f"&sig={urllib.parse.quote_plus(signed)}&se={expiry}"
        )

    uri = f"{host}/devices/{device_id}"
    token = sas_token(uri, parts["SharedAccessKey"])

    client = mqtt.Client(client_id=device_id, protocol=mqtt.MQTTv311)
    client.username_pw_set(f"{host}/{device_id}/?api-version=2021-04-12", token)
    ctx = ssl.create_default_context()
    client.tls_set_context(ctx)
    client.connect(host, 8883)
    client.loop_start()
    topic = f"devices/{device_id}/messages/events/"

    def publish(reading):
        client.publish(topic, json.dumps(reading), qos=1)

    return publish


async def _main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, required=True)
    ap.add_argument("--bootstrap", default="127.0.0.1:9000")
    ap.add_argument("--device-id", default="sim-device-001")
    ap.add_argument("--interval", type=float, default=2.0,
                    help="seconds between readings")
    ap.add_argument("--anomaly-rate", type=float, default=0.08)
    args = ap.parse_args()

    sim = SensorSimulator(device_id=args.device_id, anomaly_rate=args.anomaly_rate)
    node = PeerNode(
        host=args.host, port=args.port, role="iot",
        node_id=f"iot-{args.device_id}", bootstrap=args.bootstrap,
    )

    azure_pub = _maybe_azure_publisher()
    asyncio.create_task(_publish_loop(node, sim, args.interval, azure_pub))
    await node.start()


if __name__ == "__main__":
    try:
        asyncio.run(_main())
    except KeyboardInterrupt:
        pass
