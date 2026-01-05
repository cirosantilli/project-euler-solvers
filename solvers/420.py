#!/usr/bin/env python3
# Computes F(N) for the Project Euler-style problem:
# count 2x2 positive-integer matrices A with tr(A)<N that have TWO different
# positive-integer square roots.

import math
from array import array


def divisor_counts_upto_linear(M: int) -> array:
    """
    Return d[n] = number of positive divisors of n, for 0..M, using a linear sieve.
    d is an array('I') of length M+1.
    """
    spf = array("I", [0]) * (M + 1)  # smallest prime factor
    d = array("I", [0]) * (M + 1)  # divisor counts
    exp = array("B", [0]) * (M + 1)  # exponent of spf in n
    primes = []

    d[1] = 1
    for i in range(2, M + 1):
        if spf[i] == 0:
            spf[i] = i
            primes.append(i)
            exp[i] = 1
            d[i] = 2

        si = spf[i]
        di = d[i]
        ei = exp[i]

        for p in primes:
            ip = i * p
            if ip > M:
                break
            spf[ip] = p
            if p == si:
                # ip = i * p where p already divides i
                exp[ip] = ei + 1
                d[ip] = di // (ei + 1) * (exp[ip] + 1)
                break
            else:
                exp[ip] = 1
                d[ip] = di * 2

    return d


def F(N: int) -> int:
    """
    Implements:
      F(N) = sum_{u>v>=1, u^2+v^2<N}  sum_{a in valid range} d(a*(K-a))
    where K = gcd(u+v, u-v) and valid a satisfy v < a*(u+v)/K < u, 1<=a<=K-1.
    """
    isqrt = math.isqrt
    gcd = math.gcd

    Umax = isqrt(N - 2)
    Kmax = 2 * Umax
    M = (Kmax * Kmax) // 4  # max of a*(K-a) over K<=Kmax

    # divisor counts up to M
    d = divisor_counts_upto_linear(M)

    # prefix[K][a] = sum_{t=1..a} d(t*(K-t)), with prefix[K][0]=0
    prefix = [None] * (Kmax + 1)
    for K in range(2, Kmax + 1):
        pref = array("I", [0]) * K
        s = 0
        for a in range(1, K):
            s += d[a * (K - a)]
            pref[a] = s
        prefix[K] = pref

    total = 0

    for u in range(2, Umax + 1):
        vmax = isqrt(N - 1 - u * u)
        if vmax >= u:
            vmax = u - 1
        for v in range(1, vmax + 1):
            g = gcd(u, v)
            uu = u // g
            vv = v // g

            # K = gcd(u+v, u-v) = g * (1 or 2); it is 2g iff uu and vv are both odd
            delta = 2 if ((uu & 1) and (vv & 1)) else 1
            K = g * delta
            if K <= 1:
                continue

            s = u + v

            # a > vK/(u+v)  and  a < uK/(u+v)
            low = (v * K) // s + 1
            high = (u * K - 1) // s

            if low < 1:
                low = 1
            if high > K - 1:
                high = K - 1

            if low <= high:
                pref = prefix[K]
                total += pref[high] - pref[low - 1]

    return total


if __name__ == "__main__":
    assert F(50) == 7
    assert F(1000) == 1019
    print(F(10_000_000))
