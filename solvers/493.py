#!/usr/bin/env python
'''Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0493.cpp'''
def myrand():
    if not hasattr(myrand, "seed"):
        myrand.seed = 0
    myrand.seed = (6364136223846793005 * myrand.seed + 1) & 0xFFFFFFFFFFFFFFFF
    return myrand.seed >> 30


def monte_carlo(num_colors, num_balls_per_color, picks, iterations):
    num_balls = num_colors * num_balls_per_color
    total = 0
    for _ in range(iterations):
        current = [True] * num_balls
        for _ in range(picks):
            while True:
                ball_id = myrand() % num_balls
                if current[ball_id]:
                    current[ball_id] = False
                    break
        for c in range(num_colors):
            base = c * num_balls_per_color
            for b in range(num_balls_per_color):
                if not current[base + b]:
                    total += 1
                    break
    return total / float(iterations)


def choose(n, k):
    result = 1
    inv_k = 1
    while inv_k <= k:
        result *= n
        result //= inv_k
        n -= 1
        inv_k += 1
    return result


def solve(colors=7, balls_per_color=10, picks=20):
    num_balls = colors * balls_per_color

    result = 0.0
    for _ in range(colors):
        dont_pick_that_color = choose(num_balls - balls_per_color, picks)
        total = choose(num_balls, picks)
        absent = dont_pick_that_color / float(total)
        has_color = 1.0 - absent
        result += has_color

    return result


def main():
    print(f"{solve():.9f}")


if __name__ == "__main__":
    main()
