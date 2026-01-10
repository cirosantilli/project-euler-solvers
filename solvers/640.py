#!/usr/bin/env python3
"""Project Euler 640: Shut the Box

Compute the optimal expected number of turns to win.

We model the game as a Markov Decision Process with 2^N states.
State is a bitmask of which cards are face-down (1 = down).
Each turn we observe (x, y) and toggle one card among {x, y, x+y}.

We solve for the optimal expected time using policy iteration.
The problem statement provides a check value for Alice's smaller variant; we assert it.
"""


def _unique_actions(x: int, y: int):
    """Return unique actions from (x, y, x+y) preserving order."""
    seen = set()
    out = []
    for v in (x, y, x + y):
        if v not in seen:
            seen.add(v)
            out.append(v)
    return out


def build_probs_and_toggles(num_cards: int, values):
    """Two independent uniform draws over `values`.

    Returns:
      probs: list of probabilities, length M
      toggles: list of tuples; each tuple contains 2 or 3 XOR masks.
               Applying an action to state s is: s ^ mask.
    """
    m = len(values)
    p = 1.0 / (m * m)

    probs = []
    toggles = []
    for x in values:
        for y in values:
            probs.append(p)
            acts = _unique_actions(x, y)
            masks = tuple(1 << (a - 1) for a in acts if 1 <= a <= num_cards)
            toggles.append(masks)

    return probs, toggles


def optimal_expected_turns(num_cards: int, probs, toggles):
    """Return optimal expected turns from the start state (all cards up)."""
    n = num_cards
    goal = (1 << n) - 1
    m = len(probs)

    # Policy for non-goal states only: policy[s][k] is an index into toggles[k].
    policy = [[0] * m for _ in range(goal)]
    for s in range(goal):
        pol = policy[s]
        for k, tgs in enumerate(toggles):
            chosen = 0
            # Prefer toggling an up card to down if available.
            for j, mask in enumerate(tgs):
                if (s & mask) == 0:
                    chosen = j
                    break
            pol[k] = chosen

    # Value function (include goal for convenient indexing).
    v = [0.0] * (1 << n)

    # Policy iteration parameters (tuned for N=12).
    w = 1.35  # over-relaxation (1.0 = plain Gauss-Seidel)
    eval_tol = 1e-10  # evaluation sweep stopping tolerance
    improve_eps = 1e-12
    max_outer = 80
    max_eval_sweeps = 1500

    for _ in range(max_outer):
        # --- policy evaluation (approximate) ---
        for _sweep in range(max_eval_sweeps):
            delta = 0.0
            for s in range(goal):
                old = v[s]
                exp = 0.0
                pol = policy[s]
                for k in range(m):
                    exp += probs[k] * v[s ^ toggles[k][pol[k]]]
                target = 1.0 + exp
                new = old + w * (target - old)
                v[s] = new
                diff = new - old
                if diff < 0.0:
                    diff = -diff
                if diff > delta:
                    delta = diff
            if delta < eval_tol:
                break

        # --- policy improvement ---
        changed = False
        for s in range(goal):
            pol = policy[s]
            for k, tgs in enumerate(toggles):
                best = pol[k]
                best_val = v[s ^ tgs[best]]
                for j in range(len(tgs)):
                    vv = v[s ^ tgs[j]]
                    if vv < best_val - improve_eps:
                        best_val = vv
                        best = j
                if best != pol[k]:
                    pol[k] = best
                    changed = True
        if not changed:
            break

    # Final high-precision evaluation for stabilized policy (plain GS).
    final_tol = 1e-13
    for _ in range(200000):
        delta = 0.0
        for s in range(goal):
            old = v[s]
            exp = 0.0
            pol = policy[s]
            for k in range(m):
                exp += probs[k] * v[s ^ toggles[k][pol[k]]]
            new = 1.0 + exp
            v[s] = new
            diff = new - old
            if diff < 0.0:
                diff = -diff
            if diff > delta:
                delta = diff
        if delta < final_tol:
            break

    return v[0]


def solve():
    # Alice's check game: 2 fair coins valued {1,2}, 4 cards.
    probs_a, toggles_a = build_probs_and_toggles(4, values=(1, 2))
    alice = optimal_expected_turns(4, probs_a, toggles_a)
    assert round(alice, 6) == 5.673651, alice

    # Bob's game: 2 fair dice {1..6}, 12 cards.
    probs_b, toggles_b = build_probs_and_toggles(12, values=(1, 2, 3, 4, 5, 6))
    bob = optimal_expected_turns(12, probs_b, toggles_b)
    return bob


def main():
    ans = solve()
    print(f"{ans:.6f}")


if __name__ == "__main__":
    main()
