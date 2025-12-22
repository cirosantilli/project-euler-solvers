from typing import Final


def binom(n: int, k: int) -> int:
    """Compute C(n, k) exactly using an integer multiplicative formula."""
    if k < 0 or k > n:
        return 0
    k = min(k, n - k)
    res = 1
    for i in range(1, k + 1):
        res = res * (n - k + i) // i
    return res


def lattice_paths(grid_n: int, grid_m: int) -> int:
    """
    Number of lattice paths from top-left to bottom-right in an n x m grid,
    moving only right and down.
    """
    return binom(grid_n + grid_m, grid_n)


def main() -> None:
    # Test from statement: 2x2 grid has 6 routes
    assert lattice_paths(2, 2) == 6

    # Project Euler #15 target: 20x20 grid
    ans: Final[int] = lattice_paths(20, 20)
    print(ans)


if __name__ == "__main__":
    main()
