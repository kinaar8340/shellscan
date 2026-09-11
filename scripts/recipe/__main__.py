"""python3 -m recipe --all | --name banded-larva | compare A B"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .compile import compile_all, compile_named, recipe_dir


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] == "compare":
        return _compare(argv[1:])
    if argv and argv[0] == "compare_groups":
        return _compare_groups(argv[1:])
    if argv and argv[0] == "rd_chart":
        return _rd_chart(argv[1:])
    if argv and argv[0] == "score":
        return _score(argv[1:])
    if argv and argv[0] == "twist-scan":
        return _twist_scan(argv[1:])
    if argv and argv[0] == "film":
        return _film(argv[1:])
    p = argparse.ArgumentParser(prog="recipe", description="Recipe sidecar. Not a faceplate verb.")
    p.add_argument("--all", action="store_true", help="compile every recipes/*.yaml")
    p.add_argument("--name", type=str, help="compile recipes/<name>.yaml")
    p.add_argument("--no-render", action="store_true")
    args = p.parse_args(argv)
    render = not args.no_render
    if args.all:
        metas = compile_all(render=render)
        print(json.dumps({k: _brief(v) for k, v in metas.items()}, indent=2))
        return 0
    if args.name:
        meta = compile_named(args.name, render=render)
        print(json.dumps(_brief(meta), indent=2))
        return 0
    p.print_help()
    return 2


def _compare(argv: list[str]) -> int:
    p = argparse.ArgumentParser(prog="recipe compare")
    p.add_argument("a")
    p.add_argument("b")
    args = p.parse_args(argv)
    from .setal import compare_named

    root = recipe_dir().parent
    for name in (args.a, args.b):
        painted = root / "output" / "recipe" / name / "painted.json"
        if not painted.is_file():
            compile_named(name, render=False)
    out = compare_named(args.a, args.b, root)
    dest = root / "output" / "recipe" / f"compare_{args.a}_{args.b}.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))
    return 0


def _compare_groups(argv: list[str]) -> int:
    p = argparse.ArgumentParser(
        prog="recipe compare_groups",
        description="Per-group Δφ vs Hinton atlas. Read dumps. Do not re-snap.",
    )
    p.add_argument(
        "--ref",
        default="output/recipe/setal-hinton-cylinder/chaetotaxy.json",
        help="Hinton (or other) chaetotaxy.json",
    )
    p.add_argument(
        "--against",
        default="plexippus-cylinder,danaus-gilippus,melpomene-cylinder,polyxenes-cylinder",
        help="comma-separated recipe stems or setal-<stem> names",
    )
    args = p.parse_args(argv)
    from .setal import compare_groups

    root = recipe_dir().parent

    def atlas_path(spec: str) -> Path:
        raw = Path(spec)
        if raw.is_file():
            return raw
        name = spec
        if not name.startswith("setal-"):
            name = f"setal-{name}"
        if name.endswith(".json"):
            return root / name
        return root / "output" / "recipe" / name / "chaetotaxy.json"

    ref = atlas_path(args.ref)
    if not ref.is_file():
        raise SystemExit(f"missing ref atlas {ref}")
    against: dict[str, Path] = {}
    for item in args.against.split(","):
        item = item.strip()
        if not item:
            continue
        path = atlas_path(item)
        if not path.is_file():
            raise SystemExit(f"missing atlas {path}")
        key = item
        if key.startswith("setal-"):
            key = key[len("setal-") :]
        against[key] = path
    out = compare_groups(ref, against)
    dest = root / "output" / "recipe" / "compare_groups.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(out, indent=2) + "\n")
    scores = root / "docs" / "recipe-scores" / "compare_groups.json"
    scores.parent.mkdir(parents=True, exist_ok=True)
    scores.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out["table"], indent=2))
    print(json.dumps({"claim": out["claim"], "note": out["note"]}, indent=2))
    return 0


def _rd_chart(argv: list[str]) -> int:
    p = argparse.ArgumentParser(
        prog="recipe rd_chart",
        description="Gray-Scott on growing (s,phi). Model of pigment, not a segment clock.",
    )
    p.add_argument(
        "--chaeta",
        default="output/recipe/setal-polyxenes-cylinder/chaetotaxy.json",
    )
    p.add_argument(
        "--out",
        default="output/recipe/setal-polyxenes-cylinder/rd_field.json",
    )
    args = p.parse_args(argv)
    from .rd_chart import run_polyxenes

    root = recipe_dir().parent
    chaeta = Path(args.chaeta)
    if not chaeta.is_file():
        chaeta = root / args.chaeta
    out = Path(args.out)
    if not out.is_absolute():
        out = root / args.out
    rec = run_polyxenes(chaeta, out)
    print(
        json.dumps(
            {
                "claim": rec["claim"],
                "law": rec["law"],
                "ns": rec["ns"],
                "nphi": rec["nphi"],
                "note": rec["note"],
                "out": str(out),
            },
            indent=2,
        )
    )
    return 0


def _score(argv: list[str]) -> int:
    p = argparse.ArgumentParser(prog="recipe score")
    p.add_argument("name")
    args = p.parse_args(argv)
    root = recipe_dir().parent
    meta_path = root / "output" / "recipe" / args.name / "qga_pixel_field.json"
    if not meta_path.is_file():
        compile_named(args.name, render=False)
    meta = json.loads(meta_path.read_text())
    score = meta.get("homology")
    if not score:
        raise SystemExit(f"{args.name} has no homology block; use paint.mode: sites")
    dest = root / "output" / "recipe" / args.name / "homology.json"
    dest.write_text(json.dumps(score, indent=2) + "\n")
    print(json.dumps(score, indent=2))
    return 0


def _twist_scan(argv: list[str]) -> int:
    p = argparse.ArgumentParser(prog="recipe twist-scan")
    p.add_argument("name", nargs="?", default="setal-hinton-cylinder")
    p.add_argument(
        "--dense",
        action="store_true",
        help="six twists from π/4 to π/2 (embed D/SD crossing)",
    )
    args = p.parse_args(argv)
    from .setal import twist_scan
    import math as _math

    twists = None
    if args.dense:
        twists = [_math.pi / 4.0 + i * (_math.pi / 4.0) / 5.0 for i in range(6)]
    out = twist_scan(args.name, twists=twists)
    root = recipe_dir().parent
    dest = root / "output" / "recipe" / f"twist_scan_{args.name}.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))
    return 0


def _film(argv: list[str]) -> int:
    p = argparse.ArgumentParser(
        prog="recipe film",
        description="Sidecar field strip. Not Animation A. Not γ(s). Not a live inner_cone solve.",
    )
    p.add_argument(
        "--strip",
        choices=("t3", "cylinder"),
        default="t3",
        help="t3 occupant triangle (default) or cylinder isoline. Not both.",
    )
    p.add_argument(
        "--preview",
        action="store_true",
        help="one frame per shot (smoke), not the 60 s strip",
    )
    p.add_argument("--no-encode", action="store_true", help="PNG sequence only")
    args = p.parse_args(argv)
    from .film import run_cylinder_film, run_film

    if args.strip == "cylinder":
        run_cylinder_film(preview=args.preview, encode=not args.no_encode)
    else:
        run_film(preview=args.preview, encode=not args.no_encode)
    return 0


def _brief(meta: dict) -> dict:
    keep = (
        "name",
        "claim",
        "m",
        "n",
        "T",
        "class",
        "kind",
        "n_faces",
        "n_bytes",
        "n_pentagons",
        "n_hexagons",
        "kinds",
        "hash",
        "setal",
        "table",
        "homology",
        "occupancy",
    )
    return {k: meta.get(k) for k in keep}


if __name__ == "__main__":
    sys.exit(main())
