#!/usr/bin/env python3
"""
Project Euler 212: Combined Volume of Cuboids

Block decomposition trick:
- Max cuboid edge length is 399, so with block size B=400 each cuboid overlaps at most 8 blocks.
- Blocks are disjoint => total union volume is sum of per-block union volumes.
- Per-block union volume computed exactly via 3D coordinate compression + 3D imos + prefix sums.
"""

from __future__ import annotations


def generate_cuboids(n: int) -> list[tuple[int, int, int, int, int, int]]:
    """
    Returns cuboids as (x0, x1, y0, y1, z0, z1) with half-open intervals.
    """
    m = 6 * n
    MOD = 1_000_000
    S = [0] * (m + 1)  # 1-indexed

    # S_1..S_55
    upto = min(55, m)
    for k in range(1, upto + 1):
        S[k] = (100003 - 200003 * k + 300007 * k * k * k) % MOD

    # S_56..S_m
    for k in range(56, m + 1):
        S[k] = (S[k - 24] + S[k - 55]) % MOD

    cubs: list[tuple[int, int, int, int, int, int]] = []
    for i in range(1, n + 1):
        x0 = S[6 * i - 5] % 10000
        y0 = S[6 * i - 4] % 10000
        z0 = S[6 * i - 3] % 10000
        dx = 1 + (S[6 * i - 2] % 399)
        dy = 1 + (S[6 * i - 1] % 399)
        dz = 1 + (S[6 * i] % 399)
        cubs.append((x0, x0 + dx, y0, y0 + dy, z0, z0 + dz))
    return cubs


def union_volume_blockwise(
    cuboids: list[tuple[int, int, int, int, int, int]], B: int = 400
) -> int:
    """
    Exact union volume by splitting into BxBxB blocks and summing per-block union volumes.
    """
    # All endpoints lie in [0, 10400). B=400 => nb=26 blocks per axis (0..25)
    max_coord = 10400
    nb = (max_coord + B - 1) // B  # 26 when B=400

    # blocks[(bx,by,bz)] stored in flat list:
    # idx = (bx*nb + by)*nb + bz
    blocks: list[list[tuple[int, int, int, int, int, int]]] = [
        [] for _ in range(nb * nb * nb)
    ]

    def bindex(bx: int, by: int, bz: int) -> int:
        return (bx * nb + by) * nb + bz

    # Distribute clipped sub-cuboids into blocks
    for x0, x1, y0, y1, z0, z1 in cuboids:
        bx0 = x0 // B
        bx1 = (x1 - 1) // B
        by0 = y0 // B
        by1 = (y1 - 1) // B
        bz0 = z0 // B
        bz1 = (z1 - 1) // B

        for bx in range(bx0, bx1 + 1):
            xL = bx * B
            xR = xL + B
            rx0 = x0 - xL if x0 > xL else 0
            rx1 = x1 - xL if x1 < xR else B

            for by in range(by0, by1 + 1):
                yL = by * B
                yR = yL + B
                ry0 = y0 - yL if y0 > yL else 0
                ry1 = y1 - yL if y1 < yR else B

                for bz in range(bz0, bz1 + 1):
                    zL = bz * B
                    zR = zL + B
                    rz0 = z0 - zL if z0 > zL else 0
                    rz1 = z1 - zL if z1 < zR else B

                    blocks[bindex(bx, by, bz)].append((rx0, rx1, ry0, ry1, rz0, rz1))

    total = 0

    # Process each block independently
    for cubs in blocks:
        if not cubs:
            continue

        # Coordinate compression within the block (relative coords in [0,B])
        xs = [0, B]
        ys = [0, B]
        zs = [0, B]
        for x0, x1, y0, y1, z0, z1 in cubs:
            xs.append(x0)
            xs.append(x1)
            ys.append(y0)
            ys.append(y1)
            zs.append(z0)
            zs.append(z1)

        xs = sorted(set(xs))
        ys = sorted(set(ys))
        zs = sorted(set(zs))

        nx, ny, nz = len(xs), len(ys), len(zs)

        xi = {v: i for i, v in enumerate(xs)}
        yi = {v: i for i, v in enumerate(ys)}
        zi = {v: i for i, v in enumerate(zs)}

        stride_y = nz
        stride_x = ny * nz
        size = nx * ny * nz

        # 3D difference array (imos)
        diff = [0] * size

        for x0, x1, y0, y1, z0, z1 in cubs:
            x0i = xi[x0]
            x1i = xi[x1]
            y0i = yi[y0]
            y1i = yi[y1]
            z0i = zi[z0]
            z1i = zi[z1]

            diff[x0i * stride_x + y0i * stride_y + z0i] += 1
            diff[x1i * stride_x + y0i * stride_y + z0i] -= 1
            diff[x0i * stride_x + y1i * stride_y + z0i] -= 1
            diff[x0i * stride_x + y0i * stride_y + z1i] -= 1
            diff[x1i * stride_x + y1i * stride_y + z0i] += 1
            diff[x1i * stride_x + y0i * stride_y + z1i] += 1
            diff[x0i * stride_x + y1i * stride_y + z1i] += 1
            diff[x1i * stride_x + y1i * stride_y + z1i] -= 1

        # Prefix sums along x then y
        for i in range(1, nx):
            base = i * stride_x
            prev = (i - 1) * stride_x
            for j in range(ny):
                off = base + j * stride_y
                offp = prev + j * stride_y
                for k in range(nz):
                    diff[off + k] += diff[offp + k]

        for i in range(nx):
            base = i * stride_x
            for j in range(1, ny):
                off = base + j * stride_y
                offp = base + (j - 1) * stride_y
                for k in range(nz):
                    diff[off + k] += diff[offp + k]

        # Cell sizes
        dx = [xs[i + 1] - xs[i] for i in range(nx - 1)]
        dy = [ys[j + 1] - ys[j] for j in range(ny - 1)]
        dz = [zs[k + 1] - zs[k] for k in range(nz - 1)]

        # Prefix sum along z + accumulate volume
        vol = 0
        for i in range(nx - 1):
            base = i * stride_x
            dxi = dx[i]
            for j in range(ny - 1):
                off = base + j * stride_y
                area_xy = dxi * dy[j]
                run = 0
                for k in range(nz - 1):
                    run += diff[off + k]
                    if run > 0:
                        vol += area_xy * dz[k]

        total += vol

    return total


def solve() -> int:
    # --- Problem statement test values ---
    c2 = generate_cuboids(2)
    x0, x1, y0, y1, z0, z1 = c2[0]
    assert (x0, y0, z0) == (7, 53, 183)
    assert (x1 - x0, y1 - y0, z1 - z0) == (94, 369, 56)

    x0, x1, y0, y1, z0, z1 = c2[1]
    assert (x0, y0, z0) == (2383, 3563, 5079)
    assert (x1 - x0, y1 - y0, z1 - z0) == (42, 212, 344)

    assert union_volume_blockwise(generate_cuboids(100), B=400) == 723_581_599

    # --- Actual answer ---
    cubs = generate_cuboids(50_000)
    return union_volume_blockwise(cubs, B=400)


if __name__ == "__main__":
    print(solve())
