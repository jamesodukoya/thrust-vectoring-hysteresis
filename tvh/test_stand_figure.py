"""Annotate a raster-only exterior render; no CAD or internal geometry is distributed."""
from __future__ import annotations

from pathlib import Path

import matplotlib.image as matplotlib_image
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
INK, BLUE, ORANGE = "#172c46", "#2865b5", "#c66b38"
LABELS = [
    {"text": "Nozzle housing\nOpaque exterior envelope", "anchor": (0.3051, 0.8915), "position": (0.03, 0.985)},
    {"text": "Ducted fan\nRotor detail concealed", "anchor": (0.4119, 0.8292), "position": (0.53, 0.92)},
    {"text": "Covered servo drive\nMechanism concealed", "anchor": (0.2950, 0.8104), "position": (0.55, 0.67)},
    {"text": "Independent output encoder\nAS5600", "anchor": (0.2499, 0.7984), "position": (0.005, 0.75), "color": BLUE},
    {"text": "Rigid support\nStand geometry simplified", "anchor": (0.3176, 0.5542), "position": (0.005, 0.54)},
    {"text": "Six-axis force/torque sensor\nForce and moment channels", "anchor": (0.3176, 0.3397), "position": (0.005, 0.30)},
    {"text": "Position controller\nRP2040 feedback loop", "anchor": (0.4909, 0.2008), "position": (0.40, 0.08), "color": ORANGE},
    {"text": "Data acquisition\nForce-sensor voltages", "anchor": (0.6010, 0.3949), "position": (0.68, 0.28)},
    {"text": "Experiment computer\nLabVIEW and timestamped logs", "anchor": (0.8253, 0.5259), "position": (0.79, 0.75)},
]


def draw_leader(axis, label: dict) -> None:
    color = label.get("color", INK)
    axis.annotate(
        label["text"], xy=label["anchor"], xytext=label["position"],
        fontsize=10, color=color, ha="left", va="center", linespacing=1.5,
        bbox={"facecolor": "white", "edgecolor": "none", "pad": 3},
        arrowprops={"arrowstyle": "-", "color": color, "lw": 0.9, "connectionstyle": "angle3,angleA=0,angleB=90"},
    )
    axis.plot(*label["anchor"], "o", color=color, ms=2.5)


def draw_signal_route(axis, points: list, color: str) -> None:
    horizontal, vertical = zip(*points)
    axis.plot(horizontal, vertical, color=color, lw=1.5, alpha=0.8, linestyle=(0, (3, 3)))
    axis.annotate("", xy=points[-1], xytext=points[-2], arrowprops={"arrowstyle": "-|>", "color": color, "lw": 1.5})


def save_test_stand_figure(output_path: Path) -> Path:
    exterior_path = ROOT / "figures/assets/test_stand_exterior.png"
    exterior = matplotlib_image.imread(exterior_path)
    figure, axis = plt.subplots(figsize=(14, 10))
    axis.imshow(exterior, extent=(0, 1, 0, 1), aspect="auto")
    draw_signal_route(axis, [(0.25, 0.80), (0.22, 0.68), (0.22, 0.17), (0.49, 0.17), (0.49, 0.20)], BLUE)
    draw_signal_route(axis, [(0.49, 0.20), (0.53, 0.23), (0.53, 0.71), (0.2950, 0.8104)], ORANGE)
    for label in LABELS:
        draw_leader(axis, label)
    axis.set(xlim=(-0.01, 1.035), ylim=(0.02, 1.025))
    axis.axis("off")
    figure.text(0.045, 0.955, "Measure the output. Close the position loop.", fontsize=22, fontweight="bold", color=INK)
    figure.text(0.045, 0.918, "Instrumented test stand · housing exterior based on the actual nozzle CAD", fontsize=12, color="#5a6e85")
    figure.text(0.045, 0.075, "● Measured output position", fontsize=10, color=BLUE)
    figure.text(0.31, 0.075, "● Servo command", fontsize=10, color=ORANGE)
    figure.text(0.045, 0.043, "Opaque envelope and caps conceal the flow path, flap, linkage and outlet detail. No CAD or mechanism dimensions are included.", fontsize=9, color=INK)
    figure.text(0.045, 0.019, "Stand, electronics placement and signal routes are schematic. Force acquisition and controller logs are aligned during analysis.", fontsize=9, color="#5a6e85")
    figure.subplots_adjust(left=0.04, right=0.96, top=0.875, bottom=0.11)
    figure.savefig(output_path, dpi=160, facecolor="white")
    plt.close(figure)
    return output_path
