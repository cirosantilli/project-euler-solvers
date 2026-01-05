#!/usr/bin/env python

"""
Adapted from:
https://github.com/igorvanloo/Project-Euler-Explained/blob/19f85895945a2c9b688f85da142bae13f37dab65/Finished%20Problems/pe00141%20-%20Investigating%20progressive%20numbers%2C%20n%2C%20which%20are%20also%20square.py
by Igor Van Loo
"""


def is_square(x):
    square_root = x ** (1 / 2)
    if round(square_root) ** 2 == x:
        return True
    return False


def compute(limit):
    # r = x * y * y,
    # d = c * r = z * x * y,
    # q = c * d = z * z * x
    candidates = set()
    for z in range(2, int(limit ** (1 / 3)) + 1):
        for y in range(1, z):
            if z * z * z * y + y * y > limit:
                break
            for x in range(1, int(limit / (y * z * z * z)) + 1):
                n = z * z * z * x * x * y + x * y * y
                if n > limit:
                    break
                else:
                    if is_square(n):
                        candidates.add(n)
    return sum(candidates)


if __name__ == "__main__":
    assert compute(10**5) == 124657
    print(compute(10**12))
