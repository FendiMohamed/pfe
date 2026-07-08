import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { Presentation, PresentationFile } from "@oai/artifact-tool";
import { Canvas, loadImage } from "./node_modules/@oai/artifact-tool/node_modules/skia-canvas/lib/index.mjs";

const ROOT = path.dirname(fileURLToPath(import.meta.url));
const REPO = path.resolve(ROOT, "..", "..", "..", "..");
const CONTENT_PATH = path.join(REPO, "outputs", "graduation-defense-60-slide-content.txt");
const OUT_ROOT = path.join(REPO, "outputs", "graduation-defense-60-slide-deck");
const OUTPUT_DIR = path.join(OUT_ROOT, "output");
const PREVIEW_DIR = path.join(OUT_ROOT, "preview");
const LAYOUT_DIR = path.join(OUT_ROOT, "layout");
const QA_DIR = path.join(OUT_ROOT, "qa");
const ASSET_DIR = path.join(ROOT, "assets");
const PROOF_DIR = path.join(ASSET_DIR, "report-proof-screenshots");
const FINAL_PPTX = path.join(OUTPUT_DIR, "graduation-defense-60-slide-deck.pptx");

const C = {
  bg: "#F8FAFC",
  white: "#FFFFFF",
  ink: "#17212B",
  muted: "#5E6B78",
  faint: "#E6EBF1",
  line: "#CBD5E1",
  blue: "#2F5F7E",
  teal: "#4D817A",
  green: "#64785E",
  red: "#A85D57",
  amber: "#8C7346",
  paleBlue: "#EAF2F7",
  paleTeal: "#EAF3F1",
  paleGreen: "#EDF2E9",
  paleRed: "#F6EDEA",
  paleAmber: "#F4EFE5",
};

const sectionRanges = [
  [1, 6, "Introduction"],
  [7, 15, "Background"],
  [16, 26, "State of the Art"],
  [27, 34, "Contribution"],
  [35, 53, "Implementation"],
  [54, 58, "Demonstration"],
  [59, 60, "Conclusion"],
];

function sectionFor(index) {
  const row = sectionRanges.find(([start, end]) => index >= start && index <= end);
  return row ? row[2] : "Defense";
}

async function writeBlob(filePath, blob) {
  await fs.writeFile(filePath, new Uint8Array(await blob.arrayBuffer()));
}

async function readImage(filePath) {
  const bytes = await fs.readFile(filePath);
  return bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength);
}

function parseSlides(text) {
  const headers = [...text.matchAll(/^Slide (\d+)\. ([^\r\n]+)\r?$/gm)];
  return headers.map((match, headerIndex) => {
    const index = Number(match[1]);
    const title = match[2].trim();
    const next = headers[headerIndex + 1];
    const blockStart = match.index + match[0].length;
    const blockEnd = next ? next.index : text.length;
    const block = text.slice(blockStart, blockEnd);
    const purpose = extractBlock(block, "Purpose:", "Visible content:").join(" ").trim();
    const visible = extractBlock(block, "Visible content:", "Suggested visual:")
      .filter((line) => line.startsWith("- "))
      .map((line) => line.slice(2).trim());
    const visual = extractBlock(block, "Suggested visual:", "Speaker note summary:")
      .filter((line) => line.startsWith("- "))
      .map((line) => line.slice(2).trim());
    const notes = extractBlock(block, "Speaker note summary:", null).join(" ").trim();
    return { index, title, purpose, visible, visual, notes, section: sectionFor(index) };
  });
}

function extractBlock(text, start, end) {
  const startAt = text.indexOf(start);
  if (startAt < 0) return [];
  const bodyStart = startAt + start.length;
  const endAt = end ? text.indexOf(end, bodyStart) : text.length;
  return text
    .slice(bodyStart, endAt < 0 ? text.length : endAt)
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean);
}

function line(fill = "none", width = 0) {
  return { style: "solid", fill, width };
}

function addShape(slide, geometry, x, y, w, h, fill = "none", stroke = "none", width = 0, name) {
  return slide.shapes.add({
    geometry,
    name,
    position: { left: x, top: y, width: w, height: h },
    fill,
    line: line(stroke, width),
  });
}

