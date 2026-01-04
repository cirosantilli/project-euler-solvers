from typing import List


def nth_lexicographic_permutation(digits: List[int], n: int) -> str:
    """
    Returns the n-th lexicographic permutation (1-indexed) of the given digits.
    """
    k = len(digits)

    # Precompute factorials up to k
    fact = [1] * (k + 1)
    for i in range(2, k + 1):
        fact[i] = fact[i - 1] * i

    # Convert to 0-indexed rank
    n -= 1

    available = digits[:]
    out: List[str] = []
    for i in range(k, 0, -1):
        block = fact[i - 1]
        idx = n // block
        n %= block
        out.append(str(available.pop(idx)))
    return "".join(out)


def main() -> None:
    digits = list(range(10))
    ans = nth_lexicographic_permutation(digits, 1_000_000)
    print(ans)


if __name__ == "__main__":
    main()
