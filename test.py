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

import lint
import summary

ROOT = Path(__file__).resolve().parent
SOLUTIONS_PATH = ROOT / "data/projecteuler-solutions/Solutions.md"
SOLVERS_DIR = ROOT / "solvers"
STATEMENTS_DOCS_DIR = ROOT / "data" / "project-euler-statements" / "data" / "documents"
STATEMENTS_PROBLEM_DIR = ROOT / "data" / "project-euler-statements" / "data" / "problem"

LINE_RE = re.compile(r"^(\d+)\.\s+(.*)$")
NUMERIC_RE = re.compile(r"^\d+(?:\.\d+)?$")


@dataclass
class Result:
    puzzle_id: int
    correct: bool
    elapsed: float | None
    model: str | None
    output_tokens: int | None
    message: str
    language: str | None
    source_path: Path | None


@dataclass
class SolverTarget:
    puzzle_id: int
    path: Path
    language: str


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
        default=600,
        help="Per-solver timeout in seconds.",
    )
    parser.add_argument(
        "-A",
        "--autoupdate",
        action="store_true",
        help="Update README.adoc results table with the latest run.",
    )
    parser.add_argument(
        "--autoupdate-not-found",
        action="store_true",
        help="Update README.adoc to mark only missing solvers (no runs).",
    )
    parser.add_argument(
        "--autoupdate-links",
        action="store_true",
        help="Update README.adoc to add missing .md links (no runs).",
    )
    parser.add_argument(
        "-l",
        "--lang",
        action="append",
        default=None,
        help="Limit to one or more languages (py,c,cpp,lean). Repeatable.",
    )
    parser.add_argument(
        "-u",
        "--uncommitted",
        action="store_true",
        help="Run only solvers modified or added since the last git commit.",
    )
    return parser.parse_args()


def expand_ids(values: list[str]) -> tuple[list[int], dict[int, list[Path]]]:
    ids: list[int] = []
    overrides: dict[int, list[Path]] = {}
    for value in values:
        if (
            "_" in value
            and not value.endswith(".py")
            and not value.endswith(".out")
            and "/" not in value
        ):
            candidate = SOLVERS_DIR / f"{value}.py"
            if not candidate.exists():
                raise ValueError(f"solver not found: {candidate}")
            pid = parse_solver_id(candidate)
            if pid is None:
                raise ValueError(f"invalid solver path: {candidate}")
            ids.append(pid)
            overrides.setdefault(pid, []).append(candidate)
            continue
        if value.endswith(".py") or value.endswith(".out") or "/" in value:
            path = Path(value)
            if not path.exists():
                raise ValueError(f"solver not found: {value}")
            pid = parse_solver_id(path)
            if pid is None:
                raise ValueError(f"invalid solver path: {value}")
            ids.append(pid)
            overrides.setdefault(pid, []).append(path)
            continue
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
    return ids, overrides


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


def load_statement_ids() -> set[int]:
    ids: set[int] = set()
    for path in STATEMENTS_PROBLEM_DIR.glob("*.html"):
        try:
            ids.add(int(path.stem))
        except ValueError:
            continue
    return ids


def collect_solver_targets(
    lang_filter: set[str] | None,
) -> dict[int, list[SolverTarget]]:
    targets: dict[int, list[SolverTarget]] = {}
    for path in SOLVERS_DIR.glob("*.py"):
        lang = detect_language(path)
        if lang is None or (lang_filter and lang not in lang_filter):
            continue
        pid = parse_solver_id(path)
        if pid is None:
            continue
        targets.setdefault(pid, []).append(SolverTarget(pid, path, lang))
    for path in SOLVERS_DIR.glob("*.out"):
        lang = detect_language(path)
        if lang is None or (lang_filter and lang not in lang_filter):
            continue
        pid = parse_solver_id(path)
        if pid is None:
            continue
        targets.setdefault(pid, []).append(SolverTarget(pid, path, lang))
    order = {"py": 0, "c": 1, "cpp": 2, "lean": 3}
    for entries in targets.values():
        entries.sort(key=lambda item: order.get(item.language, 99))
    return targets


