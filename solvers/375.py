#!/usr/bin/env python
'''Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0375.cpp'''
def search(size):
    state = 290797
    best = [(0, 0)]

    result = 0
    for i in range(1, size + 1):
        state = (state * state) % 50515093
        current = state

        valid_until = i
        while best[-1][0] >= current:
            valid_until = best[-1][1]
            best.pop()

        best.append((current, valid_until))

        last = i + 1
        for number, position in reversed(best[1:]):
            distance = last - position
            result += distance * number
            last = position

    return result


def main():
    assert search(10) == 432256955
    assert search(10000) == 3264567774119
    print(search(2000000000))


if __name__ == "__main__":
    main()
