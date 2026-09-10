"""Caspar–Klug T-number, Goldberg counts, Twarock–Luque 2019 families.

Theorem (cited): T = m² + mn + n². Icosahedral close of a hexagonal
sublattice by 12 pentagons. Four Archimedean parents admit that move;
their four Laves duals are the tile sets of viral tiling theory.

This module is counts and labels. Geometry for the hexagonal parent and
its triangular dual lives in geodesic.py / goldberg.py. The other six
families are enumerated, not generated, in v1.
"""

from __future__ import annotations

from typing import Any


def triangulation_number(m: int, n: int) -> int:
    m, n = int(m), int(n)
    if m < 0 or n < 0 or (m == 0 and n == 0):
        raise ValueError(f"need m,n ≥ 0, not both 0; got {(m, n)}")
    return m * m + m * n + n * n


def hex_class(m: int, n: int) -> str:
    """Class I: one index vanishes. II: m=n. III: both nonzero and unequal."""
    m, n = int(m), int(n)
    triangulation_number(m, n)
    if m == 0 or n == 0:
        return "I"
    if m == n:
        return "II"
    return "III"


def ck_counts(m: int, n: int) -> dict[str, int | str]:
    """Hexagonal parent closed by 12 pentagons. Caspar–Klug / Goldberg."""
    t = triangulation_number(m, n)
    hexamers = 10 * (t - 1)
    return {
        "m": int(m),
        "n": int(n),
        "T": t,
        "class": hex_class(m, n),
        "geodesic_V": 10 * t + 2,
        "geodesic_E": 30 * t,
        "geodesic_F": 20 * t,
        "goldberg_V": 20 * t,
        "goldberg_E": 30 * t,
        "goldberg_F": 10 * t + 2,
        "pentagons": 12,
        "hexagons": hexamers,
        "pentamers": 12,
        "hexamers": hexamers,
        "subunits_60T": 60 * t,
    }


# Twarock & Luque 2019: four Archimedean parents that contain a hexagonal
# sublattice, plus their four Laves duals. Dual tile counts are the
# software-fact formulas from that paper / the recipe thread.
FAMILY_TABLE: dict[str, dict[str, Any]] = {
    "hexagonal": {
        "vertex_figure": "6.6.6",
        "also": "hextille",
        "extra_in_ck_triangle": "none",
        "role": "Caspar–Klug parent; Goldberg hex+pent shell",
        "dual": "triangular",
        "dual_also": "deltille",
        "dual_tile": "triangle",
        "dual_tile_count_name": "geodesic_F",
        "dual_tiles": lambda t: 20 * t,
        "represents": "classical CK subunit / geodesic facet",
    },
    "trihexagonal": {
        "vertex_figure": "3.6.3.6",
        "also": "hexadeltille, kagome",
        "extra_in_ck_triangle": "1 triangle",
        "role": "minor capsid proteins / second conformational class",
        "dual": "rhombille",
        "dual_also": "Laves dual of 3.6.3.6",
        "dual_tile": "rhomb",
        "dual_tile_count_name": "rhombs",
        "dual_tiles": lambda t: 30 * t,
        "represents": "dimer (two proteins); MS2-like",
    },
    "snub_hexagonal": {
        "vertex_figure": "3^4.6",
        "also": "snub hextille",
        "extra_in_ck_triangle": "4 triangles (chiral)",
        "role": "chiral extra triangles on the hexagonal sublattice",
        "dual": "floret_pentagonal",
        "dual_also": "floret",
        "dual_tile": "floret",
        "dual_tile_count_name": "florets",
        "dual_tiles": lambda t: 60 * t,
        "represents": "more complex local cluster",
    },
    "rhombitrihexagonal": {
        "vertex_figure": "3.4.6.4",
        "also": "rhombihexadeltille",
        "extra_in_ck_triangle": "1 triangle + 1/2 square",
        "role": "major-plus-minor layouts; herpes-like",
        "dual": "deltoidal_trihexagonal",
        "dual_also": "kite / deltoid",
        "dual_tile": "kite",
        "dual_tile_count_name": "kites",
        "dual_tiles": lambda t: 60 * t,
        "represents": "trimer or three-domain protomer; Papovaviridae VTT",
    },
}


def family_counts(name: str, m: int, n: int) -> dict[str, Any]:
    if name not in FAMILY_TABLE:
        raise KeyError(f"unknown family {name!r}; expected {tuple(FAMILY_TABLE)}")
    spec = FAMILY_TABLE[name]
    t = triangulation_number(m, n)
    out = ck_counts(m, n)
    out["family"] = name
    out["vertex_figure"] = spec["vertex_figure"]
    out["dual"] = spec["dual"]
    out["dual_tile"] = spec["dual_tile"]
    out[spec["dual_tile_count_name"]] = spec["dual_tiles"](t)
    return out


# Common biological T-values (cited, not generated from photos).
COMMON_T = (1, 3, 4, 7, 9, 13, 16)

# (h,k) pairs that realize those T as the least Class I/II/III labels.
COMMON_HK = {
    1: (1, 0),
    3: (1, 1),
    4: (2, 0),
    7: (2, 1),
    9: (3, 0),
    13: (3, 1),
    16: (4, 0),
}

# Polyoma / papilloma: 72 pentamers on a T=7 lattice, 360 subunits, not 420.
POLYOMA_T7 = {
    "T": 7,
    "hk": (2, 1),
    "caspar_klug_subunits": 420,
    "caspar_klug_hexamers": 60,
    "observed_pentamers": 72,
    "observed_hexamers": 0,
    "observed_subunits": 360,
    "note": "hexavalent sites occupied by pentamers; VTT kite/rhomb, not CK type",
}
