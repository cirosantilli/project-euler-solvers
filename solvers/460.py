import math
from typing import List


def _build_band(d: int, half: int, band: int) -> List[List[int]]:
    k = math.sqrt((d / 2) ** 2 + 1.0)
    ys: List[List[int]] = []
    for x in range(half + 1):
        y_c = math.sqrt(max(0.0, k * k - (x - d / 2) ** 2))
        lo = max(1, int(math.floor(y_c)) - band)
        hi = int(math.ceil(y_c)) + band
        ylist = list(range(lo, hi + 1))
        if x == 0 and 1 not in ylist:
            ylist.append(1)
        ylist.sort()
        ys.append(ylist)
    return ys


def _compute_half_time(d: int, band: int, max_dx: int) -> float:
    assert d % 2 == 0
    half = d // 2
    ys = _build_band(d, half, band)
    max_y = max(max(lst) for lst in ys)

    ln = [0.0] * (max_y + 1)
    inv_y = [0.0] * (max_y + 1)
    for y in range(1, max_y + 1):
        ln[y] = math.log(y)
        inv_y[y] = 1.0 / y

    ln_lists: List[List[float]] = [[ln[y] for y in ylist] for ylist in ys]

    max_dx = min(max_dx, half)
    sqrt_table = [[0.0] * (max_dx + 1) for _ in range(max_y + 1)]
    for dy in range(max_y + 1):
        row = sqrt_table[dy]
        for dx in range(1, max_dx + 1):
            row[dx] = math.hypot(dx, dy)

    inf = 1e100
    dp: List[List[float]] = [[inf] * len(ylist) for ylist in ys]

    # Start at (0, 1).
    idx_start = ys[0].index(1)
    dp[0][idx_start] = 0.0

    for x in range(half + 1):
        ylist = ys[x]
        lnlist = ln_lists[x]
        arr = dp[x]
        n = len(ylist)

        # Vertical relaxation within the same x (adjacent y moves).
        for i in range(1, n):
            cost = lnlist[i] - lnlist[i - 1]
            alt = arr[i - 1] + cost
            if alt < arr[i]:
                arr[i] = alt
        for i in range(n - 2, -1, -1):
            cost = lnlist[i + 1] - lnlist[i]
            alt = arr[i + 1] + cost
            if alt < arr[i]:
                arr[i] = alt

        # Forward moves to x+dx.
        for dx in range(1, max_dx + 1):
            x1 = x + dx
            if x1 > half:
                break
            ylist1 = ys[x1]
            lnlist1 = ln_lists[x1]
            dp1 = dp[x1]
            n1 = len(ylist1)
            for i in range(n):
                y0 = ylist[i]
                ln0 = lnlist[i]
                t0 = arr[i]
                inv_y0 = inv_y[y0]
                for j in range(n1):
                    y1 = ylist1[j]
                    dy = y1 - y0
                    if dy == 0:
                        inv_l = inv_y0
                        ady = 0
                    else:
                        inv_l = (lnlist1[j] - ln0) / dy
                        ady = abs(dy)
                    nt = t0 + inv_l * sqrt_table[ady][dx]
                    if nt < dp1[j]:
                        dp1[j] = nt

    return min(dp[half])


def compute_f(d: int) -> float:
    # Empirical safe bounds for the optimal path band and step size.
    band = 10
    max_dx = int(0.8 * math.sqrt(d)) + 5
    half_time = _compute_half_time(d, band, max_dx)
    return 2.0 * half_time


def main() -> None:
    assert abs(compute_f(4) - 2.960516287) < 5e-9
    assert abs(compute_f(10) - 4.668187834) < 5e-9
    assert abs(compute_f(100) - 9.217221972) < 5e-9

    result = compute_f(10000)
    print(f"{result:.9f}")


if __name__ == "__main__":
    main()
