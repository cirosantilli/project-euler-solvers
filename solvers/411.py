from __future__ import annotations

from array import array
from bisect import bisect_right
from math import gcd
from typing import Dict


def factor(n: int) -> Dict[int, int]:
    factors: Dict[int, int] = {}
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors[d] = factors.get(d, 0) + 1
            n //= d
        d += 1 if d == 2 else 2
    if n > 1:
        factors[n] = factors.get(n, 0) + 1
    return factors


def phi(n: int) -> int:
    factors = factor(n)
    result = n
    for p in factors:
        result //= p
        result *= p - 1
    return result


def multiplicative_order(a: int, n: int) -> int:
    if n == 1:
        return 1
    if gcd(a, n) != 1:
        raise ValueError("a and n must be coprime")
    ph = phi(n)
    factors = factor(ph)
    order = ph
    for p, exp in factors.items():
        for _ in range(exp):
            if order % p == 0 and pow(a, order // p, n) == 1:
                order //= p
            else:
                break
    return order


def lcm(a: int, b: int) -> int:
    return a // gcd(a, b) * b


def compute_S(n: int) -> int:
    n2 = n
    v2 = 0
    while n2 % 2 == 0:
        n2 //= 2
        v2 += 1

    n3 = n
    v3 = 0
    while n3 % 3 == 0:
        n3 //= 3
        v3 += 1

    preperiod = max(v2, v3)
    ord2 = 1 if n2 == 1 else multiplicative_order(2, n2)
    ord3 = 1 if n3 == 1 else multiplicative_order(3, n3)
    period = lcm(ord2, ord3)
    total = preperiod + period

    counts = array("I", [0]) * (n + 1)
    x = 1 % n
    for _ in range(total):
        counts[x] += 1
        x = (x * 2) % n

    running = 0
    for i in range(n):
        c = counts[i]
        counts[i] = running
        running += c
    counts[n] = running

    pos = counts[:-1]
    ys = array("I", [0]) * total

    x = 1 % n
    y = 1 % n
    for _ in range(total):
        idx = pos[x]
        ys[idx] = y
        pos[x] = idx + 1
        x = (x * 2) % n
        y = (y * 3) % n

    tails = []
    for x in range(n):
        start = counts[x]
        end = counts[x + 1]
        if start == end:
            continue
        if end - start == 1:
            y = ys[start]
            i = bisect_right(tails, y)
            if i == len(tails):
                tails.append(y)
            else:
                tails[i] = y
        else:
            segment = list(ys[start:end])
            segment.sort()
            for y in segment:
                i = bisect_right(tails, y)
                if i == len(tails):
                    tails.append(y)
                else:
                    tails[i] = y

    return len(tails)


def main() -> None:
    assert compute_S(22) == 5
    assert compute_S(123) == 14
    assert compute_S(10000) == 48

    total = 0
    for k in range(1, 31):
        total += compute_S(k**5)
    print(total)


if __name__ == "__main__":
    main()
