"""
P2P message protocol.

Wire format: 4-byte length prefix (big-endian) + UTF-8 JSON payload.
Every message is a JSON object with at minimum {type, sender_id, msg_id, ts}.
"""
import json
import time
import uuid
import struct
from dataclasses import dataclass, field, asdict
from typing import Any, Optional


MSG_HELLO = "hello"              # new peer announces itself
MSG_PEERS = "peers"              # reply with known peer list
MSG_PING = "ping"                # keepalive
MSG_PONG = "pong"                # keepalive reply
MSG_ELECT = "elect"              # master election bid
MSG_MASTER = "master"            # elected master announcement
MSG_SENSOR = "sensor_reading"    # IoT node publishes sensor data
MSG_ANOMALY = "anomaly_event"    # ML node publishes anomaly verdict
MSG_BC_LOGGED = "bc_logged"      # BC node confirms on-chain record
MSG_DASHBOARD_SUB = "dashboard_sub"  # dashboard subscribes to all


@dataclass
class Envelope:
    type: str
    sender_id: str
    role: str = "generic"            # "iot" | "ml" | "bc" | "bootstrap" | "dashboard"
    msg_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    ts: float = field(default_factory=time.time)
    payload: dict = field(default_factory=dict)

    def to_bytes(self) -> bytes:
        raw = json.dumps(asdict(self), separators=(",", ":")).encode("utf-8")
        return struct.pack(">I", len(raw)) + raw

    @staticmethod
    def from_json(obj: dict) -> "Envelope":
        return Envelope(
            type=obj["type"],
            sender_id=obj["sender_id"],
            role=obj.get("role", "generic"),
            msg_id=obj.get("msg_id", uuid.uuid4().hex),
            ts=obj.get("ts", time.time()),
            payload=obj.get("payload", {}),
        )


async def read_envelope(reader) -> Optional[Envelope]:
    hdr = await reader.readexactly(4)
    (length,) = struct.unpack(">I", hdr)
    if length <= 0 or length > 8 * 1024 * 1024:
        return None
    body = await reader.readexactly(length)
    try:
        obj = json.loads(body.decode("utf-8"))
        return Envelope.from_json(obj)
    except Exception:
        return None


async def write_envelope(writer, env: Envelope) -> None:
    writer.write(env.to_bytes())
    await writer.drain()
