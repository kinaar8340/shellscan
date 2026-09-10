"""Helicoid–catenoid associate family. Theorem: VMM / classical minimal surfaces.

    Px = bb*(cos(aa)*sinh(v)*sin(u) + sin(aa)*cosh(v)*cos(u))
    Py = bb*(-cos(aa)*sinh(v)*cos(u) + sin(aa)*cosh(v)*sin(u))
    Pz = bb*(cos(aa)*u + sin(aa)*v)

aa=0 helicoid (ruled screw). aa=π/2 catenoid (surface of revolution).
morph_t ∈ [0,1] maps to aa = morph_t * π/2.
The first fundamental form is independent of aa (isometry of the family).
"""

from __future__ import annotations

import math
from typing import Iterable, Sequence

PI_2 = math.pi / 2.0


def morph_aa(morph_t: float) -> float:
    t = max(0.0, min(1.0, float(morph_t)))
    return t * PI_2


def associate_point(
    u: float, v: float, aa: float, bb: float = 1.0
) -> tuple[float, float, float]:
    ca, sa = math.cos(aa), math.sin(aa)
    sh, ch = math.sinh(v), math.cosh(v)
    su, cu = math.sin(u), math.cos(u)
    px = bb * (ca * sh * su + sa * ch * cu)
    py = bb * (-ca * sh * cu + sa * ch * su)
    pz = bb * (ca * u + sa * v)
    return (px, py, pz)


def polyline_length(
    uv: Sequence[tuple[float, float]], aa: float, bb: float = 1.0
) -> float:
    """Sampled chord length of a (u,v) polyline at one associate angle."""
    if len(uv) < 2:
        return 0.0
    pts = [associate_point(u, v, aa, bb) for u, v in uv]
    total = 0.0
    for a, b in zip(pts, pts[1:]):
        dx, dy, dz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
        total += math.sqrt(dx * dx + dy * dy + dz * dz)
    return total


def sampled_isometry_error(
    uv: Iterable[tuple[float, float]], bb: float = 1.0
) -> float:
    """|L(helicoid) − L(catenoid)| on a shared (u,v) polyline. Software fact."""
    chain = list(uv)
    l0 = polyline_length(chain, 0.0, bb)
    l1 = polyline_length(chain, PI_2, bb)
    return abs(l0 - l1)


def first_fundamental_form(
    u: float, v: float, aa: float, bb: float = 1.0, h: float = 1e-6
) -> tuple[float, float, float]:
    """Numerical (E, F, G). Independent of aa (associate family)."""
    p = associate_point(u, v, aa, bb)
    pu = associate_point(u + h, v, aa, bb)
    pv = associate_point(u, v + h, aa, bb)
    ru = (pu[0] - p[0], pu[1] - p[1], pu[2] - p[2])
    rv = (pv[0] - p[0], pv[1] - p[1], pv[2] - p[2])
    inv = 1.0 / h
    ru = (ru[0] * inv, ru[1] * inv, ru[2] * inv)
    rv = (rv[0] * inv, rv[1] * inv, rv[2] * inv)
    e = ru[0] * ru[0] + ru[1] * ru[1] + ru[2] * ru[2]
    f = ru[0] * rv[0] + ru[1] * rv[1] + ru[2] * rv[2]
    g = rv[0] * rv[0] + rv[1] * rv[1] + rv[2] * rv[2]
    return (e, f, g)


def patch_grid(
    aa: float,
    bb: float = 1.0,
    u_span: float = 2.0 * math.pi,
    v_span: float = 2.0,
    nu: int = 24,
    nv: int = 12,
) -> tuple[list[tuple[float, float, float]], list[list[int]]]:
    """UV grid of the associate surface. Quads as 4-index faces. Model."""
    nu = max(2, int(nu))
    nv = max(2, int(nv))
    u0, v0 = -0.5 * u_span, -0.5 * v_span
    verts: list[tuple[float, float, float]] = []
    for j in range(nv + 1):
        v = v0 + v_span * j / nv
        for i in range(nu + 1):
            u = u0 + u_span * i / nu
            verts.append(associate_point(u, v, aa, bb))
    faces: list[list[int]] = []
    row = nu + 1
    for j in range(nv):
        for i in range(nu):
            a = j * row + i
            faces.append([a, a + 1, a + 1 + row, a + row])
    return verts, faces
