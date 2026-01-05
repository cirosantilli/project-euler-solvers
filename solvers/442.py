#!/usr/bin/env python3
"""
Project Euler 442 - Eleven-free integers

An integer is called eleven-free if its decimal expansion does not contain any
substring representing a power of 11 except 1 (so 11, 121, 1331, ... are forbidden).

We compute E(10^18), where E(n) is the n-th positive eleven-free integer.
"""

from collections import deque
from functools import lru_cache


def build_automaton(max_digits: int):
    """
    Build an Aho-Corasick automaton over the forbidden substrings:
    decimal representations of 11^k for k>=1 with length <= max_digits.

    Returns:
        trans: list[list[int]]  (state transitions for digits 0..9)
        bad:   list[bool]       (True if state corresponds to having matched a forbidden pattern)
    """
    # Generate forbidden patterns up to the maximum possible length we will scan.
    patterns = []
    p = 11
    while True:
        s = str(p)
        if len(s) > max_digits:
            break
        patterns.append(s)
        p *= 11

    # Trie construction
    nxt = [dict()]  # digit -> next_state
    link = [0]  # failure links
    bad = [False]  # terminal or inherits terminal via failure link

    for pat in patterns:
        v = 0
        for ch in pat:
            d = ord(ch) - 48
            if d not in nxt[v]:
                nxt[v][d] = len(nxt)
                nxt.append({})
                link.append(0)
                bad.append(False)
            v = nxt[v][d]
        bad[v] = True

    # Failure links (BFS)
    q = deque()
    for d, u in nxt[0].items():
        link[u] = 0
        q.append(u)

    while q:
        v = q.popleft()
        for d, u in nxt[v].items():
            q.append(u)
            f = link[v]
            while f and d not in nxt[f]:
                f = link[f]
            link[u] = nxt[f].get(d, 0)
            bad[u] = bad[u] or bad[link[u]]

    # Full digit transitions 0..9 for all states
    n_states = len(nxt)
    trans = [[0] * 10 for _ in range(n_states)]
    for v in range(n_states):
        for d in range(10):
            if d in nxt[v]:
                trans[v][d] = nxt[v][d]
            else:
                f = v
                while f and d not in nxt[f]:
                    f = link[f]
                trans[v][d] = nxt[f].get(d, 0)

    return trans, bad


def count_eleven_free_upto(x: int, trans, bad) -> int:
    """
    Count eleven-free positive integers in [1, x], using digit-DP over the automaton.
    """
    if x <= 0:
        return 0

    digits = list(map(int, str(x)))
    D = len(digits)

    @lru_cache(None)
    def dp(pos: int, state: int, started: bool, tight: bool) -> int:
        if pos == D:
            return 1 if started else 0  # exclude 0

        limit = digits[pos] if tight else 9
        total = 0

        for dig in range(limit + 1):
            ntight = tight and (dig == limit)

            if not started and dig == 0:
                # Still skipping leading zeros; automaton not advanced.
                total += dp(pos + 1, 0, False, ntight)
            else:
                nstate = trans[state if started else 0][dig]
                if not bad[nstate]:
                    total += dp(pos + 1, nstate, True, ntight)

        return total

    return dp(0, 0, False, True)


def nth_eleven_free(n: int) -> int:
    """
    Return E(n): the n-th positive eleven-free integer.
    """
    if n <= 0:
        raise ValueError("n must be positive")

    high = n
    max_digits = len(str(high))
    trans, bad = build_automaton(max_digits)

    # Ensure the search interval [1, high] contains E(n)
    while count_eleven_free_upto(high, trans, bad) < n:
        high *= 2
        if len(str(high)) > max_digits:
            max_digits = len(str(high))
            trans, bad = build_automaton(max_digits)

    # Binary search for smallest x with count(x) >= n
    low = 1
    while low < high:
        mid = (low + high) // 2
        if count_eleven_free_upto(mid, trans, bad) >= n:
            high = mid
        else:
            low = mid + 1

    return low


def main() -> None:
    # Test values from the problem statement
    assert nth_eleven_free(3) == 3
    assert nth_eleven_free(200) == 213
    assert nth_eleven_free(500_000) == 531_563

    print(nth_eleven_free(10**18))


if __name__ == "__main__":
    main()
