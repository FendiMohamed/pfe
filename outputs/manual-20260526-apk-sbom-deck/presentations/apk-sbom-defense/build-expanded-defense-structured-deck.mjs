import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { Presentation, PresentationFile } from "@oai/artifact-tool";
import { Canvas, loadImage } from "./node_modules/@oai/artifact-tool/node_modules/skia-canvas/lib/index.mjs";
import { drawSlide } from "./slides/common.mjs";

const ROOT = path.dirname(fileURLToPath(import.meta.url));
const REPO = path.resolve(ROOT, "..", "..", "..", "..");
const OUT_ROOT = path.join(REPO, "outputs", "graduation-defense-expanded-old-style-deck");
const OUTPUT_DIR = path.join(OUT_ROOT, "output");
const PREVIEW_DIR = path.join(OUT_ROOT, "preview");
const LAYOUT_DIR = path.join(OUT_ROOT, "layout");
const QA_DIR = path.join(OUT_ROOT, "qa");
const ZOOM_DIR = path.join(OUT_ROOT, "zoom");
const ASSET_DIR = path.join(ROOT, "assets");
const FIG_DIR = path.join(REPO, "thesis", "pfe", "figures");
const PROOF_DIR = path.join(ASSET_DIR, "report-proof-screenshots");
const FINAL_PPTX = path.join(OUTPUT_DIR, "apk-sbom-defense-expanded-old-style.pptx");

const C = {
  night: "#17212B",
  night2: "#22303C",
  paper: "#F6F5F2",
  white: "#FFFFFF",
  ink: "#202A33",
  muted: "#65717A",
  line: "#D2D6D8",
  lineDark: "#3B4853",
  blue: "#365F7D",
  cyan: "#4F7D76",
  lime: "#6F7C61",
  coral: "#A65C55",
  gold: "#8D754D",
  violet: "#655F73",
  paleBlue: "#EAF0F3",
  paleCyan: "#E9EFED",
  paleLime: "#EEF0EA",
  paleCoral: "#F3EAE8",
  paleGold: "#F1EDE5",
};

const sections = {
  intro: { label: "Introduction", accent: C.blue },
  background: { label: "Background", accent: C.cyan },
  state: { label: "State of the Art", accent: C.violet },
  contribution: { label: "Contribution", accent: C.lime },
  implementation: { label: "Implementation", accent: C.gold },
  demo: { label: "Demonstration", accent: C.coral },
  conclusion: { label: "Conclusion", accent: C.gold },
};

const screenshots = [
  ["clean-dashboard-01-summary.png", "F-Droid HTML dashboard shows the clean APK summary"],
  ["clean-dashboard-02-components-a.png", "F-Droid detected components panel, part 1"],
  ["clean-dashboard-03-components-b.png", "F-Droid detected components panel, part 2"],
  ["clean-dashboard-04-version-decisions-a.png", "F-Droid version-decision panel, part 1"],
  ["clean-dashboard-05-version-decisions-b.png", "F-Droid version-decision panel, part 2"],
  ["clean-dashboard-06-vulnerabilities-artifacts.png", "F-Droid vulnerability and artifacts panel"],
  ["vulnerable-dashboard-01-summary.png", "Vulnerable Jackson dashboard summary"],
  ["vulnerable-dashboard-02-components-decisions.png", "Vulnerable Jackson component and version decision"],
  ["vulnerable-dashboard-03-cves-artifacts.png", "Vulnerable Jackson CVE and artifact panel"],
  ["hybrid-dashboard-01-r8-diagnostics.png", "Hybrid AI dashboard shows R8 diagnostics"],
  ["hybrid-dashboard-02-assistance-summary.png", "Hybrid AI assistance summary"],
  ["hybrid-dashboard-03-ml-results.png", "AI result screenshot for the RandomForest lane"],
  ["hybrid-dashboard-04-dl-results.png", "AI result screenshot for the deep learning lane"],
  ["prototype-clean-fdroid-page-01.png", "Clean F-Droid full report page 1"],
  ["prototype-clean-fdroid-page-02.png", "Clean F-Droid full report page 2"],
  ["prototype-vulnerable-jackson-page-01.png", "Vulnerable Jackson full report page 1"],
  ["prototype-vulnerable-jackson-page-02.png", "Vulnerable Jackson full report page 2"],
  ["prototype-vulnerable-jackson-page-03.png", "Vulnerable Jackson full report page 3"],
];

const zoomSpecs = {
  "clean-dashboard-01-summary.png": [
    { id: "summary", title: "Zoom view of the F-Droid dashboard summary", top: 0.00, height: 0.34 },
    { id: "apk-metadata", title: "Zoom view of the F-Droid APK metadata", top: 0.22, height: 0.34 },
    { id: "component-preview", title: "Zoom view of the F-Droid component preview", top: 0.53, height: 0.36 },
  ],
  "clean-dashboard-02-components-a.png": [
    { id: "rows-1", title: "Zoom view of F-Droid detected components, first group", top: 0.00, height: 0.34 },
    { id: "rows-2", title: "Zoom view of F-Droid detected components, middle group", top: 0.31, height: 0.34 },
    { id: "rows-3", title: "Zoom view of F-Droid detected components, lower group", top: 0.62, height: 0.34 },
  ],
  "clean-dashboard-03-components-b.png": [
    { id: "rows-4", title: "Zoom view of F-Droid detected components, continuation one", top: 0.00, height: 0.34 },
    { id: "rows-5", title: "Zoom view of F-Droid detected components, continuation two", top: 0.31, height: 0.34 },
    { id: "rows-6", title: "Zoom view of F-Droid detected components, continuation three", top: 0.62, height: 0.34 },
  ],
  "clean-dashboard-04-version-decisions-a.png": [
    { id: "decisions-1", title: "Zoom view of F-Droid version decisions, first group", top: 0.00, height: 0.34 },
    { id: "decisions-2", title: "Zoom view of F-Droid version decisions, middle group", top: 0.31, height: 0.34 },
    { id: "decisions-3", title: "Zoom view of F-Droid version decisions, lower group", top: 0.62, height: 0.34 },
  ],
  "clean-dashboard-05-version-decisions-b.png": [
    { id: "decisions-4", title: "Zoom view of F-Droid version decisions, continuation one", top: 0.00, height: 0.34 },
    { id: "decisions-5", title: "Zoom view of F-Droid version decisions, continuation two", top: 0.31, height: 0.34 },
    { id: "decisions-6", title: "Zoom view of F-Droid version decisions, continuation three", top: 0.62, height: 0.34 },
  ],
  "clean-dashboard-06-vulnerabilities-artifacts.png": [
    { id: "vulnerability-status", title: "Zoom view of F-Droid vulnerability status", top: 0.00, height: 0.52 },
    { id: "artifacts", title: "Zoom view of F-Droid generated artifacts", top: 0.43, height: 0.52 },
  ],
  "vulnerable-dashboard-01-summary.png": [
    { id: "summary", title: "Zoom view of the vulnerable dashboard summary", top: 0.00, height: 0.48 },
    { id: "cve-preview", title: "Zoom view of confirmed Jackson vulnerabilities", top: 0.39, height: 0.50 },
  ],
  "vulnerable-dashboard-02-components-decisions.png": [
    { id: "component", title: "Zoom view of the vulnerable component evidence", top: 0.00, height: 0.48 },
    { id: "decision", title: "Zoom view of the vulnerable version decision", top: 0.39, height: 0.50 },
  ],
  "vulnerable-dashboard-03-cves-artifacts.png": [
    { id: "cves", title: "Zoom view of the vulnerable CVE findings", top: 0.00, height: 0.48 },
    { id: "artifacts", title: "Zoom view of vulnerable report artifacts", top: 0.39, height: 0.50 },
  ],
  "hybrid-dashboard-01-r8-diagnostics.png": [
    { id: "r8-top", title: "Zoom view of R8 diagnostics, first group", top: 0.00, height: 0.38 },
    { id: "r8-middle", title: "Zoom view of R8 diagnostics, middle group", top: 0.31, height: 0.38 },
    { id: "r8-bottom", title: "Zoom view of R8 diagnostics, lower group", top: 0.62, height: 0.36 },
  ],
  "hybrid-dashboard-02-assistance-summary.png": [
    { id: "assistance", title: "Zoom view of the hybrid AI assistance summary", top: 0.00, height: 0.50 },
    { id: "guardrails", title: "Zoom view of hybrid AI guardrails", top: 0.42, height: 0.50 },
  ],
  "hybrid-dashboard-03-ml-results.png": [
    { id: "ml-metrics", title: "Zoom view of AI machine learning metrics", top: 0.00, height: 0.50 },
    { id: "ml-status", title: "Zoom view of AI machine learning status", top: 0.42, height: 0.50 },
  ],
};

