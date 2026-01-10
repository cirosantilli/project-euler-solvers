#!/usr/bin/env python3
"""
Project Euler 679: FREEFAREA

Alphabet S = {A, E, F, R}
Keywords: FREE, FARE, AREA, REEF

Let f(n) be the number of length-n words over S that contain each keyword
exactly once (as a contiguous substring).

This program computes f(30).
"""

from collections import deque

ALPHABET = ("A", "E", "F", "R")
PATTERNS = ("FREE", "FARE", "AREA", "REEF")


class AhoCorasick:
    """A tiny Aho–Corasick automaton for multiple substring matching."""

    __slots__ = ("next", "fail", "out", "trans")

    def __init__(self, patterns, alphabet):
        # Each node: next (dict char->node), fail (int), out (bitmask of matched patterns)
        self.next = [dict()]
        self.fail = [0]
        self.out = [0]

        for idx, pat in enumerate(patterns):
            self._add_pattern(pat, idx)

        self._build_fail_links()
        self._build_dense_transitions(alphabet)

    def _add_pattern(self, pat, idx):
        node = 0
        for ch in pat:
            nxt = self.next[node].get(ch)
            if nxt is None:
                nxt = len(self.next)
                self.next[node][ch] = nxt
                self.next.append({})
                self.fail.append(0)
                self.out.append(0)
            node = nxt
        self.out[node] |= 1 << idx

    def _build_fail_links(self):
        q = deque()
        # Initialize fail links of depth-1 nodes to root.
        for ch, child in self.next[0].items():
            self.fail[child] = 0
            q.append(child)

        while q:
            v = q.popleft()
            # Inherit outputs from failure state (captures suffix matches).
            self.out[v] |= self.out[self.fail[v]]

            for ch, u in self.next[v].items():
                f = self.fail[v]
                while f and ch not in self.next[f]:
                    f = self.fail[f]
                self.fail[u] = self.next[f][ch] if ch in self.next[f] else 0
                q.append(u)

    def _build_dense_transitions(self, alphabet):
        """Precompute goto for every node and letter (fast DP)."""
        m = len(self.next)
        k = len(alphabet)
        trans = [[0] * k for _ in range(m)]
        for s in range(m):
            for ai, ch in enumerate(alphabet):
                t = s
                while t and ch not in self.next[t]:
                    t = self.fail[t]
                trans[s][ai] = self.next[t][ch] if ch in self.next[t] else 0
        self.trans = trans


def count_words(n: int) -> int:
    """
    Count words of length n over ALPHABET that contain each PATTERN exactly once.
    """
    ac = AhoCorasick(PATTERNS, ALPHABET)
    num_states = len(ac.next)
    full_mask = (1 << len(PATTERNS)) - 1  # 0b1111

    # dp[state][mask] = number of ways
    dp = [[0] * (1 << len(PATTERNS)) for _ in range(num_states)]
    dp[0][0] = 1

    for _ in range(n):
        ndp = [[0] * (1 << len(PATTERNS)) for _ in range(num_states)]
        for s in range(num_states):
            row = dp[s]
            for mask, val in enumerate(row):
                if val == 0:
                    continue
                for ai in range(len(ALPHABET)):
                    ns = ac.trans[s][ai]
                    out = ac.out[ns]
                    # Reject if any keyword would be matched a second time.
                    if out & mask:
                        continue
                    ndp[ns][mask | out] += val
        dp = ndp

    return sum(dp[s][full_mask] for s in range(num_states))


def main() -> None:
    # Test values from the problem statement:
    assert count_words(9) == 1
    assert count_words(15) == 72863

    print(count_words(30))


if __name__ == "__main__":
    main()
