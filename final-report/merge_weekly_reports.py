"""
Concatenates all weekly progress reports for one Part into a single
submission document.

Run from final-report/:
    python merge_weekly_reports.py

Outputs:
    Part1_Weekly_Progress_Reports.md
    Part2_Weekly_Progress_Reports.md
"""
from __future__ import annotations
from pathlib import Path

HERE = Path(__file__).parent
WEEKLY = HERE.parent / "plan" / "weekly_reports"

GITHUB = "https://github.com/chenli0322/cloud-computing-project"


def build_part(part: int) -> str:
    weeks = sorted(WEEKLY.glob(f"week*_part{part}_report.md"))
    if not weeks:
        raise SystemExit(f"No weekly reports found for part {part}")

    title_map = {
        1: "Part 1 — Legacy Application (ArchNav) Cloud Migration",
        2: "Part 2 — Decentralized Health Monitoring System",
    }

    lines = []
    lines.append(f"# {title_map[part]}\n\n")
    lines.append("## Weekly Progress Reports — Spring 2026 Course Project\n\n")
    lines.append(f"> **Course**: Special CS Topic — Cloud Computing, Section 026\n")
    lines.append(f"> **Instructor**: Prof. Jean-Claude Franchitti\n")
    lines.append(f"> **Student**: Chen Li (NetID: cl5725) — solo team\n")
    lines.append(f"> **Repository**: <{GITHUB}>\n\n")
    lines.append("---\n\n")

    lines.append("## Table of Contents\n\n")
    for w in weeks:
        # Strip front matter from the title
        with open(w, encoding="utf-8") as f:
            content = f.read()
        first_line = content.splitlines()[0]
        # E.g. "# Project Part 1 - Weekly Progress Report - Week 5 (Feb 26, 2026)"
        title = first_line.lstrip("# ").strip()
        anchor = title.lower().replace(" ", "-").replace("(", "").replace(")", "").replace(",", "").replace(".", "")
        lines.append(f"- [{title}](#{anchor})\n")
    lines.append("\n---\n\n")

    for w in weeks:
        with open(w, encoding="utf-8") as f:
            content = f.read()
        # Drop the front matter lines (everything between first H1 and first ---)
        body_lines = content.splitlines()
        # Keep everything as-is; just append a separator before each
        lines.append(content.rstrip() + "\n\n")
        lines.append("---\n\n")

    # End matter: deliverables summary
    lines.append("## Project Repository and Live Resources\n\n")
    lines.append(f"- **GitHub repository (full source)**: <{GITHUB}>\n")
    lines.append("- **Final Report**: `part2-health-monitor/docs/final_report.md` (594 lines, 9 sections, 13 references)\n")
    lines.append("- **Final Presentation deck**: `final-report/Cloud_Computing_Final_Presentation.pptx` (23 slides with speaker notes)\n")
    if part == 1:
        lines.append("- **Live ArchNav (AWS EC2)**: `http://3.88.156.91:9999/archemy/faces/login.jspx`\n")
        lines.append("- **Migration Report (Word)**: `Part1_Migration_Report.docx`\n")
        lines.append("- **Architecture diagrams**: `part1-migration/docs/current_state.puml`, `part1-migration/docs/future_state.puml`\n")
        lines.append("- **EC2 launcher script (boto3)**: `part1-migration/launch_aws_ec2.py`\n")
    else:
        lines.append("- **HealthLog smart contract (Sepolia)**: `0x89983910f6AE98Ea081356148B433cA3C6de283B`\n")
        lines.append("  - Etherscan: <https://sepolia.etherscan.io/address/0x89983910f6AE98Ea081356148B433cA3C6de283B>\n")
        lines.append("- **AWS S3 off-chain audit store**: `s3://chenli-cloud-final-2026/anomalies/`\n")
        lines.append("- **Azure IoT Hub**: `ChenLi-iot-final-2026.azure-devices.net` (free-tier F1)\n")
        lines.append("- **Audit-chain reference transaction**: `0xe1ebf113bef9fd1f7fdc7d734f87da8b54d1c7fc724c7044da874965270e5b8b` at block `10 739 301`\n")
    lines.append("\n*End of weekly progress reports for Part {part}.*\n".format(part=part))

    return "".join(lines)


def main():
    for part in (1, 2):
        out = HERE / f"Part{part}_Weekly_Progress_Reports.md"
        text = build_part(part)
        out.write_text(text, encoding="utf-8")
        wc = sum(1 for _ in text.splitlines())
        print(f"Wrote {out}  ({wc} lines, {len(text):,} bytes)")


if __name__ == "__main__":
    main()