function line(fill, width = 1) {
  if (!fill || fill === "#00000000" || width === 0) return { style: "solid", fill: "none", width: 0 };
  return { style: "solid", fill, width };
}

function makeContext() {
  return {
    fonts: { title: "Aptos Display", body: "Aptos", mono: "Cascadia Mono" },
    line,
    addShape(slide, cfg) {
      return slide.shapes.add({
        geometry: cfg.geometry ?? "rect",
        name: cfg.name,
        position: { left: cfg.x, top: cfg.y, width: cfg.w, height: cfg.h },
        fill: cfg.fill ?? "none",
        line: cfg.line ?? line("none", 0),
      });
    },
    addText(slide, cfg) {
      const shape = slide.shapes.add({
        geometry: "textbox",
        name: cfg.name,
        position: { left: cfg.x, top: cfg.y, width: cfg.w, height: cfg.h },
        fill: cfg.fill === "#00000000" ? "none" : cfg.fill ?? "none",
        line: cfg.line ?? line("none", 0),
      });
      shape.text = cfg.text;
      shape.text.style = {
        fontSize: cfg.fontSize,
        color: cfg.color,
        bold: cfg.bold,
        typeface: cfg.typeface,
        alignment: cfg.align,
        verticalAlignment: cfg.valign,
      };
      return shape;
    },
  };
}

function text(slide, ctx, value, x, y, w, h, opts = {}) {
  return ctx.addText(slide, {
    text: value,
    x, y, w, h,
    fontSize: opts.size ?? 22,
    color: opts.color ?? C.ink,
    bold: opts.bold ?? false,
    typeface: opts.face ?? (opts.mono ? ctx.fonts.mono : ctx.fonts.body),
    align: opts.align ?? "left",
    valign: opts.valign ?? "top",
    fill: opts.fill ?? "#00000000",
    line: opts.line ?? line("none", 0),
  });
}

function shape(slide, ctx, geometry, x, y, w, h, fill, stroke = fill) {
  return ctx.addShape(slide, { geometry, x, y, w, h, fill, line: line(stroke, stroke === "#00000000" ? 0 : 1) });
}

function rect(slide, ctx, x, y, w, h, fill, stroke = fill) {
  return shape(slide, ctx, "rect", x, y, w, h, fill, stroke);
}

function box(slide, ctx, x, y, w, h, fill = C.white, stroke = C.line) {
  return rect(slide, ctx, x, y, w, h, fill, stroke);
}

function page(slide, ctx, section, title, number, opts = {}) {
  const dark = opts.dark ?? false;
  const accent = opts.accent ?? section.accent;
  slide.background.fill = dark ? C.night : C.paper;
  rect(slide, ctx, 0, 0, 1280, 720, dark ? C.night : C.paper, "#00000000");
  if (dark) rect(slide, ctx, 0, 0, 7, 720, accent, "#00000000");
  text(slide, ctx, section.label.toUpperCase(), 66, 34, 760, 22, {
    size: 12,
    color: dark ? accent : accent,
    bold: true,
  });
  text(slide, ctx, title, 66, 64, 1040, 64, {
    size: opts.titleSize ?? 31,
    color: dark ? C.white : C.ink,
    bold: true,
    face: ctx.fonts.title,
  });
  text(slide, ctx, String(number).padStart(2, "0"), 1170, 38, 48, 22, {
    size: 12,
    color: dark ? "#8290A6" : C.muted,
    align: "right",
    bold: true,
  });
}

function footer(slide, ctx, dark = false) {
  text(
    slide,
    ctx,
    "APK-to-SBOM MVP  |  emitted confirmation is not full recall  |  v2 is a source-known upper bound",
    66,
    682,
    1000,
    18,
    { size: 9, color: dark ? "#718097" : "#7B8798" },
  );
}

function bulletList(slide, ctx, items, x, y, w, opts = {}) {
  const color = opts.color ?? C.ink;
  const accent = opts.accent ?? C.blue;
  const gap = opts.gap ?? 58;
  items.forEach((item, index) => {
    const yy = y + index * gap;
    shape(slide, ctx, "ellipse", x, yy + 8, 12, 12, accent, "#00000000");
    text(slide, ctx, item, x + 30, yy, w - 30, opts.rowH ?? 40, { size: opts.size ?? 18, color, bold: opts.bold ?? true });
  });
}

function label(slide, ctx, value, x, y, w, color, fill = C.white) {
  box(slide, ctx, x, y, w, 30, fill, color);
  text(slide, ctx, value, x + 8, y + 7, w - 16, 16, { size: 11, color, bold: true, align: "center" });
}

function addImage(slide, bytes, x, y, w, h, alt, stroke = C.line, fit = "contain") {
  box(slide, makeContext(), x, y, w, h, C.white, stroke);
  slide.images.add({
    blob: bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength),
    contentType: "image/png",
    alt,
    fit,
    position: { left: x + 8, top: y + 8, width: w - 16, height: h - 16 },
  });
}

function drawTitle(slide, ctx, number) {
  slide.background.fill = C.night;
  rect(slide, ctx, 0, 0, 1280, 720, C.night, "#00000000");
  rect(slide, ctx, 0, 0, 18, 720, C.cyan, "#00000000");
  text(slide, ctx, "GRADUATION DEFENSE", 72, 52, 430, 22, { size: 12, color: C.cyan, bold: true });
  text(slide, ctx, "Evidence-Based", 72, 114, 650, 62, { size: 48, color: C.white, bold: true, face: ctx.fonts.title });
  text(slide, ctx, "SBOM Recovery", 72, 172, 650, 62, { size: 48, color: C.white, bold: true, face: ctx.fonts.title });
  text(slide, ctx, "from compiled Android APKs", 74, 245, 600, 40, { size: 24, color: "#A9B6C9", bold: true });
  text(slide, ctx, "Static evidence fusion, CycloneDX output, confidence-aware CVE mapping, and guarded AI assistance.", 74, 310, 580, 70, { size: 17, color: "#C6D0DE" });
  text(slide, ctx, "Presented by Fendi Mohamed", 74, 408, 580, 34, { size: 22, color: C.white, bold: true });
  text(slide, ctx, "Computer Systems Engineering", 74, 448, 580, 28, { size: 16, color: "#A9B6C9", bold: true });
  [["APK", 732, 110, C.blue], ["DEX", 930, 86, C.violet], ["MATCH", 1034, 232, C.cyan], ["SBOM", 914, 382, C.lime], ["CVE", 710, 358, C.coral]].forEach(([value, x, y, color], index) => {
    const d = index === 2 ? 126 : 96;
    shape(slide, ctx, "ellipse", x, y, d, d, index === 2 ? color : C.night2, color);
    text(slide, ctx, value, x, y + d / 2 - 12, d, 24, { size: index === 2 ? 19 : 15, color: C.white, bold: true, align: "center" });
  });
  rect(slide, ctx, 70, 522, 1100, 1, C.lineDark, "#00000000");
  [
    ["927 / 1837", "source-validated emitted versions"],
    ["84 / 84", "controlled expected versions"],
    ["6772 / 6772", "source-known v2 upper-bound rows"],
  ].forEach(([value, caption], index) => {
    const x = 74 + index * 360;
    text(slide, ctx, value, x, 552, 300, 36, { size: 32, color: index === 0 ? C.cyan : index === 1 ? C.lime : C.gold, bold: true, face: ctx.fonts.title });
    text(slide, ctx, caption, x, 596, 300, 28, { size: 11, color: "#9FADBF" });
  });
}

