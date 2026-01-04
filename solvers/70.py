from __future__ import annotations

from array import array
from typing import List, Tuple


MAX_N = 9_999_999  # 1 < n < 10^7  => n <= 9_999_999


def compute_phi_linear(limit: int) -> array:
    """
    Linear sieve computing phi[0..limit] in O(limit).
    Returns array('I') of size limit+1.
    """
    phi = array("I", [0]) * (limit + 1)
    is_comp = bytearray(limit + 1)
    primes = array("I")

    phi[1] = 1
    for i in range(2, limit + 1):
        if not is_comp[i]:
            primes.append(i)
            phi[i] = i - 1
        # iterate primes until p*i > limit
        for p in primes:
            ip = i * p
            if ip > limit:
                break
            is_comp[ip] = 1
            if i % p == 0:
                phi[ip] = phi[i] * p
                break
            else:
                phi[ip] = phi[i] * (p - 1)
    return phi


_SHIFT = [1 << (3 * d) for d in range(10)]


def digit_signature(x: int) -> int:
    """
    Packed digit counts in base 8 per digit (3 bits each).
    For numbers < 10^7, each digit count <= 7, so 3 bits is enough.
    """
    if x == 0:
        return _SHIFT[0]
    s = 0
    sh = _SHIFT
    while x:
        s += sh[x % 10]
        x //= 10
    return s


def solve(limit: int = MAX_N) -> int:
    phi = compute_phi_linear(limit)

    # Asserts from the statement / examples.
    assert phi[1] == 1
    assert phi[9] == 6
    assert phi[87109] == 79180
    assert digit_signature(87109) == digit_signature(79180)

    best_n = 0
    best_phi = 1

    # Digit-length boundaries for n, to quickly reject when phi(n) has different length.
    low = 1
    high = 10

    for n in range(2, limit + 1):
        if n == high:
            low = high
            high *= 10

        pn = int(phi[n])

        # Permutations must have same number of digits
        if pn < low or pn >= high:
            continue

        # Permutations preserve digit-sum => same mod 9
        if (n - pn) % 9 != 0:
            continue

        if digit_signature(n) != digit_signature(pn):
            continue

        if best_n == 0 or n * best_phi < best_n * pn:
            best_n = n
            best_phi = pn

    return best_n


if __name__ == "__main__":
    ans = solve()
    print(ans)
