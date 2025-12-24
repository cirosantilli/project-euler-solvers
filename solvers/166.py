#!/usr/bin/env python
'''Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0166.cpp'''
def solve(max_digit: int) -> int:
    even = (max_digit + 1) % 2 == 0
    max_a = (max_digit - 1) // 2 if even else max_digit

    result = 0
    for a in range(max_a + 1):
        for b in range(max_digit + 1):
            for c in range(max_digit + 1):
                for d in range(max_digit + 1):
                    total = a + b + c + d

                    for e in range(b, max_digit + 1):
                        for f in range(max_digit + 1):
                            for g in range(max_digit + 1):
                                h = total - e - f - g
                                if h > max_digit:
                                    continue

                                for i in range(max_digit + 1):
                                    m = total - a - e - i
                                    if m > max_digit:
                                        continue

                                    j = total - d - g - m
                                    if j > max_digit:
                                        continue

                                    n = total - b - f - j
                                    if n > max_digit:
                                        continue

                                    for k in range(max_digit + 1):
                                        o = total - c - g - k
                                        if o > max_digit:
                                            continue

                                        l = total - i - j - k
                                        if l > max_digit:
                                            continue

                                        p = total - m - n - o
                                        if p > max_digit:
                                            continue

                                        if total != a + f + k + p:
                                            continue

                                        result += 1
                                        if b < e:
                                            result += 1

    if even:
        result *= 2

    return result


def main() -> None:
    print(solve(9))


if __name__ == "__main__":
    main()