function drawSection(slide, ctx, section, title, points, number) {
  slide.background.fill = C.night;
  rect(slide, ctx, 0, 0, 1280, 720, C.night, "#00000000");
  rect(slide, ctx, 0, 0, 18, 720, section.accent, "#00000000");
  text(slide, ctx, section.label.toUpperCase(), 72, 64, 560, 26, { size: 13, color: section.accent, bold: true });
  text(slide, ctx, String(number).padStart(2, "0"), 1170, 38, 48, 22, { size: 12, color: "#8290A6", align: "right", bold: true });
  text(slide, ctx, title, 72, 150, 800, 118, { size: 42, color: C.white, bold: true, face: ctx.fonts.title });
  rect(slide, ctx, 72, 322, 720, 2, section.accent, "#00000000");
  bulletList(slide, ctx, points, 78, 374, 740, { color: "#D4DCE6", accent: section.accent, size: 18, gap: 66 });
  box(slide, ctx, 892, 174, 238, 238, C.night2, C.lineDark);
  text(slide, ctx, section.label, 916, 214, 190, 34, { size: 25, color: section.accent, bold: true, align: "center", face: ctx.fonts.title });
  text(slide, ctx, "Current section", 916, 278, 190, 24, { size: 14, color: "#B8C3D3", align: "center" });
  text(slide, ctx, "Research\nsystem\nevidence", 916, 326, 190, 72, { size: 16, color: C.white, bold: true, align: "center" });
  footer(slide, ctx, true);
}

function drawContent(slide, ctx, section, title, bullets, number, opts = {}) {
  page(slide, ctx, section, title, number, { dark: opts.dark, titleSize: opts.titleSize });
  const dark = opts.dark ?? false;
  const panelFill = dark ? C.night2 : C.white;
  const stroke = dark ? C.lineDark : C.line;
  box(slide, ctx, 72, 156, 1136, 438, panelFill, stroke);
  bulletList(slide, ctx, bullets, 104, 198, 1040, {
    color: dark ? "#DCE5F0" : C.ink,
    accent: section.accent,
    size: opts.size ?? 18,
    gap: opts.gap ?? 60,
    rowH: opts.rowH ?? 42,
  });
  if (opts.callout) {
    box(slide, ctx, 112, 606, 1056, 42, dark ? C.night : opts.calloutFill ?? C.paleBlue, section.accent);
    text(slide, ctx, opts.callout, 138, 618, 1004, 18, { size: 14, color: dark ? C.white : C.ink, bold: true, align: "center" });
  }
  footer(slide, ctx, dark);
}

function drawTableSlide(slide, ctx, section, title, headers, rows, number, opts = {}) {
  page(slide, ctx, section, title, number, { dark: opts.dark, titleSize: opts.titleSize });
  const dark = opts.dark ?? false;
  const x = 72;
  const y = 156;
  const w = 1136;
  const rowH = opts.rowH ?? 54;
  box(slide, ctx, x, y, w, rowH * (rows.length + 1), dark ? C.night2 : C.white, dark ? C.lineDark : C.line);
  rect(slide, ctx, x, y, w, rowH, dark ? C.night : C.paleBlue, section.accent);
  const cols = opts.cols ?? [0.22, 0.28, 0.25, 0.25];
  let cx = x;
  headers.forEach((h, i) => {
    const cw = w * cols[i];
    text(slide, ctx, h, cx + 14, y + 18, cw - 28, 18, { size: 12, color: section.accent, bold: true, align: i === 0 ? "left" : "center" });
    cx += cw;
  });
  rows.forEach((row, r) => {
    const yy = y + rowH * (r + 1);
    rect(slide, ctx, x, yy, w, 1, dark ? C.lineDark : C.line, "#00000000");
    cx = x;
    row.forEach((cell, i) => {
      const cw = w * cols[i];
      text(slide, ctx, String(cell), cx + 14, yy + 13, cw - 28, rowH - 20, { size: opts.size ?? 13, color: dark ? "#DCE5F0" : C.ink, bold: i === 0, mono: opts.monoCols?.includes(i) });
      cx += cw;
    });
  });
  footer(slide, ctx, dark);
}

function drawCommand(slide, ctx, section, title, command, resultRows, number, opts = {}) {
  page(slide, ctx, section, title, number, { dark: true, titleSize: opts.titleSize ?? 30 });
  box(slide, ctx, 72, 154, 1136, 116, C.night2, C.lineDark);
  text(slide, ctx, "COMMAND", 96, 178, 180, 18, { size: 12, color: section.accent, bold: true });
  text(slide, ctx, command, 96, 210, 1076, 44, { size: opts.commandSize ?? 15, color: C.white, bold: true, mono: true });
  box(slide, ctx, 72, 302, 1136, 276, C.night2, C.lineDark);
  text(slide, ctx, "RESULT", 96, 326, 180, 18, { size: 12, color: C.lime, bold: true });
  resultRows.forEach((row, index) => {
    const yy = 372 + index * 42;
    rect(slide, ctx, 102, yy + 6, 10, 10, row[2] ?? C.lime, "#00000000");
    text(slide, ctx, row[0], 130, yy, 330, 22, { size: 14, color: "#DCE5F0", bold: true });
    text(slide, ctx, row[1], 470, yy, 680, 22, { size: 14, color: row[2] ?? C.lime, bold: true, mono: opts.mono });
  });
  if (opts.guardrail) {
    box(slide, ctx, 96, 604, 1088, 42, C.night, C.coral);
    text(slide, ctx, opts.guardrail, 126, 616, 1028, 18, { size: 13, color: C.white, bold: true, align: "center" });
  }
  footer(slide, ctx, true);
}

function drawScreenshot(slide, ctx, section, title, imageBytes, number, opts = {}) {
  page(slide, ctx, section, title, number, { dark: opts.dark, titleSize: opts.titleSize ?? 29 });
  const dark = opts.dark ?? false;
  const y = opts.y ?? 140;
  const h = opts.h ?? 500;
  const x = opts.x ?? 92;
  const w = opts.w ?? 1096;
  addImage(slide, imageBytes, x, y, w, h, title, section.accent, "contain");
  if (opts.caption) {
    box(slide, ctx, 120, 656, 1040, 28, dark ? C.night2 : opts.captionFill ?? C.paleBlue, section.accent);
    text(slide, ctx, opts.caption, 146, 664, 988, 12, { size: 11, color: dark ? C.white : C.ink, bold: true, align: "center" });
  }
  footer(slide, ctx, dark);
}

