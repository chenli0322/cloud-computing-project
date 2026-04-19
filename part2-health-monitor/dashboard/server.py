"""
Dashboard WebSocket bridge.

Connects to the P2P network as a peer with role="dashboard" and re-publishes
every interesting message (sensor readings, anomaly events, BC confirmations,
peer join/leave) to all browser clients over a WebSocket. Also serves the
static HTML/JS from ./public on HTTP.

Run:
    python server.py --port 8080 --bootstrap 127.0.0.1:9000
"""
from __future__ import annotations
import argparse
import asyncio
import json
import sys
import time
from pathlib import Path

from aiohttp import web

sys.path.insert(0, str(Path(__file__).parent.parent / "p2p-network"))
from peer_node import PeerNode
from message import (
    Envelope,
    MSG_SENSOR,
    MSG_ANOMALY,
    MSG_BC_LOGGED,
)


HERE = Path(__file__).parent
PUBLIC = HERE / "public"


class Broadcaster:
    def __init__(self):
        self.clients: set[web.WebSocketResponse] = set()
        self.history: list[dict] = []  # keep last 200 events

    def add(self, ws: web.WebSocketResponse):
        self.clients.add(ws)

    def remove(self, ws: web.WebSocketResponse):
        self.clients.discard(ws)

    async def fanout(self, msg: dict):
        self.history.append(msg)
        if len(self.history) > 200:
            self.history.pop(0)
        dead = []
        for ws in list(self.clients):
            try:
                await ws.send_json(msg)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.remove(ws)


def make_app(bcast: Broadcaster, node: PeerNode) -> web.Application:
    app = web.Application()

    async def index(_request):
        return web.FileResponse(PUBLIC / "index.html")

    async def ws_handler(request):
        ws = web.WebSocketResponse(heartbeat=30)
        await ws.prepare(request)
        bcast.add(ws)
        # Send backlog
        for m in bcast.history[-50:]:
            try:
                await ws.send_json(m)
            except Exception:
                break
        # Tell client current peer set
        await ws.send_json({
            "kind": "peers",
            "peers": [
                {"id": pid, "host": h, "port": p}
                for pid, (h, p) in node.peers.items()
            ],
            "master": node.master_id,
            "self": node.node_id,
            "ts": time.time(),
        })
        try:
            async for msg in ws:
                if msg.type == web.WSMsgType.CLOSE:
                    break
        finally:
            bcast.remove(ws)
        return ws

    app.router.add_get("/", index)
    app.router.add_get("/ws", ws_handler)
    app.router.add_static("/static/", PUBLIC, show_index=False)
    return app


async def _main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8080, help="HTTP/WS port")
    ap.add_argument("--p2p-port", type=int, default=9010)
    ap.add_argument("--bootstrap", default="127.0.0.1:9000")
    args = ap.parse_args()

    bcast = Broadcaster()
    node = PeerNode(
        host=args.host, port=args.p2p_port, role="dashboard",
        node_id="dashboard-0", bootstrap=args.bootstrap,
    )

    async def on_sensor(env: Envelope):
        await bcast.fanout({
            "kind": "sensor", "sender": env.sender_id,
            "ts": env.ts, "payload": env.payload,
        })

    async def on_anomaly(env: Envelope):
        await bcast.fanout({
            "kind": "anomaly", "sender": env.sender_id,
            "ts": env.ts, "payload": env.payload,
        })

    async def on_bc(env: Envelope):
        await bcast.fanout({
            "kind": "bc", "sender": env.sender_id,
            "ts": env.ts, "payload": env.payload,
        })

    node.on(MSG_SENSOR, on_sensor)
    node.on(MSG_ANOMALY, on_anomaly)
    node.on(MSG_BC_LOGGED, on_bc)

    asyncio.create_task(node.start())

    app = make_app(bcast, node)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, args.host, args.port)
    await site.start()
    print(f"Dashboard:  http://{args.host}:{args.port}")
    print(f"P2P peer :  {args.host}:{args.p2p_port}  bootstrap={args.bootstrap}")
    try:
        while True:
            await asyncio.sleep(3600)
    finally:
        await runner.cleanup()


if __name__ == "__main__":
    try:
        asyncio.run(_main())
    except KeyboardInterrupt:
        pass
