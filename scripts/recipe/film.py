"""T=3 field strip. Sidecar PNG sequence + ffmpeg.

Not Animation A. Not make scan. Not γ(s). Not a Lambert mesh.
Uses qga_pixel dumps, rgb_preview(), persist, --mask blank/nappe.
"""

from __future__ import annotations

import json
import math
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .compile import build_net, compile_named, load_recipe, output_dir, recipe_dir
from .goldberg import face_centroid
from .render import _fit_axes
from .setal import compare_painted
from .wrap import RGB, parse_field, rgb_preview

FPS = 24
WIDTH = 1280
HEIGHT = 720
DPI = 100
SIZE = (WIDTH / DPI, HEIGHT / DPI)
ELEV = 18
AZIM = 35
BG = "#07080a"
GENERATOR = 0.5**0.5
APEX_EPS = 1e-4
PARA_EPS = 0.02
BIN_ORDER = ("elliptic", "parabolic", "hyperbolic", "flat-pockets")

NAMES = {
    "ck": "capsid-t3",
    "ms2": "capsid-t3-ms2",
    "kite": "capsid-t3-kite",
    "rhomb": "capsid-t3-rhomb30",
}

# One film, three beats, ~60 s. Preview mode writes one frame per shot.
SHOTS: tuple[dict[str, Any], ...] = (
    {"id": "title", "beat": 1, "seconds": 2.0},
    {"id": "plane", "beat": 1, "seconds": 8.0},
    {"id": "ck", "beat": 2, "seconds": 5.0},
    {"id": "ck_ms2", "beat": 2, "seconds": 8.0},
    {"id": "ms2", "beat": 2, "seconds": 4.0},
    {"id": "ms2_kite", "beat": 2, "seconds": 8.0},
    {"id": "kite_card", "beat": 2, "seconds": 2.0},
    {"id": "rhombille", "beat": 2, "seconds": 6.0},
    {"id": "persist_rise", "beat": 3, "seconds": 5.0},
    {"id": "persist_decay", "beat": 3, "seconds": 4.0},
    {"id": "blank", "beat": 3, "seconds": 3.0},
    {"id": "nappe", "beat": 3, "seconds": 3.0},
    {"id": "end", "beat": 3, "seconds": 2.0},
)


@dataclass
class Bundle:
    name: str
    net: dict[str, Any]
    recs: list[dict[str, Any]]


def classify_section(
    n: tuple[float, float, float],
    offset: float,
    axis: tuple[float, float, float] = (0.0, 0.0, 1.0),
) -> str:
    """Same bins as src/section.rs. Software fact of the copy, not a fifth hue."""
    if abs(offset) < APEX_EPS:
        return "flat-pockets"

    def _norm(v: tuple[float, float, float]) -> tuple[float, float, float]:
        length = math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2]) or 1.0
        return (v[0] / length, v[1] / length, v[2] / length)

    n = _norm(n)
    axis = _norm(axis)
    s = abs(n[0] * axis[0] + n[1] * axis[1] + n[2] * axis[2])
    if abs(s - GENERATOR) < PARA_EPS:
        return "parabolic"
    if s > GENERATOR:
        return "elliptic"
    return "hyperbolic"


def lerp3(
    a: tuple[float, float, float], b: tuple[float, float, float], t: float
) -> tuple[float, float, float]:
    t = max(0.0, min(1.0, float(t)))
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t)


def lerp_preview(
    a: dict[str, Any], b: dict[str, Any], t: float
) -> tuple[float, float, float]:
    """Lerp witness RGB only. Do not invent a 33rd byte."""
    ca = rgb_preview(a["section"], a["amplitude"], a["persist"] or 1.0)
    cb = rgb_preview(b["section"], b["amplitude"], b["persist"] or 1.0)
    return lerp3(ca, cb, t)