function addText(slide, value, x, y, w, h, opts = {}) {
  const shape = slide.shapes.add({
    geometry: "textbox",
    name: opts.name,
    position: { left: x, top: y, width: w, height: h },
    fill: "none",
    line: line("none", 0),
  });
  shape.text = value;
  shape.text.style = {
    fontSize: opts.size ?? 18,
    color: opts.color ?? C.ink,
    bold: opts.bold ?? false,
    typeface: opts.face ?? "Aptos",
    alignment: opts.align ?? "left",
    verticalAlignment: opts.valign ?? "top",
  };
  return shape;
}

function setNotes(slide, text) {
  if (slide.speakerNotes?.setText) {
    slide.speakerNotes.setText(text);
  }
}

function addHeader(slide, data) {
  slide.background.fill = C.bg;
  addShape(slide, "rect", 0, 0, 1280, 720, C.bg, "none", 0);
  addShape(slide, "rect", 0, 0, 7, 720, accentFor(data.section), "none", 0);
  addText(slide, data.section.toUpperCase(), 66, 34, 640, 22, {
    size: 12,
    color: accentFor(data.section),
    bold: true,
  });
  addText(slide, String(data.index).padStart(2, "0"), 1162, 34, 54, 22, {
    size: 12,
    color: C.muted,
    bold: true,
    align: "right",
  });
  addText(slide, data.title, 66, 64, 1048, 58, {
    size: 31,
    color: C.ink,
    bold: true,
    face: "Aptos Display",
  });
  addShape(slide, "rect", 66, 130, 1148, 1, C.line, "none", 0);
}

function addFooter(slide) {
  addText(
    slide,
    "APK-to-SBOM MVP | emitted confirmation is not full recall | v2 is a source-known upper bound",
    66,
    682,
    1000,
    18,
    { size: 9, color: "#738195" },
  );
}

function accentFor(section) {
  if (section === "State of the Art") return C.teal;
  if (section === "Contribution") return C.green;
  if (section === "Implementation") return C.blue;
  if (section === "Demonstration") return C.red;
  if (section === "Conclusion") return C.amber;
  return C.blue;
}

function paleFor(section) {
  if (section === "State of the Art") return C.paleTeal;
  if (section === "Contribution") return C.paleGreen;
  if (section === "Demonstration") return C.paleRed;
  if (section === "Conclusion") return C.paleAmber;
  return C.paleBlue;
}

function addBullets(slide, items, x, y, w, h, opts = {}) {
  const fontSize = opts.size ?? (items.length > 6 ? 15 : 17);
  const rowGap = opts.rowGap ?? Math.max(42, Math.floor(h / Math.max(items.length, 1)));
  items.forEach((item, index) => {
    const yi = y + index * rowGap;
    const rowH = Math.min(rowGap - 6, 58);
    addShape(slide, "ellipse", x, yi + 7, 7, 7, opts.dot ?? C.blue, "none", 0);
    addText(slide, item, x + 18, yi, w - 18, rowH, {
      size: fontSize,
      color: opts.color ?? C.ink,
    });
  });
}

function addLabel(slide, value, x, y, w, opts = {}) {
  addShape(slide, "rect", x, y, w, 28, opts.fill ?? C.white, opts.stroke ?? accentFor(opts.section), 1);
  addText(slide, value, x + 8, y + 6, w - 16, 16, {
    size: 11,
    color: opts.color ?? accentFor(opts.section),
    bold: true,
    align: opts.align ?? "center",
  });
}

function addPanel(slide, title, lines, x, y, w, h, opts = {}) {
  addShape(slide, "rect", x, y, w, h, opts.fill ?? C.white, opts.stroke ?? C.line, 1);
  if (title) {
    addText(slide, title, x + 18, y + 16, w - 36, 26, {
      size: opts.titleSize ?? 15,
      color: opts.accent ?? C.blue,
      bold: true,
    });
  }
  addBullets(slide, lines, x + 18, y + (title ? 54 : 20), w - 36, h - (title ? 70 : 36), {
    size: opts.size ?? 14,
  });
}

function addMetric(slide, value, label, x, y, w, color = C.blue) {
  addText(slide, value, x, y, w, 48, {
    size: 36,
    color,
    bold: true,
    face: "Aptos Display",
  });
  addText(slide, label, x, y + 50, w, 42, {
    size: 12,
    color: C.muted,
  });
}

