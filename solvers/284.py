#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0284.cpp"""


class BigNum:
    MaxDigit = 14

    def __init__(self, value=0):
        if isinstance(value, list):
            self.digits = list(value)
            if not self.digits:
                self.digits = [0]
            return

        x = int(value)
        if x == 0:
            self.digits = [0]
        else:
            digits = []
            while x > 0:
                digits.append(x % self.MaxDigit)
                x //= self.MaxDigit
            self.digits = digits

    def copy(self):
        return BigNum(self.digits[:])

    def __len__(self):
        return len(self.digits)

    def __getitem__(self, idx):
        return self.digits[idx]

    def resize(self, size, fill=0):
        if size < len(self.digits):
            del self.digits[size:]
        else:
            self.digits.extend([fill] * (size - len(self.digits)))

    def to_string(self):
        digits_map = "0123456789abcd"
        result = []
        for digit in reversed(self.digits):
            result.append(digits_map[digit])
        while len(result) > 1 and result[0] == "0":
            result.pop(0)
        return "".join(result)

    def __add__(self, other):
        if not isinstance(other, BigNum):
            other = BigNum(other)
        result = self.digits[:]
        if len(result) < len(other.digits):
            result.extend([0] * (len(other.digits) - len(result)))

        carry = 0
        for i in range(len(result)):
            carry += result[i]
            if i < len(other.digits):
                carry += other.digits[i]
            else:
                if carry == 0:
                    return BigNum(result)

            if carry < self.MaxDigit:
                result[i] = carry
                carry = 0
            else:
                result[i] = carry - self.MaxDigit
                carry = 1

        if carry > 0:
            result.append(carry)

        return BigNum(result)

    def multiply_int(self, factor):
        factor = int(factor)
        if factor == 0:
            return BigNum(0)
        if factor == 1:
            return self.copy()
        if factor == self.MaxDigit:
            if len(self.digits) == 1 and self.digits[0] == 0:
                return BigNum(0)
            result = self.digits[:]
            result.insert(0, 0)
            return BigNum(result)

        carry = 0
        result = self.digits[:]
        for i in range(len(result)):
            carry += result[i] * factor
            result[i] = carry % self.MaxDigit
            carry //= self.MaxDigit

        while carry > 0:
            result.append(carry % self.MaxDigit)
            carry //= self.MaxDigit

        return BigNum(result)

    def __mul__(self, other):
        if isinstance(other, BigNum):
            if len(self.digits) < len(other.digits):
                return other * self

            result = BigNum(0)
            for i in range(len(other.digits) - 1, -1, -1):
                result = result.multiply_int(self.MaxDigit) + self.multiply_int(
                    other.digits[i]
                )
            return result

        return self.multiply_int(other)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __sub__(self, other):
        if not isinstance(other, BigNum):
            other = BigNum(other)
        result = self.digits[:]
        borrow = 0
        for i in range(len(result)):
            diff = result[i] - borrow
            if i < len(other.digits):
                diff -= other.digits[i]
            else:
                if borrow == 0:
                    break

            if diff < 0:
                borrow = 1
                diff += self.MaxDigit
            else:
                borrow = 0

            result[i] = diff

        while len(result) > 1 and result[-1] == 0:
            result.pop()

        return BigNum(result)

    def multiply_low(self, other, num_digits):
        result = [0] * num_digits
        for i in range(min(len(other.digits), num_digits)):
            carry = 0
            for j in range(num_digits - i):
                if j >= len(self.digits):
                    carry += result[i + j]
                else:
                    carry += result[i + j] + other.digits[i] * self.digits[j]

                result[i + j] = carry % self.MaxDigit
                carry //= self.MaxDigit

        self.digits = result

    def is_steady(self):
        square = BigNum(0)
        for pos in range(len(self.digits)):
            digit = self.digits[pos]
            if digit > 0:
                product = self.multiply_int(digit)
                product.digits = [0] * pos + product.digits
                square = square + product

            if pos >= len(square.digits) or digit != square.digits[pos]:
                return False

        return True


def brute_force(number):
    next_number = number.copy()
    next_number.digits.append(0)

    for digit in range(BigNum.MaxDigit):
        next_number.digits[-1] = digit
        if next_number.is_steady():
            break
    return next_number


def fast_doubling(number, num_digits):
    if not isinstance(number, BigNum):
        number = BigNum(number)

    current = number.copy()
    while len(current) < num_digits:
        twice_digits = 2 * len(current)

        square = current * current
        cube = square * current
        diff = cube * 2 - square * 3
        diff.resize(twice_digits)

        large_one = BigNum(0)
        large_one.resize(twice_digits, 0)
        large_one.digits.append(1)

        current = large_one - diff

    current.resize(num_digits)
    return current


def find_other(number):
    one0one = BigNum(1)
    one0one.resize(len(number.digits), 0)
    one0one.digits.append(1)
    return one0one - number


def solve(max_digits: int) -> str:
    seven = BigNum(7)
    eight = BigNum(8)

    seven = fast_doubling(7, max_digits)
    eight = find_other(seven)

    total = 1
    for i in range(max_digits):
        how_often = max_digits - i
        total += how_often * seven[i]
        total += how_often * eight[i]

        if seven[i] == 0:
            for j in range(i):
                total -= seven[j]

        if eight[i] == 0:
            for j in range(i):
                total -= eight[j]

    sum_base_14 = BigNum(total)
    return sum_base_14.to_string()


if __name__ == "__main__":
    assert solve(9) == "2d8"
    print(solve(10000))
