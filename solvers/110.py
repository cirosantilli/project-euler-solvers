from __future__ import annotations

import math
from typing import List


def num_distinct_solutions(n: int) -> int:
    """
    Counts distinct positive integer solutions (x,y) up to symmetry for:
        1/x + 1/y = 1/n
    Using: (x-n)(y-n) = n^2  =>  #solutions = (d(n^2)+1)/2
    """
    nn = n
    d_n_sq = 1
    p = 2
    while p * p <= nn:
        if nn % p == 0:
            e = 0
            while nn % p == 0:
                nn //= p
                e += 1
            d_n_sq *= 2 * e + 1
        p += 1 if p == 2 else 2
    if nn > 1:
        d_n_sq *= 3  # exponent 1 in n -> exponent 2 in n^2 -> (2*1+1)=3
    return (d_n_sq + 1) // 2


def least_n_with_over_solutions(target_solutions: int) -> int:
    # Need (d(n^2)+1)/2 > target_solutions  <=> d(n^2) >= 2*target_solutions
    target_divisors = 2 * target_solutions

    # First 15 primes (enough because 3^15 > 8,000,000)
    primes: List[int] = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]

    # Initial upper bound: square-free product of first k primes where 3^k >= target_divisors
    k = 0
    while pow(3, k) < target_divisors:
        k += 1
    assert k <= len(primes)
    best_n = 1
    for i in range(k):
        best_n *= primes[i]

    def dfs(i: int, max_exp: int, cur_n: int, cur_divs: int) -> None:
        nonlocal best_n

        if cur_divs >= target_divisors:
            if cur_n < best_n:
                best_n = cur_n
            return

        if i >= len(primes):
            return

        if cur_n >= best_n:
            return

        # If even using exponent=max_exp for ALL remaining primes cannot reach target, prune.
        remaining = len(primes) - i
        if cur_divs * pow(2 * max_exp + 1, remaining) < target_divisors:
            return

        p = primes[i]
        p_pow = 1
        for exp in range(1, max_exp + 1):
            p_pow *= p
            new_n = cur_n * p_pow
            if new_n >= best_n:
                break
            new_divs = cur_divs * (2 * exp + 1)
            dfs(i + 1, exp, new_n, new_divs)

    # max exponent for 2 given current best_n
    max_e2 = int(math.log2(best_n)) + 1
    dfs(0, max_e2, 1, 1)
    return best_n


def main() -> None:
    # Test case from the statement
    assert num_distinct_solutions(1260) == 113

    ans = least_n_with_over_solutions(4_000_000)
    # Sanity check: must exceed 4,000,000 solutions
    assert num_distinct_solutions(ans) > 4_000_000

    print(ans)


if __name__ == "__main__":
    main()
