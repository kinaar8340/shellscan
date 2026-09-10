"""Compile a recipe YAML to a net + qga_pixel field. Not a faceplate verb."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .dynamics import morph_t
from .geodesic import geodesic_polyhedron
from .goldberg import goldberg_dual
from .helicoid_catenoid import morph_aa, patch_grid
from .paint import paint_faces
from .wrap import manifest, pack_field, write_field
from .yaml_lite import load_simple_yaml

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore[misc, assignment]


def load_recipe(path: Path) -> dict[str, Any]:
    text = path.read_text()
    if yaml is not None:
        spec = yaml.safe_load(text)
    else:
        spec = load_simple_yaml(text)
    if not isinstance(spec, dict):
        raise ValueError(f"{path} is not a mapping")
    return spec


def build_net(spec: dict[str, Any]) -> dict[str, Any]:
    carrier = spec.get("carrier") or {}
    kind = str(carrier.get("kind", "icosahedral"))
    if kind == "icosahedral":
        m = int(carrier["m"])
        n = int(carrier["n"])
        geo = geodesic_polyhedron(m, n)
        dual = str(carrier.get("dual", "goldberg"))
        if dual == "goldberg":
            return goldberg_dual(geo)
        if dual in ("geodesic", "none"):
            geo = dict(geo)
            geo["faces"] = [list(f) for f in geo["faces"]]
            return geo
        raise ValueError(f"unknown dual {dual!r}")
    if kind == "helicoid_catenoid":
        hc = carrier.get("helicoid_catenoid") or carrier
        aa = morph_aa(morph_t(spec)) if "aa" not in hc else float(hc["aa"])
        bb = float(hc.get("bb", 1.0))
        u_span = float(hc.get("u_span", 6.283185307179586))
        v_span = float(hc.get("v_span", 2.0))
        verts, faces = patch_grid(aa, bb, u_span, v_span)
        return {
            "m": 0,
            "n": 0,
            "T": 0,
            "class": "hc",
            "kind": "helicoid_catenoid",
            "verts": verts,
            "faces": faces,
            "V": len(verts),
            "F": len(faces),
            "aa": aa,
            "bb": bb,
        }
    raise ValueError(f"unknown carrier kind {kind!r}")


def compile_recipe(
    spec: dict[str, Any] | Path,
    outdir: Path,
    render: bool = True,
) -> dict[str, Any]:
    if isinstance(spec, Path):
        spec = load_recipe(spec)
    net = build_net(spec)
    painted = paint_faces(net, spec)
    blob = pack_field(painted)
    meta = manifest(spec, net, painted, blob)
    write_field(outdir, blob, meta)
    (outdir / "recipe.json").write_text(json.dumps(spec, indent=2) + "\n")
    if render:
        from .render import render_all

        render_all(spec, net, painted, outdir)
    return meta


def recipe_dir() -> Path:
    return Path(__file__).resolve().parents[2] / "recipes"


def output_dir(name: str) -> Path:
    return Path(__file__).resolve().parents[2] / "output" / "recipe" / name


def compile_named(name: str, render: bool = True) -> dict[str, Any]:
    path = recipe_dir() / f"{name}.yaml"
    if not path.is_file():
        raise FileNotFoundError(path)
    return compile_recipe(path, output_dir(name), render=render)


def compile_all(render: bool = True) -> dict[str, dict[str, Any]]:
    out = {}
    for path in sorted(recipe_dir().glob("*.yaml")):
        out[path.stem] = compile_recipe(path, output_dir(path.stem), render=render)
    return out
