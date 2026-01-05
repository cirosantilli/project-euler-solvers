#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0371.cpp"""


def search(num_plates):
    max_have = num_plates // 2 - 1
    plates = float(num_plates)

    have500 = [0.0] * (max_have + 1)
    no500 = [0.0] * (max_have + 1)

    prob_duplicate = max_have / plates
    prob_zero = 1.0 / plates
    prob_500 = 1.0 / plates

    prob_unchanged = prob_duplicate + prob_zero
    have500[max_have] = 1.0 / (1.0 - prob_unchanged)
    no500[max_have] = (1.0 + prob_500 * have500[max_have]) / (1.0 - prob_unchanged)

    for have in range(max_have - 1, -1, -1):
        num_new = plates - 2 * have - 2
        prob_new = num_new / plates

        prob_duplicate = have / plates
        prob_unchanged = prob_duplicate + prob_zero

        have500[have] = (1.0 + prob_new * have500[have + 1]) / (1.0 - prob_unchanged)
        no500[have] = (1.0 + prob_500 * have500[have] + prob_new * no500[have + 1]) / (
            1.0 - prob_unchanged
        )

    return no500[0]


def solve(num_plates=1000):
    return search(num_plates)


def main():
    print(f"{solve():.8f}")


if __name__ == "__main__":
    main()
