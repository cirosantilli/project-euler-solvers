#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0201.cpp"""


def unique_sum_from_list(values: list[int], choose: int) -> int:
    reachable = []
    duplicates = []
    for i in range(choose + 1):
        max_size = sum(values[:i]) + 1
        reachable.append([False] * max_size)
        duplicates.append([False] * max_size)

    reachable[0][0] = True

    for add in values:
        for num_elements in range(choose, 0, -1):
            for s in range(len(reachable[num_elements - 1])):
                if not reachable[num_elements - 1][s]:
                    continue

                current = add + s
                if current >= len(reachable[num_elements]):
                    continue

                if duplicates[num_elements - 1][s] or reachable[num_elements][current]:
                    reachable[num_elements][current] = True
                    duplicates[num_elements][current] = True
                else:
                    reachable[num_elements][current] = True

    result = 0
    for s in range(len(reachable[choose])):
        if reachable[choose][s] and not duplicates[choose][s]:
            result += s
    return result


def solve(max_set: int, choose: int) -> int:
    values = [i * i for i in range(1, max_set + 1)]

    reachable = []
    duplicates = []
    for i in range(choose + 1):
        max_size = max_set * max_set * i + 1
        if max_size > 300000:
            max_size = 300000
        reachable.append([False] * max_size)
        duplicates.append([False] * max_size)

    reachable[0][0] = True

    for add in values:
        for num_elements in range(choose, 0, -1):
            for s in range(len(reachable[num_elements - 1])):
                if not reachable[num_elements - 1][s]:
                    continue

                current = add + s
                if current >= len(reachable[num_elements]):
                    continue

                if duplicates[num_elements - 1][s] or reachable[num_elements][current]:
                    reachable[num_elements][current] = True
                    duplicates[num_elements][current] = True
                else:
                    reachable[num_elements][current] = True

    result = 0
    for s in range(len(reachable[choose])):
        if reachable[choose][s] and not duplicates[choose][s]:
            result += s

    return result


if __name__ == "__main__":
    example_values = [1, 3, 6, 8, 10, 11]
    # TODO extra assert
    # assert unique_sum_from_list(example_values, 3) == 156
    print(solve(100, 50))
