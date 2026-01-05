from __future__ import annotations

from array import array
from typing import List


def sieve_spf(limit: int) -> array:
    spf = array("I", range(limit + 1))
    if limit >= 0:
        spf[0] = 0
    if limit >= 1:
        spf[1] = 1
    root = int(limit**0.5)
    for i in range(2, root + 1):
        if spf[i] == i:
            start = i * i
            step = i
            for j in range(start, limit + 1, step):
                if spf[j] == j:
                    spf[j] = i
    return spf


def compute_m(n: int, spf: array) -> int:
    if n == 1:
        return 0
    t = n
    prime_powers: List[int] = []
    while t > 1:
        p = spf[t]
        pk = 1
        while t % p == 0:
            t //= p
            pk *= p
        prime_powers.append(pk)
    if len(prime_powers) == 1:
        return 1
    es: List[int] = []
    for q in prime_powers:
        n_div = n // q
        inv = pow(n_div, -1, q)
        es.append(n_div * inv)
    sums = [0]
    min_gt = n
    for e in es:
        new_sums = []
        for s in sums:
            v = s + e
            if v >= n:
                v -= n
            if 1 < v < min_gt:
                min_gt = v
            new_sums.append(v)
        sums += new_sums
    return n + 1 - min_gt


def main() -> None:
    limit = 10_000_000
    spf = sieve_spf(limit)

    # Problem statement example.
    assert compute_m(6, spf) == 4

    total = 0
    spf_local = spf
    pow_local = pow
    for n in range(1, limit + 1):
        if n == 1:
            continue
        t = n
        p = spf_local[t]
        pk = 1
        while t % p == 0:
            t //= p
            pk *= p
        if t == 1:
            total += 1
            continue
        sums = [0]
        min_gt = n
        q = pk
        n_div = n // q
        inv = pow_local(n_div, -1, q)
        e = n_div * inv
        v = e
        if 1 < v < min_gt:
            min_gt = v
        sums.append(v)
        while t > 1:
            p = spf_local[t]
            pk = 1
            while t % p == 0:
                t //= p
                pk *= p
            q = pk
            n_div = n // q
            inv = pow_local(n_div, -1, q)
            e = n_div * inv
            new_sums = []
            for s in sums:
                v = s + e
                if v >= n:
                    v -= n
                if 1 < v < min_gt:
                    min_gt = v
                new_sums.append(v)
            sums += new_sums
        total += n + 1 - min_gt

    print(total)


if __name__ == "__main__":
    main()
