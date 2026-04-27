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
