from __future__ import annotations

from array import array
from typing import Final

MOD: Final[int] = 1_000_000_007


def count_winning(n: int) -> int:
    mod = MOD
    q = pow(2, n, mod)
    q_minus_1 = q - 1
    if q_minus_1 < 0:
        q_minus_1 += mod

    # Total ordered n-tuples of distinct nonzero elements: (q-1)_n
    total = 1
    fact = 1
    term = q_minus_1
    for i in range(1, n + 1):
        total = (total * term) % mod
        term -= 1
        if term < 0:
            term += mod
        fact = (fact * i) % mod

    inv_fact = pow(fact, mod - 2, mod)
    comb_q_minus_1_n = total * inv_fact % mod

    # E_n = (-1)^n * sum_{r=0}^{floor(n/2)} (-1)^r * C(q/2, r)
    m = n // 2
    if m == 0:
        s = 1
    else:
        inv = array("I", [0]) * (m + 1)
        inv[1] = 1
        for i in range(2, m + 1):
            inv[i] = mod - (mod // i) * inv[mod % i] % mod

        n_half = pow(2, n - 1, mod)
        binom = 1
        s = 1
        for r in range(1, m + 1):
            term = (n_half - r + 1) % mod
            binom = (binom * term) % mod
            binom = (binom * inv[r]) % mod
            if r & 1:
                s -= binom
            else:
                s += binom
            s %= mod

    e_n = (-s) % mod if (n & 1) else s

    inv_q = pow(q, mod - 2, mod)
    losing = fact * inv_q % mod
    losing = losing * (comb_q_minus_1_n + q_minus_1 * e_n % mod) % mod

    return (total - losing) % mod


def main() -> None:
    assert count_winning(1) == 1
    assert count_winning(2) == 6
    assert count_winning(3) == 168
    assert count_winning(5) == 19_764_360
    assert count_winning(100) == 384_777_056

    result = count_winning(10_000_000)
    print(result)


if __name__ == "__main__":
    main()
