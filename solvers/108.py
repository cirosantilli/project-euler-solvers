from __future__ import annotations

from typing import List, Tuple


def factorize(n: int) -> List[Tuple[int, int]]:
    """Return prime factorization of n as (prime, exponent)."""
    res: List[Tuple[int, int]] = []
    d = 2
    while d * d <= n:
        if n % d == 0:
            e = 0
            while n % d == 0:
                n //= d
                e += 1
            res.append((d, e))
        d = 3 if d == 2 else d + 2
    if n > 1:
        res.append((n, 1))
    return res


def num_distinct_solutions(n: int) -> int:
    """
    Count distinct (x, y) with x <= y, x,y positive integers, satisfying:
        1/x + 1/y = 1/n
    Using: (x-n)(y-n) = n^2, so #solutions = (d(n^2)+1)//2.
    """
    div_count_n2 = 1
    for _, a in factorize(n):
        div_count_n2 *= 2 * a + 1
    return (div_count_n2 + 1) // 2


def search_min_n(target_divisors_n2: int) -> int:
    """
    Find smallest n such that d(n^2) >= target_divisors_n2, where
    d(n^2) = Π (2*a_i + 1) for n = Π p_i^a_i.
    We use DFS over exponent vectors with non-increasing exponents.
    """
    primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]

    # Simple constructive upper bound: all exponents 1 => multiplier 3 per prime.
    best = 1
    div_prod = 1
    for p in primes:
        best *= p
        div_prod *= 3
        if div_prod >= target_divisors_n2:
            break

    best_ref = best

    def dfs(i: int, prev_exp: int, curr_n: int, curr_div_prod: int) -> None:
        nonlocal best_ref
        if curr_div_prod >= target_divisors_n2:
            if curr_n < best_ref:
                best_ref = curr_n
            return
        if i >= len(primes):
            return

        p = primes[i]
        n_val = curr_n
        for e in range(1, prev_exp + 1):
            n_val *= p
            if n_val >= best_ref:
                break
            dfs(i + 1, e, n_val, curr_div_prod * (2 * e + 1))

    dfs(0, best.bit_length(), 1, 1)
    return best_ref


def main() -> None:
    # Test case from the statement:
    assert num_distinct_solutions(4) == 3

    # Need (d(n^2)+1)//2 > 1000  <=>  d(n^2) > 1999.
    # Since d(n^2) is always odd, requiring d(n^2) >= 2000 is equivalent.
    ans = search_min_n(target_divisors_n2=2000)

    assert num_distinct_solutions(ans) > 1000
    print(ans)


if __name__ == "__main__":
    main()
