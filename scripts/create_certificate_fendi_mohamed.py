from __future__ import annotations

import random
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "output" / "pdf"
PDF_PATH = OUT_DIR / "certificate_fendi_mohamed.pdf"
FONT_DIR = Path("C:/Windows/Fonts")


def register_font(name: str, filename: str, fallback: str) -> str:
    path = FONT_DIR / filename
    if not path.exists():
        return fallback
    pdfmetrics.registerFont(TTFont(name, str(path)))
    return name


FONT_SERIF = register_font("GeorgiaCustom", "georgia.ttf", "Times-Roman")
FONT_SERIF_BOLD = register_font("GeorgiaBoldCustom", "georgiab.ttf", "Times-Bold")
FONT_SERIF_ITALIC = register_font("GeorgiaItalicCustom", "georgiai.ttf", "Times-Italic")
FONT_NAME = register_font("GabriolaCustom", "Gabriola.ttf", FONT_SERIF_ITALIC)


def hex_color(value: str) -> colors.Color:
    return colors.HexColor(value)


def set_alpha(c: canvas.Canvas, fill: float | None = None, stroke: float | None = None) -> None:
    if fill is not None and hasattr(c, "setFillAlpha"):
        c.setFillAlpha(fill)
    if stroke is not None and hasattr(c, "setStrokeAlpha"):
        c.setStrokeAlpha(stroke)


def draw_relief_path(
    c: canvas.Canvas,
    path,
    width: float = 1.0,
    shadow: str = "#c8c5ba",
    highlight: str = "#ffffff",
    alpha_shadow: float = 0.42,
    alpha_highlight: float = 0.78,
) -> None:
    c.saveState()
    c.translate(0.45, -0.45)
    c.setLineWidth(width)
    c.setStrokeColor(hex_color(shadow))
    set_alpha(c, stroke=alpha_shadow)
    c.drawPath(path, stroke=1, fill=0)
    c.restoreState()

    c.saveState()
    c.translate(-0.45, 0.45)
    c.setLineWidth(width)
    c.setStrokeColor(hex_color(highlight))
    set_alpha(c, stroke=alpha_highlight)
    c.drawPath(path, stroke=1, fill=0)
    c.restoreState()


def draw_rotated_ellipse(
    c: canvas.Canvas,
    x: float,
    y: float,
    rx: float,
    ry: float,
    angle: float,
    stroke: str,
    alpha: float,
    width: float = 0.8,
) -> None:
    c.saveState()
    c.translate(x, y)
    c.rotate(angle)
    c.setStrokeColor(hex_color(stroke))
    c.setLineWidth(width)
    set_alpha(c, stroke=alpha)
    c.ellipse(-rx, -ry, rx, ry, stroke=1, fill=0)
    c.restoreState()


def draw_corner(c: canvas.Canvas, x: float, y: float, sx: int, sy: int) -> None:
    c.saveState()
    c.translate(x, y)
    c.scale(sx, sy)

    p = c.beginPath()
    p.moveTo(0, 0)
    p.curveTo(21, 9, 38, 26, 45, 52)
    p.curveTo(51, 75, 69, 91, 96, 98)
    p.curveTo(66, 106, 36, 92, 18, 67)
    p.curveTo(3, 45, 0, 24, 0, 0)
    c.saveState()
    c.setFillColor(hex_color("#eceae2"))
    set_alpha(c, fill=0.66)
    c.drawPath(p, stroke=0, fill=1)
    c.restoreState()

    for builder in (
        lambda: _path_curve(c, [(8, 21), (33, 8, 65, 10, 91, 33), (61, 33, 39, 50, 31, 81)]),
        lambda: _path_curve(c, [(20, 95), (47, 74, 75, 80, 96, 110), (66, 99, 43, 103, 18, 126)]),
        lambda: _path_curve(c, [(70, 6), (84, 35, 82, 70, 59, 103), (91, 83, 106, 50, 105, 20)]),
        lambda: _path_curve(c, [(18, 45), (42, 37, 57, 45, 64, 67), (43, 68, 33, 79, 34, 99)]),
    ):
        draw_relief_path(c, builder(), width=1.25)

    draw_rotated_ellipse(c, 86, 43, 8, 22, 33, "#cbc8be", 0.45, 0.95)
    draw_rotated_ellipse(c, 54, 105, 7, 19, -50, "#ffffff", 0.78, 0.95)
    c.saveState()
    c.setStrokeColor(hex_color("#cbc8be"))
    set_alpha(c, stroke=0.42)
    c.setLineWidth(1)
    c.circle(90, 85, 8, stroke=1, fill=0)
    c.restoreState()
    c.restoreState()