def face_colors(
    recs: list[dict[str, Any]],
    *,
    persist: float | None = None,
    mask: str = "none",
    other: list[dict[str, Any]] | None = None,
    t: float | None = None,
) -> list[tuple[float, float, float, float]]:
    out: list[tuple[float, float, float, float]] = []
    for i, rec in enumerate(recs):
        if mask == "nappe" and rec["section"] == "elliptic":
            out.append((0.0, 0.0, 0.0, 0.0))
            continue
        amp = 0.0 if mask == "blank" else float(rec["amplitude"])
        p = float(rec["persist"] or 1.0) if persist is None else float(persist)
        if other is None or t is None:
            r, g, b = rgb_preview(rec["section"], amp, p)
        else:
            oa, ob = dict(rec), dict(other[i])
            oa["amplitude"] = amp
            ob["amplitude"] = 0.0 if mask == "blank" else float(ob["amplitude"])
            if persist is not None:
                oa["persist"] = p
                ob["persist"] = p
            r, g, b = lerp_preview(oa, ob, t)
        out.append((r, g, b, 0.96))
    return out


def plane_state(u: float) -> tuple[tuple[float, float, float], float, str]:
    """Four equal holds: elliptic, parabolic, hyperbolic, then offset→0 flat."""
    u = max(0.0, min(1.0, float(u)))
    if u < 0.25:
        v = u / 0.25
        theta = math.radians(12.0 + v * 18.0)
        offset = 0.32
    elif u < 0.50:
        theta = math.radians(45.0)
        offset = 0.32
    elif u < 0.75:
        v = (u - 0.50) / 0.25
        theta = math.radians(52.0 + v * 23.0)
        offset = 0.32
    else:
        v = (u - 0.75) / 0.25
        theta = math.radians(75.0)
        offset = 0.0 if v > 0.65 else 0.32 * (1.0 - v)
    n = (math.sin(theta), 0.0, math.cos(theta))
    return n, offset, classify_section(n, offset)


def shot_frame_count(seconds: float, preview: bool) -> int:
    if preview:
        return 1
    return max(1, int(round(float(seconds) * FPS)))


def shot_u(k: int, n: int, *, at_end: bool = False) -> float:
    """Preview morphs land on t=1 so the contact sheet shows the destination paint."""
    if n == 1:
        return 1.0 if at_end else 0.0
    return k / (n - 1)


def timeline(preview: bool = False) -> list[dict[str, Any]]:
    frames: list[dict[str, Any]] = []
    for shot in SHOTS:
        n = shot_frame_count(shot["seconds"], preview)
        for k in range(n):
            frames.append(
                {
                    "shot": shot["id"],
                    "beat": shot["beat"],
                    "u": 0.0 if n == 1 else k / (n - 1),
                    "i": len(frames),
                }
            )
    return frames


def duration_seconds(preview: bool = False) -> float:
    if preview:
        return len(SHOTS) / FPS
    return sum(float(s["seconds"]) for s in SHOTS)


def ensure_dumps(dump_root: Path | None = None) -> None:
    if dump_root is not None:
        return
    for name in NAMES.values():
        blob = output_dir(name) / "qga_pixel_field.bin"
        if not blob.is_file():
            compile_named(name, render=False)


def load_named(name: str, dump_root: Path) -> Bundle:
    spec = load_recipe(recipe_dir() / f"{name}.yaml")
    net = build_net(spec)
    d = dump_root / name
    blob_path = d / "qga_pixel_field.bin"
    if not blob_path.is_file():
        raise FileNotFoundError(blob_path)
    field = parse_field(blob_path.read_bytes())
    slim = json.loads((d / "painted.json").read_text())
    if len(field) != len(net["faces"]) or len(slim) != len(field):
        raise ValueError(
            f"{name}: dump F={len(field)} slim={len(slim)} net F={len(net['faces'])}"
        )
    recs = []
    for i, (px, sl, face) in enumerate(zip(field, slim, net["faces"])):
        recs.append(
            {
                "i": i,
                "kind": sl["kind"],
                "section": px["section"],
                "amplitude": px["amplitude"],
                "persist": px["persist"] if px["persist"] else 1.0,
                "centroid": face_centroid(net, face),
            }
        )
    return Bundle(name=name, net=net, recs=recs)


