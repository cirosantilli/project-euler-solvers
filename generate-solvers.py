#!/usr/bin/env python3
import argparse
import asyncio
import json
import re
import time
from datetime import datetime
from pathlib import Path

from openai import OpenAI, AsyncOpenAI


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Solve Project Euler statements via OpenAI (batch optional)."
    )
    parser.add_argument(
        "start",
        nargs="?",
        type=int,
        help="Optional start problem ID (inclusive).",
    )
    parser.add_argument(
        "end",
        nargs="?",
        type=int,
        help="Optional end problem ID (inclusive).",
    )
    parser.add_argument(
        "-m",
        "--model",
        default="gpt-5.2",
        help="OpenAI model name (default: gpt-5.2).",
    )
    parser.add_argument(
        "-M",
        "--max-output-tokens",
        type=int,
        default=None,
        help="Max output tokens per response (default: unlimited).",
    )
    parser.add_argument(
        "-E",
        "--reasoning-effort",
        default="high",
        choices=["low", "medium", "high"],
        help="Reasoning effort to use (default: high).",
    )
    parser.add_argument(
        "--completion-window",
        default="24h",
        help="Batch completion window (e.g. 24h).",
    )
    parser.add_argument(
        "-t",
        "--timeout",
        type=float,
        default=None,
        help="Per-request timeout in seconds.",
    )
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Re-run problems even if solver files already exist.",
    )
    parser.add_argument(
        "-b",
        "--batch",
        action="store_true",
        help="Submit as a batch job (default: off).",
    )
    parser.add_argument(
        "-D",
        "--dry-run",
        action="store_true",
        help="Write the JSONL file but do not call the API.",
    )
    return parser.parse_args()


def solver_ids(solvers_dir: Path) -> set[int]:
    ids: set[int] = set()
    for path in solvers_dir.glob("*.py"):
        if path.stem.isdigit():
            ids.add(int(path.stem))
    return ids


def statement_files(statements_dir: Path) -> list[Path]:
    files = [path for path in statements_dir.glob("*.md") if path.stem.isdigit()]
    return sorted(files, key=lambda p: int(p.stem))


def build_prompt(statement: str) -> str:
    return f'''TASK

Solve the following problem by coding a Python program that runs on pypy3. Add asserts for the test cases given in the problem statement if any, and a print with the final result at the end. Your code must run in a few minutes at most, usually a few seconds. Don't try to brute force the solution, only use brute forcing if needed to better understand the problem on small instances. Don't use external libraries, only the Python standard library. Don't use multithreading, only a single CPU core. Don't take input from stdin nor CLI arguments. If an external file is required sa input for the program, use the basename of the problem statement for it. Use typing for function signatures.

OUTPUT FORMAT

Produce the following output format within the triple quotes. Do not surround the Python implementation with triple quotes or any other delimiter.

```
main.py

<Python implementation>

README.md

<Markdown summary of the reasoning/insights used (high level; no chain-of-thought)>

PROBLEM
```

{statement.strip()}
'''


def build_requests(
    statements_dir: Path,
    solvers_dir: Path,
    model: str,
    max_output_tokens: int | None,
    reasoning_effort: str,
    start: int | None,
    end: int | None,
    force: bool,
) -> list[dict]:
    existing = solver_ids(solvers_dir) if not force else set()
    requests: list[dict] = []
    for path in statement_files(statements_dir):
        problem_id = int(path.stem)
        if start is not None and problem_id < start:
            continue
        if end is not None and problem_id > end:
            continue
        if problem_id in existing:
            continue
        statement = path.read_text(encoding="utf-8")
        prompt = build_prompt(statement)
        requests.append(
            {
                "custom_id": f"project-euler-{problem_id}",
                "method": "POST",
                "url": "/v1/responses",
                "body": {
                    "model": model,
                    "input": prompt,
                    "reasoning": {"effort": reasoning_effort},
                },
            }
        )
        if max_output_tokens is not None:
            requests[-1]["body"]["max_output_tokens"] = max_output_tokens
    return requests


