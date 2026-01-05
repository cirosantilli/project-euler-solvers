import math


def _grouped_sum_linear_times_floor(n: int) -> int:
    """
    Returns sum_{k=1..n} k * floor(n/k) in O(sqrt(n)) time by grouping equal quotients.
    """
    if n <= 0:
        return 0
    total = 0
    k = 1
    while k <= n:
        q = n // k
        k2 = n // q  # largest index with same quotient q
        # sum_{t=k..k2} t = (k + k2) * (k2 - k + 1) // 2
        total += q * (k + k2) * (k2 - k + 1) // 2
        k = k2 + 1
    return total


def solve(N: int = 10**8) -> int:
    gcd = math.gcd
    isqrt = math.isqrt

    # Part 1: real (integer) divisors contribution: sum_{d<=N} d * floor(N/d)
    ans = _grouped_sum_linear_times_floor(N)

    # Memo for F(q) = sum_{k<=q} k * floor(q/k)
    F_cache = {}

    def F(q: int) -> int:
        if q in F_cache:
            return F_cache[q]
        val = _grouped_sum_linear_times_floor(q)
        F_cache[q] = val
        return val

    # Special primitive pair (1,1): only {1+i, 1-i} => real parts sum to 2
    ans += 2 * F(N // 2)

    # Primitive pairs (a,b), 1 <= a < b, gcd(a,b)=1, a^2 + b^2 <= N
    # Note: if a<b then necessarily a <= sqrt(N/2) (since b >= a+1).
    max_a = isqrt(N // 2)
    for a in range(1, max_a + 1):
        a2 = a * a
        b = a + 1
        bmax = isqrt(N - a2)
        if b > bmax:
            continue

        b2 = b * b
        while b <= bmax:
            if gcd(a, b) == 1:
                v = a2 + b2
                ans += 2 * (a + b) * F(N // v)

            # increment b and update b^2 cheaply:
            b += 1
            b2 += 2 * b - 1  # new b^2 = old b^2 + 2*b - 1

    return ans


if __name__ == "__main__":
    # sanity checks from the problem statement:
    assert solve(5) == 35
    assert solve(10**5) == 17924657155
    print(solve(10**8))
