from __future__ import annotations

from typing import Dict, List


def satisfies_rule2(nums: List[int]) -> bool:
    """
    Rule 2 sufficient+necessary check for positive integers:
    For k = 1..n-1:
        sum(smallest k+1) > sum(largest k)
    """
    nums = sorted(nums)
    n = len(nums)

    prefix = [0] * (n + 1)
    for i, x in enumerate(nums, 1):
        prefix[i] = prefix[i - 1] + x

    suffix = [0] * (n + 1)
    for i in range(n - 1, -1, -1):
        suffix[i] = suffix[i + 1] + nums[i]

    for k in range(1, n):
        if prefix[k + 1] <= suffix[n - k]:
            return False
    return True


def is_special_sum_set(nums: List[int]) -> bool:
    nums = sorted(nums)
    n = len(nums)

    if not satisfies_rule2(nums):
        return False

    # Rule 1: no equal subset sums for any two non-empty disjoint subsets.
    # Enumerate all non-empty subset masks; if two masks have same sum and are disjoint -> fail.
    sum_to_masks: Dict[int, List[int]] = {}

    for mask in range(1, 1 << n):
        s = 0
        for i, x in enumerate(nums):
            if (mask >> i) & 1:
                s += x

        if s in sum_to_masks:
            for prev_mask in sum_to_masks[s]:
                if (prev_mask & mask) == 0:
                    return False
            sum_to_masks[s].append(mask)
        else:
            sum_to_masks[s] = [mask]

    return True


def read_sets(filename: str) -> List[List[int]]:
    sets: List[List[int]] = []
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            sets.append([int(x) for x in line.split(",")])
    return sets


def solve() -> int:
    # Problem statement examples
    ex1 = [81, 88, 75, 42, 87, 84, 86, 65]
    ex2 = [157, 150, 164, 119, 79, 159, 161, 139, 158]
    assert is_special_sum_set(ex1) is False
    assert is_special_sum_set(ex2) is True

    # File name from Project Euler distribution is typically 0105_sets.txt
    filenames = ["0105_sets.txt", "sets.txt"]
    all_sets: List[List[int]] | None = None
    for fn in filenames:
        try:
            all_sets = read_sets(fn)
            break
        except FileNotFoundError:
            continue
    if all_sets is None:
        raise FileNotFoundError(
            "Could not find input file (tried 0105_sets.txt and sets.txt)."
        )

    total = 0
    for s in all_sets:
        if is_special_sum_set(s):
            total += sum(s)
    return total


if __name__ == "__main__":
    result = solve()
    print(result)
