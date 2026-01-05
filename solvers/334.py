#!/usr/bin/env python3
"""
Project Euler 334 — Spilling the Beans

Move rule: choose i with >=2 beans:
    a[i] -= 2
    a[i-1] += 1
    a[i+1] += 1

Facts:
1) The process is Abelian (order doesn't matter).
2) Each move increases the second moment Σ i^2*a[i] by exactly 2:
      (i-1)^2 + (i+1)^2 - 2*i^2 = 2
   Therefore:
      moves = (S2_final - S2_initial) / 2

For the special input of 1500 adjacent bowls with b1..b1500 beans:
The stabilized state is a block of N+1 consecutive bowls containing 1 bean
everywhere except for one missing position ("hole").
We can solve for the block start L and hole H using conservation of Σa[i] and Σi*a[i].
"""

from collections import defaultdict, deque


def generate_b(n: int):
    """Generate b1..bn from the recurrence in the problem."""
    t = 123456
    out = []
    for _ in range(n):
        if t % 2 == 0:
            t //= 2
        else:
            t = (t // 2) ^ 926252
        out.append((t % (2**11)) + 1)
    return out


def simulate_adjacent(a: int, b: int) -> int:
    """Fast bulk stabilization simulation for test assertions (small inputs)."""
    cfg = defaultdict(int)
    cfg[0] = a
    cfg[1] = b
    q = deque([0, 1])
    moves = 0
    while q:
        i = q.popleft()
        if cfg[i] < 2:
            continue
        t = cfg[i] // 2
        cfg[i] -= 2 * t
        cfg[i - 1] += t
        cfg[i + 1] += t
        moves += t
        q.append(i - 1)
        q.append(i)
        q.append(i + 1)
    return moves


def solve():
    b = generate_b(1500)
    N = sum(b)

    # first moment and second moment of initial configuration (positions 0..1499)
    S1 = sum(i * b[i] for i in range(1500))
    S2_init = sum((i * i) * b[i] for i in range(1500))

    # block has N+1 positions: L..L+N, but one hole H missing
    sumk = N * (N + 1) // 2  # Σk for k=0..N
    sumk2 = N * (N + 1) * (2 * N + 1) // 6  # Σk^2 for k=0..N

    # Candidate L from inequality constraints (hole must lie within block)
    L = (S1 - sumk) // N  # floor division works for negative too

    # check if hole is valid; if not, increment L once
    def hole_for(Lv):
        return (N + 1) * Lv + sumk - S1

    H = hole_for(L)
    if not (L <= H <= L + N):
        L += 1
        H = hole_for(L)

    # second moment of full interval L..L+N
    interval_S2 = (N + 1) * (L * L) + 2 * L * sumk + sumk2
    S2_final = interval_S2 - H * H

    moves = (S2_final - S2_init) // 2
    return moves


if __name__ == "__main__":
    # Problem statement test assertions
    assert simulate_adjacent(2, 3) == 8
    assert generate_b(2) == [289, 145]
    assert simulate_adjacent(289, 145) == 3419100

    print(solve())
