from typing import Tuple


def is_palindrome(n: int) -> bool:
    s = str(n)
    return s == s[::-1]


def largest_palindrome_product(lo: int, hi: int) -> Tuple[int, int, int]:
    """
    Returns (best_palindrome, factor1, factor2) for factors in [lo, hi].
    """
    best = 0
    best_a = 0
    best_b = 0

    for a in range(hi, lo - 1, -1):
        # If even the maximum product with this 'a' can't beat best, we can stop.
        if a * hi < best:
            break

        for b in range(a, lo - 1, -1):
            prod = a * b

            # As b decreases, prod decreases; once <= best, no need to continue.
            if prod <= best:
                break

            if is_palindrome(prod):
                best = prod
                best_a = a
                best_b = b
                # For fixed a, this is the largest palindrome since b is descending.
                break

    return best, best_a, best_b


def main() -> None:
    # Given example: largest palindrome from product of two 2-digit numbers.
    assert largest_palindrome_product(10, 99)[0] == 9009
    ans, a, b = largest_palindrome_product(100, 999)
    print(ans)


if __name__ == "__main__":
    main()
