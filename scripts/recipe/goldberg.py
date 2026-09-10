"""Goldberg dual of an icosahedral geodesic polyhedron.

Dual: geodesic vertices ↔ Goldberg faces (12 pentagons + 10(T−1) hexagons).
Geodesic faces ↔ Goldberg vertices. Three faces meet at every vertex.

Software fact of counts: F = 10T+2 = geodesic V, V = 20T = geodesic F.
"""

from __future__ import annotations

import math
from collections import defaultdict
from typing import Any

from .geodesic import _norm

EPS = 1e-10


def _sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _cross(a, b):
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def _centroid(pts: list[tuple[float, float, float]]) -> tuple[float, float, float]:
    n = len(pts)
    s = (0.0, 0.0, 0.0)
    for p in pts:
        s = (s[0] + p[0], s[1] + p[1], s[2] + p[2])
    return _norm((s[0] / n, s[1] / n, s[2] / n))


def _order_around(
    vertex: tuple[float, float, float],
    centroids: list[tuple[float, float, float]],
    idxs: list[int],
) -> list[int]:
    nrm = _norm(vertex)
    t0 = _cross(nrm, (0.0, 0.0, 1.0))
    if _dot(t0, t0) < 1e-12:
        t0 = _cross(nrm, (0.0, 1.0, 0.0))
    t0 = _norm(t0)
    t1 = _cross(nrm, t0)
    keyed = []
    for i in idxs:
        v = _sub(centroids[i], vertex)
        keyed.append((math.atan2(_dot(v, t1), _dot(v, t0)), i))
    keyed.sort()
    return [i for _, i in keyed]


def goldberg_dual(geo: dict[str, Any]) -> dict[str, Any]:
    """Dualize a geodesic mesh produced by geodesic_polyhedron."""
    verts_g = geo["verts"]
    faces_g = geo["faces"]
    centroids = []
    for a, b, c in faces_g:
        centroids.append(_centroid([verts_g[a], verts_g[b], verts_g[c]]))

    incident: dict[int, list[int]] = defaultdict(list)
    for fi, (a, b, c) in enumerate(faces_g):
        incident[a].append(fi)
        incident[b].append(fi)
        incident[c].append(fi)

    dual_faces: list[list[int]] = []
    n_pent = 0
    n_hex = 0
    n_other = 0
    for vi, v in enumerate(verts_g):
        ring = _order_around(v, centroids, incident[vi])
        dual_faces.append(ring)
        d = len(ring)
        if d == 5:
            n_pent += 1
        elif d == 6:
            n_hex += 1
        else:
            n_other += 1

    t = geo["T"]
    return {
        "m": geo["m"],
        "n": geo["n"],
        "T": t,
        "class": geo["class"],
        "kind": "goldberg",
        "verts": centroids,
        "faces": dual_faces,
        "V": len(centroids),
        "F": len(dual_faces),
        "E": geo["E"],
        "n_pentagons": n_pent,
        "n_hexagons": n_hex,
        "n_other": n_other,
        "geodesic": geo,
    }


def face_centroid(
    net: dict[str, Any], face: list[int] | tuple[int, ...]
) -> tuple[float, float, float]:
    verts = net["verts"]
    return _centroid([verts[i] for i in face])
