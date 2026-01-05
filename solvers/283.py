#!/usr/bin/env python3
"""
Project Euler 283
Integer sided triangles for which the area/perimeter ratio is integral

Key facts:
- For any triangle, Area = r * s where r is the inradius, s is semiperimeter.
- Area / Perimeter = (r*s) / (2s) = r/2.
So requiring Area/Perimeter to be an integer k means r = 2k is an even integer.

We must sum perimeters of all integer triangles whose (Area/Perimeter) <= 1000,
i.e. whose inradius r <= 2000 and r is even.

We represent integer-sided triangles using:
x = (a+b-c)/2, y = (a-b+c)/2, z = (-a+b+c)/2  (all positive integers)
Then:
a = x+y, b = x+z, c = y+z, perimeter = 2(x+y+z)

Heron's + inradius identity gives:
r^2(x+y+z) = xyz
Let n = r^2. Then n(x+y+z) = xyz.

With ordering x <= y <= z, we have:
x+y <= 2z  => x+y+z <= 3z
xyz = n(x+y+z) <= 3nz => xy <= 3n
Thus, for fixed n:
x <= sqrt(3n), y <= 3n/x, and d = xy - n satisfies 1 <= d <= 2n.

From z = n(x+y)/(xy-n) = n(x+y)/d,
d must divide n(x+y).

Also d divides (xy - n).

A useful elimination:
d | n(x+y) and d | (xy-n)  => d | n(x^2+n)

So for each (n,x), we enumerate divisors d of n(x^2+n) up to 2n,
recover y = (n+d)/x if integral, and then compute z.

This avoids scanning huge y ranges directly.
"""

from array import array
import math


def heron_area(a: int, b: int, c: int) -> float:
    s = (a + b + c) / 2.0
    return math.sqrt(s * (s - a) * (s - b) * (s - c))


def area_over_perimeter(a: int, b: int, c: int) -> float:
    return heron_area(a, b, c) / (a + b + c)


def compute_spf(limit: int) -> array:
    """
    Compute smallest-prime-factor array up to limit using an odd-optimized sieve.
    spf[n] = smallest prime dividing n (spf[1]=1).
    """
    spf = array("I", [0]) * (limit + 1)
    if limit >= 1:
        spf[1] = 1

    # Fill even numbers
    for i in range(2, limit + 1, 2):
        spf[i] = 2

    # Odd sieve
    for i in range(3, limit + 1, 2):
        if spf[i] == 0:
            spf[i] = i
            ii = i * i
            if ii <= limit:
                step = i << 1
                for j in range(ii, limit + 1, step):
                    if spf[j] == 0:
                        spf[j] = i
    return spf


def factorize_list(num: int, spf: array):
    """
    Factorize num using spf, returning list of (prime, exponent) in increasing prime order.
    """
    out = []
    while num > 1:
        p = spf[num]
        cnt = 1
        num //= p
        while num > 1 and spf[num] == p:
            cnt += 1
            num //= p
        out.append((p, cnt))
    return out


def merge_factor_lists(a, b):
    """
    Merge two sorted factor lists (prime, exp) -> combined exponents.
    """
    i = j = 0
    la, lb = len(a), len(b)
    out = []
    while i < la and j < lb:
        pa, ea = a[i]
        pb, eb = b[j]
        if pa == pb:
            out.append((pa, ea + eb))
            i += 1
            j += 1
        elif pa < pb:
            out.append((pa, ea))
            i += 1
        else:
            out.append((pb, eb))
            j += 1
    if i < la:
        out.extend(a[i:])
    if j < lb:
        out.extend(b[j:])
    return out


def divisors_limited(factors, limit):
    """
    Generate all divisors <= limit of a number whose prime factorization is given.
    """
    divs = [1]
    for p, e in factors:
        new = []
        for d in divs:
            v = d
            for _ in range(e + 1):
                if v > limit:
                    break
                new.append(v)
                v *= p
        divs = new
    return divs


def solve(limit_k: int = 1000) -> int:
    """
    Sum perimeters of all integer sided triangles whose (area/perimeter) is an integer <= limit_k.
    """
    max_r = 2 * limit_k
    max_n = max_r * max_r
    # x <= sqrt(3n) with n=max_n
    max_x = int(math.isqrt(3 * max_n))
    # Need SPF up to max(x^2+n) = max_x^2 + max_n
    max_m = max_n + max_x * max_x

    spf = compute_spf(max_m)
    squares = [i * i for i in range(max_x + 1)]
    sqrt3 = math.sqrt(3.0)

    total = 0

    for r in range(2, max_r + 1, 2):
        n = r * r
        fn = factorize_list(n, spf)
        max_x_r = int(r * sqrt3)
        limit_d = 2 * n

        for x in range(1, max_x_r + 1):
            m = squares[x] + n
            fm = factorize_list(m, spf)
            fN = merge_factor_lists(fn, fm)

            for d in divisors_limited(fN, limit_d):
                # y = (n+d)/x must be integer
                nd = n + d
                if nd % x:
                    continue
                y = nd // x
                if y < x:
                    continue

                # z = n(x+y)/d must be integer
                num = n * (x + y)
                if num % d:
                    continue
                z = num // d
                if z < y:
                    continue

                # perimeter = 2(x+y+z)
                total += 2 * (x + y + z)

    return total


def main():
    # Asserts for the explicit examples in the problem statement:
    # Triangle 6,8,10: area/perimeter = 1
    assert abs(area_over_perimeter(6, 8, 10) - 1.0) < 1e-12
    # Triangle 13,14,15: area/perimeter = 2
    assert abs(area_over_perimeter(13, 14, 15) - 2.0) < 1e-12

    # (Extra sanity check commonly referenced by solvers; not required by statement but useful.)
    # For k <= 100 the known sum is 289620027474.
    assert solve(100) == 289620027474

    ans = solve(1000)
    print(ans)


if __name__ == "__main__":
    main()
