from typing import List


def sum_proper_divisors_sieve(limit: int) -> List[int]:
    """
    sums[n] = sum of proper divisors of n, for 0 <= n <= limit
    """
    sums = [0] * (limit + 1)
    # add d to all multiples of d greater than d itself
    for d in range(1, limit // 2 + 1):
        for m in range(d * 2, limit + 1, d):
            sums[m] += d
    return sums


def non_abundant_sums(limit: int = 28123) -> int:
    sums = sum_proper_divisors_sieve(limit)

    # Checks derived from the statement
    assert sums[28] == 28  # 28 is perfect
    abundant = [n for n in range(12, limit + 1) if sums[n] > n]
    assert abundant and abundant[0] == 12  # 12 is the smallest abundant number

    # can[x] == 1 iff x can be written as sum of two abundant numbers
    can = bytearray(limit + 1)
    abund = abundant
    lim = limit
    L = len(abund)

    for i in range(L):
        a = abund[i]
        for j in range(i, L):
            s = a + abund[j]
            if s > lim:
                break
            can[s] = 1

    assert can[24] == 1  # 24 is the smallest sum of two abundant numbers

    total = 0
    for n in range(1, lim + 1):
        if not can[n]:
            total += n
    return total


def main() -> None:
    result = non_abundant_sums()
    print(result)


if __name__ == "__main__":
    main()
