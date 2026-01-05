#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0321.cpp"""


def count_moves(stones_per_color):
    red = "R"
    blue = "B"
    empty = "."

    length = 2 * stones_per_color + 1
    initial = red * stones_per_color + empty + blue * stones_per_color
    final = blue * stones_per_color + empty + red * stones_per_color

    last = [initial]
    seen = {initial}
    num_moves = 0
    while True:
        next_states = []
        for current in last:
            if current == final:
                return num_moves

            pos = current.index(empty)

            if pos >= 2:
                jump_two_right = list(current)
                jump_two_right[pos - 2], jump_two_right[pos] = (
                    jump_two_right[pos],
                    jump_two_right[pos - 2],
                )
                jump_two_right = "".join(jump_two_right)
                if jump_two_right not in seen:
                    next_states.append(jump_two_right)
                    seen.add(jump_two_right)
            if pos >= 1:
                move_one_right = list(current)
                move_one_right[pos - 1], move_one_right[pos] = (
                    move_one_right[pos],
                    move_one_right[pos - 1],
                )
                move_one_right = "".join(move_one_right)
                if move_one_right not in seen:
                    next_states.append(move_one_right)
                    seen.add(move_one_right)
            if pos < length - 1:
                move_one_left = list(current)
                move_one_left[pos + 1], move_one_left[pos] = (
                    move_one_left[pos],
                    move_one_left[pos + 1],
                )
                move_one_left = "".join(move_one_left)
                if move_one_left not in seen:
                    next_states.append(move_one_left)
                    seen.add(move_one_left)
            if pos < length - 2:
                jump_two_left = list(current)
                jump_two_left[pos + 2], jump_two_left[pos] = (
                    jump_two_left[pos],
                    jump_two_left[pos + 2],
                )
                jump_two_left = "".join(jump_two_left)
                if jump_two_left not in seen:
                    next_states.append(jump_two_left)
                    seen.add(jump_two_left)

        num_moves += 1
        last = next_states


def solve(num_values=40):
    if num_values <= 0:
        return 0

    x1, y1 = 2, 1
    x2, y2 = 5, 3
    total = y1 + y2

    n = 3
    while n <= num_values:
        p, q, k = 3, 4, 5
        r, s, l = 2, 3, 3

        next_x1 = p * x1 + q * y1 + k
        next_y1 = r * x1 + s * y1 + l
        x1, y1 = next_x1, next_y1
        total += y1

        n += 1
        if n > num_values:
            break

        next_x2 = p * x2 + q * y2 + k
        next_y2 = r * x2 + s * y2 + l
        x2, y2 = next_x2, next_y2
        total += y2

        n += 1

    return total


def main():
    assert solve(5) == 99
    print(solve())


if __name__ == "__main__":
    main()
