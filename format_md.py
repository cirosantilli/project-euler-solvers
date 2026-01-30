#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

# import mdformat

ROOT = Path(__file__).resolve().parent
SOLVERS_DIR = ROOT / "solvers"
META_DIR = ROOT / "data" / "project-euler-statements" / "data" / "meta"


def load_title(pid: int) -> str:
    meta_path = META_DIR / f"{pid}.json"
    try:
        data = json.loads(meta_path.read_text())
    except OSError:
        return "Unknown Title"
    return str(data.get("title") or "Unknown Title")


def find_solver_files(pid: int) -> list[Path]:
    prefix = f"{pid}_"
    candidates: list[Path] = []
    for path in SOLVERS_DIR.glob(f"{pid}.*"):
        if path.suffix in {".md", ".json", ".out"}:
            continue
        candidates.append(path)
    for path in SOLVERS_DIR.glob(f"{pid}_*.*"):
        if path.suffix in {".md", ".json", ".out"}:
            continue
        candidates.append(path)
    def sort_key(path: Path) -> tuple[int, str, str]:
        suffix = path.suffix.lower()
        if suffix == ".py":
            return (0, "python", path.name.lower())
        if suffix == ".lean":
            return (1, "lean", path.name.lower())
        return (2, suffix.lstrip("."), path.name.lower())

    return sorted(candidates, key=sort_key)


def build_header(pid: int, title: str, files: list[Path]) -> list[str]:
    lines = [
        f"# Project Euler {pid} Solution - {title}",
        "",
        f"<https://projecteuler.net/problem={pid}>:",
    ]
    if files:
        lines.append("")
        for path in files:
            name = path.name
            lines.append(f"* [{name}]({name})")
    lines.append("")
    return lines


def strip_existing_prefix(lines: list[str], pid: int) -> list[str]:
    if not lines:
        return lines
    first = lines[0].strip()
    if first.startswith("#") and str(pid) in first:
        lines = lines[1:]
        while lines and lines[0].strip() == "":
            lines = lines[1:]
        if lines and f"projecteuler.net/problem={pid}" in lines[0]:
            lines = lines[1:]
        while lines and lines[0].strip() == "":
            lines = lines[1:]
        if lines and lines[0].strip() in {"Solutions:", "No solutions."}:
            lines = lines[1:]
        while lines and lines[0].lstrip().startswith("* ["):
            lines = lines[1:]
        while lines and lines[0].strip() == "":
            lines = lines[1:]
    return lines


def strip_markdown_fence(lines: list[str]) -> list[str]:
    if not lines:
        return lines
    idx = 0
    while idx < len(lines) and lines[idx].strip() == "":
        idx += 1
    if idx + 1 >= len(lines):
        return lines
    if lines[idx].strip() != "**":
        return lines
    if lines[idx + 1].strip() != "```markdown":
        return lines
    # Find closing fence; prefer a closing fence at the end.
    end_idx = None
    for j in range(len(lines) - 1, idx + 1, -1):
        if lines[j].strip() == "```":
            end_idx = j
            break
    if end_idx is None:
        return lines
    return lines[idx + 2 : end_idx]


def format_file(path: Path) -> bool:
    pid_str = path.stem
    if not pid_str.isdigit():
        return False
    pid = int(pid_str)
    title = load_title(pid)
    files = find_solver_files(pid)
    lines = path.read_text().splitlines()
    lines = strip_markdown_fence(lines)
    remaining = strip_existing_prefix(lines, pid)
    new_lines = build_header(pid, title, files) + remaining
    new_text = "\n".join(new_lines).rstrip() + "\n"
    # Caused too much destruction on the maths for now.
    # formatted = mdformat.text(new_text).rstrip() + "\n"
    if new_text == path.read_text():
        return False
    path.write_text(new_text)
    return True


def main() -> int:
    changed = 0
    paths = sorted(SOLVERS_DIR.glob("*.md"))
    total = len(paths)
    for idx, path in enumerate(paths, start=1):
        if idx == 1 or idx % 50 == 0 or idx == total:
            print(f"[{idx}/{total}] formatting {path.name}")
        if format_file(path):
            changed += 1
    print(f"Updated {changed} files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
