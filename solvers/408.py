import math
from array import array
from typing import List, Tuple

MOD = 1_000_000_007


def generate_obstacles(n: int) -> List[Tuple[int, int]]:
    m = int(math.isqrt(n))
    squares = [i * i for i in range(1, m + 1)]
    max_sum_root = int(math.isqrt(2 * n))
    sum_squares = set(i * i for i in range(1, max_sum_root + 1))

    obstacles: List[Tuple[int, int]] = []
    append = obstacles.append
    contains = sum_squares.__contains__
    for a2 in squares:
        for b2 in squares:
            if contains(a2 + b2):
                append((a2, b2))

    obstacles.sort(key=lambda p: (p[0] + p[1], p[0]))
    return obstacles


def precompute_factorials(limit: int) -> Tuple[array, array]:
    fact = array("I", [0]) * (limit + 1)
    fact[0] = 1
    mod = MOD
    for i in range(1, limit + 1):
        fact[i] = (fact[i - 1] * i) % mod

    inv_fact = array("I", [0]) * (limit + 1)
    inv_fact[limit] = pow(fact[limit], mod - 2, mod)
    for i in range(limit, 0, -1):
        inv_fact[i - 1] = (inv_fact[i] * i) % mod
    return fact, inv_fact


def count_paths(n: int) -> int:
    obstacles = generate_obstacles(n)
    limit = 2 * n
    fact, inv_fact = precompute_factorials(limit)
    mod = MOD

    k = len(obstacles)
    xs = [0] * k
    ys = [0] * k
    for i, (x, y) in enumerate(obstacles):
        xs[i] = x
        ys[i] = y

    ways = [0] * k
    for i in range(k):
        xi = xs[i]
        yi = ys[i]
        total = (fact[xi + yi] * inv_fact[xi] % mod) * inv_fact[yi] % mod
        for j in range(i):
            xj = xs[j]
            yj = ys[j]
            if xj <= xi and yj <= yi:
                dx = xi - xj
                dy = yi - yj
                total -= ways[j] * (
                    (fact[dx + dy] * inv_fact[dx] % mod) * inv_fact[dy] % mod
                )
        ways[i] = total % mod

    total_paths = (fact[2 * n] * inv_fact[n] % mod) * inv_fact[n] % mod
    for i in range(k):
        xi = xs[i]
        yi = ys[i]
        total_paths -= ways[i] * (
            (fact[(n - xi) + (n - yi)] * inv_fact[n - xi] % mod)
            * inv_fact[n - yi]
            % mod
        )
    return total_paths % mod


if __name__ == "__main__":
    assert count_paths(5) == 252
    assert count_paths(16) == 596_994_440
    assert count_paths(1000) == 341_920_854
    print(count_paths(10_000_000))
