"""Generate the repo's demo figures: python -m tvh.figures [outdir]"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.animation import FuncAnimation, PillowWriter  # noqa: E402

from .model import GKParams, eta_v, simulate, sweep  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
PATH = [0, 80, 40, 70, 10]  # the same sweep as the thesis minor-loop figure
BLUE, ORANGE, INK, BAND = "#1f6fb4", "#e8742a", "#222222", "#f3e2c3"


def _run():
    t, theta = sweep(PATH, rate_deg_s=20.0, dt=0.005)
    x, eta = simulate(theta, t, GKParams(), x_init=1.0)
    return t, theta, x, eta


def _decorate(ax_l, ax_r, p=GKParams()):
    for ax in (ax_l,):
        ax.axvspan(p.theta_desc, p.theta_asc, color=BAND, alpha=0.6, lw=0, label="bistable band")
        th = np.linspace(0, 80, 400)
        ax.plot(th, eta_v(th, 1.0), color=BLUE, lw=1, ls=":", alpha=0.7, label="attached sheet")
        ax.plot(th, eta_v(th, 0.0), color=ORANGE, lw=1, ls=":", alpha=0.7, label="separated sheet")
        ax.set(xlim=(0, 82), ylim=(-0.03, 1.05), xlabel="servo angle θ (deg)", ylabel="vertical share of thrust η_V")
        ax.grid(alpha=0.25)
    ax_r.set(xlabel="time (s)", ylabel="θ (deg)  /  x × 100")
    ax_r.grid(alpha=0.25)


def minor_loops_png(out: Path):
    t, theta, x, eta = _run()
    fig, (a, b) = plt.subplots(1, 2, figsize=(11, 4.2))
    _decorate(a, b)
    a.plot(theta, eta, color=INK, lw=2, label="path 0→80→40→70→10°")
    a.legend(loc="center right", fontsize=8, frameon=False)
    a.set_title("Same angle, two answers (illustrative model)")
    b.plot(t, theta, color=INK, lw=1.6, label="θ(t)")
    b.plot(t, 100 * x, color=BLUE, lw=1.6, ls="--", label="x(t) × 100  (1 = attached)")
    b.legend(fontsize=8, frameon=False, loc="lower right")
    b.set_title("The state remembers the history")
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)


def loop_gif(out: Path, frames: int = 120):
    t, theta, x, eta = _run()
    idx = np.linspace(0, len(t) - 1, frames).astype(int)
    fig, (a, b) = plt.subplots(1, 2, figsize=(9, 3.6))
    _decorate(a, b)
    b.set(xlim=(0, t[-1]), ylim=(-5, 105))
    a.set_title("Flap sweep: the jet remembers", fontsize=11)
    b.set_title("θ(t) and attachment state x(t)", fontsize=11)
    (trace,) = a.plot([], [], color=INK, lw=2)
    (dot,) = a.plot([], [], "o", ms=9)
    (lt,) = b.plot([], [], color=INK, lw=1.6, label="θ")
    (lx,) = b.plot([], [], color=BLUE, lw=1.6, ls="--", label="x × 100")
    b.legend(fontsize=8, frameon=False, loc="upper right")
    fig.tight_layout()

    def update(i):
        k = idx[i]
        trace.set_data(theta[: k + 1], eta[: k + 1])
        dot.set_data([theta[k]], [eta[k]])
        dot.set_color(BLUE if x[k] >= 0.5 else ORANGE)
        lt.set_data(t[: k + 1], theta[: k + 1])
        lx.set_data(t[: k + 1], 100 * x[: k + 1])
        return trace, dot, lt, lx

    anim = FuncAnimation(fig, update, frames=frames, blit=True)
    anim.save(out, writer=PillowWriter(fps=15), dpi=80)
    plt.close(fig)


def hover_yaw_png(out: Path):
    d = json.loads((ROOT / "data" / "hover_yaw.json").read_text())
    conds = list(d["conditions"].values())
    series = [("motors_only_floor", "motors only", "#c9d2dc"),
              ("flight_design", "hysteresis-aware allocator", BLUE),
              ("after_bench_v2", "after bench v2 (more states)", "#7fb3e0")]
    fig, ax = plt.subplots(figsize=(7.5, 4.2))
    w, xs = 0.26, np.arange(len(conds))
    for j, (key, label, color) in enumerate(series):
        vals = [c[key] for c in conds]
        bars = ax.bar(xs + (j - 1) * w, vals, w, color=color, label=label)
        ax.bar_label(bars, fmt="%.2f", fontsize=8, padding=2)
    req = d["requirements"]
    for key, label, ls in [("beam_wind_design", "beam-wind requirement", "-"),
                           ("nose_into_wind", "nose-into-wind requirement", "--"),
                           ("calm_air_minimum", "calm-air minimum", ":")]:
        ax.axhline(req[key], color=INK, lw=1.2, ls=ls)
        ax.text(len(conds) - 0.45, req[key] + 0.03, label, fontsize=8, ha="right")
    ax.set_xticks(xs, [c["label"] for c in conds])
    ax.set_ylabel("deliverable hover yaw (N·m)")
    ax.set_title("Hover yaw authority, thesis simulation results")
    ax.legend(fontsize=8, frameon=False, loc="upper left")
    ax.set_ylim(0, 2.4)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)


def main(outdir: str | None = None):
    out = Path(outdir) if outdir else ROOT / "figures"
    out.mkdir(parents=True, exist_ok=True)
    minor_loops_png(out / "demo_minor_loops.png")
    loop_gif(out / "hysteresis_loop.gif")
    hover_yaw_png(out / "hover_yaw.png")
    return [out / n for n in ("demo_minor_loops.png", "hysteresis_loop.gif", "hover_yaw.png")]


if __name__ == "__main__":
    for p in main(sys.argv[1] if len(sys.argv) > 1 else None):
        print("wrote", p)
