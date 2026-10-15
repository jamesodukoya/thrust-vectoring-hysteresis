"""Animate the investigation using published results and explicitly schematic diagrams."""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from matplotlib import font_manager
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
WIDTH, HEIGHT = 1200, 680
FRAMES_PER_SCENE = 50
FRAME_DURATION_MS = 100
BACKGROUND = "#f1f5fa"
WHITE, INK, MUTED = "#ffffff", "#172c46", "#5a6e85"
BLUE, ORANGE, GREEN = "#2865b5", "#c66b38", "#188376"
BORDER, LIGHT_BLUE = "#dce4ee", "#e9f0fa"
REGULAR_FONT = font_manager.findfont("DejaVu Sans")
BOLD_FONT = font_manager.findfont(font_manager.FontProperties(family="DejaVu Sans", weight="bold"))
SCENE_LABELS = ("01  Observe", "02  Measure", "03  Control & test", "04  Predict")
CAPTIONS = (
    "Observation is evidence. Its cause still needs a test.",
    "Measure the output instead of assuming it follows the command.",
    "Close the position loop. Then compare like with like.",
    "Fit a measured-position map. Predict a separate session.",
)


@lru_cache(maxsize=32)
def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(BOLD_FONT if bold else REGULAR_FONT, size)


def write(draw: ImageDraw.ImageDraw, position: tuple, wording: dict) -> None:
    draw.multiline_text(position, wording["text"], font=font(wording.get("size", 20), wording.get("bold", False)), fill=wording.get("color", INK), spacing=8)


def arrow(draw: ImageDraw.ImageDraw, endpoints: tuple, color: str = BLUE) -> None:
    start, end = endpoints
    draw.line([start, end], fill=color, width=4)
    horizontal = end[0] - start[0]
    vertical = end[1] - start[1]
    length = max(1, (horizontal ** 2 + vertical ** 2) ** 0.5)
    direction = (horizontal / length, vertical / length)
    base = (end[0] - 12 * direction[0], end[1] - 12 * direction[1])
    draw.polygon([end, (base[0] - 6 * direction[1], base[1] + 6 * direction[0]), (base[0] + 6 * direction[1], base[1] - 6 * direction[0])], fill=color)


def draw_frame(scene_index: int, progress: float) -> Image.Image:
    frame = Image.new("RGB", (WIDTH, HEIGHT), BACKGROUND)
    draw = ImageDraw.Draw(frame)
    write(draw, (32, 23), {"text": "ACTUATOR CHARACTERIZATION  /  FROM ASSUMPTION TO EVIDENCE", "size": 14, "color": MUTED, "bold": True})
    write(draw, (30, 55), {"text": "Measure the output. Test the explanation.", "size": 38, "bold": True})
    for index, label in enumerate(SCENE_LABELS):
        left = 32 + index * 287
        is_current = index == scene_index
        fill = INK if is_current else WHITE
        draw.rounded_rectangle((left, 115, left + 275, 152), radius=9, fill=fill)
        write(draw, (left + 16, 123), {"text": label, "size": 16, "bold": True, "color": WHITE if is_current else MUTED})
        if is_current:
            draw.rounded_rectangle((left, 151, left + max(2, 275 * progress), 154), radius=1, fill=GREEN)
    for left, right in [(32, 587), (611, 1168)]:
        draw.rounded_rectangle((left, 177, right, 552), radius=20, fill=WHITE, outline=BORDER, width=1)
    write(draw, (33, 578), {"text": CAPTIONS[scene_index], "size": 23, "bold": True})
    write(draw, (33, 628), {"text": "Diagrams are schematic. Force scores use session scale correction; absolute sensor gain remains unverified.", "size": 14, "color": MUTED})
    return frame


def draw_actuator(draw: ImageDraw.ImageDraw, has_encoder: bool) -> None:
    write(draw, (58, 205), {"text": "THE MEASUREMENT QUESTION", "size": 13, "color": MUTED, "bold": True})
    arrow(draw, ((74, 334), (155, 334)), BLUE)
    draw.rounded_rectangle((166, 283, 471, 385), radius=24, fill=INK)
    draw.ellipse((143, 296, 193, 372), fill=INK, outline="#8093a9", width=2)
    write(draw, (212, 315), {"text": "Vectoring actuator", "size": 22, "bold": True, "color": WHITE})
    write(draw, (76, 391), {"text": "Command", "size": 15, "color": BLUE})
    if has_encoder:
        draw.rounded_rectangle((321, 366, 374, 417), radius=7, fill=GREEN)
        draw.ellipse((334, 378, 361, 405), outline=WHITE, width=3)
        write(draw, (241, 436), {"text": "Independent output encoder", "size": 18, "color": GREEN, "bold": True})
        write(draw, (58, 501), {"text": "Output position becomes a measured variable.", "size": 17, "color": MUTED})
    else:
        write(draw, (206, 418), {"text": "Actual flap position: unmeasured", "size": 18, "color": ORANGE})
        write(draw, (58, 501), {"text": "An opaque box hides a missing measurement.", "size": 17, "color": MUTED})


