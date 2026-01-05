#!/usr/bin/env python3
"""
Project Euler 464: Möbius function and intervals

Goal: compute C(20_000_000) and print it.

No external libraries are used (only Python standard library).
"""

from __future__ import annotations

from array import array


def mobius_sieve(n: int) -> array:
    """Return an array('b') mu[0..n] containing Möbius values (-1, 0, 1).

    Uses a linear sieve (Euler sieve), O(n).
    """
    if n < 0:
        raise ValueError("n must be >= 0")
    mu = array("b", [0]) * (n + 1)
    if n == 0:
        return mu

    lp = array("I", [0]) * (n + 1)  # least prime factor
    primes: list[int] = []

    mu[1] = 1
    append_prime = primes.append

    for i in range(2, n + 1):
        if lp[i] == 0:
            lp[i] = i
            append_prime(i)
            mu[i] = -1
        li = lp[i]
        mi = mu[i]
        for p in primes:
            if p > li:
                break
            ip = i * p
            if ip > n:
                break
            lp[ip] = p
            if p == li:
                mu[ip] = 0
                break
            mu[ip] = -mi

    return mu


def compute_C(n: int) -> int:
    """Compute C(n) as defined in the problem statement."""
    if n <= 0:
        return 0

    mu = mobius_sieve(n)

    # Build compressed squarefree walk + gap weights.
    # Store u_k = k + 199*W_k and v_k = k - 199*W_k, but u_k,v_k are always even,
    # so we store (u_k/2, v_k/2) with a large bias in uint32.
    BIAS = 1 << 30

    U = array("I", [BIAS])  # u_0/2
    V = array("I", [BIAS])  # v_0/2
    start_w = array("I")  # start weights per prefix
    end_w = array("I", [0])  # end weights per squarefree index (0 unused)

    min_vk = BIAS
    max_vk = BIAS

    prev_pos = 0
    sf_count = 0
    W = 0
    zero_intervals = 0

    for pos in range(1, n + 1):
        m = mu[pos]
        if m == 0:
            continue

        gap = pos - prev_pos
        zeros = gap - 1
        if zeros:
            zero_intervals += zeros * (zeros + 1) // 2

        start_w.append(gap)
        if sf_count >= 1:
            end_w[sf_count] = gap

        prev_pos = pos
        sf_count += 1
        W += m  # m is ±1 for squarefree

        u = sf_count + 199 * W
        v = sf_count - 199 * W

        uk = (u >> 1) + BIAS
        vk = (v >> 1) + BIAS

        U.append(uk)
        V.append(vk)
        end_w.append(0)

        if vk < min_vk:
            min_vk = vk
        elif vk > max_vk:
            max_vk = vk

    # Tail after last squarefree
    tail_gap = (n + 1) - prev_pos
    tail_zeros = n - prev_pos
    if tail_zeros:
        zero_intervals += tail_zeros * (tail_zeros + 1) // 2

    end_w[sf_count] = tail_gap
    start_w.append(0)  # prefix M doesn't start any non-empty segment
    del mu

    M = sf_count
    npts = M + 1

    # Radix sort indices by (U,V): stable sort by V, then stable sort by U.
    indices = array("I", range(npts))
    tmp = array("I", [0]) * npts
    mask = 0xFFFF

    for key in (V, U):
        for shift in (0, 16):
            counts = [0] * 65536
            for idx in indices:
                counts[(key[idx] >> shift) & mask] += 1

            total = 0
            for i in range(65536):
                c = counts[i]
                counts[i] = total
                total += c

            for idx in indices:
                d = (key[idx] >> shift) & mask
                tmp[counts[d]] = idx
                counts[d] += 1

            indices, tmp = tmp, indices

    del tmp, U

    # Fenwick tree over V
    range_v = max_vk - min_vk + 1
    bit = array("Q", [0]) * (range_v + 2)
    bit_limit = range_v + 1

    V_local = V
    sw_local = start_w
    ew_local = end_w
    min_vk_local = min_vk
    bit_local = bit

    weighted_segments = 0

    for idx in indices:
        if idx:
            pos = V_local[idx] - min_vk_local + 1
            s = 0
            t = pos
            while t:
                s += bit_local[t]
                t -= t & -t
            weighted_segments += ew_local[idx] * s

        sw = sw_local[idx]
        if sw:
            pos = V_local[idx] - min_vk_local + 1
            t = pos
            while t <= bit_limit:
                bit_local[t] += sw
                t += t & -t

    return zero_intervals + weighted_segments


def main() -> None:
    # Statement checks
    mu10 = mobius_sieve(10)
    assert sum(1 for k in range(2, 11) if mu10[k] == 1) == 2  # P(2,10)
    assert sum(1 for k in range(2, 11) if mu10[k] == -1) == 4  # N(2,10)

    assert compute_C(10) == 13
    assert compute_C(500) == 16676
    assert compute_C(10_000) == 20155319

    print(compute_C(20_000_000))


if __name__ == "__main__":
    main()