def _path_curve(c: canvas.Canvas, commands):
    p = c.beginPath()
    first = commands[0]
    p.moveTo(first[0], first[1])
    for cmd in commands[1:]:
        p.curveTo(*cmd)
    return p


def draw_side_vine(c: canvas.Canvas, x: float, y: float, height: float, flip: int = 1) -> None:
    c.saveState()
    c.translate(x, y)
    c.scale(flip, 1)

    segment = height / 4
    p = c.beginPath()
    p.moveTo(0, 0)
    p.curveTo(20, segment * 0.25, -20, segment * 0.75, 0, segment)
    p.curveTo(20, segment * 1.25, -20, segment * 1.75, 0, segment * 2)
    p.curveTo(20, segment * 2.25, -20, segment * 2.75, 0, segment * 3)
    p.curveTo(20, segment * 3.25, -20, segment * 3.75, 0, segment * 4)
    draw_relief_path(c, p, width=1.0, alpha_shadow=0.34, alpha_highlight=0.74)

    for yy, angle, side in ((segment * 0.7, 35, 1), (segment * 1.65, -35, -1), (segment * 2.6, 35, 1), (segment * 3.45, -35, -1)):
        draw_rotated_ellipse(c, 16 * side, yy, 5.2, 13.5, angle, "#d2cfc6" if side > 0 else "#ffffff", 0.48 if side > 0 else 0.74, 0.75)

    c.restoreState()


def draw_damask(c: canvas.Canvas, w: float, h: float) -> None:
    c.saveState()
    c.setLineWidth(0.55)
    for cx in (w * 0.33, w * 0.5, w * 0.67):
        for cy in (h * 0.34, h * 0.5, h * 0.66):
            p = c.beginPath()
            p.moveTo(cx, cy + 52)
            p.curveTo(cx + 30, cy + 25, cx + 30, cy - 25, cx, cy - 52)
            p.curveTo(cx - 30, cy - 25, cx - 30, cy + 25, cx, cy + 52)
            draw_relief_path(c, p, width=0.62, alpha_shadow=0.18, alpha_highlight=0.48)
            p2 = c.beginPath()
            p2.moveTo(cx - 54, cy)
            p2.curveTo(cx - 24, cy + 28, cx + 24, cy + 28, cx + 54, cy)
            p2.curveTo(cx + 24, cy - 28, cx - 24, cy - 28, cx - 54, cy)
            draw_relief_path(c, p2, width=0.55, alpha_shadow=0.16, alpha_highlight=0.44)
    c.restoreState()


def draw_grain(c: canvas.Canvas, w: float, h: float) -> None:
    rng = random.Random(2026)
    c.saveState()
    for _ in range(260):
        x = rng.uniform(10 * mm, w - 10 * mm)
        y = rng.uniform(10 * mm, h - 10 * mm)
        radius = rng.uniform(0.08, 0.35)
        if rng.random() < 0.55:
            c.setFillColor(hex_color("#c8c5ba"))
            set_alpha(c, fill=rng.uniform(0.04, 0.09))
        else:
            c.setFillColor(hex_color("#ffffff"))
            set_alpha(c, fill=rng.uniform(0.12, 0.24))
        c.circle(x, y, radius, stroke=0, fill=1)
    c.restoreState()