def problem_id_from_custom_id(custom_id: str) -> int | None:
    if custom_id.startswith("project-euler-"):
        suffix = custom_id[len("project-euler-") :]
        if suffix.isdigit():
            return int(suffix)
    return None


def extract_response_text(response: object) -> str:
    output_text = getattr(response, "output_text", None)
    if isinstance(output_text, str) and output_text.strip():
        return output_text
    output = getattr(response, "output", None)
    if output:
        return "".join(_iter_output_text(output))
    return ""


def _iter_output_text(output: list) -> list[str]:
    parts: list[str] = []
    for item in output:
        content = None
        if isinstance(item, dict):
            content = item.get("content")
        else:
            content = getattr(item, "content", None)
        if not content:
            continue
        for chunk in content:
            if isinstance(chunk, dict):
                if chunk.get("type") == "output_text":
                    parts.append(chunk.get("text", ""))
            else:
                if getattr(chunk, "type", None) == "output_text":
                    parts.append(getattr(chunk, "text", ""))
    return parts


def response_error_message(response: object) -> str | None:
    error = getattr(response, "error", None)
    if error is None and isinstance(response, dict):
        error = response.get("error")
    if not error:
        return None
    if isinstance(error, dict):
        return error.get("message") or json.dumps(error, ensure_ascii=True)
    return str(error)


def response_status_info(response: object) -> tuple[str | None, str | None]:
    status = getattr(response, "status", None)
    if status is None and isinstance(response, dict):
        status = response.get("status")
    incomplete_details = getattr(response, "incomplete_details", None)
    if incomplete_details is None and isinstance(response, dict):
        incomplete_details = response.get("incomplete_details")
    incomplete_reason = None
    if isinstance(incomplete_details, dict):
        incomplete_reason = incomplete_details.get("reason")
    else:
        incomplete_reason = getattr(incomplete_details, "reason", None)
    return status, incomplete_reason


def response_output_tokens(response: object) -> int | None:
    usage = getattr(response, "usage", None)
    if usage is None and isinstance(response, dict):
        usage = response.get("usage")
    if not usage:
        return None
    output_tokens = getattr(usage, "output_tokens", None)
    if output_tokens is None and isinstance(usage, dict):
        output_tokens = usage.get("output_tokens")
    if isinstance(output_tokens, int):
        return output_tokens
    return None


def strip_code_fences(text: str) -> str:
    stripped = text.strip()
    if not stripped.startswith("```"):
        return stripped
    lines = stripped.splitlines()
    if len(lines) < 2:
        return stripped
    if not lines[0].startswith("```"):
        return stripped
    for idx in range(len(lines) - 1, 0, -1):
        if lines[idx].startswith("```"):
            return "\n".join(lines[1:idx]).strip()
    return stripped


def parse_sections(text: str) -> tuple[str | None, str | None]:
    match = re.search(
        r"(?is)\bmain\.py\b\s*(.*?)\s*\bREADME\.md\b\s*(.*)", text
    )
    if not match:
        return None, None
    main_text = strip_code_fences(match.group(1))
    readme_text = strip_code_fences(match.group(2))
    if not main_text or not readme_text:
        return None, None
    return main_text, readme_text


def solver_stem(
    solvers_dir: Path, problem_id: int, force: bool
) -> str | None:
    def stem_exists(stem: str) -> bool:
        return (
            (solvers_dir / f"{stem}.py").exists()
            or (solvers_dir / f"{stem}.md").exists()
            or (solvers_dir / f"{stem}.json").exists()
        )

    base_stem = str(problem_id)
    if not stem_exists(base_stem):
        return base_stem
    if not force:
        print(f"Skipping {problem_id}: solver files already exist.")
        return None
    suffix = 2
    while True:
        candidate = f"{problem_id}_{suffix}"
        if not stem_exists(candidate):
            return candidate
        suffix += 1


def write_solver_files(
    solvers_dir: Path,
    stem: str,
    main_text: str,
    readme_text: str,
) -> None:
    py_path = solvers_dir / f"{stem}.py"
    md_path = solvers_dir / f"{stem}.md"
    py_path.write_text(main_text.rstrip() + "\n", encoding="utf-8")
    md_path.write_text(readme_text.rstrip() + "\n", encoding="utf-8")
    current_mode = py_path.stat().st_mode
    py_path.chmod(current_mode | 0o111)


