from typing import List


def digit_fifth_power_sum(n: int, fifth: List[int]) -> int:
    s = 0
    while n > 0:
        n, d = divmod(n, 10)
        s += fifth[d]
    return s


def solve() -> int:
    # Precompute fifth powers of digits 0..9
    fifth = [d**5 for d in range(10)]

    # Upper bound reasoning:
    # For a number with k digits, the maximum sum of fifth powers is k * 9^5.
    # Find largest k where k*9^5 can still reach a k-digit number (>= 10^(k-1)).
    # It turns out k=6 is the last possible (since for k=7, 7*9^5 < 10^6).
    upper = 6 * fifth[9]  # 6 * 59049 = 354294

    matches: List[int] = []
    for n in range(2, upper + 1):  # exclude 1 as "not a sum" (per statement)
        if n == digit_fifth_power_sum(n, fifth):
            matches.append(n)

    ans = sum(matches)

    # Known results for Project Euler #30
    assert matches == [4150, 4151, 54748, 92727, 93084, 194979]

    return ans


if __name__ == "__main__":
    print(solve())