def draw_cap(c: canvas.Canvas, center_x: float, top_y: float) -> None:
    c.saveState()
    c.translate(center_x - 47, top_y - 62)
    c.setFillColor(hex_color("#050505"))
    c.setStrokeColor(hex_color("#333333"))
    c.setLineWidth(0.8)

    p = c.beginPath()
    p.moveTo(47, 62)
    p.lineTo(94, 42)
    p.lineTo(47, 22)
    p.lineTo(0, 42)
    p.close()
    c.drawPath(p, stroke=1, fill=1)

    body = c.beginPath()
    body.moveTo(22, 32)
    body.curveTo(36, 44, 58, 44, 72, 32)
    body.lineTo(72, 8)
    body.curveTo(55, 16, 39, 16, 22, 8)
    body.close()
    c.drawPath(body, stroke=0, fill=1)

    c.setStrokeColor(hex_color("#737373"))
    c.setLineWidth(2.5)
    c.bezier(22, 32, 36, 44, 58, 44, 72, 32)

    c.setStrokeColor(hex_color("#050505"))
    c.setLineWidth(2.2)
    c.line(12, 39, 12, 17)
    tassel = c.beginPath()
    tassel.moveTo(12, 17)
    tassel.curveTo(6, 11, 4, 3, 4, -2)
    tassel.lineTo(20, -2)
    tassel.curveTo(20, 3, 18, 11, 12, 17)
    tassel.close()
    c.drawPath(tassel, stroke=0, fill=1)
    c.restoreState()


def draw_arabesque(c: canvas.Canvas, center_x: float, y: float) -> None:
    c.saveState()
    c.translate(center_x - 183, y)
    c.setStrokeColor(hex_color("#4b4b4b"))
    set_alpha(c, stroke=0.88)
    c.setLineWidth(1.35)
    p = c.beginPath()
    p.moveTo(0, 8)
    p.curveTo(42, 28, 82, 28, 122, 8)
    p.curveTo(151, -6, 173, -6, 183, 8)
    p.curveTo(193, -6, 215, -6, 244, 8)
    p.curveTo(284, 28, 324, 28, 366, 8)
    c.drawPath(p, stroke=1, fill=0)

    c.setStrokeColor(hex_color("#818181"))
    set_alpha(c, stroke=0.8)
    c.setLineWidth(0.9)
    c.bezier(48, 8, 70, -3, 96, -3, 118, 8)
    c.bezier(248, 8, 270, -3, 296, -3, 318, 8)
    c.setFillColor(hex_color("#444444"))
    set_alpha(c, fill=0.88)
    c.circle(183, 8, 2.6, stroke=0, fill=1)
    c.circle(18, 8, 1.9, stroke=0, fill=1)
    c.circle(348, 8, 1.9, stroke=0, fill=1)
    c.restoreState()


def draw_centered(c: canvas.Canvas, text: str, x: float, y: float, font: str, size: float, color: str = "#111111") -> float:
    c.setFont(font, size)
    c.setFillColor(hex_color(color))
    set_alpha(c, fill=1)
    c.drawCentredString(x, y, text)
    return y


def draw_centered_lines(
    c: canvas.Canvas,
    lines: list[str],
    x: float,
    y: float,
    font: str,
    size: float,
    leading: float,
    color: str = "#111111",
) -> float:
    c.setFont(font, size)
    c.setFillColor(hex_color(color))
    set_alpha(c, fill=1)
    current = y
    for line in lines:
        c.drawCentredString(x, current, line)
        current -= leading
    return current


