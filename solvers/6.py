from typing import Final


def sum_of_squares(n: int) -> int:
    # 1^2 + 2^2 + ... + n^2 = n(n+1)(2n+1)/6
    return n * (n + 1) * (2 * n + 1) // 6


def square_of_sum(n: int) -> int:
    # (1 + 2 + ... + n)^2 = (n(n+1)/2)^2
    s = n * (n + 1) // 2
    return s * s


def solve(n: int) -> int:
    return square_of_sum(n) - sum_of_squares(n)


def main() -> None:
    # Given example test
    assert solve(10) == 2640

    N: Final[int] = 100
    ans = solve(N)

    print(ans)


if __name__ == "__main__":
    main()
