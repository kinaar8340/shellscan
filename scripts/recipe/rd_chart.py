"""Gray–Scott on a growing (s, φ) chart. Model of pigment, not a segment clock.

Domain elongates by appending posterior s-rows (instar cartoon of a growth zone).
RD does not add Goldberg faces, does not move Hinton pins, is not morph_t.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np

# Spotted-ish Gray–Scott. Belts at necks are geometric, not a Turing wavelength.
F = 0.037
K = 0.060
DU = 0.16
DV = 0.08
DT = 0.8
NPHI = 36
STEPS_PER_STAGE = 400
SEED = 7

# elliptic, parabolic, hyperbolic, flat-pockets
SECTION_ELLIPTIC = 0
SECTION_PARABOLIC = 1
SECTION_HYPERBOLIC = 2
SECTION_FLAT = 3


def _lap(a: np.ndarray) -> np.ndarray:
    """Periodic in φ (axis 1), Neumann in s (axis 0)."""
    pad = np.pad(a, ((1, 1), (0, 0)), mode="edge")
    ds = pad[2:] + pad[:-2] - 2.0 * a
    dphi = np.roll(a, 1, axis=1) + np.roll(a, -1, axis=1) - 2.0 * a
    return ds + dphi


def _grow(u: np.ndarray, v: np.ndarray, add: int, rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
    if add <= 0:
        return u, v
    tail_u = np.repeat(u[-1:], add, axis=0)
    tail_v = np.repeat(v[-1:], add, axis=0)
    tail_u += 0.04 * rng.standard_normal(tail_u.shape)
    tail_v += 0.08 * rng.random(tail_v.shape)
    tail_u = np.clip(tail_u, 0.0, 1.0)
    tail_v = np.clip(tail_v, 0.0, 1.0)
    return np.vstack([u, tail_u]), np.vstack([v, tail_v])


def _seed_spots(v: np.ndarray, sites: list[dict[str, Any]], s_max: float, rng: np.random.Generator) -> None:
    ns, nphi = v.shape
    for site in sites:
        g = str(site.get("group") or "")
        if g not in ("D", "SD", "XD"):
            continue
        s = float(site.get("s") or 0.0)
        if s > s_max:
            continue
        i = int(round(s / max(s_max, 1e-6) * (ns - 1)))
        i = max(0, min(ns - 1, i))
        phi = abs(float(site.get("phi_deg") or 0.0)) % 360.0
        j = int(round(phi / 360.0 * nphi)) % nphi
        for di in (-1, 0, 1):
            for dj in (-1, 0, 1):
                ii = max(0, min(ns - 1, i + di))
                jj = (j + dj) % nphi
                v[ii, jj] = min(1.0, v[ii, jj] + 0.35 + 0.05 * rng.random())


def integrate(
    ns_stages: list[int],
    sites: list[dict[str, Any]],
    nphi: int = NPHI,
    steps: int = STEPS_PER_STAGE,
) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(SEED)
    ns0 = max(4, ns_stages[0])
    u = np.ones((ns0, nphi), dtype=np.float64)
    v = np.zeros((ns0, nphi), dtype=np.float64)
    v += 0.02 * rng.random(v.shape)
    _seed_spots(v, sites, ns0 / ns_stages[-1], rng)
    for target in ns_stages:
        u, v = _grow(u, v, target - u.shape[0], rng)
        s_max = u.shape[0] / ns_stages[-1]
        _seed_spots(v, sites, s_max, rng)
        for _ in range(steps):
            uvv = u * v * v
            u += DT * (DU * _lap(u) - uvv + F * (1.0 - u))
            v += DT * (DV * _lap(v) + uvv - (F + K) * v)
            np.clip(u, 0.0, 1.0, out=u)
            np.clip(v, 0.0, 1.0, out=v)
    return u, v


def threshold(v: np.ndarray) -> np.ndarray:
    ns, nphi = v.shape
    out = np.full((ns, nphi), SECTION_HYPERBOLIC, dtype=np.uint8)
    necks = {int(round(n * (ns - 1))) for n in (0.25, 0.50, 0.75)}
    for i in range(ns):
        s = i / max(ns - 1, 1)
        for j in range(nphi):
            phi = 360.0 * j / nphi
            phi_abs = min(phi, 360.0 - phi)
            if i in necks or i - 1 in necks or i + 1 in necks:
                out[i, j] = SECTION_ELLIPTIC
                continue
            ventral = 145.0 < phi_abs < 178.0
            proleg = (0.50 < s < 0.75) or s > 0.90
            if ventral and proleg and v[i, j] < 0.25:
                out[i, j] = SECTION_FLAT
            elif v[i, j] > 0.22:
                out[i, j] = SECTION_PARABOLIC
    return out


def run_polyxenes(chaeta_path: Path, out_path: Path) -> dict[str, Any]:
    atlas = json.loads(chaeta_path.read_text())
    sites = atlas.get("sites") or []
    # L1..L5 cartoon of posterior growth. Not a clock+wavefront law.
    ns_stages = [7, 10, 13, 19, 25]
    u, v = integrate(ns_stages, sites)
    sections = threshold(v)
    rec = {
        "claim": "Model",
        "law": "Gray-Scott",
        "F": F,
        "k": K,
        "Du": DU,
        "Dv": DV,
        "ns": int(sections.shape[0]),
        "nphi": int(sections.shape[1]),
        "note": "RD on growing (s,phi) chart. Not segment clock. Not morph_t. Not Theorem.",
        "sections": sections.astype(int).tolist(),
        "v_mean": float(v.mean()),
        "v_max": float(v.max()),
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(rec) + "\n")
    return rec
