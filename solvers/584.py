#!/usr/bin/env python3
"""
Project Euler 584 - Birthday Problem Revisited

We compute the expected number of people entering a room one-by-one until
we first find K people whose birthdays lie within D days of each other,
in a year of N days (uniform i.i.d. birthdays, wrap-around allowed).

Key idea:
Let p_n = P(no success after n people).
Then E[T] = sum_{n>=0} p_n.

We avoid summing p_n directly by using the exponential generating function:

G(t) = sum_{n>=0} p_n * t^n / n!

Then:
E[T] = ∫_0^∞ e^{-t} G(t) dt

Since births are uniform and independent, G(t) can be expressed as the
total weight of valid configurations where each day i has count c_i and
contributes weight (t/N)^{c_i}/c_i!.

We compute G(t) via a finite-state automaton (transfer matrix / DP)
encoding the constraint "no window of length (D+1) has >= K birthdays".
We then integrate with Gauss–Laguerre quadrature (weight e^{-t}).

No external libraries are used.
"""

import math


# ---------------- Gauss–Laguerre quadrature (alpha = 0) ---------------- #

def gauss_laguerre(n, eps=1e-14):
    """
    Compute nodes x[i] and weights w[i] for n-point Gauss–Laguerre quadrature
    on [0,∞) with weight exp(-x):
        ∫_0^∞ exp(-x) f(x) dx ≈ Σ w[i] f(x[i])

    Implementation: Numerical Recipes-style root finding for Laguerre L_n(x)
    with Newton refinement.
    """
    xs = [0.0] * n
    ws = [0.0] * n

    z = 0.0
    for i in range(1, n + 1):
        # Initial guess (NR heuristic, alpha=0)
        if i == 1:
            z = 3.0 / (1.0 + 2.4 * n)
        elif i == 2:
            z += 15.0 / (1.0 + 2.5 * n)
        else:
            ai = i - 2
            z += ((1.0 + 2.55 * ai) / (1.9 * ai)) * (z - xs[i - 3])

        # Newton iterations to refine root of L_n(z)
        for _ in range(100):
            # Compute L_n(z) and L_{n-1}(z)
            L0 = 1.0
            L1 = 1.0 - z
            if n == 0:
                Ln = L0
                Lnm1 = 0.0
            elif n == 1:
                Ln = L1
                Lnm1 = L0
            else:
                for k in range(2, n + 1):
                    # Recurrence:
                    # L_k = ((2k-1 - z)*L_{k-1} - (k-1)*L_{k-2}) / k
                    L2 = ((2 * k - 1 - z) * L1 - (k - 1) * L0) / k
                    L0, L1 = L1, L2
                Ln = L1
                Lnm1 = L0

            # Derivative identity:
            # z * L_n'(z) = n * (L_n(z) - L_{n-1}(z))
            dLn = n * (Ln - Lnm1) / z if z != 0.0 else -1e100

            dz = Ln / dLn
            z -= dz
            if abs(dz) < eps:
                break

        xs[i - 1] = z

        # Weight formula (alpha=0):
        # w_i = x_i / ((n+1)^2 * [L_{n+1}(x_i)]^2)
        # Compute L_{n+1}(z)
        L0 = 1.0
        L1 = 1.0 - z
        if n + 1 == 0:
            Ln1 = L0
        elif n + 1 == 1:
            Ln1 = L1
        else:
            for k in range(2, n + 2):
                L2 = ((2 * k - 1 - z) * L1 - (k - 1) * L0) / k
                L0, L1 = L1, L2
            Ln1 = L1

        ws[i - 1] = z / ((n + 1) * (n + 1) * Ln1 * Ln1)

    return xs, ws


# ---------------- State-space construction ---------------- #

