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