def draw_certificate() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    w, h = A4
    c = canvas.Canvas(str(PDF_PATH), pagesize=A4)
    c.setTitle("Fendi Mohamed - Commemorative Certificate of Graduation")
    c.setAuthor("OpenAI Codex")
    c.setSubject("Personal commemorative graduation certificate, not an official diploma")

    c.setFillColor(hex_color("#fbfaf6"))
    c.rect(0, 0, w, h, stroke=0, fill=1)

    # Ivory page relief.
    c.saveState()
    c.setFillColor(hex_color("#f3f1eb"))
    set_alpha(c, fill=0.34)
    c.rect(6 * mm, 6 * mm, w - 12 * mm, h - 12 * mm, stroke=0, fill=1)
    c.restoreState()
    draw_damask(c, w, h)
    draw_grain(c, w, h)

    # Layered embossed border.
    for inset, stroke, width, alpha in (
        (10 * mm, "#c9c6bd", 1.5, 0.55),
        (12.6 * mm, "#ffffff", 1.2, 0.9),
        (19 * mm, "#cac7be", 0.75, 0.5),
        (22.4 * mm, "#ffffff", 0.8, 0.82),
    ):
        c.saveState()
        c.setStrokeColor(hex_color(stroke))
        set_alpha(c, stroke=alpha)
        c.setLineWidth(width)
        c.rect(inset, inset, w - 2 * inset, h - 2 * inset, stroke=1, fill=0)
        c.restoreState()

    corner_anchor_x = 19 * mm
    corner_anchor_y = 19 * mm
    draw_corner(c, corner_anchor_x, corner_anchor_y, 1, 1)
    draw_corner(c, w - corner_anchor_x, corner_anchor_y, -1, 1)
    draw_corner(c, corner_anchor_x, h - corner_anchor_y, 1, -1)
    draw_corner(c, w - corner_anchor_x, h - corner_anchor_y, -1, -1)
    draw_side_vine(c, 24 * mm, 102 * mm, 106 * mm, 1)
    draw_side_vine(c, w - 24 * mm, 102 * mm, 106 * mm, -1)

    cx = w / 2
    draw_cap(c, cx, h - 40 * mm)
    draw_arabesque(c, cx, h - 62 * mm)

    y = h - 84 * mm
    y = draw_centered_lines(
        c,
        ["COMMEMORATIVE CERTIFICATE", "OF GRADUATION"],
        cx,
        y,
        FONT_SERIF_BOLD,
        20.5,
        8.4 * mm,
    )

    y -= 8 * mm
    draw_centered(c, "Presented to", cx, y, FONT_SERIF_ITALIC, 14.2)

    y -= 19 * mm
    draw_centered(c, "FENDI MOHAMED", cx, y, FONT_NAME, 57)

    y -= 15 * mm
    y = draw_centered_lines(
        c,
        [
            "In recognition of the successful completion of the academic journey",
            "and the achievement of two degrees:",
        ],
        cx,
        y,
        FONT_SERIF,
        11.6,
        6 * mm,
    )

    y -= 3.5 * mm
    y = draw_centered_lines(
        c,
        ["State Engineer Diploma", "and", "Master's Degree in Computer Systems Engineering"],
        cx,
        y,
        FONT_SERIF_BOLD,
        15.2,
        7.1 * mm,
    )

    y -= 5.8 * mm
    draw_centered(c, "Awarded by", cx, y, FONT_SERIF_BOLD, 12.3)

    y -= 7.2 * mm
    draw_centered(
        c,
        "Higher School of Computer Science -08 May 1945- of Sidi Bel Abbes",
        cx,
        y,
        FONT_SERIF,
        11.9,
    )

    y -= 20 * mm
    draw_centered_lines(
        c,
        [
            "The journey was not easy,",
            "but your strength was greater than every challenge.",
        ],
        cx,
        y,
        FONT_SERIF_ITALIC,
        13.4,
        7.2 * mm,
    )

    draw_centered(c, "Class of 2026", cx, 38 * mm, FONT_SERIF_BOLD, 25.5)

    c.showPage()
    c.save()
    print(PDF_PATH)


if __name__ == "__main__":
    draw_certificate()
