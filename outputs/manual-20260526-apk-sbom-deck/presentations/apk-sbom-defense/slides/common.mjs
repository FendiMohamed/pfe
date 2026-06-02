const C = {
  bg: "#F6F8FB",
  panel: "#FFFFFF",
  panel2: "#EEF3F8",
  ink: "#151922",
  muted: "#596575",
  line: "#D6DEE8",
  dark: "#161B22",
  teal: "#1F9D8A",
  blue: "#356AC3",
  amber: "#D89A2B",
  red: "#C34E5A",
  green: "#367C59",
  purple: "#6F5FA8"
};

function note(slide, text) {
  if (slide.speakerNotes?.setText) slide.speakerNotes.setText(text);
}

function text(slide, ctx, value, x, y, w, h, opts = {}) {
  return ctx.addText(slide, {
    text: value,
    x, y, w, h,
    fontSize: opts.size ?? 24,
    color: opts.color ?? C.ink,
    bold: opts.bold ?? false,
    typeface: opts.face ?? (opts.mono ? ctx.fonts.mono : ctx.fonts.body),
    align: opts.align ?? "left",
    valign: opts.valign ?? "top",
    fill: opts.fill ?? "#00000000",
    line: opts.line ?? ctx.line("#00000000", 0),
    insets: opts.insets ?? { left: 8, right: 8, top: 4, bottom: 4 },
    name: opts.name
  });
}

function box(slide, ctx, x, y, w, h, fill = C.panel, line = C.line, name) {
  return ctx.addShape(slide, { x, y, w, h, fill, line: ctx.line(line, 1), name });
}

function rule(slide, ctx, x, y, w, h = 2, fill = C.line) {
  return ctx.addShape(slide, { x, y, w, h, fill, line: ctx.line("#00000000", 0), name: "rule" });
}

function header(slide, ctx, title, kicker, slideNo) {
  slide.background.fill = C.bg;
  text(slide, ctx, kicker.toUpperCase(), 56, 28, 760, 24, { size: 13, color: C.teal, bold: true });
  text(slide, ctx, title, 56, 58, 860, 58, { size: 28, bold: true, face: ctx.fonts.title });
  text(slide, ctx, String(slideNo).padStart(2, "0"), 1168, 32, 56, 26, { size: 13, color: C.muted, align: "right" });
  rule(slide, ctx, 56, 126, 1168, 2, C.line);
}

function footer(slide, ctx) {
  text(slide, ctx, "APK-to-SBOM MVP | emitted Maven version confirmation rate, not full dependency recall", 56, 680, 900, 20, { size: 10, color: C.muted });
}

function chip(slide, ctx, label, x, y, w, color = C.teal) {
  box(slide, ctx, x, y, w, 30, "#FFFFFF", color);
  text(slide, ctx, label, x + 4, y + 6, w - 8, 18, { size: 12, color, bold: true, align: "center" });
}

function metric(slide, ctx, value, label, x, y, w, h, color) {
  box(slide, ctx, x, y, w, h, C.panel, color);
  text(slide, ctx, value, x + 14, y + 14, w - 28, 36, { size: 28, bold: true, color });
  text(slide, ctx, label, x + 14, y + 54, w - 28, h - 62, { size: 12, color: C.muted });
}

function bullets(slide, ctx, items, x, y, w, h, opts = {}) {
  const body = items.map((item) => `- ${item}`).join("\n");
  text(slide, ctx, body, x, y, w, h, { size: opts.size ?? 16, color: opts.color ?? C.ink, insets: { left: 6, right: 6, top: 4, bottom: 4 } });
}

function table(slide, ctx, rows, x, y, w, rowH, colW, opts = {}) {
  const headerFill = opts.headerFill ?? C.dark;
  rows.forEach((row, r) => {
    let cx = x;
    const isHeader = r === 0;
    row.forEach((cell, c) => {
      const cw = colW[c] ?? (w / row.length);
      box(slide, ctx, cx, y + r * rowH, cw, rowH, isHeader ? headerFill : (r % 2 ? "#FFFFFF" : "#F9FBFD"), isHeader ? headerFill : C.line);
      text(slide, ctx, cell, cx + 8, y + r * rowH + 7, cw - 16, rowH - 12, {
        size: opts.size ?? (isHeader ? 12 : 11),
        color: isHeader ? "#FFFFFF" : C.ink,
        bold: isHeader,
        insets: { left: 2, right: 2, top: 0, bottom: 0 }
      });
      cx += cw;
    });
  });
}

