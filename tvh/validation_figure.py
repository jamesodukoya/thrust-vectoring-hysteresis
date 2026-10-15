"""Plot public, grouped validation results without exposing individual bench records."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SPLIT_LABELS = ("Fit first → test second", "Fit second → test first")
SPLIT_COLORS = ("#2664b5", "#c66b38")
INK = "#182b43"


def style_axis(axis) -> None:
    axis.spines[["top", "right"]].set_visible(False)
    axis.spines[["bottom", "left"]].set_color("#b8c1cb")
    axis.tick_params(colors="#4f6073", labelsize=9)
    axis.grid(alpha=0.15, color="#7e8d9d")
    axis.set_axisbelow(True)


def draw_agreement(axis, component_name: str, splits: dict) -> None:
    maximum_force_newtons = max(
        bin_summary["mean_measured_N"]
        for split in splits.values()
        for bin_summary in split["components"][component_name]["bins"]
    ) * 1.08
    axis.plot([0, maximum_force_newtons], [0, maximum_force_newtons], "--", color="#a6b1bf", lw=1.2)
    for split, label, color in zip(splits.values(), SPLIT_LABELS, SPLIT_COLORS):
        component = split["components"][component_name]
        measured = [summary["mean_measured_N"] for summary in component["bins"]]
        predicted = [summary["mean_predicted_N"] for summary in component["bins"]]
        counts = np.array([summary["n_dwells"] for summary in component["bins"]])
        legend = f'{label} · {component["rmse_N"]:.3f} N RMSE'
        axis.scatter(measured, predicted, s=22 + 5 * np.sqrt(counts), color=color, edgecolor="white", lw=0.8, label=legend)
    axis.set(xlabel="Measured force (N)", ylabel="Predicted force (N)")
    axis.set(xlim=(-0.2, maximum_force_newtons), ylim=(-0.2, maximum_force_newtons))
    axis.set_title(f"{component_name.capitalize()} force", loc="left", color=INK, fontweight="bold", pad=12)
    axis.legend(frameon=False, fontsize=8, loc="upper left")
    axis.text(0.96, 0.06, "Dashed line: exact agreement", transform=axis.transAxes, ha="right", color="#647488", fontsize=8)
    style_axis(axis)


def draw_residuals(axis, component_name: str, splits: dict) -> None:
    axis.axhline(0, color="#7a889a", lw=1, ls="--")
    for split, color in zip(splits.values(), SPLIT_COLORS):
        bins = split["components"][component_name]["bins"]
        measured = [summary["mean_measured_N"] for summary in bins]
        residuals = [summary["mean_residual_N"] for summary in bins]
        lower = [summary["residual_p10_N"] for summary in bins]
        upper = [summary["residual_p90_N"] for summary in bins]
        axis.fill_between(measured, lower, upper, color=color, alpha=0.12, lw=0)
        axis.plot(measured, residuals, "o-", color=color, ms=3.5, lw=1.1)
    axis.set(xlabel="Measured force (N)", ylabel="Prediction − measurement (N)")
    axis.set_title("Residuals reveal where errors remain", loc="left", color=INK, fontsize=10)
    style_axis(axis)


def save_validation_figure(output_path: Path) -> Path:
    measurements = json.loads((ROOT / "data/validation_bins.json").read_text())
    with plt.rc_context({"font.family": "DejaVu Sans", "font.size": 10}):
        figure, axes = plt.subplots(2, 2, figsize=(12.8, 9), gridspec_kw={"height_ratios": [1.6, 1]})
        for column, component_name in enumerate(("axial", "vertical")):
            draw_agreement(axes[0, column], component_name, measurements["splits"])
            draw_residuals(axes[1, column], component_name, measurements["splits"])
        figure.suptitle("Fit one session. Predict another.", x=0.075, y=0.975, ha="left", color=INK, fontsize=21, fontweight="bold")
        figure.text(0.075, 0.93, "Separate-session validation · 313 dwells forward / 349 in reverse", fontsize=11, color="#52667e")
        figure.text(0.075, 0.065, "Points: measured-force bin means; size reflects dwell count. RMSE uses every held-out dwell.", fontsize=9, color=INK)
        figure.text(0.075, 0.042, "Shading: observed 10–90% residual range within bins, not a confidence interval.", fontsize=9, color=INK)
        figure.text(0.075, 0.018, "Session scale correction; measured flap position and speed supplied. Absolute force-sensor gain remains unverified.", fontsize=8.5, color="#52667e")
        figure.subplots_adjust(left=0.075, right=0.98, top=0.865, bottom=0.15, hspace=0.43, wspace=0.26)
        figure.savefig(output_path, dpi=160, facecolor="white")
        plt.close(figure)
    return output_path
