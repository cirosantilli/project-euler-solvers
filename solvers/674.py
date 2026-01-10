#!/usr/bin/env python3
"""
Project Euler 674: Solving I-equations

I(x, y) = (1 + x + y)^2 + y - x

Key facts used (see README.md):
- I is injective over non-negative integers, so I(a,b)=I(c,d) => a=c and b=d.
  Therefore solving e1=e2 is exactly first-order unification with constructor I.
- I is strictly increasing in each argument for x,y>=0, so once we have a
  most-general unifier, the least simultaneous value is obtained by setting all
  remaining free variables to 0 and evaluating.

The expressions file is normally provided by Project Euler. This script tries:
- ./p674_i_expressions.txt
- ./I-expressions.txt
and if not found, attempts to download:
  https://projecteuler.net/project/resources/p674_i_expressions.txt

No external libraries are used.
"""

from __future__ import annotations

import os
import sys
import urllib.request
from typing import Dict, List, Optional, Tuple, Union


MOD = 1_000_000_000
RESOURCE_URL = "https://projecteuler.net/project/resources/p674_i_expressions.txt"
CANDIDATE_FILES = ("p674_i_expressions.txt", "I-expressions.txt")


# ----------------------------
# Term representation
# ----------------------------

class Var:
    __slots__ = ("name",)

    def __init__(self, name: str) -> None:
        # intern for faster dict/compare
        self.name = sys.intern(name)


class INode:
    __slots__ = ("a", "b")

    def __init__(self, a: "Term", b: "Term") -> None:
        self.a = a
        self.b = b


Term = Union[Var, INode]


# ----------------------------
# Parsing
# ----------------------------

def parse_expr(s: str) -> Term:
    """Parse Expr := Var | I(Expr,Expr) where Var is one or more letters."""
    i = 0
    n = len(s)

    def parse() -> Term:
        nonlocal i
        if i >= n:
            raise ValueError("Unexpected end of input")

        if s[i] == "I":
            # Expect "I("
            if i + 1 >= n or s[i + 1] != "(":
                raise ValueError(f"Malformed I( at position {i}: {s}")
            i += 2  # skip "I("
            left = parse()
            if i >= n or s[i] != ",":
                raise ValueError(f"Expected ',' at position {i}: {s}")
            i += 1
            right = parse()
            if i >= n or s[i] != ")":
                raise ValueError(f"Expected ')' at position {i}: {s}")
            i += 1
            return INode(left, right)

        # Variable: one or more letters
        start = i
        while i < n and s[i].isalpha():
            i += 1
        if start == i:
            raise ValueError(f"Expected variable at position {i}: {s}")
        return Var(s[start:i])

    term = parse()
    if i != n:
        raise ValueError(f"Trailing junk at position {i}: {s[i:]} in {s}")
    return term


# ----------------------------
# Unification (with occurs check)
# ----------------------------

def unify(t1: Term, t2: Term) -> Optional[Dict[str, Term]]:
    """
    First-order unification where INode is a constructor and Var are variables.
    Returns a substitution mapping var-name -> term, or None if not unifiable.
    """
    subs: Dict[str, Term] = {}
    occ_cache: Dict[Tuple[str, int], bool] = {}

    def deref(t: Term) -> Term:
        # Chase substitutions, with light path compression for var->var chains.
        while isinstance(t, Var) and t.name in subs:
            nxt = subs[t.name]
            if isinstance(nxt, Var) and nxt.name in subs:
                subs[t.name] = subs[nxt.name]
            t = nxt
        return t

    def occurs(vname: str, t: Term) -> bool:
        # Iterative occurs-check under current substitutions.
        t = deref(t)
        key = (vname, id(t))
        if key in occ_cache:
            return occ_cache[key]

        stack = [t]
        seen_nodes = set()
        while stack:
            cur = deref(stack.pop())
            if isinstance(cur, Var):
                if cur.name == vname:
                    occ_cache[key] = True
                    return True
            else:
                nid = id(cur)
                if nid in seen_nodes:
                    continue
                seen_nodes.add(nid)
                stack.append(cur.a)
                stack.append(cur.b)

        occ_cache[key] = False
        return False

    stack = [(t1, t2)]
    while stack:
        a, b = stack.pop()
        a = deref(a)
        b = deref(b)

        if a is b:
            continue
        if isinstance(a, Var) and isinstance(b, Var) and a.name == b.name:
            continue

        if isinstance(a, Var):
            if occurs(a.name, b):
                return None
            subs[a.name] = b
            continue

        if isinstance(b, Var):
            if occurs(b.name, a):
                return None
            subs[b.name] = a
            continue

        if isinstance(a, INode) and isinstance(b, INode):
            stack.append((a.a, b.a))
            stack.append((a.b, b.b))
            continue

        return None

    return subs