function addImage(slide, assets, key, x, y, w, h, opts = {}) {
  const blob = assets[key];
  if (!blob) throw new Error(`Missing image asset ${key}`);
  addShape(slide, "rect", x, y, w, h, opts.frameFill ?? C.white, opts.stroke ?? C.line, 1);
  slide.images.add({
    blob,
    contentType: "image/png",
    alt: opts.alt ?? key,
    fit: opts.fit ?? "contain",
    position: {
      left: x + (opts.inset ?? 8),
      top: y + (opts.inset ?? 8),
      width: w - 2 * (opts.inset ?? 8),
      height: h - 2 * (opts.inset ?? 8),
    },
  });
}

function drawPipeline(slide, labels, x, y, w, color = C.blue) {
  const gap = 14;
  const boxW = (w - gap * (labels.length - 1)) / labels.length;
  labels.forEach((label, i) => {
    const xi = x + i * (boxW + gap);
    addShape(slide, "rect", xi, y, boxW, 64, i % 2 ? C.white : C.paleBlue, color, 1);
    addText(slide, label, xi + 10, y + 19, boxW - 20, 26, {
      size: 15,
      color: C.ink,
      bold: true,
      align: "center",
      valign: "middle",
    });
    if (i < labels.length - 1) {
      addShape(slide, "chevron", xi + boxW - 1, y + 21, 18, 22, color, "none", 0);
    }
  });
}

function drawGenericSlide(slide, data) {
  addHeader(slide, data);
  const accent = accentFor(data.section);
  const pale = paleFor(data.section);
  const bullets = data.visible.slice(0, 8);
  addPanel(slide, "Main points", bullets, 72, 160, 560, 420, {
    accent,
    fill: C.white,
    size: bullets.length > 6 ? 14 : 16,
  });
  const visualLines = data.visual.length ? data.visual.slice(0, 4) : [data.purpose];
  addShape(slide, "rect", 672, 160, 536, 420, C.white, C.line, 1);
  addText(slide, "Visual plan", 696, 184, 250, 26, { size: 15, color: accent, bold: true });
  drawVisualPlaceholder(slide, data, visualLines, 696, 230, 488, 280, accent, pale);
  addText(slide, data.purpose, 696, 530, 488, 42, { size: 13, color: C.muted });
  addFooter(slide);
  setNotes(slide, data.notes);
}

function drawVisualPlaceholder(slide, data, lines, x, y, w, h, accent, pale) {
  if (/(pipeline|flow|path|chain)/i.test(lines.join(" ") + data.title)) {
    drawPipeline(slide, ["APK", "Evidence", "Match", "SBOM", "Report"], x, y + 80, w, accent);
    return;
  }
  if (/(table|matrix|comparison|taxonomy)/i.test(lines.join(" ") + data.title)) {
    const rows = Math.min(5, Math.max(3, lines.length + 1));
    for (let i = 0; i < rows; i += 1) {
      addShape(slide, "rect", x, y + i * 48, w, 44, i === 0 ? pale : C.white, i === 0 ? accent : C.line, 1);
      addText(slide, i === 0 ? "Evidence view" : (lines[i - 1] ?? "Bounded claim"), x + 14, y + i * 48 + 12, w - 28, 18, {
        size: 13,
        color: i === 0 ? accent : C.ink,
        bold: i === 0,
      });
    }
    return;
  }
  if (/(metric|result|score|rate|number)/i.test(data.title + lines.join(" "))) {
    addMetric(slide, pickNumber(data.visible, 0) ?? "927 / 1837", "source-validated emitted versions", x, y + 22, w / 2 - 14, accent);
    addMetric(slide, pickNumber(data.visible, 1) ?? "84 / 84", "controlled expected versions", x + w / 2 + 14, y + 22, w / 2 - 14, C.teal);
    addMetric(slide, pickNumber(data.visible, 2) ?? "6772 / 6772", "source-known v2 emitted rows", x, y + 150, w, C.green);
    return;
  }
  lines.forEach((lineText, index) => {
    const yi = y + index * 62;
    addShape(slide, "rect", x, yi, w, 48, index % 2 ? C.white : pale, index % 2 ? C.line : accent, 1);
    addText(slide, lineText, x + 16, yi + 14, w - 32, 18, { size: 13, color: C.ink, bold: index === 0 });
  });
}

function pickNumber(items, offset) {
  const nums = items
    .map((item) => item.match(/\d+\s*(?:of|\/)\s*\d+|\d+\.\d+\s*percent|\d+\.?\d*\s*%/i)?.[0])
    .filter(Boolean);
  return nums[offset];
}