function drawMetrics(slide, ctx, section, title, number) {
  page(slide, ctx, section, title, number, { dark: true });
  const metrics = [
    ["84 / 84", "controlled expected versions", C.lime],
    ["47 / 47", "clean real APK emitted versions", C.cyan],
    ["880 / 1790", "partial real APK confirmations", C.gold],
    ["927 / 1837", "all source-validated emitted rows", C.blue],
    ["50.5%", "emitted Maven version confirmation", C.coral],
    ["6772 / 6772", "source-known v2 upper-bound rows", C.violet],
  ];
  metrics.forEach((m, i) => {
    const x = 72 + (i % 3) * 382;
    const y = 164 + Math.floor(i / 3) * 178;
    box(slide, ctx, x, y, 340, 126, C.night2, m[2]);
    text(slide, ctx, m[0], x + 24, y + 28, 292, 38, { size: 33, color: m[2], bold: true, face: ctx.fonts.title, align: "center" });
    text(slide, ctx, m[1], x + 28, y + 78, 284, 24, { size: 13, color: "#C4CEDA", bold: true, align: "center" });
  });
  box(slide, ctx, 126, 550, 1028, 46, C.night, C.coral);
  text(slide, ctx, "These numbers are deliberately separated. The 50.5 percent result is emitted-version confirmation, not full dependency recall.", 152, 564, 976, 18, { size: 14, color: C.white, bold: true, align: "center" });
  footer(slide, ctx, true);
}

function drawLiveDemoTransition(slide, ctx, section, number) {
  page(slide, ctx, section, "Now I will show the working system live", number, { dark: true, titleSize: 38 });
  const steps = [
    ["1", "Verify readiness", "Run the one-command defense checker and confirm the report-only AI guardrail."],
    ["2", "Open the clean APK report", "Show recovered components, CycloneDX output, source validation, and zero confirmed vulnerabilities."],
    ["3", "Open the vulnerable Jackson report", "Show exact version detection and the confirmed OSV CVE findings."],
    ["4", "Show the AI/R8 guardrail", "Explain that AI appears in reports but does not change SBOM or CVE authority."],
  ];
  steps.forEach((step, i) => {
    const x = 86 + (i % 2) * 558;
    const y = 164 + Math.floor(i / 2) * 178;
    box(slide, ctx, x, y, 504, 132, C.night2, i < 2 ? C.cyan : C.gold);
    shape(slide, ctx, "ellipse", x + 24, y + 28, 54, 54, i < 2 ? C.cyan : C.gold, "#00000000");
    text(slide, ctx, step[0], x + 24, y + 42, 54, 24, { size: 22, color: C.night, bold: true, align: "center" });
    text(slide, ctx, step[1], x + 100, y + 30, 360, 26, { size: 21, color: C.white, bold: true });
    text(slide, ctx, step[2], x + 100, y + 66, 360, 42, { size: 13, color: "#BFCADA" });
  });
  box(slide, ctx, 126, 552, 1028, 62, C.night, C.coral);
  text(slide, ctx, "The proof will be shown directly from generated reports, CycloneDX output, OSV findings, and saved validation artifacts.", 156, 570, 968, 24, { size: 16, color: C.white, bold: true, align: "center" });
  footer(slide, ctx, true);
}

async function writeBlob(filePath, blob) {
  await fs.writeFile(filePath, new Uint8Array(await blob.arrayBuffer()));
}

async function createContactSheet(slideResults, outPath) {
  const thumbW = 320;
  const thumbH = 180;
  const gap = 18;
  const labelH = 24;
  const cols = 4;
  const rows = Math.ceil(slideResults.length / cols);
  const canvas = new Canvas(cols * thumbW + (cols + 1) * gap, rows * (thumbH + labelH) + (rows + 1) * gap);
  const ctx = canvas.getContext("2d");
  ctx.fillStyle = "#F6F8FB";
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  ctx.font = "bold 14px Arial";
  ctx.fillStyle = "#596575";
  for (const [index, row] of slideResults.entries()) {
    const image = await loadImage(row.previewPath);
    const col = index % cols;
    const rowIndex = Math.floor(index / cols);
    const x = gap + col * (thumbW + gap);
    const y = gap + rowIndex * (thumbH + labelH + gap);
    ctx.drawImage(image, x, y, thumbW, thumbH);
    ctx.strokeStyle = "#D6DEE8";
    ctx.lineWidth = 1;
    ctx.strokeRect(x, y, thumbW, thumbH);
    ctx.fillText(`Slide ${String(index + 1).padStart(2, "0")}`, x, y + thumbH + 18);
  }
  await fs.writeFile(outPath, await canvas.toBuffer("png"));
}

async function cropImage(bytes, topRatio, heightRatio) {
  const image = await loadImage(bytes);
  const sourceWidth = image.width;
  const sourceHeight = image.height;
  const sourceY = Math.max(0, Math.round(sourceHeight * topRatio));
  const sourceH = Math.min(sourceHeight - sourceY, Math.round(sourceHeight * heightRatio));
  const canvas = new Canvas(sourceWidth, sourceH);
  const ctx = canvas.getContext("2d");
  ctx.fillStyle = "#FFFFFF";
  ctx.fillRect(0, 0, sourceWidth, sourceH);
  ctx.drawImage(image, 0, sourceY, sourceWidth, sourceH, 0, 0, sourceWidth, sourceH);
  return await canvas.toBuffer("png");
}

async function loadAssets() {
  return {
    fig: {},
    zoom: {},
  };
}

function addScreenshotSet(p, assets, name, title) {
  p.push({ type: "screenshot", section: sections.demo, title, image: assets.fig[name], caption: name });
  for (const spec of zoomSpecs[name] ?? []) {
    p.push({
      type: "screenshot",
      section: sections.demo,
      title: spec.title,
      image: assets.zoom[`${name}::${spec.id}`],
      x: 64,
      y: 124,
      w: 1152,
      h: 532,
      titleSize: 27,
    });
  }
}

