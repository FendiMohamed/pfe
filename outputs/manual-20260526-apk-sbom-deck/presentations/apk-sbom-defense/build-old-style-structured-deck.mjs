import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { Presentation, PresentationFile } from "@oai/artifact-tool";
import { Canvas, loadImage } from "./node_modules/@oai/artifact-tool/node_modules/skia-canvas/lib/index.mjs";
import { drawSlide } from "./slides/common.mjs";

const ROOT = path.dirname(fileURLToPath(import.meta.url));
const REPO = path.resolve(ROOT, "..", "..", "..", "..");
const OUT_ROOT = path.join(REPO, "outputs", "graduation-defense-old-style-structured-deck");
const OUTPUT_DIR = path.join(OUT_ROOT, "output");
const PREVIEW_DIR = path.join(OUT_ROOT, "preview");
const LAYOUT_DIR = path.join(OUT_ROOT, "layout");
const QA_DIR = path.join(OUT_ROOT, "qa");
const ASSET_DIR = path.join(ROOT, "assets");
const PROOF_DIR = path.join(ASSET_DIR, "report-proof-screenshots");
const FINAL_PPTX = path.join(OUTPUT_DIR, "apk-sbom-defense-old-style-new-structure.pptx");

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

const sectionPlan = [
  { type: "old", old: 1, role: "Title" },
  {
    type: "section",
    label: "Introduction",
    title: "Why APK-derived SBOM recovery matters",
    points: ["Compiled APKs hide source dependency metadata.", "The defense starts from a security audit scenario.", "The target output is useful, bounded, and evidence-backed."],
    accent: C.blue,
  },
  { type: "old", old: 2, role: "Introduction" },
  { type: "old", old: 4, role: "Introduction" },
  {
    type: "section",
    label: "Background",
    title: "The task is static, post-build, and evidence-limited",
    points: ["The analyzer sees DEX, resources, manifests, native files, and report artifacts.", "Identity, version, and vulnerability authority are separate decisions.", "Uncertainty must remain visible instead of being hidden by the SBOM format."],
    accent: C.cyan,
  },
  { type: "old", old: 5, role: "Background" },
  {
    type: "section",
    label: "State of the Art",
    title: "The Master thesis turns prior tools into design constraints",
    points: ["Signature, structure, and learned approaches each fail differently.", "R8 and optimization make exact-version recovery harder than most early evaluations suggest.", "The literature supports hybrid evidence, abstention, and explicit trust boundaries."],
    accent: C.violet,
  },
  { type: "old", old: 3, role: "State of the Art" },
  { type: "state-gap", role: "State of the Art" },
  {
    type: "section",
    label: "Contribution",
    title: "The contribution is an evidence-gated APK-to-SBOM pipeline",
    points: ["The system separates extraction, matching, version decisions, SBOM output, and CVE interpretation.", "It reports confidence and ambiguity rather than forcing unsupported exact versions.", "AI and experimental signals remain report-only until they pass stronger gates."],
    accent: C.lime,
  },
  { type: "old", old: 6, role: "Contribution" },
  { type: "old", old: 23, role: "Contribution" },
  {
    type: "section",
    label: "Implementation",
    title: "The Engineering thesis implements the full analysis path",
    points: ["The implementation starts from APK extraction and DEX evidence.", "It builds Maven references, matches candidates, emits CycloneDX, and queries OSV.", "Evaluation separates controlled fixtures, real APKs, upper bounds, and failed experiments."],
    accent: C.gold,
  },
  { type: "old", old: 7, role: "Implementation" },
  { type: "old", old: 8, role: "Implementation" },
  { type: "old", old: 9, role: "Implementation" },
  { type: "old", old: 10, role: "Implementation" },
  { type: "old", old: 11, role: "Implementation" },
  { type: "old", old: 12, role: "Implementation" },
  { type: "old", old: 13, role: "Implementation" },
  { type: "old", old: 14, role: "Implementation" },
  { type: "old", old: 15, role: "Implementation" },
  { type: "old", old: 16, role: "Implementation" },
  { type: "old", old: 17, role: "Implementation" },
  { type: "old", old: 18, role: "Implementation" },
  { type: "old", old: 19, role: "Implementation" },
  { type: "old", old: 20, role: "Implementation" },
  { type: "old", old: 21, role: "Implementation" },
  { type: "old", old: 24, role: "Implementation" },
  { type: "old", old: 25, role: "Implementation" },
  { type: "old", old: 26, role: "Implementation" },
  { type: "old", old: 27, role: "Implementation" },
  { type: "old", old: 28, role: "Implementation" },
  {
    type: "section",
    label: "Demonstration",
    title: "The demo proves clean, vulnerable, and AI-assisted report surfaces",
    points: ["Clean F-Droid output shows no OSV findings.", "Controlled Jackson output confirms vulnerable exact-version CVEs.", "Hybrid AI sections are visible but do not change official SBOM or CVE authority."],
    accent: C.coral,
  },
  { type: "old", old: 22, role: "Demonstration" },
  { type: "old", old: 29, role: "Demonstration" },
  { type: "proof", proof: "clean-a", role: "Demonstration" },
  { type: "proof", proof: "clean-b", role: "Demonstration" },
  { type: "proof", proof: "vuln-a", role: "Demonstration" },
  { type: "proof", proof: "vuln-b", role: "Demonstration" },
  {
    type: "section",
    label: "Conclusion",
    title: "The final claim is bounded, auditable recovery",
    points: ["The work is useful because the output is standard and traceable.", "The limits are explicit in reference coverage, matcher recall, native code, and dynamic loading.", "Future work expands evidence safely rather than hiding uncertainty."],
    accent: C.gold,
  },
  { type: "old", old: 30, role: "Conclusion" },
  { type: "old", old: 31, role: "Conclusion" },
  {
    type: "section",
    label: "Backup",
    title: "Backup slides preserve the technical appendix",
    points: ["Repository structure, Docker packaging, matcher weights, APK families, source gaps, regression matrix, and AI details remain available.", "The main presentation should stop at the conclusion unless the jury asks for detail.", "These slides keep supporting evidence separate from the main defense structure."],
    accent: C.cyan,
  },
  { type: "old", old: 32, role: "Backup" },
  { type: "old", old: 33, role: "Backup" },
  { type: "old", old: 34, role: "Backup" },
  { type: "old", old: 35, role: "Backup" },
  { type: "old", old: 36, role: "Backup" },
  { type: "old", old: 37, role: "Backup" },
  { type: "old", old: 38, role: "Backup" },
  { type: "old", old: 39, role: "Backup" },
];

