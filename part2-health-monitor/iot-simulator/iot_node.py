"""
IoT P2P node.

Runs a PeerNode with role="iot", periodically samples the simulated sensor,
and broadcasts MSG_SENSOR envelopes to all peers directly (no broker).

Also publishes the raw reading to Azure IoT Hub via MQTT 8883/TLS, satisfying
the "IoT PaaS" requirement (the IoT Hub connection string is loaded from the
local .env or AZURE_IOT_CONN_STR env var). Without that variable set the
Azure path is silently disabled and the node continues to run as a pure P2P
peer for local development.
"""
from __future__ import annotations
import argparse
import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent / "p2p-network"))
sys.path.insert(0, str(Path(__file__).parent))

from peer_node import PeerNode
from message import MSG_SENSOR
from sensor_simulator import SensorSimulator

THIS_DIR = Path(__file__).parent


async def _publish_loop(node: PeerNode, sim: SensorSimulator, interval: float, azure_pub):
    azure_count = 0
    while True:
        reading = sim.sample().to_dict()
        await node.broadcast(MSG_SENSOR, reading)
        if azure_pub is not None:
            try:
                ok = azure_pub(reading)
                if ok:
                    azure_count += 1
                    if azure_count == 1 or azure_count % 10 == 0:
                        node.log.info("azure: published %d messages so far", azure_count)
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
    Returns a callable(reading_dict) -> bool if AZURE_IOT_CONN_STR is set.
    Returns None (and prints why) if the env var or paho-mqtt is missing.
    """
    load_dotenv(THIS_DIR / ".env")
    conn = os.environ.get("AZURE_IOT_CONN_STR")
    if not conn:
        print("[iot] AZURE_IOT_CONN_STR not set; Azure IoT Hub bridge disabled.")
        return None
    try:
        import json
        import ssl
        import paho.mqtt.client as mqtt
    except ImportError:
        print("[iot] paho-mqtt not installed; pip install paho-mqtt")
        return None

    # conn format: "HostName=xxx.azure-devices.net;DeviceId=dev;SharedAccessKey=..."
    try:
        parts = dict(kv.split("=", 1) for kv in conn.split(";"))
        host = parts["HostName"]
        device_id = parts["DeviceId"]
        shared_key = parts["SharedAccessKey"]
    except Exception as e:
        print(f"[iot] AZURE_IOT_CONN_STR malformed: {e}")
        return None

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
    token = sas_token(uri, shared_key)

    client = mqtt.Client(client_id=device_id, protocol=mqtt.MQTTv311)
    client.username_pw_set(f"{host}/{device_id}/?api-version=2021-04-12", token)
    ctx = ssl.create_default_context()
    client.tls_set_context(ctx)

    connected = {"ok": False}

    def on_connect(c, _ud, _flags, rc):
        if rc == 0:
            connected["ok"] = True
            print(f"[iot] azure IoT Hub connected: {host} device={device_id}")
        else:
            print(f"[iot] azure IoT Hub connect failed rc={rc}")

    def on_disconnect(c, _ud, rc):
        connected["ok"] = False
        print(f"[iot] azure IoT Hub disconnected rc={rc}")

    client.on_connect = on_connect
    client.on_disconnect = on_disconnect

    try:
        client.connect(host, 8883)
    except Exception as e:
        print(f"[iot] azure connect raised {e}; bridge disabled.")
        return None
    client.loop_start()
    topic = f"devices/{device_id}/messages/events/"
    print(f"[iot] azure publishing to topic={topic}")

    def publish(reading) -> bool:
        info = client.publish(topic, json.dumps(reading), qos=1)
        return info.rc == 0

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
