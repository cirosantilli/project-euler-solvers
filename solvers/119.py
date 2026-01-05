#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0119.cpp"""


class BigNum:
    def __init__(self, x: int = 0, base: int = 10) -> None:
        self.base = base
        self.digits = []
        if x == 0:
            self.digits = [0]
        else:
            while x > 0:
                self.digits.append(x % self.base)
                x //= self.base

    def __iadd__(self, other):
        if isinstance(other, BigNum):
            other_digits = other.digits
            if len(self.digits) < len(other_digits):
                self.digits.extend([0] * (len(other_digits) - len(self.digits)))

            carry = 0
            for i in range(len(self.digits)):
                carry += self.digits[i]
                if i < len(other_digits):
                    carry += other_digits[i]
                else:
                    if carry == 0:
                        return self

                if carry < self.base:
                    self.digits[i] = carry
                    carry = 0
                else:
                    self.digits[i] = carry - self.base
                    carry = 1

            if carry > 0:
                self.digits.append(carry)
            return self

        carry = int(other)
        i = 0
        while carry > 0:
            if i >= len(self.digits):
                self.digits.append(0)
            carry += self.digits[i]
            self.digits[i] = carry % self.base
            carry //= self.base
            i += 1
        return self

    def __imul__(self, factor: int):
        carry = 0
        for i in range(len(self.digits)):
            carry += self.digits[i] * factor
            self.digits[i] = carry % self.base
            carry //= self.base
        while carry > 0:
            self.digits.append(carry % self.base)
            carry //= self.base
        return self

    def __lt__(self, other: "BigNum") -> bool:
        if len(self.digits) < len(other.digits):
            return True
        if len(self.digits) > len(other.digits):
            return False
        for i in range(len(self.digits) - 1, -1, -1):
            if self.digits[i] < other.digits[i]:
                return True
            if self.digits[i] > other.digits[i]:
                return False
        return False

    def convert(self, new_radix: int) -> "BigNum":
        result = BigNum(0, new_radix)
        for digit in reversed(self.digits):
            result *= self.base
            result += digit
        return result


def digit_sum(x: BigNum) -> int:
    return sum(x.digits)


def generate_sequence(radix: int = 10) -> list[str]:
    googol = BigNum(1, 10)
    for _ in range(100):
        googol *= 10

    max_value = googol.convert(radix)

    solutions = set()
    upper_base = (radix - 1) * len(max_value.digits)
    for base in range(2, upper_base):
        current = BigNum(base, radix)
        while current < max_value:
            if digit_sum(current) == base and len(current.digits) >= 2:
                decimal = current.convert(10)
                solutions.add(tuple(decimal.digits))
            current *= base

    sorted_solutions = sorted(
        solutions,
        key=lambda digits: (len(digits), list(reversed(digits))),
    )

    output_parts: list[str] = []
    for digits in sorted_solutions:
        output_parts.append("".join(str(d) for d in reversed(digits)))
    return output_parts


def main() -> None:
    sequence = generate_sequence(10)
    assert sequence[1] == "512"
    assert sequence[9] == "614656"
    print(sequence[29])


if __name__ == "__main__":
    main()
