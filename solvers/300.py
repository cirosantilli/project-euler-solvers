#!/usr/bin/env python
'''Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0300.cpp'''
GRID_SIZE = 30
CENTER = GRID_SIZE // 2
EMPTY = -1

best = []
direct = []
visited = set()


def optimize(length, grid):
    contacts = []
    seen = 0

    ignore_straight = 9 if length == 15 else 0

    for i in range(ignore_straight, GRID_SIZE - ignore_straight - 1):
        for j in range(ignore_straight, GRID_SIZE - ignore_straight - 1):
            if seen + 1 >= length:
                break

            if grid[i][j] == EMPTY:
                continue

            seen += 1
            from_idx = grid[i][j]

            if grid[i + 1][j] != EMPTY:
                to_idx = grid[i + 1][j]
                if from_idx != to_idx + 1 and from_idx + 1 != to_idx:
                    contacts.append((1 << from_idx) | (1 << to_idx))
            if grid[i][j + 1] != EMPTY:
                to_idx = grid[i][j + 1]
                if from_idx != to_idx + 1 and from_idx + 1 != to_idx:
                    contacts.append((1 << from_idx) | (1 << to_idx))

    if not contacts:
        return

    contacts_key = tuple(contacts)
    if contacts_key in visited:
        return
    visited.add(contacts_key)

    num_proteins = 1 << length
    for protein in range(num_proteins):
        found = direct[protein]
        if found + len(contacts) <= best[protein]:
            continue
        for contact_mask in contacts:
            if (protein & contact_mask) == 0:
                found += 1
        if best[protein] < found:
            best[protein] = found


def search(current, length, grid, x, y):
    if current == length:
        if y >= CENTER:
            optimize(length, grid)
        return

    if grid[x - 1][y] == EMPTY:
        grid[x - 1][y] = current
        search(current + 1, length, grid, x - 1, y)
        grid[x - 1][y] = EMPTY

    if grid[x + 1][y] == EMPTY:
        grid[x + 1][y] = current
        search(current + 1, length, grid, x + 1, y)
        grid[x + 1][y] = EMPTY

    if grid[x][y - 1] == EMPTY:
        grid[x][y - 1] = current
        search(current + 1, length, grid, x, y - 1)
        grid[x][y - 1] = EMPTY

    if grid[x][y + 1] == EMPTY:
        grid[x][y + 1] = current
        search(current + 1, length, grid, x, y + 1)
        grid[x][y + 1] = EMPTY


def solve(length: int) -> float:
    global best, direct, visited
    visited = set()
    num_proteins = 1 << length
    direct = [0] * num_proteins
    best = [0] * num_proteins

    for protein in range(num_proteins):
        count = 0
        for i in range(length - 1):
            if (protein & (3 << i)) == 0:
                count += 1
        direct[protein] = count
        best[protein] = count

    grid = [[EMPTY for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    x = CENTER
    y = CENTER
    grid[x][y] = 0
    x += 1
    grid[x][y] = 1

    search(2, length, grid, x, y)

    total = sum(best)
    return total / len(best)


if __name__ == "__main__":
    print(f"{solve(15):.14f}")
