#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0336.cpp"""


def next_permutation(seq):
    i = len(seq) - 2
    while i >= 0 and seq[i] >= seq[i + 1]:
        i -= 1
    if i < 0:
        return False
    j = len(seq) - 1
    while seq[j] <= seq[i]:
        j -= 1
    seq[i], seq[j] = seq[j], seq[i]
    seq[i + 1 :] = reversed(seq[i + 1 :])
    return True


def solve(length=11, stop_when_found=2011):
    train = list("CABDEFGHIJKLM")[:length]

    max_rotations = (len(train) - 1) * 2 - 1
    num_found = 0

    while True:
        current = train[:]
        expect = ord("A")
        rotations = 0
        for i in range(len(current) - 1):
            if current[i] == chr(expect):
                break
            if current[-1] == chr(expect) and i != len(current) - 2:
                break

            j = i + 1
            while current[j] != chr(expect):
                j += 1

            if j < len(current) - 1:
                current[j:] = reversed(current[j:])
                rotations += 1

            current[i:] = reversed(current[i:])
            rotations += 1
            expect += 1

        if rotations == max_rotations:
            num_found += 1
            if num_found == stop_when_found:
                break

        if not next_permutation(train):
            break

    return "".join(train)


def main():
    assert solve(6, 10) == "DFAECB"
    print(solve())


if __name__ == "__main__":
    main()
