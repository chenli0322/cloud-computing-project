# Project Part 1 - Weekly Progress Report - Week 7 (Mar 10, 2026)

> **Course**: Special CS Topic - Cloud Computing, Section 026
> **Student**: Chen Li (Solo)
> **Project**: Legacy Application (ArchNav) Cloud Migration

---

## Work Completed This Week

1. **Docker containerization of all 4 services** — built Dockerfiles for MySQL 5.7, ApacheDS 2.0.0-M23, Tomcat 8.5.11 (Fortress REST + Web), and GlassFish 3.1.2 (ArchNav + ADF 11.1.2.4). Debugged and resolved multiple build issues including JDK 7 `.pack` → `.jar` conversion, GlassFish expired SSL certificates, and Fortress WAR filename mismatches.

2. **Local Docker deployment successful** — `docker-compose up --build` brings up all 4 containers on a single bridge network (`archnav-net`). ArchNav login page accessible at `http://localhost:9999/archemy/faces/login.jspx`.

3. **AWS EC2 cloud deployment** — provisioned a `t2.small` Ubuntu 24.04 instance in `us-east-1`, uploaded Docker files via SCP, and ran `docker compose up --build -d`. All 4 containers running and healthy on the cloud VM (public IP: 13.222.128.40).

4. **Fixed Fortress LDAP configuration** — the `fortress.properties` embedded in multiple JAR/WAR/EAR layers had incorrect LDAP settings (`host=localhost`, `dc=archemy,dc=com`, `cn=Manager`). Traced the root cause through 4 nested locations (domain1/lib JAR, expanded WAR directory JAR, `__internal` EAR, `/opt` EAR) and applied correct values (`host=apacheds`, `dc=example,dc=com`, `uid=admin,ou=system`). Applied the same fix on both local Docker and AWS EC2.

5. **Created LDAP RBAC structure and test users** — added `users` OrgUnit, `Admin` role (ARBAC), `NormalUser` role (RBAC), and two test users (`tom@oracle.com` as Admin, `john@oracle.com` as NormalUser) on both local and EC2 environments.

6. **Generated architecture diagrams and documentation**:
   - `current_state.puml` — PlantUML diagram of the original Windows 2-stack architecture
   - `future_state.puml` — PlantUML diagram of the Docker + cloud target architecture
   - `docs/README.md` — project structure, service ports, quick start guide
   - `deploy.sh` — one-command cloud deployment script for Ubuntu VMs

7. **Generated Part 1 Migration Report** (Word document) with 7 screenshots covering the full migration lifecycle.

---

## Planned Work for Next Week (Week 8 - Mar 17)

1. Start Part 2: research BTP P2P framework for peer-to-peer node communication
2. Set up Azure IoT Hub and write IoT sensor simulator (Python)
3. Begin P2P bootstrap node and peer node implementation
4. Stop EC2 instance when not in use to save costs

---

## Issues Encountered

- **Docker Desktop WSL2 crash**: Docker Engine became unresponsive; resolved by `wsl --shutdown` → `wsl --update` → restart.
- **C: drive out of space (3MB free)**: WSL2 virtual disk consumed all space; resolved by cleaning 33GB from Windows.old and moving WSL distro to F: drive.
- **JDK 7 `.pack` files**: RPM extraction left class libraries as `.pack` format; added `unpack200` step in Dockerfile to convert to `.jar`.
- **GlassFish SSL expired**: Built-in certificate expired in 2022; removed `enable-secure-admin` and used `--secure=false` for admin commands.
- **Fortress properties scattered in 4+ locations**: GlassFish regenerates classloader cache from the expanded WAR directory's JAR on each restart, so fixing only the top-level JAR was insufficient. Had to patch all 4 nested locations (lib JAR, expanded WAR JAR, `__internal` EAR, `/opt` EAR) and clear the JSP cache.

---

## Key Learnings

- GlassFish's classloader caches `fortress.properties` from `generated/jsp/` directories, but regenerates them from the expanded WAR's `WEB-INF/lib/` JAR on restart — fixing config requires updating the source JAR, not just the cache.
- Docker inter-container communication uses service names (e.g., `apacheds`, `mysql`) as hostnames, replacing all `localhost` references in config files.
- Cloud-based migration (no code changes) is achievable but requires careful configuration patching at the infrastructure level.
- ApacheDS listens on port 10389 internally but is mapped to 389 externally; Fortress properties inside containers should use the Docker service name with port 389.
