# Part 1: ArchNav Legacy Application Cloud Migration

> Cloud Computing Spring 2026 — Prof. Jean-Claude Franchitti
> Student: Chen Li (Solo)

## Overview

This project migrates the **ArchNav** legacy Java application from a Windows local installation to Docker containers, enabling deployment on any cloud VM. This is a **cloud-based migration** — zero source code changes; only the infrastructure is containerized.

## Project Structure

```
part1-migration/
├── docker/                  # Docker configuration & build files
│   ├── docker-compose.yml   # Orchestrates all 4 services
│   ├── .env                 # Environment variables (ports, passwords)
│   ├── Dockerfile.mysql     # MySQL 5.7 + archemy schema init
│   ├── Dockerfile.apacheds  # ApacheDS 2.0.0-M23 (LDAP)
│   ├── Dockerfile.tomcat    # Tomcat 8.5 + Fortress REST/Web
│   ├── Dockerfile.glassfish # GlassFish 3.1.2 + ADF + ArchNav
│   ├── init.sql             # MySQL schema initialization
│   ├── packages/            # Pre-downloaded installer packages
│   ├── scripts/             # Helper scripts
│   └── setup-packages.sh    # Package preparation script
├── docs/                    # Documentation & architecture diagrams
│   ├── current_state.puml   # PlantUML: original Windows architecture
│   ├── future_state.puml    # PlantUML: Docker + cloud target architecture
│   └── README.md            # This file
├── screenshots/             # Deployment evidence screenshots
└── deploy.sh                # One-click cloud deployment script
```

## Technology Stack

| Component | Version | Purpose |
|-----------|---------|---------|
| JDK | 1.7.0_80 | Java runtime (strict version requirement) |
| MySQL | 5.7 | Business data (schema: `archemy`) |
| ApacheDS | 2.0.0-M23 | LDAP directory service |
| GlassFish | 3.1.2 | App server for ArchNav (Oracle ADF 11.1.2.4) |
| Apache Tomcat | 8.5.11 | Hosts Fortress REST API + Fortress Web UI |
| Apache Fortress | 2.0.0-RC1 | RBAC security framework |
| Docker / Compose | Latest | Container orchestration |

## Services & Ports

| Service | Container Name | Internal Port | Exposed Port | URL |
|---------|---------------|---------------|--------------|-----|
| MySQL | archnav-mysql | 3306 | 3306 | — |
| ApacheDS (LDAP) | archnav-apacheds | 10389 | 389 | — |
| Tomcat (Fortress) | archnav-tomcat | 8080 | 8080 | `http://<host>:8080/fortress-web` |
| GlassFish (ArchNav) | archnav-glassfish | 9999 | 9999 | `http://<host>:9999/archemy/faces/login.jspx` |
| GlassFish Admin | archnav-glassfish | 4848 | 4848 | `http://<host>:4848` |

## Quick Start (Local)

```bash
# 1. Navigate to docker directory
cd part1-migration/docker

# 2. Ensure packages are prepared
bash setup-packages.sh

# 3. Build and start all services
docker-compose up -d --build

# 4. Wait for services to be healthy (~2 minutes)
docker-compose ps

# 5. Access the application
#    ArchNav:       http://localhost:9999/archemy/faces/login.jspx
#    Fortress Web:  http://localhost:8080/fortress-web
```

## Default Credentials

| Service | Username | Password |
|---------|----------|----------|
| ArchNav (Admin) | tom@oracle.com | oracle123 |
| ArchNav (User) | john@oracle.com | oracle123 |
| Fortress Web | test | password |
| GlassFish Admin | admin | Claude1960% |
| MySQL | archemy | archemydb1960% |
| LDAP (ApacheDS) | uid=admin,ou=system | secret |
| Tomcat Manager | tcmanager | m@nager123 |

## Cloud Deployment

For one-command deployment on a fresh Ubuntu VM:

```bash
curl -fsSL https://raw.githubusercontent.com/chenli0322/cloud-computing-project/main/part1-migration/deploy.sh | bash
```

Or manually:

```bash
git clone https://github.com/chenli0322/cloud-computing-project.git
cd cloud-computing-project/part1-migration
bash deploy.sh
```

See `deploy.sh` for details.

## Architecture Diagrams

The PlantUML diagrams can be rendered at [plantuml.com](https://www.plantuml.com/plantuml/uml/) or with any PlantUML-compatible tool:

- **`current_state.puml`** — Original 5-component Windows local architecture (17-step manual install)
- **`future_state.puml`** — Target Docker containerized architecture on cloud VM (one-command deploy)

## Container Network

All containers communicate over the `archnav-net` bridge network using service names as hostnames:

```
archnav-glassfish  ──→  mysql:3306       (JDBC)
archnav-glassfish  ──→  apacheds:389     (LDAP auth)
archnav-glassfish  ──→  tomcat:8080      (Fortress REST)
archnav-tomcat     ──→  apacheds:389     (LDAP auth)
```

## Stopping Services

```bash
# Stop and remove containers (keep data)
docker-compose down

# Stop and remove everything including volumes
docker-compose down -v
```
