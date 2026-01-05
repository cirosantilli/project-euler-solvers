#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0208.cpp"""
num_visited = [0, 0, 0, 0, 0]
max_per_arc = 0
UNKNOWN = None
cache = []


def search(arcs_left: int, current_arc: int) -> int:
    if arcs_left == 0:
        if current_arc != 0:
            return 0
        if (
            num_visited[0] != num_visited[1]
            or num_visited[2] != num_visited[3]
            or num_visited[0] != num_visited[2]
        ):
            return 0
        return 1

    id_factor = max_per_arc + 1
    key = current_arc
    for v in num_visited:
        key = key * id_factor + v

    if cache[key] is not UNKNOWN:
        return cache[key]

    result = 0

    turn_left = (current_arc + 1) % 5
    if num_visited[turn_left] < max_per_arc:
        num_visited[turn_left] += 1
        result += search(arcs_left - 1, turn_left)
        num_visited[turn_left] -= 1

    turn_right = (current_arc + 4) % 5
    if num_visited[turn_right] < max_per_arc:
        num_visited[turn_right] += 1
        result += search(arcs_left - 1, turn_right)
        num_visited[turn_right] -= 1

    cache[key] = result
    return result


def solve(num_arcs: int) -> int:
    global max_per_arc, cache
    max_per_arc = num_arcs // 5
    size = 5 * (max_per_arc + 1) ** 5
    cache = [UNKNOWN] * size

    return search(num_arcs, 0)


if __name__ == "__main__":
    assert solve(25) == 70932
    print(solve(70))
