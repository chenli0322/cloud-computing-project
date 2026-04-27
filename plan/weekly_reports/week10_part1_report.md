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
