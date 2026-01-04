from __future__ import annotations

from itertools import combinations, permutations
from typing import List, Set


def magic_5gon_max_16digit() -> str:
    """
    Returns the maximum 16-digit string for a magic 5-gon ring using 1..10.

    Model:
      inner nodes in clockwise order: i0,i1,i2,i3,i4
      outer nodes: o0..o4
      lines: (o0,i0,i1), (o1,i1,i2), ..., (o4,i4,i0)
      All line sums equal S.
    """
    nums: Set[int] = set(range(1, 11))

    best = ""

    # 10 must be an outer node for the string to have 16 digits (not 17),
    # so choose inner nodes from 1..9.
    for inner_set in combinations(range(1, 10), 5):
        inner_sum = sum(inner_set)

        # From:
        #   sum(outer) = 55 - sum(inner)
        #   sum(outer) = 5*S - 2*sum(inner)   (each inner used twice across 5 lines)
        # => 5*S = 55 + sum(inner)
        if (55 + inner_sum) % 5 != 0:
            continue
        S = (55 + inner_sum) // 5

        remaining_outer = nums - set(inner_set)
        if 10 not in remaining_outer:
            continue  # should not happen due to inner_set from 1..9, but keep safe

        for inner in permutations(inner_set):
            # compute required outer nodes from the inner cycle and sum S
            outer: List[int] = []
            ok = True
            for k in range(5):
                a = inner[k]
                b = inner[(k + 1) % 5]
                o = S - a - b
                if o < 1 or o > 10:
                    ok = False
                    break
                outer.append(o)
            if not ok:
                continue

            if set(outer) != remaining_outer or len(set(outer)) != 5:
                continue

            # Canonicalize: start from the line whose outer node is the smallest,
            # then read clockwise.
            start = min(range(5), key=lambda idx: outer[idx])

            parts: List[str] = []
            for t in range(5):
                idx = (start + t) % 5
                parts.append(f"{outer[idx]}{inner[idx]}{inner[(idx + 1) % 5]}")
            s = "".join(parts)

            if len(s) == 16 and s > best:
                best = s

    return best


def main() -> None:
    ans = magic_5gon_max_16digit()
    print(ans)


if __name__ == "__main__":
    main()
