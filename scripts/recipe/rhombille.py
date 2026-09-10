"""Edge-rhombille of a 3-valent Goldberg shell.

Parent GP(m,n): keep V parent verts, add F face centroids, one quad per
parent edge: (va, c(fL), vb, c(fR)). T=3 → F=90, V=92, E=180, χ=2.

This realises 30T rhombs. Not a Hypothesis that the quads are MS2 Cα.
"""

from __future__ import annotations

from typing import Any

from .geodesic import _norm
from .goldberg import _cross, _dot, _sub, face_centroid


def rhombille_from_goldberg(gold: dict[str, Any]) -> dict[str, Any]:
    parent_verts = gold["verts"]
    parent_faces = gold["faces"]
    cents = [face_centroid(gold, f) for f in parent_faces]
    n_parent = len(parent_verts)

    edge_hits: dict[tuple[int, int], list[tuple[int, int, int]]] = {}
    for fi, face in enumerate(parent_faces):
        k = len(face)
        for i in range(k):
            va, vb = face[i], face[(i + 1) % k]
            key = (va, vb) if va < vb else (vb, va)
            edge_hits.setdefault(key, []).append((fi, va, vb))

    faces: list[list[int]] = []
    for key, hits in edge_hits.items():
        if len(hits) != 2:
            raise ValueError(f"parent edge {key} has {len(hits)} faces, want 2")
        (f1, a1, b1), (f2, a2, b2) = hits
        if (a2, b2) == (b1, a1):
            f_l, a, b, f_r = f1, a1, b1, f2
        elif (a1, b1) == (b2, a2):
            f_l, a, b, f_r = f2, a2, b2, f1
        else:
            raise ValueError(f"edge {key} winding mismatch {hits}")
        faces.append([a, n_parent + f_l, b, n_parent + f_r])

    verts = list(parent_verts) + cents
    # outward: quad centroid should point away from origin
    oriented: list[list[int]] = []
    for face in faces:
        pts = [verts[i] for i in face]
        cen = (
            sum(p[0] for p in pts) / 4.0,
            sum(p[1] for p in pts) / 4.0,
            sum(p[2] for p in pts) / 4.0,
        )
        nrm = _cross(_sub(pts[1], pts[0]), _sub(pts[3], pts[0]))
        if _dot(nrm, cen) < 0.0:
            oriented.append([face[0], face[3], face[2], face[1]])
        else:
            oriented.append(face)
    faces = oriented

    seen: set[tuple[int, int]] = set()
    for face in faces:
        k = len(face)
        for i in range(k):
            a, b = face[i], face[(i + 1) % k]
            seen.add((a, b) if a < b else (b, a))
    e = len(seen)
    v = len(verts)
    f = len(faces)
    chi = v - e + f
    if chi != 2:
        raise ValueError(f"rhombille χ={chi} (V={v} E={e} F={f}), want 2")

    t = gold["T"]
    return {
        "m": gold["m"],
        "n": gold["n"],
        "T": t,
        "class": gold["class"],
        "kind": "rhombille",
        "parent_kind": "goldberg",
        "verts": [_norm(p) for p in verts],
        "faces": faces,
        "V": v,
        "F": f,
        "E": e,
        "chi": chi,
        "n_pentagons": 0,
        "n_hexagons": 0,
        "n_rhombs": f,
        "parent_V": n_parent,
        "parent_F": len(parent_faces),
        "parent_E": gold["E"],
    }
