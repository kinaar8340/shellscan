"""Setal-position table → nearest-face paint. Hypothesis, not a developmental proof.

A photograph is digitized by hand into this CSV. Automatic vision is a
different claim. Chart: s=0 anterior (+z), s=1 posterior (−z); phi_deg
around the body. Empty phi on a band row paints a ring.
"""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from typing import Any

from .goldberg import face_centroid

SECTIONS = ("elliptic", "parabolic", "hyperbolic", "flat-pockets")
KINDS = ("seta", "tuft", "tentacle", "band", "spine", "spiracle")
HUE_ALIAS = {
    "elliptic": "elliptic",
    "parabolic": "parabolic",
    "gold": "parabolic",
    "hyperbolic": "hyperbolic",
    "flat": "flat-pockets",
    "flat-pockets": "flat-pockets",
    "magenta": "flat-pockets",
}
SEGMENTS = (
    "T1",
    "T2",
    "T3",
    "A1",
    "A2",
    "A3",
    "A4",
    "A5",
    "A6",
    "A7",
    "A8",
    "A9",
    "A10",
)
GROUP_ORDER = ("D", "SD", "L", "SV", "V")


def _section(name: str) -> str:
    key = HUE_ALIAS.get(str(name), str(name))
    if key not in SECTIONS:
        raise ValueError(f"section {name!r} not in {SECTIONS} / {tuple(HUE_ALIAS)}")
    return key


def segment_s(segment: str) -> float:
    """Axial chart: T1 anterior → s≈0, A10 posterior → s≈1. Cylinder unroll."""
    if segment not in SEGMENTS:
        raise ValueError(f"segment {segment!r} not in {SEGMENTS}")
    i = SEGMENTS.index(segment)
    return (i + 0.5) / len(SEGMENTS)


def _shell_s(c: tuple[float, float, float]) -> float:
    return 0.5 * (c[2] + 1.0)
CHART_PHI = {
    "dorsal": 0.0,
    "subdorsal": 45.0,
    "lateral": 90.0,
    "ventral": 180.0,
}


