# Project Part 1 - Weekly Progress Report - Week 13 (Apr 23, 2026)

> **Course**: Special CS Topic - Cloud Computing, Section 026
> **Student**: Chen Li (Solo)
> **Project**: Legacy Application (ArchNav) Cloud Migration

---

## Work Completed This Week

1. **Wrote and tested `launch_aws_ec2.py`** — the Python automation that ends up performing the entire EC2 rebuild. Final form: ~360 lines of `boto3` + `paramiko` + `subprocess`, idempotent (reuses existing key pair and security group if already present), and documents the steps it takes via colored INFO/OK/ERR markers.

2. **Executed the full cold rebuild on 2026-04-26**:
   - New instance `i-05d91070fdb3bfca9` launched at public IP `3.88.156.91`, AMI `ami-05cf1e9f73fbad2e2` (Ubuntu Server 24.04 LTS amd64, gp3-backed)
   - Security group `archnav-final-2026-sg` created with 22/8080/9999/4848 inbound from `0.0.0.0/0`
   - Local `docker/` tree tar-gzipped to **251 MB**, SCP'd in ~4 minutes over the residential link
   - `apt-get update && apt-get install -y docker-ce docker-compose-plugin` ran cleanly on the fresh Ubuntu 24.04
   - `docker compose build` for the four images took ~10 minutes (Glassfish image is the slow one — JDK 7 unpack + ADF Essentials extract)
   - `docker compose up -d` brought all four containers to `Up`; `mysql` and `apacheds` reach `(healthy)` within 30 s, `glassfish` and `tomcat` within 60 s

3. **Verified the public-internet liveness**:
   - `curl -I http://3.88.156.91:9999/archemy/faces/login.jspx` returns `HTTP/1.1 200 OK` with `Server: GlassFish Server Open Source Edition 3.1.2`
   - `curl -I http://3.88.156.91:4848` returns `HTTP/1.1 202 Accepted` (Glassfish admin console)
   - The browser renders the ArchNav login page identically to the original Week-7 deployment

4. **Re-applied the Fortress LDAP runtime patch** (the same runbook drafted in Week 9): patched `host=apacheds`, `port=10389`, `admin.user=uid=admin,ou=system`, `admin.pw=secret`, `config.root=ou=Config,dc=example,dc=com` inside all three nested copies of `archemy-security-1.0-SNAPSHOT-jar-with-dependencies.jar`, then cleared the JSP cache and restarted the Glassfish container. After restart, the regenerated `fortress.properties` confirmed the new values are in effect.

5. **Captured fresh demo screenshots** (`13_archnav_login_aws.png` and `14_ec2_docker_ps.png`) for inclusion in the Final Report and Final Presentation. The cold-rebuild is the run that the grader's demo will exercise.

---

## Planned Work for Next Week (Week 14 - Final Demo)

1. Keep the EC2 instance running until the demo concludes (cost: ~$0.55 / day at t2.small).
2. Walk through the Part-1 deck on the day; show the live URL and the SSH `docker compose ps` output to make the cloud deployment concrete.
3. Stop / terminate the instance after the grade is in.

---

## Issues Encountered

- The local Python orchestrator initially hit a Windows `gbk` encoding error when streaming Glassfish-image apt output containing non-ASCII certificate names; switched to `python -u` and added `errors='replace'` on stdout to avoid this on the next rerun.
- The shipped Dockerfile builds an `archemy-security` JAR with a hardcoded `admin.pw=oracle123`, which is not the actual ApacheDS admin password (`secret`). Patched at runtime via the LDAP-properties runbook; this was already noted as the Week-9 runbook so the fix took ~10 minutes.

---

## Key Learnings

- A 30-minute scripted rebuild is the right metric for whether a migration is "production-ready as a demo". Anything longer and the demo becomes about the rebuild rather than about the application.
- The lesson of multi-tier classloader caches (Glassfish JSP cache, expanded WAR JAR, internal EAR, /opt EAR) is durable: the runtime view of `fortress.properties` is regenerated from the source JAR on every restart, so a runtime patch must always edit the source.

---

## Public URL of the Live Deployment (for grading)

`http://3.88.156.91:9999/archemy/faces/login.jspx`

GitHub repository: <https://github.com/chenli0322/cloud-computing-project>
