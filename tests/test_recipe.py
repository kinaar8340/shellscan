"""Recipe sidecar. Software facts of counts, isometry, wrap. No GPU."""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from recipe.archimedean import (  # noqa: E402
    FAMILY_TABLE,
    POLYOMA_T7,
    ck_counts,
    family_counts,
    triangulation_number,
)
from recipe.compile import compile_recipe, load_recipe  # noqa: E402
from recipe.setal import compare_painted, load_setal_table, table_xyz  # noqa: E402
from recipe.yaml_lite import load_simple_yaml  # noqa: E402
from recipe.geodesic import ck_triangles, geodesic_polyhedron  # noqa: E402
from recipe.goldberg import goldberg_dual  # noqa: E402
from recipe.helicoid_catenoid import (  # noqa: E402
    PI_2,
    first_fundamental_form,
    sampled_isometry_error,
)
from recipe.wrap import parse_field, rgb_preview  # noqa: E402

SECTIONS = {"elliptic", "parabolic", "hyperbolic", "flat-pockets"}
TABLE = (
    ((1, 0), "I", 1, 12, 20, 12),
    ((2, 0), "I", 4, 42, 80, 42),
    ((3, 0), "I", 9, 92, 180, 92),
    ((1, 1), "II", 3, 32, 60, 32),
    ((2, 1), "III", 7, 72, 140, 72),
)


def test_triangulation_number_and_class():
    for (m, n), cls, t, *_ in TABLE:
        c = ck_counts(m, n)
        assert c["T"] == t == triangulation_number(m, n)
        assert c["class"] == cls
        assert c["pentagons"] == 12
        assert c["hexagons"] == 10 * (t - 1)
        assert c["subunits_60T"] == 60 * t
        assert c["geodesic_V"] == 10 * t + 2
        assert c["geodesic_F"] == 20 * t
        assert c["goldberg_F"] == 10 * t + 2


def test_ck_triangle_has_T_faces():
    for (m, n), _cls, t, *_ in TABLE:
        assert len(ck_triangles(m, n)) == t


def test_geodesic_and_goldberg_match_wikipedia_table():
    for (m, n), cls, t, v_geo, f_geo, f_gold in TABLE:
        geo = geodesic_polyhedron(m, n)
        gold = goldberg_dual(geo)
        assert geo["class"] == cls
        assert geo["T"] == t
        assert geo["V"] == v_geo
        assert geo["F"] == f_geo
        assert geo["E"] == 30 * t
        assert gold["V"] == f_geo
        assert gold["F"] == f_gold
        assert gold["n_pentagons"] == 12
        assert gold["n_hexagons"] == 10 * (t - 1)
        assert gold["n_other"] == 0


def test_geodesic_stdlib_only():
    import recipe.geodesic as g

    assert "numpy" not in dir(g)
    geo = geodesic_polyhedron(1, 1)
    assert geo["V"] == 32
    assert geo["F"] == 60


def test_class_i_2v_matches_qga_gpu_stamp():
    geo = geodesic_polyhedron(2, 0)
    assert geo["V"] == 42
    assert geo["F"] == 80


def test_class_iii_enantiomorphs_are_distinct():
    a = geodesic_polyhedron(2, 1)
    b = geodesic_polyhedron(1, 2)
    assert a["V"] == b["V"] == 72
    ka = {(round(p[0], 5), round(p[1], 5), round(p[2], 5)) for p in a["verts"]}
    kb = {(round(p[0], 5), round(p[1], 5), round(p[2], 5)) for p in b["verts"]}
    assert ka != kb
    mirror = {(-x, y, z) for x, y, z in ka}
    assert mirror == kb


def test_associate_family_isometry():
    for u, v in ((0.2, 0.4), (1.0, -0.5), (2.5, 1.2)):
        e0, f0, g0 = first_fundamental_form(u, v, 0.0)
        e1, f1, g1 = first_fundamental_form(u, v, PI_2)
        assert e0 == pytest.approx(e1, rel=1e-8, abs=1e-8)
        assert f0 == pytest.approx(f1, rel=1e-8, abs=1e-8)
        assert g0 == pytest.approx(g1, rel=1e-8, abs=1e-8)
    uv = [(0.01 * i, 0.3 * math.sin(0.02 * i)) for i in range(800)]
    assert sampled_isometry_error(uv) < 1e-5


