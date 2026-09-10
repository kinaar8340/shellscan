"""python3 -m recipe --all | --name banded-larva [--no-render]"""

from __future__ import annotations

import argparse
import json
import sys

from .compile import compile_all, compile_named


def main(argv: list[str] | None = None) -> int:
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
    )
    return {k: meta.get(k) for k in keep}


if __name__ == "__main__":
    sys.exit(main())
