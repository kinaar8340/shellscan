"""T=3 field strip. Software facts of bins, lerp, masks, duration. No GPU."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from recipe.compile import compile_recipe  # noqa: E402
from recipe.film import (  # noqa: E402
    BIN_ORDER,
    FPS,
    NAMES,
    SHOTS,
    classify_section,
    duration_seconds,
    face_colors,
    lerp_preview,
    plane_state,
    run_film,
    shot_frame_count,
    shot_u,
    timeline,
)
from recipe.wrap import rgb_preview  # noqa: E402
from recipe.setal import compare_painted  # noqa: E402


def test_duration_is_sixty_seconds():
    assert duration_seconds() == pytest.approx(60.0)
    assert sum(shot_frame_count(s["seconds"], False) for s in SHOTS) == 60 * FPS
    assert len(timeline(preview=False)) == 1440
    assert len(timeline(preview=True)) == len(SHOTS)
    assert [s["id"] for s in SHOTS][:3] == ["title", "plane", "ck"]
    assert SHOTS[-1]["id"] == "end"
    assert shot_u(0, 1, at_end=True) == 1.0
    assert shot_u(0, 1, at_end=False) == 0.0
    assert shot_u(0, 10) == 0.0
    assert shot_u(9, 10) == 1.0


def test_classify_section_four_bins():
    assert classify_section((0.0, 0.0, 1.0), 0.4) == "elliptic"
    n_para = (GENERATOR := 0.5**0.5, 0.0, GENERATOR)
    assert classify_section(n_para, 0.4) == "parabolic"
    assert classify_section((1.0, 0.0, 0.0), 0.4) == "hyperbolic"
    assert classify_section((0.0, 0.0, 1.0), 0.0) == "flat-pockets"
    assert set(BIN_ORDER) == {"elliptic", "parabolic", "hyperbolic", "flat-pockets"}


def test_plane_tilt_lights_bins_in_order():
    seen = []
    for k in range(49):
        _n, _off, section = plane_state(k / 48.0)
        if not seen or seen[-1] != section:
            seen.append(section)
    assert seen[0] == "elliptic"
    assert "parabolic" in seen
    assert "hyperbolic" in seen
    assert seen[-1] == "flat-pockets"
    assert seen == [s for s in BIN_ORDER if s in seen]
    assert plane_state(0.12)[2] == "elliptic"
    assert plane_state(0.37)[2] == "parabolic"
    assert plane_state(0.62)[2] == "hyperbolic"
    assert plane_state(0.95)[2] == "flat-pockets"


def test_lerp_preview_endpoints_and_no_fifth():
    a = {"section": "hyperbolic", "amplitude": 1.0, "persist": 1.0}
    b = {"section": "parabolic", "amplitude": 1.0, "persist": 1.0}
    assert lerp_preview(a, b, 0.0) == rgb_preview("hyperbolic", 1.0, 1.0)
    assert lerp_preview(a, b, 1.0) == rgb_preview("parabolic", 1.0, 1.0)
    mid = lerp_preview(a, b, 0.5)
    ha = rgb_preview("hyperbolic", 1.0, 1.0)
    pb = rgb_preview("parabolic", 1.0, 1.0)
    assert mid[0] == pytest.approx(0.5 * (ha[0] + pb[0]))
    assert mid not in (ha, pb)


def test_persist_darkens_without_new_byte():
    full = rgb_preview("elliptic", 1.0, 1.0)
    dim = rgb_preview("elliptic", 1.0, 0.2)
    assert all(d < f for d, f in zip(dim, full))


def test_blank_and_nappe_masks():
    recs = [
        {"section": "elliptic", "amplitude": 1.0, "persist": 1.0},
        {"section": "hyperbolic", "amplitude": 1.0, "persist": 1.0},
    ]
    blank = face_colors(recs, mask="blank")
    assert blank[0][0] == blank[0][1] == blank[0][2] == pytest.approx(0.0)
    assert blank[1][0] == pytest.approx(0.0)
    nappe = face_colors(recs, mask="nappe")
    assert nappe[0][3] == pytest.approx(0.0)
    hyp = rgb_preview("hyperbolic", 1.0, 1.0)
    assert nappe[1][:3] == pytest.approx(hyp)
    assert nappe[1][3] > 0.5


def test_rhombille_compare_refused_on_face_count(tmp_path: Path):
    rh = compile_recipe(
        ROOT / "recipes" / "capsid-t3-rhomb30.yaml", tmp_path / "rh", render=False
    )
    ck = compile_recipe(
        ROOT / "recipes" / "capsid-t3.yaml", tmp_path / "ck", render=False
    )
    assert rh["F"] == 90
    assert ck["F"] == 32
    with pytest.raises(ValueError, match="face counts"):
        compare_painted(
            [{"section": "parabolic", "kind": "dimer"}] * 90,
            [{"section": "elliptic", "kind": "pentamer"}] * 32,
        )


def test_film_preview_keyframes(tmp_path: Path):
    pytest.importorskip("matplotlib")
    for name in NAMES.values():
        compile_recipe(ROOT / "recipes" / f"{name}.yaml", tmp_path / name, render=False)
    meta = run_film(
        outdir=tmp_path / "film",
        dump_root=tmp_path,
        preview=True,
        encode=False,
    )
    assert meta["n_frames"] == len(SHOTS)
    assert meta["title"] == "T=3 field strip"
    assert meta["not"] == "Animation A"
    assert meta["faceplate"] == "unused"
    assert meta["gamma"] is False
    assert meta["compare"]["ck_kite"]["section_agree"] == pytest.approx(1.0)
    assert meta["compare"]["ck_kite"]["kind_agree"] == pytest.approx(12 / 32)
    assert meta["compare"]["rhombille"] == "compare-refused"
    assert (tmp_path / "film" / "frames" / "frame_0000.png").is_file()
    assert (tmp_path / "film" / "frames" / f"frame_{len(SHOTS) - 1:04d}.png").is_file()
    assert meta["claim"] == "Model + Software fact"
