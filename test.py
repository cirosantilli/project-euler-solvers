#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOLUTIONS_PATH = ROOT / "data/projecteuler-solutions/Solutions.md"
SOLVERS_DIR = ROOT / "solvers"
STATEMENTS_DOCS_DIR = ROOT / "data" / "project-euler-statements" / "data" / "documents"

LINE_RE = re.compile(r"^(\d+)\.\s+(.*)$")


@dataclass
class Result:
    puzzle_id: int
    correct: bool
    elapsed: float | None
    message: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run Project Euler solvers and verify their answers."
    )
    parser.add_argument(
        "ids",
        nargs="*",
        type=str,
        help="IDs or ranges to run (e.g. 2-4 6). Defaults to every solver.",
    )
    parser.add_argument(
        "-t",
        "--timeout",
        type=float,
        default=None,
        help="Per-solver timeout in seconds.",
    )
    return parser.parse_args()

def expand_ids(values: list[str]) -> list[int]:
    ids: list[int] = []
    for value in values:
        if "-" in value:
            start_str, sep, end_str = value.partition("-")
            if not sep:
                raise ValueError(f"invalid range: {value}")
            try:
                start = int(start_str)
                end = int(end_str)
            except ValueError as exc:
                raise ValueError(f"invalid range: {value}") from exc
            if start > end:
                raise ValueError(f"invalid range: {value}")
            ids.extend(range(start, end + 1))
        else:
            try:
                ids.append(int(value))
            except ValueError as exc:
                raise ValueError(f"invalid id: {value}") from exc
    return ids


def load_reference_answers() -> dict[int, str]:
    solutions: dict[int, str] = {}
    with SOLUTIONS_PATH.open() as fh:
        for line in fh:
            line = line.strip()
            match = LINE_RE.match(line)
            if not match:
                continue
            idx = int(match.group(1))
            solutions[idx] = match.group(2).strip()
    return solutions


def collect_solvers() -> dict[int, Path]:
    return {int(path.stem): path for path in SOLVERS_DIR.glob("*.py")}


def run_solver(
    path: Path, timeout: float | None
) -> tuple[int | None, str, str, float, bool]:
    start = time.perf_counter()
    try:
        proc = subprocess.run(
            ["pypy3", str(path)],
            capture_output=True,
            text=True,
            cwd=STATEMENTS_DOCS_DIR,
            timeout=timeout,
        )
        elapsed = time.perf_counter() - start
        return proc.returncode, proc.stdout, proc.stderr, elapsed, False
    except subprocess.TimeoutExpired as exc:
        elapsed = time.perf_counter() - start
        return None, exc.stdout or "", exc.stderr or "", elapsed, True


def extract_answer(raw_output: str) -> str:
    lines = [line.strip() for line in raw_output.splitlines() if line.strip()]
    return lines[-1] if lines else ""


def main() -> None:
    args = parse_args()
    reference = load_reference_answers()
    solvers = collect_solvers()

    if args.ids:
        try:
            target_ids = sorted(set(expand_ids(args.ids)))
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            sys.exit(2)
    else:
        target_ids = sorted(solvers)
    if not target_ids:
        print("No solvers found.", file=sys.stderr)
        sys.exit(1)

    results: list[Result] = []
    for pid in target_ids:
        solver_path = solvers.get(pid)
        if solver_path is None:
            results.append(
                Result(pid, correct=False, elapsed=None, message="solver not found")
            )
            print(f"[{pid}] skipped: solver not found", file=sys.stderr)
            continue

        expected = reference.get(pid)
        if expected is None:
            results.append(
                Result(
                    pid,
                    correct=False,
                    elapsed=None,
                    message="missing reference answer",
                )
            )
            print(f"[{pid}] skipped: missing reference answer", file=sys.stderr)
            continue

        print(f"[{pid}] running")
        rc, stdout, stderr, elapsed, timed_out = run_solver(solver_path, args.timeout)
        if timed_out:
            limit = args.timeout if args.timeout is not None else elapsed
            results.append(
                Result(
                    pid,
                    correct=False,
                    elapsed=None,
                    message=f"timed out after {limit:.3f}s",
                )
            )
            print(f"[{pid}] timed out after {limit:.3f}s", file=sys.stderr)
            continue

        if rc != 0:
            if stderr.strip():
                print(stderr.rstrip(), file=sys.stderr)
            results.append(
                Result(
                    pid,
                    correct=False,
                    elapsed=elapsed,
                    message=f"failed (exit {rc})",
                )
            )
            print(f"[{pid}] failed (exit {rc})", file=sys.stderr)
            continue

        actual = extract_answer(stdout)
        if actual == expected:
            results.append(Result(pid, correct=True, elapsed=elapsed, message="ok"))
            print(f"[{pid}] ok ({elapsed:.3f}s)")
        else:
            msg = f"expected {expected!r}, got {actual!r}"
            results.append(Result(pid, correct=False, elapsed=elapsed, message=msg))
            print(f"[{pid}] wrong answer: {msg}", file=sys.stderr)

    total_run = len(results)
    passed = sum(r.correct for r in results)
    print(f"\nPassed {passed}/{total_run} tests.")

    print("\n|===")
    print("| ID | time (s) | error")
    for res in sorted(results, key=lambda r: r.puzzle_id):
        time_cell = f"{res.elapsed:.3f}" if res.elapsed is not None else ""
        error_cell = "" if res.correct else res.message
        link = f"link:solvers/{res.puzzle_id}.py[{res.puzzle_id}]"
        print(f"| {link} | {time_cell} | {error_cell}")
    print("|===")


if __name__ == "__main__":
    main()