def write_solver_metadata(
    solvers_dir: Path,
    stem: str,
    output_tokens: int | None,
    model: str | None,
    reasoning_effort: str | None,
    input_prompt: str,
    duration_seconds: float | None,
) -> None:
    json_path = solvers_dir / f"{stem}.json"
    payload = {
        "output_tokens": output_tokens,
        "model": model,
        "reasoning_effort": reasoning_effort,
        "input_prompt": input_prompt,
        "duration_seconds": duration_seconds,
    }
    json_path.write_text(
        json.dumps(payload, ensure_ascii=True, indent=2) + "\n",
        encoding="utf-8",
    )


def write_jsonl(requests: list[dict], out_path: Path) -> None:
    with out_path.open("w", encoding="utf-8") as handle:
        for entry in requests:
            handle.write(json.dumps(entry, ensure_ascii=True) + "\n")

def print_requests(requests: list[dict]) -> None:
    for entry in requests:
        print(json.dumps(entry, ensure_ascii=True))


def request_problem_ids(requests: list[dict]) -> list[int]:
    ids: list[int] = []
    for request in requests:
        problem_id = problem_id_from_custom_id(request.get("custom_id", ""))
        if problem_id is not None:
            ids.append(problem_id)
    return ids


def format_problem_ids(problem_ids: list[int]) -> str:
    if not problem_ids:
        return "none"
    return ", ".join(str(problem_id) for problem_id in problem_ids)

async def _fetch_response(
    client: AsyncOpenAI,
    request: dict,
    timeout: float | None,
) -> dict:
    problem_id = problem_id_from_custom_id(request["custom_id"])
    started_at = time.monotonic()
    try:
        if timeout is not None:
            response = await client.with_options(
                timeout=timeout
            ).responses.create(**request["body"])
        else:
            response = await client.responses.create(**request["body"])
        return {
            "problem_id": problem_id,
            "response": response,
            "elapsed": time.monotonic() - started_at,
            "request": request,
        }
    except Exception as exc:
        return {
            "problem_id": problem_id,
            "error": exc,
            "elapsed": time.monotonic() - started_at,
            "request": request,
        }


async def submit_requests_async(
    requests: list[dict],
    timeout: float | None,
    solvers_dir: Path,
    force: bool,
) -> None:
    client = AsyncOpenAI()
    try:
        tasks = [
            asyncio.create_task(_fetch_response(client, request, timeout))
            for request in requests
        ]
        total = len(tasks)
        completed = 0
        for task in asyncio.as_completed(tasks):
            result = await task
            completed += 1
            handle_result(result, solvers_dir, force, completed, total)
    finally:
        close = getattr(client, "close", None)
        if close:
            result = close()
            if asyncio.iscoroutine(result):
                await result