function plan(assets) {
  const p = [];
  p.push({ type: "title" });
  p.push({ type: "section", section: sections.intro, title: "Introduction", points: ["The defense starts from compiled APKs, not source projects.", "The goal is a useful security artifact with visible evidence.", "The Master thesis frames trust, and the Engineering thesis implements the pipeline."] });
  p.push({ type: "old", old: 2 });
  p.push({ type: "content", section: sections.intro, title: "The project answers one practical question", bullets: ["Can a compiled Android APK become a useful SBOM without pretending weak evidence is certain?", "Useful means CycloneDX output, PURL identities, confidence labels, ambiguity, and CVE interpretation.", "Unsafe means forced exact versions, hidden denominator gaps, and unqualified vulnerability claims."], callout: "The project is about bounded recovery, not perfect reverse engineering." });
  p.push({ type: "content", section: sections.intro, title: "Two theses support one defense story", bullets: ["Master thesis: evidence model, state-of-the-art review, trust taxonomy, and research agenda.", "Engineering thesis: implemented APK extraction, matching, SBOM generation, CVE lookup, reports, and evaluation.", "Old presentation: architecture, results, demo proof, AI evidence, and command-ready defense outputs."], callout: "Research explains why the gates exist. Engineering shows that the gates were implemented." });

  p.push({ type: "section", section: sections.background, title: "Background", points: ["SBOMs are easy when build metadata exists.", "A compiled Android APK has transformed evidence.", "Trust depends on separating identity, version, and vulnerability authority."] });
  p.push({ type: "content", section: sections.background, title: "An SBOM is useful only when its claims are trustworthy", bullets: ["CycloneDX and SPDX define exchange formats.", "PURL connects a component to its package ecosystem.", "A recovered APK component can be strong at identity level but weak at exact-version level.", "CVE interpretation must inherit the confidence of the component and version claim."], callout: "The format carries the result. The evidence determines how much to trust it." });
  p.push({ type: "content", section: sections.background, title: "Android compilation changes the evidence before analysis", bullets: ["Gradle resolves direct and transitive dependencies before packaging.", "D8 turns Java and Kotlin bytecode into DEX.", "R8 can rename, shrink, inline, optimize, and merge evidence.", "The released APK contains bytecode, resources, manifest metadata, native files, and signatures, but not the original dependency graph."], callout: "The analyzer sees the result of the build, not the developer dependency tree." });
  p.push({ type: "content", section: sections.background, title: "The trust boundary has three decisions", bullets: ["Identity asks whether a component family or Maven coordinate is present.", "Version asks which exact release is supported by APK evidence.", "Vulnerability authority asks whether the version claim is strong enough for a confirmed CVE label.", "The system can report uncertainty instead of forcing a false exact answer."], callout: "This boundary is the main defense against overclaiming." });

  p.push({ type: "section", section: sections.state, title: "State of the Art", points: ["The Master thesis focuses on the evidence behind component recovery.", "Prior tools expose useful ideas but not a complete trustworthy SBOM pipeline.", "R8 and realistic datasets lower what version-level recovery can honestly claim."] });
  p.push({ type: "old", old: 3 });
  p.push({ type: "content", section: sections.state, title: "The literature evolves through three evidence families", bullets: ["Generation 1 uses signatures, package names, hashes, and profiles.", "Generation 2 uses structural similarity, opcodes, graphs, and fuzzy matching.", "Generation 3 uses learned models and language-model features for obfuscation and R8 resilience.", "Each generation improves one failure mode while exposing another."], callout: "The thesis does not rank tools blindly. It extracts design constraints." });
  p.push({ type: "content", section: sections.state, title: "The main gap is trustworthy version authority", bullets: ["Library identity can remain visible when exact-version evidence is weak.", "Optimization and inlining remove method boundaries used by many detectors.", "Public evaluations often use different datasets, transformations, and correctness units.", "Most tools detect libraries but do not emit CycloneDX SBOM plus CVE-aware uncertainty."], callout: "The project contribution starts where the literature is weakest." });
  p.push({ type: "table", section: sections.state, title: "Related works solve parts of the problem, not the whole workflow", headers: ["Related work", "Main strength", "Limit for this thesis"], cols: [0.24, 0.38, 0.38], rowH: 62, rows: [["LibRadar / package clustering", "Fast candidate discovery at market scale", "No reliable exact-version or SBOM authority"], ["LibScout / reference profiles", "Version-aware profiles from known libraries", "Older assumptions; weak under shrinking, partial imports, and R8"], ["LibPecker / SAD / LibScan", "Structural, class, opcode, and version-similarity evidence", "Strong detector ideas, but no full CycloneDX and CVE workflow"], ["LibAttention", "Learned R8-resilient library presence", "No exact versions, so it cannot be the SBOM authority"], ["LibMD / UniBOM", "Closest SBOM-oriented direction", "LibMD is unreleased; UniBOM is not Android APK recovery"]] });
  p.push({ type: "table", section: sections.state, title: "The limits of prior tools become MVP requirements", headers: ["Limit in related work", "Risk in a defense", "MVP response"], cols: [0.32, 0.31, 0.37], rowH: 58, rows: [["Package/name dependence", "A renamed library can look absent or wrong", "Use names only as weak evidence"], ["Adjacent-version confusion", "Wrong CVE positives or missed CVEs", "Separate identity and exact-version confidence"], ["R8 optimization", "Methods and structures used by tools disappear", "Report uncertainty; keep R8/AI evidence guarded"], ["No standard SBOM", "Detector output cannot enter security workflows", "Emit CycloneDX with PURLs and evidence"], ["Inflated comparison metrics", "One score hides hard real APK cases", "Separate controlled, clean, partial, and upper-bound lanes"]] });
  p.push({ type: "content", section: sections.state, title: "Realistic benchmarks reset the comparison baseline", bullets: ["SAD reports strong version-level results, but heavy inlining and public reproduction remain limits.", "TPL-Benchmark reports a realistic best library-level F1 of 60.15 percent among ten tools.", "Advanced-obfuscation studies show version-level F1 can fall below 10 percent.", "LibAttention improves R8 library-presence detection, but it does not solve exact version recovery.", "This project therefore compares through capability, evidence boundaries, and denominators, not a single headline F1."], gap: 52, rowH: 36, callout: "The honest comparison is: what claim can each method safely support?" });
  p.push({ type: "table", section: sections.state, title: "The Master thesis turns state of the art into requirements", headers: ["Finding", "Implication", "Engineering response"], cols: [0.28, 0.34, 0.38], rows: [["R8 weakens names and structure", "Do not rely on one signal", "Use multi-signal matching and report uncertainty"], ["Exact versions are fragile", "Separate identity from version", "Use confidence labels and ambiguity gates"], ["SBOM output is rare", "Detection alone is not enough", "Emit CycloneDX and PURL"], ["CVE claims need authority", "Weak version evidence can mislead", "Gate confirmed and potential findings"]] });

  p.push({ type: "section", section: sections.contribution, title: "Contribution", points: ["The contribution is a working evidence-gated APK-to-SBOM system.", "It connects research trust boundaries to implemented output fields.", "It keeps experimental AI and R8 evidence separate from authoritative SBOM decisions."] });
  p.push({ type: "old", old: 4 });
  p.push({ type: "old", old: 5 });
  p.push({ type: "old", old: 6 });
  p.push({ type: "content", section: sections.contribution, title: "The contribution is not only a detector", bullets: ["It extracts APK evidence and normalizes DEX features.", "It builds a Maven reference database for bytecode-level comparison.", "It matches candidate components using multiple evidence families.", "It emits CycloneDX, human reports, OSV results, confidence labels, and ambiguity.", "It preserves source-validation and command-run evidence for audit."], callout: "The final artifact is an auditable security report, not a private score." });

  p.push({ type: "section", section: sections.implementation, title: "Implementation", points: ["This section follows the Engineering thesis solution.", "Each component has a clear role in the APK-to-report path.", "Evaluation is presented with honest denominators and guarded AI evidence."] });
  [7, 8, 9, 10, 11, 12, 13, 14].forEach((old) => p.push({ type: "old", old }));
  p.push({ type: "content", section: sections.implementation, title: "The implemented command produces a report bundle", bullets: ["Input: APK file and reference database.", "Processing: extract APK, analyze DEX, match references, decide versions, query OSV.", "Output: matches.json, sbom.cdx.json, report.json, report.md, report.html, and osv-vulnerabilities.json.", "Optional AI and R8 sections are report-only attachments."], callout: "The output bundle is designed for both human review and automated SBOM tooling." });
  [15, 16, 17, 18, 19].forEach((old) => p.push({ type: "old", old }));
  p.push({ type: "metrics", section: sections.implementation, title: "The evaluation separates controlled results, real APKs, and upper bounds" });
  p.push({ type: "old", old: 20 });
  p.push({ type: "old", old: 21 });
  p.push({ type: "table", section: sections.implementation, title: "After the results, the MVP compares differently from related work", headers: ["Dimension", "Related works usually report", "This project reports"], cols: [0.24, 0.37, 0.39], rowH: 60, rows: [["Output", "Detected libraries, versions, or scores", "CycloneDX SBOM, PURLs, OSV findings, JSON/HTML evidence"], ["Correctness unit", "Often one dataset-level precision/recall/F1", "Controlled, clean, partial, source-known, and boundary lanes"], ["Version authority", "Top candidate or tool-specific confidence", "Identity confidence, version confidence, alternatives, and abstention"], ["R8/AI handling", "Specialized detector or learned model result", "Report-only diagnostics until controls pass"], ["Security interpretation", "Vulnerability list or separate analysis", "Confirmed vs potential CVE labels inherit version confidence"]] });
  p.push({ type: "content", section: sections.implementation, title: "The contribution is practical evidence control, not a universal best score", bullets: ["Compared with LibRadar, the MVP is slower but produces versioned SBOM evidence.", "Compared with LibScout, it keeps the reference-profile idea but adds confidence and modern evidence families.", "Compared with SAD, LibScan, and LibMD, it is a simpler implemented MVP, but it emits standard SBOM and CVE artifacts.", "Compared with LibAttention, AI is not used as authority because the thesis needs exact versions.", "Compared with TPL-Benchmark, the project follows the lesson that realistic APK evaluation must expose denominator limits."], gap: 52, rowH: 36, callout: "The fair claim is not that the MVP beats every detector; it completes a trustworthy APK-to-SBOM workflow with visible limits." });
  p.push({ type: "old", old: 24 });
  p.push({ type: "old", old: 25 });
  p.push({ type: "old", old: 26 });
  p.push({ type: "old", old: 27 });
  p.push({ type: "old", old: 28 });

  p.push({ type: "demoTransition", section: sections.demo });

  p.push({ type: "section", section: sections.conclusion, title: "Conclusion", points: ["The project recovers useful APK-derived SBOM evidence without overstating certainty.", "The limitations are visible in the report and in the evaluation denominators.", "Future work expands references, matcher recall, native attribution, dynamic-code handling, and calibrated AI assistance."] });
  p.push({ type: "old", old: 30 });
  p.push({ type: "content", section: sections.conclusion, title: "The main limitations define the next research work", bullets: ["Reference coverage still limits exact-version recovery.", "Matcher recall remains hard for partial real APKs and transformed libraries.", "Native libraries and dynamically loaded code need separate attribution methods.", "AI evidence is useful for triage, but not yet authoritative for SBOM or CVE labels.", "Public benchmarks need exact denominators, transformation labels, and reproducible APK/source pairs."], callout: "The next step is to improve evidence, not to hide uncertainty." });
  p.push({ type: "old", old: 31 });
  return p;
}

