#!/usr/bin/env python
'''Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0154.cpp'''
def choose(sums: list[int], n: int, k: int) -> int:
    return sums[n] - (sums[n - k] + sums[k])


def solve(layer: int, prime1: int, exponent1: int, prime2: int, exponent2: int) -> int:
    mul_prime1 = [0]
    mul_prime2 = [0]
    for x in range(1, layer + 1):
        current = x
        count = 0
        while current % prime1 == 0:
            current //= prime1
            count += 1
        mul_prime1.append(count)

        current = x
        count = 0
        while current % prime2 == 0:
            current //= prime2
            count += 1
        mul_prime2.append(count)

    sum1 = []
    count = 0
    for x in mul_prime1:
        count += x
        sum1.append(count)

    sum2 = []
    count = 0
    for x in mul_prime2:
        count += x
        sum2.append(count)

    result = 0
    for i in range(layer + 1):
        found1 = choose(sum1, layer, i)
        found2 = choose(sum2, layer, i)

        if found1 >= exponent1 and found2 >= exponent2:
            result += i + 1
            continue

        for j in range((i + 1) // 2 + 1):
            if found1 + choose(sum1, i, j) >= exponent1 and found2 + choose(
                sum2, i, j
            ) >= exponent2:
                result += 1
                if j < i / 2:
                    result += 1

    return result


def main() -> None:
    print(solve(200000, 2, 12, 5, 12))


if __name__ == "__main__":
    main()
