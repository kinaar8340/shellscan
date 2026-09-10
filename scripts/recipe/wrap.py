"""Face records → packed 32-byte QgaPixel field. Software fact of layout.

Reuses scripts/export_slm_pixel.pack_pixel / parse_pixel.
Does not write output/pick/qga_pixel.bin.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

_SCRIPTS = Path(__file__).resolve().parents[1]
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from export_slm_pixel import pack_pixel, parse_pixel  # noqa: E402

RGB = {
    "elliptic": (0.2, 0.6, 1.0),
    "parabolic": (1.0, 0.75, 0.2),
    "hyperbolic": (1.0, 0.4, 0.2),
    "flat-pockets": (1.0, 0.2, 0.8),
}


def rgb_preview(section: str, amplitude: float, persist: float) -> tuple[float, float, float]:
    base = RGB[section]
    a = max(0.0, min(1.0, float(amplitude) * float(persist)))
    return (base[0] * a, base[1] * a, base[2] * a)


def pack_field(painted: list[dict[str, Any]]) -> bytes:
    chunks = []
    for rec in painted:
        chunks.append(
            pack_pixel(
                {
                    "theta": rec["theta"],
                    "phi": rec["phi"],
                    "psi": rec["psi"],
                    "offset": rec["offset"],
                    "amplitude": rec["amplitude"],
                    "shell_s": rec["shell_s"],
                    "persist": rec["persist"],
                    "field": rec["field"],
                    "section": rec["section"],
                    "layer": rec.get("layer", 0),
                }
            )
        )
    return b"".join(chunks)


def parse_field(blob: bytes) -> list[dict[str, Any]]:
    if len(blob) % 32 != 0:
        raise ValueError(f"field dump length {len(blob)} not a multiple of 32")
    return [parse_pixel(blob[i : i + 32]) for i in range(0, len(blob), 32)]


def manifest(
    spec: dict[str, Any],
    net: dict[str, Any],
    painted: list[dict[str, Any]],
    blob: bytes,
) -> dict[str, Any]:
    kinds: dict[str, int] = {}
    sections: dict[str, int] = {}
    tent = []
    for rec in painted:
        kinds[rec["kind"]] = kinds.get(rec["kind"], 0) + 1
        sections[rec["section"]] = sections.get(rec["section"], 0) + 1
        if rec["kind"] == "tentacle":
            tent.append(rec["i"])
    return {
        "name": spec.get("name"),
        "claim": spec.get("claim", "Model"),
        "m": net.get("m"),
        "n": net.get("n"),
        "T": net.get("T"),
        "class": net.get("class"),
        "kind": net.get("kind"),
        "V": net.get("V"),
        "F": net.get("F"),
        "n_pentagons": net.get("n_pentagons"),
        "n_hexagons": net.get("n_hexagons"),
        "n_faces": len(painted),
        "n_bytes": len(blob),
        "hash": hashlib.sha256(blob).hexdigest(),
        "kinds": kinds,
        "sections": sections,
        "tentacle_indices": tent,
        "morph_t": (spec.get("dynamics") or {}).get("morph_t", 0.0),
        "subunits_60T": 60 * int(net.get("T") or 0),
        "setal": spec.get("_setal_stats"),
        "table": (spec.get("paint") or {}).get("table"),
        "homology": spec.get("_homology"),
        "occupancy": {
            "pentamer": kinds.get("pentamer", 0),
            "hexamer": kinds.get("hexamer", 0),
            "portal": kinds.get("portal", 0),
            "dimer": kinds.get("dimer", 0),
            "vp1": kinds.get("vp1", 0),
            "vp2": kinds.get("vp2", 0),
            "vp3": kinds.get("vp3", 0),
            "subunits_60T": 60 * int(net.get("T") or 0),
            "T": net.get("T"),
            "portal_faces": spec.get("_portal_faces") or [],
        },
    }


def write_field(outdir: Path, blob: bytes, meta: dict[str, Any]) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "qga_pixel_field.bin").write_bytes(blob)
    (outdir / "qga_pixel_field.json").write_text(json.dumps(meta, indent=2) + "\n")
