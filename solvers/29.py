from typing import Set


def count_distinct_powers(max_a: int, max_b: int) -> int:
    vals: Set[int] = set()
    for a in range(2, max_a + 1):
        for b in range(2, max_b + 1):
            vals.add(pow(a, b))
    return len(vals)


def main() -> None:
    # Test case from the problem statement: 2 <= a <= 5, 2 <= b <= 5 -> 15 distinct terms
    assert count_distinct_powers(5, 5) == 15

    result = count_distinct_powers(100, 100)
    print(result)


if __name__ == "__main__":
    main()
