from __future__ import annotations

from typing import List, Tuple


def fib(n: int) -> int:
    a, b = 1, 1
    if n <= 2:
        return 1
    for _ in range(3, n + 1):
        a, b = b, a + b
    return b


def patterns_differ(o: int, A: int, B: int, C: int, d_rev: List[int]) -> bool:
    # Build the full prefix values for the concrete q (encoded in o),
    # and the coefficient ordering for q -> infinity.
    d_list = d_rev[::-1]
    terms: List[Tuple[int, int, int, int]] = []
    v = o
    a = A
    b = B
    c = C
    for d in d_list:
        terms.append((v, a, b, c))
        v = 3 * v + 1
        a, b = 3 * a, 3 * b - c
        for _ in range(d):
            terms.append((v, a, b, c))
            v //= 2
            c *= 2
    terms.append((v, a, b, c))

    idxs = list(range(len(terms)))
    idxs.sort(key=lambda i: terms[i][0])
    rank1 = [0] * len(terms)
    for r, idx in enumerate(idxs, 1):
        rank1[idx] = r

    ordered: List[int] = []
    for idx in range(len(terms)):
        a1, b1, c1 = terms[idx][1], terms[idx][2], terms[idx][3]
        lo, hi = 0, len(ordered)
        while lo < hi:
            mid = (lo + hi) // 2
            j = ordered[mid]
            a2, b2, c2 = terms[j][1], terms[j][2], terms[j][3]
            left = a1 * c2
            right = a2 * c1
            if left < right or (left == right and b1 * c2 < b2 * c1):
                hi = mid
            else:
                lo = mid + 1
        ordered.insert(lo, idx)

    rank2 = [0] * len(terms)
    for r, idx in enumerate(ordered, 1):
        rank2[idx] = r
    return rank1 != rank2


def count_ambiguous_for_q(q: int, max_len: int) -> int:
    # Reverse-generate all valid d-lists from the last odd (2^q-1)/3.
    o_k = (1 << q) - 1
    o_k //= 3
    A, B, C = 1, 1, 3  # o_k = (2^q - 1) / 3
    amb = 0

    def dfs(o: int, A: int, B: int, C: int, length: int, d_rev: List[int]) -> None:
        nonlocal amb
        if length > max_len:
            return
        if d_rev and patterns_differ(o, A, B, C, d_rev):
            amb += 1
        max_d = max_len - length - 1
        if max_d < 1:
            return
        # parity condition for divisibility by 3
        parity = 0 if o % 3 == 1 else 1
        start = 2 if parity == 0 else 1
        for d in range(start, max_d + 1, 2):
            num = (1 << d) * o - 1
            if num % 3 != 0:
                continue
            o_prev = num // 3
            if o_prev <= 1:
                continue
            d_rev.append(d)
            dfs(o_prev, A * (1 << d), B * (1 << d) + C, C * 3, length + d + 1, d_rev)
            d_rev.pop()

    dfs(o_k, A, B, C, 1, [])
    return amb


def solve(m: int) -> int:
    base = fib(m)
    # Empirically, ambiguous lists only show up for small q.
    # We scan even q up to 16, which covers all observed cases for m <= 90.
    extra = 0
    for q in range(4, 18, 2):
        extra += count_ambiguous_for_q(q, m)
    return base + extra


def main() -> None:
    # Given examples
    assert solve(5) == 5
    assert solve(10) == 55
    assert solve(20) == 6771
    print(solve(90))


if __name__ == "__main__":
    main()
