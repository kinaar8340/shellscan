"""Icosahedral geodesic polyhedra {3,5+}m,n.

Theorem: T=m²+mn+n², V=10T+2, F=20T, E=30T.
Class I (n=0 or m=0) matches the qga_gpu Class I stamp at (2,0) → 80 faces.
Class II m=n. Class III both nonzero and unequal; (m,n) and (n,m) are
enantiomorphs — do not swap.

Construction: Caspar–Klug triangle on the hexagonal lattice with vertices
(0,0), (m,n), rot60(m,n)=(-n, m+n). Unit hex triangles inside that
triangle are mapped by barycentric coordinates onto each of the 20
icosahedral faces and projected to S².
"""

from __future__ import annotations

import math
from typing import Any

from .archimedean import hex_class, triangulation_number

PHI = (1.0 + math.sqrt(5.0)) * 0.5
EPS = 1e-8
INTERN_SCALE = 1e5

# Same 12-vertex / 20-face listing as qga_gpu class_i_icosahedral.
_RAW = (
    (-1.0, PHI, 0.0),
    (1.0, PHI, 0.0),
    (-1.0, -PHI, 0.0),
    (1.0, -PHI, 0.0),
    (0.0, -1.0, PHI),
    (0.0, 1.0, PHI),
    (0.0, -1.0, -PHI),
    (0.0, 1.0, -PHI),
    (PHI, 0.0, -1.0),
    (PHI, 0.0, 1.0),
    (-PHI, 0.0, -1.0),
    (-PHI, 0.0, 1.0),
)

# Outward triangles, same order as qga_gpu.
_FACES = (
    (0, 11, 5),
    (0, 5, 1),
    (0, 1, 7),
    (0, 7, 10),
    (0, 10, 11),
    (1, 5, 9),
    (5, 11, 4),
    (11, 10, 2),
    (10, 7, 6),
    (7, 1, 8),
    (3, 9, 4),
    (3, 4, 2),
    (3, 2, 6),
    (3, 6, 8),
    (3, 8, 9),
    (4, 9, 5),
    (2, 4, 11),
    (6, 2, 10),
    (8, 6, 7),
    (9, 8, 1),
)


def _norm(p: tuple[float, float, float]) -> tuple[float, float, float]:
    n = math.sqrt(p[0] * p[0] + p[1] * p[1] + p[2] * p[2])
    if n < EPS:
        raise ValueError("zero vector")
    return (p[0] / n, p[1] / n, p[2] / n)


def _add(
    a: tuple[float, float, float], b: tuple[float, float, float], s: float = 1.0
) -> tuple[float, float, float]:
    return (a[0] + s * b[0], a[1] + s * b[1], a[2] + s * b[2])


def _scale(a: tuple[float, float, float], s: float) -> tuple[float, float, float]:
    return (a[0] * s, a[1] * s, a[2] * s)


def icosahedron() -> tuple[list[tuple[float, float, float]], tuple[tuple[int, int, int], ...]]:
    verts = [_norm(p) for p in _RAW]
    return verts, _FACES


def rot60(i: int, j: int) -> tuple[int, int]:
    """60° rotation in hexagonal coordinates: (i,j) → (-j, i+j)."""
    return (-j, i + j)


def hex_to_xy(i: float, j: float) -> tuple[float, float]:
    return (i + 0.5 * j, j * math.sqrt(3.0) * 0.5)


def _barycentric(
    p: tuple[float, float],
    a: tuple[float, float],
    b: tuple[float, float],
    c: tuple[float, float],
) -> tuple[float, float, float]:
    v0x, v0y = b[0] - a[0], b[1] - a[1]
    v1x, v1y = c[0] - a[0], c[1] - a[1]
    v2x, v2y = p[0] - a[0], p[1] - a[1]
    den = v0x * v1y - v1x * v0y
    if abs(den) < EPS:
        raise ValueError("degenerate CK triangle")
    u = (v2x * v1y - v1x * v2y) / den  # weight of B
    v = (v0x * v2y - v2x * v0y) / den  # weight of C
    w = 1.0 - u - v  # weight of A
    return (w, u, v)


def _inside(wuv: tuple[float, float, float], eps: float = 1e-7) -> bool:
    return wuv[0] >= -eps and wuv[1] >= -eps and wuv[2] >= -eps


def ck_triangle(m: int, n: int) -> tuple[tuple[int, int], tuple[int, int], tuple[int, int]]:
    p0 = (0, 0)
    p1 = (int(m), int(n))
    p2 = rot60(p1[0], p1[1])
    return (p0, p1, p2)


def lattice_points(m: int, n: int) -> list[tuple[int, int]]:
    p0, p1, p2 = ck_triangle(m, n)
    a, b, c = hex_to_xy(*p0), hex_to_xy(*p1), hex_to_xy(*p2)
    is_ = [p0[0], p1[0], p2[0]]
    js_ = [p0[1], p1[1], p2[1]]
    pts: list[tuple[int, int]] = []
    for i in range(min(is_) - 1, max(is_) + 2):
        for j in range(min(js_) - 1, max(js_) + 2):
            wuv = _barycentric(hex_to_xy(i, j), a, b, c)
            if _inside(wuv):
                pts.append((i, j))
    return pts


def _ccw(a: tuple[float, float], b: tuple[float, float], c: tuple[float, float]) -> float:
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def _in_circumcircle(
    a: tuple[float, float],
    b: tuple[float, float],
    c: tuple[float, float],
    d: tuple[float, float],
) -> bool:
    """D inside circumcircle of CCW triangle ABC."""
    adx, ady = a[0] - d[0], a[1] - d[1]
    bdx, bdy = b[0] - d[0], b[1] - d[1]
    cdx, cdy = c[0] - d[0], c[1] - d[1]
    det = (
        (adx * adx + ady * ady) * (bdx * cdy - cdx * bdy)
        - (bdx * bdx + bdy * bdy) * (adx * cdy - cdx * ady)
        + (cdx * cdx + cdy * cdy) * (adx * bdy - bdx * ady)
    )
    return det > EPS