function drawTitleSlide(slide, data) {
  slide.background.fill = C.bg;
  addShape(slide, "rect", 0, 0, 1280, 720, C.bg, "none", 0);
  addShape(slide, "rect", 0, 0, 11, 720, C.blue, "none", 0);
  addText(slide, "GRADUATION DEFENSE", 74, 58, 420, 24, { size: 13, color: C.blue, bold: true });
  addText(slide, "Evidence-Based\nSBOM Recovery\nfrom Compiled Android APKs", 72, 142, 700, 220, {
    size: 46,
    color: C.ink,
    bold: true,
    face: "Aptos Display",
  });
  addText(slide, "Trustworthy component attribution, CycloneDX output, and vulnerability interpretation", 76, 390, 620, 70, {
    size: 20,
    color: C.muted,
  });
  drawPipeline(slide, ["APK", "Evidence", "SBOM", "CVE report"], 706, 180, 450, C.teal);
  addShape(slide, "rect", 74, 536, 540, 1, C.line, "none", 0);
  addText(slide, "Fendi Mohamed\nComputer Systems Engineering", 76, 558, 520, 62, {
    size: 18,
    color: C.ink,
  });
  setNotes(slide, data.notes);
}

function drawRoadmap(slide, data) {
  addHeader(slide, data);
  const items = ["Introduction", "Background", "State of the Art", "Contribution", "Implementation", "Demonstration", "Conclusion"];
  items.forEach((item, i) => {
    const x = 92 + (i % 4) * 276;
    const y = 174 + Math.floor(i / 4) * 170;
    addText(slide, String(i + 1).padStart(2, "0"), x, y, 54, 38, {
      size: 26,
      color: accentFor(item),
      bold: true,
      face: "Aptos Display",
    });
    addShape(slide, "rect", x, y + 50, 230, 76, paleFor(item), accentFor(item), 1);
    addText(slide, item, x + 14, y + 76, 202, 20, { size: 16, color: C.ink, bold: true, align: "center" });
  });
  addFooter(slide);
  setNotes(slide, data.notes);
}

function drawResults(slide, data) {
  addHeader(slide, data);
  addShape(slide, "rect", 72, 158, 540, 410, C.white, C.line, 1);
  addLabel(slide, "NORMAL APK / SOURCE-VALIDATED METRIC", 96, 188, 310, { section: data.section });
  addMetric(slide, "50.5%", "927 of 1837 emitted Maven versions confirmed", 96, 240, 430, C.blue);
  progress(slide, "Controlled", "84/84", 96, 382, 390, C.green);
  progress(slide, "Clean real", "47/47", 96, 430, 390, C.green);
  progress(slide, "Partial real", "880/1790", 96, 478, 390, C.teal);
  addText(slide, "Measures correctness of what the APK-only tool emitted.", 96, 536, 470, 28, { size: 14, color: C.muted });
  addShape(slide, "rect", 668, 158, 540, 410, C.white, C.line, 1);
  addLabel(slide, "SOURCE-KNOWN V2 LANE", 692, 188, 230, { section: data.section });
  addMetric(slide, "6772 / 6772", "exact emitted rows", 692, 240, 420, C.green);
  const rows = [["Cases", "106"], ["Wrong emitted", "0"], ["Missing emitted", "0"], ["Source gaps", "5238"]];
  rows.forEach(([k, v], i) => {
    const y = 376 + i * 42;
    addShape(slide, "rect", 692, y, 370, 1, C.line, "none", 0);
    addText(slide, k, 692, y + 10, 180, 22, { size: 14, color: C.ink });
    addText(slide, v, 974, y + 8, 88, 24, { size: 15, color: C.green, bold: true, align: "right" });
  });
  addShape(slide, "rect", 160, 608, 960, 42, C.paleBlue, C.blue, 1);
  addText(slide, "Do not combine these lanes. v2 proves bounded recognition, not unconstrained APK-only accuracy.", 184, 621, 912, 18, {
    size: 14,
    color: C.ink,
    bold: true,
    align: "center",
  });
  addFooter(slide);
  setNotes(slide, data.notes);
}

