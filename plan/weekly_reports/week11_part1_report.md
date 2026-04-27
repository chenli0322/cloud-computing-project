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
