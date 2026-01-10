#!/usr/bin/env python3
"""
Project Euler 584 — Birthday Problem Revisited (pure Python, no external libraries)

We want the expected number of people entering a room until we first find K people
whose birthdays are within D days of each other (wrap-around allowed) on an N-day year.

Let p_n = P(condition has NOT occurred after n people). Then:
    E[T] = sum_{n>=0} p_n

We compute this using an exponential generating function and Gauss–Laguerre quadrature:
    G(t) = sum_{n>=0} p_n * t^n / n!
    E[T] = ∫_0^∞ e^{-t} G(t) dt

A transfer matrix (finite-state automaton) lets us compute G(t) efficiently for a given t.
"""

import math


# ---------------- Gauss–Laguerre quadrature (alpha = 0) ---------------- #


def gauss_laguerre(n: int, eps: float = 1e-14):
    """
    n-point Gauss–Laguerre nodes x[i] and weights w[i] for:
        ∫_0^∞ e^{-x} f(x) dx  ≈  Σ w[i] f(x[i])

    Uses Newton refinement on roots of Laguerre polynomial L_n (Numerical Recipes style).
    """
    xs = [0.0] * n
    ws = [0.0] * n

    z = 0.0
    for i in range(1, n + 1):
        # Initial guesses (alpha = 0)
        if i == 1:
            z = 3.0 / (1.0 + 2.4 * n)
        elif i == 2:
            z += 15.0 / (1.0 + 2.5 * n)
        else:
            ai = i - 2
            z += ((1.0 + 2.55 * ai) / (1.9 * ai)) * (z - xs[i - 3])

        # Newton iterations
        for _ in range(100):
            # L_n(z) and L_{n-1}(z)
            L0 = 1.0
            L1 = 1.0 - z
            if n == 1:
                Ln = L1
                Lnm1 = L0
            else:
                for k in range(2, n + 1):
                    L2 = ((2 * k - 1 - z) * L1 - (k - 1) * L0) / k
                    L0, L1 = L1, L2
                Ln = L1
                Lnm1 = L0

            # z * L_n'(z) = n (L_n(z) - L_{n-1}(z))
            dLn = n * (Ln - Lnm1) / z
            dz = Ln / dLn
            z -= dz
            if abs(dz) < eps:
                break

        xs[i - 1] = z

        # Weight: w_i = x_i / ((n+1)^2 * [L_{n+1}(x_i)]^2)
        L0 = 1.0
        L1 = 1.0 - z
        for k in range(2, n + 2):
            L2 = ((2 * k - 1 - z) * L1 - (k - 1) * L0) / k
            L0, L1 = L1, L2
        Ln1 = L1
        ws[i - 1] = z / ((n + 1) * (n + 1) * Ln1 * Ln1)

    return xs, ws


# ---------------- State-space (transfer matrix) ---------------- #


def enumerate_states(window_len: int, max_total: int):
    """
    State = counts of the last (window_len - 1) days (a tuple).

    Complement event ("not yet succeeded"):
        every window of length window_len has sum <= max_total

    So every state satisfies sum(state) <= max_total.
    """
    state_len = window_len - 1
    states = []
    index = {}

    def rec(pos: int, remaining: int, cur):
        if pos == state_len:
            t = tuple(cur)
            index[t] = len(states)
            states.append(t)
            return
        for v in range(remaining + 1):
            cur.append(v)
            rec(pos + 1, remaining - v, cur)
            cur.pop()

    rec(0, max_total, [])
    return states, index


def build_transitions(states, index, max_total: int):
    """
    Transition: choose today's count c with sum(state) + c <= max_total.
    Next state is shift-left and append c.

    Stored as sparse adjacency lists: trans[i] = [(j, c), ...]
    """
    trans = []
    for s in states:
        ssum = sum(s)
        opts = []
        for c in range(max_total - ssum + 1):
            ns = s[1:] + (c,)
            opts.append((index[ns], c))
        trans.append(opts)
    return trans


# ---------------- G(t) via trace(M(t)^N) ---------------- #


def trace_power_weighted(N: int, trans, max_total: int, t: float) -> float:
    """
    For fixed t, define weights per day-count c:
        w_c = (t/N)^c / c!

    Let M(t) be the weighted transition operator.
    Then:
        G(t) = trace(M(t)^N)

    Trace counts closed walks of length N in the state graph, which corresponds to
    cyclic day-count sequences and enforces wrap-around constraints.
    """
    ratio = t / N

    # max_total is tiny (2 or 3), so compute weights directly
    w0 = 1.0
    w1 = ratio
    w2 = (ratio * ratio) * 0.5 if max_total >= 2 else 0.0
    w3 = (ratio * ratio * ratio) / 6.0 if max_total >= 3 else 0.0
    w = (w0, w1, w2, w3)

    S = len(trans)
    total = 0.0

    for start in range(S):
        v = [0.0] * S
        v[start] = 1.0
        for _ in range(N):
            nv = [0.0] * S
            for i in range(S):
                val = v[i]
                if val:
                    for j, c in trans[i]:
                        nv[j] += val * w[c]
            v = nv
        total += v[start]

    return total


def expected_people(N: int, within_days: int, target_people: int, quad_n: int) -> float:
    """
    Expected number of people until first finding target_people birthdays within within_days.

    within_days = D  => window_len = D+1
    target_people = K => complement uses max_total = K-1
    """
    window_len = within_days + 1
    max_total = target_people - 1

    states, index = enumerate_states(window_len, max_total)
    trans = build_transitions(states, index, max_total)

    xs, ws = gauss_laguerre(quad_n)
    acc = 0.0
    for x, wgt in zip(xs, ws):
        acc += wgt * trace_power_weighted(N, trans, max_total, x)
    return acc


def main():
    # Test values given in the problem statement (assert to 8 decimals)
    wimwi = expected_people(N=10, within_days=1, target_people=3, quad_n=16)
    joka = expected_people(N=100, within_days=7, target_people=3, quad_n=20)
    assert format(wimwi, ".8f") == "5.78688636", format(wimwi, ".10f")
    assert format(joka, ".8f") == "8.48967364", format(joka, ".10f")

    # Earth (365-day year, 4 people within 7 days)
    # 28-point Gauss–Laguerre is enough to get the answer correct to 8 decimals.
    earth = expected_people(N=365, within_days=7, target_people=4, quad_n=28)
    print(format(earth, ".8f"))


if __name__ == "__main__":
    main()