def load_occupant(dump_root: Path) -> dict[str, Bundle]:
    return {key: load_named(name, dump_root) for key, name in NAMES.items()}


def _pyplot():
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Line3DCollection, Poly3DCollection

    return plt, Poly3DCollection, Line3DCollection


def _style_ax(ax) -> None:
    ax.set_axis_off()
    ax.view_init(elev=ELEV, azim=AZIM)
    ax.set_facecolor(BG)
    ax.grid(False)
    try:
        ax.xaxis.pane.fill = False
        ax.yaxis.pane.fill = False
        ax.zaxis.pane.fill = False
        ax.xaxis.pane.set_edgecolor(BG)
        ax.yaxis.pane.set_edgecolor(BG)
        ax.zaxis.pane.set_edgecolor(BG)
    except AttributeError:
        pass


def _new_fig(plt):
    fig = plt.figure(figsize=SIZE, dpi=DPI, facecolor=BG)
    ax = fig.add_axes((0.04, 0.16, 0.92, 0.78), projection="3d")
    _style_ax(ax)
    card = fig.text(
        0.5,
        0.09,
        "",
        ha="center",
        va="center",
        color="#f2f2f6",
        fontsize=14,
        fontname="DejaVu Sans",
    )
    sub = fig.text(
        0.5,
        0.045,
        "",
        ha="center",
        va="center",
        color="#9aa0aa",
        fontsize=11,
        fontname="DejaVu Sans",
    )
    return fig, ax, card, sub


def _set_card(card, sub, text: str, extra: str = "") -> None:
    card.set_text(text)
    sub.set_text(extra)


def _edges_for(colors: list[tuple[float, float, float, float]]):
    return [(1.0, 1.0, 1.0, 0.0 if c[3] <= 0.0 else 0.16) for c in colors]


class NetCanvas:
    def __init__(self, plt, Poly3DCollection):
        self.plt = plt
        self.Poly3DCollection = Poly3DCollection
        self.fig = None
        self.ax = None
        self.col = None
        self.card = None
        self.sub = None
        self.n_faces = None

    def bind(self, net: dict[str, Any]) -> None:
        n = len(net["faces"])
        if self.col is not None and self.n_faces == n:
            return
        self.close()
        fig, ax, card, sub = _new_fig(self.plt)
        verts = net["verts"]
        polys = [[verts[i] for i in face] for face in net["faces"]]
        dummy = [(0.0, 0.0, 0.0, 0.0)] * n
        col = self.Poly3DCollection(
            polys,
            facecolors=dummy,
            edgecolors=_edges_for(dummy),
            linewidths=0.35,
            shade=False,
        )
        ax.add_collection3d(col)
        _fit_axes(ax, verts)
        _style_ax(ax)
        self.fig = fig
        self.ax = ax
        self.col = col
        self.card = card
        self.sub = sub
        self.n_faces = n

    def paint(
        self,
        colors: list[tuple[float, float, float, float]],
        text: str,
        extra: str = "",
    ) -> None:
        self.col.set_facecolor(colors)
        self.col.set_edgecolor(_edges_for(colors))
        _set_card(self.card, self.sub, text, extra)

    def save(self, path: Path) -> None:
        self.fig.savefig(path, dpi=DPI, facecolor=BG)

    def close(self) -> None:
        if self.fig is not None:
            self.plt.close(self.fig)
        self.fig = self.ax = self.col = self.card = self.sub = None
        self.n_faces = None