const legacyTitles = {
  2: "The Problem",
  3: "Research Positioning",
  4: "Project Objective",
  5: "Architecture Decisions",
  6: "System Architecture",
  7: "APK Extractor",
  8: "DEX Analyzer",
  9: "Reference Database",
  10: "Matcher",
  11: "Version Decision",
  12: "SBOM Generator",
  13: "CVE and OSV",
  14: "Reports",
  15: "Dataset Design",
  16: "Dataset Collection",
  17: "APK Classification",
  18: "Dataset Composition",
  19: "Evaluation Methodology",
  20: "Evaluation Results",
  21: "Upper-Bound Experiment",
  24: "Failed Experiments",
  25: "AI Problem Formulation",
  26: "Classical ML",
  27: "Deep Learning",
  28: "AI Integration Gate",
  30: "Limitations and Future Work",
  31: "Final Closing",
};

function slideTitleFor(item) {
  if (item.type === "title") return "Title";
  if (item.type === "demoTransition") return "Live Demo Transition";
  if (item.type === "old") return legacyTitles[item.old] ?? `Legacy Slide ${item.old}`;
  return item.title ?? item.section?.label ?? "Slide";
}

function speechFor(item, number) {
  const title = slideTitleFor(item);
  const generic = `On this page, I explain ${title.toLowerCase()} and connect it back to the same principle: APK-derived SBOM claims must stay tied to visible evidence, confidence, and validation boundaries.`;
  const byTitle = {
    "Title": "Good morning respected jury members, supervisors, and guests. My name is Fendi Mohamed, and I am presenting my graduation project on evidence-based SBOM recovery from compiled Android APKs. The goal is to recover useful software component evidence from APK files, generate CycloneDX SBOM output, and connect that evidence to CVE analysis while being honest about uncertainty.",
    "Introduction": "I begin with the practical audit situation: sometimes we receive only the compiled APK, not the source project. The defense story is therefore about recovering useful evidence from that artifact while keeping uncertainty visible.",
    "The Problem": "The problem begins when dependency metadata disappears during compilation and packaging. A source project can declare Gradle dependencies, but the released APK contains transformed DEX bytecode, resources, native files, and signatures.",
    "The project answers one practical question": "The practical question is whether a compiled APK can become a useful SBOM without pretending weak evidence is certain. Useful means component identities, selected versions when justified, confidence labels, ambiguity, CycloneDX output, and CVE interpretation.",
    "Two theses support one defense story": "The Master thesis provides the research framing, state of the art, and trust model. The PFE thesis implements the APK analysis pipeline, reference database, matcher, SBOM generator, OSV lookup, reports, evaluation, and demo evidence.",
    "Background": "Before the system design, I define the technical objects: APK, DEX, SBOM, PURL, CVE, R8, and confidence. The key idea is that each object gives a different level of evidence.",
    "An SBOM is useful only when its claims are trustworthy": "An SBOM format such as CycloneDX makes the result machine-readable, but the format alone does not prove the component is present. The trust comes from the evidence behind the component identity and exact version.",
    "Android compilation changes the evidence before analysis": "Android compilation transforms Java and Kotlin dependencies into DEX. D8 performs bytecode conversion, and R8 can rename, shrink, inline, optimize, and merge code, so the analyzer sees the shipped artifact rather than the original dependency tree.",
    "The trust boundary has three decisions": "The system separates component identity, exact version, and vulnerability authority. This prevents a plausible library match from automatically becoming a confirmed exact-version CVE claim.",
    "State of the Art": "The related-work section explains where my method comes from and why the contribution is not simply another detector. The literature gives useful signals, but also shows why exact version recovery is fragile.",
    "Research Positioning": "I position the project between Android third-party library detection and practical SBOM/CVE workflows. Prior work often detects libraries, while this project focuses on auditable SBOM output and confidence-aware vulnerability interpretation.",
    "The literature evolves through three evidence families": "The first family uses names, hashes, package signatures, and profiles. The second uses structure, graphs, opcodes, and fuzzy matching. The third uses learned representations for R8 and obfuscation. Each generation improves one weakness but does not remove the need for evidence gates.",
    "The main gap is trustworthy version authority": "The gap is not only finding a library family. The hard part is deciding whether the exact version is strong enough for SBOM and CVE authority, especially after R8 and partial library inclusion.",
    "Related works solve parts of the problem, not the whole workflow": "Here I compare the main related works by what they are best at and where they stop. LibRadar is fast, LibScout motivates version profiles, structural tools improve matching, LibAttention helps R8 presence detection, and SBOM-oriented tools guide the output direction. None of them alone gives the complete APK-to-CycloneDX-to-CVE workflow implemented here.",
    "The limits of prior tools become MVP requirements": "This slide turns limitations into design requirements. If names are fragile, names become weak evidence. If adjacent versions are hard, identity and version confidence must be separated. If many tools lack SBOM output, the MVP must emit CycloneDX and PURLs.",
    "Realistic benchmarks reset the comparison baseline": "I do not compare only against optimistic paper numbers. TPL-Benchmark and obfuscation studies show that realistic datasets and advanced R8 reduce performance strongly, especially for exact version recovery. That is why my evaluation separates denominators instead of giving one inflated score.",
    "The Master thesis turns state of the art into requirements": "The Master thesis converts the literature into engineering requirements: multi-signal matching, explicit confidence, CycloneDX output, PURL identity, and confirmed-versus-potential CVE labels.",
    "Contribution": "Now I move from related work to my contribution. The contribution is a working evidence-gated APK-to-SBOM pipeline, not a claim that every APK can be perfectly reconstructed.",
    "Project Objective": "The objective is to start from a compiled APK and produce a security artifact that a human can inspect and a tool can consume. The artifact includes detected Maven components, versions when supported, CycloneDX output, OSV findings, and evidence reports.",
    "Architecture Decisions": "The architecture decisions follow from the research: static analysis first, Maven reference profiles, DEX-to-DEX comparison, CycloneDX output, OSV lookup, and confidence instead of forced precision.",
    "System Architecture": "The system has two main lanes: the APK evidence lane and the Maven reference lane. The matcher compares them, the confidence gate decides what can be emitted, and the reporting layer exposes the evidence.",
    "The contribution is not only a detector": "The project is not only a list of detected libraries. It extracts evidence, builds references, matches candidates, chooses versions carefully, emits CycloneDX, queries OSV, and generates reviewable reports.",
    "Implementation": "The implementation section follows the PFE thesis. I describe how the main modules work and how the evaluation proves the system behavior without hiding limits.",
    "APK Extractor": "The APK extractor unpacks the APK and records container evidence: DEX files, manifest, resources, native files, hashes, and metadata. This makes every report traceable to the analyzed input.",
    "DEX Analyzer": "The DEX analyzer extracts code-level evidence: packages, classes, methods, opcode fingerprints, literals, API references, and dependency structure. These features become the basis for matching.",
    "Reference Database": "The reference database stores features from selected Maven JAR and AAR releases. Because exact version claims need known references, reference coverage directly affects what the tool can recover.",
    "Matcher": "The matcher compares APK evidence with reference evidence and ranks candidates. It uses multiple evidence families, but it does not force every top candidate into a confirmed version.",
    "Version Decision": "The version decision stage checks whether the best candidate is strong and separated from alternatives. If versions are too close, the report preserves ambiguity instead of inventing certainty.",
    "SBOM Generator": "The SBOM generator emits accepted components in CycloneDX JSON using Maven PURLs. CycloneDX gives interoperability, while the surrounding report preserves confidence and evidence.",
    "CVE and OSV": "The vulnerability step queries OSV using package and version evidence. Confirmed CVEs require sufficiently strong component and version evidence; weaker cases remain potential or report-only.",
    "Reports": "The report layer is central because it shows what the system decided and why. JSON, Markdown, HTML, CycloneDX, and OSV artifacts are generated from the same evidence.",
    "Dataset Design": "The dataset is layered. Controlled APKs answer whether the pipeline works under known ground truth, clean real APKs show favorable real cases, partial real APKs expose limits, and boundary cases prevent overclaiming.",
    "Dataset Collection": "For real APKs, source links and dependency trees were collected when possible. The point is not only to run many APKs, but to know which outputs can be verified.",
    "APK Classification": "APK classification explains difficulty: clear, multidex, R8, native-heavy, hidden-code, and source-boundary cases do not support the same claims. Classification keeps evaluation honest.",
    "Dataset Composition": "This page summarizes the dataset groups used in the evaluation. The important point is that controlled, clean, partial, source-known, and boundary lanes are reported separately.",
    "Evaluation Methodology": "The methodology separates exact expected-version recovery from emitted-version confirmation and from source-known upper-bound recognition. These are different questions and must not be mixed.",
    "The evaluation separates controlled results, real APKs, and upper bounds": "The headline numbers are deliberately separated: 84 out of 84 controlled expected versions, 47 out of 47 clean real emitted versions, 880 out of 1790 partial real emitted versions, and 927 out of 1837 source-validated emitted rows overall.",
    "Evaluation Results": "The results show that the pipeline works well where evidence and references are strong, while real APKs still expose ambiguity and coverage limits. This is a useful result because it says exactly where the system is reliable.",
    "Upper-Bound Experiment": "The source-known v2 lane asks a different question: if the correct coordinate and version slice is known from source, can the matcher recognize it? This is an upper bound, not general APK-only accuracy.",
    "After the results, the MVP compares differently from related work": "After the implementation and results, the comparison changes. Related works usually report detector metrics, while this project reports SBOM artifacts, confidence labels, source-validation lanes, and vulnerability authority.",
    "The contribution is practical evidence control, not a universal best score": "The fair claim is not that this MVP beats every detector on every metric. The fair claim is that it completes a practical APK-to-SBOM workflow and exposes where the evidence is strong, weak, or missing.",
    "Failed Experiments": "Failed experiments are included because they protect the production tool. A signal can help one target but still be unsafe globally if it creates regressions in controls.",
    "AI Problem Formulation": "Before using machine learning, I first defined the task very carefully. The AI task is not to choose the final Maven version. The task is supervised multiclass classification over existing project evidence rows.\n\nEach training example is one matcher or transparency row. The input features describe what the deterministic system already observed: match scores, score gaps, identity confidence, version confidence, overlap counts, dependency evidence, boundary flags, source-validation context, and diagnostic signals. The output label is a report role, such as confirmed_exact, suggest_report_only, suppress_uncertain, risk_only, mismatch_or_extra, or boundary_do_not_suggest.\n\nThe important methodology decision is the split. I did not randomly mix similar rows into train and test. The dataset is grouped by case_id so that related rows from the same APK case do not leak across splits. The corpus used 20,523 training-eligible rows, 149 grouped case IDs, and 1,370 Maven coordinates, with 104 train cases, 15 validation cases, and 30 test cases.\n\nSo, when I present the AI part, I should say: AI is learning how to classify evidence quality and triage hard cases. It is not learning permission to emit final SBOM components.",
    "Classical ML": "The first AI model is RandomForestClassifier. A Random Forest is an ensemble of decision trees. One decision tree predicts a label by asking a sequence of feature questions, for example whether confidence is high, whether a boundary flag exists, or whether the score gap is small. A single tree can overfit, so Random Forest trains many trees on different samples and feature subsets, then combines their votes. This gives a more stable model and also gives feature-importance values, which are useful in a defense.\n\nThe ML workflow was: build labeled rows from project evidence, extract structured numeric and categorical features, group the data by case_id, train the RandomForest with class-balancing, compare it to simple baselines, evaluate on held-out test cases, inspect feature importance and ablations, then integrate it only as report annotations.\n\nThe result was a test macro-F1 of 0.708 and test accuracy of 0.690. This is clearly above the majority baseline accuracy of 0.383 and the simple score-threshold baseline of 0.165. The important features included identity confidence, boundary flags, best score, source rank, and dependency score. The model produced 13,736 report-only suggestions.\n\nThe defense conclusion is: RandomForest is useful because the evidence is tabular and explainable, but it remains report-only. It can suggest where a reviewer should look; it cannot change selected versions, CycloneDX components, or CVE labels.",
    "Deep Learning": "The deep-learning part uses Transformer encoders. A Transformer is a neural sequence model based on attention. Instead of reading features only as separate columns, it can read a sequence of tokens and learn which tokens should pay attention to each other. This is useful when the meaning depends on combinations of evidence, such as confidence, boundary status, score gaps, and report context.\n\nI tested two DL directions. The first direction used structured project-evidence tokens. Each evidence row was converted into a token sequence, then trained with a small torch.nn.TransformerEncoder. The MVP-safe run used a 1-layer encoder with d_model 64 and 4 attention heads. The split was 14,905 training rows, 1,750 validation rows, and 3,868 test rows.\n\nThe full structured-token Transformer reached 0.977 test macro-F1 and 0.992 test accuracy, but I do not present it as production authority because shortcut context may inflate the score. Therefore I also trained the MVP-safe profile, which removes source-version, raw candidate-version, source-rank, source-validation-role, and diagnostic-context shortcut tokens. That stricter profile reached 0.882 test macro-F1 and 0.907 test accuracy.\n\nThe second direction was a raw-opcode Transformer. That corpus had 1,680 method-level opcode sequences from 14 APKs, evaluated with a case-heldout split. It reached only 0.110 test macro-F1, below the opcode-count logistic-regression baseline of 0.128. This is an honest negative result: raw method opcodes alone are not enough yet.\n\nThe defense conclusion is: the structured Transformer proves a useful DL workflow for report-only triage, while the raw-opcode Transformer shows why I did not promote deep learning as the production APK detector.",
    "AI Integration Gate": "The AI integration gate is the safety boundary. The allowed role is assistance: AI can annotate risk, suggest report-only investigation, help prioritize difficult R8 or matcher-recall rows, and improve the human-readable report. The forbidden role is authority: AI cannot change selected versions, detected components, CycloneDX SBOM output, CVE or OSV labels, or source-validation metrics.\n\nThis gate exists because the output is a security artifact. A wrong AI prediction could create a false CVE claim or hide a real vulnerable version. Also, no strict APK-only AI promotion candidate passed all target and control requirements, and the raw-opcode DL model did not beat its baseline.\n\nSo the sentence I should use in the defense is: AI helps decide where to look, but the deterministic evidence gate decides what enters the SBOM and what becomes a confirmed vulnerability claim.",
    "Live Demo Transition": "Now I will move from slides to the live demonstration. I will not show static screenshots in the deck. Instead, I will open the generated artifacts directly.\n\nDemo steps and commands:\n\n1. Readiness check:\n\n```powershell\npython scripts\\run_final_ai_defense_demo.py --refresh\n```\n\nExpected result: 10 out of 10 checks passed, ready true, and matcher authority for AI remains false.\n\n2. Clean APK report:\n\nOpen `data/results/report-real-f-droid-final-demo-osv/report.html`, then show `sbom.cdx.json` and `source-validation.md`. The point is that the clean F-Droid case shows recovered Maven components, native file observations, low risk, and zero confirmed vulnerabilities.\n\n3. Positive CVE report:\n\nOpen `data/results/demo-osv-vulnerable-jackson-databind/report.html`, then show `osv-vulnerabilities.json`. The point is that Jackson Databind 2.9.10.8 produces confirmed HIGH CVE findings because exact version evidence is strong.\n\n4. Optional command used to regenerate reports, if asked:\n\n```powershell\ndocker compose run --rm apk-sbom python -m apk_sbom.cli generate-report <apk> --output-dir <result-dir> --db-path <reference-db> --top 30\n```\n\n5. Optional regression proof, if asked:\n\n```powershell\ndocker compose run --rm apk-sbom pytest -q\n```\n\nI should say clearly that long evaluations and large reference-DB rebuilds are not rerun live during the defense; the demo uses saved generated artifacts.",
    "Conclusion": "In conclusion, the project recovers useful APK-derived SBOM evidence without overstating certainty. The limitations are not hidden; they are part of the contribution.",
    "Limitations and Future Work": "The main limitations are reference coverage, matcher recall in difficult real APKs, R8 inlining, native version attribution, hidden code, and the need for larger independent AI/R8 corpora.",
    "Main Limitations": "The next work follows directly from the evidence gaps: broaden references safely, improve version-specific evidence, expand independent R8 datasets, and keep native and dynamic-code attribution as separate research tracks.",
    "Final Closing": "My final message is that the project does not claim perfect APK reverse engineering. It provides an implemented, auditable, confidence-aware APK-to-SBOM workflow that is honest about where its evidence is strong and where it must abstain.",
  };
  return byTitle[title] ?? generic;
}

