"""Project Euler 289: Eulerian Cycles

We count Eulerian *non-crossing* cycles on the circle arrangement E(m,n).

The key observation is that at every lattice point there are 8 incident arcs,
but they come in 4 adjacent pairs (north/east/south/west). A non-crossing local
traversal can be described by a non-crossing partition of these 4 directions.
There are Catalan(4)=14 such partitions; we enumerate them and do a transfer-
matrix / frontier dynamic programming sweep over the (n+1) x (m+1) lattice.

The DP keeps a compact encoding of the connectivity of the frontier (planar
connectivity / "bracket" state), and prevents closing a component early (which
would create additional disjoint cycles) so that the final result is a *single*
Eulerian cycle.

Answer requested: L(6,10) mod 1e10.
"""

from __future__ import annotations

from collections import defaultdict


MOD = 10**10


# The 14 non-crossing partitions of 4 items, written as 4 digits 1..4.
# Two positions are in the same block iff they have the same digit.
_CONNECTIONS = (
    1111,
    1114,
    1133,
    1134,
    1131,
    1211,
    1214,
    1221,
    1222,
    1224,
    1231,
    1232,
    1233,
    1234,
)


def _rep_state(s: int, m: int) -> int:
    """Canonicalize labels in a packed state.

    The state is a sequence of 4-bit labels (nibbles). We relabel in order of
    first appearance (scanning from least-significant nibble upwards) to
    0,1,2,... This keeps the state space small.
    """

    if s == 0:
        return 0

    mapping = [0] * 20
    nxt = 0
    out = 0
    i = 0
    # Same termination condition as the reference implementation:
    # stop after the last non-zero nibble.
    while (s >> (4 * i)) != 0:
        x = (s >> (4 * i)) & 15
        if mapping[x] == 0:
            nxt += 1
            mapping[x] = nxt
        out |= (mapping[x] - 1) << (4 * i)
        i += 1
    return out


def _merge_label(s: int, src: int, dst: int, m: int) -> int:
    """Replace all occurrences of label src with dst in the packed state."""

    if s == -1:
        return -1
    for i in range(m + 4):
        if ((s >> (4 * i)) & 15) == src:
            s ^= (src ^ dst) << (4 * i)
    return s


def _count_label(s: int, label: int, m: int) -> int:
    """Count occurrences of a label in the first (m+4) nibbles."""

    cnt = 0
    for _ in range(m + 4):
        cnt += (s & 15) == label
        s >>= 4
    return cnt


def _transitions(state: int, x: int, y: int, n: int, m: int, final: bool) -> list[int]:
    """All valid successor states at lattice point (x,y)."""

    get_nib = lambda idx: (state >> (4 * idx)) & 15

    new_color = 0 if (x == n or y == m) else 15
    colors = [get_nib(y), get_nib(y + 1), get_nib(y + 2), new_color]

    out: list[int] = []

    for C in _CONNECTIONS:
        a = C // 1000 - 1
        b = (C // 100) % 10 - 1
        c = (C // 10) % 10 - 1
        d = C % 10 - 1
        idx = (a, b, c, d)

        kk = (state << 4) | new_color

        # Boundary handling: "outside" label (0) may only appear in one block.
        ok = True
        for i in range(4):
            if colors[i] != 0:
                continue
            for j in range(4):
                if (colors[j] == 0) != (idx[i] == idx[j]):
                    ok = False
                    break
            if not ok:
                break
        if not ok:
            continue

        # Merge connectivity labels according to the partition blocks.
        for i in range(4):
            if i == idx[i]:
                continue
            src = new_color if i == 3 else (kk >> (4 * (y + i + 1))) & 15
            dst = (kk >> (4 * (y + idx[i] + 1))) & 15
            if src == 0:
                continue
            if dst == 0 or src == dst:
                kk = -1
                break
            kk = _merge_label(kk, src, dst, m)
        if kk == -1:
            continue

        # Slide the frontier: remove the inserted nibble and write it into slot (y+1).
        cur = kk & 15
        kk >>= 4
        old = (kk >> (4 * (y + 1))) & 15

        # If `old` would disappear, that would close a component early, creating
        # extra disjoint cycles. Only allow that at the very end.
        if _count_label(kk, old, m) > 1 or old == cur or final:
            kk ^= (cur ^ old) << (4 * (y + 1))
            if y == m:
                kk <<= 4
            out.append(_rep_state(kk, m))

    return out


def L(m: int, n: int, mod: int = MOD) -> int:
    """Compute L(m,n) mod `mod`."""

    # The configuration is symmetric under swapping axes.
    if m > n:
        m, n = n, m

    dp: dict[int, int] = {0: 1}
    cache: dict[tuple[int, int, int], list[int]] = {}

    for x in range(n + 1):
        for y in range(m + 1):
            final = x == n and y == m
            nxt = defaultdict(int)
            for st, ways in dp.items():
                new_color = 0 if (x == n or y == m) else 15
                if final:
                    trans = _transitions(st, x, y, n, m, final=True)
                else:
                    key = (st, y, new_color)
                    trans = cache.get(key)
                    if trans is None:
                        trans = _transitions(st, x, y, n, m, final=False)
                        cache[key] = trans
                for st2 in trans:
                    nxt[st2] = (nxt[st2] + ways) % mod
            dp = nxt
    return dp.get(0, 0) % mod


def solve() -> int:
    # Test values from the problem statement.
    assert L(1, 2) == 2
    assert L(2, 2) == 37
    assert L(3, 3) == 104290
    return L(6, 10)


if __name__ == "__main__":
    print(solve())
