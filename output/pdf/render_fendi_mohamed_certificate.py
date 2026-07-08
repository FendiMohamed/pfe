from math import sin, cos, pi
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph


ROOT = Path(__file__).resolve().parents[2]
OUT_PDF = ROOT / "output" / "pdf" / "fendi_mohamed_commemorative_certificate.pdf"
FONT_DIR = Path("C:/Windows/Fonts")


def register_font(name, filename, fallback):
    path = FONT_DIR / filename
    if path.exists():
        pdfmetrics.registerFont(TTFont(name, str(path)))
        return name
    return fallback


BODY_FONT = register_font("PalatinoLocal", "pala.ttf", "Times-Roman")
BODY_BOLD = register_font("PalatinoBoldLocal", "palab.ttf", "Times-Bold")
BODY_ITALIC = register_font("PalatinoItalicLocal", "palai.ttf", "Times-Italic")
TITLE_FONT = register_font("GeorgiaBoldLocal", "georgiab.ttf", "Times-Bold")
NAME_FONT = register_font("GabriolaLocal", "Gabriola.ttf", BODY_ITALIC)


IVORY = colors.HexColor("#fbfaf4")
BLACK = colors.HexColor("#111111")
RAISED = colors.HexColor("#e4e1d8")
SHADOW = colors.HexColor("#d3d0c7")
HIGHLIGHT = colors.HexColor("#ffffff")
LINE = colors.HexColor("#cfcac0")


