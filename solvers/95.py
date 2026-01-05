from __future__ import annotations

from typing import Dict, List, Tuple


def compute_sum_proper_divisors(limit: int) -> List[int]:
    """
    Returns array s where s[n] = sum of proper divisors of n, for 0<=n<=limit.
    """
    s = [0] * (limit + 1)
    half = limit // 2
    # Add divisor i to all multiples 2i, 3i, ... <= limit
    for i in range(1, half + 1):
        step = i
        start = i + i
        for j in range(start, limit + 1, step):
            s[j] += i
    return s


def amicable_chain_best(limit: int) -> Tuple[int, int]:
    """
    Finds the longest amicable chain where all elements are <= limit.
    Returns (best_length, smallest_member_of_best_chain).
    """
    s = compute_sum_proper_divisors(limit)

    # Quick correctness checks (from problem statement examples)
    assert s[28] == 28
    assert s[220] == 284 and s[284] == 220
    # 12496 chain example (length 5)
    example = [12496, 14288, 15472, 14536, 14264]
    for a, b in zip(example, example[1:] + example[:1]):
        assert s[a] == b

    processed = [False] * (limit + 1)

    best_len = 0
    best_min = 0

    for start in range(2, limit + 1):
        if processed[start]:
            continue

        path: List[int] = []
        idx: Dict[int, int] = {}
        n = start

        while True:
            if n == 0 or n > limit:
                # Leaves the allowed range -> no amicable chain from this start
                for v in path:
                    processed[v] = True
                break

            if processed[n]:
                # We already analyzed anything reachable from n
                for v in path:
                    processed[v] = True
                break

            if n in idx:
                # Found a cycle within current path
                cycle = path[idx[n] :]
                clen = len(cycle)
                cmin = min(cycle)
                if clen > best_len or (
                    clen == best_len and (best_min == 0 or cmin < best_min)
                ):
                    best_len = clen
                    best_min = cmin

                for v in path:
                    processed[v] = True
                break

            idx[n] = len(path)
            path.append(n)
            n = s[n]

    return best_len, best_min


def main() -> None:
    limit = 1_000_000
    best_len, best_min = amicable_chain_best(limit)
    print(best_min)


if __name__ == "__main__":
    main()
