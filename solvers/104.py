from __future__ import annotations

from decimal import Decimal, getcontext
from typing import Tuple
import sys


TARGET_MASK = (1 << 10) - 2  # bits 1..9 set (1022)
MOD_LAST9 = 1_000_000_000


def is_1_to_9_pandigital_str9(s: str) -> bool:
    if len(s) != 9:
        return False
    mask = 0
    for ch in s:
        d = ord(ch) - 48
        if d == 0:
            return False
        bit = 1 << d
        if mask & bit:
            return False
        mask |= bit
    return mask == TARGET_MASK


def is_1_to_9_pandigital_last9(x_mod_1e9: int) -> bool:
    return is_1_to_9_pandigital_str9(f"{x_mod_1e9:09d}")


def is_1_to_9_pandigital_first9(x_first9: int) -> bool:
    s = str(x_first9)
    return len(s) == 9 and is_1_to_9_pandigital_str9(s)


def fib_fast_doubling(n: int) -> int:
    """Return F_n exactly (F_0=0, F_1=1)."""

    def rec(k: int) -> Tuple[int, int]:
        if k == 0:
            return 0, 1
        a, b = rec(k >> 1)  # (F_m, F_{m+1})
        c = a * (2 * b - a)  # F_{2m}
        d = a * a + b * b  # F_{2m+1}
        if k & 1:
            return d, c + d
        return c, d

    return rec(n)[0]


class LeadingDigits:
    """
    Compute leading 9 digits of F_n using logs:
      log10(F_n) ~= n*log10(phi) - log10(sqrt(5))
    We use Decimal exp/ln at high precision for reliability.
    """

    def __init__(self, prec: int = 110) -> None:
        getcontext().prec = prec
        self.ln10 = Decimal(10).ln()
        sqrt5 = Decimal(5).sqrt()
        phi = (Decimal(1) + sqrt5) / Decimal(2)
        self.log10_phi = phi.ln() / self.ln10
        self.log10_sqrt5 = sqrt5.ln() / self.ln10

    def first9(self, n: int) -> int:
        x = Decimal(n) * self.log10_phi - self.log10_sqrt5
        frac = x - int(x)  # 0 <= frac < 1
        y = frac + Decimal(8)  # we want floor(10^(frac+8))
        val = (y * self.ln10).exp()
        return int(val)


def find_k() -> int:
    leader = LeadingDigits()

    # Validate statement facts with exact Fibonacci values.
    f541 = fib_fast_doubling(541)
    assert is_1_to_9_pandigital_last9(f541 % MOD_LAST9)
    f2749 = fib_fast_doubling(2749)
    assert is_1_to_9_pandigital_str9(str(f2749)[:9])
    assert leader.first9(2749) == int(str(f2749)[:9])

    # Iterate Fibonacci numbers modulo 1e9 for last 9 digits.
    f_prev = 1  # F_1
    f_cur = 1  # F_2
    n = 2

    while True:
        n += 1
        f_prev, f_cur = f_cur, (f_prev + f_cur) % MOD_LAST9

        if not is_1_to_9_pandigital_last9(f_cur):
            continue

        first9 = leader.first9(n)
        if not is_1_to_9_pandigital_first9(first9):
            continue

        # Final verification with exact Fibonacci (very rare).
        fn = fib_fast_doubling(n)
        s = str(fn)
        if is_1_to_9_pandigital_str9(s[:9]) and is_1_to_9_pandigital_str9(s[-9:]):
            return n


if __name__ == "__main__":
    sys.set_int_max_str_digits(2**32 - 1)
    print(find_k())
