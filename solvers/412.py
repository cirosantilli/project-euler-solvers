from typing import List

MOD = 76543217


def factorial_mod(n: int, mod: int) -> int:
    res = 1
    i = 2
    while i <= n:
        res = (res * i) % mod
        i += 1
    return res


def lc_mod(m: int, n: int, mod: int) -> int:
    k = m - n
    max_small = 2 * m - 1

    fac = [1] * (max_small + 1)
    for i in range(1, max_small + 1):
        fac[i] = fac[i - 1] * i % mod

    invfac = [1] * (max_small + 1)
    invfac[max_small] = pow(fac[max_small], mod - 2, mod)
    for i in range(max_small, 0, -1):
        invfac[i - 1] = invfac[i] * i % mod

    v_a = 1
    for i in range(1, n):
        v_a = v_a * fac[i] % mod

    v_b = 1
    for i in range(1, k):
        v_b = v_b * fac[i] % mod

    v_ab = 1
    for t in range(k):
        v_ab = v_ab * fac[2 * n + t] % mod
        v_ab = v_ab * invfac[n + t] % mod

    d_inv = 1
    for a in range(k, m):
        d_inv = d_inv * invfac[a] % mod
    for b in range(m + n, 2 * m):
        d_inv = d_inv * invfac[b] % mod

    total_fact = factorial_mod(m * m - n * n, mod)

    res = total_fact
    res = res * v_a % mod
    res = res * v_b % mod
    res = res * v_ab % mod
    res = res * d_inv % mod
    return res


def main() -> None:
    assert lc_mod(3, 0, MOD) == 42
    assert lc_mod(5, 3, MOD) == 250250
    assert lc_mod(6, 3, MOD) == 406029023400 % MOD
    assert lc_mod(10, 5, MOD) == 61251715

    result = lc_mod(10000, 5000, MOD)
    print(result)


if __name__ == "__main__":
    main()
