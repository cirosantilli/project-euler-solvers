import math


LIMIT = 10**10


def build_spf(n: int):
    """Smallest prime factor sieve up to n."""
    spf = list(range(n + 1))
    for i in range(2, int(math.isqrt(n)) + 1):
        if spf[i] == i:  # prime
            step = i
            start = i * i
            for j in range(start, n + 1, step):
                if spf[j] == j:
                    spf[j] = i
    return spf


def squarefree_and_sqrt(n: int, spf):
    """
    Decompose n as: n = sf * sq^2, where sf is squarefree, sq >= 1.
    Returns (sf, sq).
    """
    sf = 1
    sq = 1
    while n > 1:
        p = spf[n]
        e = 0
        while n % p == 0:
            n //= p
            e += 1
        if e & 1:
            sf *= p
        sq *= p ** (e // 2)
    return sf, sq


def pell_fundamental(D: int, cache: dict):
    """
    Fundamental solution (x, y) to x^2 - D*y^2 = 1 for nonsquare D,
    using continued fractions of sqrt(D).
    """
    if D in cache:
        return cache[D]

    a0 = int(math.isqrt(D))
    if a0 * a0 == D:
        raise ValueError("D must be nonsquare")

    m = 0
    d = 1
    a = a0

    # convergents:
    num1, num = 1, a
    den1, den = 0, 1

    while num * num - D * den * den != 1:
        m = d * a - m
        d = (D - m * m) // d
        a = (a0 + m) // d

        num2, num1 = num1, num
        den2, den1 = den1, den

        num = a * num1 + num2
        den = a * den1 + den2

    cache[D] = (num, den)
    return num, den


def solve(limit: int = LIMIT) -> int:
    # From n >= k constraint we can show k >= 2m(m+1), hence m is bounded:
    mmax = (math.isqrt(1 + 2 * limit) - 1) // 2

    spf = build_spf(mmax + 2)

    pell_cache = {}
    pivots = set()

    for m in range(1, mmax + 1):
        # m = s * p^2, where s squarefree
        s, p = squarefree_and_sqrt(m, spf)

        # m+1 = g * r^2, where g squarefree
        g, r = squarefree_and_sqrt(m + 1, spf)

        # Reduced Pell discriminant (squarefree):
        D = s * g

        # Fundamental unit (x1 + y1*sqrt(D)) for x^2 - D y^2 = 1
        x1, y1 = pell_fundamental(D, pell_cache)

        # We solve x^2 - D y^2 = g starting from the small solution:
        # x0 = g*r, y0 = p  (always satisfies the equation)
        x, y = g * r, p

        # Iterate through solutions via multiplication by the fundamental unit
        while True:
            q = y  # corresponds to 'q' in a = s*q^2

            # Candidate pivot formula derived from algebra:
            numerator = s * p * (p + q)
            k_floor = numerator // 2
            if k_floor > limit and q > p:
                break

            if numerator % 2 == 0:
                k = numerator // 2

                if k <= limit and k >= 2 * m * (m + 1):
                    # Recover u from x = g*u  (x always divisible by g as g is squarefree and divides D)
                    u = x // g

                    # t = sqrt((m+1)(a+1)) = g*r*u
                    t = g * r * u

                    if (t - m - 1) % 2 == 0:
                        n = (t - m - 1) // 2
                        if n >= k:
                            pivots.add(k)

            # Next solution:
            x, y = x * x1 + y * y1 * D, x * y1 + y * x1

    # Asserts from problem statement examples
    for test_k in (4, 21, 24, 110):
        assert test_k in pivots, f"Expected test pivot {test_k} not found!"

    return sum(pivots)


def main():
    print(solve())


if __name__ == "__main__":
    main()
