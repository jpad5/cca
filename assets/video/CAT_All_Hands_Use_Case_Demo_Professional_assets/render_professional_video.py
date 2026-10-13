from __future__ import annotations

import glob
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parent
WORKSPACE = ROOT.parent
STOCK = ROOT / "stock"
SCENES_DIR = ROOT / "scenes"
CLIPS_DIR = ROOT / "clips"
OUTPUT = WORKSPACE / "CAT_All_Hands_Use_Case_Demo_Professional.mp4"
AUDIO = WORKSPACE / "CAT_All_Hands_Use_Case_Demo_Voice.mp3"

WIDTH = 1920
HEIGHT = 1080
FPS = 30
FADE = 0.4

GREEN = "#00693C"
BRIGHT_GREEN = "#54B848"
MINT = "#B9E4C9"
CREAM = "#F5F2EA"
INK = "#0A1F17"
WHITE = "#FFFFFF"
SOFT_WHITE = "#F7FAF8"
AMBER = "#F2A900"

BOUNDARIES = [
    0.0,
    16.35,
    34.35,
    54.28,
    71.81,
    95.24,
    116.00,
    134.48,
    152.62,
    170.32,
    188.36,
    209.28,
    219.28,
]

SCENES = [
    {
        "eyebrow": "THE SETTING",
        "title": "When a catastrophe\nchanges everything",
        "subtitle": "Customers need clarity. CAT teams need speed without losing care.",
        "image": "catastrophe.jpg",
        "accent": "CLARITY",
        "layout": "standard",
    },
    {
        "eyebrow": "THE ADJUSTER",
        "title": "Meet Maya",
        "subtitle": "A licensed CAT adjuster managing hundreds of items and fragmented evidence.",
        "image": "adjuster.jpg",
        "accent": "JUDGMENT",
        "layout": "standard",
    },
    {
        "eyebrow": "THE FRICTION",
        "title": "Too much work happens\none item at a time",
        "subtitle": "Search. Enter. Reconcile. Document. Repeat.",
        "image": "inventory.jpg",
        "accent": "REPETITION",
        "layout": "metrics",
    },
    {
        "eyebrow": "THE PRINCIPLE",
        "title": "Prepare the evidence.\nDo not automate the decision.",
        "subtitle": "A bounded agent experience supports the adjuster - it does not replace authority.",
        "image": "workflow.jpg",
        "accent": "HUMAN CONTROL",
        "layout": "principle",
    },
    {
        "eyebrow": "THE DESIGN",
        "title": "Clear responsibilities.\nControlled execution.",
        "subtitle": "Copilot guides. Workflows enforce. Services calculate. Dataverse remembers.",
        "image": "research.jpg",
        "accent": "GOVERNED",
        "layout": "architecture",
    },
    {
        "eyebrow": "THE JOURNEY",
        "title": "From intake to an\napproved package",
        "subtitle": "A transparent path with explicit gates, evidence, and exceptions.",
        "image": "workflow.jpg",
        "accent": "TRACEABLE",
        "layout": "journey",
    },
    {
        "eyebrow": "THE WORKSPACE",
        "title": "One view brings the\nevidence together",
        "subtitle": "Normalized inventory, replacement evidence, calculations, and exceptions.",
        "image": "household.jpg",
        "accent": "VISIBLE",
        "layout": "workspace",
    },
    {
        "eyebrow": "THE CONTROL",
        "title": "Maya remains the\ndecision-maker",
        "subtitle": "Approve, correct, override with reason, research further, or hold.",
        "image": "decision.jpg",
        "accent": "AUTHORITY",
        "layout": "decision",
    },
    {
        "eyebrow": "THE OUTPUT",
        "title": "A defensible package,\nready for review",
        "subtitle": "Every recommendation carries evidence, calculations, versions, and exceptions.",
        "image": "research.jpg",
        "accent": "AUDIT READY",
        "layout": "package",
    },
    {
        "eyebrow": "THE VALUE",
        "title": "Faster preparation.\nMore consistent evidence.",
        "subtitle": "Professional time shifts toward exceptions, judgment, and customer outcomes.",
        "image": "recovery.jpg",
        "accent": "FOCUS",
        "layout": "value",
    },
    {
        "eyebrow": "CAT CONTENTS AGENT",
        "title": "Accelerate the evidence.\nPreserve the judgment.",
        "subtitle": "Transparent recommendations. Deterministic calculations. Licensed-adjuster authority.",
        "image": "recovery.jpg",
        "accent": "TRUST",
        "layout": "closing",
    },
    {
        "eyebrow": "END-TO-END VIEW",
        "title": "From claim intake to a\ntrusted recommendation",
        "subtitle": "One governed journey. Clear responsibilities. Human authority throughout.",
        "image": "workflow.jpg",
        "accent": "END TO END",
        "layout": "summary",
    },
]


