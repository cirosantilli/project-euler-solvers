#!/usr/bin/env python
'''Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0308.cpp'''

def enumerate_primes(num_primes, display_steps=True):
    num_fractions = 14
    num_exponents = 10
    fractions = [
        [0, 0, 0, -1, 0, -1, 1, 0, 0, 0],
        [1, 1, -1, 0, 0, 1, -1, 0, 0, 0],
        [0, -1, 0, 0, 0, 0, -1, 1, 0, 0],
        [-1, 0, 0, 0, 0, 0, 0, -1, 1, 0],
        [0, -1, 0, 0, -1, 0, 0, 0, 0, 1],
        [0, 0, 0, 1, 1, 0, 0, 0, 0, -1],
        [0, 0, 1, 0, 0, 0, 0, 1, -1, 0],
        [0, 0, 0, 1, 1, 0, 0, -1, 0, 0],
        [0, 0, 0, 0, 0, 0, -1, 0, 0, 0],
        [0, 0, 0, 0, 1, -1, 0, 0, 0, 0],
        [0, 0, 0, 0, -1, 1, 0, 0, 0, 0],
        [-1, 1, 1, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, -1, 0, 0, 0, 0, 0, 0],
        [0, 0, 1, 0, 1, 0, 0, 0, 0, 0],
    ]

    current = [1, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    steps = 0
    num_found = 0

    while num_found < num_primes:
        if display_steps:
            parts = []
            for x in current:
                parts.append("-" if x == 0 else str(x))
            print(f"step {steps:3d}: " + " ".join(f"{p:>2}" for p in parts))

        for fraction in fractions:
            matching = True
            for exponent in range(num_exponents):
                if current[exponent] + fraction[exponent] < 0:
                    matching = False
                    break
            if matching:
                for exponent in range(num_exponents):
                    current[exponent] += fraction[exponent]
                break

        steps += 1

        is_prime = True
        for exponent in range(1, num_exponents):
            if current[exponent] != 0:
                is_prime = False
                break
        if is_prime:
            num_found += 1
            if display_steps:
                print(f"prime {current[0]} @ step {steps}")

    return steps


def search(num_primes):
    state_s = "S_"
    state = state_s

    two = 1
    three = 0
    five = 0
    seven = 0

    steps = 0
    iterations = 0
    num_found = 0

    while True:
        iterations += 1

        if state == "S_":
            if three == 0 and five == 0 and seven == 0 and steps > 0:
                num_found += 1
                if num_found == num_primes:
                    return steps

            if two > 0:
                two -= 1
                three += 1
                five += 1
            elif seven > 0:
                seven -= 1
            else:
                five += 1
                state = "S11"

        elif state == "S11":
            if three > 0:
                steps += 2 * three
                seven += three
                three = 0
                continue
            state = "S13"

        elif state == "S13":
            if seven > 0:
                if five > 0:
                    smallest = min(five, seven)
                    steps += 2 * smallest
                    two += smallest
                    three += smallest
                    five -= smallest
                    seven -= smallest
                    continue
                seven -= 1
                state = "S17"
            else:
                state = "S11"

        elif state == "S17":
            if five > 0:
                five -= 1
                two += 1
                three += 1
                state = "S13"
            elif three > 0:
                three -= 1
                state = "S19"
            else:
                state = state_s

        elif state == "S19":
            if two > 0:
                steps += 2 * two
                five += two
                two = 0
                continue
            seven += 1
            state = "S11"

        elif state == "S23":
            five += 1
            state = "S19"

        elif state == "S29":
            seven += 1
            state = "S11"

        steps += 1


def solve(num_primes: int) -> int:
    return search(num_primes)


def main():
    print(solve(10001))


if __name__ == "__main__":
    main()
