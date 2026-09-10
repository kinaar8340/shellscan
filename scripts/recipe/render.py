"""Sidecar stills. Not the Phosphor Loom faceplate. Not a gun."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .helicoid_catenoid import morph_aa, patch_grid
from .wrap import rgb_preview


def render_all(
    spec: dict[str, Any],
    net: dict[str, Any],
    painted: list[dict[str, Any]],
    outdir: Path,
) -> None:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    except ImportError:
        return
    outdir.mkdir(parents=True, exist_ok=True)
    _net_png(net, painted, outdir / "net.png", plt, Poly3DCollection)
    _field_preview(painted, outdir / "field_preview.png", plt)
    _morph_gif(outdir / "morph.gif", plt)


def _net_png(net, painted, path, plt, Poly3DCollection) -> None:
    fig = plt.figure(figsize=(6, 6), dpi=120)
    ax = fig.add_subplot(111, projection="3d")
    verts = net["verts"]
    polys = []
    colors = []
    for rec, face in zip(painted, net["faces"]):
        polys.append([verts[i] for i in face])
        r, g, b = rgb_preview(rec["section"], rec["amplitude"], rec["persist"])
        colors.append((r, g, b, 0.92))
    col = Poly3DCollection(polys, facecolors=colors, edgecolors=(0.1, 0.1, 0.12, 0.45), linewidths=0.35)
    ax.add_collection3d(col)
    ax.set_xlim(-1.15, 1.15)
    ax.set_ylim(-1.15, 1.15)
    ax.set_zlim(-1.15, 1.15)
    ax.set_box_aspect((1, 1, 1))
    ax.set_axis_off()
    ax.view_init(elev=18, azim=35)
    fig.tight_layout(pad=0)
    fig.savefig(path, facecolor="white")
    plt.close(fig)


def _field_preview(painted, path, plt) -> None:
    fig = plt.figure(figsize=(6, 6), dpi=120)
    ax = fig.add_subplot(111, projection="3d")
    xs, ys, zs, cs = [], [], [], []
    for rec in painted:
        c = rec["centroid"]
        xs.append(c[0])
        ys.append(c[1])
        zs.append(c[2])
        cs.append(rgb_preview(rec["section"], rec["amplitude"], rec["persist"]))
    ax.scatter(xs, ys, zs, c=cs, s=18, depthshade=True)
    ax.set_xlim(-1.15, 1.15)
    ax.set_ylim(-1.15, 1.15)
    ax.set_zlim(-1.15, 1.15)
    ax.set_box_aspect((1, 1, 1))
    ax.set_axis_off()
    ax.view_init(elev=18, azim=35)
    fig.tight_layout(pad=0)
    fig.savefig(path, facecolor="white")
    plt.close(fig)


def _morph_gif(path, plt) -> None:
    try:
        from PIL import Image
        import io
    except ImportError:
        _morph_pngs(path.with_suffix(""), plt)
        return
    frames = []
    for k in range(8):
        t = k / 7.0
        aa = morph_aa(t)
        fig = plt.figure(figsize=(5, 5), dpi=80)
        ax = fig.add_subplot(111, projection="3d")
        verts, faces = patch_grid(aa, nu=20, nv=10)
        for f in faces:
            ring = [verts[i] for i in f] + [verts[f[0]]]
            xs, ys, zs = zip(*ring)
            ax.plot(xs, ys, zs, color="#66c2ff", lw=0.5, alpha=0.8)
        ax.set_xlim(-3, 3)
        ax.set_ylim(-3, 3)
        ax.set_zlim(-4, 4)
        ax.set_axis_off()
        ax.set_title(f"aa={aa:.2f}", color="white", fontsize=9)
        fig.patch.set_facecolor("black")
        ax.set_facecolor("black")
        buf = io.BytesIO()
        fig.savefig(buf, format="png", facecolor="black")
        plt.close(fig)
        buf.seek(0)
        frames.append(Image.open(buf).convert("P"))
    frames[0].save(
        path,
        save_all=True,
        append_images=frames[1:],
        duration=180,
        loop=0,
    )


def _morph_pngs(stem: Path, plt) -> None:
    stem.mkdir(parents=True, exist_ok=True)
    for k in range(8):
        t = k / 7.0
        aa = morph_aa(t)
        fig = plt.figure(figsize=(5, 5), dpi=80)
        ax = fig.add_subplot(111, projection="3d")
        verts, faces = patch_grid(aa, nu=20, nv=10)
        for f in faces:
            ring = [verts[i] for i in f] + [verts[f[0]]]
            xs, ys, zs = zip(*ring)
            ax.plot(xs, ys, zs, color="#66c2ff", lw=0.5)
        ax.set_axis_off()
        fig.savefig(stem / f"frame_{k:02d}.png", facecolor="black")
        plt.close(fig)
