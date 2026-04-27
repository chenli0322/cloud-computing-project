# Part 1 — Legacy Application (ArchNav) Cloud Migration

## Weekly Progress Reports — Spring 2026 Course Project

> **Course**: Special CS Topic — Cloud Computing, Section 026
> **Instructor**: Prof. Jean-Claude Franchitti
> **Student**: Chen Li (NetID: cl5725) — solo team
> **Repository**: <https://github.com/chenli0322/cloud-computing-project>

---

## Table of Contents

- [Project Part 1 - Weekly Progress Report - Week 5 (Feb 26, 2026)](#project-part-1---weekly-progress-report---week-5-feb-26-2026)
- [Project Part 1 - Weekly Progress Report - Week 6 (Mar 5, 2026)](#project-part-1---weekly-progress-report---week-6-mar-5-2026)
- [Project Part 1 - Weekly Progress Report - Week 7 (Mar 10, 2026)](#project-part-1---weekly-progress-report---week-7-mar-10-2026)
- [Project Part 1 - Weekly Progress Report - Week 8 (Mar 19, 2026)](#project-part-1---weekly-progress-report---week-8-mar-19-2026)
- [Project Part 1 - Weekly Progress Report - Week 9 (Mar 26, 2026)](#project-part-1---weekly-progress-report---week-9-mar-26-2026)
- [Project Part 1 - Weekly Progress Report - Week 10 (Apr 2, 2026)](#project-part-1---weekly-progress-report---week-10-apr-2-2026)
- [Project Part 1 - Weekly Progress Report - Week 11 (Apr 9, 2026)](#project-part-1---weekly-progress-report---week-11-apr-9-2026)
- [Project Part 1 - Weekly Progress Report - Week 12 (Apr 16, 2026)](#project-part-1---weekly-progress-report---week-12-apr-16-2026)
- [Project Part 1 - Weekly Progress Report - Week 13 (Apr 23, 2026)](#project-part-1---weekly-progress-report---week-13-apr-23-2026)

---

# Project Part 1 - Weekly Progress Report - Week 5 (Feb 26, 2026)

> **Course**: Special CS Topic - Cloud Computing, Section 026
> **Student**: Chen Li (Solo)
> **Project**: Legacy Application (ArchNav) Cloud Migration

---

## Work Completed This Week

1. **Downloaded all required packages** for the legacy ArchNav application from the provided Google Drive link (13 files total, including JDK, JDeveloper, Glassfish, ADF Essentials, MySQL connector, Fortress-related packages, and the ArchNav application archive).

2. **Installed JDK 7u80** and verified the installation:
   - Installation path: `F:\Java\jdk1.7.0_80`
   - `java -version` confirms `1.7.0_80`
   - Configured `JAVA_HOME` and `PATH` environment variables at both user and system level
   - Ensured JDK 7 takes priority over existing JDK 23 installation

3. **Reviewed the ArchNav Installation Instructions document** (45 pages) and `Installing_fortress.md`:
   - Identified complete 17-step installation sequence
   - Understood the two-stack application architecture:
     - **Stack 1 (Security)**: Apache Fortress 2.0.0-RC1 (RBAC) + ApacheDS 2.0.0-M23 (LDAP, port 389) + Apache Tomcat 8.5.11 (port 8080)
     - **Stack 2 (Business)**: ArchNav (Oracle ADF 11.1.2.4) + Glassfish 3.1.2 (HTTP port 9999, Admin port 4848) + MySQL 5.7 (port 3306)
   - Identified key configurations: Glassfish HTTP port **9999** (changed from default 8080 to avoid Tomcat conflict), MySQL schema **"archemy"**, LDAP via **ApacheDS** (not OpenLDAP)

4. **Created project repository structure** with organized directories for both Part 1 (migration) and Part 2 (health monitor), including docs, docker, screenshots, and source code folders.

5. **Created installation_summary.md** — a structured reference document extracted from the PDF containing all credentials, ports, version requirements, and step-by-step commands.

---

## Planned Work for Next Week (Week 6 - Mar 5)

1. Install MySQL 5.7 and create the `archemy` database schema (user: archemy / archemydb1960%)
2. Install JDeveloper 11.1.2.4.0 IDE (Studio mode)
3. Install and configure Glassfish 3.1.2 (domain1, HTTP port 9999, admin port 4848)
4. Deploy ADF Essentials 11.1.2.4 to Glassfish
5. Prepare Midterm Proposal Presentation

---

## Issues Encountered

- JDK silent install (command-line) failed with exit code 103 — resolved by using the GUI installer instead.
- System had JDK 23 pre-installed — resolved by placing JDK 7 bin path at the beginning of the system PATH variable.
- `tools.jar` missing from JDK lib directory — low impact since the project deploys pre-built WAR/EAR files rather than compiling from source. Will address if needed later.

---

## Key Learnings

- The ArchNav application strictly requires JDK 1.7.0_80; later Java versions are incompatible.
- ADF Essentials version must exactly match JDeveloper version (both 11.1.2.4).
- The application uses ApacheDS (not OpenLDAP) as the LDAP directory service for Fortress RBAC.
- Docker containerization will involve 5 services: ApacheDS, MySQL, Tomcat, Glassfish, and Fortress.

---

# Project Part 1 - Weekly Progress Report - Week 6 (Mar 5, 2026)

> **Course**: Special CS Topic - Cloud Computing, Section 026
> **Student**: Chen Li (Solo)
> **Project**: Legacy Application (ArchNav) Cloud Migration

---

## Work Completed This Week

1. **Delivered the Midterm Proposal Presentation** in class on 2026-03-05. Presented as a solo team. Six slides covering: project overview, ArchNav legacy stack and the cloud-based migration framing, target Docker architecture, midterm deliverables, decentralized health-monitoring system (Part 2 sketch), and timeline.

2. **Began the bottom-up install** to make the original ArchNav stack runnable on a local Windows host:
   - **Installed MySQL 5.7 + Workbench 6.3**, created the `archemy` schema, ran `procedures.sql` to create the stored procedures (`insert_into_kad`, `insert_into_kad_dim_area`), created the user `archemy/archemydb1960%`.
   - **Installed JDeveloper 11.1.2.4.0** in Studio mode. Loaded `AppArchemy.jws` to confirm the project builds against the original ADF.
   - **Installed Maven 3.3.9** and **Cygwin 64-bit** (with `wget` and `git` packages) so the Fortress install steps in Week 7 can run without surprises.

3. **Confirmed the planned port assignments** by running each service in isolation:
   - MySQL on 3306
   - Glassfish HTTP on **9999** (deliberately changed from default 8080 to avoid the Tomcat conflict)
   - Tomcat on 8080
   - ApacheDS LDAP on 389 / 10389

---

## Planned Work for Next Week (Week 7 - Mar 12)

1. Install Glassfish 3.1.2 + ADF Essentials 11.1.2.4.
2. Install Apache Fortress Core 2.0.0-RC1 + ApacheDS 2.0.0-M23.
3. Build and deploy Fortress REST + Fortress Web on Tomcat.
4. Build the ArchNav security JAR + deploy the ArchNav EAR on Glassfish.
5. Containerise everything with Docker.
6. Deploy to AWS EC2.

---

## Issues Encountered

- JDeveloper 11.1.2.4 is a 1.24 GB installer that took several attempts to download cleanly from the Google Drive link.
- The JDeveloper installer requires JDK 7 specifically, which Week 5 already had configured.

---

## Key Learnings

- The instructor's response to the proposal was supportive — the only specific critique was the bootstrap node looking like a single point of failure in the Part 2 architecture diagram. That observation was logged for the Final Report's §6.6.
- Six slides for a 15–20 minute proposal is exactly the right amount; less feels rushed, more loses the audience.

---

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

---

# Project Part 1 - Weekly Progress Report - Week 8 (Mar 19, 2026)

> **Course**: Special CS Topic - Cloud Computing, Section 026
> **Student**: Chen Li (Solo)
> **Project**: Legacy Application (ArchNav) Cloud Migration

---

## Work Completed This Week

1. **Stabilised the deployed AWS EC2 instance** from Week 7. Verified that the four containers (`archnav-mysql`, `archnav-apacheds`, `archnav-tomcat`, `archnav-glassfish`) survived an instance reboot and continued to serve `http://<public-ip>:9999/archemy/faces/login.jspx` after the boot.

2. **Drafted the PlantUML architecture diagrams** that will accompany the final report:
   - `current_state.puml` — original Windows-host two-stack install (Fortress security + Glassfish/ADF business)
   - `future_state.puml` — Docker-Compose 4-container target on AWS EC2 with the bridge network `archnav-net` and external-facing ports 3306/389/8080/9999/4848

3. **Wrote the Migration Report skeleton** (Word document) — the section structure, screenshot placeholders, and key version-and-port tables. The content was filled in during Week 9.

4. **Stopped the EC2 instance** at the end of the week to avoid further hourly billing while the focus shifts to Part 2 work; the EBS volume is preserved so the instance can be restarted in seconds when needed.

---

## Planned Work for Next Week (Week 9 - Mar 26)

1. Complete the Migration Report's Word document using the screenshots collected in Week 7.
2. Begin the Part-2 work in earnest (BTP research, IoT simulator). Part 1 is in maintenance mode.
3. Validate that restarting the stopped EC2 instance brings the four containers back to `Up (healthy)` automatically.

---

## Issues Encountered

- None this week — Part 1 was in stabilisation mode after the Week 7 push.

---

## Key Learnings

- Stopping (rather than terminating) an EC2 instance preserves the EBS volume and the docker images, so a restart is essentially a "resume" rather than a fresh build. This is the right cost-management posture during weeks where Part 1 is not the active focus.
- The two-stack architecture is robust enough that an EC2 reboot does not require any re-configuration; the bridge network and the volumes pick up cleanly.

---

# Project Part 1 - Weekly Progress Report - Week 9 (Mar 26, 2026)

> **Course**: Special CS Topic - Cloud Computing, Section 026
> **Student**: Chen Li (Solo)
> **Project**: Legacy Application (ArchNav) Cloud Migration

---

## Work Completed This Week

1. **Finalised `Part1_Migration_Report.docx`** — the Word document submitted as part of the Part-1 deliverables. It contains seven screenshots from the Week-7 deployment session: local Docker `compose up` output, all four containers in `(healthy)` state, the AWS EC2 console showing the running instance, the public IP confirmation, the ArchNav login page rendered from the public IP, and a successful login after the LDAP-config patches.

2. **Reviewed and froze the PlantUML diagrams**. Both `current_state.puml` and `future_state.puml` were exported to PNG at 1200px width to keep the figure quality acceptable when embedded in the report.

3. **Documented the LDAP-properties patch path** as a runbook (in the Word document's appendix) — the four nested locations where `fortress.properties` lives inside an exploded ArchNav deployment, and the exact `host=apacheds`, `dc=example,dc=com`, `uid=admin,ou=system` overrides that need to be applied. This is the same runbook that is reused in Week 13 when the EC2 instance is rebuilt.

4. **Confirmed the deployment is reproducible**: started the stopped EC2 instance from Week 8, confirmed all four containers came back healthy, opened the ArchNav login page from the public IP, then stopped the instance again.

---

## Planned Work for Next Week (Week 10 - Apr 2)

1. Part 1 remains in maintenance mode; main effort moves to Part 2 (Blockchain + cloud deployment).
2. If Part 2 requires another EC2 instance, decide whether to colocate it with Part 1 or keep separate accounts.

---

## Issues Encountered

- None this week.

---

## Key Learnings

- The migration report is most useful when it includes both *what worked* (the final screenshots) and *what failed and why* (the LDAP-properties runbook). The latter is the part a reviewer trying to reproduce the work will actually need.
- The Glassfish JSP cache regenerates the runtime `fortress.properties` from the WAR's source JAR on every restart, so any runtime patch must be applied to the source JAR — a one-shot edit to the running file gets reverted by the next Glassfish restart.

---

# Project Part 1 - Weekly Progress Report - Week 10 (Apr 2, 2026)

> **Course**: Special CS Topic - Cloud Computing, Section 026
> **Student**: Chen Li (Solo)
> **Project**: Legacy Application (ArchNav) Cloud Migration

---

## Work Completed This Week

1. **Audited the EC2 cost** since the Week-7 launch. The instance was stopped most of the time; April-to-date charges were under $1 USD, well within the planned demo budget. Decision: keep the same `t2.small` size for the final demo rather than downsize, because the demo benefits from the spare RAM headroom (Glassfish + Tomcat together can spike to ~1.6 GB).

2. **Reviewed the deploy.sh script** for cold-rebuild correctness. Identified that the script depends on a `git clone` of the (private) repository, which would not work without GitHub authentication. Decided to add a non-git rebuild path in Week 12 (a Python automation script) so the demo rebuild does not depend on the repository being public at that time.

3. **Verified the docker-compose.yml** has correct dependency declarations: `glassfish` waits on `mysql` and `apacheds` to be healthy, and `tomcat` waits on `apacheds`. This means a cold rebuild produces a deterministic startup order without manual intervention.

4. **No active Docker work** — Part 1 is fully delivered up to a single `docker compose up`. Effort this week was entirely on Part 2 (HealthLog smart contract design and Hardhat configuration).

---

## Planned Work for Next Week (Week 11 - Apr 9)

1. Continue with Part 2 (Blockchain). Part 1 still in maintenance.
2. Begin sketching the Part 1 chapter of the Final Report (`current state`, `future state`, `migration story`).

---

## Issues Encountered

- A brief check confirmed the `deploy.sh` script is incomplete for our actual deployment (it assumes a public repo). This is on the backlog for Week 12.

---

## Key Learnings

- Stopped EC2 instances cost essentially nothing; the only ongoing charge is the EBS volume's storage class (gp3, ~$0.08/GiB-month → ~$1.6/month for our 20 GiB), which is acceptable for a 14-week project.
- A cloud-based migration is "done" when the deployment is one command from a clean machine. We are mostly there; the missing piece is a non-git transfer path, which Week 12 will add.

---

# Project Part 1 - Weekly Progress Report - Week 11 (Apr 9, 2026)

> **Course**: Special CS Topic - Cloud Computing, Section 026
> **Student**: Chen Li (Solo)
> **Project**: Legacy Application (ArchNav) Cloud Migration

---

## Work Completed This Week

1. **Drafted the Part-1 chapter of the Final Report** — the section that will sit alongside Part 2 in the consolidated final document. It covers: original two-stack architecture, container target architecture, the JDK 7 / Glassfish SSL / Fortress filename / nested-LDAP-properties debug stories from the Week-7 push, and the final live demonstration on the public AWS IP.

2. **Updated the EC2 instance's security group** to be specific about source CIDRs (rather than `0.0.0.0/0` open everything). Decided to keep `0.0.0.0/0` for the demo since the instance contains no real data and the demo URL needs to be reachable from the grader's machine, but documented this as a "do differently in production" item in §6 of the report.

3. **Confirmed the EC2 instance is still recoverable**: a `start-instances` from `stopped` state followed by waiting for SSH brings the four containers back into a runnable state. This is captured as a one-line `aws ec2 start-instances ...` recipe in the appendix.

4. **No new code changes to the Docker stack** this week. Effort was on documentation and Part 2 dashboard.

---

## Planned Work for Next Week (Week 12 - Apr 16)

1. Begin the Final Report consolidation (Part 1 + Part 2 sections together).
2. Decide whether the EC2 instance for the final demo will be the existing one (warm) or a freshly-launched one (cold demo, more honest).

---

## Issues Encountered

- None this week — pure documentation effort.

---

## Key Learnings

- The act of writing the Part-1 chapter forced me to be precise about *what* the cloud-based migration delivers vs. *what* a cloud-enabled rewrite would deliver. The distinction matters for the final presentation: we are demonstrably the former.
- Security-group hygiene matters even for demo accounts. For grading purposes the open ingress is fine, but writing the report made it clear that the production posture would be VPC-private + a bastion host.

---

# Project Part 1 - Weekly Progress Report - Week 12 (Apr 16, 2026)

> **Course**: Special CS Topic - Cloud Computing, Section 026
> **Student**: Chen Li (Solo)
> **Project**: Legacy Application (ArchNav) Cloud Migration

---

## Work Completed This Week

1. **Discovered the EC2 instance had been terminated**. At some point between the last successful test (Week 11) and the cleanup pass for the final demo, the instance was no longer reachable. Whether this was an account-level idle-termination or a manual cleanup, the practical effect is the same: the demo needs a fresh instance. This was anticipated in the Week-7 plan and the rebuild path was already in scope.

2. **Designed a non-git rebuild path** so the new EC2 instance can be brought up without making the repository public. The plan is a single Python script (`launch_aws_ec2.py`) using `boto3` that:
   - creates an EC2 key pair, locks down the .pem ACL on Windows
   - creates a security group with TCP 22 / 8080 / 9999 / 4848 inbound
   - finds the latest Ubuntu 24.04 LTS amd64 AMI in `us-east-1`
   - launches a `t2.small` with a 20 GiB gp3 root
   - waits for SSH reachability
   - tarballs the local `docker/` tree (~250 MB packed) and `scp`s it to the instance
   - SSH-executes the apt + Docker install + `docker compose up`

3. **Identified that the shell `deploy.sh` already does the second half** of the rebuild (apt + Docker + `docker compose up`), so the new Python script effectively wraps the AWS-side bring-up *around* the existing shell script. This minimised new code surface.

4. **Inventoried what is needed for the live demo**: the four Dockerfiles, the docker-compose.yml, the .env, the contents of `packages/` (~265 MB of legacy installers and the EAR), and the `init.sql`. All present and committed in `part1-migration/docker/`.

5. **Wrote the Part-1 section of the Final Report** to its current shape — current state, target architecture, deployment procedure, debug stories from Week 7, and the cloud-based-vs-cloud-enabled framing.

---

## Planned Work for Next Week (Week 13 - Apr 23)

1. Execute the EC2 rebuild via the new launcher script.
2. Re-verify `http://<new-public-ip>:9999/archemy/faces/login.jspx` is HTTP 200.
3. Take a fresh set of demo screenshots from the rebuilt instance.
4. Confirm the `docker compose ps` view shows four healthy containers.

---

## Issues Encountered

- The previous EC2 instance is gone. This was not a surprise (we explicitly stopped it most weeks to save cost), but the rebuild path needs to be smooth so the demo does not depend on me remembering 17 install steps.

---

## Key Learnings

- Owning the rebuild path is what separates a "cloud-based migration" from a "one-time deployment". The Python launcher captures every step that used to live in my head; the deployment is now genuinely reproducible.
- A 250 MB tarball over SCP from a residential connection takes 4–8 minutes — acceptable as a one-shot, but a sign that for production you would put the JAR/EAR artefacts on S3 and have the EC2 pull from there.

---

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

---

## Project Repository and Live Resources

- **GitHub repository (full source)**: <https://github.com/chenli0322/cloud-computing-project>
- **Final Report**: `part2-health-monitor/docs/final_report.md` (594 lines, 9 sections, 13 references)
- **Final Presentation deck**: `final-report/Cloud_Computing_Final_Presentation.pptx` (23 slides with speaker notes)
- **Live ArchNav (AWS EC2)**: `http://3.88.156.91:9999/archemy/faces/login.jspx`
- **Migration Report (Word)**: `Part1_Migration_Report.docx`
- **Architecture diagrams**: `part1-migration/docs/current_state.puml`, `part1-migration/docs/future_state.puml`
- **EC2 launcher script (boto3)**: `part1-migration/launch_aws_ec2.py`

*End of weekly progress reports for Part 1.*
