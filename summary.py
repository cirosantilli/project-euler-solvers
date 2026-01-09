#!/usr/bin/env python3
from __future__ import annotations

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
        group_start = (pid - 1) // 100 * 100
        solved_by_group[group_start] = solved_by_group.get(group_start, 0) + 1
    return solved_by_group, max_pid


def build_summary(solved_by_group: dict[int, int], max_pid: int) -> list[str]:
    if max_pid == 0:
        return ["* no entries found"]
    max_group_start = (max_pid - 1) // 100 * 100
    groups = []
    for start in range(0, max_group_start + 1, 100):
        solved = solved_by_group.get(start, 0)
        end = start + 100
        total = 100
        if start == max_group_start:
            total = max_pid - start
            end = start + total
        groups.append((start, end, solved, total))

    done_prefix = 0
    for start, end, solved, total in groups:
        if start != done_prefix or solved != total or total != 100:
            break
        done_prefix += 100

    output: list[str] = []
    if done_prefix >= 200:
        output.append(f"* 0-{done_prefix}: done")
        groups = groups[done_prefix // 100 :]

    for start, end, solved, total in groups:
        output.append(f"* {start}-{end}: {solved}/{total}")
    return output


def main() -> int:
    try:
        lines = README_PATH.read_text().splitlines()
    except OSError as exc:
        print(f"error: failed to read {README_PATH}: {exc}", file=sys.stderr)
        return 2

    rows = iter_table_rows(lines)
    solved_by_group, max_pid = parse_rows(rows)
    for line in build_summary(solved_by_group, max_pid):
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
