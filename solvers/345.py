#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0345.cpp"""
SIZE = 15
MATRIX = [
    [7, 53, 183, 439, 863, 497, 383, 563, 79, 973, 287, 63, 343, 169, 583],
    [627, 343, 773, 959, 943, 767, 473, 103, 699, 303, 957, 703, 583, 639, 913],
    [447, 283, 463, 29, 23, 487, 463, 993, 119, 883, 327, 493, 423, 159, 743],
    [217, 623, 3, 399, 853, 407, 103, 983, 89, 463, 290, 516, 212, 462, 350],
    [960, 376, 682, 962, 300, 780, 486, 502, 912, 800, 250, 346, 172, 812, 350],
    [870, 456, 192, 162, 593, 473, 915, 45, 989, 873, 823, 965, 425, 329, 803],
    [973, 965, 905, 919, 133, 673, 665, 235, 509, 613, 673, 815, 165, 992, 326],
    [322, 148, 972, 962, 286, 255, 941, 541, 265, 323, 925, 281, 601, 95, 973],
    [445, 721, 11, 525, 473, 65, 511, 164, 138, 672, 18, 428, 154, 448, 848],
    [414, 456, 310, 312, 798, 104, 566, 520, 302, 248, 694, 976, 430, 392, 198],
    [184, 829, 373, 181, 631, 101, 969, 613, 840, 740, 778, 458, 284, 760, 390],
    [821, 461, 843, 513, 17, 901, 711, 993, 293, 157, 274, 94, 192, 156, 574],
    [34, 124, 4, 878, 450, 476, 712, 914, 838, 669, 875, 299, 823, 329, 699],
    [815, 559, 813, 459, 522, 788, 168, 586, 966, 232, 308, 833, 251, 631, 107],
    [813, 883, 451, 509, 615, 77, 281, 613, 459, 205, 380, 274, 302, 35, 805],
]

max_remaining = [0] * SIZE


def search(row=0, column_mask=0, total=0, at_least=0):
    if row == SIZE:
        return total

    if total + max_remaining[row] <= at_least:
        return 0

    for column in range(SIZE):
        mask = 1 << column
        if column_mask & mask:
            continue
        current = search(
            row + 1, column_mask | mask, total + MATRIX[row][column], at_least
        )
        if at_least < current:
            at_least = current

    return at_least


def max_sum_small(matrix):
    size = len(matrix)
    dp = {0: 0}
    for row in range(size):
        next_dp = {}
        for mask, value in dp.items():
            for col in range(size):
                if mask & (1 << col):
                    continue
                next_mask = mask | (1 << col)
                next_dp[next_mask] = max(
                    next_dp.get(next_mask, 0), value + matrix[row][col]
                )
        dp = next_dp
    return max(dp.values()) if dp else 0


def solve():
    max_value_per_row = [0] * SIZE
    for row in range(SIZE):
        max_value_per_row[row] = MATRIX[0][row]
        for column in range(1, SIZE):
            if max_value_per_row[row] < MATRIX[column][row]:
                max_value_per_row[row] = MATRIX[column][row]

    max_remaining[SIZE - 1] = max_value_per_row[SIZE - 1]
    for row in range(SIZE - 1, 0, -1):
        max_remaining[row - 1] = max_remaining[row] + max_value_per_row[row - 1]

    return search()


def main():
    example_matrix = [
        [7, 53, 183, 439, 863],
        [497, 383, 563, 79, 973],
        [287, 63, 343, 169, 583],
        [627, 343, 773, 959, 943],
        [767, 473, 103, 699, 303],
    ]
    assert max_sum_small(example_matrix) == 3315
    print(solve())


if __name__ == "__main__":
    main()