def draw_centered_tracking(c, text, y, font, size, tracking, fill=BLACK):
    widths = [pdfmetrics.stringWidth(ch, font, size) for ch in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x = A4[0] / 2 - total / 2
    c.setFont(font, size)
    c.setFillColor(fill)
    for ch, width in zip(text, widths):
        c.drawString(x, y, ch)
        x += width + tracking


def draw_leaf(c, x, y, rx, ry, angle, stroke, fill=None, width=0.55):
    c.saveState()
    c.translate(x, y)
    c.rotate(angle)
    c.setStrokeColor(stroke)
    c.setLineWidth(width)
    if fill:
        c.setFillColor(fill)
    c.ellipse(-rx, -ry, rx, ry, stroke=1, fill=1 if fill else 0)
    c.restoreState()


def draw_flower(c, x, y, scale, color, stroke_width=0.5):
    c.setStrokeColor(color)
    c.setLineWidth(stroke_width)
    for angle in range(0, 360, 60):
        draw_leaf(c, x + cos(angle * pi / 180) * scale * 1.4, y + sin(angle * pi / 180) * scale * 1.4, scale * 0.75, scale * 0.28, angle, color, None, stroke_width)
    c.circle(x, y, scale * 0.25, stroke=1, fill=0)


def ornamental_path(c, x, y, sx, sy, color, width=0.75):
    c.saveState()
    c.translate(x, y)
    c.scale(sx, sy)
    c.setStrokeColor(color)
    c.setLineWidth(width)
    p = c.beginPath()
    p.moveTo(0, 0)
    p.curveTo(18, 34, 52, 20, 47, 60)
    p.curveTo(44, 88, 82, 92, 78, 122)
    p.curveTo(75, 150, 117, 144, 124, 173)
    c.drawPath(p, stroke=1, fill=0)
    for lx, ly, angle in [(24, 25, 35), (43, 57, -34), (67, 83, 45), (79, 117, -40), (104, 144, 35)]:
        draw_leaf(c, lx, ly, 8, 3.4, angle, color, None, width)
    draw_flower(c, 49, 65, 4.2, color, width)
    draw_flower(c, 122, 172, 4.8, color, width)
    c.restoreState()


def draw_corner_ornament(c, x, y, sx, sy):
    for dx, dy, color, width in [(0.9, -0.9, SHADOW, 0.7), (-0.8, 0.8, HIGHLIGHT, 0.55), (0, 0, RAISED, 0.72)]:
        ornamental_path(c, x + dx, y + dy, sx, sy, color, width)


def draw_border(c, w, h):
    c.setFillColor(IVORY)
    c.rect(0, 0, w, h, fill=1, stroke=0)

    c.setStrokeColor(HIGHLIGHT)
    c.setLineWidth(1.6)
    c.rect(28, 31, w - 56, h - 62, fill=0, stroke=1)
    c.setStrokeColor(LINE)
    c.setLineWidth(0.8)
    c.rect(32, 35, w - 64, h - 70, fill=0, stroke=1)
    c.setStrokeColor(RAISED)
    c.setLineWidth(1.0)
    c.rect(46, 50, w - 92, h - 100, fill=0, stroke=1)

    # Embossed edge texture.
    c.setLineWidth(0.45)
    for i in range(44):
        x = 39 + i * (w - 78) / 43
        c.setStrokeColor(HIGHLIGHT if i % 2 else SHADOW)
        c.line(x, h - 44, x + 3, h - 39)
        c.line(x, 39, x + 3, 44)
    for i in range(60):
        y = 59 + i * (h - 118) / 59
        c.setStrokeColor(HIGHLIGHT if i % 2 else SHADOW)
        c.line(39, y, 44, y + 3)
        c.line(w - 39, y, w - 44, y + 3)

    # Corner and side floral ornaments.
    draw_corner_ornament(c, 55, 54, 1.0, 1.0)
    draw_corner_ornament(c, w - 55, 54, -1.0, 1.0)
    draw_corner_ornament(c, 55, h - 54, 1.0, -1.0)
    draw_corner_ornament(c, w - 55, h - 54, -1.0, -1.0)

    for base_y in [168, 326, 484]:
        draw_corner_ornament(c, 51, base_y, 0.58, 0.58)
        draw_corner_ornament(c, w - 51, base_y, -0.58, 0.58)


def draw_damask(c, w, h):
    c.saveState()
    c.setStrokeColor(colors.HexColor("#ebe8df"))
    c.setLineWidth(0.55)
    for offset in [-92, 0, 92]:
        cx = w / 2 + offset
        for y in [250, 370, 490, 610]:
            p = c.beginPath()
            p.moveTo(cx, y - 48)
            p.curveTo(cx - 52, y - 14, cx - 36, y + 30, cx, y + 47)
            p.curveTo(cx + 36, y + 30, cx + 52, y - 14, cx, y - 48)
            c.drawPath(p, stroke=1, fill=0)
            draw_leaf(c, cx - 25, y + 8, 11, 3.5, 48, colors.HexColor("#efede7"), None, 0.45)
            draw_leaf(c, cx + 25, y + 8, 11, 3.5, -48, colors.HexColor("#efede7"), None, 0.45)
    c.restoreState()


def draw_cap(c, cx, y, scale=1.0):
    c.saveState()
    c.translate(cx, y)
    c.scale(scale, scale)
    c.setFillColor(BLACK)
    c.setStrokeColor(BLACK)
    c.setLineJoin(1)
    p = c.beginPath()
    p.moveTo(-46, 0)
    p.lineTo(0, 20)
    p.lineTo(46, 0)
    p.lineTo(0, -20)
    p.close()
    c.drawPath(p, stroke=1, fill=1)
    p = c.beginPath()
    p.moveTo(-27, -8)
    p.curveTo(-18, -22, 18, -22, 27, -8)
    p.lineTo(27, -36)
    p.curveTo(11, -27, -11, -27, -27, -36)
    p.close()
    c.drawPath(p, stroke=1, fill=1)
    c.setLineWidth(2.2)
    c.line(-34, -6, -34, -48)
    c.roundRect(-39, -49, 10, 20, 3, stroke=0, fill=1)
    c.restoreState()


def paragraph(c, text, top_y, width, font, size, leading, italic=False, bold=False):
    style = ParagraphStyle(
        "centered",
        alignment=TA_CENTER,
        fontName=font,
        fontSize=size,
        leading=leading,
        textColor=BLACK,
        spaceAfter=0,
        spaceBefore=0,
    )
    p = Paragraph(text, style)
    _, height = p.wrap(width, 300)
    p.drawOn(c, (A4[0] - width) / 2, top_y - height)
    return top_y - height


def render():
    OUT_PDF.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(OUT_PDF), pagesize=A4)
    w, h = A4
    draw_border(c, w, h)
    draw_damask(c, w, h)

    draw_cap(c, w / 2, 719, 0.82)

    draw_centered_tracking(c, "COMMEMORATIVE CERTIFICATE", 654, TITLE_FONT, 22, 1.25)
    draw_centered_tracking(c, "OF GRADUATION", 626, TITLE_FONT, 14, 1.0)

    c.setFillColor(BLACK)
    c.setFont(BODY_FONT, 13.2)
    c.drawCentredString(w / 2, 586, "Presented to")

    c.setFont(NAME_FONT, 55)
    c.drawCentredString(w / 2, 523, "FENDI MOHAMED")
    c.setStrokeColor(LINE)
    c.setLineWidth(0.55)
    c.line(172, 505, w - 172, 505)

    body = "In recognition of the successful completion of his academic journey and the achievement of two degrees:"
    paragraph(c, body, 462, 410, BODY_FONT, 12.6, 18)

    c.setFont(BODY_BOLD, 14.3)
    c.drawCentredString(w / 2, 397, "State Engineer Diploma")
    c.setFont(BODY_FONT, 12.8)
    c.drawCentredString(w / 2, 374, "and")
    c.setFont(BODY_BOLD, 14.3)
    c.drawCentredString(w / 2, 349, "Master's Degree in Computer Systems Engineering")

    c.setFont(BODY_FONT, 12.8)
    c.drawCentredString(w / 2, 303, "Awarded by")
    paragraph(c, "Higher School of Computer Science -08 May 1945- of Sidi Bel Abbes", 277, 440, BODY_FONT, 12.9, 17)

    c.setFont(BODY_BOLD, 16.5)
    c.drawCentredString(w / 2, 218, "Class of 2026")

    paragraph(c, "Through dedication, patience, and perseverance, this achievement was earned.", 168, 420, BODY_ITALIC, 13.2, 18)

    c.showPage()
    c.save()


if __name__ == "__main__":
    render()
    print(OUT_PDF)
