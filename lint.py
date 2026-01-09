#!/usr/bin/env python3
from __future__ import annotations

import io
import re
import sys
import tokenize
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOLUTIONS_PATH = ROOT / "data/projecteuler-solutions/Solutions.md"
SOLVERS_DIR = ROOT / "solvers"

LINE_RE = re.compile(r"^(\d+)\.\s+(.*)$")


def load_reference_answers() -> dict[int, str]:
    solutions: dict[int, str] = {}
    with SOLUTIONS_PATH.open() as fh:
        for line in fh:
            line = line.strip()
            match = LINE_RE.match(line)
            if not match:
                continue
            pid = int(match.group(1))
            solutions[pid] = match.group(2).strip()
    return solutions


def parse_solver_id(path: Path) -> int | None:
    stem = path.stem
    if stem.isdigit():
        return int(stem)
    if "_" in stem:
        prefix = stem.split("_", 1)[0]
        if prefix.isdigit():
            return int(prefix)
    return None


def iter_solver_sources() -> list[Path]:
    sources: list[Path] = []
    for ext in (".py", ".c", ".cpp"):
        sources.extend(SOLVERS_DIR.glob(f"*{ext}"))
    return sorted(sources)


def should_scan_answer(answer: str) -> bool:
    return len(answer) > 1


def python_comment_or_string_hits(text: str, answer: str) -> list[int]:
    hits: list[int] = []
    reader = io.StringIO(text).readline
    try:
        for tok in tokenize.generate_tokens(reader):
            if tok.type in (tokenize.COMMENT, tokenize.STRING):
                if answer in tok.string:
                    hits.append(tok.start[0])
    except tokenize.TokenError:
        return hits
    return hits


def python_line_hits(text: str, answer: str) -> list[int]:
    hits: list[int] = []
    for idx, line in enumerate(text.splitlines(), 1):
        if answer not in line:
            continue
        stripped = line.strip()
        if re.search(r"\bassert\b", line):
            hits.append(idx)
            continue
        if re.search(r"\breturn\b", line) and answer in line:
            hits.append(idx)
            continue
        if re.search(r"\bprint\s*\(", line) and answer in line:
            hits.append(idx)
            continue
        if stripped.startswith("#"):
            hits.append(idx)
            continue
    return hits


def c_comment_hits(text: str, answer: str) -> list[int]:
    hits: list[int] = []
    in_block = False
    for idx, line in enumerate(text.splitlines(), 1):
        if in_block:
            if answer in line:
                hits.append(idx)
            if "*/" in line:
                in_block = False
            continue
        if "/*" in line:
            in_block = True
            if answer in line:
                hits.append(idx)
            if "*/" in line:
                in_block = False
            continue
        if "//" in line:
            if answer in line.split("//", 1)[1]:
                hits.append(idx)
    return hits


def c_line_hits(text: str, answer: str) -> list[int]:
    hits: list[int] = []
    in_block = False
    for idx, line in enumerate(text.splitlines(), 1):
        if in_block:
            if "*/" in line:
                in_block = False
            continue
        if "/*" in line:
            if "*/" not in line:
                in_block = True
            continue
        if "//" in line:
            line = line.split("//", 1)[0]
        if answer not in line:
            continue
        if re.search(r"\breturn\b", line):
            hits.append(idx)
            continue
        if re.search(r"\bprintf\s*\(", line):
            hits.append(idx)
            continue
    return hits


def main() -> int:
    answers = load_reference_answers()
    violations: list[tuple[int, Path, str, list[tuple[int, str]]]] = []
    for path in iter_solver_sources():
        pid = parse_solver_id(path)
        if pid is None:
            continue
        answer = answers.get(pid)
        if not answer or not should_scan_answer(answer):
            continue
        try:
            text = path.read_text()
        except OSError as exc:
            print(f"error: failed to read {path}: {exc}", file=sys.stderr)
            return 2
        if path.suffix == ".py":
            line_hits = python_comment_or_string_hits(text, answer)
            line_hits += python_line_hits(text, answer)
        else:
            line_hits = c_comment_hits(text, answer)
            line_hits += c_line_hits(text, answer)
        if line_hits:
            lines = text.splitlines()
            hit_lines = sorted(set(line_hits))
            context = [
                (line_no, lines[line_no - 1].rstrip())
                for line_no in hit_lines
                if 0 < line_no <= len(lines)
            ]
            violations.append((pid, path, answer, context))

    if not violations:
        print("ok: no reference answers found in solver sources.")
        return 0

    print("error: reference answers found in solver sources:")
    for pid, path, answer, context in violations:
        rel = path.relative_to(ROOT)
        print(f"- {pid}: {rel} contains {answer!r}")
        for line_no, line in context:
            print(f"  line {line_no}: {line}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
