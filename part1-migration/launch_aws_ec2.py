"""
One-shot AWS EC2 launcher for the ArchNav Part 1 demo.

What it does:
  1. Creates an SSH key pair (saved to ./archnav-key.pem)
  2. Creates a security group with 22/8080/9999/4848 inbound
  3. Finds the latest Ubuntu 24.04 LTS AMI in us-east-1
  4. Launches a t2.small instance
  5. Waits for SSH to be reachable
  6. Tars + scps the docker/ tree to the instance
  7. SSH-executes the setup script (apt + docker + docker compose up)
  8. Prints the public IP and the URLs to demo

Usage (from part1-migration/):
    python launch_aws_ec2.py

Reads AWS creds from ../part2-health-monitor/blockchain/.env (or boto3 default chain).
Demo credentials are committed in this script ONLY because the user explicitly
authorised it for this single rehearsal; rotate the IAM key after the demo.
"""
from __future__ import annotations
import os
import sys
import time
import socket
import subprocess
from pathlib import Path

import boto3
from botocore.exceptions import ClientError
import paramiko
from dotenv import load_dotenv

THIS_DIR = Path(__file__).parent
DOCKER_DIR = THIS_DIR / "docker"
KEY_PATH = THIS_DIR / "archnav-key.pem"
TARBALL = THIS_DIR / "docker.tar.gz"

KEY_NAME = "archnav-final-2026"
SG_NAME = "archnav-final-2026-sg"
INSTANCE_NAME = "archnav-final-2026"
INSTANCE_TYPE = "t2.small"
REGION = "us-east-1"


def info(msg):  print(f"\033[1;34m[INFO]\033[0m  {msg}")
def ok(msg):    print(f"\033[1;32m[OK]\033[0m    {msg}")
def warn(msg):  print(f"\033[1;33m[WARN]\033[0m  {msg}")
def err(msg):   print(f"\033[1;31m[ERROR]\033[0m {msg}", file=sys.stderr); sys.exit(1)


def get_ec2_client():
    # Reuse the same env as the BC node so credentials are central
    load_dotenv(THIS_DIR.parent / "part2-health-monitor" / "blockchain" / ".env")
    return boto3.client("ec2", region_name=REGION)


def ensure_key_pair(ec2):
    if KEY_PATH.exists():
        ok(f"Reusing existing key at {KEY_PATH}")
        return
    info(f"Creating key pair {KEY_NAME} ...")
    try:
        ec2.delete_key_pair(KeyName=KEY_NAME)
    except ClientError:
        pass
    resp = ec2.create_key_pair(KeyName=KEY_NAME, KeyType="rsa", KeyFormat="pem")
    KEY_PATH.write_text(resp["KeyMaterial"])
    # Lock down ACL on Windows so ssh.exe won't refuse the key
    try:
        subprocess.run(
            ["icacls", str(KEY_PATH), "/inheritance:r"],
            check=True, capture_output=True,
        )
        user = os.environ.get("USERNAME", "")
        if user:
            subprocess.run(
                ["icacls", str(KEY_PATH), "/grant:r", f"{user}:R"],
                check=True, capture_output=True,
            )
    except subprocess.CalledProcessError as e:
        warn(f"icacls failed: {e.stderr.decode(errors='ignore')}")
    ok(f"Wrote key to {KEY_PATH}")


def ensure_security_group(ec2) -> str:
    # Find default VPC
    vpcs = ec2.describe_vpcs(Filters=[{"Name": "isDefault", "Values": ["true"]}])
    if not vpcs["Vpcs"]:
        err("No default VPC in us-east-1; create one or pick another region")
    vpc_id = vpcs["Vpcs"][0]["VpcId"]

    existing = ec2.describe_security_groups(
        Filters=[{"Name": "group-name", "Values": [SG_NAME]}]
    )["SecurityGroups"]
    if existing:
        sg_id = existing[0]["GroupId"]
        ok(f"Reusing security group {SG_NAME} ({sg_id})")
        return sg_id

    info(f"Creating security group {SG_NAME} ...")
    sg = ec2.create_security_group(
        GroupName=SG_NAME,
        Description="ArchNav final demo: SSH + 8080 + 9999 + 4848",
        VpcId=vpc_id,
    )
    sg_id = sg["GroupId"]
    ec2.authorize_security_group_ingress(
        GroupId=sg_id,
        IpPermissions=[
            {"IpProtocol": "tcp", "FromPort": p, "ToPort": p,
             "IpRanges": [{"CidrIp": "0.0.0.0/0"}]}
            for p in (22, 8080, 9999, 4848)
        ],
    )
    ok(f"Security group {sg_id} created with TCP 22, 8080, 9999, 4848 open")
    return sg_id


