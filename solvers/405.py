from __future__ import annotations

from typing import Tuple

MOD = 17**7
PHI = MOD - MOD // 17  # Euler's totient for 17^7
INV15 = pow(15, -1, MOD)


def f_from_parts(n_mod_phi: int, parity: int) -> int:
    """Compute f(n) mod MOD given n mod PHI and n mod 2."""
    # Closed form from the recurrence:
    # f(n) = (6*4^n - 20*2^n + 15 - (-1)^n) / 15
    p2 = pow(2, n_mod_phi, MOD)
    p4 = pow(4, n_mod_phi, MOD)
    sign = 1 if parity == 0 else -1
    num = (6 * p4 - 20 * p2 + 15 - sign) % MOD
    return (num * INV15) % MOD


def f_mod(n: int) -> int:
    return f_from_parts(n % PHI, n & 1)


def f_mod_power10(k: int) -> int:
    n_mod_phi = pow(10, k, PHI)
    parity = pow(10, k, 2)
    return f_from_parts(n_mod_phi, parity)


def main() -> None:
    # Given examples
    assert f_mod(1) == 0
    assert f_mod(4) == 82
    assert f_mod(10**9) == 126897180

    k = 10**18
    result = f_mod_power10(k)
    print(result)


if __name__ == "__main__":
    main()