async function writeSpeech(deckPlan, outPath) {
  const lines = ["# Presentation Speech Page By Page", ""];
  for (const [index, item] of deckPlan.entries()) {
    const pageNumber = index + 1;
    lines.push(`## Page ${pageNumber}: ${slideTitleFor(item)}`, "");
    lines.push(speechFor(item, pageNumber), "");
  }
  await fs.writeFile(outPath, lines.join("\n"));
}

async function cleanGeneratedSlides(dir, pattern) {
  let entries = [];
  try {
    entries = await fs.readdir(dir);
  } catch {
    return;
  }
  await Promise.all(
    entries
      .filter((entry) => pattern.test(entry))
      .map((entry) => fs.rm(path.join(dir, entry), { force: true })),
  );
}

async function build() {
  await fs.mkdir(OUTPUT_DIR, { recursive: true });
  await fs.mkdir(PREVIEW_DIR, { recursive: true });
  await fs.mkdir(LAYOUT_DIR, { recursive: true });
  await fs.mkdir(QA_DIR, { recursive: true });
  await fs.mkdir(ZOOM_DIR, { recursive: true });
  await cleanGeneratedSlides(PREVIEW_DIR, /^slide-\d+\.png$/);
  await cleanGeneratedSlides(LAYOUT_DIR, /^slide-\d+\.layout\.json$/);
  const presentation = Presentation.create({ slideSize: { width: 1280, height: 720 } });
  const ctx = makeContext();
  const assets = await loadAssets();
  ctx.assets = {};
  const deckPlan = plan(assets);
  const slideResults = [];
  for (const [index, item] of deckPlan.entries()) {
    const slideNumber = index + 1;
    const slide = item.type === "old"
      ? await (async () => {
          ctx.displayNumber = slideNumber;
          const oldSlide = await drawSlide(presentation, ctx, item.old);
          delete ctx.displayNumber;
          return oldSlide;
        })()
      : presentation.slides.add();
    if (item.type === "title") drawTitle(slide, ctx, slideNumber);
    if (item.type === "section") drawSection(slide, ctx, item.section, item.title, item.points, slideNumber);
    if (item.type === "content") drawContent(slide, ctx, item.section, item.title, item.bullets, slideNumber, item);
    if (item.type === "table") drawTableSlide(slide, ctx, item.section, item.title, item.headers, item.rows, slideNumber, item);
    if (item.type === "metrics") drawMetrics(slide, ctx, item.section, item.title, slideNumber);
    if (item.type === "command") drawCommand(slide, ctx, item.section, item.title, item.command, item.resultRows, slideNumber, item);
    if (item.type === "screenshot") drawScreenshot(slide, ctx, item.section, item.title, item.image, slideNumber, item);
    if (item.type === "demoTransition") drawLiveDemoTransition(slide, ctx, item.section, slideNumber);
    const stem = `slide-${String(slideNumber).padStart(2, "0")}`;
    const previewPath = path.join(PREVIEW_DIR, `${stem}.png`);
    const layoutPath = path.join(LAYOUT_DIR, `${stem}.layout.json`);
    await writeBlob(previewPath, await presentation.export({ slide, format: "png", scale: 1 }));
    await fs.writeFile(layoutPath, await (await slide.export({ format: "layout" })).text());
    slideResults.push({ index: slideNumber, type: item.type, oldSlide: item.old, title: item.title, previewPath, layoutPath });
  }
  const contactSheet = path.join(PREVIEW_DIR, "contact-sheet.png");
  await createContactSheet(slideResults, contactSheet);
  await writeBlob(path.join(PREVIEW_DIR, "deck-montage.webp"), await presentation.export({ format: "webp", montage: true, scale: 1 }));
  const pptx = await PresentationFile.exportPptx(presentation);
  await pptx.save(FINAL_PPTX);
  const stat = await fs.stat(FINAL_PPTX);
  await writeSpeech(deckPlan, path.join(OUTPUT_DIR, "presentation-speech-page-by-page.md"));
  await fs.writeFile(path.join(OUTPUT_DIR, "artifact-build-manifest.json"), JSON.stringify({
    output: FINAL_PPTX,
    outputBytes: stat.size,
    slideCount: presentation.slides.items.length,
    structure: ["Introduction", "Background", "State of the Art and Related Work", "Contribution", "Implementation and Results", "Live Demonstration", "Conclusion"],
    screenshotSlides: [],
    contactSheet,
    slides: slideResults,
  }, null, 2) + "\n");
  await fs.writeFile(path.join(QA_DIR, "build-notes.txt"), [
    "Expanded old-style graduation defense deck",
    "",
    "Requested changes addressed:",
    "- Presented by Fendi Mohamed added on the first slide.",
    "- Each agreed section has its own divider slide.",
    "- Section content expanded with dedicated explanation slides.",
    "- Related-work comparison and limitations added before the contribution.",
    "- Results are compared back to related work after the implementation and evaluation section.",
    "- Demo screenshots were removed from the deck.",
    "- A single live-demo transition slide remains, with demo steps and commands in the speech file.",
    "",
  ].join("\n"));
  console.log(JSON.stringify({ pptx: FINAL_PPTX, slides: presentation.slides.items.length, bytes: stat.size, contactSheet }, null, 2));
}

build().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