function pipeline(slide, ctx, labels, x, y, w, color = C.teal) {
  const gap = 18;
  const bw = (w - gap * (labels.length - 1)) / labels.length;
  labels.forEach((label, i) => {
    const bx = x + i * (bw + gap);
    box(slide, ctx, bx, y, bw, 56, i === 0 ? color : C.panel, i === 0 ? color : C.line);
    text(slide, ctx, label, bx + 6, y + 15, bw - 12, 24, { size: 12, bold: true, color: i === 0 ? "#FFFFFF" : C.ink, align: "center" });
    if (i < labels.length - 1) text(slide, ctx, "->", bx + bw, y + 18, gap, 20, { size: 14, color: C.muted, align: "center" });
  });
}

function bar(slide, ctx, label, value, max, x, y, w, color) {
  text(slide, ctx, label, x, y - 2, 260, 22, { size: 13, bold: true, color: C.ink });
  box(slide, ctx, x + 285, y, w, 20, "#E8EDF4", "#E8EDF4");
  const fillW = Math.max(2, Math.round((value / max) * w));
  ctx.addShape(slide, { x: x + 285, y, w: fillW, h: 20, fill: color, line: ctx.line("#00000000", 0) });
  text(slide, ctx, `${value}/${max}`, x + 300 + w, y - 2, 90, 22, { size: 13, bold: true, color });
}

function slide01(presentation, ctx) {
  const slide = presentation.slides.add();
  slide.background.fill = C.dark;
  ctx.addShape(slide, { x: 0, y: 0, w: 1280, h: 720, fill: C.dark, line: ctx.line("#00000000", 0) });
  text(slide, ctx, "Evidence-Based SBOM Recovery", 70, 88, 760, 58, { size: 37, bold: true, color: "#FFFFFF", face: ctx.fonts.title });
  text(slide, ctx, "from Compiled Android APKs", 70, 145, 720, 48, { size: 32, bold: true, color: "#BFEFE8", face: ctx.fonts.title });
  text(slide, ctx, "Hybrid static library version detection and vulnerability lookup for APK-only analysis", 72, 214, 770, 52, { size: 18, color: "#D6DEE8" });
  pipeline(slide, ctx, ["APK", "Evidence", "Maven candidates", "CycloneDX", "OSV"], 76, 330, 780, C.teal);
  metric(slide, ctx, "137/173", "source-validated emitted Maven versions confirmed", 930, 92, 245, 116, C.teal);
  metric(slide, ctx, "35/35", "controlled expected versions confirmed", 930, 238, 245, 116, C.blue);
  metric(slide, ctx, "12", "source-validated real APKs", 930, 384, 245, 116, C.amber);
  text(slide, ctx, "PFE Defense Deck", 72, 640, 340, 28, { size: 15, color: "#AAB7C7", bold: true });
  note(slide, "This project starts from a realistic audit situation: we may only have an APK, not the source or Gradle files. The goal is to recover third-party library and version evidence, generate CycloneDX SBOMs, and connect them to vulnerability lookup.");
  return slide;
}