function progress(slide, label, value, x, y, w, color) {
  addText(slide, label, x, y, 160, 22, { size: 14, color: C.ink, bold: true });
  addShape(slide, "rect", x + 170, y + 3, 190, 15, C.faint, "none", 0);
  addShape(slide, "rect", x + 170, y + 3, value.includes("1790") ? 94 : 190, 15, color, "none", 0);
  addText(slide, value, x + 370, y - 2, 84, 22, { size: 14, color, bold: true });
}

function drawAiLane(slide, data, assets) {
  addHeader(slide, data);
  addPanel(slide, "Dataset evidence", data.visible.slice(0, 5), 72, 158, 468, 398, {
    accent: C.blue,
    fill: C.white,
    size: 16,
  });
  addImage(slide, assets, "aiReportTop", 584, 168, 584, 330, { alt: "Hybrid AI report screenshot" });
  addShape(slide, "rect", 584, 526, 584, 54, C.paleBlue, C.blue, 1);
  addText(slide, "Report-only AI assistance is visible, but the deterministic matcher remains the SBOM authority.", 604, 542, 544, 18, {
    size: 14,
    color: C.ink,
    bold: true,
    align: "center",
  });
  addFooter(slide);
  setNotes(slide, data.notes);
}

function drawMlSlide(slide, data) {
  addHeader(slide, data);
  const rows = [
    ["Model", "RandomForestClassifier"],
    ["Rows", "20523"],
    ["Test macro-F1", "0.708"],
    ["Test accuracy", "0.690"],
    ["Decision", "report-only assistance"],
  ];
  addResultTable(slide, "Classical ML result", rows, 92, 176, 500, C.blue);
  addPanel(slide, "Authority boundary", [
    "Allowed: report wording, prioritization, diagnostics.",
    "Blocked: selected versions, SBOM components, CVE labels, source-validation metrics.",
    "Interpretation: useful triage, not exact Maven version proof.",
  ], 656, 176, 500, 270, { accent: C.red, fill: C.white, size: 16 });
  addShape(slide, "rect", 92, 520, 1064, 54, C.paleRed, C.red, 1);
  addText(slide, "The ML result is included because it is useful, and bounded because model output is not direct APK evidence.", 116, 536, 1016, 18, {
    size: 15,
    color: C.ink,
    bold: true,
    align: "center",
  });
  addFooter(slide);
  setNotes(slide, data.notes);
}

function drawDlSlide(slide, data, assets) {
  addHeader(slide, data);
  const rows = [
    ["Structured-token Transformer", "0.977 macro-F1"],
    ["MVP-safe Transformer", "0.882 macro-F1"],
    ["Raw-opcode Transformer", "0.110 macro-F1"],
    ["Raw-opcode baseline", "0.128 macro-F1"],
    ["Verdict", "raw-opcode DL research-only"],
  ];
  addResultTable(slide, "Deep learning result", rows, 72, 172, 520, C.teal);
  addShape(slide, "rect", 646, 182, 480, 250, C.white, C.line, 1);
  addText(slide, "Macro-F1 comparison", 676, 206, 420, 22, { size: 15, color: C.teal, bold: true });
  [
    ["Structured token", 0.977, C.teal],
    ["MVP safe", 0.882, C.green],
    ["Raw opcode", 0.110, C.red],
    ["Raw baseline", 0.128, C.amber],
  ].forEach(([label, value, color], index) => {
    const y = 250 + index * 42;
    addText(slide, label, 676, y, 120, 18, { size: 12, color: C.ink, bold: true });
    addShape(slide, "rect", 806, y + 3, 250, 12, C.faint, "none", 0);
    addShape(slide, "rect", 806, y + 3, 250 * value, 12, color, "none", 0);
    addText(slide, value.toFixed(3), 1070, y - 1, 52, 18, { size: 12, color, bold: true, align: "right" });
  });
  addShape(slide, "rect", 646, 468, 480, 80, C.paleTeal, C.teal, 1);
  addText(slide, "Structured evidence helps report-only triage. Raw opcode sequences did not beat the baseline.", 668, 492, 436, 34, {
    size: 15,
    color: C.ink,
    bold: true,
    align: "center",
  });
  addFooter(slide);
  setNotes(slide, data.notes);
}

