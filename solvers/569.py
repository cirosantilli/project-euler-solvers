#!/usr/bin/env python3
"""
Project Euler 569: Prime Mountain Range

We generate the first 2N primes, build the coordinates of the N peaks, then compute

    S(N) = sum_{k=1..N} P(k)

where P(k) is the number of earlier peaks visible from peak k.

No third-party libraries are used.
"""

from __future__ import annotations

from array import array
import math


# ----------------------------
# Prime generation (odd sieve)
# ----------------------------


def _upper_bound_nth_prime(n: int) -> int:
    """
    A safe upper bound for the nth prime for n >= 6:
        p_n < n (log n + log log n) + 10
    """
    if n < 6:
        return 15
    nn = float(n)
    return int(nn * (math.log(nn) + math.log(math.log(nn))) + 10.0)


def _odd_sieve(limit: int) -> bytearray:
    """
    Sieve of Eratosthenes for odd numbers up to 'limit' inclusive.
    Returns a bytearray 'is_prime' where index i represents number (2*i + 1).
    So is_prime[0] corresponds to 1 (not prime).
    """
    size = (limit // 2) + 1
    is_prime = bytearray(b"\x01") * size
    is_prime[0] = 0  # 1 is not prime

    r = int(limit**0.5)
    # i represents p = 2*i+1, start i=1 -> p=3
    for i in range(1, (r // 2) + 1):
        if is_prime[i]:
            p = 2 * i + 1
            start = (p * p) // 2
            # mark start, start+p, ...
            is_prime[start::p] = b"\x00" * (((size - 1 - start) // p) + 1)
    return is_prime


def build_peaks(n_peaks: int) -> tuple[array, array]:
    """
    Build arrays X[k], Y[k] (0-based) for the first n_peaks peaks of the Prime Mountain Range.

    Peak k (1-based) uses primes p_{2k-1} (up) and p_{2k} (down):
        X_k = sum_{i=1..2k-1} p_i
        Y_k = p1 - p2 + p3 - ... - p_{2k-2} + p_{2k-1}

    Returns:
        (X, Y) as array('q') each, length n_peaks.
    """
    if n_peaks <= 0:
        return array("q"), array("q")

    need_primes = 2 * n_peaks
    limit = _upper_bound_nth_prime(need_primes)

    while True:
        is_prime = _odd_sieve(limit)

        X = array("q", [0]) * n_peaks
        Y = array("q", [0]) * n_peaks

        x_base = 0
        y_base = 0
        count = 0  # number of primes consumed
        peak_i = 0
        x_peak = 0
        y_peak = 0

        # prime 2
        count = 1
        up = 2
        x_peak = x_base + up
        y_peak = y_base + up
        X[0] = x_peak
        Y[0] = y_peak
        peak_i = 1

        if need_primes == 1:
            return X, Y

        # scan odd primes
        for idx in range(1, len(is_prime)):
            if not is_prime[idx]:
                continue
            p = 2 * idx + 1
            count += 1
            if count & 1:  # odd index prime => "up" prime gives a new peak
                x_peak = x_base + p
                y_peak = y_base + p
                X[peak_i] = x_peak
                Y[peak_i] = y_peak
                peak_i += 1
            else:  # even index prime => "down" prime updates base
                x_base = x_peak + p
                y_base = y_peak - p

            if count == need_primes:
                return X, Y

        # If we reach here, limit was too small (should be rare with the bound).
        limit = int(limit * 1.1) + 1000


# --------------------------------------
# Visibility counting (output-sensitive)
# --------------------------------------


def visibility_sum(
    X: array, Y: array, want_P: bool = False
) -> tuple[int, array | None]:
    """
    Compute S(N) = sum P(k) where P(k) is the number of visible earlier peaks from peak k.

    Key property used:
      The visible peaks from k form a chain v1, v2, ...
      where v1 = k-1, and each next vertex v_{t+1} belongs to the visibility list of v_t.
      This lets us compute all visibility lists in total time roughly proportional to the
      number of visible pairs.

    Storage is compact:
      - one flattened array 'vis' holds all visibility lists back-to-back
      - 'offs[k]' and 'ln[k]' provide the slice for peak k
    """
    n = len(X)
    if n <= 1:
        return 0, array("I") if want_P else None

    offs = array("I", [0]) * n
    ln = array("I", [0]) * n
    vis = array("I")  # flattened visibility lists (indices of peaks)

    total = 0

    # locals for speed
    X_arr = X
    Y_arr = Y
    offs_arr = offs
    ln_arr = ln
    vis_arr = vis
    vis_append = vis_arr.append

    for k in range(1, n):
        xk = X_arr[k]
        yk = Y_arr[k]

        start_k = len(vis_arr)
        offs_arr[k] = start_k

        # First visible peak is always k-1 (adjacent peaks).
        a = k - 1
        vis_append(a)
        l = 1

        m_num = yk - Y_arr[a]
        m_den = xk - X_arr[a]

        while True:
            offa = offs_arr[a]
            enda = offa + ln_arr[a]
            found = False

            # Scan the visibility list of 'a' from nearest to farthest;
            # the first one with a smaller slope is the next visible peak for k.
            for pos in range(offa, enda):
                cand = vis_arr[pos]
                dy = yk - Y_arr[cand]
                dx = xk - X_arr[cand]
                if dy * m_den < m_num * dx:  # slope(k,cand) < current min slope
                    vis_append(cand)
                    l += 1
                    a = cand
                    m_num = dy
                    m_den = dx
                    found = True
                    break

            if not found:
                break

        ln_arr[k] = l
        total += l

    return total, ln_arr if want_P else None


def solve(n_peaks: int, want_P: bool = False) -> tuple[int, array | None]:
    X, Y = build_peaks(n_peaks)
    return visibility_sum(X, Y, want_P=want_P)


# ----------------------------
# Self-test (from statement)
# ----------------------------


def _self_test() -> None:
    s100, P = solve(100, want_P=True)
    assert P is not None
    # Problem statement test values
    assert P[2] == 1, f"Expected P(3)=1, got {P[2]}"
    assert P[8] == 3, f"Expected P(9)=3, got {P[8]}"
    assert s100 == 227, f"Expected sum_{k<=100} P(k)=227, got {s100}"


def main() -> None:
    _self_test()
    ans, _ = solve(2_500_000, want_P=False)
    print(ans)


if __name__ == "__main__":
    main()