def test_archimedean_dual_tile_counts():
    t = triangulation_number(1, 1)
    assert t == 3
    assert family_counts("hexagonal", 1, 1)["geodesic_F"] == 20 * t
    assert family_counts("trihexagonal", 1, 1)["rhombs"] == 30 * t
    assert family_counts("snub_hexagonal", 1, 1)["florets"] == 60 * t
    assert family_counts("rhombitrihexagonal", 1, 1)["kites"] == 60 * t
    assert set(FAMILY_TABLE) == {
        "hexagonal",
        "trihexagonal",
        "snub_hexagonal",
        "rhombitrihexagonal",
    }


def test_polyoma_exception_numbers():
    assert POLYOMA_T7["observed_pentamers"] == 72
    assert POLYOMA_T7["observed_subunits"] == 360
    assert POLYOMA_T7["caspar_klug_subunits"] == 420


def _compile(name: str, tmp_path: Path) -> dict:
    return compile_recipe(
        ROOT / "recipes" / f"{name}.yaml",
        tmp_path / name,
        render=False,
    )


def test_banded_larva_acceptance(tmp_path: Path):
    meta = _compile("banded-larva", tmp_path)
    assert meta["T"] == 9
    assert meta["n_faces"] == 92
    assert meta["n_pentagons"] == 12
    assert meta["n_hexagons"] == 80
    assert meta["n_bytes"] == 92 * 32
    assert meta["kinds"].get("tentacle") == 4
    blob = (tmp_path / "banded-larva" / "qga_pixel_field.bin").read_bytes()
    recs = parse_field(blob)
    assert len(recs) == 92
    tent_i = set(meta["tentacle_indices"])
    assert len(tent_i) == 4
    for i, rec in enumerate(recs):
        assert rec["section"] in SECTIONS
        assert rec["layer"] == 0
        assert rec["n_bytes"] == 32
        if i in tent_i:
            assert rec["amplitude"] == pytest.approx(1.0)
        rgb_preview(rec["section"], rec["amplitude"], rec["persist"] or 1.0)


def test_hang_chrysalis_same_net_no_bands(tmp_path: Path):
    larva = _compile("banded-larva", tmp_path)
    hang = _compile("hang-chrysalis", tmp_path)
    assert hang["T"] == larva["T"] == 9
    assert hang["n_faces"] == 92
    assert hang["kinds"].get("tentacle", 0) == 0
    assert hang["morph_t"] == 1.0


def test_capsid_t3_caspar_klug(tmp_path: Path):
    meta = _compile("capsid-t3", tmp_path)
    assert meta["T"] == 3
    assert meta["class"] == "II"
    assert meta["kinds"]["pentamer"] == 12
    assert meta["kinds"]["hexamer"] == 20
    assert meta["subunits_60T"] == 180
    blob = (tmp_path / "capsid-t3" / "qga_pixel_field.bin").read_bytes()
    recs = parse_field(blob)
    assert len(recs) == 32
    for rec in recs:
        assert rec["section"] in SECTIONS
        assert rec["layer"] == 0


def test_capsid_t7_and_polyoma_paint(tmp_path: Path):
    ck = _compile("capsid-t7", tmp_path)
    py = _compile("capsid-t7-polyoma", tmp_path)
    assert ck["T"] == py["T"] == 7
    assert ck["n_faces"] == py["n_faces"] == 72
    assert ck["kinds"]["pentamer"] == 12
    assert ck["kinds"]["hexamer"] == 60
    assert ck["subunits_60T"] == 420
    assert py["kinds"]["pentamer"] == 72
    assert py["kinds"].get("hexamer", 0) == 0
    assert (tmp_path / "capsid-t7" / "qga_pixel_field.bin").stat().st_size == 72 * 32


def test_yaml_lite_loads_shipped_recipes():
    for path in sorted((ROOT / "recipes").glob("*.yaml")):
        spec = load_simple_yaml(path.read_text())
        assert spec["name"] == path.stem
        assert "carrier" in spec
        assert "paint" in spec
    larva = load_simple_yaml((ROOT / "recipes" / "banded-larva.yaml").read_text())
    assert larva["carrier"]["m"] == 3
    assert larva["paint"]["bands"]["cycle"] == ["elliptic", "hyperbolic", "elliptic"]
    sings = larva["paint"]["singularities"]
    assert sings[0]["kind"] == "tentacle"
    assert sings[0]["count"] == 2
    assert sings[0]["amplitude"] == pytest.approx(1.0)
    t3 = load_simple_yaml((ROOT / "recipes" / "capsid-t3.yaml").read_text())
    assert t3["paint"]["quasi_equivalence"]["hexamer_offset"] == pytest.approx(0.45)