def load_setal_table(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(newline="") as f:
        text = f.read().splitlines()
    lines = [ln for ln in text if ln.strip() and not ln.lstrip().startswith("#")]
    if not lines:
        raise ValueError(f"empty setal table {path}")
    reader = csv.DictReader(lines)
    required = {"id", "kind", "s"}
    if reader.fieldnames is None or not required.issubset(set(reader.fieldnames)):
        raise ValueError(f"{path} needs columns {sorted(required)}")
    for raw in reader:
        kind = str(raw.get("kind", "")).strip()
        if kind not in KINDS:
            raise ValueError(f"kind {kind!r} not in {KINDS}")
        s = float(raw["s"])
        if not 0.0 <= s <= 1.0:
            raise ValueError(f"s={s} not in [0,1] for {raw.get('id')}")
        phi_raw = (raw.get("phi_deg") or "").strip()
        width_raw = (raw.get("width") or "").strip()
        amp_raw = (raw.get("amplitude") or "").strip()
        sec_raw = (raw.get("section") or "").strip()
        psi_raw = (raw.get("psi") or "").strip()
        chart = str(raw.get("chart") or "").strip() or None
        phi: float | None
        if phi_raw in ("", "*", "ring"):
            phi = None
        else:
            phi = float(phi_raw)
        if phi is None and kind != "band":
            if chart in CHART_PHI:
                phi = CHART_PHI[chart]
            else:
                raise ValueError(f"{raw.get('id')} needs phi_deg or a named chart")
        section = _section(sec_raw) if sec_raw else ("parabolic" if kind in ("tentacle", "tuft", "spine") else "elliptic")
        rows.append(
            {
                "id": str(raw.get("id") or f"row{len(rows)}"),
                "kind": kind,
                "segment": str(raw.get("segment") or "") or None,
                "chart": chart,
                "s": s,
                "phi_deg": phi,
                "amplitude": float(amp_raw) if amp_raw else 1.0,
                "section": section,
                "width": float(width_raw) if width_raw else 0.08,
                "psi": float(psi_raw) if psi_raw else 0.0,
            }
        )
    return rows


def table_xyz(s: float, phi_deg: float) -> tuple[float, float, float]:
    """s=0 anterior (+z), s=1 posterior (−z). Unit sphere."""
    z = max(-1.0, min(1.0, 1.0 - 2.0 * s))
    rxy = math.sqrt(max(0.0, 1.0 - z * z))
    phi = math.radians(phi_deg)
    return (rxy * math.cos(phi), rxy * math.sin(phi), z)


def _dist2(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    dx, dy, dz = a[0] - b[0], a[1] - b[1], a[2] - b[2]
    return dx * dx + dy * dy + dz * dz


def _angle_deg(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    na = math.sqrt(a[0] * a[0] + a[1] * a[1] + a[2] * a[2]) or 1.0
    nb = math.sqrt(b[0] * b[0] + b[1] * b[1] + b[2] * b[2]) or 1.0
    d = (a[0] * b[0] + a[1] * b[1] + a[2] * b[2]) / (na * nb)
    return math.degrees(math.acos(max(-1.0, min(1.0, d))))


def nearest_face(
    cents: list[tuple[float, float, float]], xyz: tuple[float, float, float]
) -> tuple[int, float]:
    return nearest_unused_face(cents, xyz, set())


def nearest_unused_face(
    cents: list[tuple[float, float, float]],
    xyz: tuple[float, float, float],
    taken: set[int],
) -> tuple[int, float]:
    order = sorted(range(len(cents)), key=lambda i: _dist2(cents[i], xyz))
    for i in order:
        if i not in taken:
            return i, _angle_deg(cents[i], xyz)
    i = order[0]
    return i, _angle_deg(cents[i], xyz)


def assign_setal(
    net: dict[str, Any], rows: list[dict[str, Any]]
) -> tuple[dict[int, dict[str, Any]], list[dict[str, Any]]]:
    """Map table rows onto faces. Rings first, point sites overwrite.

    Returns (face_index → assignment, log of every row).
    """
    cents = [face_centroid(net, f) for f in net["faces"]]
    face_s = [_shell_s(c) for c in cents]
    assigned: dict[int, dict[str, Any]] = {}
    log: list[dict[str, Any]] = []

    def write_face(i: int, row: dict[str, Any], snap_deg: float, how: str) -> None:
        prev = assigned.get(i)
        rec = {
            "id": row["id"],
            "kind": row["kind"],
            "section": row["section"],
            "amplitude": row["amplitude"],
            "psi": row["psi"],
            "snap_deg": snap_deg,
            "how": how,
            "group": row.get("group"),
            "seta": row.get("seta"),
            "segment": row.get("segment"),
            "phi_deg": row.get("phi_deg"),
        }
        collision = prev is not None and prev.get("id") != row["id"]
        if prev is None or row["amplitude"] >= prev.get("amplitude", 0.0):
            assigned[i] = rec
        log.append(
            {
                "id": row["id"],
                "kind": row["kind"],
                "face": i,
                "snap_deg": snap_deg,
                "how": how,
                "collision": collision,
                "group": row.get("group"),
                "seta": row.get("seta"),
                "segment": row.get("segment"),
                "phi_deg": row.get("phi_deg"),
            }
        )

    rings = [r for r in rows if r["kind"] == "band" and r["phi_deg"] is None]
    points = [r for r in rows if not (r["kind"] == "band" and r["phi_deg"] is None)]

    if net.get("kind") == "cylinder" and net.get("face_chart"):
        from .cylinder import dphi_deg, phi_bin

        n_phi = int(net["n_phi"])
        segs: list[str] = list(net["segments"])
        chart = net["face_chart"]
        taken_c: set[int] = set()
        for row in points:
            seg = str(row.get("segment") or "")
            if seg in segs:
                i_seg = segs.index(seg)
            else:
                i_seg = min(
                    range(len(segs)),
                    key=lambda k: abs(chart[k * n_phi][0] - float(row["s"])),
                )
            i_phi = phi_bin(float(row["phi_deg"]), n_phi)
            chosen: int | None = None
            snap = 0.0
            for delta in range(n_phi):
                for sign in (0,) if delta == 0 else (1, -1):
                    j = (i_phi + sign * delta) % n_phi
                    fi = i_seg * n_phi + j
                    if fi in taken_c:
                        continue
                    taken_c.add(fi)
                    snap = dphi_deg(float(row["phi_deg"]), chart[fi][1])
                    chosen = fi
                    break
                if chosen is not None:
                    break
            if chosen is None:
                chosen = i_seg * n_phi + i_phi
                snap = dphi_deg(float(row["phi_deg"]), chart[chosen][1])
            write_face(chosen, row, snap, "nearest")
        return assigned, log

    for row in rings:
        target_s = 1.0 - row["s"]
        width = row["width"]
        n_hit = 0
        for i, fs in enumerate(face_s):
            if abs(fs - target_s) <= width:
                write_face(i, row, abs(fs - target_s) * 180.0, "ring")
                n_hit += 1
        if n_hit == 0:
            # snap the closest ring of faces by s
            i = min(range(len(face_s)), key=lambda k: abs(face_s[k] - target_s))
            write_face(i, row, abs(face_s[i] - target_s) * 180.0, "ring-nearest")

    taken: set[int] = set()
    for row in points:
        xyz = table_xyz(row["s"], float(row["phi_deg"]))
        i, ang = nearest_unused_face(cents, xyz, taken)
        taken.add(i)
        write_face(i, row, ang, "nearest")

    return assigned, log


def setal_stats(log: list[dict[str, Any]], assigned: dict[int, dict[str, Any]]) -> dict[str, Any]:
    snaps = [x["snap_deg"] for x in log if x["how"] == "nearest"]
    return {
        "n_rows": len(log),
        "n_assigned_faces": len(assigned),
        "n_point_rows": sum(1 for x in log if x["how"] == "nearest"),
        "n_collisions": sum(1 for x in log if x["collision"]),
        "mean_snap_deg": (sum(snaps) / len(snaps)) if snaps else 0.0,
        "max_snap_deg": max(snaps) if snaps else 0.0,
        "kinds": _count(x["kind"] for x in assigned.values()),
    }


def compare_painted(
    a: list[dict[str, Any]], b: list[dict[str, Any]]
) -> dict[str, Any]:
    if len(a) != len(b):
        raise ValueError(f"face counts differ: {len(a)} vs {len(b)}")
    n = len(a)
    sec = sum(1 for i in range(n) if a[i]["section"] == b[i]["section"])
    kind = sum(1 for i in range(n) if a[i]["kind"] == b[i]["kind"])
    return {
        "n_faces": n,
        "section_agree": sec / n if n else 0.0,
        "kind_agree": kind / n if n else 0.0,
        "kinds_a": _count(x["kind"] for x in a),
        "kinds_b": _count(x["kind"] for x in b),
        "sections_a": _count(x["section"] for x in a),
        "sections_b": _count(x["section"] for x in b),
    }


def compare_named(name_a: str, name_b: str, root: Path) -> dict[str, Any]:
    def load(name: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        d = root / "output" / "recipe" / name
        meta = json.loads((d / "qga_pixel_field.json").read_text())
        painted = json.loads((d / "painted.json").read_text()) if (d / "painted.json").is_file() else None
        return meta, painted

    ma, pa = load(name_a)
    mb, pb = load(name_b)
    if pa is None or pb is None:
        raise FileNotFoundError("painted.json missing; recompile the recipes")
    if (ma.get("T"), ma.get("n_faces")) != (mb.get("T"), mb.get("n_faces")):
        raise ValueError(
            f"nets differ: {name_a} T={ma.get('T')} F={ma.get('n_faces')} "
            f"vs {name_b} T={mb.get('T')} F={mb.get('n_faces')}"
        )
    out = compare_painted(pa, pb)
    out["a"] = name_a
    out["b"] = name_b
    out["T"] = ma.get("T")
    out["claim"] = "Hypothesis"
    return out


def twist_scan(base_name: str, twists: list[float] | None = None) -> dict[str, Any]:
    """Same sites, chart snap; vary generator twist. Hypothesis.

    Chart φ of homologs should stay tight. Embedded φ spreads as |twist|·Δu.
    """
    from copy import deepcopy

    from .compile import build_net, load_recipe, recipe_dir
    from .paint import paint_faces

    if twists is None:
        twists = [0.0, math.pi / 4.0, math.pi / 2.0, math.pi]
    spec0 = load_recipe(recipe_dir() / f"{base_name}.yaml")
    spec0["_base"] = str(recipe_dir())
    rows = []
    for t in twists:
        spec = deepcopy(spec0)
        spec.setdefault("carrier", {})
        spec["carrier"]["kind"] = "cylinder"
        spec["carrier"]["twist"] = float(t)
        net = build_net(spec)
        paint_faces(net, spec)
        h = spec.get("_homology") or {}
        d1 = (h.get("homologs") or {}).get("D1") or {}
        sigma_u = float(d1.get("std_shell_s") or 0.0)
        pred = abs(float(t)) * sigma_u * (180.0 / math.pi)
        rows.append(
            {
                "twist": float(t),
                "phi_order_ok": h.get("phi_order_ok"),
                "embed_phi_order_ok": h.get("embed_phi_order_ok"),
                "cluster_pure": h.get("cluster_pure"),
                "D1_std_phi_chart": d1.get("std_phi_deg"),
                "D1_std_phi_embed": d1.get("std_phi_embed"),
                "D1_std_phi_embed_pred": pred,
                "D1_sigma_u": sigma_u,
                "D1_shell_s_range": d1.get("shell_s_range"),
            }
        )
    return {
        "claim": "Hypothesis",
        "base": base_name,
        "snap": "segment-ring, nearest unused azimuth",
        "shear": "|twist| * sigma_u * 180/pi",
        "embed_order_bound": "pi/4 on 36-bin Hinton chart",
        "twists": rows,
    }


def _count(items) -> dict[str, int]:
    out: dict[str, int] = {}
    for x in items:
        out[str(x)] = out.get(str(x), 0) + 1
    return out


def _std(xs: list[float]) -> float:
    if len(xs) < 2:
        return 0.0
    m = sum(xs) / len(xs)
    return (sum((x - m) ** 2 for x in xs) / (len(xs) - 1)) ** 0.5


def sites_from_spec(spec: dict[str, Any]) -> list[dict[str, Any]]:
    """YAML paint.mode: sites → setal rows. Cylinder unroll by segment."""
    paint = spec.get("paint") or {}
    inherit = paint.get("inherit")
    if inherit:
        from .compile import load_recipe, recipe_dir

        parent = load_recipe(recipe_dir() / f"{inherit}.yaml")
        pp = dict(parent.get("paint") or {})
        merged = dict(pp)
        merged["sites"] = list(pp.get("sites") or []) + list(paint.get("sites") or [])
        merged["singularities"] = list(pp.get("singularities") or []) + list(
            paint.get("singularities") or []
        )
        groups = dict(pp.get("groups") or {})
        groups.update(paint.get("groups") or {})
        merged["groups"] = groups
        for k, v in paint.items():
            if k not in ("inherit", "sites", "singularities", "groups"):
                merged[k] = v
        paint = merged
        spec = dict(spec)
        spec["paint"] = paint
    groups = paint.get("groups") or {}
    group_sec = {str(g): _section(h) for g, h in groups.items()}
    default = _section(paint.get("default_hue") or "elliptic")
    rows: list[dict[str, Any]] = []

    def add(
        *,
        segment: str,
        seta: str,
        phi: float,
        amp: float,
        group: str | None,
        kind: str,
        section: str | None = None,
    ) -> None:
        sec = section or (group_sec[group] if group in group_sec else default)
        rows.append(
            {
                "id": f"{segment}-{seta}",
                "kind": kind,
                "segment": segment,
                "seta": seta,
                "group": group,
                "s": segment_s(str(segment)),
                "phi_deg": float(phi),
                "amplitude": float(amp),
                "section": sec,
                "width": 0.08,
                "psi": 0.0,
            }
        )

    for site in paint.get("sites") or []:
        add(
            segment=str(site["segment"]),
            seta=str(site.get("seta") or site.get("id") or "site"),
            phi=float(site.get("phi") if site.get("phi") is not None else site.get("phi_deg")),
            amp=float(site.get("amp") if site.get("amp") is not None else site.get("amplitude") or 1.0),
            group=str(site["group"]) if site.get("group") else None,
            kind=str(site.get("kind") or "seta"),
        )
    for sg in paint.get("singularities") or []:
        kind = str(sg.get("kind") or "tentacle")
        if kind not in KINDS:
            raise ValueError(f"singularity kind {kind!r} not in {KINDS}")
        seg = str(sg["segment"])
        hue = sg.get("hue") or sg.get("section")
        section = _section(hue) if hue else default
        amp = float(sg.get("amplitude") or sg.get("amp") or 1.0)
        phi0 = float(sg.get("phi") if sg.get("phi") is not None else 0.0)
        count = int(sg.get("count") or 1)
        if count >= 2:
            phis = [phi0 + 8.0, -(phi0 + 8.0)] if phi0 == 0.0 else [phi0, -phi0]
            phis = phis[:count]
        else:
            phis = [phi0]
        group = "SD" if kind == "tentacle" else (kind if kind == "spiracle" else None)
        for k, phi in enumerate(phis):
            add(
                segment=seg,
                seta=f"{kind}{k + 1}",
                phi=phi,
                amp=amp,
                group=group,
                kind=kind,
                section=section,
            )
    return rows


def homology_score(
    net: dict[str, Any], painted: list[dict[str, Any]], log: list[dict[str, Any]]
) -> dict[str, Any]:
    """Do homologous setae keep hue, and stay ordered in φ after the wrap?

    Cluster purity of group→section is mostly the paint rule (Software fact).
    Axial spread in shell_s vs φ, and D<SD<L<SV<V mean-φ order, test whether
    the closed Goldberg net scrambled the cylinder (Hypothesis).
    """
    cents = [face_centroid(net, f) for f in net["faces"]]
    chart = net.get("face_chart")
    by_group: dict[str, list[int]] = {}
    by_seta: dict[str, list[dict[str, Any]]] = {}
    snaps = [x["snap_deg"] for x in log if x.get("how") == "nearest"]

    def face_phi(i: int) -> float:
        if chart:
            return float(chart[i][1])
        c = cents[i]
        return math.degrees(math.atan2(c[1], c[0]))

    def embed_phi(i: int) -> float:
        if net.get("kind") == "cylinder":
            from .cylinder import face_centroid_euclid

            c = face_centroid_euclid(net, net["faces"][i])
        else:
            c = cents[i]
        return math.degrees(math.atan2(c[1], c[0]))

    def left_abs(p: float, from_chart: bool) -> float:
        if from_chart and chart:
            return p if p <= 180.0 else 360.0 - p
        return abs(p)

    for entry in log:
        if entry.get("how") != "nearest":
            continue
        i = int(entry["face"])
        g = entry.get("group") or "plain"
        by_group.setdefault(str(g), []).append(i)
        seta = entry.get("seta")
        if not seta:
            continue
        phi_face = face_phi(i)
        by_seta.setdefault(str(seta), []).append(
            {
                "id": entry["id"],
                "segment": entry.get("segment"),
                "face": i,
                "section": painted[i]["section"],
                "shell_s": painted[i]["shell_s"],
                "phi_face": phi_face,
                "phi_abs": left_abs(phi_face, True),
                "phi_embed": left_abs(embed_phi(i), False),
                "snap_deg": entry["snap_deg"],
            }
        )

    groups: dict[str, Any] = {}
    for g, idxs in sorted(by_group.items()):
        secs = sorted({painted[i]["section"] for i in idxs})
        groups[g] = {"n": len(idxs), "sections": secs, "pure": len(secs) == 1}

    homologs: dict[str, Any] = {}
    for seta, recs in sorted(by_seta.items()):
        if len(recs) < 2:
            continue
        phis = [r["phi_abs"] for r in recs]
        ss = [r["shell_s"] for r in recs]
        secs = sorted({r["section"] for r in recs})
        phis_e = [r["phi_embed"] for r in recs]
        homologs[seta] = {
            "n": len(recs),
            "section_pure": len(secs) == 1,
            "sections": secs,
            "std_phi_deg": _std(phis),
            "std_phi_embed": _std(phis_e),
            "std_shell_s": _std(ss),
            "shell_s_range": max(ss) - min(ss),
            "mean_phi_abs": sum(phis) / len(phis),
            "mean_phi_embed": sum(phis_e) / len(phis_e),
        }

    means: dict[str, float] = {}
    embed_means: dict[str, float] = {}
    for g in GROUP_ORDER:
        if g == "D":
            idxs = (by_group.get("D") or []) + (by_group.get("XD") or [])
        else:
            idxs = by_group.get(g) or []
        if not idxs:
            continue
        phis = [left_abs(face_phi(i), True) for i in idxs]
        means[g] = sum(phis) / len(phis)
        embed_means[g] = sum(left_abs(embed_phi(i), False) for i in idxs) / len(idxs)
    ordered = list(means.keys())
    phi_order_ok = all(means[ordered[i]] <= means[ordered[i + 1]] + 1e-6 for i in range(len(ordered) - 1))
    embed_order = list(embed_means.keys())
    embed_phi_order_ok = all(
        embed_means[embed_order[i]] <= embed_means[embed_order[i + 1]] + 1e-6
        for i in range(len(embed_order) - 1)
    )

    return {
        "claim": "Hypothesis",
        "cluster_pure": all(v["pure"] for v in groups.values()),
        "axial_hue_pure": all(v["section_pure"] for v in homologs.values()) if homologs else True,
        "phi_order_ok": phi_order_ok,
        "embed_phi_order_ok": embed_phi_order_ok,
        "phi_means": means,
        "embed_phi_means": embed_means,
        "groups": groups,
        "homologs": homologs,
        "n_sites": sum(1 for x in log if x.get("how") == "nearest"),
        "max_snap_deg": max(snaps) if snaps else 0.0,
        "mean_snap_deg": (sum(snaps) / len(snaps)) if snaps else 0.0,
        "twist": net.get("twist", 0.0),
        "snap": "segment-ring, nearest unused azimuth",
    }