def font_path(*names: str) -> str:
    windows_fonts = Path("C:/Windows/Fonts")
    for name in names:
        candidate = windows_fonts / name
        if candidate.exists():
            return str(candidate)
    raise FileNotFoundError(f"Could not find any of these fonts: {names}")


FONT_REGULAR = font_path("segoeui.ttf", "arial.ttf")
FONT_SEMIBOLD = font_path("seguisb.ttf", "segoeuib.ttf", "arialbd.ttf")
FONT_BOLD = font_path("segoeuib.ttf", "arialbd.ttf")


def fit_cover(image: Image.Image, size: tuple[int, int], focus_x: float = 0.5) -> Image.Image:
    target_w, target_h = size
    source_ratio = image.width / image.height
    target_ratio = target_w / target_h
    if source_ratio > target_ratio:
        new_h = target_h
        new_w = round(new_h * source_ratio)
    else:
        new_w = target_w
        new_h = round(new_w / source_ratio)
    image = image.resize((new_w, new_h), Image.Resampling.LANCZOS)
    left = int((new_w - target_w) * focus_x)
    left = max(0, min(left, new_w - target_w))
    top = max(0, (new_h - target_h) // 2)
    return image.crop((left, top, left + target_w, top + target_h))


def add_gradient_overlay(image: Image.Image, dark_right: bool = False) -> Image.Image:
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    pixels = overlay.load()
    for x in range(WIDTH):
        ratio = x / (WIDTH - 1)
        if dark_right:
            alpha = int(105 + 125 * ratio)
        else:
            alpha = int(220 - 100 * ratio)
        for y in range(HEIGHT):
            vignette = int(25 * abs((y / HEIGHT) - 0.5) * 2)
            pixels[x, y] = (3, 24, 16, min(245, alpha + vignette))
    return Image.alpha_composite(image.convert("RGBA"), overlay)


def draw_wrapped_text(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    font: ImageFont.FreeTypeFont,
    fill: str,
    max_width: int,
    spacing: int = 10,
) -> int:
    x, y = xy
    lines: list[str] = []
    for paragraph in text.split("\n"):
        words = paragraph.split()
        current = ""
        for word in words:
            candidate = f"{current} {word}".strip()
            if draw.textbbox((0, 0), candidate, font=font)[2] <= max_width:
                current = candidate
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
    line_height = font.size + spacing
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        y += line_height
    return y


def rounded_panel(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    fill: tuple[int, int, int, int],
    outline: str | None = None,
    radius: int = 28,
    width: int = 2,
) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def draw_progress(draw: ImageDraw.ImageDraw, scene_index: int) -> None:
    y = HEIGHT - 48
    draw.line((72, y, WIDTH - 72, y), fill=(255, 255, 255, 65), width=4)
    progress_x = 72 + int((WIDTH - 144) * ((scene_index + 1) / len(SCENES)))
    draw.line((72, y, progress_x, y), fill=BRIGHT_GREEN, width=5)
    draw.text(
        (WIDTH - 72, y - 35),
        f"{scene_index + 1:02d} / {len(SCENES):02d}",
        font=ImageFont.truetype(FONT_SEMIBOLD, 24),
        fill=(255, 255, 255, 210),
        anchor="ra",
    )


def draw_brand(draw: ImageDraw.ImageDraw) -> None:
    draw.ellipse((68, 62, 126, 120), fill=GREEN)
    draw.text(
        (97, 91),
        "CAT",
        font=ImageFont.truetype(FONT_BOLD, 18),
        fill=WHITE,
        anchor="mm",
    )
    draw.text(
        (144, 91),
        "TD INSURANCE",
        font=ImageFont.truetype(FONT_SEMIBOLD, 23),
        fill=(255, 255, 255, 225),
        anchor="lm",
    )


def draw_common_text(draw: ImageDraw.ImageDraw, scene: dict[str, str]) -> None:
    eyebrow_font = ImageFont.truetype(FONT_SEMIBOLD, 25)
    title_font = ImageFont.truetype(FONT_BOLD, 68)
    subtitle_font = ImageFont.truetype(FONT_REGULAR, 31)
    accent_font = ImageFont.truetype(FONT_BOLD, 22)

    eyebrow_width = max(
        206,
        draw.textbbox((0, 0), scene["eyebrow"], font=eyebrow_font)[2] + 42,
    )
    draw.rounded_rectangle((72, 176, 72 + eyebrow_width, 220), radius=22, fill=BRIGHT_GREEN)
    draw.text(
        (72 + eyebrow_width / 2, 198),
        scene["eyebrow"],
        font=eyebrow_font,
        fill=INK,
        anchor="mm",
    )

    title_bottom = draw_wrapped_text(
        draw,
        (72, 265),
        scene["title"],
        title_font,
        WHITE,
        950,
        spacing=9,
    )
    draw_wrapped_text(
        draw,
        (76, title_bottom + 34),
        scene["subtitle"],
        subtitle_font,
        (239, 247, 243, 230),
        820,
        spacing=8,
    )

    accent_box = (76, 820, 76 + max(230, len(scene["accent"]) * 19), 882)
    rounded_panel(draw, accent_box, (5, 28, 20, 220), outline=MINT, radius=31, width=2)
    draw.text(
        (accent_box[0] + 28, 851),
        scene["accent"],
        font=accent_font,
        fill=MINT,
        anchor="lm",
    )


def draw_metric_cards(draw: ImageDraw.ImageDraw) -> None:
    labels = [("100s", "of household items"), ("1 by 1", "manual preparation"), ("CAT surge", "amplifies the load")]
    x = 1080
    for i, (value, label) in enumerate(labels):
        top = 235 + i * 184
        rounded_panel(draw, (x, top, 1780, top + 142), (5, 28, 20, 190), outline=(185, 228, 201, 150))
        draw.text((x + 36, top + 28), value, font=ImageFont.truetype(FONT_BOLD, 42), fill=WHITE)
        draw.text((x + 36, top + 88), label, font=ImageFont.truetype(FONT_REGULAR, 25), fill=MINT)


def draw_principle(draw: ImageDraw.ImageDraw) -> None:
    rounded_panel(draw, (1075, 255, 1790, 735), (5, 28, 20, 198), outline=(185, 228, 201, 135))
    center_x = 1432
    steps = [
        ("AGENT", "prepares"),
        ("EVIDENCE", "stays visible"),
        ("ADJUSTER", "decides"),
    ]
    for i, (title, subtitle) in enumerate(steps):
        y = 345 + i * 135
        draw.ellipse((1125, y - 30, 1185, y + 30), fill=BRIGHT_GREEN)
        draw.text((1155, y), str(i + 1), font=ImageFont.truetype(FONT_BOLD, 24), fill=INK, anchor="mm")
        draw.text((1220, y - 22), title, font=ImageFont.truetype(FONT_BOLD, 29), fill=WHITE)
        draw.text((1220, y + 20), subtitle, font=ImageFont.truetype(FONT_REGULAR, 23), fill=MINT)
        if i < 2:
            draw.line((1155, y + 38, 1155, y + 96), fill=BRIGHT_GREEN, width=4)
    draw.text((center_x, 680), "NO AUTONOMOUS SETTLEMENT", font=ImageFont.truetype(FONT_SEMIBOLD, 21), fill=AMBER, anchor="mm")


def draw_architecture(draw: ImageDraw.ImageDraw) -> None:
    cards = [
        ("COPILOT", "guides"),
        ("WORKFLOWS", "enforce"),
        ("SERVICES", "calculate"),
        ("DATAVERSE", "remembers"),
    ]
    x0 = 1010
    for i, (title, subtitle) in enumerate(cards):
        x = x0 + (i % 2) * 390
        y = 250 + (i // 2) * 250
        rounded_panel(draw, (x, y, x + 340, y + 195), (5, 28, 20, 200), outline=(185, 228, 201, 150))
        draw.text((x + 28, y + 38), f"0{i + 1}", font=ImageFont.truetype(FONT_BOLD, 26), fill=BRIGHT_GREEN)
        draw.text((x + 28, y + 91), title, font=ImageFont.truetype(FONT_BOLD, 27), fill=WHITE)
        draw.text((x + 28, y + 138), subtitle, font=ImageFont.truetype(FONT_REGULAR, 23), fill=MINT)


def draw_journey(draw: ImageDraw.ImageDraw) -> None:
    labels = ["OPEN", "PREPARE", "RESEARCH", "QUALITY", "DECIDE"]
    left = 1010
    top = 340
    gap = 140
    for i, label in enumerate(labels):
        x = left + i * gap
        draw.ellipse((x, top, x + 78, top + 78), fill=BRIGHT_GREEN if i < 4 else WHITE)
        draw.text(
            (x + 39, top + 39),
            str(i + 1),
            font=ImageFont.truetype(FONT_BOLD, 25),
            fill=INK,
            anchor="mm",
        )
        draw.text(
            (x + 39, top + 112),
            label,
            font=ImageFont.truetype(FONT_SEMIBOLD, 19),
            fill=WHITE,
            anchor="mm",
        )
        if i < len(labels) - 1:
            draw.line((x + 83, top + 39, x + gap - 6, top + 39), fill=(255, 255, 255, 165), width=4)
    rounded_panel(draw, (1000, 565, 1785, 690), (5, 28, 20, 190), outline=(185, 228, 201, 120))
    draw.text((1036, 600), "Every gate is explicit.", font=ImageFont.truetype(FONT_BOLD, 28), fill=WHITE)
    draw.text((1036, 645), "Every exception has a path.", font=ImageFont.truetype(FONT_REGULAR, 25), fill=MINT)


def draw_workspace(draw: ImageDraw.ImageDraw) -> None:
    cards = [
        ("INVENTORY", "normalized items"),
        ("EVIDENCE", "qualified sources"),
        ("CALCULATION", "reproducible trace"),
        ("EXCEPTIONS", "visible and routed"),
    ]
    for i, (title, subtitle) in enumerate(cards):
        x = 1030 + (i % 2) * 365
        y = 250 + (i // 2) * 240
        rounded_panel(draw, (x, y, x + 325, y + 184), (247, 250, 248, 225), outline=GREEN)
        draw.rectangle((x, y, x + 10, y + 184), fill=BRIGHT_GREEN)
        draw.text((x + 34, y + 43), title, font=ImageFont.truetype(FONT_BOLD, 25), fill=GREEN)
        draw.text((x + 34, y + 101), subtitle, font=ImageFont.truetype(FONT_REGULAR, 23), fill=INK)


def draw_decision(draw: ImageDraw.ImageDraw) -> None:
    labels = ["APPROVE", "CORRECT", "RESEARCH", "HOLD"]
    for i, label in enumerate(labels):
        x = 1050 + (i % 2) * 360
        y = 290 + (i // 2) * 190
        fill = BRIGHT_GREEN if i == 0 else (255, 255, 255, 218)
        text_fill = INK if i == 0 else GREEN
        rounded_panel(draw, (x, y, x + 310, y + 142), fill, outline=MINT)
        draw.text((x + 155, y + 71), label, font=ImageFont.truetype(FONT_BOLD, 25), fill=text_fill, anchor="mm")
    draw.text((1405, 720), "LICENSED-ADJUSTER AUTHORITY", font=ImageFont.truetype(FONT_SEMIBOLD, 22), fill=MINT, anchor="mm")


def draw_package(draw: ImageDraw.ImageDraw) -> None:
    rounded_panel(draw, (1060, 220, 1750, 750), (247, 250, 248, 228), outline=GREEN)
    draw.text((1110, 275), "VALUATION PACKAGE", font=ImageFont.truetype(FONT_BOLD, 31), fill=GREEN)
    rows = [
        "Workbook and item detail",
        "Replacement evidence",
        "Depreciation and ACV",
        "Exceptions and rationale",
        "Version and audit history",
    ]
    for i, row in enumerate(rows):
        y = 355 + i * 72
        draw.ellipse((1110, y, 1142, y + 32), fill=BRIGHT_GREEN)
        draw.line((1118, y + 16, 1124, y + 23), fill=INK, width=3)
        draw.line((1124, y + 23, 1135, y + 9), fill=INK, width=3)
        draw.text((1170, y + 16), row, font=ImageFont.truetype(FONT_REGULAR, 25), fill=INK, anchor="lm")


def draw_value(draw: ImageDraw.ImageDraw) -> None:
    statements = [
        ("FASTER", "claim preparation"),
        ("STRONGER", "audit readiness"),
        ("BETTER", "adjuster experience"),
    ]
    for i, (headline, detail) in enumerate(statements):
        y = 265 + i * 180
        rounded_panel(draw, (1060, y, 1775, y + 135), (5, 28, 20, 190), outline=(185, 228, 201, 140))
        draw.text((1100, y + 35), headline, font=ImageFont.truetype(FONT_BOLD, 31), fill=BRIGHT_GREEN)
        draw.text((1100, y + 86), detail, font=ImageFont.truetype(FONT_REGULAR, 25), fill=WHITE)


def draw_closing(draw: ImageDraw.ImageDraw) -> None:
    rounded_panel(draw, (1030, 300, 1785, 665), (5, 28, 20, 210), outline=(185, 228, 201, 150))
    points = [
        "Transparent recommendation",
        "Deterministic calculation",
        "Professional accountability",
    ]
    for i, point in enumerate(points):
        y = 375 + i * 90
        draw.ellipse((1090, y - 18, 1126, y + 18), fill=BRIGHT_GREEN)
        draw.text((1160, y), point, font=ImageFont.truetype(FONT_SEMIBOLD, 27), fill=WHITE, anchor="lm")


def draw_summary(draw: ImageDraw.ImageDraw) -> None:
    stages = [
        ("01", "OPEN +\nAUTHORIZE"),
        ("02", "PREPARE\nINVENTORY"),
        ("03", "RESEARCH +\nVALUE"),
        ("04", "QUALITY +\nPACKAGE"),
        ("05", "DECIDE +\nTRACK"),
    ]
    left = 860
    top = 280
    card_w = 180
    gap = 22
    for index, (number, label) in enumerate(stages):
        x = left + index * (card_w + gap)
        fill = (247, 250, 248, 235) if index < 4 else (84, 184, 72, 245)
        text_fill = GREEN if index < 4 else INK
        rounded_panel(draw, (x, top, x + card_w, top + 270), fill, outline=MINT, radius=26)
        draw.text((x + 26, top + 34), number, font=ImageFont.truetype(FONT_BOLD, 27), fill=text_fill)
        draw.multiline_text(
            (x + 26, top + 105),
            label,
            font=ImageFont.truetype(FONT_BOLD, 23),
            fill=text_fill,
            spacing=10,
        )
        if index < len(stages) - 1:
            arrow_x = x + card_w + 5
            arrow_y = top + 135
            draw.line((arrow_x, arrow_y, arrow_x + 18, arrow_y), fill=WHITE, width=4)
            draw.polygon(
                [
                    (arrow_x + 18, arrow_y - 8),
                    (arrow_x + 31, arrow_y),
                    (arrow_x + 18, arrow_y + 8),
                ],
                fill=WHITE,
            )

    rounded_panel(draw, (860, 610, 1870, 735), (5, 28, 20, 220), outline=(185, 228, 201, 160))
    footer = "Copilot guides  |  Workflows enforce  |  Services calculate  |  Dataverse remembers  |  Adjuster decides"
    draw.multiline_text(
        (910, 650),
        footer,
        font=ImageFont.truetype(FONT_SEMIBOLD, 20),
        fill=MINT,
        spacing=8,
    )


def render_scene(scene: dict[str, str], index: int) -> Path:
    image_path = STOCK / scene["image"]
    focus_x = 0.62 if scene["image"] in {"adjuster.jpg", "decision.jpg"} else 0.5
    source = Image.open(image_path).convert("RGB")
    if scene["image"] == "adjuster.jpg":
        source = source.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    background = fit_cover(source, (WIDTH, HEIGHT), focus_x=focus_x)
    background = ImageEnhance.Color(background).enhance(0.82)
    background = ImageEnhance.Contrast(background).enhance(1.08)
    background = background.filter(ImageFilter.GaussianBlur(radius=0.35))
    canvas = add_gradient_overlay(background, dark_right=scene["layout"] == "closing")
    draw = ImageDraw.Draw(canvas, "RGBA")

    draw.rectangle((0, 0, WIDTH, 14), fill=BRIGHT_GREEN)
    draw.rectangle((0, 14, WIDTH, 25), fill=GREEN)
    draw_brand(draw)
    draw_common_text(draw, scene)
    draw_progress(draw, index)

    layout = scene["layout"]
    if layout == "metrics":
        draw_metric_cards(draw)
    elif layout == "principle":
        draw_principle(draw)
    elif layout == "architecture":
        draw_architecture(draw)
    elif layout == "journey":
        draw_journey(draw)
    elif layout == "workspace":
        draw_workspace(draw)
    elif layout == "decision":
        draw_decision(draw)
    elif layout == "package":
        draw_package(draw)
    elif layout == "value":
        draw_value(draw)
    elif layout == "closing":
        draw_closing(draw)
    elif layout == "summary":
        draw_summary(draw)

    SCENES_DIR.mkdir(parents=True, exist_ok=True)
    output = SCENES_DIR / f"scene_{index + 1:02d}.png"
    canvas.convert("RGB").save(output, quality=96)
    return output


def find_ffmpeg() -> Path:
    candidates = glob.glob(
        str(
            Path.home()
            / "AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg*/ffmpeg-*/bin/ffmpeg.exe"
        )
    )
    if not candidates:
        raise FileNotFoundError("FFmpeg was not found in the WinGet package directory.")
    return Path(sorted(candidates)[-1])


def run(command: list[str]) -> None:
    subprocess.run(command, check=True)


def render_clips(ffmpeg: Path, scene_paths: list[Path]) -> list[Path]:
    CLIPS_DIR.mkdir(parents=True, exist_ok=True)
    clips: list[Path] = []
    for index, scene_path in enumerate(scene_paths):
        base_duration = BOUNDARIES[index + 1] - BOUNDARIES[index]
        clip_duration = base_duration + (FADE if index < len(scene_paths) - 1 else 0)
        output = CLIPS_DIR / f"clip_{index + 1:02d}.mp4"
        run(
            [
                str(ffmpeg),
                "-hide_banner",
                "-loglevel",
                "error",
                "-loop",
                "1",
                "-i",
                str(scene_path),
                "-vf",
                f"scale={WIDTH}:{HEIGHT}:flags=lanczos,fps={FPS},format=yuv420p",
                "-t",
                f"{clip_duration:.3f}",
                "-an",
                "-c:v",
                "libx264",
                "-preset",
                "medium",
                "-crf",
                "18",
                "-movflags",
                "+faststart",
                "-y",
                str(output),
            ]
        )
        clips.append(output)
    return clips


def assemble_video(ffmpeg: Path, clips: list[Path]) -> None:
    command = [str(ffmpeg), "-hide_banner", "-loglevel", "error"]
    for clip in clips:
        command.extend(["-i", str(clip)])
    command.extend(["-i", str(AUDIO)])

    filters: list[str] = []
    current = "[0:v]"
    cumulative = BOUNDARIES[1]
    for index in range(1, len(clips)):
        output_label = f"[v{index}]"
        filters.append(
            f"{current}[{index}:v]xfade=transition=fade:"
            f"duration={FADE}:offset={cumulative:.3f}{output_label}"
        )
        current = output_label
        cumulative = BOUNDARIES[index + 1]

    audio_index = len(clips)
    filters.append(
        f"[{audio_index}:a]"
        "highpass=f=80,"
        "lowpass=f=12000,"
        "afftdn=nf=-24,"
        "dynaudnorm=f=150:g=7:p=0.9,"
        "loudnorm=I=-16:TP=-1.5:LRA=7,"
        "apad=pad_dur=10"
        "[aout]"
    )

    command.extend(
        [
            "-filter_complex",
            ";".join(filters),
            "-map",
            current,
            "-map",
            "[aout]",
            "-c:v",
            "libx264",
            "-preset",
            "slow",
            "-crf",
            "18",
            "-profile:v",
            "high",
            "-level",
            "4.1",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-ar",
            "48000",
            "-t",
            f"{BOUNDARIES[-1]:.3f}",
            "-movflags",
            "+faststart",
            "-metadata",
            "title=CAT Contents Agent - Professional Use Case Demo",
            "-y",
            str(OUTPUT),
        ]
    )
    run(command)


def main() -> None:
    ffmpeg = find_ffmpeg()
    scene_paths = [render_scene(scene, index) for index, scene in enumerate(SCENES)]
    clips = render_clips(ffmpeg, scene_paths)
    assemble_video(ffmpeg, clips)
    print(OUTPUT)


if __name__ == "__main__":
    main()
