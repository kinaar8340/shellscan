"""Cylinder isoline strip. Hypothesis. No capsid paints. No GPU."""

from __future__ import annotations

import math
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from recipe.film import (  # noqa: E402
    CYL_SHOTS,
    CYLINDER_RECIPE,
    EMBED_ORDER_BOUND,
    FPS,
    cyl_duration_seconds,
    paint_cylinder,
    run_cylinder_film,
    shot_frame_count,
    site_colors,
    twist_card,
    twist_values,
)


def test_cyl_duration_sixty():
    assert cyl_duration_seconds() == pytest.approx(60.0)
    assert sum(shot_frame_count(s["seconds"], False) for s in CYL_SHOTS) == 60 * FPS


def test_cylinder_recipe_is_not_a_capsid():
    assert "capsid" not in CYLINDER_RECIPE
    assert CYLINDER_RECIPE.startswith("setal-")
    ids = [s["id"] for s in CYL_SHOTS]
    assert "t1_walk" in ids
    assert "twist" in ids
    joined = " ".join(ids)
    assert "capsid" not in joined
    assert "kite" not in joined
    assert "ms2" not in joined
    assert "rhomb" not in joined


def test_site_colors_blank_plains_and_keep_groups():
    recs = [
        {"kind": "plain", "section": "elliptic", "amplitude": 1.0, "persist": 1.0},
        {
            "kind": "seta",
            "section": "parabolic",
            "amplitude": 1.0,
            "persist": 1.0,
            "setal_group": "SD",
            "seta": "SD1",
        },
        {
            "kind": "seta",
            "section": "hyperbolic",
            "amplitude": 1.0,
            "persist": 1.0,
            "setal_group": "L",
            "seta": "L2",
        },
    ]
    all_sites = site_colors(recs)
    assert all_sites[0][3] == pytest.approx(0.0)
    assert all_sites[1][3] > 0.5
    only_l2 = site_colors(recs, seta="L2")
    assert only_l2[1][3] == pytest.approx(0.0)
    assert only_l2[2][3] > 0.5
    only_sd = site_colors(recs, groups={"SD"})
    assert only_sd[1][3] > 0.5
    assert only_sd[2][3] == pytest.approx(0.0)


def test_twist_collides_after_bound():
    _net, recs, h0 = paint_cylinder(0.0)
    assert h0["phi_order_ok"] is True
    assert h0["embed_phi_order_ok"] is True
    assert h0["phi_means"]["D"] < h0["phi_means"]["SD"]
    occupied = [r for r in recs if r.get("kind") != "plain"]
    assert occupied
    assert all(r.get("setal_group") for r in occupied)
    l2 = [r for r in occupied if r.get("seta") == "L2"]
    assert len(l2) >= 4
    t1 = [r for r in l2 if r.get("segment") == "T1"]
    abd = [r for r in l2 if str(r.get("segment") or "").startswith("A")]
    assert t1 and abd
    _n1, _r1, h1 = paint_cylinder(math.pi / 4.0)
    assert h1["embed_phi_order_ok"] is True
    _n2, _r2, h2 = paint_cylinder(0.94)
    assert h2["phi_order_ok"] is True
    assert h2["embed_phi_order_ok"] is False


def test_twist_values_preview_is_collide():
    assert twist_values(1, True) == [0.94]


def test_twist_card_number_matches_frame():
    """π/4 is the dump bound, not the live angle. Same rule as the kite card."""
    assert EMBED_ORDER_BOUND == pytest.approx(math.pi / 4.0)
    t46, e46 = twist_card(0.46, False)
    assert "0.46" in e46
    assert "π/4" not in e46
    assert "bound" not in e46
    t91, e91 = twist_card(0.91, False)
    assert "0.91" in e91
    assert "π/4" not in e91
    assert t46 == t91 == "chart φ holds · embed shears"
    tc, ec = twist_card(0.94, True)
    assert tc == "embed D/SD collide"
    assert "π/4" in ec
    assert "0.94" in ec
    assert "shear is not a paint" in ec


def test_cylinder_preview_keyframes(tmp_path: Path):
    pytest.importorskip("matplotlib")
    meta = run_cylinder_film(outdir=tmp_path, preview=True, encode=False)
    assert meta["n_frames"] == len(CYL_SHOTS)
    assert meta["title"] == "cylinder isoline"
    assert meta["claim"] == "Hypothesis"
    assert meta["capsid"] is False
    assert meta["faceplate"] == "unused"
    assert meta["gamma"] is False
    assert meta["t1_walk"] == "L2 one 10° bin"
    assert (tmp_path / "cyl_frames" / "frame_0000.png").is_file()
