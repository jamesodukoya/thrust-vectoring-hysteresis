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
from .investigation_animation import save_investigation_animation  # noqa: E402
from .test_stand_figure import save_test_stand_figure  # noqa: E402
from .validation_figure import save_validation_figure  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
PATH = [0, 80, 40, 70, 10]  # Synthetic input for the separate state-model illustration.
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
    a.set_title("Synthetic state model, not bench data")
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
    a.set_title("Illustrative state model, not bench data", fontsize=11)
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


def draw_uncertainty_comparison(axis, uncertainty: dict) -> None:
    quantities = ["thrust_constant", "thrust_prediction"]
    percentages = [100 * uncertainty[quantity]["expanded"] for quantity in quantities]
    bars = axis.bar(["Fitted constant", "Thrust prediction"], percentages, color=[BLUE, ORANGE])
    axis.bar_label(bars, fmt="%.2f%%", padding=3, fontsize=9)
    axis.set(ylabel="Expanded relative uncertainty (%)", ylim=(0, 7))
    axis.set_title("Prediction includes model mismatch")


def characterization_png(output_path: Path) -> None:
    summary_path = ROOT / "data" / "characterization_summary.json"
    summary = json.loads(summary_path.read_text())
    figure, uncertainty_axis = plt.subplots(figsize=(8, 4.8))
    draw_uncertainty_comparison(uncertainty_axis, summary["uncertainty"])
    uncertainty_axis.spines[["top", "right"]].set_visible(False)
    uncertainty_axis.grid(axis="y", alpha=0.2)
    uncertainty_axis.set_axisbelow(True)
    figure.text(0.5, 0.035, "Coverage factor 2; unverified absolute gain excluded.", ha="center", fontsize=9)
    figure.tight_layout(rect=(0, 0.06, 1, 1))
    figure.savefig(output_path, dpi=150)
    plt.close(figure)


def main(outdir: str | None = None):
    out = Path(outdir) if outdir else ROOT / "figures"
    out.mkdir(parents=True, exist_ok=True)
    minor_loops_png(out / "demo_minor_loops.png")
    loop_gif(out / "hysteresis_loop.gif")
    characterization_png(out / "characterization_results.png")
    paths = [out / name for name in ("demo_minor_loops.png", "hysteresis_loop.gif", "characterization_results.png")]
    paths.append(save_validation_figure(out / "force_validation.png"))
    paths.append(save_test_stand_figure(out / "test_stand.png"))
    paths.extend(save_investigation_animation(out))
    return paths


if __name__ == "__main__":
    for p in main(sys.argv[1] if len(sys.argv) > 1 else None):
        print("wrote", p)