function addResultTable(slide, title, rows, x, y, w, accent) {
  addShape(slide, "rect", x, y, w, 58 + rows.length * 48, C.white, C.line, 1);
  addShape(slide, "rect", x, y, w, 44, C.paleBlue, accent, 1);
  addText(slide, title, x + 16, y + 13, w - 32, 18, { size: 14, color: accent, bold: true });
  rows.forEach(([label, value], i) => {
    const yy = y + 56 + i * 48;
    addShape(slide, "rect", x + 16, yy - 8, w - 32, 1, C.faint, "none", 0);
    addText(slide, label, x + 18, yy + 6, 220, 20, { size: 14, color: C.ink, bold: true });
    addText(slide, value, x + 250, yy + 6, w - 282, 20, { size: 14, color: accent, bold: true, align: "right" });
  });
}

function drawDemoFlow(slide, data) {
  addHeader(slide, data);
  drawPipeline(slide, ["Input APK", "Reference DB", "generate-report", "Output dir", "Report bundle"], 110, 210, 1060, C.blue);
  const artifacts = ["matches.json", "sbom.cdx.json", "osv-vulnerabilities.json", "report.json", "report.md", "report.html"];
  artifacts.forEach((artifact, i) => {
    const x = 112 + (i % 3) * 350;
    const y = 360 + Math.floor(i / 3) * 78;
    addShape(slide, "rect", x, y, 300, 46, i % 2 ? C.white : C.paleBlue, C.line, 1);
    addText(slide, artifact, x + 12, y + 14, 276, 18, { size: 14, color: C.ink, bold: true, align: "center" });
  });
  addShape(slide, "rect", 154, 560, 972, 44, C.paleBlue, C.blue, 1);
  addText(slide, "Optional hybrid AI sections appear only when requested and do not alter the official output.", 180, 573, 920, 18, {
    size: 14,
    color: C.ink,
    bold: true,
    align: "center",
  });
  addFooter(slide);
  setNotes(slide, data.notes);
}

function drawCveScreens(slide, data, assets) {
  addHeader(slide, data);
  addText(slide, "CLEAN REAL APK", 72, 146, 300, 22, { size: 13, color: C.blue, bold: true });
  addText(slide, "CONTROLLED POSITIVE CVE", 670, 146, 340, 22, { size: 13, color: C.red, bold: true });
  addImage(slide, assets, "cleanReport", 72, 176, 540, 328, { alt: "Clean F-Droid report screenshot" });
  addImage(slide, assets, "vulnerableReport", 670, 176, 538, 328, { alt: "Vulnerable Jackson report screenshot" });
  addLabel(slide, "23 Maven components | OSV 0", 96, 524, 470, { section: "Implementation", color: C.blue, stroke: C.blue });
  addLabel(slide, "Jackson Databind 2.9.10.8 | 3 HIGH", 692, 524, 470, { section: "Demonstration", color: C.red, stroke: C.red });
  ["CVE-2020-36518", "CVE-2022-42003", "CVE-2022-42004"].forEach((cve, i) => {
    addLabel(slide, cve, 692 + i * 160, 572, 145, { section: "Demonstration", color: C.red, stroke: C.red });
  });
  addFooter(slide);
  setNotes(slide, data.notes);
}

function drawProofMontage(slide, data, assets) {
  addHeader(slide, data);
  const keys = [
    "cleanPage01",
    "cleanPage02",
    "cleanPage03",
    "cleanPage04",
    "cleanPage05",
    "vulnPage01",
    "vulnPage02",
    "vulnPage03",
    "aiReportTop",
  ];
  keys.forEach((key, i) => {
    const col = i % 3;
    const row = Math.floor(i / 3);
    const x = 78 + col * 382;
    const y = 154 + row * 146;
    addImage(slide, assets, key, x, y, 340, 122, { inset: 4, alt: `${key} report proof screenshot` });
  });
  addShape(slide, "rect", 112, 604, 1056, 40, C.paleRed, C.red, 1);
  addText(slide, "The screenshots prove implemented output surfaces. They do not claim perfect APK coverage.", 134, 616, 1012, 18, {
    size: 14,
    color: C.ink,
    bold: true,
    align: "center",
  });
  addFooter(slide);
  setNotes(slide, data.notes);
}