def handle_result(
    result: dict,
    solvers_dir: Path,
    force: bool,
    completed: int,
    total: int,
) -> None:
    problem_id = result.get("problem_id")
    request = result.get("request")
    if problem_id is None or request is None:
        custom_id = None
        if isinstance(request, dict):
            custom_id = request.get("custom_id")
        if not custom_id:
            custom_id = "unknown"
        print(f"Skipping unexpected custom_id: {custom_id}")
        return
    elapsed = result.get("elapsed", 0.0)
    error = result.get("error")
    if error is not None:
        print(f"OpenAI request failed for problem {problem_id}: {error}")
        print(
            f"Request for problem {problem_id} completed in {elapsed:.2f}s "
            f"({completed}/{total})"
        )
        return
    response = result.get("response")
    error_message = response_error_message(response)
    status, incomplete_reason = response_status_info(response)
    if error_message:
        print(f"OpenAI error for problem {problem_id}: {error_message}")
        print(
            f"Request for problem {problem_id} completed in {elapsed:.2f}s "
            f"({completed}/{total})"
        )
        return
    if status and status != "completed":
        if incomplete_reason:
            print(
                f"OpenAI response {status} for problem {problem_id}: "
                f"{incomplete_reason}"
            )
        else:
            print(f"OpenAI response {status} for problem {problem_id}")
        print(
            f"Request for problem {problem_id} completed in {elapsed:.2f}s "
            f"({completed}/{total})"
        )
        return
    text = extract_response_text(response)
    main_text, readme_text = parse_sections(text)
    if not main_text or not readme_text:
        print(
            f"Failed to parse output for problem {problem_id}. Response: \n\n{text}\n"
        )
        print(
            f"Request for problem {problem_id} completed in {elapsed:.2f}s "
            f"({completed}/{total})"
        )
        return
    stem = solver_stem(solvers_dir, problem_id, force)
    if stem is None:
        print(
            f"Request for problem {problem_id} completed in {elapsed:.2f}s "
            f"({completed}/{total})"
        )
        return
    write_solver_files(solvers_dir, stem, main_text, readme_text)
    output_tokens = response_output_tokens(response)
    model = getattr(response, "model", None)
    if model is None and isinstance(response, dict):
        model = response.get("model")
    request_body = request.get("body", {})
    reasoning_effort = None
    if isinstance(request_body, dict):
        reasoning = request_body.get("reasoning")
        if isinstance(reasoning, dict):
            reasoning_effort = reasoning.get("effort")
    input_prompt = ""
    if isinstance(request_body, dict):
        input_prompt = request_body.get("input", "")
    write_solver_metadata(
        solvers_dir,
        stem,
        output_tokens,
        model,
        reasoning_effort,
        input_prompt,
        round(elapsed, 3),
    )
    print(
        f"Request for problem {problem_id} completed in {elapsed:.2f}s "
        f"({completed}/{total})"
    )


def main() -> None:
    args = parse_args()
    if args.start is not None and args.end is None:
        args.end = args.start
    if args.start is None and args.end is not None:
        raise SystemExit("Provide both start and end, or neither.")
    if args.start is not None and args.start > args.end:
        raise SystemExit("Start must be less than or equal to end.")
    root = Path(__file__).resolve().parent
    statements_dir = root / "data" / "project-euler-statements" / "data" / "md"
    solvers_dir = root / "solvers"
    requests = build_requests(
        statements_dir,
        solvers_dir,
        args.model,
        args.max_output_tokens,
        args.reasoning_effort,
        args.start,
        args.end,
        args.force,
    )
    if not requests:
        print("No unsolved statements found. Nothing to submit.")
        return
    if args.batch:
        client = OpenAI()
        batches_dir = root / "tmp" / "openai-batches"
        batches_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        jsonl_path = batches_dir / f"requests-{timestamp}.jsonl"
        write_jsonl(requests, jsonl_path)
        print(f"Wrote {len(requests)} requests to {jsonl_path}")
        if args.dry_run:
            print("Dry run enabled; not submitting batch.")
            return
        problem_ids = request_problem_ids(requests)
        print(
            "Submitting batch to OpenAI; this may take a while."
            f" Problems: {format_problem_ids(problem_ids)}"
        )
        print_requests(requests)
        uploaded = client.files.create(file=jsonl_path.open("rb"), purpose="batch")
        batch = client.batches.create(
            input_file_id=uploaded.id,
            endpoint="/v1/responses",
            completion_window=args.completion_window,
            metadata={"description": "project-euler batch"},
        )
        print(f"Batch submitted: {batch.id}")
        print(f"Input file: {uploaded.id}")
        return
    if args.dry_run:
        for request in requests:
            problem_id = problem_id_from_custom_id(request["custom_id"])
            print(f"Would solve problem {problem_id}")
        return
    problem_ids = request_problem_ids(requests)
    print(
        "Submitting requests to OpenAI; this may take a while."
        f" Problems: {format_problem_ids(problem_ids)}"
    )
    print_requests(requests)
    asyncio.run(
        submit_requests_async(requests, args.timeout, solvers_dir, args.force)
    )


if __name__ == "__main__":
    main()
