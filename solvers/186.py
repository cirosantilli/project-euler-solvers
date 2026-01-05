#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0186.cpp"""


def generate():
    history = generate.history
    if len(history) < 55:
        k = len(history) + 1
        current = (300007 * k * k * k - 200003 * k + 100003) % 1000000
    else:
        current = (history[-55] + history[-24]) % 1000000
        if len(history) > 55 + 100:
            del history[:100]
    history.append(current)
    return current


def find(nodes, idx):
    current = idx
    while True:
        leader = nodes[current][0]
        if leader == current:
            if nodes[idx][0] != leader:
                nodes[idx][0] = leader
            return leader
        current = leader


def merge(nodes, x, y):
    root_x = find(nodes, x)
    root_y = find(nodes, y)
    if root_x == root_y:
        return
    if nodes[root_x][1] >= nodes[root_y][1]:
        nodes[root_x][1] += nodes[root_y][1]
        nodes[root_y][0] = root_x
    else:
        nodes[root_y][1] += nodes[root_x][1]
        nodes[root_x][0] = root_y


def solve(phone: int, percentage: int) -> int:
    nodes = [[i, 1] for i in range(1000000)]

    generate.history = []

    calls = 0
    target = 1000000 * percentage // 100
    while nodes[find(nodes, phone)][1] < target:
        from_id = generate()
        to_id = generate()
        if from_id == to_id:
            continue
        calls += 1
        merge(nodes, from_id, to_id)

    return calls


if __name__ == "__main__":
    print(solve(524287, 99))
