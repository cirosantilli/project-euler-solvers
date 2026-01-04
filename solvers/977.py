#!/usr/bin/env python3
"""Compute the number of functions f:[n]->[n] with f^{(x)}(y)=f^{(y)}(x)."""

MOD = 1_000_000_007


def count_mod(n: int) -> int:
    if n == 1:
        return 1

    total = 0

    # L = 1 has a closed form.
    m = n - 2
    sum_q = m * (m + 1) * (2 * m + 1) // 6 + m * (m + 1) // 2
    total = (sum_q + n) % MOD

    for L in range(2, n + 1):
        R = n - L

        if R >= 1:
            q_full = (R - 1) // L
            max_a = q_full + 2

            # Precompute a^L for a in [1..max_a] to reuse for B=q+2.
            powA = [0] * (max_a + 1)
            if L == 2:
                for a in range(1, max_a + 1):
                    powA[a] = (a * a) % MOD
            elif L == 3:
                for a in range(1, max_a + 1):
                    aa = a * a % MOD
                    powA[a] = aa * a % MOD
            else:
                for a in range(1, max_a + 1):
                    powA[a] = pow(a, L, MOD)

            for q in range(q_full):
                A = q + 1
                B = q + 2
                A_L = powA[A]
                B_L = powA[B]
                A_L1 = A_L * A % MOD
                term = (q * A_L + (A * A % MOD) * B_L - B * A_L1) % MOD
                total = (total + term) % MOD

            # Last partial block for q = q_full.
            q = q_full
            m = (R - 1) - q_full * L
            A = q + 1
            B = q + 2
            A_L = powA[A]
            term = q * A_L % MOD
            if m >= 1:
                A_L1 = A_L * A % MOD
                exp = L + 1 - m
                if exp == 1:
                    A_L1_m = A % MOD
                elif exp == 2:
                    A_L1_m = (A * A) % MOD
                elif exp == 3:
                    A_L1_m = (A * A % MOD) * A % MOD
                else:
                    A_L1_m = pow(A, exp, MOD)

                if m == 1:
                    B_m = B % MOD
                elif m == 2:
                    B_m = (B * B) % MOD
                elif m == 3:
                    B_m = (B * B % MOD) * B % MOD
                else:
                    B_m = pow(B, m, MOD)

                term = (term + B * ((A_L1_m * B_m - A_L1) % MOD)) % MOD
            total = (total + term) % MOD

        # mu = 0 contribution for rem = R.
        q = R // L
        r = R - q * L
        A = q + 1
        B = q + 2
        if r == 0:
            base = pow(A, L, MOD)
        else:
            base = pow(A, L - r, MOD) * pow(B, r, MOD) % MOD
        total = (total + base) % MOD

    return total % MOD


def count_exact(n: int) -> int:
    if n == 1:
        return 1

    total = 0
    m = n - 2
    sum_q = m * (m + 1) * (2 * m + 1) // 6 + m * (m + 1) // 2
    total = sum_q + n

    for L in range(2, n + 1):
        R = n - L

        if R >= 1:
            q_full = (R - 1) // L
            max_a = q_full + 2

            powA = [0] * (max_a + 1)
            for a in range(1, max_a + 1):
                powA[a] = pow(a, L)

            for q in range(q_full):
                A = q + 1
                B = q + 2
                A_L = powA[A]
                B_L = powA[B]
                term = q * A_L + (A * A) * B_L - B * (A_L * A)
                total += term

            q = q_full
            m = (R - 1) - q_full * L
            A = q + 1
            B = q + 2
            A_L = powA[A]
            term = q * A_L
            if m >= 1:
                A_L1 = A_L * A
                A_L1_m = pow(A, L + 1 - m)
                B_m = pow(B, m)
                term += B * (A_L1_m * B_m - A_L1)
            total += term

        q = R // L
        r = R - q * L
        A = q + 1
        B = q + 2
        base = pow(A, L - r) * pow(B, r)
        total += base

    return total


def main() -> None:
    # Provided examples.
    assert count_exact(3) == 8
    assert count_exact(7) == 174
    assert count_exact(100) == 570271270297640131

    n = 1_000_000
    print(count_mod(n))


if __name__ == "__main__":
    main()
