import sys
from array import array


MOD = 1234567891


def build_inverses(n, mod):
    inv = array("I", [0]) * (n + 1)
    if n >= 1:
        inv[1] = 1
    for i in range(2, n + 1):
        inv[i] = mod - (mod // i) * inv[mod % i] % mod
    return inv


def solve():
    # Problem asks for F(10^7, 10^7).
    n = 10_000_000
    k = 10_000_000

    e = n // 2
    a_cnt = (n + 3) // 4  # n == 1 (mod 4)
    b_cnt = (n + 1) // 4  # n == 3 (mod 4)
    c = b_cnt - a_cnt

    if e == 0:
        # Only odd strips exist; X wins iff count of 1 mod 4 is odd.
        # This reduces to counting odd sizes up to k from a_cnt values.
        inv = build_inverses(k + 2, MOD)
        inv2 = (MOD + 1) // 2
        h = 1
        q = 1
        sum_odd_a = 0
        ans = 0
        for s in range(0, k + 1):
            if s > 0:
                h = h * (a_cnt + b_cnt + s - 1) % MOD * inv[s] % MOD
                if s % 2 == 0:
                    r = s // 2
                    q = q * (a_cnt + r - 1) % MOD * inv[r] % MOD
            if c == 0:
                coeff = q if s % 2 == 0 else 0
            elif c == 1:
                # With e == 0 we only hit c == -1 or 0, but keep safe.
                coeff = q
            else:
                coeff = q if s % 2 == 0 else (MOD - q)
            h_odd_a = (h - coeff) * inv2 % MOD
            sum_odd_a = (sum_odd_a + h_odd_a) % MOD
            ans = sum_odd_a
        print(ans % MOD)
        return

    max_inv = e + k + 2
    inv = build_inverses(max_inv, MOD)
    inv2 = (MOD + 1) // 2

    # total_even_m at m = k: C(e + k - 1, k)
    total_even = 1
    for m in range(0, k):
        total_even = total_even * (e + m) % MOD * inv[m + 1] % MOD

    # e0 at q = k // 2: C(e + q - 1, q)
    qmax = k // 2
    e0 = 1
    for q in range(0, qmax):
        e0 = e0 * (e + q) % MOD * inv[q + 1] % MOD

    h = 1  # h_s
    q = 1  # C(a_cnt + r - 1, r)
    qsum = 1  # C(a_cnt + r, r) if needed
    sum_even = 0
    sum_odd = 0
    sum_odd_a = 0
    ans = 0
    ab = a_cnt + b_cnt

    for s in range(0, k + 1):
        if s > 0:
            h = h * (ab + s - 1) % MOD * inv[s] % MOD
            if s % 2 == 0:
                r = s // 2
                q = q * (a_cnt + r - 1) % MOD * inv[r] % MOD
                if c == 1:
                    qsum = qsum * (a_cnt + r) % MOD * inv[r] % MOD

        if c == 0:
            coeff = q if s % 2 == 0 else 0
        elif c == 1:
            coeff = qsum
        else:
            coeff = q if s % 2 == 0 else (MOD - q)

        h_odd_a = (h - coeff) * inv2 % MOD

        if s % 2 == 0:
            sum_even = (sum_even + h) % MOD
        else:
            sum_odd = (sum_odd + h) % MOD
        sum_odd_a = (sum_odd_a + h_odd_a) % MOD

        m = k - s
        if m % 2 == 0:
            e0_m = e0
            t0 = e0_m * sum_odd_a % MOD
            t1 = (total_even - e0_m) % MOD * sum_even % MOD
        else:
            t0 = 0
            t1 = total_even * sum_odd % MOD
        ans = (ans + t0 + t1) % MOD

        if m > 0:
            total_even = total_even * m % MOD * inv[e + m - 1] % MOD
        if m % 2 == 0 and m >= 2:
            qcur = m // 2
            e0 = e0 * qcur % MOD * inv[e + qcur - 1] % MOD

    print(ans % MOD)


if __name__ == "__main__":
    solve()