def _title_fig(plt, title: str, extra: str):
    fig = plt.figure(figsize=SIZE, dpi=DPI, facecolor=BG)
    fig.text(
        0.5,
        0.56,
        title,
        ha="center",
        va="center",
        color="#f2f2f6",
        fontsize=26,
        fontname="DejaVu Sans",
    )
    fig.text(
        0.5,
        0.40,
        extra,
        ha="center",
        va="center",
        color="#9aa0aa",
        fontsize=14,
        fontname="DejaVu Sans",
    )
    return fig


def _plane_fig(plt, Poly3DCollection, Line3DCollection, n, offset, section, seen):
    fig, ax, card, sub = _new_fig(plt)
    gens = []
    for k in range(20):
        ang = 2.0 * math.pi * k / 20.0
        x, y = math.cos(ang), math.sin(ang)
        gens.append([(x, y, 1.15), (0.0, 0.0, 0.0)])
        gens.append([(x, y, -1.15), (0.0, 0.0, 0.0)])
    ax.add_collection3d(
        Line3DCollection(gens, colors=(0.55, 0.58, 0.62, 0.35), linewidths=0.6)
    )
    length = math.sqrt(n[0] * n[0] + n[1] * n[1] + n[2] * n[2]) or 1.0
    nh = (n[0] / length, n[1] / length, n[2] / length)
    if abs(nh[2]) < 0.9:
        tmp = (0.0, 0.0, 1.0)
    else:
        tmp = (1.0, 0.0, 0.0)
    u = (
        nh[1] * tmp[2] - nh[2] * tmp[1],
        nh[2] * tmp[0] - nh[0] * tmp[2],
        nh[0] * tmp[1] - nh[1] * tmp[0],
    )
    ul = math.sqrt(u[0] * u[0] + u[1] * u[1] + u[2] * u[2]) or 1.0
    u = (u[0] / ul, u[1] / ul, u[2] / ul)
    v = (
        nh[1] * u[2] - nh[2] * u[1],
        nh[2] * u[0] - nh[0] * u[2],
        nh[0] * u[1] - nh[1] * u[0],
    )
    center = (nh[0] * offset, nh[1] * offset, nh[2] * offset)
    ring = []
    rad = 0.95
    for k in range(28):
        ang = 2.0 * math.pi * k / 28.0
        c, s = math.cos(ang), math.sin(ang)
        ring.append(
            (
                center[0] + rad * (c * u[0] + s * v[0]),
                center[1] + rad * (c * u[1] + s * v[1]),
                center[2] + rad * (c * u[2] + s * v[2]),
            )
        )
    rgb = rgb_preview(section, 1.0, 1.0)
    disk = Poly3DCollection(
        [ring],
        facecolors=[(*rgb, 0.88)],
        edgecolors=[(1.0, 1.0, 1.0, 0.35)],
        linewidths=0.6,
        shade=False,
    )
    ax.add_collection3d(disk)
    _fit_axes(ax, ring + [(0.0, 0.0, 1.15), (0.0, 0.0, -1.15)])
    _style_ax(ax)
    card.set_position((0.5, 0.125))
    sub.set_position((0.5, 0.09))
    _set_card(card, sub, "color is conic type", "inner_cone · not MathFlow · not a fifth hue")
    xs = [0.18, 0.36, 0.54, 0.72]
    for x, name in zip(xs, BIN_ORDER):
        lit = name in seen
        r, g, b = rgb_preview(name, 1.0, 1.0 if lit else 0.12)
        bin_ax = fig.add_axes((x, 0.02, 0.12, 0.024), facecolor=(r, g, b, 1.0))
        bin_ax.set_xticks([])
        bin_ax.set_yticks([])
        for spine in bin_ax.spines.values():
            spine.set_color("#f2f2f6" if name == section else "#33353a")
            spine.set_linewidth(1.6 if name == section else 0.4)
    return fig


