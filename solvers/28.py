from typing import Final


def spiral_diagonals_sum(n: int) -> int:
    """
    Sum of the numbers on both diagonals in an n x n number spiral (n odd).
    """
    assert n >= 1 and n % 2 == 1
    m = (n - 1) // 2  # number of "layers" around the center

    # For layer k (1..m), side length s = 2k+1, corner sum:
    # s^2 + (s^2-(s-1)) + (s^2-2(s-1)) + (s^2-3(s-1)) = 4s^2 - 6(s-1)
    # With s=2k+1 this becomes 16k^2 + 4k + 4.
    total = 1
    total += 16 * m * (m + 1) * (2 * m + 1) // 6  # 16 * sum k^2
    total += 4 * m * (m + 1) // 2  # 4 * sum k
    total += 4 * m  # 4 * sum 1
    return total


def main() -> None:
    # Given example
    assert spiral_diagonals_sum(5) == 101
    # Small sanity checks
    assert spiral_diagonals_sum(1) == 1
    assert spiral_diagonals_sum(3) == 25

    N: Final[int] = 1001
    print(spiral_diagonals_sum(N))


if __name__ == "__main__":
    main()
