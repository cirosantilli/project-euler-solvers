from typing import List


def reverse_int(n: int) -> int:
    return int(str(n)[::-1])


def is_palindrome(n: int) -> bool:
    s = str(n)
    return s == s[::-1]


def is_lychrel_candidate(n: int, max_iters: int = 50) -> bool:
    x = n
    for _ in range(max_iters):
        x = x + reverse_int(x)
        if is_palindrome(x):
            return False
    return True


def solve(limit: int = 10_000) -> int:
    return sum(1 for n in range(1, limit) if is_lychrel_candidate(n, 50))


if __name__ == "__main__":
    result = solve(10_000)
    print(result)
