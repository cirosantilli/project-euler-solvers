#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0349.cpp"""


def solve(limit=1000000000000000000):
    white = False
    black = True

    size = 128
    grid = [white] * (size * size)

    x = size // 2
    y = size // 2

    delta_x = [0, 1, 0, -1]
    delta_y = [1, 0, -1, 0]
    direction = 0

    cycle = 104
    remainder = limit % cycle

    count = 0
    last = count
    last_deltas = [0]
    stop_if_same = 10

    steps = 0
    while steps < limit:
        if steps % cycle == remainder:
            diff = count - last
            last_deltas.append(diff)
            last = count

            if len(last_deltas) >= stop_if_same:
                samesame = True
                for scan in last_deltas[-stop_if_same:]:
                    if scan != diff:
                        samesame = False
                        break

                if samesame:
                    remaining_cycles = (limit - steps) // cycle
                    count += remaining_cycles * diff
                    break

        pos = y * size + x
        if grid[pos] == white:
            grid[pos] = black
            count += 1
            direction = (direction + 1) % 4
        else:
            grid[pos] = white
            count -= 1
            direction = (direction + 3) % 4

        x += delta_x[direction]
        y += delta_y[direction]
        steps += 1

    return count


def main():
    print(solve())


if __name__ == "__main__":
    main()
