from typing import List


def distinct_prime_factor_counts(limit: int) -> List[int]:
    """
    Returns an array cnt where cnt[n] = number of distinct prime factors of n, for 0 <= n <= limit.
    Uses a sieve-like process: for each prime p, increment all multiples of p.
    """
    cnt = [0] * (limit + 1)
    for p in range(2, limit + 1):
        if cnt[p] == 0:  # p is prime
            for m in range(p, limit + 1, p):
                cnt[m] += 1
    return cnt


def first_consecutive_with_k_factors(k: int, run_len: int, start_limit: int) -> int:
    """
    Finds the first integer n such that n..n+run_len-1 each have exactly k distinct prime factors.
    """
    limit = start_limit
    while True:
        cnt = distinct_prime_factor_counts(limit)
        streak = 0
        for n in range(2, limit + 1):
            if cnt[n] == k:
                streak += 1
                if streak == run_len:
                    return n - run_len + 1
            else:
                streak = 0
        limit *= 2  # expand search if not found


def main() -> None:
    # Problem statement examples / sanity checks
    assert first_consecutive_with_k_factors(2, 2, 100) == 14
    assert first_consecutive_with_k_factors(3, 3, 2000) == 644

    # Target problem
    ans = first_consecutive_with_k_factors(4, 4, 200_000)

    print(ans)


if __name__ == "__main__":
    main()
