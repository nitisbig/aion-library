"""Bake the globe's land points: a Fibonacci sphere of N unit vectors, masked by Natural Earth 1:110m land polygons.

Source: Natural Earth (public domain), ne_110m_land.geojson, from github.com/nvkelso/natural-earth-vector.
Usage (from the repo root):
    uv run python -I videos/011-matrix-exponential/assets/land/make_land.py \
        videos/011-matrix-exponential/assets/land/raw/ne_110m_land.geojson \
        videos/011-matrix-exponential/assets/land/land_pts.npy
Writes land_pts.npy and ocean_pts.npy, (M, 3) float32 arrays of unit vectors (x toward lon 0 at the equator, z toward the north pole).
"""
import json
import sys

import numpy as np

N = 26000


def fibonacci(n):
    k = np.arange(n) + 0.5
    lat = np.arcsin(1 - 2 * k / n)
    lon = (np.pi * (1 + 5 ** 0.5) * k) % (2 * np.pi) - np.pi
    return np.degrees(lon), np.degrees(lat)


def inside(ring, x, y):
    ring = np.asarray(ring, float)
    ins = np.zeros(len(x), bool)
    x1, y1 = ring[:, 0], ring[:, 1]
    x2, y2 = np.roll(x1, -1), np.roll(y1, -1)
    for a, b, c, d in zip(x1, y1, x2, y2):
        ins ^= ((b > y) != (d > y)) & (x < (c - a) * (y - b) / (d - b + 1e-12) + a)
    return ins


def main(src, dst):
    with open(src) as f:
        gj = json.load(f)
    lon, lat = fibonacci(N)
    land = np.zeros(N, bool)
    for feat in gj["features"]:
        g = feat["geometry"]
        polys = [g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]
        for poly in polys:
            outer = inside(poly[0], lon, lat)
            for hole in poly[1:]:
                outer &= ~inside(hole, lon, lat)
            land |= outer
    L, B = np.radians(lon[land]), np.radians(lat[land])
    pts = np.stack([np.cos(B) * np.cos(L), np.cos(B) * np.sin(L), np.sin(B)], -1).astype(np.float32)
    np.save(dst, pts)
    print(f"{land.sum()} land points of {N} ({land.mean():.1%})")
    # a sparser ocean shell: every 3rd sphere point that is not land
    sea = ~land & (np.arange(N) % 3 == 0)
    L, B = np.radians(lon[sea]), np.radians(lat[sea])
    np.save(dst.replace("land_pts", "ocean_pts"),
            np.stack([np.cos(B) * np.cos(L), np.cos(B) * np.sin(L), np.sin(B)], -1).astype(np.float32))
    print(f"{sea.sum()} ocean points")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
