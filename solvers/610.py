#!/usr/bin/env python
'''Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0610.cpp'''
import math

NUM_LETTERS = 7
LETTERS = ["M", "D", "C", "L", "X", "V", "I"]

TERMINAL = 0.02
ANY_LETTER = 0.14


def roman2number(roman):
    result = 0
    last = 0
    subtract = False

    for ch in reversed(roman):
        if ch == "M":
            current = 1000
        elif ch == "D":
            current = 500
        elif ch == "C":
            current = 100
        elif ch == "L":
            current = 50
        elif ch == "X":
            current = 10
        elif ch == "V":
            current = 5
        else:
            current = 1

        if current < last:
            subtract = True
            last = current
        elif current > last:
            subtract = False
            last = current

        if subtract:
            result -= current
        else:
            result += current

    return result


def number2roman(number):
    rules = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
    action = ["M", "CM", "D", "CD", "C", "XC", "L", "XL", "X", "IX", "V", "IV", "I"]

    result = []
    for value, symbol in zip(rules, action):
        while number >= value:
            number -= value
            result.append(symbol)
    return "".join(result)


def myrand():
    if not hasattr(myrand, "seed"):
        myrand.seed = 0
    myrand.seed = (6364136223846793005 * myrand.seed + 1) & 0xFFFFFFFFFFFFFFFF
    return myrand.seed >> 30


next_states = [[] for _ in range(1000)]


def monte_carlo(iterations):
    total = 0.0
    for _ in range(iterations):
        current = ""
        while True:
            choice = myrand() % 1000
            if choice < TERMINAL * 1000:
                total += roman2number(current)
                break

            current += LETTERS[choice % NUM_LETTERS]
            number = roman2number(current)
            verify = number2roman(number)
            if current != verify:
                current = current[:-1]

    return total / iterations


def search(current):
    if not next_states[current]:
        return current

    result = TERMINAL * current
    percentages = TERMINAL
    for x in next_states[current]:
        result += ANY_LETTER * search(x)
        percentages += ANY_LETTER

    result /= percentages
    return result


def solve():
    n2r = [""] * 1000
    r2n = {}

    for i in range(1000):
        roman = number2roman(i)
        n2r[i] = roman
        r2n[roman] = i

    for i in range(1000):
        current = n2r[i] + " "
        for add in LETTERS:
            current = current[:-1] + add
            if current in r2n:
                next_states[i].append(r2n[current])

    up_to_1000 = 0.0
    up_to_1000 += ANY_LETTER * search(1)
    up_to_1000 += ANY_LETTER * search(5)
    up_to_1000 += ANY_LETTER * search(10)
    up_to_1000 += ANY_LETTER * search(50)
    up_to_1000 += ANY_LETTER * search(100)
    up_to_1000 += ANY_LETTER * search(500)

    precision = 0.000000001
    num_m = 1

    result = up_to_1000
    while True:
        many_m = num_m * 1000 * (1 - ANY_LETTER)
        increment = many_m + up_to_1000
        result += increment * (ANY_LETTER ** num_m)

        if increment < precision:
            break
        num_m += 1

    return result


def main():
    print(f"{solve():.8f}")


if __name__ == "__main__":
    main()
