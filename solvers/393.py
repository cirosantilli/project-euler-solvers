#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0393.cpp"""
MAX_SIZE = 10
size = 10

NO_ANT = 0

MOVE_UP = 0
MOVE_RIGHT = 1
MOVE_DOWN = 2
MOVE_LEFT = 3

BITS_PER_MOVE = 2
NUMBER_OF_MOVES = 4
MOVE_MASK = 3

cache = {}


def get_move(bits, pos):
    mypos = size - (pos + 1)
    return (bits >> (BITS_PER_MOVE * mypos)) & MOVE_MASK


def search(row=0, down=NO_ANT, up=NO_ANT):
    if row == size:
        symmetries = 2
        return symmetries if down == 0 and up == 0 else 0

    state = (row, down, up)
    if state in cache:
        return cache[state]

    result = 0
    combinations = 1 << (BITS_PER_MOVE * size)
    i = 0
    while i < combinations:
        first_move = get_move(i, 0)
        if first_move == MOVE_LEFT:
            skip_squares = size - 1
            skip_ids = 1 << (BITS_PER_MOVE * skip_squares)
            i += skip_ids
            continue

        last_move = get_move(i, size - 1)
        if last_move == MOVE_RIGHT:
            i += 1
            continue

        if row == 0 and first_move != MOVE_RIGHT:
            i += 1
            continue

        previous = MOVE_RIGHT
        invalid = False
        failed_at = 0
        for pos in range(size):
            current = get_move(i, pos)
            bit = 1 << pos

            if current == MOVE_UP and (down & bit):
                invalid = True
            if current == MOVE_UP and not (up & bit):
                invalid = True
            if current != MOVE_UP and (up & bit):
                invalid = True

            if current == MOVE_LEFT and previous == MOVE_RIGHT:
                invalid = True

            if current == MOVE_DOWN and row + 1 == size:
                invalid = True

            if invalid:
                failed_at = pos
                break

            previous = current

        if invalid:
            if failed_at != size - 1:
                skip_squares = size - (failed_at + 1)
                skip_ids = 1 << (BITS_PER_MOVE * skip_squares)
                i += skip_ids
                continue
            i += 1
            continue

        movement = [0] * MAX_SIZE
        for pos in range(size):
            bit = 1 << pos
            if down & bit:
                movement[pos] += 1

            movement[pos] -= 1

            current = get_move(i, pos)
            if current == MOVE_LEFT:
                movement[pos - 1] += 1
            elif current == MOVE_RIGHT:
                movement[pos + 1] += 1

        next_down = NO_ANT
        next_up = NO_ANT
        for pos in range(size):
            bit = 1 << pos
            current = get_move(i, pos)

            if current == MOVE_DOWN:
                next_down |= bit
                invalid = invalid or (row + 1 == size)

            if movement[pos] > 0 or movement[pos] < -1:
                invalid = True

            if movement[pos] == -1:
                next_up |= bit
                if current == MOVE_DOWN:
                    invalid = True

        if not invalid:
            result += search(row + 1, next_down, next_up)

        i += 1

    cache[state] = result
    return result


def solve(target_size=10):
    global size, cache
    size = target_size
    cache = {}
    return search()


def main():
    assert solve(4) == 88
    print(solve())


if __name__ == "__main__":
    main()