# ----------------------------
# Evaluation at all-free-vars = 0
# ----------------------------

def i_op(x: int, y: int, mod: Optional[int]) -> int:
    if mod is None:
        s = 1 + x + y
        return s * s + y - x
    m = mod
    s = (1 + x + y) % m
    return (s * s + y - x) % m


def eval_term(root: Term, subs: Dict[str, Term], mod: Optional[int]) -> int:
    """
    Evaluate root under substitution subs, with any remaining free Var = 0.
    """
    memo: Dict[int, int] = {}

    def deref(t: Term) -> Term:
        while isinstance(t, Var) and t.name in subs:
            t = subs[t.name]
        return t

    sys.setrecursionlimit(1_000_000)

    def rec(t: Term) -> int:
        t = deref(t)
        if isinstance(t, Var):
            return 0
        tid = id(t)
        if tid in memo:
            return memo[tid]
        x = rec(t.a)
        y = rec(t.b)
        v = i_op(x, y, mod)
        memo[tid] = v
        return v

    return rec(root)


def least_simultaneous_value(e1: Term, e2: Term, mod: Optional[int]) -> int:
    sub = unify(e1, e2)
    if sub is None:
        return 0
    return eval_term(e1, sub, mod)


# ----------------------------
# Input loading
# ----------------------------

def load_expressions() -> List[str]:
    for fn in CANDIDATE_FILES:
        if os.path.exists(fn):
            with open(fn, "r", encoding="utf-8") as f:
                return [line.strip() for line in f if line.strip()]

    # Attempt download if missing locally
    try:
        with urllib.request.urlopen(RESOURCE_URL) as resp:
            data = resp.read().decode("utf-8")
    except Exception as e:
        raise RuntimeError(
            "Could not find expressions file locally and download failed. "
            f"Please place p674_i_expressions.txt next to this script. ({e})"
        ) from e

    # Save for convenience
    try:
        with open(CANDIDATE_FILES[0], "w", encoding="utf-8") as f:
            f.write(data)
    except Exception:
        pass

    return [line.strip() for line in data.splitlines() if line.strip()]


# ----------------------------
# Tests from the problem statement
# ----------------------------

def run_asserts() -> None:
    A = parse_expr("I(x,I(z,t))")
    B = parse_expr("I(I(y,z),y)")
    C = parse_expr("I(I(x,z),y)")

    ab = least_simultaneous_value(A, B, None)
    ac = least_simultaneous_value(A, C, None)
    bc = least_simultaneous_value(B, C, None)

    # Given: least simultaneous value of A and B is 23; A and C is 0; total over {A,B,C} is 26.
    assert ab == 23, ab
    assert ac == 0, ac
    assert ab + ac + bc == 26, (ab, ac, bc)


# ----------------------------
# Main solve
# ----------------------------

def main() -> None:
    run_asserts()

    lines = load_expressions()
    terms = [parse_expr(s) for s in lines]

    total = 0
    # local bindings for speed
    _unify = unify
    _eval = eval_term
    m = MOD

    n = len(terms)
    for i in range(n):
        ti = terms[i]
        for j in range(i + 1, n):
            sub = _unify(ti, terms[j])
            if sub is None:
                continue
            total = (total + _eval(ti, sub, m)) % m

    print(f"{total:09d}")  # last 9 digits (keep leading zeros)


if __name__ == "__main__":
    main()

