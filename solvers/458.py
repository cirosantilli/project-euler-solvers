#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0458.cpp"""
WORD_SIZE = 7
MODULO = 1000000000


class Matrix:
    def __init__(self, size):
        self.size = size
        self.data = [[0 for _ in range(size)] for _ in range(size)]

    def get(self, column, row):
        return self.data[row][column]

    def set(self, column, row, value):
        self.data[row][column] = value

    def multiply(self, other, modulo):
        result = Matrix(self.size)
        for i in range(self.size):
            for j in range(self.size):
                value = other.get(i, j)
                if value == 0:
                    continue
                for k in range(self.size):
                    result.data[k][i] += self.get(j, k) * value
        for i in range(self.size):
            for k in range(self.size):
                result.data[k][i] %= modulo
        return result

    def powmod(self, exponent, modulo):
        result = Matrix(self.size)
        for i in range(self.size):
            result.set(i, i, 1)

        base = self
        while exponent > 0:
            if exponent & 1:
                result = result.multiply(base, modulo)
            base = base.multiply(base, modulo)
            exponent >>= 1
        return result


def fast(num_letters):
    mat = Matrix(8)
    mat.set(0, 0, 0)
    mat.set(1, 0, 0)
    mat.set(2, 0, 0)
    mat.set(3, 0, 0)
    mat.set(4, 0, 0)
    mat.set(5, 0, 0)
    mat.set(6, 0, 0)
    mat.set(7, 0, 0)
    mat.set(0, 1, 7)
    mat.set(1, 1, 1)
    mat.set(2, 1, 1)
    mat.set(3, 1, 1)
    mat.set(4, 1, 1)
    mat.set(5, 1, 1)
    mat.set(6, 1, 1)
    mat.set(7, 1, 0)
    mat.set(0, 2, 0)
    mat.set(1, 2, 6)
    mat.set(2, 2, 1)
    mat.set(3, 2, 1)
    mat.set(4, 2, 1)
    mat.set(5, 2, 1)
    mat.set(6, 2, 1)
    mat.set(7, 2, 0)
    mat.set(0, 3, 0)
    mat.set(1, 3, 0)
    mat.set(2, 3, 5)
    mat.set(3, 3, 1)
    mat.set(4, 3, 1)
    mat.set(5, 3, 1)
    mat.set(6, 3, 1)
    mat.set(7, 3, 0)
    mat.set(0, 4, 0)
    mat.set(1, 4, 0)
    mat.set(2, 4, 0)
    mat.set(3, 4, 4)
    mat.set(4, 4, 1)
    mat.set(5, 4, 1)
    mat.set(6, 4, 1)
    mat.set(7, 4, 0)
    mat.set(0, 5, 0)
    mat.set(1, 5, 0)
    mat.set(2, 5, 0)
    mat.set(3, 5, 0)
    mat.set(4, 5, 3)
    mat.set(5, 5, 1)
    mat.set(6, 5, 1)
    mat.set(7, 5, 0)
    mat.set(0, 6, 0)
    mat.set(1, 6, 0)
    mat.set(2, 6, 0)
    mat.set(3, 6, 0)
    mat.set(4, 6, 0)
    mat.set(5, 6, 2)
    mat.set(6, 6, 1)
    mat.set(7, 6, 0)
    mat.set(0, 7, 0)
    mat.set(1, 7, 0)
    mat.set(2, 7, 0)
    mat.set(3, 7, 0)
    mat.set(4, 7, 0)
    mat.set(5, 7, 0)
    mat.set(6, 7, 1)
    mat.set(7, 7, 7)

    super_matrix = mat.powmod(num_letters, MODULO)

    with_project = super_matrix.get(0, 7)
    all_strings = super_matrix.get(7, 7)
    if all_strings < with_project:
        all_strings += MODULO
    return all_strings - with_project


def main():
    assert fast(7) == 818503
    print(fast(1000000000000))


if __name__ == "__main__":
    main()