def draw_observation(frame: Image.Image, progress: float) -> None:
    draw = ImageDraw.Draw(frame)
    draw_actuator(draw, False)
    write(draw, (58, 238), {"text": "Same command. Same throttle.", "size": 21, "bold": True})
    write(draw, (640, 205), {"text": "INITIAL BENCH OBSERVATION", "size": 13, "color": MUTED, "bold": True})
    write(draw, (640, 240), {"text": "How much thrust points vertically?", "size": 23, "bold": True})
    baseline = 466
    revealed = min(1, progress * 2)
    for left, fraction, label, color in [(737, 0.047, "Ascending", BLUE), (970, 0.987, "Descending", ORANGE)]:
        height = max(3, fraction * 148 * revealed)
        draw.rounded_rectangle((left, baseline - height, left + 86, baseline), radius=5, fill=color)
        write(draw, (left - 5, baseline - height - 38), {"text": f"{fraction * 100:.1f}%", "size": 27, "bold": True, "color": color})
        write(draw, (left - 17, 477), {"text": label, "size": 17, "color": MUTED})
    draw.line((685, baseline + 1, 1124, baseline + 1), fill=BORDER, width=2)
    write(draw, (654, 289), {"text": "Hypothesis: flow hysteresis?", "size": 19, "color": ORANGE})
    write(draw, (640, 518), {"text": "Servo command 40° · throttle PWM 2000 µs", "size": 15, "color": MUTED})


def draw_feedback(frame: Image.Image, progress: float) -> None:
    draw = ImageDraw.Draw(frame)
    draw_actuator(draw, True)
    write(draw, (58, 238), {"text": "Command ≠ measured position", "size": 21, "bold": True})
    write(draw, (639, 205), {"text": "CLOSE THE LOOP ON POSITION", "size": 13, "color": MUTED, "bold": True})
    write(draw, (639, 241), {"text": "Control the variable being tested.", "size": 23, "bold": True})
    boxes = [(655, "Target"), (822, "Controller"), (1010, "Actuator")]
    for left, label in boxes:
        draw.rounded_rectangle((left, 321, left + 122, 384), radius=10, fill=LIGHT_BLUE, outline=BORDER)
        write(draw, (left + 10, 343), {"text": label, "size": 17, "bold": True})
    arrow(draw, ((782, 352), (813, 352)))
    arrow(draw, ((949, 352), (1003, 352)))
    route = [(1071, 391), (1071, 451), (881, 451), (881, 392)]
    draw.line(route, fill=GREEN, width=4, joint="curve")
    arrow(draw, ((881, 423), (881, 391)), GREEN)
    dot_x = int(1071 - 190 * progress)
    draw.ellipse((dot_x - 6, 445, dot_x + 6, 457), fill=GREEN)
    write(draw, (945, 469), {"text": "Encoder feedback", "size": 17, "color": GREEN})
    write(draw, (639, 511), {"text": "Hold measured position for force measurements.", "size": 17, "color": MUTED})


def draw_experiment(frame: Image.Image, progress: float) -> None:
    draw = ImageDraw.Draw(frame)
    write(draw, (58, 205), {"text": "DESIGN COMPARABLE MEASUREMENTS", "size": 13, "color": MUTED, "bold": True})
    write(draw, (58, 241), {"text": "Approach. Hold. Measure. Repeat.", "size": 22, "bold": True})
    protocols = [(314, "Approach from below", BLUE), (382, "Approach from above", ORANGE), (450, "Change throttle and repeat", GREEN)]
    for row_index, (top, label, color) in enumerate(protocols):
        write(draw, (65, top), {"text": label, "size": 18, "color": color})
        arrow(draw, ((361, top + 14), (528, top + 14)), color)
        dot_x = int(367 + 140 * ((progress + row_index / 3) % 1))
        draw.ellipse((dot_x - 6, top + 8, dot_x + 6, top + 20), fill=color)
    write(draw, (58, 516), {"text": "Schematic protocol, not a recorded motion trace.", "size": 15, "color": MUTED})
    write(draw, (639, 205), {"text": "FIVE SESSIONS, SPECIFIC QUESTIONS", "size": 13, "color": MUTED, "bold": True})
    checks = ["Both approach directions", "Several throttle settings", "Drift checks and fresh telemetry", "Separate fitting and validation"]
    for index, label in enumerate(checks):
        top = 282 + 59 * index
        is_checked = progress >= index / 5
        color = GREEN if is_checked else BORDER
        draw.rounded_rectangle((645, top, 671, top + 26), radius=5, fill=color)
        if is_checked:
            draw.line([(651, top + 13), (657, top + 19), (666, top + 7)], fill=WHITE, width=3)
        write(draw, (688, top + 2), {"text": label, "size": 19, "color": INK if is_checked else MUTED})


