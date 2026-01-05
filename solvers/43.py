from __future__ import annotations

from typing import Dict, List, Tuple


PRIMES: List[int] = [2, 3, 5, 7, 11, 13, 17]


def is_pandigital_substring_property(n: int) -> bool:
    s = str(n)
    if len(s) != 10:
        return False
    if set(s) != set("0123456789"):
        return False
    digits = list(map(int, s))
    # d2d3d4 divisible by 2, ..., d8d9d10 divisible by 17
    for i, p in enumerate(PRIMES):
        a, b, c = digits[i + 1], digits[i + 2], digits[i + 3]
        val = 100 * a + 10 * b + c
        if val % p != 0:
            return False
    return True


def build_maps() -> Dict[int, Dict[Tuple[int, int], List[int]]]:
    """
    For each prime p, build map[(b,c)] -> [a] such that abc (3-digit, with leading zeros)
    is divisible by p and a,b,c are all distinct digits.
    """
    maps: Dict[int, Dict[Tuple[int, int], List[int]]] = {}
    for p in PRIMES:
        mp: Dict[Tuple[int, int], List[int]] = {}
        for x in range(0, 1000, p):
            a, b, c = x // 100, (x // 10) % 10, x % 10
            if a == b or a == c or b == c:
                continue
            mp.setdefault((b, c), []).append(a)
        maps[p] = mp
    return maps


def solve() -> int:
    maps = build_maps()

    # Start from the last constraint: d8 d9 d10 divisible by 17
    states: List[Tuple[Tuple[int, ...], int]] = []
    for x in range(0, 1000, 17):
        a, b, c = x // 100, (x // 10) % 10, x % 10
        if a == b or a == c or b == c:
            continue
        used = (1 << a) | (1 << b) | (1 << c)
        states.append(((a, b, c), used))  # digits are (d8,d9,d10)

    # Extend leftwards with primes 13, 11, 7, 5, 3, 2
    for p in [13, 11, 7, 5, 3, 2]:
        mp = maps[p]
        new_states: List[Tuple[Tuple[int, ...], int]] = []
        for digits, used in states:
            b, c = digits[0], digits[1]  # these become d_{i+1}, d_{i+2}
            for a in mp.get((b, c), []):  # candidate new digit d_i
                if used & (1 << a):
                    continue
                new_states.append(((a,) + digits, used | (1 << a)))
        states = new_states

    # Now each state contains digits (d2..d10). Add the remaining digit as d1 (must not be 0).
    total = 0
    all_mask = (1 << 10) - 1
    for suffix, used in states:
        remaining_mask = all_mask ^ used
        # exactly one digit remains
        if remaining_mask == 0 or (remaining_mask & (remaining_mask - 1)) != 0:
            continue
        d1 = remaining_mask.bit_length() - 1
        if d1 == 0:
            continue  # leading digit cannot be 0
        num = d1
        for d in suffix:
            num = num * 10 + d
        total += num

    # Problem statement example check
    assert is_pandigital_substring_property(1406357289)

    return total


if __name__ == "__main__":
    print(solve())
