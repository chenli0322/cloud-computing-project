/**
 * Deploys HealthLog to whichever network --network points at.
 *
 *   npx hardhat run scripts/deploy.js --network sepolia
 *
 * Writes deployment.json with {address, txHash, block} for the Python
 * BC node to pick up.
 */
const fs = require("fs");
const path = require("path");
const hre = require("hardhat");

async function main() {
  const [deployer] = await hre.ethers.getSigners();
  const bal = await hre.ethers.provider.getBalance(deployer.address);
  console.log("Deployer:", deployer.address);
  console.log("Balance :", hre.ethers.formatEther(bal), "ETH");

  const Factory = await hre.ethers.getContractFactory("HealthLog");
  const contract = await Factory.deploy();
  await contract.waitForDeployment();

  const address = await contract.getAddress();
  const tx = contract.deploymentTransaction();
  const receipt = await tx.wait();

  console.log("HealthLog deployed at:", address);
  console.log("Tx hash :", tx.hash);
  console.log("Block   :", receipt.blockNumber);

  const out = {
    network: hre.network.name,
    address,
    txHash: tx.hash,
    block: receipt.blockNumber,
    deployer: deployer.address,
    abi: JSON.parse(contract.interface.formatJson()),
  };
  const outPath = path.join(__dirname, "..", "deployment.json");
  fs.writeFileSync(outPath, JSON.stringify(out, null, 2));
  console.log("Wrote", outPath);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
