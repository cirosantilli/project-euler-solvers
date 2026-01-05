#!/usr/bin/env python3
"""Project Euler 366: Stone Game III

Rules (Fibonacci Nim):
- One pile of n stones.
- First move: take 1..n-1 stones.
- Thereafter: may take at most twice the opponent's previous take.
- Taking the last stone wins.

Let M(n) be the maximum first move from a winning starting position, else 0.
Compute sum_{n<=10^18} M(n) mod 1e8.

No external libraries are used.
"""

MOD = 10**8
TARGET_N = 10**18


def build_fibs_upto(n: int) -> list[int]:
    """Return Fibonacci numbers for Zeckendorf/Fibonacci Nim: F1=1,F2=2,... up to >n."""
    fib = [0, 1, 2]  # index 0 unused; fib[1]=1, fib[2]=2
    while fib[-1] <= n:
        fib.append(fib[-1] + fib[-2])
    return fib


def m_single(n: int, fib: list[int]) -> int:
    """Compute M(n) for a single n using the known Fibonacci Nim greedy strategy."""
    if n <= 1:
        return 0

    i = len(fib) - 1
    while fib[i] > n:
        i -= 1
    if fib[i] == n:
        return 0

    rem = n - fib[i]
    idx = i
    while idx >= 3 and 2 * rem >= fib[idx]:
        rem -= fib[idx - 2]
        idx -= 2
    return rem


def sum_m_upto(n: int, mod: int = MOD) -> int:
    """Compute S(n) = sum_{k<=n} M(k) (mod mod) without iterating all k."""
    if n <= 1:
        return 0

    fib = build_fibs_upto(n + 1)
    total = 0

    for i in range(1, len(fib) - 1):
        Fi = fib[i]
        if Fi > n:
            break

        # We only sum k in (Fi, min(F_{i+1}-1, n)] because M(Fi)=0.
        max_k = min(fib[i + 1] - 1, n)
        max_m0 = max_k - Fi
        if max_m0 <= 0:
            continue

        # Also k < F_{i+1} = F_i + F_{i-1} => m0 <= F_{i-1}-1 (for i>=2).
        if i - 1 < 1:
            continue
        max_m0 = min(max_m0, fib[i - 1] - 1)
        if max_m0 <= 0:
            continue

        # j = number of subtractions performed; idx = i-2j.
        # S = sum of subtracted Fibonacci numbers = F_{i-2} + F_{i-4} + ... + F_{idx}.
        # LB = smallest m0 that reaches this stage (i.e., did not stop earlier).
        S = 0
        LB = 1
        j = 0

        while True:
            idx = i - 2 * j
            if idx < 1:
                break

            # Stop condition at this stage: remainder r = m0 - S satisfies 2*r < fib[idx]
            # => r <= floor((fib[idx]-1)/2) => m0 <= S + floor((fib[idx]-1)/2).
            U = min(max_m0, S + (fib[idx] - 1) // 2)

            if LB <= U:
                cnt = U - LB + 1
                # Sum_{m=LB..U} (m - S) = Sum(m) - cnt*S
                sum_m = (LB + U) * cnt // 2
                total = (total + sum_m - cnt * S) % mod

            # Prepare next stage (j+1): require we did NOT stop here:
            # 2*(m0 - S) >= fib[idx]  => m0 >= S + ceil(fib[idx]/2).
            if idx - 2 < 1:
                break
            LB = max(LB, S + (fib[idx] + 1) // 2)

            # Next stage subtracts fib[idx-2]
            S += fib[idx - 2]
            j += 1

            if LB > max_m0:
                break

    return total % mod


def main() -> None:
    # Problem statement checks
    fib_small = build_fibs_upto(10**6)
    assert m_single(5, fib_small) == 0  # 5 is losing
    assert m_single(17, fib_small) == 4  # 17: can take 1 or 4, so M(17)=4
    assert sum_m_upto(100) == 728  # given in statement

    print(sum_m_upto(TARGET_N))


if __name__ == "__main__":
    main()