def test_load_recipe_without_pyyaml(monkeypatch: pytest.MonkeyPatch):
    import recipe.compile as compile_mod

    monkeypatch.setattr(compile_mod, "yaml", None)
    spec = load_recipe(ROOT / "recipes" / "capsid-t3.yaml")
    assert spec["name"] == "capsid-t3"
    assert spec["carrier"]["n"] == 1


def test_setal_table_load_and_snap():
    rows = load_setal_table(ROOT / "recipes" / "setal" / "monarch.csv")
    points = [r for r in rows if r["kind"] == "tentacle"]
    rings = [r for r in rows if r["kind"] == "band"]
    assert len(points) == 4
    assert len(rings) == 8
    xyz = table_xyz(0.0, 0.0)
    assert xyz[2] == pytest.approx(1.0)
    xyz_t = table_xyz(1.0, 0.0)
    assert xyz_t[2] == pytest.approx(-1.0)


def test_monarch_setal_paint(tmp_path: Path):
    meta = _compile("monarch-setal", tmp_path)
    assert meta["T"] == 9
    assert meta["n_faces"] == 92
    assert meta["kinds"].get("tentacle") == 4
    assert meta["table"] == "setal/monarch.csv"
    st = meta["setal"]
    assert st["n_point_rows"] == 4
    assert st["mean_snap_deg"] < 35.0
    log = json.loads((tmp_path / "monarch-setal" / "setal_log.json").read_text())
    tent_faces = {x["face"] for x in log if x["kind"] == "tentacle"}
    assert len(tent_faces) == 4


def test_tussock_setal_paint(tmp_path: Path):
    meta = _compile("tussock-setal", tmp_path)
    assert meta["kinds"].get("tuft") == 4
    assert meta["kinds"].get("tentacle") == 1
    assert meta["setal"]["n_point_rows"] == 5
    assert meta["setal"]["mean_snap_deg"] < 35.0


def test_setal_compare_self(tmp_path: Path):
    _compile("monarch-setal", tmp_path)
    painted = json.loads((tmp_path / "monarch-setal" / "painted.json").read_text())
    cmp = compare_painted(painted, painted)
    assert cmp["section_agree"] == pytest.approx(1.0)
    assert cmp["kind_agree"] == pytest.approx(1.0)


def test_capsid_t3_kite_vs_ck_and_ms2(tmp_path: Path):
    kite = _compile("capsid-t3-kite", tmp_path)
    ck = _compile("capsid-t3", tmp_path)
    ms2 = _compile("capsid-t3-ms2", tmp_path)
    assert kite["n_faces"] == 32
    assert kite["occupancy"]["pentamer"] == 12
    assert kite["occupancy"]["trimer"] == 20
    pk = json.loads((tmp_path / "capsid-t3-kite" / "painted.json").read_text())
    pc = json.loads((tmp_path / "capsid-t3" / "painted.json").read_text())
    pm = json.loads((tmp_path / "capsid-t3-ms2" / "painted.json").read_text())
    vs_ck = compare_painted(pk, pc)
    vs_ms2 = compare_painted(pk, pm)
    assert vs_ck["kind_agree"] == pytest.approx(12 / 32)
    assert vs_ms2["kind_agree"] == pytest.approx(12 / 32)
    assert vs_ck["section_agree"] == pytest.approx(1.0)
    assert vs_ms2["section_agree"] == pytest.approx(12 / 32)


def test_capsid_t3_ms2_dimer_vs_ck(tmp_path: Path):
    ms2 = _compile("capsid-t3-ms2", tmp_path)
    ck = _compile("capsid-t3", tmp_path)
    assert ms2["n_faces"] == ck["n_faces"] == 32
    assert ms2["occupancy"]["pentamer"] == 12
    assert ms2["occupancy"]["dimer"] == 20
    assert ms2["occupancy"]["hexamer"] == 0
    pa = json.loads((tmp_path / "capsid-t3-ms2" / "painted.json").read_text())
    pb = json.loads((tmp_path / "capsid-t3" / "painted.json").read_text())
    cmp = compare_painted(pa, pb)
    assert cmp["kind_agree"] == pytest.approx(12 / 32)
    assert cmp["section_agree"] == pytest.approx(12 / 32)


