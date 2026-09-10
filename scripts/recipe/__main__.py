"""python3 -m recipe --all | --name banded-larva | compare A B"""

from __future__ import annotations

import argparse
import json
import sys

from .compile import compile_all, compile_named, recipe_dir


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] == "compare":
        return _compare(argv[1:])
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
        description="T=3 field strip. Sidecar PNG + ffmpeg. Not Animation A. Not γ(s).",
    )
    p.add_argument(
        "--preview",
        action="store_true",
        help="one frame per shot (smoke), not the 60 s strip",
    )
    p.add_argument("--no-encode", action="store_true", help="PNG sequence only")
    args = p.parse_args(argv)
    from .film import run_film

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
