def count_combinatoric_selections(limit_n: int, threshold: int) -> int:
    total = 0
    for n in range(1, limit_n + 1):
        c = 1  # C(n, 0)
        for r in range(1, n // 2 + 1):
            # C(n, r) = C(n, r-1) * (n-r+1) / r
            c = c * (n - r + 1) // r
            if c > threshold:
                # By symmetry and unimodality, all r in [r, n-r] exceed threshold
                total += n - 2 * r + 1
                break
    return total


def main() -> None:
    ans = count_combinatoric_selections(100, 1_000_000)
    print(ans)


if __name__ == "__main__":
    main()