def test_capsid_t7_p22_portal_one_face(tmp_path: Path):
    portal = _compile("capsid-t7-p22-portal", tmp_path)
    ck = _compile("capsid-t7", tmp_path)
    occ = portal["occupancy"]
    assert occ["portal"] == 1
    assert occ["pentamer"] == 11
    assert occ["hexamer"] == 60
    assert len(occ["portal_faces"]) == 1
    pa = json.loads((tmp_path / "capsid-t7-p22-portal" / "painted.json").read_text())
    pb = json.loads((tmp_path / "capsid-t7" / "painted.json").read_text())
    cmp = compare_painted(pa, pb)
    assert cmp["kind_agree"] == pytest.approx(71 / 72)
    assert pa[occ["portal_faces"][0]]["kind"] == "portal"
    assert pa[occ["portal_faces"][0]]["section"] == "parabolic"


def test_capsid_t7_p22_occupancy(tmp_path: Path):
    p22 = _compile("capsid-t7-p22", tmp_path)
    ck = _compile("capsid-t7", tmp_path)
    occ = p22["occupancy"]
    assert occ["T"] == 7
    assert occ["pentamer"] == 12
    assert occ["hexamer"] == 60
    assert occ["subunits_60T"] == 420
    pa = json.loads((tmp_path / "capsid-t7-p22" / "painted.json").read_text())
    pb = json.loads((tmp_path / "capsid-t7" / "painted.json").read_text())
    cmp = compare_painted(pa, pb)
    assert cmp["kind_agree"] == pytest.approx(1.0)
    py = _compile("capsid-t7-polyoma", tmp_path)
    assert py["occupancy"]["pentamer"] == 72
    assert py["occupancy"]["hexamer"] == 0


def test_polyxenes_extrafamilial_order(tmp_path: Path):
    meta = _compile("setal-polyxenes-cylinder", tmp_path)
    h = meta["homology"]
    assert h["cluster_pure"] is True
    assert h["phi_order_ok"] is True
    means = h["phi_means"]
    assert means["D"] < means["SD"] < means["L"] < means["SV"] < means["V"]
    assert means["SD"] > 60.0
    d1 = h["homologs"]["D1"]
    assert d1["std_phi_deg"] < 10.0
    assert meta["n_faces"] == 468


def test_melpomene_outgroup_order(tmp_path: Path):
    meta = _compile("setal-melpomene-cylinder", tmp_path)
    h = meta["homology"]
    assert h["cluster_pure"] is True
    means = h["phi_means"]
    assert means["D"] < means["SD"] < means["L"] < means["SV"] < means["V"]
    assert h["phi_order_ok"] is True
    assert means["SD"] > 60.0
    d1 = h["homologs"]["D1"]
    assert d1["std_phi_deg"] < 10.0
    assert d1["std_shell_s"] == pytest.approx(0.2516, rel=0.05)


def test_plexippus_abdomen_L2_isoline(tmp_path: Path):
    meta = _compile("setal-plexippus-cylinder", tmp_path)
    l2 = meta["homology"]["homologs"]["L2"]
    assert l2["std_phi_deg"] > 8.0
    assert l2["abdomen"]["std_phi_deg"] == pytest.approx(0.0, abs=1e-9)
    assert l2["abdomen"]["n"] == 4


def test_plexippus_measured_phi(tmp_path: Path):
    meta = _compile("setal-plexippus-cylinder", tmp_path)
    assert meta["kind"] == "cylinder"
    h = meta["homology"]
    assert h["cluster_pure"] is True
    assert h["axial_hue_pure"] is True
    assert h["phi_order_ok"] is True
    d1 = h["homologs"]["D1"]
    assert d1["std_phi_deg"] < 10.0
    assert d1["shell_s_range"] > 0.2
    means = h["phi_means"]
    assert means["D"] < means["SD"] < means["L"] < means["SV"] < means["V"]
    from recipe.setal import twist_scan

    scan = twist_scan("setal-plexippus-cylinder")
    rows = scan["twists"]
    assert rows[1]["embed_phi_order_ok"] is True
    assert rows[2]["embed_phi_order_ok"] is False


def test_hinton_helicoid_chart_vs_embed(tmp_path: Path):
    meta = _compile("setal-hinton-helicoid", tmp_path)
    assert meta["kind"] == "cylinder"
    h = meta["homology"]
    assert h["phi_order_ok"] is True
    assert h["cluster_pure"] is True
    d1 = h["homologs"]["D1"]
    assert d1["std_phi_deg"] < 8.0
    assert d1["std_phi_embed"] > d1["std_phi_deg"] + 5.0


