#!/usr/bin/env bash
#
# ArchNav Cloud Deployment Script
# Deploys the containerized ArchNav application on a fresh Ubuntu VM.
#
# Usage:
#   bash deploy.sh
#
# Tested on: Ubuntu 22.04 LTS (Azure / AWS EC2)
#

set -euo pipefail

REPO_URL="https://github.com/chenli0322/cloud-computing-project.git"
PROJECT_DIR="$HOME/cloud-computing-project"
DOCKER_DIR="$PROJECT_DIR/part1-migration/docker"

# ---------- helpers ----------
info()  { echo -e "\033[1;34m[INFO]\033[0m  $*"; }
ok()    { echo -e "\033[1;32m[OK]\033[0m    $*"; }
err()   { echo -e "\033[1;31m[ERROR]\033[0m $*" >&2; exit 1; }

# ---------- 1. System update ----------
info "Updating system packages..."
sudo apt-get update -y && sudo apt-get upgrade -y
ok "System updated"

# ---------- 2. Install Docker ----------
if command -v docker &>/dev/null; then
    ok "Docker already installed: $(docker --version)"
else
    info "Installing Docker..."
    sudo apt-get install -y ca-certificates curl gnupg lsb-release

    sudo install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
        | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    sudo chmod a+r /etc/apt/keyrings/docker.gpg

    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
      https://download.docker.com/linux/ubuntu \
      $(lsb_release -cs) stable" \
      | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

    sudo apt-get update -y
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

    sudo usermod -aG docker "$USER"
    ok "Docker installed: $(docker --version)"
fi

# ---------- 3. Install Docker Compose (standalone, fallback) ----------
if docker compose version &>/dev/null; then
    ok "Docker Compose plugin available"
elif command -v docker-compose &>/dev/null; then
    ok "docker-compose standalone available"
else
    info "Installing Docker Compose standalone..."
    COMPOSE_VERSION=$(curl -fsSL https://api.github.com/repos/docker/compose/releases/latest | grep tag_name | cut -d '"' -f 4)
    sudo curl -fsSL "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" \
        -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    ok "Docker Compose installed: $(docker-compose --version)"
fi

# ---------- 4. Install Git ----------
if ! command -v git &>/dev/null; then
    info "Installing Git..."
    sudo apt-get install -y git
fi
ok "Git available: $(git --version)"

# ---------- 5. Clone repository ----------
if [ -d "$PROJECT_DIR" ]; then
    info "Repository exists, pulling latest..."
    cd "$PROJECT_DIR" && git pull
else
    info "Cloning repository..."
    git clone "$REPO_URL" "$PROJECT_DIR"
fi
ok "Repository ready at $PROJECT_DIR"

# ---------- 6. Build and start containers ----------
cd "$DOCKER_DIR"

info "Checking for required package files..."
if [ -f setup-packages.sh ]; then
    bash setup-packages.sh
fi

info "Building Docker images (this may take 10-15 minutes)..."
if docker compose version &>/dev/null; then
    COMPOSE_CMD="docker compose"
else
    COMPOSE_CMD="docker-compose"
fi

$COMPOSE_CMD build --no-cache
ok "Images built"

info "Starting containers..."
$COMPOSE_CMD up -d
ok "Containers started"

# ---------- 7. Wait for services to be healthy ----------
info "Waiting for services to become healthy (up to 3 minutes)..."
SECONDS=0
TIMEOUT=180
while [ $SECONDS -lt $TIMEOUT ]; do
    HEALTHY=$($COMPOSE_CMD ps --format json 2>/dev/null | grep -c '"healthy"' || true)
    TOTAL=$($COMPOSE_CMD ps --format json 2>/dev/null | wc -l || true)
    if [ "$HEALTHY" -ge 2 ] 2>/dev/null; then
        break
    fi
    echo -n "."
    sleep 10
done
echo ""

# ---------- 8. Show status ----------
info "Container status:"
$COMPOSE_CMD ps

PUBLIC_IP=$(curl -fsSL --connect-timeout 5 http://checkip.amazonaws.com 2>/dev/null || hostname -I | awk '{print $1}')

echo ""
echo "========================================"
echo "  ArchNav Deployment Complete"
echo "========================================"
echo ""
echo "  ArchNav Application:"
echo "    http://${PUBLIC_IP}:9999/archemy/faces/login.jspx"
echo ""
echo "  Fortress Web (RBAC Admin):"
echo "    http://${PUBLIC_IP}:8080/fortress-web"
echo ""
echo "  GlassFish Admin Console:"
echo "    http://${PUBLIC_IP}:4848"
echo ""
echo "  Default logins:"
echo "    ArchNav Admin : tom@oracle.com  / oracle123"
echo "    ArchNav User  : john@oracle.com / oracle123"
echo "    Fortress Web  : test / password"
echo ""
echo "========================================"
echo ""
info "If running on a cloud VM, ensure security group allows inbound TCP on ports: 3306, 389, 8080, 9999, 4848"