async function writeBlob(filePath, blob) {
  await fs.writeFile(filePath, new Uint8Array(await blob.arrayBuffer()));
}

function makeContext() {
  return {
    fonts: {
      title: "Aptos Display",
      body: "Aptos",
      mono: "Cascadia Mono",
    },
    line(fill, width = 1) {
      if (!fill || fill === "#00000000" || width === 0) return { style: "solid", fill: "none", width: 0 };
      return { style: "solid", fill, width };
    },
    addShape(slide, cfg) {
      return slide.shapes.add({
        geometry: cfg.geometry ?? "rect",
        name: cfg.name,
        position: { left: cfg.x, top: cfg.y, width: cfg.w, height: cfg.h },
        fill: cfg.fill ?? "none",
        line: cfg.line ?? { style: "solid", fill: "none", width: 0 },
      });
    },
    addText(slide, cfg) {
      const shape = slide.shapes.add({
        geometry: "textbox",
        name: cfg.name,
        position: { left: cfg.x, top: cfg.y, width: cfg.w, height: cfg.h },
        fill: cfg.fill === "#00000000" ? "none" : cfg.fill ?? "none",
        line: cfg.line ?? { style: "solid", fill: "none", width: 0 },
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
    line: opts.line ?? ctx.line("#00000000", 0),
  });
}

function rect(slide, ctx, x, y, w, h, fill, line = fill) {
  return ctx.addShape(slide, { geometry: "rect", x, y, w, h, fill, line: ctx.line(line, line === "#00000000" ? 0 : 1) });
}

function box(slide, ctx, x, y, w, h, fill = C.white, line = C.line) {
  return rect(slide, ctx, x, y, w, h, fill, line);
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

function drawSection(slide, ctx, item, number) {
  slide.background.fill = C.night;
  rect(slide, ctx, 0, 0, 1280, 720, C.night, "#00000000");
  rect(slide, ctx, 0, 0, 16, 720, item.accent, "#00000000");
  text(slide, ctx, item.label.toUpperCase(), 72, 64, 560, 26, { size: 13, color: item.accent, bold: true });
  text(slide, ctx, String(number).padStart(2, "0"), 1170, 38, 48, 22, { size: 12, color: "#8290A6", align: "right", bold: true });
  text(slide, ctx, item.title, 72, 150, 760, 120, { size: 42, color: C.white, bold: true, face: ctx.fonts.title });
  box(slide, ctx, 72, 322, 720, 2, item.accent, "#00000000");
  item.points.forEach((point, index) => {
    const y = 374 + index * 66;
    rect(slide, ctx, 78, y + 10, 12, 12, item.accent, "#00000000");
    text(slide, ctx, point, 110, y, 660, 38, { size: 18, color: "#D4DCE6", bold: true });
  });
  box(slide, ctx, 874, 150, 260, 260, C.night2, C.lineDark);
  text(slide, ctx, item.label, 904, 190, 200, 34, { size: 26, color: item.accent, bold: true, align: "center", face: ctx.fonts.title });
  text(slide, ctx, "Current section", 904, 256, 200, 24, { size: 14, color: "#B8C3D3", align: "center" });
  text(slide, ctx, "Research\nsystem\nevidence", 904, 306, 200, 72, { size: 16, color: C.white, bold: true, align: "center" });
  footer(slide, ctx, true);
}

function drawStateGap(slide, ctx, number) {
  slide.background.fill = C.paper;
  text(slide, ctx, "STATE OF THE ART", 66, 34, 760, 22, { size: 12, color: C.violet, bold: true });
  text(slide, ctx, "The Master thesis explains why existing detectors are not enough", 66, 64, 1040, 56, { size: 31, color: C.ink, bold: true, face: ctx.fonts.title });
  text(slide, ctx, String(number).padStart(2, "0"), 1170, 38, 48, 22, { size: 12, color: C.muted, align: "right", bold: true });
  const cards = [
    ["Over-optimistic metrics", "Early papers often report high F1 on limited datasets or weaker transformations.", C.coral, C.paleCoral],
    ["Version-level fragility", "Exact versions fail faster than coarse library identity under R8 and optimization.", C.gold, C.paleGold],
    ["No full SBOM toolchain", "Most work detects libraries; few emit standard SBOM plus vulnerability interpretation.", C.blue, C.paleBlue],
    ["Trust boundary gap", "CVE claims need provenance, confidence, ambiguity, and abstention.", C.cyan, C.paleCyan],
  ];
  cards.forEach((card, index) => {
    const x = 72 + (index % 2) * 572;
    const y = 168 + Math.floor(index / 2) * 170;
    box(slide, ctx, x, y, 520, 126, card[3], card[2]);
    text(slide, ctx, card[0], x + 24, y + 24, 472, 24, { size: 20, color: card[2], bold: true });
    text(slide, ctx, card[1], x + 24, y + 62, 456, 38, { size: 14, color: C.ink, bold: true });
  });
  box(slide, ctx, 104, 548, 1072, 46, C.night, C.night);
  text(slide, ctx, "Design implication: recover what the APK evidence supports, label what is uncertain, and keep unsafe signals out of authority paths.", 136, 562, 1008, 20, { size: 15, color: C.white, bold: true, align: "center" });
  footer(slide, ctx, false);
}

function addImage(slide, bytes, x, y, w, h, alt, line = C.line) {
  box(slide, { ...makeContext(), fonts: { title: "Aptos Display", body: "Aptos", mono: "Cascadia Mono" } }, x, y, w, h, C.white, line);
  return slide.images.add({
    blob: bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength),
    contentType: "image/png",
    alt,
    fit: "contain",
    position: { left: x + 12, top: y + 12, width: w - 24, height: h - 24 },
  });
}

function drawProofSlide(slide, ctx, item, number, proofAssets) {
  slide.background.fill = C.paper;
  const isVuln = item.proof.startsWith("vuln");
  const accent = isVuln ? C.coral : C.cyan;
  rect(slide, ctx, 0, 0, 1280, 720, C.paper, "#00000000");
  rect(slide, ctx, 0, 0, 16, 720, accent, "#00000000");
  text(slide, ctx, "PROTOTYPE OUTPUT PROOF", 48, 36, 420, 24, { size: 14, color: accent, bold: true });
  text(slide, ctx, String(number).padStart(2, "0"), 1208, 36, 40, 22, { size: 12, color: C.muted, align: "right", bold: true });

  if (item.proof === "clean-a") {
    text(slide, ctx, "Clean lane: F-Droid report pages show zero OSV findings", 48, 70, 990, 76, { size: 28, color: C.ink, bold: true, face: ctx.fonts.title });
    addImage(slide, proofAssets.clean01, 46, 154, 574, 492, "Clean F-Droid report page 1", C.line);
    addImage(slide, proofAssets.clean02, 660, 154, 574, 492, "Clean F-Droid report page 2", C.line);
    text(slide, ctx, "Source artifacts: data/results/demo-osv-clean-fdroid/report.html, report.json, report.md, sbom.cdx.json, osv-vulnerabilities.json", 70, 676, 1140, 24, { size: 10, color: C.muted });
  } else if (item.proof === "clean-b") {
    text(slide, ctx, "Clean lane continued: components, version decisions, native hashes, artifacts", 48, 70, 990, 76, { size: 28, color: C.ink, bold: true, face: ctx.fonts.title });
    addImage(slide, proofAssets.clean03, 42, 154, 366, 492, "Clean F-Droid report page 3", C.line);
    addImage(slide, proofAssets.clean04, 442, 154, 366, 492, "Clean F-Droid report page 4", C.line);
    addImage(slide, proofAssets.clean05, 842, 154, 366, 492, "Clean F-Droid report page 5", C.line);
    text(slide, ctx, "Clean claim: 23 Maven components, 4 native file hashes, 0 OSV vulnerabilities.", 68, 638, 1120, 26, { size: 13, color: C.cyan, bold: true, align: "center" });
    text(slide, ctx, "Full long image and copied raw output are in assets/report-proof-screenshots/clean-fdroid and original-output/clean-fdroid.", 70, 676, 1140, 24, { size: 10, color: C.muted });
  } else if (item.proof === "vuln-a") {
    text(slide, ctx, "Vulnerable lane: exact Jackson version match before OSV lookup", 48, 70, 990, 76, { size: 28, color: C.ink, bold: true, face: ctx.fonts.title });
    addImage(slide, proofAssets.vuln01, 46, 154, 574, 492, "Vulnerable Jackson report page 1", C.line);
    addImage(slide, proofAssets.vuln02, 660, 154, 574, 492, "Vulnerable Jackson report page 2", C.line);
    text(slide, ctx, "The component row is exact/high confidence: com.fasterxml.jackson.core:jackson-databind@2.9.10.8.", 70, 676, 1140, 24, { size: 10, color: C.muted });
  } else {
    text(slide, ctx, "Vulnerable lane: OSV returns 3 confirmed HIGH findings", 48, 70, 990, 76, { size: 28, color: C.ink, bold: true, face: ctx.fonts.title });
    addImage(slide, proofAssets.vuln03, 52, 154, 720, 470, "Vulnerable Jackson report page 3", C.line);
    box(slide, ctx, 806, 154, 380, 174, C.paleCoral, C.coral);
    text(slide, ctx, "Confirmed HIGH CVEs", 832, 188, 330, 30, { size: 20, color: C.coral, bold: true });
    text(slide, ctx, "CVE-2020-36518\nCVE-2022-42003\nCVE-2022-42004", 832, 238, 330, 88, { size: 20, color: C.ink, bold: true });
    box(slide, ctx, 806, 358, 380, 228, C.white, C.line);
    text(slide, ctx, "Copied output bundle", 832, 382, 330, 30, { size: 20, color: C.blue, bold: true });
    text(slide, ctx, "report.html\nreport.json\nreport.md\nsbom.cdx.json\nosv-vulnerabilities.json\nmatches.json", 832, 426, 330, 132, { size: 15, color: C.ink, bold: true, mono: true });
    text(slide, ctx, "Full long image and copied raw output are in assets/report-proof-screenshots/vulnerable-jackson and original-output/vulnerable-jackson.", 70, 676, 1140, 24, { size: 10, color: C.muted });
  }
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

async function loadProofAssets() {
  return {
    clean01: await fs.readFile(path.join(PROOF_DIR, "clean-fdroid", "clean-fdroid-report-page-01.png")),
    clean02: await fs.readFile(path.join(PROOF_DIR, "clean-fdroid", "clean-fdroid-report-page-02.png")),
    clean03: await fs.readFile(path.join(PROOF_DIR, "clean-fdroid", "clean-fdroid-report-page-03.png")),
    clean04: await fs.readFile(path.join(PROOF_DIR, "clean-fdroid", "clean-fdroid-report-page-04.png")),
    clean05: await fs.readFile(path.join(PROOF_DIR, "clean-fdroid", "clean-fdroid-report-page-05.png")),
    vuln01: await fs.readFile(path.join(PROOF_DIR, "vulnerable-jackson", "vulnerable-jackson-report-page-01.png")),
    vuln02: await fs.readFile(path.join(PROOF_DIR, "vulnerable-jackson", "vulnerable-jackson-report-page-02.png")),
    vuln03: await fs.readFile(path.join(PROOF_DIR, "vulnerable-jackson", "vulnerable-jackson-report-page-03.png")),
  };
}

async function build() {
  await fs.mkdir(OUTPUT_DIR, { recursive: true });
  await fs.mkdir(PREVIEW_DIR, { recursive: true });
  await fs.mkdir(LAYOUT_DIR, { recursive: true });
  await fs.mkdir(QA_DIR, { recursive: true });

  const presentation = Presentation.create({ slideSize: { width: 1280, height: 720 } });
  const ctx = makeContext();
  ctx.assets = {
    cleanReport: await fs.readFile(path.join(ASSET_DIR, "clean-report.png")),
    vulnerableReport: await fs.readFile(path.join(ASSET_DIR, "vulnerable-report-top.png")),
    aiReport: await fs.readFile(path.join(ASSET_DIR, "ai-report-top.png")),
  };
  const proofAssets = await loadProofAssets();
  const slideResults = [];

  for (const [index, item] of sectionPlan.entries()) {
    const slideNumber = index + 1;
    const slide = item.type === "old"
      ? await (async () => {
          ctx.displayNumber = slideNumber;
          const oldSlide = await drawSlide(presentation, ctx, item.old);
          delete ctx.displayNumber;
          return oldSlide;
        })()
      : presentation.slides.add();

    if (item.type === "section") drawSection(slide, ctx, item, slideNumber);
    if (item.type === "state-gap") drawStateGap(slide, ctx, slideNumber);
    if (item.type === "proof") drawProofSlide(slide, ctx, item, slideNumber, proofAssets);

    const stem = `slide-${String(slideNumber).padStart(2, "0")}`;
    const previewPath = path.join(PREVIEW_DIR, `${stem}.png`);
    const layoutPath = path.join(LAYOUT_DIR, `${stem}.layout.json`);
    await writeBlob(previewPath, await presentation.export({ slide, format: "png", scale: 1 }));
    await fs.writeFile(layoutPath, await (await slide.export({ format: "layout" })).text());
    slideResults.push({ index: slideNumber, type: item.type, oldSlide: item.old, role: item.role, previewPath, layoutPath });
  }

  const contactSheet = path.join(PREVIEW_DIR, "contact-sheet.png");
  await createContactSheet(slideResults, contactSheet);
  await writeBlob(path.join(PREVIEW_DIR, "deck-montage.webp"), await presentation.export({ format: "webp", montage: true, scale: 1 }));

  const pptx = await PresentationFile.exportPptx(presentation);
  await pptx.save(FINAL_PPTX);
  const stat = await fs.stat(FINAL_PPTX);

  await fs.writeFile(
    path.join(OUTPUT_DIR, "artifact-build-manifest.json"),
    JSON.stringify({
      output: FINAL_PPTX,
      outputBytes: stat.size,
      slideCount: presentation.slides.items.length,
      sourceStyle: "old academic APK SBOM defense deck",
      structure: ["Introduction", "Background", "State of the Art", "Contribution", "Implementation", "Demonstration", "Conclusion", "Backup"],
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
      "Old-style structured graduation defense deck",
      "",
      "Base style: existing academic APK SBOM defense deck.",
      `Slide count: ${presentation.slides.items.length}.`,
      "Main narrative follows: Introduction, Background, State of the Art, Contribution, Implementation, Demonstration, Conclusion.",
      "Backup slides preserve the old technical appendix after the conclusion.",
      "Proof slides recreate the old report-proof screenshots using the same geometry from the report-proof deck.",
      "",
    ].join("\n"),
  );

  console.log(JSON.stringify({ pptx: FINAL_PPTX, slides: presentation.slides.items.length, bytes: stat.size, contactSheet }, null, 2));
}

build().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