class Sequence:
    def __init__(self, frames_dir: Path):
        self.frames_dir = frames_dir
        self.frames_dir.mkdir(parents=True, exist_ok=True)
        self.i = 0
        self.last: Path | None = None

    def write_fig(self, fig, plt, n: int = 1) -> None:
        path = self.frames_dir / f"frame_{self.i:04d}.png"
        fig.savefig(path, dpi=DPI, facecolor=BG)
        plt.close(fig)
        self.last = path
        self.i += 1
        self.repeat(n - 1)

    def write_canvas(self, canvas: NetCanvas, n: int = 1) -> None:
        path = self.frames_dir / f"frame_{self.i:04d}.png"
        canvas.save(path)
        self.last = path
        self.i += 1
        self.repeat(n - 1)

    def repeat(self, n: int) -> None:
        if n <= 0 or self.last is None:
            return
        src = self.last
        for _ in range(n):
            dst = self.frames_dir / f"frame_{self.i:04d}.png"
            shutil.copyfile(src, dst)
            self.last = dst
            self.i += 1


def encode_mp4(frames_dir: Path, mp4_path: Path, fps: int = FPS) -> None:
    if shutil.which("ffmpeg") is None:
        raise SystemExit("ffmpeg not on PATH")
    mp4_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg",
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-framerate",
        str(fps),
        "-i",
        str(frames_dir / "frame_%04d.png"),
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        str(mp4_path),
    ]
    subprocess.run(cmd, check=True)


