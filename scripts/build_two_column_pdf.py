from pathlib import Path
import re
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, Frame, HRFlowable, KeepTogether, PageTemplate,
    Paragraph, Spacer, Table, TableStyle, PageBreak,
)

ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = ROOT / "papers" / "INTEGRATED_MANUSCRIPT_DRAFT.md"
REFERENCES = ROOT / "papers" / "REFERENCES_DRAFT.md"
OUTPUT = ROOT / "output" / "pdf" / "MANUSCRIPT_TWO_COLUMN.pdf"

pdfmetrics.registerFont(TTFont("PaperSerif", r"C:\Windows\Fonts\times.ttf"))
pdfmetrics.registerFont(TTFont("PaperSerif-Bold", r"C:\Windows\Fonts\timesbd.ttf"))
pdfmetrics.registerFont(TTFont("PaperSerif-Italic", r"C:\Windows\Fonts\timesi.ttf"))
pdfmetrics.registerFont(TTFont("PaperMono", r"C:\Windows\Fonts\consola.ttf"))

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(
    name="PaperBody", fontName="PaperSerif", fontSize=9.0, leading=10.6,
    spaceAfter=4, alignment=TA_LEFT, splitLongWords=1,
))
styles.add(ParagraphStyle(
    name="PaperAbstract", fontName="PaperSerif-Bold", fontSize=8.7,
    leading=10.1, spaceAfter=4, alignment=TA_LEFT, splitLongWords=1,
))
styles.add(ParagraphStyle(
    name="PaperSection", fontName="PaperSerif-Bold", fontSize=10.5,
    leading=12, spaceBefore=7, spaceAfter=4, keepWithNext=1,
))
styles.add(ParagraphStyle(
    name="PaperSubsection", fontName="PaperSerif-Italic", fontSize=9.5,
    leading=11, spaceBefore=5, spaceAfter=3, keepWithNext=1,
))
styles.add(ParagraphStyle(
    name="PaperParagraph", fontName="PaperSerif-Bold", fontSize=9.0,
    leading=10, spaceBefore=4, spaceAfter=3, keepWithNext=1,
))
styles.add(ParagraphStyle(
    name="PaperTitle", fontName="PaperSerif", fontSize=20,
    leading=18, alignment=TA_CENTER, spaceAfter=8,
))
styles.add(ParagraphStyle(
    name="PaperCaption", fontName="PaperSerif", fontSize=7.8,
    leading=8.5, alignment=TA_LEFT, textColor=colors.HexColor("#333333"),
    spaceBefore=3, spaceAfter=4,
))
styles.add(ParagraphStyle(
    name="PaperRef", fontName="PaperSerif", fontSize=7.5, leading=8.7,
    leftIndent=10, firstLineIndent=-10, spaceAfter=3,
))
styles.add(ParagraphStyle(
    name="PaperBullet", fontName="PaperSerif", fontSize=8.8, leading=10.3,
    leftIndent=10, firstLineIndent=-7, spaceAfter=2,
))


