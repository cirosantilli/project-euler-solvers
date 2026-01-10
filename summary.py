#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
README_PATH = ROOT / "README.adoc"

ID_RE = re.compile(r"(\d+)")


def iter_table_rows(lines: list[str]) -> list[list[str]]:
    rows: list[list[str]] = []
    in_table = False
    found_header = False
    for raw in lines:
        line = raw.rstrip("\n")
        if line.startswith("|==="):
            if in_table and found_header:
                break
            in_table = True
            continue
        if not in_table or not line.startswith("|"):
            continue
        parts = [part.strip() for part in line.split("|")[1:]]
        if not found_header:
            if len(parts) >= 6 and parts[0] == "ID" and parts[-1] == "Error":
                found_header = True
            continue
        if len(parts) < 6:
            continue
        rows.append(parts[:6])
    return rows


def parse_rows(rows: list[list[str]]) -> tuple[dict[int, int], int]:
    solved_by_group: dict[int, int] = {}
    solved_by_pid: dict[int, bool] = {}
    max_pid = 0
    for parts in rows:
        match = ID_RE.search(parts[0])
        if not match:
            continue
        pid = int(match.group(1))
        max_pid = max(max_pid, pid)
        error = parts[5].strip()
        if pid not in solved_by_pid:
            solved_by_pid[pid] = False
        if not error:
            solved_by_pid[pid] = True

    for pid, solved in solved_by_pid.items():
        if not solved:
            continue
        group_start = (pid - 1) // 100 * 100 + 1
        solved_by_group[group_start] = solved_by_group.get(group_start, 0) + 1
    return solved_by_group, max_pid


def build_summary(solved_by_group: dict[int, int], max_pid: int) -> list[str]:
    if max_pid == 0:
        return ["* no entries found"]
    max_group_start = (max_pid - 1) // 100 * 100 + 1
    groups = []
    for start in range(1, max_group_start + 1, 100):
        solved = solved_by_group.get(start, 0)
        end = start + 99
        total = 100
        if start == max_group_start:
            end = max_pid
            total = end - start + 1
        groups.append((start, end, solved, total))

    done_prefix_end = 0
    for start, end, solved, total in groups:
        expected_start = done_prefix_end + 1
        if start != expected_start or solved != total or total != 100:
            break
        done_prefix_end = end

    output: list[str] = []
    if done_prefix_end >= 200:
        output.append(f"* **1-{done_prefix_end}**: done")
        groups = groups[done_prefix_end // 100 :]

    for start, end, solved, total in groups:
        output.append(f"* **{start}-{end}**: {solved}/{total}")
    return output


def update_readme_status(lines: list[str], summary_lines: list[str]) -> list[str]:
    for idx, line in enumerate(lines):
        if line.strip() != "// STATUS TABLE":
            continue
        start = idx + 1
        end = start
        while end < len(lines) and lines[end].startswith("* "):
            end += 1
        return lines[:start] + summary_lines + lines[end:]
    raise ValueError("STATUS TABLE marker not found or malformed")


def compute_summary_lines(lines: list[str]) -> list[str]:
    rows = iter_table_rows(lines)
    solved_by_group, max_pid = parse_rows(rows)
    return build_summary(solved_by_group, max_pid)


def autoupdate_readme(readme_path: Path = README_PATH) -> list[str]:
    lines = readme_path.read_text().splitlines()
    summary_lines = compute_summary_lines(lines)
    updated_lines = update_readme_status(lines, summary_lines)
    readme_path.write_text("\n".join(updated_lines) + "\n")
    return summary_lines


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Summarize solved Project Euler problems."
    )
    parser.add_argument(
        "-A",
        "--autoupdate",
        action="store_true",
        help="Update the status list in README.adoc before printing.",
    )
    args = parser.parse_args()

    try:
        lines = README_PATH.read_text().splitlines()
    except OSError as exc:
        print(f"error: failed to read {README_PATH}: {exc}", file=sys.stderr)
        return 2

    summary_lines = compute_summary_lines(lines)
    if args.autoupdate:
        try:
            updated_lines = update_readme_status(lines, summary_lines)
        except ValueError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
        try:
            README_PATH.write_text("\n".join(updated_lines) + "\n")
        except OSError as exc:
            print(f"error: failed to write {README_PATH}: {exc}", file=sys.stderr)
            return 2
    for line in summary_lines:
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