function drawClosing(slide, data) {
  addHeader(slide, data);
  const metrics = [
    ["84 / 84", "controlled expected versions", C.green],
    ["927 / 1837", "source-validated emitted Maven versions", C.blue],
    ["6772 / 6772", "source-known v2 emitted rows", C.teal],
  ];
  metrics.forEach(([value, label, color], i) => addMetric(slide, value, label, 112 + i * 360, 190, 300, color));
  addPanel(slide, "Synthesis", data.visible.slice(0, 5), 112, 350, 1010, 170, {
    accent: C.amber,
    fill: C.white,
    size: 16,
  });
  addShape(slide, "rect", 202, 580, 876, 46, C.paleAmber, C.amber, 1);
  addText(slide, "Auditable partial knowledge is safer than unsupported exact-version certainty.", 226, 594, 828, 18, {
    size: 16,
    color: C.ink,
    bold: true,
    align: "center",
  });
  addFooter(slide);
  setNotes(slide, data.notes);
}

function drawFuture(slide, data) {
  addHeader(slide, data);
  const items = data.visible.slice(0, 6);
  items.forEach((item, i) => {
    const x = 88 + (i % 3) * 374;
    const y = 180 + Math.floor(i / 3) * 180;
    addText(slide, String(i + 1).padStart(2, "0"), x, y, 52, 34, { size: 24, color: C.amber, bold: true, face: "Aptos Display" });
    addShape(slide, "rect", x, y + 44, 320, 96, i % 2 ? C.white : C.paleAmber, C.amber, 1);
    addText(slide, item, x + 18, y + 70, 284, 36, { size: 15, color: C.ink, bold: true, align: "center" });
  });
  addFooter(slide);
  setNotes(slide, data.notes);
}

async function createContactSheet(slideResults, outPath) {
  const thumbW = 256;
  const thumbH = 144;
  const gap = 14;
  const labelH = 22;
  const cols = 5;
  const rows = Math.ceil(slideResults.length / cols);
  const canvas = new Canvas(
    cols * thumbW + (cols + 1) * gap,
    rows * (thumbH + labelH) + (rows + 1) * gap,
  );
  const ctx = canvas.getContext("2d");
  ctx.fillStyle = C.bg;
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  ctx.font = "bold 12px Arial";
  ctx.fillStyle = C.muted;
  for (const [index, row] of slideResults.entries()) {
    const image = await loadImage(row.previewPath);
    const col = index % cols;
    const rowIndex = Math.floor(index / cols);
    const x = gap + col * (thumbW + gap);
    const y = gap + rowIndex * (thumbH + labelH + gap);
    ctx.drawImage(image, x, y, thumbW, thumbH);
    ctx.strokeStyle = C.line;
    ctx.lineWidth = 1;
    ctx.strokeRect(x, y, thumbW, thumbH);
    ctx.fillText(`Slide ${String(index + 1).padStart(2, "0")}`, x, y + thumbH + 16);
  }
  await fs.writeFile(outPath, await canvas.toBuffer("png"));
}

async function loadAssets() {
  return {
    cleanReport: await readImage(path.join(ASSET_DIR, "clean-report.png")),
    vulnerableReport: await readImage(path.join(ASSET_DIR, "vulnerable-report-top.png")),
    aiReportTop: await readImage(path.join(ASSET_DIR, "ai-report-top.png")),
    aiAssisted: await readImage(path.join(ASSET_DIR, "ai-assisted-report.png")),
    cleanVersionDecisions: await readImage(path.join(ASSET_DIR, "clean-version-decisions.png")),
    vulnerableCves: await readImage(path.join(ASSET_DIR, "vulnerable-cves.png")),
    cleanPage01: await readImage(path.join(PROOF_DIR, "clean-fdroid", "clean-fdroid-report-page-01.png")),
    cleanPage02: await readImage(path.join(PROOF_DIR, "clean-fdroid", "clean-fdroid-report-page-02.png")),
    cleanPage03: await readImage(path.join(PROOF_DIR, "clean-fdroid", "clean-fdroid-report-page-03.png")),
    cleanPage04: await readImage(path.join(PROOF_DIR, "clean-fdroid", "clean-fdroid-report-page-04.png")),
    cleanPage05: await readImage(path.join(PROOF_DIR, "clean-fdroid", "clean-fdroid-report-page-05.png")),
    vulnPage01: await readImage(path.join(PROOF_DIR, "vulnerable-jackson", "vulnerable-jackson-report-page-01.png")),
    vulnPage02: await readImage(path.join(PROOF_DIR, "vulnerable-jackson", "vulnerable-jackson-report-page-02.png")),
    vulnPage03: await readImage(path.join(PROOF_DIR, "vulnerable-jackson", "vulnerable-jackson-report-page-03.png")),
  };
}

