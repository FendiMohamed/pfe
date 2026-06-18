const C = {
  night: "#0B1220",
  night2: "#111B2E",
  paper: "#F4F7FB",
  white: "#FFFFFF",
  ink: "#101827",
  muted: "#5E6B7D",
  line: "#D8E0EA",
  lineDark: "#26344D",
  blue: "#4F7CFF",
  cyan: "#24BFAE",
  lime: "#9DCC3B",
  coral: "#F06464",
  gold: "#E8AA3B",
  violet: "#806FE8",
  paleBlue: "#EAF0FF",
  paleCyan: "#E4F7F4",
  paleLime: "#EFF7DD",
  paleCoral: "#FCE8E8",
  paleGold: "#FBF1DC",
};

function note(slide, value) {
  if (slide.speakerNotes?.setText) slide.speakerNotes.setText(value);
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
    insets: opts.insets ?? { left: 4, right: 4, top: 2, bottom: 2 },
    name: opts.name,
  });
}

function shape(slide, ctx, geometry, x, y, w, h, fill, line = fill, name) {
  return ctx.addShape(slide, {
    geometry,
    x, y, w, h,
    fill,
    line: ctx.line(line, line === "#00000000" ? 0 : 1),
    name,
  });
}

function box(slide, ctx, x, y, w, h, fill = C.white, line = C.line, name) {
  return shape(slide, ctx, "roundRect", x, y, w, h, fill, line, name);
}

function rect(slide, ctx, x, y, w, h, fill, line = fill, name) {
  return shape(slide, ctx, "rect", x, y, w, h, fill, line, name);
}

function circle(slide, ctx, x, y, d, fill, line = fill, name) {
  return shape(slide, ctx, "ellipse", x, y, d, d, fill, line, name);
}

function rule(slide, ctx, x, y, w, h = 2, fill = C.line) {
  return rect(slide, ctx, x, y, w, h, fill, "#00000000", "rule");
}