function slide02(presentation, ctx) {
  const slide = presentation.slides.add();
  header(slide, ctx, "Android APKs hide the dependency evidence SBOM tools usually need", "Problem", 2);
  box(slide, ctx, 72, 170, 500, 340, "#FFFFFF", C.line);
  box(slide, ctx, 708, 170, 500, 340, "#FFFFFF", C.line);
  text(slide, ctx, "Source project", 92, 194, 240, 32, { size: 24, bold: true, color: C.green });
  bullets(slide, ctx, ["Gradle files and version catalogs", "Dependency metadata visible", "Package coordinates explicit", "Source-based SBOM tools work well"], 92, 250, 420, 170, { size: 17 });
  text(slide, ctx, "Compiled APK", 728, 194, 240, 32, { size: 24, bold: true, color: C.red });
  bullets(slide, ctx, ["DEX bytecode mixed together", "Maven versions usually absent", "R8 can rename, shrink, inline", "Native files need separate handling"], 728, 250, 420, 170, { size: 17 });
  text(slide, ctx, "Normal SBOM input", 142, 456, 280, 28, { size: 16, bold: true, color: C.green, align: "center" });
  text(slide, ctx, "Reverse-SBOM input", 792, 456, 280, 28, { size: 16, bold: true, color: C.red, align: "center" });
  text(slide, ctx, "The MVP must infer component identity and version from static APK evidence.", 230, 558, 820, 42, { size: 22, bold: true, color: C.ink, align: "center" });
  footer(slide, ctx);
  note(slide, "Source SBOM tools are still useful when source metadata exists. The different problem here is APK-only analysis, where library versions must be inferred from compiled evidence.");
  return slide;
}

function slide03(presentation, ctx) {
  const slide = presentation.slides.add();
  header(slide, ctx, "The state of the art supports hybrid matching, not perfect claims", "Research gap", 3);
  table(slide, ctx, [
    ["Lesson", "Evidence from state of the art", "MVP response"],
    ["Package names are fragile", "LibScout, LibRadar, Systematic Assessment", "Use as weak evidence, not sole proof"],
    ["Graph/opcode features help", "LibPecker, LibID, LibScan, ATVHunter, SAD", "Fuse structural and bytecode signals"],
    ["R8 changes bytecode", "LibHunter, LibAttention, ObfDetector", "Evaluate by APK family and confidence"],
    ["Exact versions are harder", "SAD, TPL-Benchmark, LibMD", "Separate identity and version confidence"],
    ["SBOM output is rare", "LibMD, CycloneDX, PURL, OSV", "Emit standard SBOM plus evidence"]
  ], 72, 170, 1136, 62, [300, 430, 406], { size: 12 });
  text(slide, ctx, "Traceability source: docs/thesis/PAPER_TO_IMPLEMENTATION_TRACEABILITY.md", 76, 596, 760, 24, { size: 12, color: C.muted });
  footer(slide, ctx);
  note(slide, "The literature does not justify claiming perfect matching. It justifies combining multiple signals and reporting limits honestly. The traceability matrix maps each MVP feature to papers/tools and experiments.");
  return slide;
}

function slide04(presentation, ctx) {
  const slide = presentation.slides.add();
  header(slide, ctx, "The MVP gives strong claims when evidence is strong, and uncertainty when it is not", "Project goal", 4);
  box(slide, ctx, 86, 180, 350, 350, C.panel, C.line);
  text(slide, ctx, "Input", 112, 206, 140, 28, { size: 22, bold: true, color: C.blue });
  text(slide, ctx, "compiled APK", 112, 250, 240, 36, { size: 28, bold: true });
  text(slide, ctx, "DEX + manifest + resources + native files", 112, 306, 250, 66, { size: 17, color: C.muted });
  text(slide, ctx, "No Gradle dependency tree required at runtime", 112, 410, 260, 52, { size: 17, color: C.muted });
  box(slide, ctx, 470, 180, 724, 350, "#FFFFFF", C.teal);
  text(slide, ctx, "Output", 496, 206, 140, 28, { size: 22, bold: true, color: C.teal });
  const outs = ["Detected Maven components", "Version confidence", "Ambiguous version sets", "CycloneDX SBOM", "OSV vulnerability results"];
  outs.forEach((o, i) => {
    chip(slide, ctx, o, 510 + (i % 2) * 320, 260 + Math.floor(i / 2) * 72, 270, [C.teal, C.blue, C.amber, C.green, C.purple][i]);
  });
  text(slide, ctx, "Core policy: do not hide hard APKs and do not force unsupported exact versions.", 160, 578, 960, 38, { size: 22, bold: true, align: "center" });
  footer(slide, ctx);
  note(slide, "The goal is a useful security artifact: an SBOM with evidence, confidence, and limitations. Ambiguity is not hidden; it is represented as data.");
  return slide;
}

