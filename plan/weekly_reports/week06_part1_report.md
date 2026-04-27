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
