from typing import List


def count_ways(target: int, coins: List[int]) -> int:
    dp = [0] * (target + 1)
    dp[0] = 1
    for c in coins:
        for s in range(c, target + 1):
            dp[s] += dp[s - c]
    return dp[target]


def main() -> None:
    coins = [1, 2, 5, 10, 20, 50, 100, 200]

    # Basic sanity checks (no official test cases were given in the statement)
    assert count_ways(0, coins) == 1
    assert count_ways(1, coins) == 1
    assert count_ways(2, coins) == 2
    assert count_ways(5, coins) == 4
    assert count_ways(10, coins) == 11

    ans = count_ways(200, coins)

    print(ans)


if __name__ == "__main__":
    main()