function slide05(presentation, ctx) {
  const slide = presentation.slides.add();
  header(slide, ctx, "The MVP is an end-to-end static APK-to-SBOM pipeline", "Architecture", 5);
  const labels = ["APK extraction", "DEX analysis", "Reference DB", "Hybrid matching", "Confidence", "CycloneDX", "OSV report"];
  pipeline(slide, ctx, labels, 68, 190, 1140, C.blue);
  const details = [
    ["APK extraction", "standard/nonstandard DEX\nmanifest metadata\nnative .so hashes"],
    ["DEX analysis", "classes, methods\nopcodes, literals\nclass dependency graph"],
    ["Reference DB", "Maven JAR/AAR\nD8 conversion\nSQLite features"],
    ["Decision layer", "identity status\nversion status\nambiguity set"],
  ];
  details.forEach((d, i) => {
    const x = 78 + i * 292;
    box(slide, ctx, x, 320, 250, 170, "#FFFFFF", [C.blue, C.teal, C.amber, C.green][i]);
    text(slide, ctx, d[0], x + 16, 342, 210, 26, { size: 17, bold: true, color: [C.blue, C.teal, C.amber, C.green][i] });
    text(slide, ctx, d[1], x + 16, 386, 210, 82, { size: 15, color: C.ink });
  });
  text(slide, ctx, "Implementation map: src/apk_sbom/* + scripts/build_* evaluation generators", 120, 574, 1040, 28, { size: 16, bold: true, align: "center", color: C.muted });
  footer(slide, ctx);
  note(slide, "The architecture carries static evidence from APK extraction all the way to CycloneDX and OSV. This is more than detecting a library name; it is a traceable SBOM workflow.");
  return slide;
}

function slide06(presentation, ctx) {
  const slide = presentation.slides.add();
  header(slide, ctx, "The matcher combines complementary evidence instead of trusting one fragile signal", "Evidence signals", 6);
  table(slide, ctx, [
    ["Signal", "Purpose", "Status"],
    ["Package/class/method overlap", "Candidate generation and identity", "core"],
    ["Opcode histograms", "Bytecode similarity", "core"],
    ["Class dependency graph", "Structural evidence", "core"],
    ["Literals/version-unique evidence", "Version tie-breaking", "core"],
    ["Maven POM metadata", "Conservative dependency coherence", "guarded"],
    ["API refs / opcode tri-grams", "Independent experimental signals", "disabled globally"]
  ], 72, 166, 1136, 58, [340, 520, 276], { size: 12, headerFill: C.blue });
  text(slide, ctx, "Negative experiments are evidence too: API weight changed no metrics; opcode tri-grams regressed controls.", 110, 594, 1000, 28, { size: 15, color: C.red, bold: true, align: "center" });
  footer(slide, ctx);
  note(slide, "Each signal contributes a different kind of evidence. Optional signals were not promoted globally because the regression matrix did not support them.");
  return slide;
}

function slide07(presentation, ctx) {
  const slide = presentation.slides.add();
  header(slide, ctx, "Identity confidence and version confidence are intentionally separate", "Confidence and ambiguity", 7);
  const xs = [90, 464, 838];
  const titles = ["Library identity", "Version confidence", "Ambiguous versions"];
  const subs = ["Is this component present?", "Is this exact version supported?", "Which nearby versions are plausible?"];
  const colors = [C.blue, C.teal, C.amber];
  xs.forEach((x, i) => {
    box(slide, ctx, x, 188, 300, 260, "#FFFFFF", colors[i]);
    text(slide, ctx, titles[i], x + 18, 214, 250, 30, { size: 21, bold: true, color: colors[i] });
    text(slide, ctx, subs[i], x + 18, 274, 248, 72, { size: 18, color: C.ink });
    text(slide, ctx, i === 0 ? "identity-confidence\nidentity-status" : i === 1 ? "version-confidence\nversion-status" : "ambiguous-versions\nversion-ambiguity", x + 18, 365, 246, 52, { size: 14, color: C.muted, mono: true });
  });
  text(slide, ctx, "Why it matters: a real library with an uncertain version should not create a false confirmed CVE result.", 130, 532, 1020, 48, { size: 22, bold: true, color: C.ink, align: "center" });
  footer(slide, ctx);
  note(slide, "A component can be present even when the exact version is uncertain. The report and SBOM now preserve this distinction and export ambiguous versions.");
  return slide;
}

