from __future__ import annotations

from array import array
from typing import List


def totients_up_to(n: int) -> array:
    """
    Compute phi(k) for all 0 <= k <= n using a linear sieve.
    Returns an array('I') where phi[k] is Euler's totient function.
    """
    phi = array("I", [0]) * (n + 1)
    if n >= 1:
        phi[1] = 1

    is_comp = bytearray(n + 1)
    primes: List[int] = []

    for i in range(2, n + 1):
        if not is_comp[i]:
            primes.append(i)
            phi[i] = i - 1
        for p in primes:
            ip = i * p
            if ip > n:
                break
            is_comp[ip] = 1
            if i % p == 0:
                phi[ip] = phi[i] * p
                break
            else:
                phi[ip] = phi[i] * (p - 1)

    return phi


def count_reduced_proper_fractions(max_d: int) -> int:
    """
    Count reduced proper fractions n/d with 1 <= n < d <= max_d and gcd(n,d)=1.
    This equals sum_{d=2..max_d} phi(d).
    """
    if max_d < 2:
        return 0
    phi = totients_up_to(max_d)
    return int(sum(phi[2:]))


def _tests() -> None:
    # From the statement: for d <= 8 there are 21 reduced proper fractions.
    assert count_reduced_proper_fractions(8) == 21
    assert count_reduced_proper_fractions(1) == 0
    assert count_reduced_proper_fractions(2) == 1  # only 1/2


def main() -> None:
    _tests()
    n = 1_000_000
    ans = count_reduced_proper_fractions(n)
    print(ans)


if __name__ == "__main__":
    main()