def find_ubuntu_ami(ec2) -> str:
    info("Looking up latest Ubuntu 24.04 LTS amd64 AMI ...")
    images = ec2.describe_images(
        Owners=["099720109477"],   # Canonical
        Filters=[
            {"Name": "name", "Values": ["ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*"]},
            {"Name": "state", "Values": ["available"]},
        ],
    )["Images"]
    if not images:
        # Fallback to gp2 naming
        images = ec2.describe_images(
            Owners=["099720109477"],
            Filters=[
                {"Name": "name", "Values": ["ubuntu/images/hvm-ssd/ubuntu-noble-24.04-amd64-server-*"]},
                {"Name": "state", "Values": ["available"]},
            ],
        )["Images"]
    if not images:
        err("No Ubuntu 24.04 amd64 AMI found in us-east-1")
    images.sort(key=lambda x: x["CreationDate"], reverse=True)
    ami = images[0]["ImageId"]
    ok(f"Using AMI {ami} ({images[0]['Name']})")
    return ami


def launch_instance(ec2, ami, sg_id) -> dict:
    # Reuse a previous demo instance if one is running with our Name tag
    existing = ec2.describe_instances(Filters=[
        {"Name": "tag:Name", "Values": [INSTANCE_NAME]},
        {"Name": "instance-state-name", "Values": ["running", "pending"]},
    ])["Reservations"]
    for res in existing:
        for inst in res["Instances"]:
            ok(f"Reusing existing instance {inst['InstanceId']} ({inst.get('PublicIpAddress','?')})")
            return inst

    info(f"Launching {INSTANCE_TYPE} ...")
    res = ec2.run_instances(
        ImageId=ami,
        InstanceType=INSTANCE_TYPE,
        KeyName=KEY_NAME,
        SecurityGroupIds=[sg_id],
        MinCount=1, MaxCount=1,
        BlockDeviceMappings=[{
            "DeviceName": "/dev/sda1",
            "Ebs": {"VolumeSize": 20, "VolumeType": "gp3", "DeleteOnTermination": True},
        }],
        TagSpecifications=[{
            "ResourceType": "instance",
            "Tags": [{"Key": "Name", "Value": INSTANCE_NAME}],
        }],
    )
    inst = res["Instances"][0]
    instance_id = inst["InstanceId"]
    ok(f"Launched {instance_id}; waiting for running state ...")

    waiter = ec2.get_waiter("instance_running")
    waiter.wait(InstanceIds=[instance_id])

    # Re-fetch to get public IP
    inst = ec2.describe_instances(InstanceIds=[instance_id])["Reservations"][0]["Instances"][0]
    return inst


def wait_for_ssh(ip: str, timeout: int = 240):
    info(f"Waiting for SSH on {ip}:22 (up to {timeout}s) ...")
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection((ip, 22), timeout=5):
                ok("SSH port open")
                # Give sshd a moment to actually accept connections
                time.sleep(5)
                return
        except OSError:
            time.sleep(5)
    err("SSH never came up")


def make_tarball():
    info("Creating docker.tar.gz of part1-migration/docker/ ...")
    if TARBALL.exists():
        TARBALL.unlink()
    # Use Python's tarfile so we don't depend on tar.exe being available
    import tarfile
    with tarfile.open(TARBALL, "w:gz") as tar:
        for entry in DOCKER_DIR.rglob("*"):
            if entry.is_file():
                # Skip hidden, lock files, and bak
                rel = entry.relative_to(DOCKER_DIR)
                if any(part.startswith(".") for part in rel.parts):
                    continue
                if entry.suffix in (".bak",):
                    continue
                tar.add(str(entry), arcname=f"docker/{rel.as_posix()}")
    size_mb = TARBALL.stat().st_size / (1024 * 1024)
    ok(f"Tarball: {TARBALL} ({size_mb:.1f} MB)")


