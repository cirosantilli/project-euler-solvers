#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0185.cpp"""


def myrand(modulo: int) -> int:
    myrand.seed = (1103515245 * myrand.seed + 12345) & 0xFFFFFFFF
    return myrand.seed % modulo


def shuffle_digit(digit: int) -> int:
    old = digit
    while True:
        digit = myrand(10)
        if digit != old:
            return digit


def add_guess(
    guess: str, matches: int, sequences: list[list[int]], hits: list[int]
) -> None:
    sequences.append([int(c) for c in guess])
    hits.append(matches)


def distance(current: list[int], sequences: list[list[int]], hits: list[int]) -> int:
    errors = 0
    for i, seq in enumerate(sequences):
        same = 0
        for j in range(len(current)):
            if current[j] == seq[j]:
                same += 1
        if same > hits[i]:
            errors += same - hits[i]
        else:
            errors += hits[i] - same
    return errors


def solve_bruteforce(guesses: list[tuple[str, int]]) -> str:
    length = len(guesses[0][0])
    for value in range(10**length):
        candidate = str(value).zfill(length)
        ok = True
        for guess, matches in guesses:
            same = sum(1 for a, b in zip(candidate, guess) if a == b)
            if same != matches:
                ok = False
                break
        if ok:
            return candidate
    return ""


def solve_heuristic(guesses: list[tuple[str, int]]) -> str:
    sequences: list[list[int]] = []
    hits: list[int] = []
    for guess, matches in guesses:
        add_guess(guess, matches, sequences, hits)

    myrand.seed = 0

    num_digits = len(sequences[0])
    current = [shuffle_digit(0) for _ in range(num_digits)]

    max_rounds_without_improvement = 20
    quiet_rounds = 0

    errors = distance(current, sequences, hits)
    previous = errors

    while errors != 0:
        for idx in range(num_digits):
            previous_digit = current[idx]
            current[idx] = shuffle_digit(previous_digit)

            modified = distance(current, sequences, hits)
            if modified <= errors:
                errors = modified
            else:
                current[idx] = previous_digit

        if errors == previous:
            quiet_rounds += 1
            if quiet_rounds == max_rounds_without_improvement:
                current[myrand(num_digits)] = shuffle_digit(current[myrand(num_digits)])
                errors = distance(current, sequences, hits)
                quiet_rounds = 0
        else:
            quiet_rounds = 0
            previous = errors

    return "".join(str(c) for c in current)


def main() -> None:
    example_guesses = [
        ("90342", 2),
        ("70794", 0),
        ("39458", 2),
        ("34109", 1),
        ("51545", 2),
        ("12531", 1),
    ]
    assert solve_bruteforce(example_guesses) == "39542"

    guesses = [
        ("5616185650518293", 2),
        ("3847439647293047", 1),
        ("5855462940810587", 3),
        ("9742855507068353", 3),
        ("4296849643607543", 3),
        ("3174248439465858", 1),
        ("4513559094146117", 2),
        ("7890971548908067", 3),
        ("8157356344118483", 1),
        ("2615250744386899", 2),
        ("8690095851526254", 3),
        ("6375711915077050", 1),
        ("6913859173121360", 1),
        ("6442889055042768", 2),
        ("2321386104303845", 0),
        ("2326509471271448", 2),
        ("5251583379644322", 2),
        ("1748270476758276", 3),
        ("4895722652190306", 1),
        ("3041631117224635", 3),
        ("1841236454324589", 3),
        ("2659862637316867", 2),
    ]
    print(solve_heuristic(guesses))


if __name__ == "__main__":
    main()