function slide08(presentation, ctx) {
  const slide = presentation.slides.add();
  header(slide, ctx, "Evaluation is by APK family, not by hiding hard cases", "Evaluation design", 8);
  const rows = [
    ["Controlled APKs", "30", "known ground truth"],
    ["Clean source-validated real", "3", "strong exact-version evidence"],
    ["Partial source-validated real", "9", "realistic hard cases"],
    ["Source-linked blocked", "1", "proof exists, metric excluded"],
    ["Limitation cases", "3", "native/hidden-code boundaries"]
  ];
  rows.forEach((r, i) => {
    const y = 170 + i * 78;
    const color = [C.green, C.teal, C.amber, C.red, C.purple][i];
    box(slide, ctx, 112, y, 940, 54, "#FFFFFF", C.line);
    ctx.addShape(slide, { x: 112, y, w: 10, h: 54, fill: color, line: ctx.line("#00000000", 0) });
    text(slide, ctx, r[0], 144, y + 14, 330, 26, { size: 18, bold: true, color: C.ink });
    text(slide, ctx, r[1], 520, y + 9, 70, 32, { size: 25, bold: true, color });
    text(slide, ctx, r[2], 638, y + 15, 330, 24, { size: 15, color: C.muted });
  });
  text(slide, ctx, "Blocked and boundary cases are visible but excluded from accuracy metrics.", 160, 592, 930, 28, { size: 18, bold: true, align: "center", color: C.ink });
  footer(slide, ctx);
  note(slide, "This split is a key research contribution. A single global score hides why the tool succeeds or fails across APK families.");
  return slide;
}

function slide09(presentation, ctx) {
  const slide = presentation.slides.add();
  header(slide, ctx, "The MVP is exact on controlled and clean cases, useful but partial on harder APKs", "Main results", 9);
  bar(slide, ctx, "Controlled APKs", 35, 35, 120, 190, 560, C.green);
  bar(slide, ctx, "Clean real APKs", 43, 43, 120, 266, 560, C.teal);
  bar(slide, ctx, "Partial real APKs", 94, 130, 120, 342, 560, C.amber);
  bar(slide, ctx, "All source-validated real", 137, 173, 120, 418, 560, C.blue);
  box(slide, ctx, 930, 174, 230, 250, "#FFFFFF", C.blue);
  text(slide, ctx, "79.2%", 960, 210, 170, 42, { size: 36, bold: true, color: C.blue, align: "center" });
  text(slide, ctx, "overall emitted Maven version confirmation rate", 958, 272, 175, 76, { size: 16, color: C.ink, align: "center" });
  text(slide, ctx, "Not full dependency recall", 954, 372, 185, 26, { size: 13, color: C.red, bold: true, align: "center" });
  text(slide, ctx, "Always report clean and partial rows separately.", 150, 570, 980, 30, { size: 19, bold: true, align: "center" });
  footer(slide, ctx);
  note(slide, "Use the phrase emitted Maven version confirmation rate. Do not call it full dependency recall. The overall number is useful only with the clean and partial split.");
  return slide;
}

function slide10(presentation, ctx) {
  const slide = presentation.slides.add();
  header(slide, ctx, "Mixed results are evidence about APK types, not total failure", "Interpretation", 10);
  table(slide, ctx, [
    ["Case family", "Interpretation"],
    ["F-Droid, OpenTracks, Tusky", "Clean source-validated evidence; Tusky is clean but sparse"],
    ["NewPipe, AntennaPod, KDE, Wikipedia, Conversations, Aegis, FairEmail, Nextcloud", "Useful partial evidence with AndroidX/Kotlin and version-band ambiguity"],
    ["Markor", "Older-dependency drift; app-specific calibration can regress others"],
    ["K-9", "Source-linked blocked; not counted until dependency tree exists"],
    ["Organic Maps, Termux, hidden DEX", "Boundary evidence; native/hash-only and hidden-code limitations"]
  ], 70, 170, 1140, 68, [430, 710], { size: 12, headerFill: C.teal });
  text(slide, ctx, "This is why the thesis reports APK families instead of a single polished score.", 132, 610, 1010, 28, { size: 18, bold: true, align: "center" });
  footer(slide, ctx);
  note(slide, "If we only showed clean cases, the tool would look stronger but the thesis would be weaker. Partial cases show the hard families and guide future work.");
  return slide;
}

