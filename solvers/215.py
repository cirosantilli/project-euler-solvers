#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0215.cpp"""


def generate_rows(row, max_width, all_rows):
    width = row[-1] if row else 0
    if width + 2 == max_width or width + 3 == max_width:
        all_rows.append(row[:])
        return
    if width + 1 == max_width:
        return

    row.append(width + 2)
    generate_rows(row, max_width, all_rows)

    row[-1] += 1
    generate_rows(row, max_width, all_rows)

    row.pop()


def check_compatibility(all_rows):
    compatible = [[] for _ in range(len(all_rows))]
    for i in range(len(all_rows)):
        for j in range(i + 1, len(all_rows)):
            valid = True
            it1 = 0
            it2 = 0
            row1 = all_rows[i]
            row2 = all_rows[j]
            while it1 < len(row1) and it2 < len(row2):
                if row1[it1] < row2[it2]:
                    it1 += 1
                elif row2[it2] < row1[it1]:
                    it2 += 1
                else:
                    valid = False
                    break
            if valid:
                compatible[i].append(j)
                compatible[j].append(i)
    return compatible


def count(row_id, rows_left, compatible, cache):
    if rows_left == 1:
        return 1
    if cache[row_id][rows_left] is not None:
        return cache[row_id][rows_left]

    result = 0
    for nxt in compatible[row_id]:
        result += count(nxt, rows_left - 1, compatible, cache)

    cache[row_id][rows_left] = result
    return result


def solve(width: int, height: int) -> int:
    all_rows = []
    generate_rows([], width, all_rows)

    compatible = check_compatibility(all_rows)

    cache = [[None] * (height + 1) for _ in range(len(all_rows))]

    result = 0
    for i in range(len(all_rows)):
        result += count(i, height, compatible, cache)
    return result


if __name__ == "__main__":
    assert solve(9, 3) == 8
    print(solve(32, 10))
