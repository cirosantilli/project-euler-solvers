from __future__ import annotations

from typing import Dict, List, Optional, Set, Tuple


def polygonal(s: int, n: int) -> int:
    """
    s-gonal number P_{s,n} = n((s-2)n - (s-4)) / 2, for s >= 3
    """
    return n * ((s - 2) * n - (s - 4)) // 2


def generate_4digit_polygonals(s: int) -> List[int]:
    nums: List[int] = []
    n = 1
    while True:
        val = polygonal(s, n)
        if val >= 10000:
            break
        if 1000 <= val <= 9999:
            # last two digits must be a valid next "prefix" (10..99) for a 4-digit number
            if val % 100 >= 10:
                nums.append(val)
        n += 1
    return nums


def build_prefix_map(nums: List[int]) -> Dict[int, List[int]]:
    mp: Dict[int, List[int]] = {}
    for x in nums:
        pref = x // 100
        mp.setdefault(pref, []).append(x)
    return mp


def find_cycle_sum() -> int:
    types = [3, 4, 5, 6, 7, 8]
    nums_by_type: Dict[int, List[int]] = {
        t: generate_4digit_polygonals(t) for t in types
    }
    pref_map: Dict[int, Dict[int, List[int]]] = {
        t: build_prefix_map(nums_by_type[t]) for t in types
    }

    Path = List[Tuple[int, int]]  # (number, type)

    def dfs(path: Path, used_types: Set[int], used_nums: Set[int]) -> Optional[Path]:
        if len(path) == 6:
            last_num = path[-1][0]
            first_num = path[0][0]
            if last_num % 100 == first_num // 100:
                return path
            return None

        suffix = path[-1][0] % 100
        for t in types:
            if t in used_types:
                continue
            for nxt in pref_map[t].get(suffix, []):
                if nxt in used_nums:
                    continue
                res = dfs(path + [(nxt, t)], used_types | {t}, used_nums | {nxt})
                if res is not None:
                    return res
        return None

    # Fix the start type to 8 (octagonal) to break rotational symmetry of the cycle.
    for start in nums_by_type[8]:
        res = dfs([(start, 8)], {8}, {start})
        if res is not None:
            return sum(x for x, _t in res)

    raise RuntimeError("No cycle found")


def main() -> None:
    # Problem statement examples
    assert polygonal(3, 127) == 8128
    assert polygonal(4, 91) == 8281
    assert polygonal(5, 44) == 2882

    ans = find_cycle_sum()

    print(ans)


if __name__ == "__main__":
    main()
