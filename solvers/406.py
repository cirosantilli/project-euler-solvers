import math
from typing import Dict, Tuple


def max_numbers(t: float, a: float, b: float, cap: int) -> int:
    memo: Dict[Tuple[int, int], int] = {}

    def helper(i: int, j: int) -> int:
        rem = t - i * a - j * b
        if rem < 0.0:
            return 0
        key = (i, j)
        if key in memo:
            return memo[key]
        n = 1 + helper(i + 1, j) + helper(i, j + 1)
        if n > cap:
            n = cap
        memo[key] = n
        return n

    return helper(0, 0)


def min_cost(n: int, a: float, b: float) -> float:
    if n <= 1:
        return 0.0
    hi = 1.0
    while True:
        if max_numbers(hi, a, b, n) >= n:
            break
        hi *= 2.0
    lo = 0.0
    for _ in range(80):
        mid = (lo + hi) / 2.0
        if max_numbers(mid, a, b, n) >= n:
            hi = mid
        else:
            lo = mid
    return hi


def main() -> None:
    assert abs(min_cost(5, 2.0, 3.0) - 5.0) < 1e-9
    assert abs(min_cost(500, math.sqrt(2.0), math.sqrt(3.0)) - 13.22073197) < 1e-6
    assert abs(min_cost(20000, 5.0, 7.0) - 82.0) < 1e-9
    assert abs(min_cost(2000000, math.sqrt(5.0), math.sqrt(7.0)) - 49.63755955) < 1e-6

    fib = [0, 1, 1]
    for _ in range(3, 31):
        fib.append(fib[-1] + fib[-2])

    total = 0.0
    n = 10**12
    for k in range(1, 31):
        a = math.sqrt(float(k))
        b = math.sqrt(float(fib[k]))
        total += min_cost(n, a, b)

    print(f"{total:.8f}")


if __name__ == "__main__":
    main()
