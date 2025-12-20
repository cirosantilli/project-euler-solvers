from typing import Final


MOD: Final[int] = 10**9


def sum_sq_mod(n: int, mod: int) -> int:
    """Return sum_{i=1..n} i^2 modulo mod using exact division by 6."""
    if n <= 0:
        return 0
    a = n
    b = n + 1
    c = 2 * n + 1

    if a % 2 == 0:
        a //= 2
    else:
        b //= 2

    if a % 3 == 0:
        a //= 3
    elif b % 3 == 0:
        b //= 3
    else:
        c //= 3

    return (a % mod) * (b % mod) % mod * (c % mod) % mod


def sigma2_summatory(n: int, mod: int = MOD) -> int:
    """Compute SIGMA_2(n) = sum_{k=1..n} sigma_2(k) modulo mod."""
    total = 0
    l = 1
    prev_s2_mod = 0
    while l <= n:
        q = n // l
        r = n // q
        s2_r_mod = sum_sq_mod(r, mod)
        range_sum_mod = s2_r_mod - prev_s2_mod
        if range_sum_mod < 0:
            range_sum_mod += mod
        total = (total + range_sum_mod * (q % mod)) % mod
        prev_s2_mod = s2_r_mod
        l = r + 1
    return total


def main() -> None:
    # Given values of SIGMA_2 for n=1..6.
    expected = [1, 6, 16, 37, 63, 113]
    for i, value in enumerate(expected, 1):
        assert sigma2_summatory(i, MOD) == value

    result = sigma2_summatory(10**15, MOD)
    print(result)


if __name__ == "__main__":
    main()
