"""
Generic P2P peer node (no broker).

Responsibilities:
  - Bind a TCP server on --port
  - On start, connect to --bootstrap and send MSG_HELLO
  - Maintain a live peer set; gossip new peers via MSG_PEERS
  - Forward payload messages (sensor/anomaly/bc_logged) to all known peers
  - Participate in simple bully-style master election on peer loss

This is NOT a message broker: every peer keeps its own TCP connections
to every other peer it has learned about. Messages are sent directly.
"""
from __future__ import annotations
import argparse
import asyncio
import logging
import uuid
from typing import Callable, Awaitable, Optional

from message import (
    Envelope,
    MSG_HELLO,
    MSG_PEERS,
    MSG_PING,
    MSG_PONG,
    MSG_ELECT,
    MSG_MASTER,
    read_envelope,
    write_envelope,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)


class PeerNode:
    def __init__(
        self,
        host: str,
        port: int,
        role: str = "generic",
        node_id: Optional[str] = None,
        bootstrap: Optional[str] = None,
    ):
        self.host = host
        self.port = port
        self.role = role
        self.node_id = node_id or f"{role}-{uuid.uuid4().hex[:8]}"
        self.bootstrap = bootstrap  # "host:port" or None
        self.peers: dict[str, tuple[str, int]] = {}     # node_id -> (host, port)
        self.writers: dict[str, asyncio.StreamWriter] = {}
        self.master_id: Optional[str] = None
        self.handlers: dict[str, Callable[[Envelope], Awaitable[None]]] = {}
        self.log = logging.getLogger(f"peer:{self.node_id}")

    # ---------- public API --------------------------------------------------

    def on(self, msg_type: str, handler: Callable[[Envelope], Awaitable[None]]):
        """Register a handler for a message type."""
        self.handlers[msg_type] = handler

    async def broadcast(self, msg_type: str, payload: dict):
        env = Envelope(
            type=msg_type, sender_id=self.node_id, role=self.role, payload=payload
        )
        dead = []
        for pid, w in list(self.writers.items()):
            try:
                await write_envelope(w, env)
            except Exception as e:
                self.log.warning("peer %s dead: %s", pid, e)
                dead.append(pid)
        for pid in dead:
            self._drop_peer(pid)

    async def send_to(self, peer_id: str, msg_type: str, payload: dict) -> bool:
        w = self.writers.get(peer_id)
        if not w:
            return False
        env = Envelope(
            type=msg_type, sender_id=self.node_id, role=self.role, payload=payload
        )
        try:
            await write_envelope(w, env)
            return True
        except Exception as e:
            self.log.warning("send_to %s failed: %s", peer_id, e)
            self._drop_peer(peer_id)
            return False

    async def start(self):
        server = await asyncio.start_server(
            self._handle_incoming, self.host, self.port
        )
        self.log.info("listening on %s:%d role=%s", self.host, self.port, self.role)
        if self.bootstrap:
            asyncio.create_task(self._connect_bootstrap())
        asyncio.create_task(self._keepalive_loop())
        async with server:
            await server.serve_forever()

    # ---------- internals ---------------------------------------------------

    async def _connect_bootstrap(self):
        if not self.bootstrap:
            return
        host, port = self.bootstrap.split(":")
        port = int(port)
        try:
            reader, writer = await asyncio.open_connection(host, port)
        except OSError as e:
            self.log.error("bootstrap connect failed: %s", e)
            return
        hello = Envelope(
            type=MSG_HELLO,
            sender_id=self.node_id,
            role=self.role,
            payload={"host": self.host, "port": self.port},
        )
        await write_envelope(writer, hello)
        # we'll learn the bootstrap's node_id from the first message it sends
        asyncio.create_task(self._read_loop(reader, writer, peer_id=None))

    async def _handle_incoming(self, reader, writer):
        await self._read_loop(reader, writer, peer_id=None)

    async def _read_loop(self, reader, writer, peer_id: Optional[str]):
        try:
            while True:
                env = await read_envelope(reader)
                if env is None:
                    break
                if peer_id is None:
                    peer_id = env.sender_id
                    host = env.payload.get("host")
                    port = env.payload.get("port")
                    if host and port:
                        self.peers[peer_id] = (host, int(port))
                    self.writers[peer_id] = writer
                    self.log.info(
                        "peer joined: %s role=%s (total=%d)",
                        peer_id, env.role, len(self.writers),
                    )
                    if env.type == MSG_HELLO:
                        # reply with known peers
                        await write_envelope(
                            writer,
                            Envelope(
                                type=MSG_PEERS,
                                sender_id=self.node_id,
                                role=self.role,
                                payload={
                                    "peers": [
                                        {"id": pid, "host": h, "port": p}
                                        for pid, (h, p) in self.peers.items()
                                        if pid != peer_id
                                    ],
                                    "host": self.host,
                                    "port": self.port,
                                },
                            ),
                        )
                        continue
                await self._dispatch(env)
        except asyncio.IncompleteReadError:
            pass
        except Exception as e:
            self.log.warning("read_loop error: %s", e)
        finally:
            if peer_id:
                self._drop_peer(peer_id)

    async def _dispatch(self, env: Envelope):
        if env.type == MSG_PEERS:
            await self._learn_peers(env.payload.get("peers", []))
            return
        if env.type == MSG_PING:
            await self.send_to(env.sender_id, MSG_PONG, {})
            return
        if env.type == MSG_PONG:
            return
        if env.type == MSG_ELECT:
            # bully: higher node_id wins
            if env.sender_id < self.node_id:
                await self._start_election()
            return
        if env.type == MSG_MASTER:
            self.master_id = env.sender_id
            self.log.info("master announced: %s", self.master_id)
            return
        handler = self.handlers.get(env.type)
        if handler:
            await handler(env)
        else:
            self.log.debug("no handler for %s from %s", env.type, env.sender_id)

    async def _learn_peers(self, peer_list: list[dict]):
        for p in peer_list:
            pid = p["id"]
            if pid == self.node_id or pid in self.writers:
                continue
            host, port = p["host"], int(p["port"])
            try:
                reader, writer = await asyncio.open_connection(host, port)
            except OSError:
                continue
            hello = Envelope(
                type=MSG_HELLO,
                sender_id=self.node_id,
                role=self.role,
                payload={"host": self.host, "port": self.port},
            )
            await write_envelope(writer, hello)
            self.peers[pid] = (host, port)
            asyncio.create_task(self._read_loop(reader, writer, peer_id=None))

    def _drop_peer(self, peer_id: str):
        self.peers.pop(peer_id, None)
        w = self.writers.pop(peer_id, None)
        if w:
            try:
                w.close()
            except Exception:
                pass
        self.log.info("peer left: %s (remaining=%d)", peer_id, len(self.writers))
        if peer_id == self.master_id:
            self.master_id = None
            asyncio.create_task(self._start_election())

    async def _start_election(self):
        # announce our bid; if no higher peer objects within 2s, we become master
        self.log.info("starting master election")
        await self.broadcast(MSG_ELECT, {})
        await asyncio.sleep(2.0)
        if self.master_id is None:
            self.master_id = self.node_id
            await self.broadcast(MSG_MASTER, {})
            self.log.info("elected self as master")

    async def _keepalive_loop(self):
        while True:
            await asyncio.sleep(15)
            await self.broadcast(MSG_PING, {})


def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, required=True)
    ap.add_argument("--role", default="generic")
    ap.add_argument("--id", default=None)
    ap.add_argument("--bootstrap", default=None, help="host:port of seed node")
    return ap.parse_args()


async def _main():
    args = parse_args()
    node = PeerNode(
        host=args.host,
        port=args.port,
        role=args.role,
        node_id=args.id,
        bootstrap=args.bootstrap,
    )
    await node.start()


if __name__ == "__main__":
    try:
        asyncio.run(_main())
    except KeyboardInterrupt:
        pass
