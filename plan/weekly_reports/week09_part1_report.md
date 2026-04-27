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
