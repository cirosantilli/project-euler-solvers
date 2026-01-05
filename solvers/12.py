from __future__ import annotations

from math import isqrt
from typing import List


class PrimeTable:
    def __init__(self) -> None:
        self.primes: List[int] = [2]

    def _is_prime(self, x: int) -> bool:
        r = isqrt(x)
        for p in self.primes:
            if p > r:
                break
            if x % p == 0:
                return False
        return True

    def ensure_up_to(self, n: int) -> None:
        """Ensure we have all primes up to at least n (inclusive)."""
        if self.primes[-1] >= n:
            return
        candidate = self.primes[-1] + 1
        if candidate % 2 == 0:
            candidate += 1
        while self.primes[-1] < n:
            if self._is_prime(candidate):
                self.primes.append(candidate)
            candidate += 2

    def divisor_count(self, m: int) -> int:
        """Return number of positive divisors of m."""
        if m <= 1:
            return 1
        self.ensure_up_to(isqrt(m) + 1)
        x = m
        total = 1
        for p in self.primes:
            if p * p > x:
                break
            if x % p == 0:
                exp = 0
                while x % p == 0:
                    x //= p
                    exp += 1
                total *= exp + 1
        if x > 1:
            total *= 2
        return total


def first_triangular_with_over(k: int) -> int:
    """
    Find the first triangular number T_n = n(n+1)/2 having > k divisors.
    Uses gcd(n, n+1)=1 so divisor_count(T_n)=div(a)*div(b) where (a,b) are
    the split parts after dividing one of them by 2.
    """
    pt = PrimeTable()
    n = 1
    while True:
        if n % 2 == 0:
            a = n // 2
            b = n + 1
        else:
            a = n
            b = (n + 1) // 2
        d = pt.divisor_count(a) * pt.divisor_count(b)
        if d > k:
            return n * (n + 1) // 2
        n += 1


def main() -> None:
    # From the statement: first triangular number with over 5 divisors is 28.
    assert first_triangular_with_over(5) == 28

    ans = first_triangular_with_over(500)
    print(ans)


if __name__ == "__main__":
    main()
