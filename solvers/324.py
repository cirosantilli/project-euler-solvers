#!/usr/bin/env python
'''Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0324.cpp'''
MODULO = 100000007

UP = 'U'
DOWN = 'D'
HORIZONTAL = '-'
VERTICAL = '|'
EMPTY = ' '

NUM_BORDERS = 1 << 9

layers = set()
borders = [[0 for _ in range(NUM_BORDERS)] for _ in range(NUM_BORDERS)]


def create_layers(current):
    pos = None
    for i, value in enumerate(current):
        if value == EMPTY:
            pos = i
            break
    if pos is None:
        layers.add(tuple(current))
        return

    layer_up = current[:]
    layer_up[pos] = UP
    create_layers(layer_up)

    layer_down = current[:]
    layer_down[pos] = DOWN
    create_layers(layer_down)

    if pos % 3 != 2 and current[pos + 1] == EMPTY:
        layer_h = current[:]
        layer_h[pos] = HORIZONTAL
        layer_h[pos + 1] = HORIZONTAL
        create_layers(layer_h)

    if pos < 6 and current[pos + 3] == EMPTY:
        layer_v = current[:]
        layer_v[pos] = VERTICAL
        layer_v[pos + 3] = VERTICAL
        create_layers(layer_v)


def add_borders(layer):
    top = 0
    bottom = 0
    for i, value in enumerate(layer):
        if value == UP:
            top |= 1 << i
        if value == DOWN:
            bottom |= 1 << i
    borders[bottom][top] += 1


def brute_force(mask_bottom, mask_top, height, cache):
    if height == 0:
        return 0
    if height == 1:
        return borders[mask_bottom][mask_top]

    key = (mask_bottom, mask_top, height)
    if key in cache:
        return cache[key]

    power_of_two = 1
    while power_of_two * 2 < height:
        power_of_two *= 2

    height_top = power_of_two
    height_bottom = height - height_top

    result = 0
    for middle in range(NUM_BORDERS):
        result += brute_force(mask_bottom, middle, height_bottom, cache) * brute_force(
            middle, mask_top, height_top, cache
        )
        result %= MODULO

    cache[key] = result
    return result


class Matrix:
    def __init__(self, size=1):
        self.size_ = size
        self.data = [[0 for _ in range(size)] for _ in range(size)]

    def size(self):
        return self.size_

    def get(self, column, row):
        return self.data[column][row]

    def set(self, column, row, value):
        self.data[column][row] = value

    def multiply_symmetric(self, other, modulo):
        size = self.size_
        result = Matrix(size)
        for i in range(size):
            for j in range(size):
                if other.get(i, j) == 0:
                    continue
                for k in range(i, size):
                    result.data[i][k] += self.data[j][k] * other.data[i][j]

        for i in range(size):
            result.data[i][i] %= modulo
            for j in range(i + 1, size):
                value = result.data[i][j] % modulo
                result.data[i][j] = value
                result.data[j][i] = value

        return result

    def powmod(self, exponent, modulo):
        if exponent == 1:
            return self

        size = self.size_
        result = Matrix(size)
        for i in range(size):
            result.data[i][i] = 1
        is_identity = True

        base = self
        while exponent > 0:
            if exponent & 1:
                if is_identity:
                    result = base
                    is_identity = False
                else:
                    result = result.multiply_symmetric(base, modulo)

            if exponent > 1:
                base = base.multiply_symmetric(base, modulo)

            exponent >>= 1

        return result


def remove_unreachable(matrix):
    reachable = set()
    todo = {0}
    while todo:
        current = todo.pop()
        reachable.add(current)
        for i in range(matrix.size()):
            if matrix.get(current, i) > 0 and i not in reachable:
                todo.add(i)

    matrix_size = len(reachable)
    if matrix_size == matrix.size():
        return matrix

    smaller = Matrix(matrix_size)
    x = 0
    for i in range(NUM_BORDERS):
        if i not in reachable:
            continue
        y = 0
        for j in range(NUM_BORDERS):
            if j not in reachable:
                continue
            smaller.data[x][y] = matrix.get(i, j)
            y += 1
        x += 1

    return smaller


def build_base_matrix():
    global layers, borders
    layers = set()
    borders = [[0 for _ in range(NUM_BORDERS)] for _ in range(NUM_BORDERS)]

    empty_layer = [EMPTY] * 9
    create_layers(empty_layer)

    for layer in layers:
        add_borders(layer)

    matrix = Matrix(NUM_BORDERS)
    for i in range(NUM_BORDERS):
        for j in range(NUM_BORDERS):
            matrix.data[i][j] = borders[i][j]

    return remove_unreachable(matrix)


def solve(n):
    matrix = build_base_matrix()
    matrix = matrix.powmod(n, MODULO)
    return matrix.get(0, 0)


def solve_power10(power):
    matrix = build_base_matrix()
    matrix = matrix.powmod(10, MODULO)
    matrix = remove_unreachable(matrix)

    remaining = power - 1
    at_once = 19
    while remaining > 0:
        power10 = 1
        i = 1
        while i < at_once and remaining > 0:
            power10 *= 10
            remaining -= 1
            i += 1

        matrix = matrix.powmod(power10, MODULO)

    return matrix.get(0, 0)


def main():
    assert solve(2) == 229
    assert solve(4) == 117805
    assert solve(10) % MODULO == 96149360
    assert solve_power10(3) == 24806056
    assert solve_power10(6) == 30808124
    print(solve_power10(10000))


if __name__ == "__main__":
    main()
