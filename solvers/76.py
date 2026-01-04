from typing import List


def count_summations(n: int) -> int:
    """
    Number of ways to write n as a sum of at least two positive integers,
    where order does not matter (i.e., integer partitions excluding [n]).
    """
    dp: List[int] = [0] * (n + 1)
    dp[0] = 1

    # Use parts 1..n-1, which excludes the single-part partition [n]
    for part in range(1, n):
        for s in range(part, n + 1):
            dp[s] += dp[s - part]

    return dp[n]


def main() -> None:
    # Given example: 5 can be written in 6 ways (excluding "5" itself)
    assert count_summations(5) == 6

    result = count_summations(100)

    print(result)


if __name__ == "__main__":
    main()