def inline(text: str) -> str:
    text = text.strip()
    placeholders = []

    def hold(value: str) -> str:
        placeholders.append(value)
        return f"@@P{len(placeholders)-1}@@"

    text = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)",
                  lambda m: hold(f'<link href="{escape(m.group(2))}" color="#0645ad">{escape(m.group(1))}</link>'), text)
    text = re.sub(r"`([^`]+)`", lambda m: hold(f'<font name="PaperMono">{escape(m.group(1))}</font>'), text)
    text = escape(text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<i>\1</i>", text)
    for i, value in enumerate(placeholders):
        text = text.replace(f"@@P{i}@@", value)
    return text


def table_flow(rows):
    if not rows:
        return []
    n = max(len(row) for row in rows)
    rows = [row + [""] * (n - len(row)) for row in rows]
    available = 8.2 * cm
    if n == 3:
        widths = [available * 0.23, available * 0.43, available * 0.34]
    elif n == 4:
        widths = [available * 0.18, available * 0.29, available * 0.29, available * 0.24]
    else:
        widths = [available / n] * n
    data = []
    for r, row in enumerate(rows):
        style = styles["PaperCaption"]
        data.append([Paragraph(("<b>" if r == 0 else "") + inline(cell) + ("</b>" if r == 0 else ""), style) for cell in row])
    t = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e9eef5")),
        ("LINEBELOW", (0, 0), (-1, 0), 0.5, colors.HexColor("#4d5b6a")),
        ("GRID", (0, 0), (-1, -1), 0.2, colors.HexColor("#b8c0c8")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 2),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    return [Spacer(1, 3), t, Spacer(1, 4)]


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("PaperSerif", 7.5)
    canvas.setFillColor(colors.HexColor("#555555"))
    canvas.drawCentredString(letter[0] / 2, 0.55 * inch, f"{doc.page}")
    canvas.restoreState()


def build_story():
    lines = MANUSCRIPT.read_text(encoding="utf-8").splitlines()
    story = []
    paragraph = []
    table_rows = []
    in_fence = False
    in_quote = False
    in_refs = False
    current_section = ""
    abstract_first = True

    def flush_para():
        nonlocal paragraph, abstract_first
        if paragraph:
            text = " ".join(x.strip() for x in paragraph)
            if text:
                if current_section == "Abstract":
                    prefix = "<b>Abstract—</b>" if abstract_first else ""
                    story.append(Paragraph(prefix + inline(text), styles["PaperAbstract"]))
                    abstract_first = False
                else:
                    story.append(Paragraph(inline(text), styles["PaperBody"]))
            paragraph = []

    def flush_table():
        nonlocal table_rows
        if table_rows:
            story.extend(table_flow(table_rows))
            table_rows = []

    for line in lines:
        if line.startswith("```"):
            flush_para(); flush_table()
            if not in_fence:
                story.append(Paragraph("[Editable workflow/code diagram; see the source manuscript for the Mermaid definition.]", styles["PaperCaption"]))
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if line.startswith("## References"):
            flush_para(); flush_table(); in_refs = True
            story.append(Paragraph("References", styles["PaperSection"]))
            continue
        if in_refs:
            continue
        if line.startswith("|"):
            flush_para()
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if cells and not all(re.fullmatch(r":?-+:?", c) for c in cells):
                table_rows.append(cells)
            continue
        if table_rows:
            flush_table()
        if line.startswith("# Evidence-Gated"):
            continue
        m = re.match(r"^##\s+(?:\d+\.\s+)?(.+)$", line)
        if m:
            flush_para()
            current_section = m.group(1)
            if current_section == "Abstract":
                continue
            story.append(Paragraph(inline(current_section), styles["PaperSection"])); continue
        m = re.match(r"^###\s+(?:\d+\.\d+\s+)?(.+)$", line)
        if m:
            flush_para(); story.append(Paragraph(inline(m.group(1)), styles["PaperSubsection"])); continue
        m = re.match(r"^\*\*([^*]+)\*\*$", line)
        if m:
            flush_para(); story.append(Paragraph(inline(m.group(1)), styles["PaperParagraph"])); continue
        m = re.match(r"^\s*[-*]\s+(.+)$", line)
        if m:
            flush_para(); story.append(Paragraph("• " + inline(m.group(1)), styles["PaperBullet"])); continue
        m = re.match(r"^\s*\d+\.\s+(.+)$", line)
        if m:
            flush_para(); story.append(Paragraph(inline(m.group(1)), styles["PaperBullet"])); continue
        if line.startswith(">"):
            flush_para(); story.append(Paragraph("<i>" + inline(line[1:].strip()) + "</i>", styles["PaperCaption"])); continue
        if not line.strip():
            flush_para(); continue
        paragraph.append(line)
    flush_para(); flush_table()

    ref_blocks = []
    current = []
    for line in REFERENCES.read_text(encoding="utf-8").splitlines():
        if line.startswith("# References") or line.startswith(">"):
            continue
        if not line.strip():
            if current:
                ref_blocks.append(" ".join(current)); current = []
        else:
            current.append(line.strip())
    if current:
        ref_blocks.append(" ".join(current))
    for ref in ref_blocks:
        ref = re.sub(r"\*\*([^*]+)\*\*", r"\1", ref)
        ref = re.sub(r"\*([^*]+)\*", r"\1", ref)
        story.append(Paragraph(inline(ref), styles["PaperRef"]))
    return story


def first_page(canvas, doc):
    canvas.saveState()
    width, height = letter
    canvas.setFont("PaperSerif", 21)
    canvas.drawCentredString(width / 2, height - 1.05 * inch, "Evidence-Gated Recovery of Maven")
    canvas.drawCentredString(width / 2, height - 1.38 * inch, "Components from Compiled Android APKs")
    canvas.setFont("PaperSerif", 10.5)
    canvas.drawCentredString(width / 2, height - 1.78 * inch, "Implementation and experimental evaluation paper")
    canvas.setStrokeColor(colors.HexColor("#777777"))
    canvas.setLineWidth(0.5)
    canvas.line(0.72 * inch, height - 2.05 * inch, width - 0.72 * inch, height - 2.05 * inch)
    footer(canvas, doc)
    canvas.restoreState()


def main():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    page_width, page_height = letter
    margin = 0.72 * inch
    gap = 0.25 * inch
    col_width = (page_width - 2 * margin - gap) / 2
    first_height = page_height - 2.9 * inch
    regular_height = page_height - 1.35 * inch
    first_frames = [
        Frame(margin, 0.75 * inch, col_width, first_height, id="first1", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0),
        Frame(margin + col_width + gap, 0.75 * inch, col_width, first_height, id="first2", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0),
    ]
    regular_frames = [
        Frame(margin, 0.75 * inch, col_width, regular_height, id="regular1", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0),
        Frame(margin + col_width + gap, 0.75 * inch, col_width, regular_height, id="regular2", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0),
    ]
    doc = BaseDocTemplate(str(OUTPUT), pagesize=letter, leftMargin=margin, rightMargin=margin, topMargin=margin, bottomMargin=0.75 * inch, title="Evidence-Gated Recovery of Maven Components from Compiled Android APKs")
    doc.addPageTemplates([
        PageTemplate(id="First", frames=first_frames, onPage=first_page, autoNextPageTemplate="TwoColumn"),
        PageTemplate(id="TwoColumn", frames=regular_frames, onPage=footer),
    ])
    doc.build(build_story())
    print(OUTPUT)


if __name__ == "__main__":
    main()
