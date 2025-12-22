from __future__ import annotations

from math import gcd
from typing import Iterable


def lcm(a: int, b: int) -> int:
    return a // gcd(a, b) * b


def lcm_range(n: int) -> int:
    ans = 1
    for x in range(2, n + 1):
        ans = lcm(ans, x)
    return ans


def main() -> None:
    # Test from the statement
    assert lcm_range(10) == 2520

    result = lcm_range(20)
    print(result)


if __name__ == "__main__":
    main()
