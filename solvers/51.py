from __future__ import annotations

from math import isqrt
from typing import List, Tuple


def sieve(n: int) -> Tuple[bytearray, List[int]]:
    """Return (is_prime[0..n], list_of_primes_up_to_n)."""
    if n < 1:
        return bytearray(b"\x00") * (n + 1), []
    is_prime = bytearray(b"\x01") * (n + 1)
    is_prime[0:2] = b"\x00\x00"
    r = isqrt(n)
    for i in range(2, r + 1):
        if is_prime[i]:
            start = i * i
            step = i
            is_prime[start : n + 1 : step] = b"\x00" * (((n - start) // step) + 1)
    primes = [i for i in range(2, n + 1) if is_prime[i]]
    return is_prime, primes


def count_prime_family_for_positions(p: int, idxs: List[int]) -> int:
    """
    For a fixed prime p and fixed digit positions idxs, replace those positions
    with the same digit r in [0..9] (skipping leading zero) and count primes.
    """
    s = str(p)
    n = len(s)
    upper = 10**n - 1
    is_prime, _ = sieve(upper)

    digits = [ord(c) - 48 for c in s]
    d0 = digits[idxs[0]]
    assert all(
        digits[i] == d0 for i in idxs
    ), "chosen positions must share same digit in p"

    pow10 = [10 ** (n - 1 - i) for i in range(n)]
    shift = sum(pow10[i] for i in idxs)
    lead = 0 in idxs

    cnt = 0
    for r in range(10):
        if lead and r == 0:
            continue
        num = p + (r - d0) * shift
        if is_prime[num]:
            cnt += 1
    return cnt


def find_smallest_prime_in_family(target: int = 8) -> int:
    """
    Search by number of digits. For each prime p, consider subsets of positions
    containing the same digit (so that p is in the family), excluding the last digit
    (otherwise you can't reach 8 primes). For each subset, count primes in the family.
    """
    for ndigits in range(2, 10):
        upper = 10**ndigits - 1
        lower = 10 ** (ndigits - 1)
        is_prime, primes = sieve(upper)
        pow10 = [10 ** (ndigits - 1 - i) for i in range(ndigits)]

        for p in primes:
            if p < lower:
                continue

            s = str(p)
            ds = [ord(c) - 48 for c in s]

            # group positions by digit, excluding the last digit (can't get family size 8 otherwise)
            pos_lists: List[List[int]] = [[] for _ in range(10)]
            for i, dig in enumerate(ds[:-1]):
                pos_lists[dig].append(i)

            for d, pos in enumerate(pos_lists):
                m = len(pos)
                if m == 0:
                    continue

                # For 8-prime families, it's enough (and much faster) to only consider
                # subset sizes that are multiples of 3: since 10^k ≡ 1 (mod 3),
                # shift mod 3 == (#replaced digits) mod 3; otherwise at least 3 replacements
                # yield numbers divisible by 3, making it impossible to have 8 primes.
                if target >= 8 and m < 3:
                    continue

                for mask in range(1, 1 << m):
                    k = mask.bit_count()
                    if k % 3 != 0:
                        continue

                    shift = 0
                    lead = False
                    for j in range(m):
                        if (mask >> j) & 1:
                            idx = pos[j]
                            shift += pow10[idx]
                            if idx == 0:
                                lead = True

                    cnt = 0
                    for r in range(10):
                        if lead and r == 0:
                            continue
                        num = p + (r - d) * shift
                        if is_prime[num]:
                            cnt += 1
                    if cnt >= target:
                        return p

    raise ValueError("Not found within searched digit range")


def main() -> None:
    # Examples from the statement:
    assert count_prime_family_for_positions(13, [0]) == 6
    assert count_prime_family_for_positions(56003, [2, 3]) == 7

    ans = find_smallest_prime_in_family(8)
    print(ans)


if __name__ == "__main__":
    main()
