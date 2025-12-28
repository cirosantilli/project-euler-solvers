#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
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
    model: str | None
    output_tokens: int | None
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
    parser.add_argument(
        "-A",
        "--autoupdate",
        action="store_true",
        help="Update README.adoc results table with the latest run.",
    )
    parser.add_argument(
        "-u",
        "--uncommitted",
        action="store_true",
        help="Run only solvers modified or added since the last git commit.",
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


def collect_uncommitted_solvers() -> list[int]:
    try:
        proc = subprocess.run(
            ["git", "status", "--porcelain", "--", str(SOLVERS_DIR / "*.py")],
            capture_output=True,
            text=True,
            cwd=ROOT,
            check=False,
        )
    except OSError as exc:
        raise RuntimeError("Failed to run git to find uncommitted solvers.") from exc
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or "git status failed.")
    ids: list[int] = []
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        if not parts:
            continue
        path_str = parts[-1]
        path = Path(path_str)
        if path.suffix != ".py":
            continue
        if path.parent.name != "solvers":
            continue
        if path.stem.isdigit():
            ids.append(int(path.stem))
    return sorted(set(ids))


def load_solver_metadata(puzzle_id: int) -> tuple[str | None, int | None]:
    meta_path = SOLVERS_DIR / f"{puzzle_id}.json"
    if not meta_path.exists():
        return None, None
    try:
        payload = json.loads(meta_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None, None
    output_tokens = payload.get("output_tokens")
    model = payload.get("model")
    model_value = model if isinstance(model, str) else None
    tokens_value = output_tokens if isinstance(output_tokens, int) else None
    return model_value, tokens_value


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

def format_row(res: Result) -> str:
    time_cell = f"{res.elapsed:.3f}" if res.elapsed is not None else ""
    model_cell = res.model or ""
    tokens_cell = str(res.output_tokens) if res.output_tokens is not None else ""
    error_cell = "" if res.correct else res.message
    link = f"link:solvers/{res.puzzle_id}.py[{res.puzzle_id}]"
    return (
        f"| {link} | {time_cell} | {model_cell} | {tokens_cell} | {error_cell}"
    ).rstrip()

def update_readme(results: list[Result]) -> None:
    readme_path = ROOT / "README.adoc"
    lines = readme_path.read_text().splitlines()
    try:
        results_idx = next(i for i, line in enumerate(lines) if line.strip() == "== Results")
    except StopIteration:
        raise RuntimeError("Could not find Results section in README.adoc")

    start = None
    end = None
    for i in range(results_idx + 1, len(lines)):
        if lines[i].strip() == "|===":
            if start is None:
                start = i
            else:
                end = i
                break
    if start is None or end is None:
        raise RuntimeError("Could not find results table in README.adoc")

    header_line = "| ID | Runtime (s) | Model | Out Tokens | Error"
    row_re = re.compile(r"^\|\s+link:solvers/(\d+)\.py\[\d+\]\s+\|")
    result_map = {res.puzzle_id: format_row(res) for res in results}
    row_map: dict[int, str] = {}

    for i in range(start + 1, end):
        match = row_re.match(lines[i])
        if not match:
            continue
        pid = int(match.group(1))
        row_map[pid] = lines[i]

    for pid, row in result_map.items():
        row_map[pid] = row

    sorted_rows = [row_map[pid] for pid in sorted(row_map)]
    new_block = [header_line, *sorted_rows]
    lines[start + 1 : end] = new_block

    readme_path.write_text("\n".join(lines) + "\n")


def main() -> None:
    args = parse_args()
    reference = load_reference_answers()
    solvers = collect_solvers()

    if args.uncommitted:
        try:
            target_ids = collect_uncommitted_solvers()
        except RuntimeError as exc:
            print(str(exc), file=sys.stderr)
            sys.exit(2)
    elif args.ids:
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
                Result(
                    pid,
                    correct=False,
                    elapsed=None,
                    model=None,
                    output_tokens=None,
                    message="solver not found",
                )
            )
            print(f"[{pid}] skipped: solver not found", file=sys.stderr)
            continue

        expected = reference.get(pid)
        missing_reference = expected is None
        model, output_tokens = load_solver_metadata(pid)

        print(f"[{pid}] running {solver_path}")
        rc, stdout, stderr, elapsed, timed_out = run_solver(solver_path, args.timeout)
        if timed_out:
            limit = args.timeout if args.timeout is not None else elapsed
            results.append(
                Result(
                    pid,
                    correct=False,
                    elapsed=None,
                    model=model,
                    output_tokens=output_tokens,
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
                    model=model,
                    output_tokens=output_tokens,
                    message=f"failed (exit {rc})",
                )
            )
            print(f"[{pid}] failed (exit {rc})", file=sys.stderr)
            continue

        if missing_reference:
            results.append(
                Result(
                    pid,
                    correct=False,
                    elapsed=elapsed,
                    model=model,
                    output_tokens=output_tokens,
                    message="missing reference answer",
                )
            )
            print(f"[{pid}] missing reference answer", file=sys.stderr)
            continue

        actual = extract_answer(stdout)
        if actual == expected:
            results.append(
                Result(
                    pid,
                    correct=True,
                    elapsed=elapsed,
                    model=model,
                    output_tokens=output_tokens,
                    message="ok",
                )
            )
            print(f"[{pid}] ok ({elapsed:.3f}s)")
        else:
            msg = f"expected {expected!r}, got {actual!r}"
            results.append(
                Result(
                    pid,
                    correct=False,
                    elapsed=elapsed,
                    model=model,
                    output_tokens=output_tokens,
                    message=msg,
                )
            )
            print(f"[{pid}] wrong answer: {msg}", file=sys.stderr)

    total_run = len(results)
    passed = sum(r.correct for r in results)
    print(f"\nPassed {passed}/{total_run} tests.")

    print("\n|===")
    print("| ID | time (s) | model | Out Tokens | error")
    for res in sorted(results, key=lambda r: r.puzzle_id):
        print(format_row(res))
    print("|===")

    if args.autoupdate:
        update_readme(results)


if __name__ == "__main__":
    main()