def test_twist_scan_chart_stable():
    from recipe.setal import twist_scan

    out = twist_scan("setal-hinton-cylinder")
    rows = out["twists"]
    assert [round(r["twist"], 5) for r in rows] == [
        0.0,
        round(math.pi / 4, 5),
        round(math.pi / 2, 5),
        round(math.pi, 5),
    ]
    for r in rows:
        assert r["phi_order_ok"] is True
        assert r["D1_std_phi_chart"] == pytest.approx(0.0, abs=1e-9)
        assert r["D1_std_phi_embed"] == pytest.approx(r["D1_std_phi_embed_pred"], rel=1e-6, abs=1e-6)
    assert rows[0]["embed_phi_order_ok"] is True
    assert rows[1]["embed_phi_order_ok"] is True
    assert rows[2]["embed_phi_order_ok"] is False
    assert rows[3]["embed_phi_order_ok"] is False


def test_danaus_gilippus_extra_A2(tmp_path: Path):
    meta = _compile("setal-danaus-gilippus", tmp_path)
    assert meta["homology"]["n_sites"] == 70
    assert meta["kinds"].get("tentacle") == 6
    assert meta["homology"]["phi_order_ok"] is True
    assert meta["homology"]["homologs"]["D1"]["std_phi_deg"] < 8.0
    log = json.loads((tmp_path / "setal-danaus-gilippus" / "setal_log.json").read_text())
    assert {x["id"] for x in log if x.get("segment") == "A2"} >= {"A2-tentacle1", "A2-tentacle2"}


def test_hinton_cylinder_phi_order(tmp_path: Path):
    meta = _compile("setal-hinton-cylinder", tmp_path)
    assert meta["kind"] == "cylinder"
    assert meta.get("n_pentagons") == 0
    assert meta["n_faces"] == 13 * 36
    assert meta["kinds"].get("tentacle") == 4
    h = meta["homology"]
    assert h["n_sites"] == 68
    assert h["cluster_pure"] is True
    assert h["axial_hue_pure"] is True
    assert h["phi_order_ok"] is True
    means = h["phi_means"]
    assert means["D"] < means["SD"] < means["L"] < means["SV"] < means["V"]
    d1 = h["homologs"]["D1"]
    assert d1["n"] == 6
    assert d1["std_phi_deg"] < 8.0
    assert d1["shell_s_range"] > 0.2


def test_hinton_sites_homology(tmp_path: Path):
    meta = _compile("setal-hinton", tmp_path)
    assert meta["T"] == 9
    assert meta["n_faces"] == 92
    assert meta["kinds"].get("tentacle") == 4
    assert meta["kinds"].get("spiracle") == 4
    h = meta["homology"]
    assert h["n_sites"] == 68
    assert h["cluster_pure"] is True
    assert h["axial_hue_pure"] is True
    d1 = h["homologs"]["D1"]
    assert d1["n"] == 6
    assert d1["section_pure"] is True
    assert d1["shell_s_range"] > 0.05
    assert set(h["groups"]["D"]["sections"]) == {"elliptic"}
    assert set(h["groups"]["L"]["sections"]) == {"hyperbolic"}
    assert set(h["groups"]["SD"]["sections"]) == {"parabolic"}
    assert isinstance(h["phi_order_ok"], bool)
    log = json.loads((tmp_path / "setal-hinton" / "setal_log.json").read_text())
    ids = {x["id"] for x in log}
    assert "T1-XD1" in ids
    assert "A6-V1" in ids


def test_setal_compare_vs_banded_larva(tmp_path: Path):
    a = _compile("monarch-setal", tmp_path)
    b = _compile("banded-larva", tmp_path)
    pa = json.loads((tmp_path / "monarch-setal" / "painted.json").read_text())
    pb = json.loads((tmp_path / "banded-larva" / "painted.json").read_text())
    cmp = compare_painted(pa, pb)
    assert a["n_faces"] == b["n_faces"] == cmp["n_faces"] == 92
    assert cmp["kinds_a"]["tentacle"] == cmp["kinds_b"]["tentacle"] == 4


def test_does_not_touch_pick_blob(tmp_path: Path):
    pick = ROOT / "output" / "pick" / "qga_pixel.bin"
    before = pick.read_bytes() if pick.is_file() else None
    _compile("banded-larva", tmp_path)
    after = pick.read_bytes() if pick.is_file() else None
    assert before == after