async function build() {
  await fs.mkdir(OUTPUT_DIR, { recursive: true });
  await fs.mkdir(PREVIEW_DIR, { recursive: true });
  await fs.mkdir(LAYOUT_DIR, { recursive: true });
  await fs.mkdir(QA_DIR, { recursive: true });

  const content = await fs.readFile(CONTENT_PATH, "utf8");
  const slides = parseSlides(content);
  if (slides.length !== 60) throw new Error(`Expected 60 slides, found ${slides.length}`);

  const assets = await loadAssets();
  const presentation = Presentation.create({ slideSize: { width: 1280, height: 720 } });
  const slideResults = [];

  for (const data of slides) {
    const slide = presentation.slides.add();
    if (data.index === 1) drawTitleSlide(slide, data);
    else if (data.index === 6) drawRoadmap(slide, data);
    else if (data.index === 49 || data.index === 51) drawResults(slide, data);
    else if (data.index === 53) drawAiLane(slide, data, assets);
    else if (data.index === 54) drawMlSlide(slide, data);
    else if (data.index === 55) drawDlSlide(slide, data, assets);
    else if (data.index === 56) drawDemoFlow(slide, data);
    else if (data.index === 57) drawCveScreens(slide, data, assets);
    else if (data.index === 58) drawProofMontage(slide, data, assets);
    else if (data.index === 59) drawClosing(slide, data);
    else if (data.index === 60) drawFuture(slide, data);
    else drawGenericSlide(slide, data);

    const stem = `slide-${String(data.index).padStart(2, "0")}`;
    const previewPath = path.join(PREVIEW_DIR, `${stem}.png`);
    const layoutPath = path.join(LAYOUT_DIR, `${stem}.layout.json`);
    await writeBlob(previewPath, await presentation.export({ slide, format: "png", scale: 1 }));
    await fs.writeFile(layoutPath, await (await slide.export({ format: "layout" })).text());
    slideResults.push({ index: data.index, previewPath, layoutPath, title: data.title });
  }

  const contactSheet = path.join(PREVIEW_DIR, "contact-sheet.png");
  await createContactSheet(slideResults, contactSheet);

  const montage = await presentation.export({ format: "webp", montage: true, scale: 1 });
  await writeBlob(path.join(PREVIEW_DIR, "deck-montage.webp"), montage);

  const pptx = await PresentationFile.exportPptx(presentation);
  await pptx.save(FINAL_PPTX);

  const stat = await fs.stat(FINAL_PPTX);
  await fs.writeFile(
    path.join(OUTPUT_DIR, "artifact-build-manifest.json"),
    JSON.stringify({
      output: FINAL_PPTX,
      outputBytes: stat.size,
      slideCount: presentation.slides.items.length,
      slideSize: { width: 1280, height: 720 },
      contentSource: CONTENT_PATH,
      previewDir: PREVIEW_DIR,
      contactSheet,
      slides: slideResults,
      requiredScreenshots: [
        "clean-report.png",
        "vulnerable-report-top.png",
        "ai-report-top.png",
        "clean-fdroid-report-page-01.png",
        "clean-fdroid-report-page-02.png",
        "clean-fdroid-report-page-03.png",
        "clean-fdroid-report-page-04.png",
        "clean-fdroid-report-page-05.png",
        "vulnerable-jackson-report-page-01.png",
        "vulnerable-jackson-report-page-02.png",
        "vulnerable-jackson-report-page-03.png",
      ],
    }, null, 2) + "\n",
  );

  await fs.writeFile(
    path.join(QA_DIR, "build-notes.txt"),
    [
      "Graduation defense 60-slide deck build notes",
      "",
      "Source: outputs/graduation-defense-60-slide-content.txt",
      "Theme: minimal light academic palette.",
      "Slide count: 60.",
      "Required screenshots from latest PPTX are embedded.",
      "No em dash or en dash characters are used in the content script.",
      "Manual visual QA still required after preview inspection.",
      "",
    ].join("\n"),
  );

  console.log(JSON.stringify({
    pptx: FINAL_PPTX,
    slides: presentation.slides.items.length,
    bytes: stat.size,
    contactSheet,
  }, null, 2));
}

build().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
