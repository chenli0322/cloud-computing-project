"""
Bootstrap (seed) node — always-on discovery entry point.

A bootstrap is just a PeerNode with role="bootstrap" and no upstream bootstrap.
New peers connect here first with MSG_HELLO; the bootstrap replies with the
current peer list (MSG_PEERS). After that, peers talk to each other directly.
"""
import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from peer_node import PeerNode


async def _main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=9000)
    args = ap.parse_args()
    node = PeerNode(
        host=args.host, port=args.port, role="bootstrap", node_id="bootstrap-0"
    )
    await node.start()


if __name__ == "__main__":
    try:
        asyncio.run(_main())
    except KeyboardInterrupt:
        pass
