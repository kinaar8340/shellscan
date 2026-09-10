"""Face paint: bands, tentacles, Caspar–Klug pentamer/hexamer, polyoma exception.

Paint assigns inner_cone section classes plus amplitude/offset/psi.
No fifth hue. Quasi-equivalence is a small offset give between pentamer
and hexamer sites of the same protein (Model).
"""

from __future__ import annotations

import math
from typing import Any

from .goldberg import face_centroid

SECTIONS = ("elliptic", "parabolic", "hyperbolic", "flat-pockets")


def _section(name: str) -> str:
    name = str(name)
    if name not in SECTIONS:
        raise ValueError(f"section {name!r} not in {SECTIONS}")
    return name


def _z(c: tuple[float, float, float]) -> float:
    return c[2]


def _shell_s(c: tuple[float, float, float]) -> float:
    return 0.5 * (c[2] + 1.0)


def _band_section(s: float, spec: dict[str, Any]) -> str:
    paint = spec.get("paint") or {}
    bands = paint.get("bands") or {}
    cycle = [_section(x) for x in bands.get("cycle") or ["elliptic"]]
    period = int(bands.get("period") or len(cycle) or 1)
    period = max(1, period)
    u = max(0.0, min(0.999999, s))
    idx = int(u * period) % len(cycle)
    return cycle[idx]


def _tentacle_indices(net: dict[str, Any], spec: dict[str, Any]) -> list[int]:
    sings = (spec.get("paint") or {}).get("singularities") or []
    if not sings:
        return []
    cents = [face_centroid(net, f) for f in net["faces"]]
    order_hi = sorted(range(len(cents)), key=lambda i: (-_z(cents[i]), i))
    order_lo = sorted(range(len(cents)), key=lambda i: (_z(cents[i]), i))
    used: set[int] = set()
    out: list[int] = []
    for sg in sings:
        if str(sg.get("kind")) != "tentacle":
            continue
        n = int(sg.get("count", 0))
        src = order_hi if str(sg.get("chart", "anterior")) == "anterior" else order_lo
        taken = 0
        for i in src:
            if i in used:
                continue
            out.append(i)
            used.add(i)
            taken += 1
            if taken >= n:
                break
    return out


def paint_faces(net: dict[str, Any], spec: dict[str, Any]) -> list[dict[str, Any]]:
    """One record per face. kind ∈ {band, tentacle, pentamer, hexamer, plain}."""
    wrap = spec.get("wrap") or {}
    paint = spec.get("paint") or {}
    mode = str(paint.get("mode") or ("caspar-klug" if net.get("kind") == "goldberg" and "bands" not in paint else "bands"))
    if paint.get("bands"):
        mode = "bands"
    if paint.get("mode"):
        mode = str(paint["mode"])
    lock = _section(wrap.get("section_lock", "elliptic"))
    persist = float(wrap.get("persist", 1.0))
    field = int(wrap.get("field", 0)) & 1
    qe = paint.get("quasi_equivalence") or {}
    pent_off = float(qe.get("pentamer_offset", 0.40))
    hex_off = float(qe.get("hexamer_offset", 0.45))
    pent_sec = _section(qe.get("pentamer_section", "elliptic"))
    hex_sec = _section(qe.get("hexamer_section", "hyperbolic"))

    faces = net["faces"]
    n = len(faces)
    kinds = ["plain"] * n
    tent = []
    if mode == "bands":
        tent = _tentacle_indices(net, spec)
        tent_set = set(tent)
    else:
        tent_set = set()

    from .dynamics import intensity_at, psi_at

    out: list[dict[str, Any]] = []
    for i, face in enumerate(faces):
        c = face_centroid(net, face)
        theta, phi = _cart_to_sph(c)
        s = _shell_s(c)
        kind = "plain"
        section = lock
        amp = intensity_at(s, spec)
        offset = 0.40
        psi = psi_at(phi, spec)

        if mode == "bands":
            kind = "band"
            section = _band_section(s, spec)
            if i in tent_set:
                kind = "tentacle"
                amp = 1.0
                section = _section((spec.get("paint") or {}).get("tentacle_section", "parabolic"))
        elif mode == "caspar-klug":
            deg = len(face)
            if deg == 5:
                kind = "pentamer"
                section = pent_sec
                offset = pent_off
                amp = 1.0
            else:
                kind = "hexamer"
                section = hex_sec
                offset = hex_off
                amp = 0.85
        elif mode == "all-pentamer":
            # Polyoma / papilloma: 72 pentamers on a T=7 lattice. Hypothesis
            # relative to biochemistry; Software fact of the paint flag.
            kind = "pentamer"
            section = pent_sec
            offset = pent_off
            amp = 1.0
        elif mode == "none":
            kind = "plain"
            section = lock
            amp = 1.0
        else:
            raise ValueError(f"unknown paint mode {mode!r}")

        out.append(
            {
                "i": i,
                "kind": kind,
                "section": section,
                "theta": theta,
                "phi": phi,
                "psi": psi,
                "offset": offset,
                "amplitude": amp,
                "shell_s": s,
                "persist": persist,
                "field": field,
                "layer": 0,
                "degree": len(face),
                "centroid": c,
            }
        )
    return out


def _cart_to_sph(p: tuple[float, float, float]) -> tuple[float, float]:
    x, y, z = p
    r = math.sqrt(x * x + y * y + z * z) or 1.0
    theta = math.acos(max(-1.0, min(1.0, z / r)))
    phi = math.atan2(y, x)
    return (theta, phi)