def ck_triangles(m: int, n: int) -> list[tuple[tuple[int, int], ...]]:
    """Delaunay triangulation of hex-lattice points in the CK triangle.

    Class I recovers the unit hex tiling. Class II/III need the long
    CK sides (hex length √T) as edges — unit (1,0)/(0,1) steps do not
    fill a skewed triangle. Software fact: number of triangles equals T.
    """
    pts = lattice_points(m, n)
    xy = [hex_to_xy(*p) for p in pts]
    npts = len(pts)
    faces: list[tuple[tuple[int, int], ...]] = []
    for i in range(npts):
        for j in range(i + 1, npts):
            for k in range(j + 1, npts):
                a, b, c = xy[i], xy[j], xy[k]
                cr = _ccw(a, b, c)
                if abs(cr) < EPS:
                    continue
                if cr < 0:
                    aa, bb, cc = a, c, b
                    ia, ib, ic = i, k, j
                else:
                    aa, bb, cc = a, b, c
                    ia, ib, ic = i, j, k
                if any(
                    _in_circumcircle(aa, bb, cc, xy[p])
                    for p in range(npts)
                    if p not in (i, j, k)
                ):
                    continue
                faces.append((pts[ia], pts[ib], pts[ic]))
    return faces


def _sub(a: tuple[float, float, float], b: tuple[float, float, float]) -> tuple[float, float, float]:
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _dot(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _cross(a: tuple[float, float, float], b: tuple[float, float, float]) -> tuple[float, float, float]:
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def _convex_hull_faces(
    verts: list[tuple[float, float, float]],
) -> list[tuple[int, int, int]]:
    """Triangle faces of the convex hull, oriented outward from the origin.

    Brute-force: a triple is a hull face iff every other vertex is on one
    side of its plane. n ≤ 162 for the shipped T-series; no numpy/scipy.
    """
    n = len(verts)
    faces: list[tuple[int, int, int]] = []
    plane_eps = 1e-9
    for i in range(n):
        a = verts[i]
        for j in range(i + 1, n):
            b = verts[j]
            ab = _sub(b, a)
            for k in range(j + 1, n):
                c = verts[k]
                nrm = _cross(ab, _sub(c, a))
                if _dot(nrm, nrm) < EPS * EPS:
                    continue
                pos = 0
                neg = 0
                skip = False
                for p in range(n):
                    if p == i or p == j or p == k:
                        continue
                    d = _dot(nrm, _sub(verts[p], a))
                    if d > plane_eps:
                        pos += 1
                    elif d < -plane_eps:
                        neg += 1
                    if pos and neg:
                        skip = True
                        break
                if skip or (pos and neg):
                    continue
                # origin is inside the spherical polyhedron; outward = away from 0
                cen = ((a[0] + b[0] + c[0]) / 3.0, (a[1] + b[1] + c[1]) / 3.0, (a[2] + b[2] + c[2]) / 3.0)
                if _dot(nrm, cen) < 0.0:
                    faces.append((i, k, j))
                else:
                    faces.append((i, j, k))
    return faces


def _intern_key(p: tuple[float, float, float]) -> tuple[int, int, int]:
    return (
        int(round(p[0] * INTERN_SCALE)),
        int(round(p[1] * INTERN_SCALE)),
        int(round(p[2] * INTERN_SCALE)),
    )


def geodesic_polyhedron(m: int, n: int) -> dict[str, Any]:
    """Return verts, triangular faces, edges, and CK counts. Software fact."""
    t = triangulation_number(m, n)
    base, ifaces = icosahedron()
    p0, p1, p2 = ck_triangle(m, n)
    a2, b2, c2 = hex_to_xy(*p0), hex_to_xy(*p1), hex_to_xy(*p2)
    small = ck_triangles(m, n)

    verts: list[tuple[float, float, float]] = []
    id_of: dict[tuple[int, int, int], int] = {}

    def intern(p: tuple[float, float, float]) -> int:
        p = _norm(p)
        k = _intern_key(p)
        if k in id_of:
            return id_of[k]
        i = len(verts)
        verts.append(p)
        id_of[k] = i
        return i

    pts = lattice_points(m, n)
    for ia, ib, ic in ifaces:
        a, b, c = base[ia], base[ib], base[ic]
        for ij in pts:
            w, u, v = _barycentric(hex_to_xy(*ij), a2, b2, c2)
            intern(_add(_add(_scale(a, w), b, u), c, v))

    # Spherical Delaunay = convex hull of points on S². Per-face Delaunay of
    # the CK triangle is Class I only; II/III triangles cross icosa edges.
    faces = _convex_hull_faces(verts)
    edges: list[tuple[int, int]] = []
    seen: set[tuple[int, int]] = set()
    for a, b, c in faces:
        for e in ((a, b), (b, c), (c, a)):
            key = (e[0], e[1]) if e[0] < e[1] else (e[1], e[0])
            if key not in seen:
                seen.add(key)
                edges.append(key)

    return {
        "m": int(m),
        "n": int(n),
        "T": t,
        "class": hex_class(m, n),
        "kind": "geodesic",
        "verts": verts,
        "faces": faces,
        "edges": edges,
        "V": len(verts),
        "F": len(faces),
        "E": len(edges),
        "ck_face_T": len(small),
    }