def enumerate_states(window_len, max_total):
    """
    State is a tuple of length window_len-1 giving counts of the last (window_len-1) days.
    Constraint for the complement event:
        every window of length window_len has sum <= max_total
    So every state must satisfy sum(state) <= max_total.

    Returns:
        states: list of tuples
        index: dict mapping tuple -> index
    """
    state_len = window_len - 1
    states = []
    index = {}

    def rec(pos, remaining, cur):
        if pos == state_len:
            t = tuple(cur)
            index[t] = len(states)
            states.append(t)
            return
        # Nonnegative counts, sum <= max_total => we cap by remaining
        for v in range(remaining + 1):
            cur.append(v)
            rec(pos + 1, remaining - v, cur)
            cur.pop()

    rec(0, max_total, [])
    return states, index


def build_transitions(states, index, max_total):
    """
    For each state s, transitions correspond to choosing next day count c such that:
        sum(s) + c <= max_total
    Next state is shift-left and append c.

    Returns:
        trans[i] = list of (j, c) transitions
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


# ---------------- Core G(t) computation via trace DP ---------------- #

def trace_power_weighted(days, trans, max_total, t):
    """
    Computes trace(M(t)^days) where M(t) is the weighted transition matrix.

    M(t) edge weight for choosing count c on a day:
        w_c = (t/days)^c / c!

    To compute trace, we sum over starting states s:
        trace = Σ_s (M^days)[s,s]
    We do this by running a length-days DP from each basis vector e_s.

    This is the bottleneck but is feasible because:
    - state count for Earth is 120
    - outgoing edges per state <= 4
    """
    # factorials up to max_total (<=3 for Earth)
    fact = [1.0] * (max_total + 1)
    for i in range(2, max_total + 1):
        fact[i] = fact[i - 1] * i

    ratio = t / days
    w = [0.0] * (max_total + 1)
    w[0] = 1.0
    # compute ratio^c / c!
    rpow = 1.0
    for c in range(1, max_total + 1):
        rpow *= ratio
        w[c] = rpow / fact[c]

    S = len(trans)
    total = 0.0

    # For each start state, propagate a vector for 'days' steps
    for start in range(S):
        v = [0.0] * S
        v[start] = 1.0
        for _ in range(days):
            nv = [0.0] * S
            # sparse transitions
            for i, val in enumerate(v):
                if val != 0.0:
                    for j, c in trans[i]:
                        nv[j] += val * w[c]
            v = nv
        total += v[start]

    return total


def expected_people(days, within_days, target_people, quad_n=12):
    """
    Compute expected number of people until first finding `target_people`
    birthdays lying within `within_days` days of each other
    (wrap-around on a `days`-day year).

    Interpretation:
        "within D days from each other" means max distance <= D,
        which is equivalent to all lying in a window of length D+1.

    Success condition:
        some window length (D+1) has >= target_people birthdays.
    Complement:
        every such window has <= target_people-1.

    Then expectation:
        E = ∫_0^∞ e^{-t} G(t) dt
    with G(t) computed by trace(M(t)^days).
    """
    window_len = within_days + 1
    max_total = target_people - 1

    # State space (length window_len-1 tuples with sum <= max_total)
    states, index = enumerate_states(window_len, max_total)
    trans = build_transitions(states, index, max_total)

    xs, ws = gauss_laguerre(quad_n)
    acc = 0.0
    for x, wgt in zip(xs, ws):
        acc += wgt * trace_power_weighted(days, trans, max_total, x)
    return acc


def main():
    # Test values from the statement:
    wimwi = expected_people(days=10, within_days=1, target_people=3, quad_n=12)
    joka  = expected_people(days=100, within_days=7, target_people=3, quad_n=12)

    assert format(wimwi, ".8f") == "5.78688636", (wimwi, format(wimwi, ".8f"))
    assert format(joka,  ".8f") == "8.48967364", (joka,  format(joka,  ".8f"))

    # Earth question:
    earth = expected_people(days=365, within_days=7, target_people=4, quad_n=12)
    print(format(earth, ".8f"))


if __name__ == "__main__":
    main()

