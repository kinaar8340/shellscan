"""Open cylinder / helicoid chart. Segment-indexed u, azimuth φ.

Not a Goldberg net. No 12-pentagon close. No fifth hue.
u = (segment index + ½) / 13, T1 anterior → +z. φ from middorsal, degrees.
twist=0 is a circular cylinder; twist≠0 rotates the generators (helicoid).
"""

from __future__ import annotations

import math
from typing import Any, Sequence

from .setal import SEGMENTS


def cylinder_net(
    n_phi: int = 36,
    radius: float = 1.0,
    height: float = 2.0,
    twist: float = 0.0,
    segments: Sequence[str] | None = None,
) -> dict[str, Any]:
    segs = list(segments or SEGMENTS)
    n_u = len(segs)
    n_phi = max(8, int(n_phi))
    verts: list[tuple[float, float, float]] = []
    for i in range(n_u + 1):
        u = i / n_u
        z = height * (0.5 - u)
        for j in range(n_phi):
            phi = 360.0 * j / n_phi
            psi = math.radians(phi) + twist * u
            verts.append((radius * math.cos(psi), radius * math.sin(psi), z))
    faces: list[list[int]] = []
    face_chart: list[tuple[float, float, str, int, int]] = []
    for i in range(n_u):
        u_c = (i + 0.5) / n_u
        for j in range(n_phi):
            j2 = (j + 1) % n_phi
            a = i * n_phi + j
            b = i * n_phi + j2
            c = (i + 1) * n_phi + j2
            d = (i + 1) * n_phi + j
            faces.append([a, b, c, d])
            phi_c = 360.0 * (j + 0.5) / n_phi
            face_chart.append((u_c, phi_c, segs[i], i, j))
    return {
        "m": 0,
        "n": 0,
        "T": 0,
        "class": "helicoid" if abs(twist) > 1e-12 else "cylinder",
        "kind": "cylinder",
        "open": True,
        "n_pentagons": 0,
        "n_hexagons": 0,
        "verts": verts,
        "faces": faces,
        "face_chart": face_chart,
        "segments": segs,
        "n_phi": n_phi,
        "n_segments": n_u,
        "twist": float(twist),
        "radius": float(radius),
        "height": float(height),
        "V": len(verts),
        "F": len(faces),
        "E": n_u * n_phi * 2 + n_phi,  # open cylinder: verticals + rings including ends
    }


def face_centroid_euclid(
    net: dict[str, Any], face: list[int] | tuple[int, ...]
) -> tuple[float, float, float]:
    pts = [net["verts"][i] for i in face]
    n = len(pts)
    return (
        sum(p[0] for p in pts) / n,
        sum(p[1] for p in pts) / n,
        sum(p[2] for p in pts) / n,
    )


def phi_bin(phi_deg: float, n_phi: int) -> int:
    p = phi_deg % 360.0
    return int(p / 360.0 * n_phi) % n_phi


def dphi_deg(a: float, b: float) -> float:
    return abs(((a - b + 180.0) % 360.0) - 180.0)
