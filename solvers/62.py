from __future__ import annotations

from typing import Dict, Tuple, List


Signature = Tuple[int, int, int, int, int, int, int, int, int, int]


def digit_signature(x: int) -> Signature:
    cnt = [0] * 10
    for ch in str(x):
        cnt[ord(ch) - 48] += 1
    return tuple(cnt)  # type: ignore[return-value]


def smallest_cube_with_k_permutations(k: int) -> int:
    """
    Returns the smallest cube for which exactly k permutations of its digits are cubes.
    """
    groups: Dict[Signature, List[int]] = {}  # sig -> [count, min_cube]
    current_len = 1

    n = 1
    while True:
        cube = n * n * n
        l = len(str(cube))

        if l > current_len:
            candidates = [
                min_cube for (count, min_cube) in groups.values() if count == k
            ]
            if candidates:
                return min(candidates)
            groups.clear()
            current_len = l

        sig = digit_signature(cube)
        if sig in groups:
            groups[sig][0] += 1
            if cube < groups[sig][1]:
                groups[sig][1] = cube
        else:
            groups[sig] = [1, cube]

        n += 1


def main() -> None:
    # Given example from the statement (Project Euler 62 known fact)
    assert smallest_cube_with_k_permutations(3) == 41063625

    # Target question
    ans = smallest_cube_with_k_permutations(5)

    print(ans)


if __name__ == "__main__":
    main()
