#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0280.cpp"""
GRID_SIZE = 5
moved_seeds = 5


def make_hash(x, y, carries_seed, seeds_top, seeds_bottom):
    hash_value = 1 if carries_seed else 0
    hash_value = (hash_value << GRID_SIZE) + seeds_top
    hash_value = (hash_value << GRID_SIZE) + seeds_bottom
    hash_value = hash_value * GRID_SIZE + x
    hash_value = hash_value * GRID_SIZE + y
    return hash_value


def is_final(seeds_top, carries_seed):
    return bin(seeds_top).count("1") == moved_seeds and not carries_seed


def is_valid(x, y, carries_seed, seeds_top, seeds_bottom):
    if y == 0 and carries_seed and not (seeds_top & (1 << x)):
        return False
    if y == GRID_SIZE - 1 and (not carries_seed) and (seeds_bottom & (1 << x)):
        return False

    if is_final(seeds_top, carries_seed) and y != 0:
        return False

    seeds = bin(seeds_top).count("1") + bin(seeds_bottom).count("1")
    if carries_seed:
        seeds += 1
    if seeds != GRID_SIZE:
        return False

    return True


def solve(seeds_to_move: int) -> float:
    global moved_seeds
    moved_seeds = seeds_to_move
    epsilon = 1e-10
    all_bits = (1 << GRID_SIZE) - 1

    initial_x = 2
    initial_y = 2
    initial_carries = False
    initial_top = 0
    initial_bottom = all_bits
    initial_hash = make_hash(
        initial_x, initial_y, initial_carries, initial_top, initial_bottom
    )

    states = {}
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            for carries_seed in (0, 1):
                for seeds_top in range(all_bits + 1):
                    for seeds_bottom in range(all_bits + 1):
                        carries = carries_seed == 1
                        if not is_valid(x, y, carries, seeds_top, seeds_bottom):
                            continue
                        hash_value = make_hash(x, y, carries, seeds_top, seeds_bottom)
                        states[hash_value] = (x, y, carries, seeds_top, seeds_bottom)

    transitions = {}
    final = []
    for hash_value, state in states.items():
        x, y, carries, seeds_top, seeds_bottom = state

        if is_final(seeds_top, carries):
            final.append(hash_value)
            continue

        candidates = []
        if y > 0:
            candidates.append((x, y - 1, carries, seeds_top, seeds_bottom))
        if y < GRID_SIZE - 1:
            candidates.append((x, y + 1, carries, seeds_top, seeds_bottom))
        if x > 0:
            candidates.append((x - 1, y, carries, seeds_top, seeds_bottom))
        if x < GRID_SIZE - 1:
            candidates.append((x + 1, y, carries, seeds_top, seeds_bottom))

        next_hashes = []
        for cx, cy, ccarries, ctop, cbottom in candidates:
            if ccarries and cy == 0 and not (ctop & (1 << cx)):
                ccarries = False
                ctop |= 1 << cx

            if (not ccarries) and cy == GRID_SIZE - 1 and (cbottom & (1 << cx)):
                ccarries = True
                cbottom &= ~(1 << cx)

            next_hashes.append(make_hash(cx, cy, ccarries, ctop, cbottom))

        transitions[hash_value] = next_hashes

    if not final or not transitions:
        return

    max_hash = max(transitions.keys())

    last = [0.0] * (max_hash + 1)
    last[initial_hash] = 1.0

    expected = 0.0
    iteration = 1
    while True:
        next_probs = [0.0] * len(last)
        for from_hash, to_list in transitions.items():
            probability = last[from_hash] / len(to_list)
            for move in to_list:
                next_probs[move] += probability

        last = next_probs

        add = 0.0
        for x in final:
            add += last[x]

        add *= iteration
        expected += add

        if add < epsilon and expected > 1.0:
            break

        iteration += 1

    return expected


if __name__ == "__main__":
    print(f"{solve(5):.6f}")