def collect_solver_entries() -> dict[tuple[int, str], Path]:
    entries: dict[tuple[int, str], Path] = {}
    for path in SOLVERS_DIR.glob("*"):
        language = detect_language(path)
        if language is None:
            continue
        pid = parse_solver_id(path)
        if pid is None:
            continue
        key = (pid, language)
        source_path = path
        if path.suffix == ".out":
            candidate = source_from_target(path, language)
            if candidate.exists():
                source_path = candidate
        existing = entries.get(key)
        if existing is None:
            entries[key] = source_path
            continue
        if existing.suffix == ".out" and source_path.suffix != ".out":
            entries[key] = source_path
    return entries


def collect_uncommitted_solvers() -> list[int]:
    try:
        proc = subprocess.run(
            ["git", "status", "--porcelain", "--", str(SOLVERS_DIR)],
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
        if path.parent.name != "solvers":
            continue
        pid = parse_solver_id(path)
        if pid is not None:
            ids.append(pid)
    return sorted(set(ids))


def parse_solver_id(path: Path) -> int | None:
    stem = path.stem
    if stem.isdigit():
        return int(stem)
    if "_" in stem:
        prefix = stem.split("_", 1)[0]
        if prefix.isdigit():
            return int(prefix)
    return None


def detect_language(path: Path) -> str | None:
    if path.suffix == ".py":
        return "py"
    if path.suffix == ".c":
        return "c"
    if path.suffix == ".cpp":
        return "cpp"
    if path.suffix == ".lean":
        return "lean"
    if path.suffix == ".out":
        if path.stem.endswith("_c"):
            return "c"
        if path.stem.endswith("_cpp"):
            return "cpp"
        if path.stem.endswith("_lean"):
            return "lean"
    return None


def source_from_target(path: Path, language: str) -> Path:
    if language == "py":
        return path
    if language == "c":
        stem = path.stem.removesuffix("_c")
        return path.with_name(f"{stem}.c")
    if language == "cpp":
        stem = path.stem.removesuffix("_cpp")
        return path.with_name(f"{stem}.cpp")
    if language == "lean":
        stem = path.stem.removesuffix("_lean")
        return path.with_name(f"{stem}.lean")
    return path


def load_solver_metadata(
    puzzle_id: int, language: str | None
) -> tuple[str | None, int | None]:
    if not language:
        return None, None
    meta_path = SOLVERS_DIR / f"{puzzle_id}.{language}.json"
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
    path: Path, timeout: float | None, language: str
) -> tuple[int | None, str, str, float, bool]:
    solver_path = path.resolve()
    start = time.perf_counter()
    try:
        if language == "py":
            command = ["pypy3", str(solver_path)]
        else:
            command = [str(solver_path)]
        proc = subprocess.run(
            command,
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
    error_cell = "" if res.correct else normalize_error_cell(res.message)
    if res.message == "solver not found":
        link = f"{res.puzzle_id}.py"
    else:
        link_path = (
            res.source_path
            if res.source_path is not None
            else SOLVERS_DIR / f"{res.puzzle_id}.py"
        )
        try:
            rel_path = link_path.resolve().relative_to(ROOT)
        except ValueError:
            rel_path = link_path
        link = f"link:{rel_path.as_posix()}[{rel_path.name}]"
    explanation_cell = explanation_link(res.puzzle_id)
    return format_row_fields(
        link, explanation_cell, time_cell, model_cell, tokens_cell, error_cell
    )


def result_key(res: Result) -> tuple[int, str]:
    if res.source_path is not None:
        link_path = res.source_path
    else:
        link_path = SOLVERS_DIR / f"{res.puzzle_id}.py"
    language = res.language or detect_language(link_path) or ""
    return res.puzzle_id, language


def explanation_link(puzzle_id: int) -> str:
    md_path = SOLVERS_DIR / f"{puzzle_id}.md"
    if not md_path.exists():
        return ""
    try:
        rel_path = md_path.resolve().relative_to(ROOT)
    except ValueError:
        rel_path = md_path
    return f"link:{rel_path.as_posix()}[{md_path.name}]"


def looks_numeric(value: str) -> bool:
    return bool(NUMERIC_RE.match(value))


def row_has_statement(cells: list[str]) -> bool:
    if len(cells) < 2:
        return False
    if cells[1].startswith("link:"):
        return True
    if looks_numeric(cells[1]):
        return False
    if len(cells) >= 3 and (looks_numeric(cells[2]) or cells[2] == ""):
        return True
    return False


def normalize_row_fields(
    pid: int, cells: list[str]
) -> tuple[str, str, str, str, str, str] | None:
    if (
        len(cells) >= 6
        and cells[1].startswith("link:")
        and cells[2].startswith("link:")
    ):
        cells = [cells[0], cells[1], *cells[3:]]
    if len(cells) >= 6:
        id_cell, statement_cell, time_cell, model_cell, tokens_cell, error_cell = cells[
            :6
        ]
    elif len(cells) == 5:
        if row_has_statement(cells):
            id_cell, statement_cell, time_cell, model_cell, last_cell = cells
            if last_cell and not looks_numeric(last_cell):
                tokens_cell = ""
                error_cell = last_cell
            else:
                tokens_cell = last_cell
                error_cell = ""
        else:
            id_cell, time_cell, model_cell, tokens_cell, error_cell = cells
            statement_cell = explanation_link(pid)
    elif len(cells) == 4:
        id_cell, time_cell, model_cell, tokens_cell = cells
        statement_cell = explanation_link(pid)
        error_cell = ""
    else:
        return None
    if not statement_cell:
        statement_cell = explanation_link(pid)
    error_cell = normalize_error_cell(error_cell)
    return id_cell, statement_cell, time_cell, model_cell, tokens_cell, error_cell


def normalize_error_cell(value: str) -> str:
    if not value:
        return ""
    if value.startswith("error: "):
        return value
    return f"error: {value}"


def format_row_fields(
    id_cell: str,
    statement_cell: str,
    time_cell: str,
    model_cell: str,
    tokens_cell: str,
    error_cell: str,
) -> str:
    return (
        f"| {id_cell} | {statement_cell} | {time_cell} | "
        f"{model_cell} | {tokens_cell} | {error_cell}"
    ).rstrip()


def update_readme(results: list[Result]) -> None:
    readme_path = ROOT / "README.adoc"
    lines = readme_path.read_text().splitlines()
    try:
        results_idx = next(
            i for i, line in enumerate(lines) if line.strip() == "== Results"
        )
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

    header_line = "| ID | Explanation | Runtime (s) | Model | Out Tokens | Error"
    row_re = re.compile(r"^\|\s+link:([^\[]+)\[")
    plain_re = re.compile(r"^\|\s+(\d+)\.py\s+\|")
    result_map: dict[tuple[int, str], str] = {}
    row_map: dict[tuple[int, str], str] = {}

    for res in results:
        result_map[result_key(res)] = format_row(res)

    for i in range(start + 1, end):
        line = lines[i]
        match = row_re.match(line)
        if match:
            link_target = match.group(1)
            pid = parse_solver_id(Path(link_target))
            if pid is None:
                id_match = re.search(r"\\[(\\d+)\\]", line)
                if not id_match:
                    continue
                pid = int(id_match.group(1))
            language = detect_language(Path(link_target)) or ""
            cells = [cell.strip() for cell in line.split("|")[1:]]
            if cells and cells[-1] == "":
                cells = cells[:-1]
            normalized = normalize_row_fields(pid, cells)
            if normalized is None:
                continue
            id_cell, statement_cell, time_cell, model_cell, tokens_cell, error_cell = (
                normalized
            )
            row_map[(pid, language)] = format_row_fields(
                id_cell,
                statement_cell,
                time_cell,
                model_cell,
                tokens_cell,
                error_cell,
            )
            continue
        plain_match = plain_re.match(line)
        if not plain_match:
            continue
        pid_text = plain_match.group(1)
        if not pid_text:
            continue
        pid = int(pid_text)
        cells = [cell.strip() for cell in line.split("|")[1:]]
        if cells and cells[-1] == "":
            cells = cells[:-1]
        normalized = normalize_row_fields(pid, cells)
        if normalized is None:
            continue
        id_cell, statement_cell, time_cell, model_cell, tokens_cell, error_cell = (
            normalized
        )
        row_map[(pid, "py")] = format_row_fields(
            id_cell,
            statement_cell,
            time_cell,
            model_cell,
            tokens_cell,
            error_cell,
        )

    for key, row in result_map.items():
        row_map[key] = row

    sorted_rows = [row_map[key] for key in sorted(row_map, key=lambda k: (k[0], k[1]))]
    new_block = [header_line, *sorted_rows]
    lines[start + 1 : end] = new_block

    readme_path.write_text("\n".join(lines) + "\n")


def update_readme_links() -> None:
    readme_path = ROOT / "README.adoc"
    lines = readme_path.read_text().splitlines()
    try:
        results_idx = next(
            i for i, line in enumerate(lines) if line.strip() == "== Results"
        )
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

    header_line = "| ID | Explanation | Runtime (s) | Model | Out Tokens | Error"
    row_re = re.compile(r"^\|\s+link:([^\[]+)\[")
    plain_re = re.compile(r"^\|\s+(\d+)\.py\s+\|")
    row_map: dict[tuple[int, str], str] = {}

    for i in range(start + 1, end):
        line = lines[i]
        match = row_re.match(line)
        if match:
            link_target = match.group(1)
            pid = parse_solver_id(Path(link_target))
            if pid is None:
                continue
            language = detect_language(Path(link_target)) or ""
        else:
            plain_match = plain_re.match(line)
            if not plain_match:
                continue
            pid_text = plain_match.group(1)
            if not pid_text:
                continue
            pid = int(pid_text)
            language = "py"

        cells = [cell.strip() for cell in line.split("|")[1:]]
        if cells and cells[-1] == "":
            cells = cells[:-1]
        normalized = normalize_row_fields(pid, cells)
        if normalized is None:
            continue
        id_cell, statement_cell, time_cell, model_cell, tokens_cell, error_cell = (
            normalized
        )
        row_map[(pid, language)] = format_row_fields(
            id_cell,
            statement_cell,
            time_cell,
            model_cell,
            tokens_cell,
            error_cell,
        )

    sorted_rows = [row_map[key] for key in sorted(row_map, key=lambda k: (k[0], k[1]))]
    lines[start + 1 : end] = [header_line, *sorted_rows]
    readme_path.write_text("\n".join(lines) + "\n")


def update_readme_not_found() -> None:
    reference_ids = set(load_reference_answers())
    statement_ids = load_statement_ids()
    known_ids = reference_ids | statement_ids
    solver_entries = collect_solver_entries()
    solver_ids = {pid for pid, _language in solver_entries}
    readme_path = ROOT / "README.adoc"
    lines = readme_path.read_text().splitlines()
    try:
        results_idx = next(
            i for i, line in enumerate(lines) if line.strip() == "== Results"
        )
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

    row_re = re.compile(r"^\|\s+link:([^\[]+)\[")
    plain_re = re.compile(r"^\|\s+(\d+)\.py\s+\|")
    row_map: dict[tuple[int, str], str] = {}
    result_map: dict[tuple[int, str], str] = {}
    seen_ids: set[int] = set()

    for i in range(start + 1, end):
        line = lines[i]
        match = row_re.match(line)
        link_target = None
        if match:
            link_target = match.group(1)
            pid = parse_solver_id(Path(link_target))
            language = detect_language(Path(link_target)) or ""
        else:
            plain_match = plain_re.match(line)
            if not plain_match:
                continue
            pid_text = plain_match.group(1)
            if not pid_text:
                continue
            pid = int(pid_text)
            language = "py"

        seen_ids.add(pid)
        cells = [cell.strip() for cell in line.split("|")[1:]]
        if cells and cells[-1] == "":
            cells = cells[:-1]
        normalized = normalize_row_fields(pid, cells)
        if normalized is None:
            continue
        id_cell, statement_cell, time_cell, model_cell, tokens_cell, error_cell = (
            normalized
        )
        row_map[(pid, language)] = format_row_fields(
            id_cell,
            statement_cell,
            time_cell,
            model_cell,
            tokens_cell,
            error_cell,
        )
        if link_target:
            path = ROOT / link_target
        else:
            path = SOLVERS_DIR / f"{pid}.py"
        if path.exists():
            continue
        res = Result(
            puzzle_id=pid,
            correct=False,
            elapsed=None,
            model=None,
            output_tokens=None,
            message="solver not found",
            language=language,
            source_path=None,
        )
        result_map[result_key(res)] = format_row(res)

    for key, path in solver_entries.items():
        if key in row_map:
            continue
        pid, language = key
        res = Result(
            puzzle_id=pid,
            correct=False,
            elapsed=None,
            model=None,
            output_tokens=None,
            message="untested",
            language=language,
            source_path=path,
        )
        result_map[result_key(res)] = format_row(res)

    for pid in sorted(known_ids):
        if pid in seen_ids or pid in solver_ids:
            continue
        res = Result(
            puzzle_id=pid,
            correct=False,
            elapsed=None,
            model=None,
            output_tokens=None,
            message="solver not found",
            language="py",
            source_path=None,
        )
        result_map[result_key(res)] = format_row(res)

    for key, row in result_map.items():
        row_map[key] = row

    sorted_rows = [row_map[key] for key in sorted(row_map, key=lambda k: (k[0], k[1]))]
    lines[start + 1 : end] = [
        "| ID | Explanation | Runtime (s) | Model | Out Tokens | Error",
        *sorted_rows,
    ]

    readme_path.write_text("\n".join(lines) + "\n")


def parse_lang_filter(values: list[str] | None) -> set[str] | None:
    if not values:
        return None
    allowed = {"py", "c", "cpp", "lean"}
    selected: set[str] = set()
    for value in values:
        for token in value.split(","):
            token = token.strip().lower()
            if not token:
                continue
            if token not in allowed:
                raise ValueError(f"invalid language: {token}")
            selected.add(token)
    return selected


def main() -> None:
    args = parse_args()
    if args.autoupdate_links:
        update_readme_links()
        return
    if args.autoupdate_not_found:
        update_readme_not_found()
        return
    reference = load_reference_answers()
    try:
        lang_filter = parse_lang_filter(args.lang)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(2)
    solver_targets = collect_solver_targets(lang_filter)

    path_overrides: dict[int, list[Path]] = {}
    if args.uncommitted:
        try:
            target_ids = collect_uncommitted_solvers()
        except RuntimeError as exc:
            print(str(exc), file=sys.stderr)
            sys.exit(2)
    elif args.ids:
        try:
            target_ids, path_overrides = expand_ids(args.ids)
            target_ids = sorted(set(target_ids))
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            sys.exit(2)
    else:
        target_ids = sorted(solver_targets)
    if not target_ids:
        print("No solvers found.", file=sys.stderr)
        sys.exit(1)

    lint_paths: set[Path] = set()
    for pid in target_ids:
        override_paths = path_overrides.get(pid)
        targets = solver_targets.get(pid, [])
        if override_paths:
            for path in override_paths:
                language = detect_language(path)
                if language is None:
                    continue
                lint_paths.add(source_from_target(path, language))
        else:
            for target in targets:
                lint_paths.add(source_from_target(target.path, target.language))

    violations = lint.lint_paths(sorted(path for path in lint_paths if path.exists()))
    if violations:
        for line in lint.format_violations(violations, root=ROOT):
            print(line, file=sys.stderr)
        lint_results: list[Result] = []
        for violation in violations:
            language = detect_language(violation.path)
            lint_results.append(
                Result(
                    violation.puzzle_id,
                    correct=False,
                    elapsed=None,
                    model=None,
                    output_tokens=None,
                    message="lint failed",
                    language=language,
                    source_path=violation.path,
                )
            )
        print("\n|===")
        print("| ID | Explanation | Runtime (s) | Model | Out Tokens | Error")
        for res in sorted(lint_results, key=lambda r: (r.puzzle_id, r.language or "")):
            print(format_row(res))
        print("|===")
        if args.autoupdate:
            update_readme(lint_results)
            try:
                summary.autoupdate_readme()
            except (OSError, ValueError) as exc:
                print(f"summary update failed: {exc}", file=sys.stderr)
                sys.exit(2)
        sys.exit(1)

    results: list[Result] = []
    for pid in target_ids:
        override_paths = path_overrides.get(pid)
        targets: list[SolverTarget] = []
        if override_paths:
            for path in override_paths:
                language = detect_language(path)
                if language is None:
                    print(f"invalid solver path: {path}", file=sys.stderr)
                    sys.exit(2)
                if lang_filter and language not in lang_filter:
                    print(
                        f"solver path {path} does not match --lang filter",
                        file=sys.stderr,
                    )
                    sys.exit(2)
                targets.append(SolverTarget(pid, path, language))
        else:
            targets = solver_targets.get(pid, [])
        if not targets:
            results.append(
                Result(
                    pid,
                    correct=False,
                    elapsed=None,
                    model=None,
                    output_tokens=None,
                    message="solver not found",
                    language=None,
                    source_path=None,
                )
            )
            print(f"[{pid}] skipped: solver not found", file=sys.stderr)
            continue

        expected = reference.get(pid)
        missing_reference = expected is None
        for target in targets:
            model, output_tokens = load_solver_metadata(pid, target.language)
            label = f"{target.language}" if target.language else "unknown"
            print(f"[{pid}] running {target.path} ({label})")
            rc, stdout, stderr, elapsed, timed_out = run_solver(
                target.path, args.timeout, target.language
            )
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
                        language=target.language,
                        source_path=source_from_target(target.path, target.language),
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
                        language=target.language,
                        source_path=source_from_target(target.path, target.language),
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
                        language=target.language,
                        source_path=source_from_target(target.path, target.language),
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
                        language=target.language,
                        source_path=source_from_target(target.path, target.language),
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
                        language=target.language,
                        source_path=source_from_target(target.path, target.language),
                    )
                )
                print(f"[{pid}] wrong answer: {msg}", file=sys.stderr)

    total_run = len(results)
    passed = sum(r.correct for r in results)
    print(f"\nPassed {passed}/{total_run} tests.")

    print("\n|===")
    print("| ID | Explanation | Runtime (s) | Model | Out Tokens | Error")
    for res in sorted(results, key=lambda r: (r.puzzle_id, r.language or "")):
        print(format_row(res))
    print("|===")

    if args.autoupdate:
        update_readme(results)
        try:
            summary.autoupdate_readme()
        except (OSError, ValueError) as exc:
            print(f"summary update failed: {exc}", file=sys.stderr)
            sys.exit(2)


if __name__ == "__main__":
    main()