def draw_agreement_plot(draw: ImageDraw.ImageDraw, progress: float, split: dict) -> None:
    bounds = (106, 300, 542, 475)
    left, top, right, bottom = bounds
    maximum_force = max(summary["mean_measured_N"] for component in split["components"].values() for summary in component["bins"]) * 1.05
    draw.line([(left, top), (left, bottom), (right, bottom)], fill=MUTED, width=2)
    draw.line([(left, bottom), (right, top)], fill=BORDER, width=2)
    for component_name, color in [("axial", BLUE), ("vertical", ORANGE)]:
        bins = split["components"][component_name]["bins"]
        visible_count = max(1, int(len(bins) * min(1, progress * 1.6)))
        for summary in bins[:visible_count]:
            point_x = left + summary["mean_measured_N"] / maximum_force * (right - left)
            point_y = bottom - summary["mean_predicted_N"] / maximum_force * (bottom - top)
            draw.ellipse((point_x - 5, point_y - 5, point_x + 5, point_y + 5), fill=color, outline=WHITE)
    write(draw, (198, 492), {"text": "Measured force →", "size": 15, "color": MUTED})
    write(draw, (58, 278), {"text": "Predicted force ↑", "size": 15, "color": MUTED})
    write(draw, (58, 522), {"text": "Actual validation statistics · grouped force means", "size": 15, "color": MUTED})


def draw_prediction(frame: Image.Image, progress: float, split: dict) -> None:
    draw = ImageDraw.Draw(frame)
    write(draw, (58, 205), {"text": "MEASURED-POSITION FORCE MAP", "size": 13, "color": MUTED, "bold": True})
    write(draw, (58, 242), {"text": "Measured position + speed → force", "size": 21, "bold": True})
    draw_agreement_plot(draw, progress, split)
    write(draw, (639, 205), {"text": "313 DWELLS EXCLUDED FROM MAP FITTING", "size": 13, "color": MUTED, "bold": True})
    for left, component_name, color in [(644, "axial", BLUE), (907, "vertical", ORANGE)]:
        rmse_newtons = split["components"][component_name]["rmse_N"]
        draw.rounded_rectangle((left, 274, left + 228, 425), radius=15, fill=LIGHT_BLUE)
        write(draw, (left + 18, 294), {"text": component_name.capitalize() + " force", "size": 19, "color": MUTED})
        write(draw, (left + 17, 335), {"text": f"{rmse_newtons:.3f} N", "size": 36, "bold": True, "color": color})
        write(draw, (left + 19, 388), {"text": "prediction RMSE", "size": 17, "color": MUTED})
    write(draw, (644, 455), {"text": "Remaining direction effects stay in the band.", "size": 19, "bold": True, "color": GREEN})
    write(draw, (644, 495), {"text": "Fit a force map on one session.\nTest on another using measured position and speed.", "size": 16, "color": MUTED})


def render_scene(scene_index: int, progress: float, split: dict) -> Image.Image:
    frame = draw_frame(scene_index, progress)
    if scene_index == 0:
        draw_observation(frame, progress)
    elif scene_index == 1:
        draw_feedback(frame, progress)
    elif scene_index == 2:
        draw_experiment(frame, progress)
    else:
        draw_prediction(frame, progress, split)
    return frame


def save_investigation_animation(output_directory: Path) -> list[Path]:
    measurements = json.loads((ROOT / "data/validation_bins.json").read_text())
    split = measurements["splits"]["S2_to_S3"]
    palette_samples = Image.new("RGB", (WIDTH, HEIGHT), WHITE)
    for scene_index in range(4):
        preview = render_scene(scene_index, 1.0, split).resize((WIDTH // 2, HEIGHT // 2))
        palette_samples.paste(preview, ((scene_index % 2) * WIDTH // 2, (scene_index // 2) * HEIGHT // 2))
    palette = palette_samples.quantize(colors=128)
    frames = []
    for scene_index in range(4):
        for frame_index in range(FRAMES_PER_SCENE):
            progress = frame_index / (FRAMES_PER_SCENE - 1)
            frame = render_scene(scene_index, progress, split)
            frames.append(frame.quantize(palette=palette, dither=Image.Dither.NONE))
    animation_path = output_directory / "investigation.gif"
    durations = [FRAME_DURATION_MS] * len(frames)
    durations[-1] = 1600
    frames[0].save(animation_path, save_all=True, append_images=frames[1:], duration=durations, loop=0, optimize=True)
    poster_path = output_directory / "investigation_overview.png"
    overview = Image.new("RGB", (WIDTH * 2, HEIGHT * 2), WHITE)
    for scene_index in range(4):
        position = ((scene_index % 2) * WIDTH, (scene_index // 2) * HEIGHT)
        overview.paste(render_scene(scene_index, 1.0, split), position)
    overview.save(poster_path, optimize=True)
    return [animation_path, poster_path]