def run_film(
    *,
    outdir: Path | None = None,
    dump_root: Path | None = None,
    preview: bool = False,
    encode: bool = True,
) -> dict[str, Any]:
    root = Path(__file__).resolve().parents[2]
    dump_root = dump_root or (root / "output" / "recipe")
    outdir = outdir or (root / "output" / "recipe" / "film")
    if dump_root == root / "output" / "recipe":
        ensure_dumps()
    occ = load_occupant(dump_root)
    ck, ms2, kite, rhomb = occ["ck"], occ["ms2"], occ["kite"], occ["rhomb"]
    vs_ms2 = compare_painted(ck.recs, ms2.recs)
    vs_kite = compare_painted(ck.recs, kite.recs)
    frames_dir = outdir / "frames"
    if frames_dir.is_dir():
        shutil.rmtree(frames_dir)
    seq = Sequence(frames_dir)
    plt, Poly3DCollection, Line3DCollection = _pyplot()
    canvas = NetCanvas(plt, Poly3DCollection)
    seen: set[str] = set()
    for shot in SHOTS:
        n = shot_frame_count(shot["seconds"], preview)
        sid = shot["id"]
        print(f"film {sid} ×{n}", flush=True)
        if sid == "title":
            fig = _title_fig(
                plt,
                "T=3 field strip",
                "catalog is the net and the conic · the life is the occupant",
            )
            seq.write_fig(fig, plt, n)
        elif sid == "plane":
            for k in range(n):
                u = shot_u(k, n, at_end=False)
                normal, offset, section = plane_state(u)
                seen.add(section)
                fig = _plane_fig(
                    plt,
                    Poly3DCollection,
                    Line3DCollection,
                    normal,
                    offset,
                    section,
                    seen,
                )
                seq.write_fig(fig, plt)
        elif sid == "ck":
            canvas.bind(ck.net)
            canvas.paint(
                face_colors(ck.recs),
                "CK face-degree",
                "12 elliptic + 20 hyperbolic · GP(1,1) F=32",
            )
            seq.write_canvas(canvas, n)
        elif sid == "ck_ms2":
            canvas.bind(ck.net)
            for k in range(n):
                u = shot_u(k, n, at_end=True)
                canvas.paint(
                    face_colors(ck.recs, other=ms2.recs, t=u),
                    "MS2 dimer",
                    "hexagons flip parabolic · paint moves, surface does not",
                )
                seq.write_canvas(canvas)
        elif sid == "ms2":
            canvas.bind(ms2.net)
            canvas.paint(
                face_colors(ms2.recs),
                "MS2 dimer",
                "12 pentamer + 20 dimer · same catalog",
            )
            seq.write_canvas(canvas, n)
        elif sid == "ms2_kite":
            canvas.bind(ck.net)
            for k in range(n):
                u = shot_u(k, n, at_end=True)
                canvas.paint(
                    face_colors(ms2.recs, other=kite.recs, t=u),
                    "kite / trimer",
                    "hexagons hyperbolic again · kind changed, section matches CK",
                )
                seq.write_canvas(canvas)
        elif sid == "kite_card":
            canvas.bind(kite.net)
            canvas.paint(
                face_colors(kite.recs),
                "section_agree 1.0 · kind_agree 12/32",
                "same T=3 net · occupant is not the catalog",
            )
            seq.write_canvas(canvas, n)
        elif sid == "rhombille":
            canvas.bind(rhomb.net)
            canvas.paint(
                face_colors(rhomb.recs),
                "compare-refused",
                "F=90 rhombille · all parabolic · same T=3, different F",
            )
            seq.write_canvas(canvas, n)
        elif sid == "persist_rise":
            canvas.bind(ck.net)
            for k in range(n):
                u = shot_u(k, n, at_end=True)
                canvas.paint(
                    face_colors(ck.recs, persist=u),
                    "persist is mote age",
                    "amplitude × persist · not a key light",
                )
                seq.write_canvas(canvas)
        elif sid == "persist_decay":
            canvas.bind(ck.net)
            for k in range(n):
                u = 0.5 if n == 1 else k / (n - 1)
                canvas.paint(
                    face_colors(ck.recs, persist=1.0 - 0.85 * u),
                    "phosphor decay",
                    "darkening is age · not a shadow map",
                )
                seq.write_canvas(canvas)
        elif sid == "blank":
            canvas.bind(ck.net)
            for k in range(n):
                u = shot_u(k, n, at_end=True)
                mask = "blank" if u > 0.35 else "none"
                canvas.paint(
                    face_colors(ck.recs, persist=0.15, mask=mask),
                    "blanking is the separator",
                    "--mask blank · amplitude 0",
                )
                seq.write_canvas(canvas)
        elif sid == "nappe":
            canvas.bind(ck.net)
            canvas.paint(
                face_colors(ck.recs, persist=1.0, mask="nappe"),
                "32-byte pixel · RGB is a projection",
                "--mask nappe · omit elliptic · no section flip",
            )
            seq.write_canvas(canvas, n)
        elif sid == "end":
            fig = _title_fig(
                plt,
                "Model + Software fact",
                "not a proof that MS2 is this mesh · faceplate unused",
            )
            seq.write_fig(fig, plt, n)
        else:
            raise ValueError(sid)
    canvas.close()
    mp4 = outdir / ("t3_field_strip_preview.mp4" if preview else "t3_field_strip.mp4")
    if encode:
        encode_mp4(frames_dir, mp4)
        dest = root / "output" / "mp4" / mp4.name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(mp4, dest)
    meta = {
        "title": "T=3 field strip",
        "not": "Animation A",
        "claim": "Model + Software fact",
        "fps": FPS,
        "n_frames": seq.i,
        "n_shots": len(SHOTS),
        "seconds": round(seq.i / FPS, 4),
        "preview": preview,
        "mp4": str(mp4) if encode else None,
        "faceplate": "unused",
        "gamma": False,
        "compare": {
            "ck_ms2": {
                "section_agree": vs_ms2["section_agree"],
                "kind_agree": vs_ms2["kind_agree"],
            },
            "ck_kite": {
                "section_agree": vs_kite["section_agree"],
                "kind_agree": vs_kite["kind_agree"],
            },
            "rhombille": "compare-refused",
        },
        "dumps": list(NAMES.values()),
    }
    (outdir / "manifest.json").write_text(json.dumps(meta, indent=2) + "\n")
    print(json.dumps(meta, indent=2), flush=True)
    return meta