function page(slide, ctx, title, kicker, number, opts = {}) {
  const dark = opts.dark ?? false;
  slide.background.fill = dark ? C.night : C.paper;
  if (dark) {
    rect(slide, ctx, 0, 0, 1280, 720, C.night, "#00000000");
    rect(slide, ctx, 0, 0, 14, 720, opts.accent ?? C.cyan, "#00000000");
  }
  text(slide, ctx, kicker.toUpperCase(), 66, 34, 760, 22, {
    size: 12,
    color: dark ? (opts.accent ?? C.cyan) : (opts.accent ?? C.blue),
    bold: true,
  });
  text(slide, ctx, title, 66, 64, 1040, 56, {
    size: 31,
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

function footer(slide, ctx, opts = {}) {
  const dark = opts.dark ?? false;
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

function label(slide, ctx, value, x, y, w, color, opts = {}) {
  box(slide, ctx, x, y, w, 28, opts.fill ?? C.white, color);
  text(slide, ctx, value, x + 7, y + 6, w - 14, 16, {
    size: 11,
    color,
    bold: true,
    align: opts.align ?? "center",
  });
}

function bigMetric(slide, ctx, value, caption, x, y, w, color, opts = {}) {
  const dark = opts.dark ?? false;
  text(slide, ctx, value, x, y, w, 54, {
    size: opts.size ?? 42,
    color,
    bold: true,
    face: ctx.fonts.title,
  });
  text(slide, ctx, caption, x, y + 60, w, 48, {
    size: 13,
    color: dark ? "#B8C3D4" : C.muted,
  });
}

function bullets(slide, ctx, items, x, y, w, h, opts = {}) {
  const body = items.map((item) => `- ${item}`).join("\n");
  text(slide, ctx, body, x, y, w, h, {
    size: opts.size ?? 15,
    color: opts.color ?? C.ink,
    insets: { left: 2, right: 2, top: 2, bottom: 2 },
  });
}

function arrow(slide, ctx, x, y, w, color, labelValue = "") {
  rule(slide, ctx, x, y + 11, w - 16, 2, color);
  shape(slide, ctx, "chevron", x + w - 24, y + 2, 24, 20, color, "#00000000");
  if (labelValue) {
    text(slide, ctx, labelValue, x, y - 18, w, 16, {
      size: 10,
      color,
      bold: true,
      align: "center",
    });
  }
}

function progress(slide, ctx, labelValue, numerator, denominator, x, y, w, color, opts = {}) {
  const ratio = denominator ? numerator / denominator : 0;
  text(slide, ctx, labelValue, x, y, 250, 22, {
    size: 13,
    color: opts.dark ? C.white : C.ink,
    bold: true,
  });
  rect(slide, ctx, x + 265, y + 2, w, 15, opts.dark ? "#243149" : "#DFE6EF", "#00000000");
  rect(slide, ctx, x + 265, y + 2, Math.max(3, w * ratio), 15, color, "#00000000");
  text(slide, ctx, `${numerator}/${denominator}`, x + 280 + w, y - 2, 120, 22, {
    size: 13,
    color,
    bold: true,
  });
}

function miniWindow(slide, ctx, x, y, w, h, titleValue, accent) {
  box(slide, ctx, x, y, w, h, C.white, C.line);
  rect(slide, ctx, x, y, w, 34, C.night2, "#00000000");
  circle(slide, ctx, x + 14, y + 12, 9, C.coral, "#00000000");
  circle(slide, ctx, x + 30, y + 12, 9, C.gold, "#00000000");
  circle(slide, ctx, x + 46, y + 12, 9, C.lime, "#00000000");
  text(slide, ctx, titleValue, x + 68, y + 9, w - 84, 18, {
    size: 11,
    color: C.white,
    bold: true,
  });
  rect(slide, ctx, x + 18, y + 52, 6, h - 72, accent, "#00000000");
}

function slide01(presentation, ctx) {
  const slide = presentation.slides.add();
  slide.background.fill = C.night;
  rect(slide, ctx, 0, 0, 1280, 720, C.night, "#00000000");
  rect(slide, ctx, 0, 0, 18, 720, C.cyan, "#00000000");
  text(slide, ctx, "PFE DEFENSE  /  JUNE 2026", 72, 52, 430, 22, { size: 12, color: C.cyan, bold: true });
  text(slide, ctx, "Evidence-Based", 72, 114, 650, 62, { size: 48, color: C.white, bold: true, face: ctx.fonts.title });
  text(slide, ctx, "SBOM Recovery", 72, 172, 650, 62, { size: 48, color: C.white, bold: true, face: ctx.fonts.title });
  text(slide, ctx, "from compiled Android APKs", 74, 245, 600, 40, { size: 24, color: "#A9B6C9", bold: true });
  text(slide, ctx, "Static evidence fusion, CycloneDX output, confidence-aware CVE mapping, and guarded AI assistance.", 74, 310, 580, 70, { size: 17, color: "#C6D0DE" });
  const nodes = [
    ["APK", 732, 110, C.blue],
    ["DEX", 930, 86, C.violet],
    ["MATCH", 1034, 232, C.cyan],
    ["SBOM", 914, 382, C.lime],
    ["CVE", 710, 358, C.coral],
  ];
  nodes.forEach(([value, x, y, color], index) => {
    const d = index === 2 ? 126 : 96;
    circle(slide, ctx, x, y, d, index === 2 ? color : C.night2, color);
    text(slide, ctx, value, x, y + d / 2 - 12, d, 24, { size: index === 2 ? 19 : 15, color: C.white, bold: true, align: "center" });
  });
  rule(slide, ctx, 820, 154, 122, 2, C.blue);
  rule(slide, ctx, 1008, 167, 80, 2, C.violet);
  rule(slide, ctx, 1028, 337, 88, 2, C.cyan);
  rule(slide, ctx, 802, 412, 124, 2, C.lime);
  rule(slide, ctx, 758, 287, 2, 78, C.coral);
  rect(slide, ctx, 70, 494, 1100, 1, C.lineDark, "#00000000");
  bigMetric(slide, ctx, "927 / 1837", "normal source-validated emitted versions confirmed", 74, 524, 300, C.cyan, { dark: true, size: 32 });
  bigMetric(slide, ctx, "84 / 84", "controlled expected Maven versions", 438, 524, 220, C.lime, { dark: true, size: 32 });
  bigMetric(slide, ctx, "6772 / 6772", "source-known v2 lane, not APK-only accuracy", 744, 524, 350, C.gold, { dark: true, size: 32 });
  note(slide, "Open with the problem, not the score. Say: this project starts from a compiled APK, where dependency metadata is absent. The tool recovers evidence, emits CycloneDX, maps vulnerabilities, and keeps uncertainty visible. Mention the three headline numbers only after stating that the v2 lane is source-known and not APK-only accuracy.");
  return slide;
}

function slide02(presentation, ctx) {
  const slide = presentation.slides.add();
  page(slide, ctx, "Compilation removes the dependency metadata SBOM tools expect", "The problem", 2, { accent: C.coral });
  box(slide, ctx, 70, 158, 430, 400, C.white, C.line);
  label(slide, ctx, "SOURCE PROJECT", 94, 182, 150, C.lime, { fill: C.paleLime });
  text(slide, ctx, "Dependencies are explicit", 94, 232, 340, 34, { size: 25, bold: true });
  [["build.gradle", "coordinates + versions"], ["version catalog", "shared dependency policy"], ["lock / tree", "resolved transitives"]].forEach((row, i) => {
    rect(slide, ctx, 96, 294 + i * 62, 10, 42, C.lime, "#00000000");
    text(slide, ctx, row[0], 124, 292 + i * 62, 150, 22, { size: 14, bold: true, mono: true });
    text(slide, ctx, row[1], 124, 314 + i * 62, 250, 20, { size: 12, color: C.muted });
  });
  text(slide, ctx, "Normal source-based SBOM", 94, 500, 330, 28, { size: 16, color: C.lime, bold: true });
  arrow(slide, ctx, 518, 320, 164, C.coral, "compile + R8");
  text(slide, ctx, "metadata lost", 532, 370, 130, 24, { size: 13, color: C.coral, bold: true, align: "center" });
  box(slide, ctx, 700, 158, 500, 400, C.night2, C.night2);
  label(slide, ctx, "COMPILED APK", 724, 182, 142, C.coral, { fill: C.night });
  text(slide, ctx, "Evidence is indirect", 724, 232, 360, 34, { size: 25, color: C.white, bold: true });
  [["DEX bytecode", "classes mixed and optimized", C.blue], ["R8 transforms", "rename, shrink, inline", C.coral], ["Native files", "hash evidence only", C.gold], ["No Maven version", "must be inferred", C.cyan]].forEach((row, i) => {
    circle(slide, ctx, 726, 298 + i * 52, 18, row[2], "#00000000");
    text(slide, ctx, row[0], 758, 294 + i * 52, 150, 22, { size: 14, color: C.white, bold: true });
    text(slide, ctx, row[1], 914, 294 + i * 52, 230, 22, { size: 13, color: "#AEBACB" });
  });
  text(slide, ctx, "Reverse-SBOM problem", 724, 500, 340, 28, { size: 16, color: C.cyan, bold: true });
  text(slide, ctx, "The MVP must reconstruct identity and version from what survives compilation.", 166, 606, 950, 38, { size: 21, bold: true, align: "center" });
  footer(slide, ctx);
  note(slide, "Explain why normal SBOM tools are not enough: they consume source metadata. In an APK, Maven coordinates and exact versions are usually absent and R8 can transform the remaining bytecode. The research problem is evidence reconstruction, not manifest parsing.");
  return slide;
}

function slide03(presentation, ctx) {
  const slide = presentation.slides.add();
  page(slide, ctx, "The literature converges on hybrid evidence, but not perfect version recovery", "Research positioning", 3, { dark: true, accent: C.violet });
  [
    { x: 72, color: C.blue, year: "GEN 1", title: "Signatures", items: ["packages", "class hashes", "profiles"], tools: "LibScout  LibRadar" },
    { x: 404, color: C.cyan, year: "GEN 2", title: "Structure", items: ["graphs", "opcodes", "fuzzy similarity"], tools: "LibPecker  SAD  ATVHunter" },
    { x: 736, color: C.violet, year: "GEN 3", title: "Learned models", items: ["token models", "R8 resilience", "risk classification"], tools: "LibAttention  ObfDetector" },
  ].forEach((lane) => {
    box(slide, ctx, lane.x, 174, 288, 286, C.night2, C.lineDark);
    label(slide, ctx, lane.year, lane.x + 20, 194, 88, lane.color, { fill: C.night });
    text(slide, ctx, lane.title, lane.x + 20, 242, 220, 30, { size: 23, color: C.white, bold: true });
    lane.items.forEach((item, i) => {
      circle(slide, ctx, lane.x + 22, 302 + i * 42, 12, lane.color, "#00000000");
      text(slide, ctx, item, lane.x + 48, 296 + i * 42, 200, 24, { size: 14, color: "#C5CFDD" });
    });
    rule(slide, ctx, lane.x + 20, 414, 248, 1, C.lineDark);
    text(slide, ctx, lane.tools, lane.x + 20, 430, 248, 20, { size: 11, color: lane.color, bold: true });
  });
  box(slide, ctx, 1056, 174, 154, 286, C.white, C.white);
  text(slide, ctx, "GAP", 1080, 196, 106, 22, { size: 12, color: C.coral, bold: true, align: "center" });
  text(slide, ctx, "Exact\nversions\nunder R8", 1076, 248, 114, 96, { size: 21, color: C.ink, bold: true, align: "center" });
  text(slide, ctx, "+ standard\nSBOM output", 1080, 368, 106, 56, { size: 14, color: C.muted, align: "center" });
  rect(slide, ctx, 72, 510, 1138, 86, C.violet, "#00000000");
  text(slide, ctx, "Project response", 96, 532, 190, 28, { size: 17, color: C.white, bold: true });
  text(slide, ctx, "multi-scale evidence  +  separate identity/version confidence  +  CycloneDX  +  transparent limits", 292, 530, 860, 32, { size: 18, color: C.white, bold: true });
  footer(slide, ctx, { dark: true });
  note(slide, "Do not present the papers as a list. Present the progression: signatures, structure, then learned models. The unresolved gap is exact version recovery under optimization together with standard SBOM and vulnerability output. Our design combines proven signals and reports uncertainty.");
  return slide;
}

function slide04(presentation, ctx) {
  const slide = presentation.slides.add();
  page(slide, ctx, "The objective is a useful security artifact, not forced certainty", "Project objective", 4, { accent: C.cyan });
  box(slide, ctx, 76, 176, 236, 330, C.night2, C.night2);
  text(slide, ctx, "INPUT", 98, 198, 120, 20, { size: 11, color: C.cyan, bold: true });
  text(slide, ctx, "APK", 98, 246, 170, 56, { size: 42, color: C.white, bold: true, face: ctx.fonts.title });
  rect(slide, ctx, 98, 330, 104, 18, C.blue, "#00000000");
  rect(slide, ctx, 98, 358, 142, 18, C.violet, "#00000000");
  rect(slide, ctx, 98, 386, 82, 18, C.cyan, "#00000000");
  text(slide, ctx, "DEX  manifest\nresources  native", 98, 432, 150, 52, { size: 13, color: "#B7C2D1", mono: true });
  arrow(slide, ctx, 324, 328, 144, C.blue, "static evidence");
  box(slide, ctx, 480, 176, 304, 330, C.white, C.blue);
  text(slide, ctx, "EVIDENCE ENGINE", 506, 198, 220, 20, { size: 11, color: C.blue, bold: true });
  text(slide, ctx, "Identity", 506, 248, 126, 28, { size: 22, bold: true });
  text(slide, ctx, "Version", 638, 248, 112, 28, { size: 22, bold: true });
  [["class / method", 88, C.blue], ["opcode / graph", 74, C.cyan], ["literal / unique", 52, C.gold]].forEach((row, i) => {
    const y = 310 + i * 46;
    text(slide, ctx, row[0], 506, y, 126, 22, { size: 12, color: C.ink, bold: true });
    rect(slide, ctx, 646, y + 3, 82, 14, "#DFE6EF", "#00000000");
    rect(slide, ctx, 646, y + 3, 82 * row[1] / 100, 14, row[2], "#00000000");
    text(slide, ctx, `${row[1]}/100`, 726, y - 1, 56, 22, { size: 10, color: row[2], bold: true, align: "right" });
  });
  text(slide, ctx, "confidence + ambiguity policy", 506, 454, 238, 24, { size: 13, color: C.muted, bold: true });
  arrow(slide, ctx, 804, 340, 116, C.cyan, "evidence");
  [["CycloneDX", "standard SBOM", C.blue, C.paleBlue], ["Confidence", "identity + version", C.cyan, C.paleCyan], ["Ambiguity", "near versions", C.gold, C.paleGold], ["OSV", "CVE evidence", C.coral, C.paleCoral]].forEach((item, i) => {
    const x = 934 + (i % 2) * 142;
    const y = 190 + Math.floor(i / 2) * 150;
    box(slide, ctx, x, y, 126, 126, item[3], item[2]);
    text(slide, ctx, item[0], x + 10, y + 22, 106, 26, { size: 17, color: item[2], bold: true, align: "center" });
    text(slide, ctx, item[1], x + 10, y + 70, 106, 34, { size: 12, color: C.ink, align: "center" });
  });
  rect(slide, ctx, 142, 562, 996, 62, C.ink, "#00000000");
  text(slide, ctx, "Policy: strong evidence produces strong claims; weak evidence stays uncertain or report-only.", 174, 581, 932, 28, { size: 18, color: C.white, bold: true, align: "center" });
  footer(slide, ctx);
  note(slide, "The output is not only a list of library names. It is a CycloneDX SBOM with identity confidence, version confidence, ambiguous alternatives, and confidence-aware OSV results. Ambiguity is preserved because a false exact version can create a false confirmed CVE.");
  return slide;
}

function slide05(presentation, ctx) {
  const slide = presentation.slides.add();
  page(slide, ctx, "The MVP is an end-to-end static APK-to-SBOM system", "Architecture", 5, { dark: true, accent: C.blue });
  [["01", "Extract", "DEX\nmanifest\nnative", C.blue], ["02", "Fingerprint", "classes\nmethods\nopcodes", C.violet], ["03", "Retrieve", "Maven\ncandidates", C.cyan], ["04", "Match", "multi-scale\nscoring", C.lime], ["05", "Decide", "confidence\nambiguity", C.gold], ["06", "Export", "CycloneDX\nOSV report", C.coral]].forEach((stage, i) => {
    const x = 64 + i * 194;
    circle(slide, ctx, x + 56, 180, 54, stage[3], "#00000000");
    text(slide, ctx, stage[0], x + 56, 197, 54, 20, { size: 13, color: C.night, bold: true, align: "center" });
    if (i < 5) arrow(slide, ctx, x + 118, 196, 70, C.lineDark);
    box(slide, ctx, x, 258, 170, 178, C.night2, C.lineDark);
    text(slide, ctx, stage[1], x + 18, 280, 134, 28, { size: 20, color: C.white, bold: true });
    text(slide, ctx, stage[2], x + 18, 330, 134, 68, { size: 15, color: "#ADB9CB", mono: true });
    rect(slide, ctx, x, 426, 170, 10, stage[3], "#00000000");
  });
  box(slide, ctx, 260, 500, 760, 100, C.white, C.white);
  text(slide, ctx, "Reference DB", 286, 522, 170, 26, { size: 19, color: C.blue, bold: true });
  text(slide, ctx, "Maven JAR/AAR  ->  D8/DEX conversion  ->  SQLite structural features", 470, 522, 520, 26, { size: 15, color: C.ink, bold: true });
  text(slide, ctx, "10,517 stored coordinate-version components in the final large evaluation DB", 286, 562, 660, 22, { size: 13, color: C.muted });
  footer(slide, ctx, { dark: true });
  note(slide, "Walk left to right. The APK is extracted, DEX evidence is fingerprinted, reference candidates are retrieved, multiple signals are scored, confidence and ambiguity are decided, then CycloneDX and OSV-aware reports are generated. The reference DB is a separate reproducible pipeline built from Maven artifacts.");
  return slide;
}

function slide06(presentation, ctx) {
  const slide = presentation.slides.add();
  page(slide, ctx, "Complementary signals reduce dependence on any single fragile feature", "Matcher evidence", 6, { accent: C.violet });
  circle(slide, ctx, 500, 224, 278, C.night2, C.night2);
  circle(slide, ctx, 558, 282, 162, C.white, C.white);
  text(slide, ctx, "HYBRID", 558, 326, 162, 24, { size: 17, color: C.ink, bold: true, align: "center" });
  text(slide, ctx, "MATCH", 558, 354, 162, 30, { size: 24, color: C.blue, bold: true, align: "center" });
  [["Packages", "candidate recall", 118, 170, C.blue, C.paleBlue], ["Classes", "identity overlap", 100, 394, C.cyan, C.paleCyan], ["Methods", "API surface", 382, 522, C.lime, C.paleLime], ["Opcodes", "bytecode shape", 804, 522, C.violet, "#EEEAFE"], ["CDG", "structure", 1034, 394, C.gold, C.paleGold], ["Literals", "version clues", 1030, 170, C.coral, C.paleCoral]].forEach((signal) => {
    box(slide, ctx, signal[2], signal[3], 150, 92, signal[5], signal[4]);
    text(slide, ctx, signal[0], signal[2] + 12, signal[3] + 16, 126, 24, { size: 17, color: signal[4], bold: true, align: "center" });
    text(slide, ctx, signal[1], signal[2] + 12, signal[3] + 52, 126, 20, { size: 11, color: C.muted, align: "center" });
  });
  rule(slide, ctx, 270, 220, 260, 2, C.blue);
  rule(slide, ctx, 250, 438, 282, 2, C.cyan);
  rule(slide, ctx, 516, 504, 72, 2, C.lime);
  rule(slide, ctx, 690, 504, 114, 2, C.violet);
  rule(slide, ctx, 748, 438, 286, 2, C.gold);
  rule(slide, ctx, 748, 220, 282, 2, C.coral);
  label(slide, ctx, "CORE", 540, 622, 90, C.lime, { fill: C.paleLime });
  text(slide, ctx, "package / class / method / opcode / graph / literal", 644, 626, 480, 22, { size: 12, color: C.ink, bold: true });
  label(slide, ctx, "GUARDED", 540, 652, 90, C.gold, { fill: C.paleGold });
  text(slide, ctx, "POM coherence; API refs and tri-grams disabled globally", 644, 656, 480, 22, { size: 12, color: C.muted });
  footer(slide, ctx);
  note(slide, "Each signal answers a different question. Package and class overlap support identity; opcodes and class dependency graphs add structure; literals and version-distinctive evidence help with nearby versions. Experimental API-reference and opcode tri-gram weights were not promoted because controls did not improve.");
  return slide;
}

function slide07(presentation, ctx) {
  const slide = presentation.slides.add();
  page(slide, ctx, "Identity confidence and exact-version confidence are different decisions", "Confidence model", 7, { dark: true, accent: C.gold });
  [
    { x: 76, number: "1", title: "Identity", question: "Is this library present?", color: C.blue, rows: ["package evidence", "class/method overlap", "structural agreement"] },
    { x: 414, number: "2", title: "Version", question: "Is this exact version supported?", color: C.cyan, rows: ["version-distinctive clues", "score gap", "candidate competition"] },
    { x: 752, number: "3", title: "Ambiguity", question: "Which alternatives remain plausible?", color: C.gold, rows: ["near-tie versions", "single-reference boundary", "uncertain policy"] },
  ].forEach((column) => {
    box(slide, ctx, column.x, 174, 292, 354, C.night2, C.lineDark);
    circle(slide, ctx, column.x + 22, 198, 42, column.color, "#00000000");
    text(slide, ctx, column.number, column.x + 22, 210, 42, 18, { size: 13, color: C.night, bold: true, align: "center" });
    text(slide, ctx, column.title, column.x + 80, 198, 178, 30, { size: 23, color: C.white, bold: true });
    text(slide, ctx, column.question, column.x + 24, 258, 244, 48, { size: 17, color: column.color, bold: true });
    column.rows.forEach((row, i) => {
      rule(slide, ctx, column.x + 24, 332 + i * 48, 18, 3, column.color);
      text(slide, ctx, row, column.x + 58, 322 + i * 48, 202, 26, { size: 14, color: "#B8C3D3" });
    });
  });
  box(slide, ctx, 1072, 174, 136, 354, C.white, C.white);
  text(slide, ctx, "CVE", 1090, 208, 100, 30, { size: 23, color: C.coral, bold: true, align: "center" });
  text(slide, ctx, "Strong\nversion\nproof", 1090, 276, 100, 72, { size: 17, color: C.ink, bold: true, align: "center" });
  arrow(slide, ctx, 1096, 370, 88, C.coral);
  text(slide, ctx, "confirmed\nfinding", 1090, 412, 100, 48, { size: 15, color: C.coral, bold: true, align: "center" });
  text(slide, ctx, "A real library with an uncertain version must not become a fake confirmed vulnerability.", 154, 586, 970, 38, { size: 20, color: C.white, bold: true, align: "center" });
  footer(slide, ctx, { dark: true });
  note(slide, "This separation is central to the thesis. A library may be present even when its exact version is ambiguous. Vulnerability findings are only treated as confirmed when identity and exact-version evidence are strong; otherwise they remain potential or report-only.");
  return slide;
}

function slide08(presentation, ctx) {
  const slide = presentation.slides.add();
  page(slide, ctx, "Evaluation keeps hard APK families visible instead of collapsing them into one score", "Evaluation design", 8, { accent: C.lime });
  [["Controlled", "72 APKs", "84 expected versions", "known ground truth", C.lime], ["Clean real", "5 APKs", "47 emitted versions", "strong source proof", C.cyan], ["Partial real", "97 APKs", "1790 emitted versions", "realistic hard cases", C.gold], ["Blocked", "0 APKs", "none remaining", "proof gates completed", C.blue], ["Limitations", "4 cases", "outside exact metric", "native / hidden / protected", C.violet]].forEach((row, i) => {
    const y = 162 + i * 84;
    box(slide, ctx, 74, y, 1132, 66, C.white, C.line);
    rect(slide, ctx, 74, y, 12, 66, row[4], "#00000000");
    text(slide, ctx, row[0], 112, y + 18, 210, 28, { size: 19, color: C.ink, bold: true });
    text(slide, ctx, row[1], 364, y + 18, 140, 28, { size: 17, color: row[4], bold: true });
    text(slide, ctx, row[2], 552, y + 18, 210, 28, { size: 15, color: C.ink, bold: true });
    label(slide, ctx, row[3], 884, y + 18, 270, row[4], { fill: C.paper });
  });
  rect(slide, ctx, 176, 602, 928, 42, C.ink, "#00000000");
  text(slide, ctx, "Scientific rule: preserve the denominator, classify exclusions, and expose every remaining gap.", 198, 612, 884, 22, { size: 16, color: C.white, bold: true, align: "center" });
  footer(slide, ctx);
  note(slide, "Explain the five layers. Controlled cases test mechanics. Clean real APKs provide strong exact evidence. Partial real APKs are the difficult, realistic population. Blocked is now zero. Limitation cases remain visible but are excluded from exact Maven-version metrics.");
  return slide;
}

function slide09(presentation, ctx) {
  const slide = presentation.slides.add();
  page(slide, ctx, "The normal real-APK result and the v2 upper-bound answer different questions", "Results", 9, { dark: true, accent: C.cyan });
  box(slide, ctx, 72, 162, 664, 430, C.night2, C.lineDark);
  label(slide, ctx, "NORMAL APK / SOURCE-VALIDATED METRIC", 96, 188, 278, C.cyan, { fill: C.night });
  text(slide, ctx, "50.5%", 96, 244, 220, 64, { size: 50, color: C.cyan, bold: true, face: ctx.fonts.title });
  text(slide, ctx, "927 of 1837 emitted Maven versions confirmed", 96, 314, 500, 28, { size: 18, color: C.white, bold: true });
  progress(slide, ctx, "Controlled", 84, 84, 96, 382, 196, C.lime, { dark: true });
  progress(slide, ctx, "Clean real", 47, 47, 96, 428, 196, C.cyan, { dark: true });
  progress(slide, ctx, "Partial real", 880, 1790, 96, 474, 196, C.gold, { dark: true });
  text(slide, ctx, "Measures correctness of what the APK-only tool emitted.", 96, 536, 520, 24, { size: 13, color: "#AEBACC" });
  box(slide, ctx, 770, 162, 438, 430, C.white, C.white);
  label(slide, ctx, "SOURCE-KNOWN V2 LANE", 798, 188, 198, C.gold, { fill: C.paleGold });
  text(slide, ctx, "6772 / 6772", 798, 248, 360, 64, { size: 45, color: C.gold, bold: true, face: ctx.fonts.title });
  text(slide, ctx, "exact emitted rows", 798, 316, 300, 28, { size: 19, color: C.ink, bold: true });
  [["Cases", "106"], ["Wrong emitted", "0"], ["Missing emitted", "0"], ["Source gaps", "5238"]].forEach((row, i) => {
    rule(slide, ctx, 798, 374 + i * 42, 310, 1, C.line);
    text(slide, ctx, row[0], 798, 384 + i * 42, 180, 22, { size: 13, color: C.muted });
    text(slide, ctx, row[1], 1010, 382 + i * 42, 98, 24, { size: 15, color: i === 3 ? C.coral : C.ink, bold: true, align: "right" });
  });
  rect(slide, ctx, 142, 620, 996, 38, C.coral, "#00000000");
  text(slide, ctx, "Do not combine these lanes: v2 proves bounded recognition, not unconstrained APK-only accuracy.", 164, 628, 952, 22, { size: 15, color: C.white, bold: true, align: "center" });
  footer(slide, ctx, { dark: true });
  note(slide, "State the normal metric first: 927 of 1837 emitted Maven versions confirmed across 102 source-validated real APKs. Then separate the v2 lane: 6772 exact emitted rows across 106 source-tree cases under exact source-version slices. It is an upper-bound recognition test, not APK-only production accuracy.");
  return slide;
}

function slide10(presentation, ctx) {
  const slide = presentation.slides.add();
  page(slide, ctx, "Mixed results reveal where the matcher succeeds, drifts, or reaches a boundary", "Result interpretation", 10, { accent: C.gold });
  [
    { x: 70, w: 344, color: C.cyan, fill: C.paleCyan, title: "CLEAN", subtitle: "strong exact evidence", cases: ["F-Droid", "OpenTracks", "Tusky"], result: "high-confidence emitted versions" },
    { x: 468, w: 344, color: C.gold, fill: C.paleGold, title: "PARTIAL", subtitle: "useful but version-sensitive", cases: ["NewPipe  AntennaPod", "Wikipedia  Aegis", "Nextcloud  Markor"], result: "AndroidX / Kotlin / older-version drift" },
    { x: 866, w: 344, color: C.violet, fill: "#EEEAFE", title: "BOUNDARY", subtitle: "outside exact Maven claims", cases: ["Organic Maps", "Termux", "hidden DEX / protected"], result: "native, dynamic, or transformed evidence" },
  ].forEach((column) => {
    box(slide, ctx, column.x, 164, column.w, 408, C.white, column.color);
    rect(slide, ctx, column.x, 164, column.w, 74, column.color, "#00000000");
    text(slide, ctx, column.title, column.x + 24, 184, column.w - 48, 28, { size: 22, color: C.white, bold: true });
    text(slide, ctx, column.subtitle, column.x + 24, 244, column.w - 48, 24, { size: 13, color: column.color, bold: true });
    column.cases.forEach((value, i) => label(slide, ctx, value, column.x + 24, 294 + i * 52, column.w - 48, column.color, { fill: column.fill }));
    rule(slide, ctx, column.x + 24, 462, column.w - 48, 1, C.line);
    text(slide, ctx, column.result, column.x + 24, 486, column.w - 48, 56, { size: 14, color: C.ink, bold: true, align: "center" });
  });
  text(slide, ctx, "The difficult cases are not discarded; they become the roadmap for reference growth and matcher recall.", 134, 616, 1012, 34, { size: 18, color: C.ink, bold: true, align: "center" });
  footer(slide, ctx);
  note(slide, "This slide defends the mixed results. Clean cases show the pipeline can work end to end. Partial cases expose version-band and ecosystem ambiguity. Boundary cases show where static APK evidence is fundamentally limited. Keeping all three groups visible makes the evaluation more credible.");
  return slide;
}

function slide11(presentation, ctx) {
  const slide = presentation.slides.add();
  page(slide, ctx, "The final demo proves SBOM output, positive CVEs, and transparent remaining gaps", "Demo evidence", 11, { dark: true, accent: C.coral });
  miniWindow(slide, ctx, 62, 166, 362, 384, "clean-real-apk / report.html", C.cyan);
  text(slide, ctx, "23", 94, 238, 100, 50, { size: 40, color: C.cyan, bold: true });
  text(slide, ctx, "Maven components", 188, 254, 180, 24, { size: 14, color: C.ink, bold: true });
  label(slide, ctx, "23 / 23 source-confirmed", 94, 318, 264, C.lime, { fill: C.paleLime });
  label(slide, ctx, "CycloneDX + PURLs", 94, 366, 264, C.blue, { fill: C.paleBlue });
  label(slide, ctx, "OSV: 0 vulnerabilities", 94, 414, 264, C.cyan, { fill: C.paleCyan });
  text(slide, ctx, "Clean F-Droid control", 94, 490, 264, 24, { size: 14, color: C.muted, bold: true, align: "center" });
  miniWindow(slide, ctx, 458, 166, 362, 384, "vulnerable-fixture / report.html", C.coral);
  text(slide, ctx, "3", 490, 238, 80, 50, { size: 40, color: C.coral, bold: true });
  text(slide, ctx, "confirmed HIGH advisories", 566, 254, 210, 24, { size: 14, color: C.ink, bold: true });
  label(slide, ctx, "CVE-2020-36518", 490, 318, 264, C.coral, { fill: C.paleCoral });
  label(slide, ctx, "CVE-2022-42003", 490, 366, 264, C.coral, { fill: C.paleCoral });
  label(slide, ctx, "CVE-2022-42004", 490, 414, 264, C.coral, { fill: C.paleCoral });
  text(slide, ctx, "Jackson Databind 2.9.10.8", 490, 490, 264, 24, { size: 14, color: C.muted, bold: true, align: "center" });
  miniWindow(slide, ctx, 854, 166, 362, 384, "transparency-export.json", C.blue);
  [["12082", "source rows"], ["5238", "source gaps"], ["2515", "explained / boundary"], ["2281", "matcher recall"], ["442", "missing reference"]].forEach((row, i) => {
    text(slide, ctx, row[0], 888, 222 + i * 54, 100, 28, { size: 20, color: i < 2 ? C.blue : C.ink, bold: true });
    text(slide, ctx, row[1], 996, 226 + i * 54, 170, 24, { size: 13, color: C.muted });
  });
  text(slide, ctx, "Demo guardrail: weak version evidence never becomes a fake confirmed vulnerability.", 142, 602, 996, 34, { size: 18, color: C.white, bold: true, align: "center" });
  footer(slide, ctx, { dark: true });
  note(slide, "Use the existing generated artifacts rather than rerunning long jobs. Show the clean F-Droid report and CycloneDX file, then the controlled Jackson report with three HIGH advisories, then the transparency export. The point is both capability and honesty: remaining gaps are classified row by row.");
  return slide;
}

function slide12(presentation, ctx) {
  const slide = presentation.slides.add();
  page(slide, ctx, "AI assists hard R8 triage, while the deterministic matcher keeps authority", "Guarded AI contribution", 12, { accent: C.violet });
  [["RandomForest", "0.708", 0.708, C.blue, "integrated report-only"], ["MVP-safe Transformer", "0.882", 0.882, C.cyan, "risk-triage candidate"], ["Structured Transformer", "0.977", 0.977, C.violet, "research status only"], ["Raw opcode Transformer", "0.110", 0.110, C.coral, "below 0.128 baseline"]].forEach((model, i) => {
    const y = 174 + i * 84;
    text(slide, ctx, model[0], 78, y + 3, 230, 24, { size: 16, color: C.ink, bold: true });
    rect(slide, ctx, 330, y + 5, 440, 20, "#DFE6EF", "#00000000");
    rect(slide, ctx, 330, y + 5, 440 * model[2], 20, model[3], "#00000000");
    text(slide, ctx, model[1], 788, y - 1, 88, 28, { size: 18, color: model[3], bold: true });
    label(slide, ctx, model[4], 900, y, 260, model[3], { fill: C.white });
  });
  box(slide, ctx, 76, 524, 504, 104, C.paleCyan, C.cyan);
  text(slide, ctx, "READY", 98, 548, 96, 24, { size: 13, color: C.cyan, bold: true });
  text(slide, ctx, "report wording, prioritization, R8 risk triage", 198, 544, 350, 42, { size: 16, color: C.ink, bold: true });
  box(slide, ctx, 624, 524, 584, 104, C.paleCoral, C.coral);
  text(slide, ctx, "BLOCKED", 646, 548, 108, 24, { size: 13, color: C.coral, bold: true });
  text(slide, ctx, "selected versions, SBOM components, CVE labels", 764, 544, 410, 42, { size: 16, color: C.ink, bold: true });
  text(slide, ctx, "31,589 local evidence rows  |  strict APK promotion candidates: 0", 210, 650, 860, 24, { size: 14, color: C.muted, bold: true, align: "center" });
  footer(slide, ctx);
  note(slide, "Present AI as a guarded research contribution. The RandomForest is integrated only for report suggestions. The source-free MVP-safe Transformer reaches 0.882 macro-F1 and is a report-only risk-triage candidate. The raw-opcode model underperforms its baseline, so it remains an honest negative result. AI cannot select final versions or change SBOM/CVE output.");
  return slide;
}

function slide13(presentation, ctx) {
  const slide = presentation.slides.add();
  slide.background.fill = C.night;
  rect(slide, ctx, 0, 0, 1280, 720, C.night, "#00000000");
  rect(slide, ctx, 0, 0, 18, 720, C.gold, "#00000000");
  text(slide, ctx, "CONCLUSION", 72, 50, 200, 22, { size: 12, color: C.gold, bold: true });
  text(slide, ctx, "A credible reverse-SBOM tool", 72, 102, 760, 54, { size: 40, color: C.white, bold: true, face: ctx.fonts.title });
  text(slide, ctx, "must be useful, measurable, and honest about uncertainty.", 72, 158, 850, 46, { size: 25, color: "#B9C4D3", bold: true });
  [["01", "End-to-end MVP", "APK -> evidence -> CycloneDX -> CVE", C.blue], ["02", "Transparent evaluation", "clean, partial, boundary, and gap exports", C.cyan], ["03", "Guarded innovation", "hybrid matcher research + report-only AI", C.violet]].forEach((item, i) => {
    const x = 72 + i * 376;
    box(slide, ctx, x, 260, 336, 190, C.night2, C.lineDark);
    circle(slide, ctx, x + 24, 284, 42, item[3], "#00000000");
    text(slide, ctx, item[0], x + 24, 296, 42, 18, { size: 12, color: C.night, bold: true, align: "center" });
    text(slide, ctx, item[1], x + 82, 286, 224, 28, { size: 20, color: C.white, bold: true });
    text(slide, ctx, item[2], x + 24, 350, 282, 56, { size: 15, color: "#B8C3D2" });
    rect(slide, ctx, x, 440, 336, 10, item[3], "#00000000");
  });
  box(slide, ctx, 72, 500, 1090, 96, C.white, C.white);
  text(slide, ctx, "NEXT", 98, 526, 76, 22, { size: 12, color: C.coral, bold: true });
  text(slide, ctx, "stronger version-specific evidence, broader independent R8 corpora, and stricter APK-only promotion controls", 184, 518, 930, 44, { size: 17, color: C.ink, bold: true });
  text(slide, ctx, "Questions", 72, 638, 360, 38, { size: 26, color: C.gold, bold: true, face: ctx.fonts.title });
  text(slide, ctx, "Demo command: python scripts/run_final_ai_defense_demo.py --refresh", 570, 642, 590, 24, { size: 12, color: "#8997AA", mono: true, align: "right" });
  note(slide, "Close with three contributions: an end-to-end APK-to-SBOM pipeline, a transparent evaluation that keeps hard cases visible, and guarded matcher/AI research that does not overrule deterministic evidence. The next work is stronger version-specific evidence and larger independent R8 corpora. Then invite questions.");
  return slide;
}

const slides = [slide01, slide02, slide03, slide04, slide05, slide06, slide07, slide08, slide09, slide10, slide11, slide12, slide13];

export async function drawSlide(presentation, ctx, number) {
  return slides[number - 1](presentation, ctx);
}
