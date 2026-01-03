#!/usr/bin/env python3
"""
Project Euler 397: Triangle on Parabola

We count integer quadruplets (k, a, b, c) with:
  1 <= k <= K
  -X <= a < b < c <= X
  A=(a,a^2/k), B=(b,b^2/k), C=(c,c^2/k)
such that at least one angle of triangle ABC is 45 degrees.

No third-party libraries are used.
"""

from __future__ import annotations


def _sieve_spf(n: int) -> list[int]:
    """Smallest prime factor sieve for 1..n."""
    spf = list(range(n + 1))
    if n >= 1:
        spf[0] = 0
        spf[1] = 1
    # standard SPF sieve
    i = 2
    while i * i <= n:
        if spf[i] == i:
            step = i
            j = i * i
            while j <= n:
                if spf[j] == j:
                    spf[j] = i
                j += step
        i += 1
    return spf


def _divisors_of_2k2(k: int, spf: list[int]) -> list[int]:
    """
    Return all positive divisors of D = 2*k^2.

    If k = Π p^e then D has exponents:
      p=2: 2e+1
      p!=2: 2e
      plus (2^1) if k is odd.
    """
    x = k
    factors: list[tuple[int, int]] = []
    has2 = False

    while x > 1:
        p = spf[x]
        e = 0
        while x % p == 0:
            x //= p
            e += 1
        if p == 2:
            factors.append((2, 2 * e + 1))
            has2 = True
        else:
            factors.append((p, 2 * e))

    if not has2:
        factors.append((2, 1))

    divs = [1]
    for p, exp in factors:
        # build powers of p: 1, p, p^2, ..., p^exp
        powers = [1]
        pe = 1
        for _ in range(exp):
            pe *= p
            powers.append(pe)

        new_divs: list[int] = []
        for d in divs:
            # multiply d by each power
            for pw in powers:
                new_divs.append(d * pw)
        divs = new_divs

    return divs


def _count_angle_at_left_vertex(X: int, s: int, t: int) -> int:
    """
    Count choices of a given sums:
      s = a+b, t = a+c with a<b<c
    and -X <= a,b,c <= X, assuming s<t.
    """
    # Bounds from -X <= a <= X and -X <= c=t-a <= X  ->  t-X <= a <= t+X
    # plus b=s-a within bounds, and strict a<b -> 2a < s.
    L = t - X
    if L < -X:
        L = -X

    U = s + X
    if U > X:
        U = X

    # strict 2a < s  -> a <= floor((s-1)/2)
    u2 = (s - 1) // 2
    if u2 < U:
        U = u2

    if U < L:
        return 0
    return U - L + 1


def _count_angle_at_middle_vertex(X: int, p: int, q: int) -> int:
    """
    Count choices of b given sums:
      p = a+b, q = b+c with a<b<c
    and -X <= a,b,c <= X, assuming p<q.
    """
    # From a=p-b bounds: p-X <= b <= p+X
    # From c=q-b bounds: q-X <= b <= q+X
    # and -X <= b <= X.
    L = p - X
    if L < -X:
        L = -X

    qx = q - X
    if qx > L:
        L = qx

    # strict a<b: p-b < b -> 2b > p -> b >= floor(p/2)+1
    l2 = p // 2 + 1
    if l2 > L:
        L = l2

    U = p + X
    if U > X:
        U = X

    # strict b<c: b < q-b -> 2b < q -> b <= floor((q-1)/2)
    u2 = (q - 1) // 2
    if u2 < U:
        U = u2

    if U < L:
        return 0
    return U - L + 1


def F(K: int, X: int) -> int:
    """
    Compute F(K, X) as defined in the problem.
    """
    spf = _sieve_spf(K)
    twoX = 2 * X

    count_A = 0  # angle 45 at leftmost vertex (A)
    count_B = 0  # angle 45 at middle vertex (B)
    overlap_AB = 0  # triangles with angles A and B both 45 (then C is 90)
    overlap_AC = 0  # triangles with angles A and C both 45 (then B is 90)

    for k in range(1, K + 1):
        D = 2 * k * k  # 2*k^2
        divisors = _divisors_of_2k2(k, spf)

        for d in divisors:
            u = D // d  # paired divisor

            # --- Angle at A (leftmost point) ---
            # Let s=a+b and t=a+c.
            # From the 45-degree condition: k(t-s) = k^2 + s*t
            # Solving gives: t = d - k and s = k - D/d = k - u for some d|D, d>0.
            s = k - u
            t = d - k

            if -twoX <= s <= twoX and -twoX <= t <= twoX:
                count_A += _count_angle_at_left_vertex(X, s, t)

                # --- Overlaps (two 45-degree angles) ---
                # If angle at A is 45 and angle at B is 45, then:
                #   q = b+c satisfies q = k(s-k)/(s+k) where s=a+b.
                denom = s + k
                if denom:
                    num = k * (s - k)
                    if num % denom == 0:
                        q = num // denom
                        if -twoX <= q <= twoX and ((s + t - q) & 1) == 0:
                            a = (s + t - q) // 2
                            b = (s + q - t) // 2
                            c = (t + q - s) // 2
                            if -X <= a < b < c <= X:
                                overlap_AB += 1

                # If angle at A is 45 and angle at C is 45, then:
                #   q = b+c satisfies q = k(k+t)/(k-t) where t=a+c.
                denom2 = k - t
                if denom2:
                    num2 = k * (k + t)
                    if num2 % denom2 == 0:
                        q2 = num2 // denom2
                        if -twoX <= q2 <= twoX and ((s + t - q2) & 1) == 0:
                            a = (s + t - q2) // 2
                            b = (s + q2 - t) // 2
                            c = (t + q2 - s) // 2
                            if -X <= a < b < c <= X:
                                overlap_AC += 1

            # --- Angle at B (middle point) ---
            # Let p=a+b and q=b+c.
            # From the 45-degree condition at the middle vertex (rays point opposite ways):
            #   k(q-p) = -k^2 - p*q
            # Solving gives: q = k + d and p = -(k + D/d) = -(k + u) for some d|D, d>0.
            p = -(k + u)
            q = k + d

            if -twoX <= p <= twoX and q <= twoX:
                count_B += _count_angle_at_middle_vertex(X, p, q)

    # By symmetry count(angle at C) = count(angle at A), and overlap(B,C)=overlap(A,B)
    total = 2 * count_A + count_B - 2 * overlap_AB - overlap_AC
    return total


def main() -> None:
    # Test values from the problem statement:
    assert F(1, 10) == 41
    assert F(10, 100) == 12492

    # Problem query:
    print(F(1_000_000, 1_000_000_000))


if __name__ == "__main__":
    main()
