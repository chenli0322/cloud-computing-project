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