function slide11(presentation, ctx) {
  const slide = presentation.slides.add();
  header(slide, ctx, "The SBOM workflow is standard, and vulnerability output is confidence-aware", "SBOM and CVE demo", 11);
  box(slide, ctx, 92, 184, 500, 292, "#FFFFFF", C.green);
  text(slide, ctx, "Clean real APK demo", 118, 214, 280, 30, { size: 22, bold: true, color: C.green });
  text(slide, ctx, "F-Droid report", 118, 270, 240, 26, { size: 18, bold: true });
  bullets(slide, ctx, ["23/23 source-confirmed emitted Maven versions", "CycloneDX JSON with Maven PURLs", "OSV returns 0 vulnerabilities"], 118, 316, 400, 102, { size: 15 });
  box(slide, ctx, 684, 184, 500, 292, "#FFFFFF", C.red);
  text(slide, ctx, "Positive vulnerability demo", 710, 214, 320, 30, { size: 22, bold: true, color: C.red });
  text(slide, ctx, "Jackson Databind fixture", 710, 270, 320, 26, { size: 18, bold: true });
  bullets(slide, ctx, ["com.fasterxml.jackson.core:jackson-databind@2.9.10.8", "3 confirmed HIGH OSV advisories", "CVE-2020-36518, CVE-2022-42003, CVE-2022-42004"], 710, 316, 420, 112, { size: 15 });
  text(slide, ctx, "Confidence rule: high-confidence exact versions can support confirmed findings; ambiguous versions stay potential.", 120, 562, 1040, 44, { size: 18, bold: true, align: "center" });
  footer(slide, ctx);
  note(slide, "The SBOM is CycloneDX with PURLs and evidence properties. Vulnerability results are interpreted through version confidence, which reduces false confirmed CVE claims.");
  return slide;
}

function slide12(presentation, ctx) {
  const slide = presentation.slides.add();
  header(slide, ctx, "The MVP is credible because it exposes scope boundaries and next improvements", "Limitations and next work", 12);
  box(slide, ctx, 74, 178, 540, 356, "#FFFFFF", C.red);
  text(slide, ctx, "Current limitations", 100, 206, 260, 30, { size: 22, bold: true, color: C.red });
  bullets(slide, ctx, ["reference DB coverage affects exact versions", "adjacent AndroidX/Kotlin versions can tie", "native .so files are hash-only", "hidden DEX/dynamic loading is risk-labeled", "K-9 remains source-linked blocked", "scanner validation blocked by missing tools"], 100, 258, 420, 210, { size: 15 });
  box(slide, ctx, 666, 178, 540, 356, "#FFFFFF", C.blue);
  text(slide, ctx, "Next work", 692, 206, 220, 30, { size: 22, bold: true, color: C.blue });
  bullets(slide, ctx, ["scale source-validated real APKs", "add framework families", "investigate scoped per-coordinate rerankers", "explore stronger multi-scale graph fusion", "add Trivy/Grype validation when available"], 692, 258, 420, 188, { size: 15 });
  text(slide, ctx, "Closing: useful, measurable, and transparent beats a perfect-looking score that hides difficult APKs.", 128, 588, 1024, 34, { size: 20, bold: true, align: "center", color: C.ink });
  footer(slide, ctx);
  note(slide, "The conclusion is not that the MVP is perfect. It is that the tool is useful, measurable, and honest about uncertainty, with clear next improvements.");
  return slide;
}

const slides = [slide01, slide02, slide03, slide04, slide05, slide06, slide07, slide08, slide09, slide10, slide11, slide12];

export async function drawSlide(presentation, ctx, number) {
  return slides[number - 1](presentation, ctx);
}
