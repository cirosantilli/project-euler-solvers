from typing import Tuple


def digit_signature(n: int) -> Tuple[int, ...]:
    """Return a digit-count signature (length 10 tuple) for n in base-10."""
    cnt = [0] * 10
    while n > 0:
        cnt[n % 10] += 1
        n //= 10
    return tuple(cnt)


def smallest_permuted_multiple(limit_mul: int = 6) -> int:
    d = 1
    while True:
        lo = 10 ** (d - 1)
        hi = (10**d - 1) // limit_mul  # ensure limit_mul*x still has <= d digits
        for x in range(lo, hi + 1):
            sig = digit_signature(x)
            ok = True
            for m in range(2, limit_mul + 1):
                if digit_signature(m * x) != sig:
                    ok = False
                    break
            if ok:
                return x
        d += 1


def main() -> None:
    ans = smallest_permuted_multiple(6)
    print(ans)


if __name__ == "__main__":
    main()
