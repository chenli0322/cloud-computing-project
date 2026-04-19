# Blockchain Layer (HealthLog on Sepolia)

Hybrid Web2/Web3 design: only the SHA-256 hash + timestamp of each detected
anomaly is written on-chain. Raw sensor readings and ML scores stay off-chain
on the P2P network.

## One-time setup

```bash
# from blockchain/ directory
npm init -y                                        # if package.json is missing
npm install --save-dev hardhat @nomicfoundation/hardhat-toolbox dotenv
cp .env.example .env                               # then edit .env
```

Edit `.env`:
- `SEPOLIA_RPC_URL` — grab from https://www.infura.io (free account → new project → copy Sepolia URL)
- `PRIVATE_KEY` — MetaMask → three dots on account → Account details → Export private key (NO `0x` prefix, testnet only!)

## Compile + deploy

```bash
npx hardhat compile
npx hardhat run scripts/deploy.js --network sepolia
```

On success, `deployment.json` is written with address + ABI. The Python BC
node auto-loads it.

## Run the BC P2P node

```bash
python bc_node.py --port 9003 --bootstrap 127.0.0.1:9000
```

It listens for `MSG_ANOMALY` messages, submits `logAnomaly()` on chain, and
re-broadcasts `MSG_BC_LOGGED` once mined.
