from typing import List


def is_palindrome_base2(n: int) -> bool:
    s = bin(n)[2:]
    return s == s[::-1]


def generate_decimal_palindromes(limit: int) -> List[int]:
    pals: List[int] = []
    # For limit < 1_000_000, generating from i in [1..999] covers all palindromes up to 6 digits.
    for i in range(1, 1000):
        s = str(i)

        # Odd-length palindrome: mirror all but last digit
        odd = int(s + s[-2::-1])
        if odd < limit:
            pals.append(odd)

        # Even-length palindrome: mirror all digits
        even = int(s + s[::-1])
        if even < limit:
            pals.append(even)

    return pals


def solve(limit: int = 1_000_000) -> int:
    total = 0
    for n in generate_decimal_palindromes(limit):
        # Binary palindrome cannot be even (would end with 0 -> leading zero when reversed)
        if (n & 1) == 0:
            continue
        if is_palindrome_base2(n):
            total += n
    return total


def main() -> None:
    # Provided example: 585 is palindromic in base 10 and base 2
    assert str(585) == str(585)[::-1]
    assert is_palindrome_base2(585)

    ans = solve(1_000_000)

    print(ans)


if __name__ == "__main__":
    main()
