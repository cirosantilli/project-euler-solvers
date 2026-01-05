from __future__ import annotations

from typing import List, Set, Tuple


def build_near_optimum(prev: List[int]) -> List[int]:
    """
    Heuristic from the problem statement:
    If prev = {a1, a2, ..., an} is optimum, then a near-optimum for size n+1 is:
      {b, a1+b, a2+b, ..., an+b}
    where b is the "middle" element of prev (for even length, the lower middle).
    """
    prev = sorted(prev)
    mid = prev[(len(prev) - 1) // 2]
    return [mid] + [mid + x for x in prev]


def is_special_sum_set(A: List[int]) -> bool:
    """
    Exact check of the two defining properties for a special sum set:
      1) All non-empty subset sums are distinct.
      2) For any two non-empty disjoint subsets B,C:
           if |B| > |C| then S(B) > S(C).
    """
    A = sorted(A)
    n = len(A)
    masks = list(range(1, 1 << n))

    # Precompute subset sizes and sums
    subset_size = [0] * (1 << n)
    subset_sum = [0] * (1 << n)
    for m in masks:
        lsb = m & -m
        i = lsb.bit_length() - 1
        pm = m ^ lsb
        subset_size[m] = subset_size[pm] + 1
        subset_sum[m] = subset_sum[pm] + A[i]

    # Property 1: subset sums unique
    seen = set()
    for m in masks:
        s = subset_sum[m]
        if s in seen:
            return False
        seen.add(s)

    # Property 2: size implies larger sum for disjoint subsets
    # (Only need to check each unordered pair once.)
    for i, m1 in enumerate(masks):
        s1, k1 = subset_sum[m1], subset_size[m1]
        for m2 in masks[i + 1 :]:
            if m1 & m2:
                continue  # not disjoint
            s2, k2 = subset_sum[m2], subset_size[m2]
            if k1 > k2 and s1 <= s2:
                return False
            if k2 > k1 and s2 <= s1:
                return False

    return True


def set_string(A: List[int]) -> str:
    return "".join(map(str, sorted(A)))


def optimum_special_sum_set_n7(dmax: int = 6) -> List[int]:
    """
    Finds the optimum special sum set for n=7 (Project Euler 103)
    by searching small perturbations around the near-optimal construction
    derived from the known optimum n=6 set.
    """
    # Known optimum for n=6 (from the problem statement)
    prev6 = [11, 18, 19, 20, 22, 25]

    base = build_near_optimum(prev6)  # near-optimum seed for n=7
    n = 7

    best: List[int] | None = None
    best_sum = float("inf")
    cur: List[int] = []

    def dfs(i: int, last: int, subset_sums: Set[int], total: int, d: int) -> None:
        nonlocal best, best_sum

        if total >= best_sum:
            return

        if i == n:
            # We already ensured subset-sum uniqueness incrementally.
            # Now enforce the full definition's property (2) exactly.
            if is_special_sum_set(cur):
                best = cur.copy()
                best_sum = total
            return

        for delta in range(-d, d + 1):
            x = base[i] + delta
            if x <= last:
                continue

            new_sums = {s + x for s in subset_sums}
            if subset_sums & new_sums:
                continue  # violates uniqueness

            cur.append(x)
            dfs(i + 1, x, subset_sums | new_sums, total + x, d)
            cur.pop()

    for d in range(dmax + 1):
        dfs(0, 0, {0}, 0, d)

    assert best is not None
    return best


if __name__ == "__main__":
    # True optimum for n=6 from the statement
    opt6 = [11, 18, 19, 20, 22, 25]
    assert sum(opt6) == 115
    assert set_string(opt6) == "111819202225"
    assert is_special_sum_set(opt6)

    # ---- Solve n=7 and verify result ----
    print(set_string(optimum_special_sum_set_n7()))
