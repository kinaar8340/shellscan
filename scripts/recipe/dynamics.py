"""Intensity / orientation / winding schedule. Model."""

from __future__ import annotations

import math
from typing import Any


def morph_t(spec: dict[str, Any]) -> float:
    dyn = spec.get("dynamics") or {}
    return float(dyn.get("morph_t", 0.0))


def windings(spec: dict[str, Any]) -> int:
    dyn = spec.get("dynamics") or {}
    return int(dyn.get("windings", 1))


def intensity_at(s: float, spec: dict[str, Any]) -> float:
    """s is chart height in [0, 1] (shell_s). Periodic or a list of knots."""
    dyn = spec.get("dynamics") or {}
    kind = dyn.get("intensity", "periodic")
    s = max(0.0, min(1.0, float(s)))
    if isinstance(kind, (list, tuple)) and kind:
        if len(kind) == 1:
            return float(kind[0])
        x = s * (len(kind) - 1)
        i = int(x)
        if i >= len(kind) - 1:
            return float(kind[-1])
        t = x - i
        return float(kind[i]) * (1.0 - t) + float(kind[i + 1]) * t
    w = max(1, windings(spec))
    # raised cosine so bands read as intensity, not a fifth hue
    return 0.35 + 0.65 * 0.5 * (1.0 + math.cos(2.0 * math.pi * w * s))


def psi_at(phi: float, spec: dict[str, Any]) -> float:
    dyn = spec.get("dynamics") or {}
    orient = str(dyn.get("orientation", "circumferential"))
    if orient == "helical":
        return windings(spec) * float(phi)
    return 0.0
