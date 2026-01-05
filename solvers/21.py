from __future__ import annotations

from typing import List


def proper_divisor_sums_sieve(n_max: int) -> List[int]:
    """
    Returns s where s[n] = sum of proper divisors of n, for 0 <= n <= n_max.
    """
    s = [0] * (n_max + 1)
    # add i to all multiples of i greater than i (so i is a proper divisor)
    for i in range(1, n_max // 2 + 1):
        for j in range(i * 2, n_max + 1, i):
            s[j] += i
    return s


def proper_divisor_sum_factorization(n: int) -> int:
    """
    Sum of proper divisors via prime factorization.
    proper(n) = sigma(n) - n
    """
    if n <= 1:
        return 0
    original = n
    sigma = 1

    # factor 2
    if n % 2 == 0:
        term = 1
        p_pow = 1
        while n % 2 == 0:
            n //= 2
            p_pow *= 2
            term += p_pow
        sigma *= term

    # factor odd primes
    p = 3
    while p * p <= n:
        if n % p == 0:
            term = 1
            p_pow = 1
            while n % p == 0:
                n //= p
                p_pow *= p
                term += p_pow
            sigma *= term
        p += 2

    # remaining prime factor
    if n > 1:
        sigma *= 1 + n

    return sigma - original


def amicable_sum_under(limit: int) -> int:
    divsum = proper_divisor_sums_sieve(limit - 1)

    def d(x: int) -> int:
        if 0 <= x < len(divsum):
            return divsum[x]
        return proper_divisor_sum_factorization(x)

    total = 0
    for a in range(2, limit):
        b = d(a)
        if b != a and d(b) == a:
            total += a
    return total


def main() -> None:
    # Given example checks
    assert proper_divisor_sum_factorization(220) == 284
    assert proper_divisor_sum_factorization(284) == 220

    ans = amicable_sum_under(10000)
    print(ans)


if __name__ == "__main__":
    main()
