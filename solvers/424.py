#!/usr/bin/env python3
"""
Project Euler 424 - Kakuro
Solve 200 "cryptic kakuro" puzzles and print the sum of the decoded A..J numbers.

Input:
  Reads puzzle lines from a file named "0424_kakuro200.txt" in the current directory.

No external libraries are used (stdlib only).
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import permutations
from collections import defaultdict, deque
from pathlib import Path


INPUT_FILE = "0424_kakuro200.txt"


# ----------------------------------------------------------------------
# Bitmask helpers
# ----------------------------------------------------------------------

ALL10 = (1 << 10) - 1  # digits 0..9
DIGITS_1_9 = sum(1 << d for d in range(1, 10))


def popcount(x: int) -> int:
    return x.bit_count()


def iter_bits(mask: int):
    """Yield digits whose bits are set in mask, in increasing order."""
    while mask:
        b = mask & -mask
        yield b.bit_length() - 1
        mask ^= b


# ----------------------------------------------------------------------
# Parsing
# ----------------------------------------------------------------------


def split_tokens(line: str) -> list[str]:
    """Split comma-separated tokens, but ignore commas inside parentheses."""
    out: list[str] = []
    cur: list[str] = []
    depth = 0
    for ch in line.strip():
        if ch == "," and depth == 0:
            out.append("".join(cur))
            cur.clear()
            continue
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        cur.append(ch)
    out.append("".join(cur))
    return out


def parse_puzzle(line: str):
    """
    Returns (n, grid) where:
      n is 6 or 7 (information grid size),
      grid is a list of length n*n with entries:
        ('X', None)                 gray cell
        ('O', None)                 white empty cell
        ('L', 'A'..'J')             white prefilled letter-digit
        ('C', {'h':code, 'v':code}) clue cell with encrypted sums
    """
    toks = split_tokens(line)
    n = int(toks[0])
    cells = toks[1:]
    if len(cells) != n * n:
        raise ValueError("Bad puzzle encoding length")

    grid = []
    for t in cells:
        if t == "X":
            grid.append(("X", None))
        elif t == "O":
            grid.append(("O", None))
        elif len(t) == 1 and "A" <= t <= "J":
            grid.append(("L", t))
        elif t.startswith("(") and t.endswith(")"):
            inside = t[1:-1]
            parts = inside.split(",")
            sums = {}
            for part in parts:
                sums[part[0]] = part[1:]  # 'h' or 'v' -> code letters
            grid.append(("C", sums))
        else:
            raise ValueError(f"Unknown token: {t}")
    return n, grid


# ----------------------------------------------------------------------
# Kakuro constraint model
# ----------------------------------------------------------------------

# Precompute all ordered digit-tuples (permutations) of length <= 6 from digits 1..9,
# grouped by (length, sum). Each tuple already has distinct digits by construction.
MAX_RUN_LEN = 6
PERMS_BY_LEN_SUM: dict[int, dict[int, list[tuple[int, ...]]]] = {
    L: defaultdict(list) for L in range(1, MAX_RUN_LEN + 1)
}
_DIGITS = list(range(1, 10))
for L in range(1, MAX_RUN_LEN + 1):
    for p in permutations(_DIGITS, L):
        PERMS_BY_LEN_SUM[L][sum(p)].append(p)


@dataclass(frozen=True)
class RunConstraint:
    # Cell variables in this run, in order along the row/column
    cell_vars: tuple[int, ...]
    # Sum code letters (variable ids 0..9), length 1 or 2
    sum_letters: tuple[int, ...]
    # Unique involved variable ids (cells + sum letters)
    involved: tuple[int, ...]
    # Map var id -> index in `involved`
    inv_index: dict[int, int]
    length: int
    sums_list: tuple[int, ...]
    dup_cells: bool
    sum_same: bool


def build_csp(line: str):
    """
    Variables:
      - Letters A..J are variable ids 0..9, domains over digits 0..9 (bitmask).
      - Each 'O' cell is a fresh variable id >= 10, domain digits 1..9.
      - Each letter-filled cell references its letter variable (0..9), and that
        letter variable is restricted to digits 1..9 (no zeros in grid cells).

    Constraints:
      - All-different among the 10 letter variables.
      - For each run: digits in the run are all different (handled via precomputed permutations),
        sum(run digits) == decrypted clue sum.
    """
    n, grid = parse_puzzle(line)

    # Domains for letters A..J
    domains: list[int] = [ALL10] * 10
    for typ, val in grid:
        if typ == "L":
            domains[ord(val) - 65] &= DIGITS_1_9

    # Map white cells to variable ids
    cell_to_var: dict[tuple[int, int], int] = {}
    ocount = 0
    for r in range(n):
        for c in range(n):
            typ, val = grid[r * n + c]
            if typ == "O":
                cell_to_var[(r, c)] = 10 + ocount
                ocount += 1
            elif typ == "L":
                cell_to_var[(r, c)] = ord(val) - 65

    # Domains for 'O' cells
    domains.extend([DIGITS_1_9] * ocount)

    runs: list[RunConstraint] = []

    def add_run(code: str, cell_vars: list[int]):
        if not cell_vars:
            return
        sum_letters = (
            (ord(code) - 65,)
            if len(code) == 1
            else (ord(code[0]) - 65, ord(code[1]) - 65)
        )
        L = len(cell_vars)
        sums_list = tuple(PERMS_BY_LEN_SUM[L].keys())
        cell_vars_t = tuple(cell_vars)
        involved = tuple(sorted(set(cell_vars_t).union(sum_letters)))
        inv_index = {v: i for i, v in enumerate(involved)}
        runs.append(
            RunConstraint(
                cell_vars=cell_vars_t,
                sum_letters=sum_letters,
                involved=involved,
                inv_index=inv_index,
                length=L,
                sums_list=sums_list,
                dup_cells=(len(set(cell_vars_t)) != len(cell_vars_t)),
                sum_same=(len(sum_letters) == 2 and sum_letters[0] == sum_letters[1]),
            )
        )

    # Extract runs from clue cells
    for r in range(n):
        for c in range(n):
            typ, val = grid[r * n + c]
            if typ != "C":
                continue
            sums: dict[str, str] = val

            # Horizontal run to the right
            if "h" in sums:
                cc = c + 1
                cell_vars = []
                while cc < n and grid[r * n + cc][0] in ("O", "L"):
                    cell_vars.append(cell_to_var[(r, cc)])
                    cc += 1
                add_run(sums["h"], cell_vars)

            # Vertical run downward
            if "v" in sums:
                rr = r + 1
                cell_vars = []
                while rr < n and grid[rr * n + c][0] in ("O", "L"):
                    cell_vars.append(cell_to_var[(rr, c)])
                    rr += 1
                add_run(sums["v"], cell_vars)

    # Variable -> runs adjacency (for fast propagation)
    var_to_runs: list[list[int]] = [[] for _ in range(len(domains))]
    for i, run in enumerate(runs):
        for v in run.involved:
            var_to_runs[v].append(i)

    return domains, runs, var_to_runs


# ----------------------------------------------------------------------
# Propagation (generalized arc consistency for runs + all-different on letters)
# ----------------------------------------------------------------------


def enforce_all_diff_letters(dom: list[int]):
    """
    Simple all-different propagation:
      - If a letter is fixed to digit d, remove d from all other letters.
      - Detect contradictions where two letters are fixed to the same digit.
    Returns (changed_letter_ids, failed).
    """
    fixed_mask = 0
    seen = set()
    for i in range(10):
        if popcount(dom[i]) == 1:
            d = next(iter_bits(dom[i]))
            if d in seen:
                return (), True
            seen.add(d)
            fixed_mask |= 1 << d

    changed: list[int] = []
    for i in range(10):
        if popcount(dom[i]) > 1:
            new = dom[i] & ~fixed_mask
            if new == 0:
                return (), True
            if new != dom[i]:
                dom[i] = new
                changed.append(i)
    return tuple(changed), False


def process_run(run: RunConstraint, dom: list[int]):
    """
    GAC for one run constraint:
      - Enumerate all compatible decrypted sums for the clue letters.
      - For each such sum, enumerate all digit permutations of the run length producing that sum.
      - Keep only digits that appear in at least one satisfying assignment (support).
    Returns (changed_var_ids, failed).
    """
    if run.dup_cells:
        return (
            (),
            True,
        )  # repeated variable inside a run would force duplicate digits -> impossible

    support = [0] * len(run.involved)
    inv = run.inv_index
    cv = run.cell_vars
    L = run.length

    if len(run.sum_letters) == 1:
        l = run.sum_letters[0]
        li = inv[l]
        doml = dom[l]
        for S in run.sums_list:
            if S > 9:
                continue
            if not (doml & (1 << S)):
                continue
            for p in PERMS_BY_LEN_SUM[L][S]:
                ok = True
                for vid, d in zip(cv, p):
                    if not (dom[vid] & (1 << d)):
                        ok = False
                        break
                if not ok:
                    continue
                for vid, d in zip(cv, p):
                    support[inv[vid]] |= 1 << d
                support[li] |= 1 << S
    else:
        a, b = run.sum_letters
        ai, bi = inv[a], inv[b]
        if run.sum_same:
            doma = dom[a]
            for S in run.sums_list:
                if S < 10:
                    continue
                t, o = divmod(S, 10)
                if t != o:
                    continue
                if not (doma & (1 << t)):
                    continue
                for p in PERMS_BY_LEN_SUM[L][S]:
                    ok = True
                    for vid, d in zip(cv, p):
                        if not (dom[vid] & (1 << d)):
                            ok = False
                            break
                    if not ok:
                        continue
                    for vid, d in zip(cv, p):
                        support[inv[vid]] |= 1 << d
                    support[ai] |= 1 << t
        else:
            doma, domb = dom[a], dom[b]
            for S in run.sums_list:
                if S < 10:
                    continue
                t, o = divmod(S, 10)
                if t == o:
                    continue  # different letters => different digits
                if not (doma & (1 << t)) or not (domb & (1 << o)):
                    continue
                for p in PERMS_BY_LEN_SUM[L][S]:
                    ok = True
                    for vid, d in zip(cv, p):
                        if not (dom[vid] & (1 << d)):
                            ok = False
                            break
                    if not ok:
                        continue
                    for vid, d in zip(cv, p):
                        support[inv[vid]] |= 1 << d
                    support[ai] |= 1 << t
                    support[bi] |= 1 << o

    changed: list[int] = []
    for i, v in enumerate(run.involved):
        sup = support[i]
        if sup == 0:
            return (), True
        new = dom[v] & sup
        if new == 0:
            return (), True
        if new != dom[v]:
            dom[v] = new
            changed.append(v)
    return tuple(changed), False


def propagate(
    dom: list[int], runs: list[RunConstraint], var_to_runs: list[list[int]]
) -> bool:
    """
    Queue-based propagation: only re-check constraints that touch a changed variable.
    """
    q = deque(range(len(runs)))
    inq = [True] * len(runs)

    while True:
        changed_letters, fail = enforce_all_diff_letters(dom)
        if fail:
            return False
        for l in changed_letters:
            for ri in var_to_runs[l]:
                if not inq[ri]:
                    q.append(ri)
                    inq[ri] = True

        if not q:
            return True

        ri = q.popleft()
        inq[ri] = False
        changed_vars, fail = process_run(runs[ri], dom)
        if fail:
            return False
        for v in changed_vars:
            for rj in var_to_runs[v]:
                if not inq[rj]:
                    q.append(rj)
                    inq[rj] = True


# ----------------------------------------------------------------------
# Backtracking search
# ----------------------------------------------------------------------


def select_var(dom: list[int]) -> int | None:
    """Minimum Remaining Values heuristic."""
    best = None
    best_c = 999
    for i, m in enumerate(dom):
        c = popcount(m)
        if 1 < c < best_c:
            best_c = c
            best = i
            if c == 2:
                break
    return best


def solve(dom: list[int], runs: list[RunConstraint], var_to_runs: list[list[int]]):
    dom = dom[:]  # copy
    if not propagate(dom, runs, var_to_runs):
        return None

    v = select_var(dom)
    if v is None:
        return dom  # solved

    for d in iter_bits(dom[v]):
        dom2 = dom[:]
        dom2[v] = 1 << d
        sol = solve(dom2, runs, var_to_runs)
        if sol is not None:
            return sol
    return None


def mapping_to_number(sol_dom: list[int]) -> int:
    """Convert solved letter domains (A..J) to the 10-digit answer number."""
    num = 0
    for i in range(10):
        d = next(iter_bits(sol_dom[i]))
        num = num * 10 + d
    return num


def solve_puzzle(line: str) -> int:
    dom, runs, var_to_runs = build_csp(line)
    sol = solve(dom, runs, var_to_runs)
    if sol is None:
        raise RuntimeError("Puzzle has no solution (unexpected).")
    return mapping_to_number(sol)


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------


def read_puzzles(path: str = INPUT_FILE) -> list[str]:
    p = Path(path)
    lines = p.read_text(encoding="utf-8").splitlines()
    return [ln.strip() for ln in lines if ln.strip()]


def main() -> None:
    puzzles = read_puzzles(INPUT_FILE)
    answers = [solve_puzzle(ln) for ln in puzzles]

    # Test values given in the problem statement (for the official 200-puzzle file):
    assert answers[0] == 8426039571
    assert sum(answers[:10]) == 64414157580

    print(sum(answers))


if __name__ == "__main__":
    main()
