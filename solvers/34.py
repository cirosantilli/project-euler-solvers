from typing import List


def precompute_factorials() -> List[int]:
    facts = [1] * 10
    f = 1
    for d in range(1, 10):
        f *= d
        facts[d] = f
    return facts


def digit_factorial_sum(n: int, facts: List[int]) -> int:
    s = 0
    while n:
        n, r = divmod(n, 10)
        s += facts[r]
    return s


def solve() -> int:
    facts = precompute_factorials()

    # Upper bound:
    # For an n-digit number, the maximum sum of digit factorials is n * 9!.
    # Find largest n where n*9! can still reach an n-digit number (>= 10^(n-1)).
    nine_fact = facts[9]
    n = 1
    while n * nine_fact >= 10 ** (n - 1):
        n += 1
    # After loop, n is first that fails, so max digits is n-1
    upper = (n - 1) * nine_fact

    total = 0
    for x in range(3, upper + 1):  # exclude 1 and 2 per statement
        if x == digit_factorial_sum(x, facts):
            total += x
    return total


if __name__ == "__main__":
    ans = solve()
    print(ans)
