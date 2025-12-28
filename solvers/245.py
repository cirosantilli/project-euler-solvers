from __future__ import annotations

import math
import random
from typing import Dict, List


LIMIT = 2 * 10**11


def sieve(n: int) -> List[int]:
    bs = bytearray(b"\x01") * (n + 1)
    bs[0:2] = b"\x00\x00"
    primes: List[int] = []
    for i in range(2, n + 1):
        if bs[i]:
            primes.append(i)
            if i * i <= n:
                bs[i * i : n + 1 : i] = b"\x00" * (((n - i * i) // i) + 1)
    return primes


def is_probable_prime(n: int) -> bool:
    if n < 2:
        return False
    small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]
    for p in small_primes:
        if n % p == 0:
            return n == p
    d = n - 1
    s = 0
    while d % 2 == 0:
        s += 1
        d //= 2
    for a in [2, 3, 5, 7, 11, 13]:
        if a >= n:
            continue
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True


def pollard_rho(n: int) -> int:
    if n % 2 == 0:
        return 2
    if n % 3 == 0:
        return 3
    while True:
        c = random.randrange(1, n - 1)
        x = random.randrange(2, n - 1)
        y = x
        d = 1
        while d == 1:
            x = (pow(x, 2, n) + c) % n
            y = (pow(y, 2, n) + c) % n
            y = (pow(y, 2, n) + c) % n
            d = math.gcd(abs(x - y), n)
        if d != n:
            return d


def factor(n: int, res: List[int]) -> None:
    if n == 1:
        return
    if is_probable_prime(n):
        res.append(n)
        return
    d = pollard_rho(n)
    factor(d, res)
    factor(n // d, res)


def divisors_from_factors(factors: List[int]) -> List[int]:
    counts: Dict[int, int] = {}
    for p in factors:
        counts[p] = counts.get(p, 0) + 1
    divs = [1]
    for p, exp in counts.items():
        cur = list(divs)
        mult = 1
        for _ in range(exp):
            mult *= p
            for d in divs:
                cur.append(d * mult)
        divs = cur
    return divs


def int_root(n: int, k: int) -> int:
    if k == 1:
        return n
    if k == 2:
        return int(math.isqrt(n))
    x = int(n ** (1.0 / k))
    while (x + 1) ** k <= n:
        x += 1
    while x**k > n:
        x -= 1
    return x


def main() -> None:
    random.seed(0)
    max_p = int(math.isqrt(LIMIT)) + 1
    primes = [p for p in sieve(max_p) if p >= 3]
    solutions = set()

    # k = 2 (semiprime) case via divisors of p^2 - p + 1
    for p in primes:
        s = p * p - p + 1
        fac: List[int] = []
        factor(s, fac)
        divs = divisors_from_factors(fac)
        for d in divs:
            if d < 2 * p - 1:
                continue
            q = d - p + 1
            if q <= p:
                continue
            if p * q > LIMIT:
                continue
            if is_probable_prime(q):
                solutions.add(p * q)

    # compute max possible number of prime factors
    prod = 1
    max_k = 0
    for p in primes:
        if prod * p > LIMIT:
            break
        prod *= p
        max_k += 1

    def try_last_prime(A: int, B: int, last_p: int) -> None:
        D = A - B
        if D <= 0:
            return
        r_max = LIMIT // A
        if r_max <= last_p:
            return
        num_min = B * (last_p - 1) - 1
        den_min = B + last_p * D
        u_min = num_min // den_min + 1
        if u_min < 1:
            u_min = 1
        num_max = B * (r_max - 1) - 1
        den_max = B + r_max * D
        if num_max < 0:
            return
        u_max = num_max // den_max
        u_max = min(u_max, (B - 1) // D)
        if u_max < u_min:
            return
        for u in range(u_min, u_max + 1):
            denom = B - u * D
            if denom <= 0:
                break
            numer = B * (u + 1) + 1
            if numer % denom != 0:
                continue
            r = numer // denom
            if r <= last_p or A * r > LIMIT:
                continue
            if is_probable_prime(r):
                n = A * r
                phi = B * (r - 1)
                if (n - 1) % (n - phi) == 0:
                    solutions.add(n)

    def dfs(idx: int, remaining: int, A: int, B: int, last_p: int) -> None:
        if remaining == 0:
            try_last_prime(A, B, last_p)
            return
        max_p_local = int_root(LIMIT // A, remaining + 1)
        for i in range(idx, len(primes)):
            p = primes[i]
            if p > max_p_local:
                break
            dfs(i + 1, remaining - 1, A * p, B * (p - 1), p)

    for k in range(3, max_k + 1):
        m = k - 1
        if m < 2:
            continue
        dfs(0, m, 1, 1, 2)

    result = sum(solutions)
    print(result)


if __name__ == "__main__":
    main()