def scp_to_instance(ip: str):
    info(f"SCP {TARBALL.name} -> ubuntu@{ip}:~/")
    cmd = [
        "scp",
        "-o", "StrictHostKeyChecking=no",
        "-o", "UserKnownHostsFile=/dev/null",
        "-i", str(KEY_PATH),
        str(TARBALL),
        f"ubuntu@{ip}:~/",
    ]
    res = subprocess.run(cmd, check=False)
    if res.returncode != 0:
        err(f"scp failed with code {res.returncode}")
    ok("SCP complete")


def ssh_run(ip: str, command: str, *, timeout: int = 1800) -> tuple[int, str]:
    """Run a shell command on the remote, streaming stdout to local."""
    info(f"REMOTE: {command[:80]}{'...' if len(command) > 80 else ''}")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        hostname=ip,
        username="ubuntu",
        key_filename=str(KEY_PATH),
        timeout=20,
    )
    try:
        chan = client.get_transport().open_session()
        chan.set_combine_stderr(True)
        chan.exec_command(command)
        out_buf = []
        deadline = time.time() + timeout
        while True:
            if chan.recv_ready():
                chunk = chan.recv(8192).decode(errors="replace")
                sys.stdout.write(chunk)
                sys.stdout.flush()
                out_buf.append(chunk)
            if chan.exit_status_ready():
                break
            if time.time() > deadline:
                err(f"remote command timed out after {timeout}s")
            time.sleep(0.2)
        # Drain
        while chan.recv_ready():
            chunk = chan.recv(8192).decode(errors="replace")
            sys.stdout.write(chunk)
            sys.stdout.flush()
            out_buf.append(chunk)
        rc = chan.recv_exit_status()
        return rc, "".join(out_buf)
    finally:
        client.close()


def remote_setup(ip: str):
    # 1. Untar the docker tree
    rc, _ = ssh_run(ip, "set -e; rm -rf ~/docker; tar xzf ~/docker.tar.gz -C ~; ls -la ~/docker | head")
    if rc != 0:
        err("untar failed")

    # 2. Apt install Docker (single shell so package list is fresh)
    install_script = """
set -e
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y
sudo apt-get install -y ca-certificates curl gnupg lsb-release
sudo install -m 0755 -d /etc/apt/keyrings
if [ ! -f /etc/apt/keyrings/docker.gpg ]; then
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
  sudo chmod a+r /etc/apt/keyrings/docker.gpg
fi
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update -y
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker ubuntu
docker --version
docker compose version
"""
    rc, _ = ssh_run(ip, install_script, timeout=900)
    if rc != 0:
        err("docker install failed")

    # 3. Build images
    rc, _ = ssh_run(ip, "cd ~/docker && sudo docker compose build", timeout=1800)
    if rc != 0:
        err("docker compose build failed")

    # 4. Bring up containers
    rc, _ = ssh_run(ip, "cd ~/docker && sudo docker compose up -d && sleep 5 && sudo docker compose ps", timeout=300)
    if rc != 0:
        err("docker compose up failed")


def main():
    if not DOCKER_DIR.is_dir():
        err(f"docker dir not found at {DOCKER_DIR}")

    ec2 = get_ec2_client()
    ensure_key_pair(ec2)
    sg_id = ensure_security_group(ec2)
    ami = find_ubuntu_ami(ec2)
    inst = launch_instance(ec2, ami, sg_id)
    instance_id = inst["InstanceId"]
    public_ip = inst.get("PublicIpAddress")
    if not public_ip:
        err("Instance has no public IP; check VPC/subnet auto-assign-public-ip")

    print()
    ok(f"Instance: {instance_id}")
    ok(f"Public IP: {public_ip}")
    ok(f"SSH: ssh -i {KEY_PATH} ubuntu@{public_ip}")
    print()

    wait_for_ssh(public_ip)
    if not TARBALL.exists():
        make_tarball()
    scp_to_instance(public_ip)
    remote_setup(public_ip)

    print()
    print("=" * 60)
    print(f"  ArchNav LIVE on AWS EC2: http://{public_ip}:9999/archemy/faces/login.jspx")
    print(f"  Fortress Web:            http://{public_ip}:8080/fortress-web   (test/password)")
    print(f"  Glassfish admin:         http://{public_ip}:4848")
    print("=" * 60)
    print()
    print("LDAP/RBAC user setup (run after the build settles):")
    print(f"  ssh -i {KEY_PATH} ubuntu@{public_ip}")
    print(f"  cd ~/docker && cat README.md   # follow the 'Creating ArchNav Users' section")


if __name__ == "__main__":
    main()
