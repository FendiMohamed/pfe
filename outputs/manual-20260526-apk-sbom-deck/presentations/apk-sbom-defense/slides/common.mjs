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
  return shape(slide, ctx, "rect", x, y, w, h, fill, line, name);
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
    rect(slide, ctx, 0, 0, 7, 720, opts.accent ?? C.cyan, "#00000000");
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
  text(slide, ctx, String(ctx.displayNumber ?? number).padStart(2, "0"), 1170, 38, 48, 22, {
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
  circle(slide, ctx, x + 14, y + 12, 9, "#7A858D", "#00000000");
  circle(slide, ctx, x + 30, y + 12, 9, "#9BA3A8", "#00000000");
  circle(slide, ctx, x + 46, y + 12, 9, C.cyan, "#00000000");
  text(slide, ctx, titleValue, x + 68, y + 9, w - 84, 18, {
    size: 11,
    color: C.white,
    bold: true,
  });
  rect(slide, ctx, x + 18, y + 52, 6, h - 72, accent, "#00000000");
}

function screenshot(slide, ctx, assetKey, x, y, w, h, opts = {}) {
  const bytes = ctx.assets?.[assetKey];
  if (!bytes) throw new Error(`Missing screenshot asset: ${assetKey}`);
  box(slide, ctx, x, y, w, h, opts.frameFill ?? C.white, opts.line ?? C.line);
  return slide.images.add({
    blob: bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength),
    contentType: "image/png",
    alt: opts.alt ?? `${assetKey} project evidence screenshot`,
    fit: opts.fit ?? "contain",
    position: {
      left: x + (opts.inset ?? 8),
      top: y + (opts.inset ?? 8),
      width: w - 2 * (opts.inset ?? 8),
      height: h - 2 * (opts.inset ?? 8),
    },
  });
}

function evolutionRibbon(slide, ctx, items, y, opts = {}) {
  const dark = opts.dark ?? false;
  const x0 = opts.x ?? 72;
  const totalWidth = opts.w ?? 1136;
  const gap = opts.gap ?? 18;
  const itemWidth = (totalWidth - gap * (items.length - 1)) / items.length;
  items.forEach((item, index) => {
    const x = x0 + index * (itemWidth + gap);
    const color = item.color ?? C.blue;
    box(
      slide,
      ctx,
      x,
      y,
      itemWidth,
      opts.h ?? 92,
      dark ? C.night2 : (item.fill ?? C.white),
      dark ? C.lineDark : color,
    );
    text(slide, ctx, String(index + 1).padStart(2, "0"), x + 14, y + 12, 34, 18, {
      size: 11,
      color,
      bold: true,
    });
    text(slide, ctx, item.title, x + 50, y + 10, itemWidth - 64, 24, {
      size: 15,
      color: dark ? C.white : C.ink,
      bold: true,
    });
    text(slide, ctx, item.detail, x + 14, y + 42, itemWidth - 28, 42, {
      size: 11,
      color: dark ? "#AEBACC" : C.muted,
      align: "center",
    });
    if (index < items.length - 1) {
      arrow(slide, ctx, x + itemWidth - 2, y + 34, gap + 14, color);
    }
  });
}

function rationaleBand(slide, ctx, labelValue, value, y, opts = {}) {
  const dark = opts.dark ?? false;
  box(
    slide,
    ctx,
    opts.x ?? 72,
    y,
    opts.w ?? 1136,
    opts.h ?? 62,
    dark ? C.night2 : (opts.fill ?? C.white),
    opts.color ?? C.blue,
  );
  text(slide, ctx, labelValue.toUpperCase(), (opts.x ?? 72) + 20, y + 18, 150, 22, {
    size: 11,
    color: opts.color ?? C.blue,
    bold: true,
  });
  text(slide, ctx, value, (opts.x ?? 72) + 174, y + 13, (opts.w ?? 1136) - 194, 38, {
    size: opts.size ?? 15,
    color: dark ? C.white : C.ink,
    bold: true,
  });
}

function filePathBand(slide, ctx, value, y, opts = {}) {
  const dark = opts.dark ?? false;
  rect(
    slide,
    ctx,
    opts.x ?? 72,
    y,
    opts.w ?? 1136,
    opts.h ?? 34,
    dark ? "#17233A" : "#E9EEF5",
    "#00000000",
  );
  text(slide, ctx, value, (opts.x ?? 72) + 14, y + 7, (opts.w ?? 1136) - 28, 20, {
    size: opts.size ?? 10,
    color: dark ? "#AEBACC" : C.muted,
    mono: true,
    align: opts.align ?? "left",
  });
}

function metricTile(slide, ctx, value, labelValue, x, y, w, color, opts = {}) {
  box(slide, ctx, x, y, w, opts.h ?? 112, opts.dark ? C.night2 : C.white, opts.dark ? C.lineDark : color);
  text(slide, ctx, value, x + 14, y + 18, w - 28, 40, {
    size: opts.valueSize ?? 30,
    color,
    bold: true,
    align: "center",
    face: ctx.fonts.title,
  });
  text(slide, ctx, labelValue, x + 14, y + 64, w - 28, 34, {
    size: 12,
    color: opts.dark ? "#B5C0D0" : C.muted,
    bold: true,
    align: "center",
  });
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

function slide05(presentation, ctx, pageNumber = 5) {
  const slide = presentation.slides.add();
  page(slide, ctx, "MVP architecture: APK evidence and Maven references converge at the matcher", "System architecture", pageNumber, { accent: C.blue });
  const stages = [
    ["1", "Compiled APK", "DEX · manifest · resources · native"],
    ["2", "APK extraction", "inventory · metadata · forensic risk"],
    ["3", "DEX analysis", "packages · classes · methods · opcodes · graph"],
    ["4", "Hybrid matcher", "candidate shortlist · multi-signal scoring"],
    ["5", "Confidence gate", "identity · version · ambiguity"],
    ["6", "Security outputs", "CycloneDX · OSV · JSON/HTML report"],
  ];
  stages.forEach((stage, i) => {
    const x = 66 + i * 194;
    box(slide, ctx, x, 168, 166, 124, C.white, i === 3 ? C.cyan : C.line);
    text(slide, ctx, stage[0], x + 14, 184, 24, 20, { size: 11, color: C.blue, bold: true });
    text(slide, ctx, stage[1], x + 14, 214, 138, 28, { size: 16, color: C.ink, bold: true });
    text(slide, ctx, stage[2], x + 14, 250, 138, 28, { size: 10, color: C.muted, mono: true });
    if (i < stages.length - 1) arrow(slide, ctx, x + 166, 218, 28, C.blue);
  });

  text(slide, ctx, "REFERENCE PROFILE PIPELINE", 72, 354, 300, 20, { size: 11, color: C.blue, bold: true });
  [
    ["Maven JAR/AAR", "coordinate + version + POM"],
    ["D8 normalization", "JAR/AAR bytecode converted to DEX"],
    ["Feature extraction", "same representation as APK evidence"],
    ["SQLite reference DB", "versioned profiles + PURLs"],
  ].forEach((stage, i) => {
    const x = 72 + i * 228;
    box(slide, ctx, x, 388, 198, 86, i === 3 ? C.paleCyan : C.white, i === 3 ? C.cyan : C.line);
    text(slide, ctx, stage[0], x + 14, 404, 170, 22, { size: 14, color: C.ink, bold: true });
    text(slide, ctx, stage[1], x + 14, 434, 170, 26, { size: 10, color: C.muted });
    if (i < 3) arrow(slide, ctx, x + 198, 421, 30, C.blue);
  });
  rule(slide, ctx, 731, 292, 2, 52, C.cyan);
  rule(slide, ctx, 731, 344, 127, 2, C.cyan);
  rule(slide, ctx, 858, 344, 2, 44, C.cyan);
  text(slide, ctx, "candidate profiles feed the matcher", 876, 348, 240, 20, { size: 10, color: C.cyan, bold: true });

  rect(slide, ctx, 72, 520, 1136, 76, C.night, "#00000000");
  text(slide, ctx, "WHY THIS SHAPE", 92, 538, 150, 18, { size: 11, color: C.white, bold: true });
  text(slide, ctx, "Static and reproducible", 270, 536, 210, 22, { size: 14, color: C.white, bold: true });
  text(slide, ctx, "Same feature space", 530, 536, 190, 22, { size: 14, color: C.white, bold: true });
  text(slide, ctx, "Confidence before CVE", 780, 536, 210, 22, { size: 14, color: C.white, bold: true });
  text(slide, ctx, "Every decision can be traced to evidence and replayed.", 270, 564, 220, 18, { size: 10, color: "#C8CFD4" });
  text(slide, ctx, "APK and Maven artifacts are compared using equivalent DEX features.", 530, 564, 220, 18, { size: 10, color: "#C8CFD4" });
  text(slide, ctx, "Weak version evidence cannot become a confirmed vulnerability.", 780, 564, 310, 18, { size: 10, color: "#C8CFD4" });
  filePathBand(slide, ctx, "Implementation map: src/apk_sbom/apk_extractor.py -> dex_analyzer.py -> matcher.py -> sbom.py / vulnerability.py / report.py", 616);
  footer(slide, ctx);
  note(slide, "This is the actual MVP architecture. The main APK lane extracts and analyzes evidence, the separate Maven lane builds comparable versioned profiles, and both meet at the hybrid matcher. A confidence gate sits before CycloneDX and OSV so uncertain version evidence cannot become a strong vulnerability claim. The separation also makes the system reproducible: reference construction can evolve without hiding matcher behavior.");
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

function slide08(presentation, ctx, pageNumber = 8) {
  const slide = presentation.slides.add();
  page(slide, ctx, "Evaluation keeps hard APK families visible instead of collapsing them into one score", "APK classification", pageNumber, { accent: C.lime });
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

function slide09(presentation, ctx, pageNumber = 9) {
  const slide = presentation.slides.add();
  page(slide, ctx, "The normal real-APK result and the v2 upper-bound answer different questions", "Results", pageNumber, { dark: true, accent: C.cyan });
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

function slide10(presentation, ctx, pageNumber = 10) {
  const slide = presentation.slides.add();
  page(slide, ctx, "One run separates correct versions from scoring, recall, and reference-DB gaps", "Concrete demo interpretation", pageNumber, { accent: C.gold });
  const columns = [
    {
      x: 58, w: 274, color: C.cyan, title: "CORRECT",
      subtitle: "emitted + source-confirmed",
      rows: ["okhttp  4.12.0", "coroutines-android  1.7.3", "activity  1.10.1"],
      detail: "The selected Maven version matches the source dependency tree.",
    },
    {
      x: 356, w: 274, color: C.coral, title: "SCORING MISS",
      subtitle: "candidate version mismatch",
      rows: ["okio selected  2.8.0", "source version  3.7.0", "status  version-mismatch"],
      detail: "Kept outside the confirmed SBOM instead of becoming a false exact claim.",
    },
    {
      x: 654, w: 274, color: C.violet, title: "MATCHER RECALL",
      subtitle: "reference exists, not emitted",
      rows: ["activity-compose", "source  1.10.1", "exact version is in DB"],
      detail: "The next action is threshold or feature-recall work, not DB growth.",
    },
    {
      x: 952, w: 274, color: C.gold, title: "REFERENCE GAP",
      subtitle: "exact version absent from DB",
      rows: ["collection-ktx", "source  1.4.4", "missing-reference-candidate"],
      detail: "The coordinate/version must be added or safely aliased before matching can succeed.",
    },
  ];
  columns.forEach((column) => {
    box(slide, ctx, column.x, 154, column.w, 420, C.white, column.color);
    rect(slide, ctx, column.x, 154, column.w, 68, column.color, "#00000000");
    text(slide, ctx, column.title, column.x + 18, 174, column.w - 36, 26, { size: 18, color: C.white, bold: true, align: "center" });
    text(slide, ctx, column.subtitle, column.x + 18, 240, column.w - 36, 34, { size: 12, color: column.color, bold: true, align: "center" });
    column.rows.forEach((value, i) => {
      label(slide, ctx, value, column.x + 18, 296 + i * 52, column.w - 36, column.color, {
        fill: i === 0 ? C.white : (column.color === C.coral ? C.paleCoral : column.color === C.gold ? C.paleGold : column.color === C.violet ? "#EEEAFE" : C.paleCyan),
      });
    });
    rule(slide, ctx, column.x + 20, 464, column.w - 40, 1, C.line);
    text(slide, ctx, column.detail, column.x + 22, 486, column.w - 44, 64, { size: 11, color: C.ink, bold: true, align: "center" });
  });
  text(slide, ctx, "Transparency totals: 442 missing-reference rows  |  2,281 matcher-recall rows  |  5,238 source-gap rows", 100, 608, 1080, 30, { size: 16, color: C.ink, bold: true, align: "center" });
  footer(slide, ctx);
  note(slide, "Use concrete examples. F-Droid confirms versions such as okhttp 4.12.0, coroutines-android 1.7.3, and activity 1.10.1. The okio 2.8.0 candidate disagreed with source 3.7.0 and was not promoted as confirmed. activity-compose 1.10.1 is a matcher-recall case because the reference exists. collection-ktx 1.4.4 is a missing-reference case because the exact version is absent.");
  return slide;
}

function slide11(presentation, ctx, pageNumber = 11) {
  const slide = presentation.slides.add();
  page(slide, ctx, "Generated report screenshots prove both the clean and vulnerable demo lanes", "CVE results", pageNumber, { dark: true, accent: C.coral });
  text(slide, ctx, "CLEAN REAL APK", 72, 136, 300, 22, { size: 12, color: C.cyan, bold: true });
  text(slide, ctx, "CONTROLLED POSITIVE CVE", 670, 136, 320, 22, { size: 12, color: C.coral, bold: true });
  screenshot(slide, ctx, "cleanReport", 72, 166, 540, 334, {
    alt: "Generated F-Droid APK SBOM report showing 23 Maven components and zero vulnerabilities",
    line: C.cyan,
  });
  screenshot(slide, ctx, "vulnerableReport", 670, 166, 538, 334, {
    alt: "Generated Jackson Databind report showing one Maven component and three confirmed vulnerabilities",
    line: C.coral,
  });
  label(slide, ctx, "23 Maven components  |  OSV 0", 94, 520, 494, C.cyan, { fill: C.night2 });
  label(slide, ctx, "Jackson Databind 2.9.10.8  |  3 HIGH", 692, 520, 492, C.coral, { fill: C.night2 });
  ["CVE-2020-36518", "CVE-2022-42003", "CVE-2022-42004"].forEach((value, i) => {
    label(slide, ctx, value, 690 + i * 166, 566, 154, C.coral, { fill: C.night2 });
  });
  text(slide, ctx, "Artifacts: report.html + sbom.cdx.json + osv-vulnerabilities.json + source-validation.json", 92, 624, 1096, 24, { size: 13, color: C.white, bold: true, align: "center", mono: true });
  footer(slide, ctx, { dark: true });
  note(slide, "These are screenshots of the generated project reports, not mockups. The clean F-Droid report shows 23 Maven components and zero returned vulnerabilities. The controlled Jackson Databind 2.9.10.8 report shows three confirmed HIGH advisories: CVE-2020-36518, CVE-2022-42003, and CVE-2022-42004.");
  return slide;
}

function slide12(presentation, ctx, pageNumber = 12) {
  const slide = presentation.slides.add();
  page(slide, ctx, "AI assists hard R8 triage, while the deterministic matcher keeps authority", "AI integration gate", pageNumber, { accent: C.violet });
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

function slideWhyArchitecture(presentation, ctx) {
  const slide = presentation.slides.add();
  page(slide, ctx, "Architecture choices were driven by evidence, scope, and interoperability", "Architecture decisions", 5, { accent: C.blue });
  rect(slide, ctx, 72, 148, 1136, 42, C.night, "#00000000");
  text(slide, ctx, "DECISION", 92, 160, 170, 18, { size: 11, color: C.white, bold: true });
  text(slide, ctx, "CHOSEN DESIGN", 282, 160, 230, 18, { size: 11, color: C.white, bold: true });
  text(slide, ctx, "WHY", 532, 160, 390, 18, { size: 11, color: C.white, bold: true });
  text(slide, ctx, "NOT CHOSEN", 942, 160, 220, 18, { size: 11, color: C.white, bold: true });
  [
    ["Analysis", "Hybrid static pipeline", "Works from the APK alone; combines name and structural evidence; reproducible for evaluation.", "Package/hash-only or dynamic-first"],
    ["Versions", "Local Maven reference DB", "SBOM and CVE claims require coordinate + version; JAR/AAR profiles are repeatable.", "Library-name-only detection"],
    ["SBOM", "CycloneDX + PURL", "Standard security artifact with Maven identity, evidence properties, and scanner compatibility.", "Custom JSON as final output"],
    ["Vulnerabilities", "OSV first", "Queries Maven package/version directly and fits PURL-based component evidence.", "NVD/CPE-only mapping"],
    ["Obfuscation", "Confidence-affecting policy", "R8 can remove or transform evidence, so the system lowers confidence instead of claiming immunity.", "“Obfuscation-proof” claims"],
  ].forEach((row, i) => {
    const y = 190 + i * 78;
    rect(slide, ctx, 72, y, 1136, 78, i % 2 === 0 ? C.white : "#F0F1EF", C.line);
    text(slide, ctx, row[0], 92, y + 20, 160, 28, { size: 15, color: C.blue, bold: true });
    text(slide, ctx, row[1], 282, y + 17, 220, 38, { size: 14, color: C.ink, bold: true });
    text(slide, ctx, row[2], 532, y + 13, 382, 50, { size: 12, color: C.ink });
    text(slide, ctx, row[3], 942, y + 17, 226, 42, { size: 12, color: C.coral });
  });
  filePathBand(slide, ctx, "Architecture rationale: docs/architecture/DECISIONS_LOG.md  |  docs/architecture/MVP_ARCHITECTURE.md", 602);
  footer(slide, ctx);
  note(slide, "Explain the choices as engineering decisions, not decoration. Static hybrid analysis was chosen because the input is an APK and package/hash-only evidence is fragile. Maven references were chosen because exact versions are required for SBOM and CVE work. CycloneDX and PURL provide interoperability. OSV aligns with Maven package/version queries. R8 is treated as confidence-affecting because perfect resilience is not supported by the evidence.");
  return slide;
}

function slideApkExtractor(presentation, ctx) {
  const slide = presentation.slides.add();
  page(slide, ctx, "APK extraction evolved from file listing into a forensic boundary detector", "Component 1  |  APK extractor", 7, { dark: true, accent: C.blue });
  evolutionRibbon(slide, ctx, [
    { title: "ZIP inventory", detail: "List classes.dex and basic APK entries.", color: C.blue },
    { title: "Metadata", detail: "Decode manifest, SDK levels, package and version.", color: C.cyan },
    { title: "Native evidence", detail: "Hash every .so file by ABI without inventing identity.", color: C.gold },
    { title: "Forensics", detail: "Flag hidden DEX, opaque assets, and protector hints.", color: C.coral },
  ], 144, { dark: true });
  box(slide, ctx, 72, 268, 540, 292, C.night2, C.lineDark);
  text(slide, ctx, "CURRENT OUTPUT", 96, 292, 180, 22, { size: 12, color: C.blue, bold: true });
  [
    "APK SHA-256 and exact binary identity",
    "standard and nonstandard DEX paths",
    "manifest package, version, SDK, permissions",
    "resources/assets counts",
    "native files, ABI, size, SHA-256",
    "extraction-risk indicators",
  ].forEach((item, i) => {
    circle(slide, ctx, 98, 340 + i * 34, 10, i < 3 ? C.blue : C.cyan, "#00000000");
    text(slide, ctx, item, 122, 332 + i * 34, 450, 24, { size: 13, color: "#C2CDDB" });
  });
  box(slide, ctx, 642, 268, 566, 292, C.white, C.white);
  text(slide, ctx, "WHY THIS CHOICE", 668, 292, 180, 22, { size: 12, color: C.coral, bold: true });
  text(slide, ctx, "The extractor must establish what evidence is actually present before matching begins.", 668, 330, 500, 46, { size: 18, color: C.ink, bold: true });
  [
    ["No decompiler dependency", "Uses the APK ZIP surface and Androguard only where binary XML/DEX parsing is needed."],
    ["Boundary honesty", "Native and hidden-code cases become explicit limitations instead of false Maven claims."],
    ["Multidex first-class", "All standard classes*.dex files are carried into later analysis."],
  ].forEach((row, i) => {
    label(slide, ctx, row[0], 668, 402 + i * 50, 170, i === 1 ? C.coral : C.blue, { fill: i === 1 ? C.paleCoral : C.paleBlue });
    text(slide, ctx, row[1], 852, 402 + i * 50, 320, 36, { size: 11, color: C.muted });
  });
  filePathBand(slide, ctx, "Implementation: src/apk_sbom/apk_extractor.py  ->  inspect_apk(), build_forensic_summary(), apk_indicators()", 584, { dark: true });
  footer(slide, ctx, { dark: true });
  note(slide, "Evolution: the extractor began as a ZIP/DEX inventory, then added manifest decoding, native hashing, and finally forensic indicators for nonstandard DEX and protector-like packaging. We chose this because later confidence is only credible if the pipeline first knows which evidence is present or hidden. Code: src/apk_sbom/apk_extractor.py.");
  return slide;
}

function slideDexAnalyzer(presentation, ctx) {
  const slide = presentation.slides.add();
  page(slide, ctx, "DEX analysis grew from coarse counts into reusable multi-scale evidence", "Component 2  |  DEX analyzer", 8, { accent: C.violet });
  evolutionRibbon(slide, ctx, [
    { title: "Coarse", detail: "Packages, class counts, method counts, opcode histogram.", color: C.blue, fill: C.paleBlue },
    { title: "Identity", detail: "Class descriptors, methods, fields, API references.", color: C.cyan, fill: C.paleCyan },
    { title: "Structure", detail: "Class dependencies, graph shape, literals and context.", color: C.gold, fill: C.paleGold },
    { title: "R8 research", detail: "Basic-block, call-chain, neighbor, field-operation features.", color: C.violet, fill: "#EEEAFE" },
  ], 144);
  box(slide, ctx, 72, 268, 716, 298, C.white, C.line);
  text(slide, ctx, "FEATURE LAYERS", 96, 292, 180, 22, { size: 12, color: C.violet, bold: true });
  [
    ["CORE SCORING", "package  class  method  opcode  CDG  literal", C.blue, C.paleBlue],
    ["GUARDED", "API references  opcode tri-grams  POM coherence", C.gold, C.paleGold],
    ["INERT / REPORT", "basic blocks  call chains  class neighbors  field operations", C.violet, "#EEEAFE"],
  ].forEach((row, i) => {
    box(slide, ctx, 96, 336 + i * 68, 660, 52, row[3], row[2]);
    text(slide, ctx, row[0], 112, 351 + i * 68, 132, 22, { size: 11, color: row[2], bold: true });
    text(slide, ctx, row[1], 252, 348 + i * 68, 486, 26, { size: 13, color: C.ink, bold: true });
  });
  box(slide, ctx, 818, 268, 390, 298, C.night2, C.night2);
  text(slide, ctx, "DESIGN RULE", 842, 292, 150, 22, { size: 12, color: C.cyan, bold: true });
  text(slide, ctx, "Extract broadly.\nScore narrowly.", 842, 334, 318, 84, { size: 29, color: C.white, bold: true, align: "center", face: ctx.fonts.title });
  text(slide, ctx, "Promising features remain available for experiments without silently changing production decisions.", 852, 448, 298, 72, { size: 14, color: "#B8C3D3", align: "center" });
  filePathBand(slide, ctx, "Implementation: src/apk_sbom/dex_analyzer.py  ->  analyze_dex_bytes(), analyze_apk_dex()", 588);
  footer(slide, ctx);
  note(slide, "The DEX analyzer started with packages and opcode counts. It then added class/method identity, graph and literal evidence, and later the Phase 3 multi-scale features. The key choice is to extract broadly but keep new features inert until control matrices justify scoring. Code: src/apk_sbom/dex_analyzer.py. Evidence: docs/evaluation/R8_MULTISCALE_FEATURE_DIAGNOSTICS.md.");
  return slide;
}

function slideReferenceDb(presentation, ctx) {
  const slide = presentation.slides.add();
  page(slide, ctx, "The reference database became a reproducible Maven-to-DEX feature factory", "Component 3  |  Reference DB", 9, { dark: true, accent: C.cyan });
  evolutionRibbon(slide, ctx, [
    { title: "Seed list", detail: "Hand-selected coordinates and versions.", color: C.blue },
    { title: "Maven fetch", detail: "Download JAR/AAR plus POM metadata and hashes.", color: C.cyan },
    { title: "DEX normalization", detail: "Convert JAR/classes.jar through D8 for comparable bytecode.", color: C.lime },
    { title: "Guarded growth", detail: "Store rich SQLite features; promote versions only after controls.", color: C.gold },
  ], 144, { dark: true });
  const stages = [
    ["Maven", "JAR / AAR\nPOM", C.blue],
    ["D8", "DEX\nnormalization", C.violet],
    ["Features", "classes  methods\nopcodes  graph", C.cyan],
    ["SQLite", "coordinate + version\nsearchable evidence", C.lime],
  ];
  stages.forEach((item, i) => {
    const x = 76 + i * 276;
    box(slide, ctx, x, 286, 228, 164, C.night2, C.lineDark);
    text(slide, ctx, item[0], x + 18, 310, 192, 28, { size: 22, color: item[2], bold: true, align: "center" });
    text(slide, ctx, item[1], x + 18, 354, 192, 58, { size: 14, color: "#B9C5D4", mono: true, align: "center" });
    if (i < stages.length - 1) arrow(slide, ctx, x + 228, 350, 48, item[2]);
  });
  metricTile(slide, ctx, "10,517", "coordinate-version components in the final large v2 DB", 76, 480, 330, C.cyan, { dark: true });
  metricTile(slide, ctx, "15.8 GB", "feature database artifact", 430, 480, 250, C.violet, { dark: true });
  metricTile(slide, ctx, "106 / 106", "source-tree cases rerun in the bounded lane", 704, 480, 250, C.lime, { dark: true });
  metricTile(slide, ctx, "Guarded", "reference additions must pass current controls", 978, 480, 230, C.gold, { dark: true, valueSize: 25 });
  filePathBand(slide, ctx, "Code: maven_downloader.py  ->  reference_converter.py  ->  reference_features.py  |  DB: data/reference_db/reference_features_demo_final_large_v2.sqlite", 612, { dark: true, size: 9 });
  footer(slide, ctx, { dark: true });
  note(slide, "The reference lane evolved from a small manual list into a reproducible factory: fetch Maven artifacts and POMs, normalize JAR/AAR bytecode through D8, extract the same features as the APK, and store them in SQLite. We guard reference growth because adding the correct version can still regress another APK when adjacent versions are similar.");
  return slide;
}

function slideMatcherEvolution(presentation, ctx) {
  const slide = presentation.slides.add();
  page(slide, ctx, "Candidate generation and matching evolved toward guarded multi-signal decisions", "Component 4  |  Matcher", 10, { accent: C.lime });
  evolutionRibbon(slide, ctx, [
    { title: "Package shortlist", detail: "Fast recall, but fragile under renaming and artifact overlap.", color: C.blue, fill: C.paleBlue },
    { title: "Weighted fusion", detail: "Class, method, opcode, graph, literal evidence.", color: C.cyan, fill: C.paleCyan },
    { title: "Version policy", detail: "Unique evidence, artifact families, ambiguity and near ties.", color: C.gold, fill: C.paleGold },
    { title: "Evidence gates", detail: "Unsafe global signals stay disabled or report-only.", color: C.coral, fill: C.paleCoral },
  ], 144);
  box(slide, ctx, 72, 272, 508, 286, C.night2, C.night2);
  text(slide, ctx, "CANDIDATE FLOW", 96, 296, 180, 22, { size: 12, color: C.lime, bold: true });
  ["APK feature set", "reference package prefilter", "same-coordinate versions", "artifact-family rules", "ranked candidates"].forEach((item, i) => {
    label(slide, ctx, item, 104, 338 + i * 42, 270, i < 2 ? C.blue : C.lime, { fill: C.night });
    if (i < 4) arrow(slide, ctx, 386, 343 + i * 42, 112, i < 2 ? C.blue : C.lime);
  });
  text(slide, ctx, "shortlist before deep scoring", 386, 510, 150, 28, { size: 11, color: "#AEBACC", align: "center" });
  box(slide, ctx, 610, 272, 598, 286, C.white, C.line);
  text(slide, ctx, "CURRENT DECISION LOGIC", 636, 296, 220, 22, { size: 12, color: C.blue, bold: true });
  [
    ["Identity", "package, class, method, opcode and graph agreement", C.blue],
    ["Version", "score gap plus version-distinctive literals/context", C.cyan],
    ["Family", "Okio/OkHttp/Lifecycle target overlap rules", C.violet],
    ["Guardrail", "API-ref and opcode tri-gram weights remain 0.0 globally", C.coral],
  ].forEach((row, i) => {
    circle(slide, ctx, 640, 340 + i * 48, 14, row[2], "#00000000");
    text(slide, ctx, row[0], 668, 334 + i * 48, 94, 24, { size: 13, color: row[2], bold: true });
    text(slide, ctx, row[1], 770, 332 + i * 48, 402, 30, { size: 12, color: C.ink });
  });
  rationaleBand(slide, ctx, "Why", "One global improvement is not enough: a target fix is rejected when controlled, clean, partial, or boundary controls regress.", 584, { color: C.coral, fill: C.paleCoral, h: 58 });
  filePathBand(slide, ctx, "Implementation: src/apk_sbom/matcher.py  |  Decision evidence: docs/thesis/EXPERIMENT_DECISION_LEDGER.md", 650);
  footer(slide, ctx);
  note(slide, "The matcher evolved from package-driven candidate generation into weighted multi-signal fusion, then added artifact-family and version-ambiguity policies. The strongest project lesson is the evidence gate: a change that fixes one target but regresses controls is not promoted. Code: src/apk_sbom/matcher.py.");
  return slide;
}

function slideConfidenceEvolution(presentation, ctx) {
  const slide = presentation.slides.add();
  page(slide, ctx, "Confidence evolved from one score into separate claims and explicit ambiguity", "Component 5  |  Version decision", 11, { dark: true, accent: C.gold });
  evolutionRibbon(slide, ctx, [
    { title: "Single score", detail: "Easy to display, but mixes presence and exact version.", color: C.coral },
    { title: "Identity split", detail: "First decide whether the library is present.", color: C.blue },
    { title: "Version split", detail: "Then measure exact-version support and score gap.", color: C.cyan },
    { title: "Ambiguity", detail: "Export near-tie versions and gate CVE confirmation.", color: C.gold },
  ], 144, { dark: true });
  [
    { x: 76, title: "IDENTITY", color: C.blue, value: "present?", rows: ["overlap strength", "structural agreement", "family coherence"] },
    { x: 414, title: "VERSION", color: C.cyan, value: "exact?", rows: ["rank and score gap", "unique evidence", "near-version competition"] },
    { x: 752, title: "AMBIGUITY", color: C.gold, value: "alternatives?", rows: ["feature-equivalent tie", "near tie <= 0.006", "structured version set"] },
  ].forEach((column) => {
    box(slide, ctx, column.x, 272, 292, 276, C.night2, C.lineDark);
    text(slide, ctx, column.title, column.x + 22, 296, 248, 22, { size: 12, color: column.color, bold: true, align: "center" });
    text(slide, ctx, column.value, column.x + 22, 332, 248, 42, { size: 28, color: C.white, bold: true, align: "center", face: ctx.fonts.title });
    column.rows.forEach((row, i) => {
      rule(slide, ctx, column.x + 32, 406 + i * 40, 22, 3, column.color);
      text(slide, ctx, row, column.x + 68, 397 + i * 40, 190, 24, { size: 13, color: "#B8C3D3" });
    });
  });
  box(slide, ctx, 1070, 272, 138, 276, C.white, C.white);
  text(slide, ctx, "CVE", 1092, 304, 96, 28, { size: 22, color: C.coral, bold: true, align: "center" });
  text(slide, ctx, "confirmed", 1090, 372, 100, 28, { size: 15, color: C.coral, bold: true, align: "center" });
  text(slide, ctx, "only when\nidentity + version\nare strong", 1090, 418, 100, 76, { size: 13, color: C.ink, align: "center" });
  rationaleBand(slide, ctx, "Policy", "A detected library can be real while its exact version remains uncertain; the output must preserve that distinction.", 578, { dark: true, color: C.gold });
  filePathBand(slide, ctx, "Implementation: matcher.py  ->  build_version_decisions(), classify_identity_candidate(), classify_version_candidate()", 650, { dark: true });
  footer(slide, ctx, { dark: true });
  note(slide, "The original single-score view was too easy to overinterpret. The current model separates identity from exact version, records score-gap and distinctive evidence, and exports ambiguous alternatives. This is why uncertain versions cannot create confirmed vulnerabilities.");
  return slide;
}

function slideSbomEvolution(presentation, ctx) {
  const slide = presentation.slides.add();
  page(slide, ctx, "SBOM output evolved from internal JSON into evidence-rich CycloneDX 1.5", "Component 6  |  SBOM generator", 12, { accent: C.blue });
  evolutionRibbon(slide, ctx, [
    { title: "Internal JSON", detail: "Useful for debugging, not interoperable.", color: C.muted, fill: C.white },
    { title: "CycloneDX", detail: "Standard components, hashes, dependencies and metadata.", color: C.blue, fill: C.paleBlue },
    { title: "PURL + evidence", detail: "Maven identity, confidence properties, ambiguity.", color: C.cyan, fill: C.paleCyan },
    { title: "Boundary files", detail: "Native .so entries remain hash-only file components.", color: C.gold, fill: C.paleGold },
  ], 144);
  miniWindow(slide, ctx, 72, 278, 622, 290, "sbom.cdx.json", C.blue);
  text(slide, ctx, '"type": "library"', 112, 346, 250, 22, { size: 14, color: C.blue, bold: true, mono: true });
  text(slide, ctx, '"purl": "pkg:maven/...@version"', 112, 384, 470, 22, { size: 14, color: C.cyan, bold: true, mono: true });
  text(slide, ctx, '"identity-confidence": "0.871"', 112, 422, 470, 22, { size: 13, color: C.ink, mono: true });
  text(slide, ctx, '"version-confidence": "0.843"', 112, 456, 470, 22, { size: 13, color: C.ink, mono: true });
  text(slide, ctx, '"ambiguous-versions": [...]', 112, 490, 470, 22, { size: 13, color: C.gold, mono: true });
  box(slide, ctx, 726, 278, 482, 290, C.night2, C.night2);
  text(slide, ctx, "WHY CYCLONEDX", 752, 302, 190, 22, { size: 12, color: C.blue, bold: true });
  [
    ["Standard", "Can be consumed by other SBOM and security workflows.", C.blue],
    ["Traceable", "Every component carries PURL, confidence, and evidence.", C.cyan],
    ["Honest", "Native files and uncertainty are represented without false package claims.", C.gold],
  ].forEach((row, i) => {
    circle(slide, ctx, 754, 354 + i * 62, 16, row[2], "#00000000");
    text(slide, ctx, row[0], 786, 348 + i * 62, 110, 24, { size: 14, color: row[2], bold: true });
    text(slide, ctx, row[1], 900, 344 + i * 62, 276, 40, { size: 12, color: "#B9C5D4" });
  });
  filePathBand(slide, ctx, "Implementation: src/apk_sbom/sbom.py  ->  build_cyclonedx_bom()  |  Spec version: CycloneDX 1.5", 598);
  footer(slide, ctx);
  note(slide, "The SBOM lane moved from internal result JSON to CycloneDX 1.5, then added Maven PURLs, evidence properties, separate identity/version confidence, ambiguity, and native hash-only file components. We chose CycloneDX because it connects directly to vulnerability and scanner workflows.");
  return slide;
}

function slideCveEvolution(presentation, ctx) {
  const slide = presentation.slides.add();
  page(slide, ctx, "Vulnerability lookup became package-aware and confidence-aware", "Component 7  |  CVE / OSV", 13, { dark: true, accent: C.coral });
  evolutionRibbon(slide, ctx, [
    { title: "NVD idea", detail: "CPE mapping is awkward for Maven coordinates.", color: C.muted },
    { title: "OSV first", detail: "Batch Maven package + version queries.", color: C.blue },
    { title: "Enrichment", detail: "Deduplicate CVE/GHSA aliases and retain strongest severity.", color: C.coral },
    { title: "Claim gate", detail: "Confirmed vs potential depends on identity/version/source proof.", color: C.gold },
  ], 144, { dark: true });
  const flow = [
    ["Maven PURL", "pkg:maven/group/artifact@version", C.blue],
    ["OSV batch", "query package + version", C.cyan],
    ["Normalize", "aliases + severity + duplicates", C.violet],
    ["Classify", "confirmed / potential / none", C.coral],
  ];
  flow.forEach((item, i) => {
    const x = 72 + i * 284;
    box(slide, ctx, x, 290, 246, 166, C.night2, C.lineDark);
    text(slide, ctx, item[0], x + 18, 316, 210, 28, { size: 20, color: item[2], bold: true, align: "center" });
    text(slide, ctx, item[1], x + 18, 370, 210, 46, { size: 12, color: "#BAC5D4", align: "center" });
    if (i < flow.length - 1) arrow(slide, ctx, x + 246, 354, 38, item[2]);
  });
  box(slide, ctx, 72, 488, 550, 102, C.paleCyan, C.cyan);
  text(slide, ctx, "CONFIRMED", 94, 514, 118, 22, { size: 12, color: C.cyan, bold: true });
  text(slide, ctx, "Strong identity + exact/high version confidence + source confirmation when available.", 220, 506, 370, 48, { size: 14, color: C.ink, bold: true });
  box(slide, ctx, 654, 488, 554, 102, C.paleGold, C.gold);
  text(slide, ctx, "POTENTIAL", 676, 514, 118, 22, { size: 12, color: C.gold, bold: true });
  text(slide, ctx, "OSV matched, but version ambiguity or source mismatch blocks a confirmed claim.", 802, 506, 370, 48, { size: 14, color: C.ink, bold: true });
  filePathBand(slide, ctx, "Implementation: src/apk_sbom/vulnerability.py  ->  query_osv_for_libraries(), deduplicate_vulnerabilities(), classify_vulnerability_finding()", 620, { dark: true, size: 9 });
  footer(slide, ctx, { dark: true });
  note(slide, "We considered NVD-first mapping, but Maven coordinates align much better with OSV. The current lane batches queries, enriches and deduplicates aliases, extracts severity, and then classifies findings using the component confidence and source validation. Code: src/apk_sbom/vulnerability.py.");
  return slide;
}

function slideReportingEvolution(presentation, ctx) {
  const slide = presentation.slides.add();
  page(slide, ctx, "Reporting evolved into the transparency layer of the system", "Component 8  |  Reports", 14, { accent: C.cyan });
  evolutionRibbon(slide, ctx, [
    { title: "Raw outputs", detail: "matches.json and sbom.cdx.json.", color: C.blue, fill: C.paleBlue },
    { title: "Human formats", detail: "JSON, Markdown, and HTML from one evidence model.", color: C.cyan, fill: C.paleCyan },
    { title: "Uncertainty", detail: "Identity/version confidence, ambiguity, R8 and extraction risk.", color: C.gold, fill: C.paleGold },
    { title: "Research layers", detail: "Source validation, Phase 5, router, and AI remain labeled report-only.", color: C.violet, fill: "#EEEAFE" },
  ], 144);
  [
    ["matches.json", "ranked candidates and signal breakdown", C.blue],
    ["sbom.cdx.json", "standard component and evidence output", C.cyan],
    ["osv-vulnerabilities.json", "normalized advisory evidence", C.coral],
    ["report.json", "complete machine-readable package", C.violet],
    ["report.md", "thesis and review friendly", C.gold],
    ["report.html", "demo and analyst friendly", C.lime],
  ].forEach((item, i) => {
    const col = i % 3;
    const row = Math.floor(i / 3);
    const x = 72 + col * 382;
    const y = 286 + row * 118;
    box(slide, ctx, x, y, 350, 92, C.white, item[2]);
    text(slide, ctx, item[0], x + 18, y + 16, 314, 24, { size: 16, color: item[2], bold: true, mono: true });
    text(slide, ctx, item[1], x + 18, y + 50, 314, 28, { size: 12, color: C.muted });
  });
  rationaleBand(slide, ctx, "Why", "The report is where experimental evidence can be useful without silently changing selected versions, SBOM components, or CVE labels.", 536, { color: C.violet, fill: "#EEEAFE" });
  filePathBand(slide, ctx, "Implementation: src/apk_sbom/report.py  ->  generate_final_report(), build_json_report(), build_markdown_report(), build_html_report()", 620);
  footer(slide, ctx);
  note(slide, "Reporting is not cosmetic. It is the transparency layer that keeps default matcher authority separate from experiment-only and AI assistance. All formats are generated from the same evidence, so uncertainty and provenance stay consistent. Code: src/apk_sbom/report.py.");
  return slide;
}

function slideLayeredDataset(presentation, ctx) {
  const slide = presentation.slides.add();
  page(slide, ctx, "A layered dataset is necessary because different APKs support different claims", "Dataset design", 15, { dark: true, accent: C.lime });
  [
    { y: 160, w: 1080, x: 100, title: "L1  CONTROLLED", detail: "Exact dependencies by construction  |  precision, recall, F1, version correctness", color: C.lime },
    { y: 250, w: 930, x: 175, title: "L2  SOURCE-VALIDATED REAL", detail: "APK + source tag + resolved dependency tree  |  emitted-version confirmation", color: C.cyan },
    { y: 340, w: 780, x: 250, title: "L3 / L4  SOURCE-LINKED OR SMOKE", detail: "Qualitative robustness, runtime, parse success, report coverage", color: C.blue },
    { y: 430, w: 630, x: 325, title: "L5  LIMITATION", detail: "Native, hidden DEX, protected or framework boundaries", color: C.violet },
  ].forEach((layer) => {
    box(slide, ctx, layer.x, layer.y, layer.w, 68, C.night2, layer.color);
    text(slide, ctx, layer.title, layer.x + 24, layer.y + 16, 280, 26, { size: 17, color: layer.color, bold: true });
    text(slide, ctx, layer.detail, layer.x + 318, layer.y + 14, layer.w - 342, 38, { size: 13, color: "#BDC8D7", align: "center" });
  });
  rationaleBand(slide, ctx, "Rule", "Never use a smoke or limitation APK to claim precision, recall, or exact-version accuracy.", 540, { dark: true, color: C.coral });
  filePathBand(slide, ctx, "Design source: docs/evaluation/DATASET_DESIGN.md", 630, { dark: true });
  footer(slide, ctx, { dark: true });
  note(slide, "The layered design prevents claim inflation. Controlled and source-validated APKs support quantitative correctness claims. Smoke APKs support robustness claims. Limitation APKs show whether the tool warns honestly. Evidence: docs/evaluation/DATASET_DESIGN.md.");
  return slide;
}

function slideDatasetCollection(presentation, ctx) {
  const slide = presentation.slides.add();
  page(slide, ctx, "Every real APK proof bundle connects binary, source, dependency tree, and report", "Dataset collection", 16, { accent: C.blue });
  const steps = [
    ["1", "Acquire APK", "F-Droid / GitHub release\nrecord SHA-256", C.blue],
    ["2", "Pin source", "matching tag or commit\nverify versionName/code", C.cyan],
    ["3", "Resolve tree", "exact Gradle module +\nruntime configuration", C.violet],
    ["4", "Run MVP", "report + CycloneDX +\nOSV artifacts", C.lime],
    ["5", "Validate", "coordinate/version comparison\nclassify clean or partial", C.gold],
  ];
  steps.forEach((step, i) => {
    const x = 62 + i * 244;
    circle(slide, ctx, x + 76, 166, 54, step[3], "#00000000");
    text(slide, ctx, step[0], x + 76, 184, 54, 18, { size: 13, color: C.white, bold: true, align: "center" });
    box(slide, ctx, x, 244, 206, 220, C.white, step[3]);
    text(slide, ctx, step[1], x + 18, 268, 170, 28, { size: 19, color: step[3], bold: true, align: "center" });
    text(slide, ctx, step[2], x + 18, 326, 170, 64, { size: 13, color: C.ink, align: "center" });
    if (i < steps.length - 1) arrow(slide, ctx, x + 206, 342, 38, step[3]);
  });
  rationaleBand(slide, ctx, "Rescue lesson", "Old Android projects often require validation-only copies, exact module/flavor probing, and legacy Gradle/JDK lanes.", 500, { color: C.gold, fill: C.paleGold });
  filePathBand(slide, ctx, "Workflow: scripts/advance_real_apk_batch_proofs.py  |  Rescue profiles: configs/real_apk_blocker_rescue_profiles.json", 592);
  filePathBand(slide, ctx, "Proof outputs: data/results/source-validation/  |  Classification: data/results/evaluation/apk-type-evaluation.json", 634);
  footer(slide, ctx);
  note(slide, "A real APK is not counted because a source link exists. The proof bundle must identify the exact binary, matching source, resolved runtime dependency tree, generated report, and source-validation output. For difficult builds we used validation-only copies and exact module/configuration probing.");
  return slide;
}

function slideDatasetComposition(presentation, ctx) {
  const slide = presentation.slides.add();
  page(slide, ctx, "The current thesis set combines exact controls, real proof, and explicit boundaries", "Dataset composition", 18, { dark: true, accent: C.cyan });
  metricTile(slide, ctx, "72", "controlled fixtures", 72, 166, 250, C.lime, { dark: true, h: 132, valueSize: 42 });
  metricTile(slide, ctx, "102", "source-validated real APKs", 348, 166, 250, C.cyan, { dark: true, h: 132, valueSize: 42 });
  metricTile(slide, ctx, "5 / 97", "clean / partial real APKs", 624, 166, 250, C.gold, { dark: true, h: 132, valueSize: 38 });
  metricTile(slide, ctx, "4", "limitation or boundary cases", 900, 166, 250, C.violet, { dark: true, h: 132, valueSize: 42 });
  box(slide, ctx, 72, 332, 1078, 220, C.night2, C.lineDark);
  text(slide, ctx, "COVERAGE DIMENSIONS", 96, 356, 220, 22, { size: 12, color: C.cyan, bold: true });
  [
    ["Build", "clear  rename  shrink  optimize  repackage  inline stress", C.blue],
    ["Packaging", "single DEX  multidex  multi-library  native-heavy", C.cyan],
    ["Ecosystem", "AndroidX  Kotlin  Compose  networking  security  legacy", C.gold],
    ["Boundaries", "native .so  hidden DEX  protected/obfuscated samples", C.violet],
  ].forEach((row, i) => {
    text(slide, ctx, row[0], 100, 402 + i * 38, 118, 22, { size: 13, color: row[2], bold: true });
    rule(slide, ctx, 228, 412 + i * 38, 40, 3, row[2]);
    text(slide, ctx, row[1], 286, 398 + i * 38, 820, 28, { size: 14, color: "#C0CAD8" });
  });
  filePathBand(slide, ctx, "Canonical truth: data/results/evaluation/thesis-evaluation-tables.json  |  docs/evaluation/THESIS_EVALUATION_TABLES.md", 598, { dark: true });
  footer(slide, ctx, { dark: true });
  note(slide, "The current generated truth is 72 controlled fixtures, 102 source-validated real APKs split into 5 clean and 97 partial, plus 4 boundary cases. These counts come from data/results/evaluation/thesis-evaluation-tables.json, not the older planning targets.");
  return slide;
}

function slideEvaluationMethod(presentation, ctx) {
  const slide = presentation.slides.add();
  page(slide, ctx, "The methodology measures only what each ground-truth layer can support", "Evaluation methodology", 19, { accent: C.coral });
  [
    ["Controlled", "Expected coordinate + version", "TP / FP / FN / version mismatch", "Precision, recall, F1, exact version", C.lime],
    ["Source-validated", "Resolved runtime dependency tree", "Confirmed / mismatch / missing or nuance", "Emitted Maven version confirmation", C.cyan],
    ["Smoke / limitation", "No complete dependency truth", "Parse success, runtime, warnings, outputs", "Qualitative behavior only", C.violet],
  ].forEach((row, i) => {
    const y = 160 + i * 130;
    box(slide, ctx, 72, y, 1136, 104, C.white, row[4]);
    text(slide, ctx, row[0], 94, y + 18, 160, 28, { size: 19, color: row[4], bold: true });
    text(slide, ctx, row[1], 274, y + 16, 270, 40, { size: 13, color: C.ink, bold: true });
    text(slide, ctx, row[2], 568, y + 16, 300, 42, { size: 13, color: C.muted });
    label(slide, ctx, row[3], 894, y + 26, 282, row[4], { fill: C.paper });
  });
  rationaleBand(slide, ctx, "Required phrase", "The real-APK metric is emitted Maven version confirmation rate, not full dependency recall.", 566, { color: C.coral, fill: C.paleCoral });
  filePathBand(slide, ctx, "Generation: scripts/build_apk_type_evaluation.py  ->  scripts/build_thesis_evaluation_tables.py", 646);
  footer(slide, ctx);
  note(slide, "Be precise about the metric. Controlled fixtures can support full precision/recall/F1 because dependencies are known by construction. Real APKs use the resolved source tree to confirm the versions the tool emitted. That is not full dependency recall.");
  return slide;
}

function slideV2UpperBound(presentation, ctx) {
  const slide = presentation.slides.add();
  page(slide, ctx, "The source-known v2 lane isolates recognition from candidate-selection difficulty", "Upper-bound experiment", 21, { accent: C.gold });
  box(slide, ctx, 72, 154, 532, 400, C.night2, C.night2);
  text(slide, ctx, "WHAT IS CONSTRAINED", 98, 182, 220, 22, { size: 12, color: C.gold, bold: true });
  text(slide, ctx, "Each APK is matched only against coordinate-version rows observed in its resolved source tree.", 98, 230, 454, 82, { size: 22, color: C.white, bold: true });
  ["removes global version-selection noise", "tests bytecode recognition in the correct slice", "keeps non-emitted source rows as a separate denominator"].forEach((item, i) => {
    circle(slide, ctx, 102, 354 + i * 54, 14, i === 2 ? C.coral : C.gold, "#00000000");
    text(slide, ctx, item, 132, 346 + i * 54, 414, 36, { size: 13, color: "#BCC7D5" });
  });
  metricTile(slide, ctx, "106 / 106", "source-tree cases completed", 638, 154, 254, C.cyan, { h: 124, valueSize: 36 });
  metricTile(slide, ctx, "6772 / 6772", "emitted rows exact", 918, 154, 290, C.lime, { h: 124, valueSize: 34 });
  metricTile(slide, ctx, "0", "wrong-version emitted rows", 638, 304, 254, C.blue, { h: 124, valueSize: 40 });
  metricTile(slide, ctx, "5238", "source-gap rows remain", 918, 304, 290, C.coral, { h: 124, valueSize: 38 });
  rationaleBand(slide, ctx, "Interpretation", "This proves bounded recognition when the correct source versions are available; it does not prove unconstrained APK-only accuracy.", 470, { color: C.coral, fill: C.paleCoral, h: 76 });
  filePathBand(slide, ctx, "Evidence: docs/evaluation/DEMO_FINAL_V2_PACKAGE.md  |  data/results/evaluation/real-apk-demo-final-large-v2-source-version-dashboard.json", 580, { size: 9 });
  footer(slide, ctx);
  note(slide, "This is the slide where wording matters most. The v2 lane uses exact source coordinate-version slices, so it answers whether the matcher recognizes correct bytecode when candidate selection is bounded. It does not measure unconstrained APK-only production accuracy.");
  return slide;
}

function slideFailedExperiments(presentation, ctx) {
  const slide = presentation.slides.add();
  page(slide, ctx, "Negative experiments protected the production tool from attractive regressions", "Failed experiments", 24, { dark: true, accent: C.coral });
  const rows = [
    ["API-reference weight", "No metric change", "Keep disabled", C.muted],
    ["Opcode tri-grams", "Regressed OpenTracks + Conversations", "Keep disabled", C.coral],
    ["Global multi-scale blend", "10 target gains; 6 controlled + 121 real blockers", "Reject globally", C.coral],
    ["Coroutines 1.6.4 reference", "20/20 targets fixed; 3 controls regressed", "Experiment only", C.gold],
    ["APK-only reranker", "0 safe fixes across 582 wrong-version rows", "Reject", C.coral],
    ["Candidate expansion", "134 refs selected wrong old Activity version", "Do not promote", C.coral],
    ["Raw opcode Transformer", "0.110 macro-F1 < 0.128 baseline", "Research only", C.violet],
  ];
  rows.forEach((row, i) => {
    const y = 144 + i * 66;
    box(slide, ctx, 72, y, 1136, 50, C.night2, C.lineDark);
    text(slide, ctx, row[0], 92, y + 14, 280, 22, { size: 13, color: C.white, bold: true });
    text(slide, ctx, row[1], 390, y + 11, 500, 28, { size: 12, color: "#B9C4D3" });
    label(slide, ctx, row[2], 940, y + 11, 238, row[3], { fill: C.night });
  });
  rationaleBand(slide, ctx, "Lesson", "Promotion requires target improvement and a clean current-control matrix; novelty alone is not enough.", 620, { dark: true, color: C.coral, h: 46, size: 14 });
  footer(slide, ctx, { dark: true });
  note(slide, "This slide is a strength, not an apology. The project records experiments that looked promising but failed controls. The production matcher stays conservative because target improvements were not allowed to hide regressions. Evidence: docs/thesis/EXPERIMENT_DECISION_LEDGER.md.");
  return slide;
}

function slideAiFormulation(presentation, ctx) {
  const slide = presentation.slides.add();
  page(slide, ctx, "AI predicts evidence roles and risk states, not final Maven versions", "AI problem formulation", 25, { accent: C.violet });
  box(slide, ctx, 72, 154, 520, 404, C.white, C.violet);
  text(slide, ctx, "TRAINING UNIT", 98, 178, 170, 22, { size: 12, color: C.violet, bold: true });
  text(slide, ctx, "One matcher / transparency evidence row", 98, 218, 450, 38, { size: 24, color: C.ink, bold: true });
  [
    ["Rows", "20,523 training eligible"],
    ["Cases", "149 grouped case IDs"],
    ["Coordinates", "1,370 Maven coordinates"],
    ["Split", "104 train / 15 validation / 30 test cases"],
    ["Features", "scores, overlap counts, context flags"],
  ].forEach((row, i) => {
    text(slide, ctx, row[0], 100, 296 + i * 44, 116, 22, { size: 12, color: C.muted, bold: true });
    text(slide, ctx, row[1], 224, 292 + i * 44, 320, 28, { size: 14, color: C.ink, bold: true });
  });
  box(slide, ctx, 624, 154, 584, 404, C.night2, C.night2);
  text(slide, ctx, "SIX LABELS", 650, 178, 170, 22, { size: 12, color: C.cyan, bold: true });
  [
    ["confirmed_exact", C.lime],
    ["suggest_report_only", C.cyan],
    ["suppress_uncertain", C.gold],
    ["risk_only", C.blue],
    ["mismatch_or_extra", C.coral],
    ["boundary_do_not_suggest", C.violet],
  ].forEach((row, i) => {
    const col = i % 2;
    const r = Math.floor(i / 2);
    label(slide, ctx, row[0], 650 + col * 266, 226 + r * 78, 238, row[1], { fill: C.night });
  });
  text(slide, ctx, "Grouped splitting by APK case reduces row-level leakage.", 662, 476, 510, 34, { size: 15, color: C.white, bold: true, align: "center" });
  rationaleBand(slide, ctx, "Authority", "The task is report-only identity/risk triage. Selected versions, SBOM components, and CVE labels remain deterministic.", 588, { color: C.coral, fill: C.paleCoral });
  footer(slide, ctx);
  note(slide, "The AI task is deliberately not exact-version selection. Each row is classified into one of six evidence roles. Splits are grouped by APK case to reduce leakage. The labels and features come from existing matcher, transparency, Phase 5, and boundary artifacts.");
  return slide;
}

function slideRandomForest(presentation, ctx) {
  const slide = presentation.slides.add();
  page(slide, ctx, "RandomForest was selected for explainable, structured, report-only assistance", "Classical ML", 26, { dark: true, accent: C.blue });
  metricTile(slide, ctx, "0.708", "test macro-F1", 72, 154, 230, C.blue, { dark: true, h: 122, valueSize: 40 });
  metricTile(slide, ctx, "0.690", "test accuracy", 326, 154, 230, C.cyan, { dark: true, h: 122, valueSize: 40 });
  metricTile(slide, ctx, "0.383", "majority baseline accuracy", 580, 154, 260, C.gold, { dark: true, h: 122, valueSize: 40 });
  metricTile(slide, ctx, "13,736", "report-only suggestions", 864, 154, 286, C.violet, { dark: true, h: 122, valueSize: 34 });
  box(slide, ctx, 72, 310, 532, 270, C.night2, C.lineDark);
  text(slide, ctx, "WHY RANDOM FOREST", 96, 334, 220, 22, { size: 12, color: C.blue, bold: true });
  [
    "fits the structured numeric evidence already produced",
    "class weighting handles imbalanced labels",
    "feature importance supports defense explanations",
    "fast local training and deterministic grouped split",
  ].forEach((item, i) => {
    circle(slide, ctx, 100, 378 + i * 44, 12, C.blue, "#00000000");
    text(slide, ctx, item, 126, 370 + i * 44, 432, 30, { size: 13, color: "#BCC7D5" });
  });
  box(slide, ctx, 636, 310, 514, 270, C.white, C.white);
  text(slide, ctx, "TOP FEATURES", 660, 334, 190, 22, { size: 12, color: C.violet, bold: true });
  [
    ["identity confidence", 0.231, C.blue],
    ["boundary flag", 0.217, C.coral],
    ["best score", 0.206, C.cyan],
    ["source rank", 0.086, C.gold],
    ["dependency score", 0.068, C.violet],
  ].forEach((row, i) => {
    text(slide, ctx, row[0], 660, 376 + i * 38, 180, 22, { size: 12, color: C.ink, bold: true });
    rect(slide, ctx, 846, 380 + i * 38, 220, 14, "#E1E7EF", "#00000000");
    rect(slide, ctx, 846, 380 + i * 38, 220 * row[1] / 0.25, 14, row[2], "#00000000");
    text(slide, ctx, row[1].toFixed(3), 1074, 374 + i * 38, 54, 22, { size: 11, color: row[2], bold: true, align: "right" });
  });
  filePathBand(slide, ctx, "Implementation: src/apk_sbom/ai_r8_assistant.py  |  Metrics: data/results/experiments/ai-r8-assistant/metrics.json", 612, { dark: true });
  footer(slide, ctx, { dark: true });
  note(slide, "RandomForest was chosen because the evidence is structured and numeric, the model trains quickly, class weights handle imbalance, and feature importance is explainable. The result is 0.708 macro-F1, but suggestions remain report-only.");
  return slide;
}

function slideDeepLearning(presentation, ctx) {
  const slide = presentation.slides.add();
  page(slide, ctx, "The DL lane separates a strong structured-token result from a weak raw-opcode result", "Deep learning", 27, { accent: C.violet });
  box(slide, ctx, 72, 154, 540, 416, C.white, C.violet);
  text(slide, ctx, "MVP-SAFE STRUCTURED TOKENS", 96, 180, 300, 22, { size: 12, color: C.violet, bold: true });
  text(slide, ctx, "0.882", 96, 222, 200, 56, { size: 46, color: C.violet, bold: true, face: ctx.fonts.title });
  text(slide, ctx, "test macro-F1  |  0.907 accuracy", 96, 286, 350, 28, { size: 16, color: C.ink, bold: true });
  [
    "20,523 rows; 1,704-token vocabulary",
    "1-layer TransformerEncoder, d_model 64, 4 heads",
    "removes source version, raw coordinate, source rank, and diagnostic shortcuts",
    "candidate for report-only risk triage",
  ].forEach((item, i) => {
    circle(slide, ctx, 100, 344 + i * 48, 12, C.violet, "#00000000");
    text(slide, ctx, item, 126, 336 + i * 48, 440, 34, { size: 12, color: C.muted });
  });
  box(slide, ctx, 642, 154, 566, 416, C.night2, C.night2);
  text(slide, ctx, "RAW DEX OPCODE TOKENS", 668, 180, 260, 22, { size: 12, color: C.coral, bold: true });
  text(slide, ctx, "0.110", 668, 222, 200, 56, { size: 46, color: C.coral, bold: true, face: ctx.fonts.title });
  text(slide, ctx, "below 0.128 opcode-count baseline", 668, 286, 420, 28, { size: 16, color: C.white, bold: true });
  [
    "1,680 method sequences from 14 APKs",
    "case-heldout split across seven profile labels",
    "raw sequence alone does not generalize",
    "needs more APKs, context, and APK-level aggregation",
  ].forEach((item, i) => {
    circle(slide, ctx, 672, 344 + i * 48, 12, i === 3 ? C.gold : C.coral, "#00000000");
    text(slide, ctx, item, 698, 336 + i * 48, 450, 34, { size: 12, color: "#BDC8D6" });
  });
  rationaleBand(slide, ctx, "Decision", "Keep the structured model as report-only evidence; keep the raw-opcode model as an honest negative result.", 596, { color: C.coral, fill: C.paleCoral });
  footer(slide, ctx);
  note(slide, "The structured-token Transformer is strong even after obvious source shortcuts are removed. The raw-opcode Transformer is much weaker and does not beat a simple baseline under a case-heldout split. This is why the DL story includes both a useful prototype and a negative result.");
  return slide;
}

function slideDemoFlow(presentation, ctx) {
  const slide = presentation.slides.add();
  page(slide, ctx, "The reproducible demo command returns a 10/10 verdict and keeps AI report-only", "Live demo evidence", 29, { dark: true, accent: C.cyan });
  box(slide, ctx, 64, 150, 600, 410, "#101820", C.lineDark);
  rect(slide, ctx, 64, 150, 600, 36, C.night2, "#00000000");
  text(slide, ctx, "PowerShell  |  project .venv", 84, 160, 300, 18, { size: 11, color: C.white, bold: true });
  text(slide, ctx, ".\\.venv\\Scripts\\python.exe scripts\\run_final_ai_defense_demo.py --refresh", 86, 210, 548, 48, { size: 14, color: C.cyan, bold: true, mono: true });
  text(slide, ctx, "{\n  \"checks_passed\": 10,\n  \"checks_total\": 10,\n  \"ready\": true,\n  \"matcher_authority_ready\": false\n}", 86, 276, 548, 150, { size: 15, color: C.white, mono: true });
  rule(slide, ctx, 86, 444, 548, 1, C.lineDark);
  text(slide, ctx, "Model reruns", 86, 460, 180, 22, { size: 12, color: C.gold, bold: true });
  text(slide, ctx, "RandomForest  0.708   |   MVP-safe Transformer  0.882\nRaw opcode Transformer  0.110 < 0.128 baseline", 86, 492, 548, 48, { size: 13, color: "#C4CEDA", bold: true, mono: true });
  screenshot(slide, ctx, "aiReport", 696, 150, 512, 330, {
    alt: "Generated hard Aegis APK report used by the hybrid AI smoke test",
    line: C.violet,
  });
  label(slide, ctx, "Aegis hard APK  |  7 emitted components", 718, 498, 468, C.violet, { fill: C.night2 });
  box(slide, ctx, 696, 544, 512, 82, C.night2, C.coral);
  text(slide, ctx, "GUARDRAIL", 716, 562, 110, 20, { size: 11, color: C.coral, bold: true });
  text(slide, ctx, "AI changes report wording and triage only; selected versions, SBOM components, and CVE labels remain deterministic.", 830, 554, 354, 54, { size: 12, color: C.white, bold: true });
  text(slide, ctx, "Present from saved reports; do not rebuild the 15.8 GB DB during the defense.", 120, 628, 1040, 26, { size: 15, color: C.gold, bold: true, align: "center" });
  footer(slide, ctx, { dark: true });
  note(slide, "This exact command was rerun through the project virtual environment and returned 10 of 10 checks with ready true. The RandomForest, five-epoch MVP-safe Transformer, and raw-opcode Transformer scripts were also rerun; the five-epoch structured model reproduced 0.882165 macro-F1. During the defense, show the saved metrics and reports instead of spending several minutes retraining. Avoid rebuilding the large DB or querying OSV live.");
  return slide;
}

function slideLimitationsFuture(presentation, ctx) {
  const slide = presentation.slides.add();
  page(slide, ctx, "The next research steps follow directly from the remaining evidence gaps", "Limitations and future work", 30, { accent: C.gold });
  const lanes = [
    { x: 72, title: "CURRENT LIMIT", color: C.coral, items: ["adjacent AndroidX/Kotlin versions", "reference coverage gaps", "R8 inlining and removed evidence", "native and hidden-code boundaries"] },
    { x: 430, title: "NEXT ENGINEERING", color: C.blue, items: ["stronger candidate recall and pruning", "version-unique literal/context evidence", "broader guarded reference growth", "faster batch and DB workflows"] },
    { x: 788, title: "NEXT RESEARCH", color: C.violet, items: ["larger independent R8 corpora", "class/package-aware opcode aggregation", "scoped hybrid structural rerankers", "strict APK-only promotion controls"] },
  ];
  lanes.forEach((lane) => {
    box(slide, ctx, lane.x, 164, 326, 388, C.white, lane.color);
    rect(slide, ctx, lane.x, 164, 326, 70, lane.color, "#00000000");
    text(slide, ctx, lane.title, lane.x + 18, 186, 290, 24, { size: 15, color: C.white, bold: true, align: "center" });
    lane.items.forEach((item, i) => {
      circle(slide, ctx, lane.x + 26, 274 + i * 64, 12, lane.color, "#00000000");
      text(slide, ctx, item, lane.x + 52, 264 + i * 64, 246, 44, { size: 13, color: C.ink, bold: true });
    });
  });
  rationaleBand(slide, ctx, "Promotion bar", "A future method becomes authoritative only after nonzero APK-only candidates survive representative exact and boundary controls.", 584, { color: C.violet, fill: "#EEEAFE", h: 64 });
  footer(slide, ctx);
  note(slide, "Future work is evidence-driven. The first priority is version-distinctive and candidate-recall evidence, then broader independent R8 data and stricter APK-only promotion controls. Native and hidden-code recovery remain separate research problems.");
  return slide;
}

function backupModuleMap(presentation, ctx) {
  const slide = presentation.slides.add();
  page(slide, ctx, "The pfe-final repository connects source code, datasets, Docker, databases, and evidence outputs", "Backup 1  |  project structure", 32, { dark: true, accent: C.blue });
  box(slide, ctx, 62, 142, 474, 466, "#101820", C.lineDark);
  text(slide, ctx, "pfe-final/", 86, 166, 220, 24, { size: 16, color: C.cyan, bold: true, mono: true });
  const tree = [
    ["src/apk_sbom/", "production pipeline modules", C.blue],
    ["scripts/", "evaluation, training, demo, DB workflows", C.cyan],
    ["datasets/", "dataset manifests and ground truth", C.lime],
    ["data/test_apks/", "controlled and real APK inputs", C.gold],
    ["data/reference_db/", "SQLite Maven feature databases", C.violet],
    ["data/results/", "SBOM, reports, metrics, screenshots", C.coral],
    ["tests/", "unit and regression controls", C.blue],
    ["docs/", "architecture, evaluation, thesis evidence", C.cyan],
    ["Dockerfile", "toolchain image definition", C.gold],
    ["docker-compose.yml", "bind-mounted reproducible workspace", C.violet],
  ];
  tree.forEach((row, i) => {
    text(slide, ctx, `${i === tree.length - 1 ? "└─" : "├─"} ${row[0]}`, 88, 206 + i * 36, 220, 24, { size: 11, color: row[2], bold: true, mono: true });
    text(slide, ctx, row[1], 312, 206 + i * 36, 194, 24, { size: 10, color: "#B8C3D3" });
  });
  box(slide, ctx, 570, 142, 648, 466, C.night2, C.lineDark);
  text(slide, ctx, "IMPLEMENTATION FLOW", 594, 166, 220, 22, { size: 12, color: C.blue, bold: true });
  [
    ["APK input", "data/test_apks or mounted user APK", C.gold],
    ["Extract + analyze", "apk_extractor.py + dex_analyzer.py", C.blue],
    ["Match", "matcher.py queries reference_features*.sqlite", C.violet],
    ["Emit", "sbom.py + vulnerability.py + report.py", C.cyan],
    ["Validate", "source-validation JSON + evaluation scripts", C.lime],
    ["Preserve evidence", "data/results/... HTML, JSON, CycloneDX, metrics", C.coral],
  ].forEach((row, i) => {
    const y = 210 + i * 60;
    label(slide, ctx, row[0], 594, y, 154, row[2], { fill: C.night });
    arrow(slide, ctx, 756, y + 2, 44, row[2]);
    text(slide, ctx, row[1], 810, y + 2, 374, 28, { size: 11, color: C.white, bold: true });
  });
  filePathBand(slide, ctx, "Core modules: apk_extractor.py  dex_analyzer.py  reference_features.py  matcher.py  sbom.py  vulnerability.py  report.py", 628, { dark: true });
  footer(slide, ctx, { dark: true });
  note(slide, "Use this slide when asked how the repository is organized. It shows the complete path from APK inputs and Maven reference databases through production modules, evaluation scripts, tests, Docker, and generated evidence under data/results.");
  return slide;
}

function backupMatcherWeights(presentation, ctx) {
  const slide = presentation.slides.add();
  page(slide, ctx, "Exact matcher signals, default weights, and guarded signals", "Backup 2", 33, { accent: C.lime });
  const weights = [
    ["Class", 0.45, C.blue],
    ["Method", 0.25, C.cyan],
    ["Package", 0.15, C.lime],
    ["Opcode", 0.15, C.violet],
    ["Unique version", 0.12, C.gold],
    ["Dependency", 0.10, C.blue],
    ["Literal", 0.08, C.coral],
  ];
  weights.forEach((row, i) => {
    const y = 152 + i * 58;
    text(slide, ctx, row[0], 84, y + 4, 180, 22, { size: 14, color: C.ink, bold: true });
    rect(slide, ctx, 272, y + 7, 520, 18, "#DFE6EF", "#00000000");
    rect(slide, ctx, 272, y + 7, 520 * row[1] / 0.45, 18, row[2], "#00000000");
    text(slide, ctx, row[1].toFixed(2), 810, y, 60, 28, { size: 16, color: row[2], bold: true, align: "right" });
  });
  box(slide, ctx, 902, 152, 306, 218, C.paleCoral, C.coral);
  text(slide, ctx, "DISABLED GLOBALLY", 924, 176, 262, 22, { size: 12, color: C.coral, bold: true, align: "center" });
  text(slide, ctx, "API-reference weight  0.00\nOpcode tri-gram weight  0.00", 924, 226, 262, 70, { size: 17, color: C.ink, bold: true, align: "center" });
  text(slide, ctx, "Implemented for diagnostics, but current controls do not justify global scoring.", 930, 316, 250, 38, { size: 11, color: C.muted, align: "center" });
  box(slide, ctx, 902, 398, 306, 168, C.paleGold, C.gold);
  text(slide, ctx, "TIE THRESHOLDS", 924, 420, 262, 22, { size: 12, color: C.gold, bold: true, align: "center" });
  text(slide, ctx, "feature-equivalent <= 0.001\nnear tie <= 0.006\nnear-tie score floor 0.35", 924, 458, 262, 76, { size: 14, color: C.ink, bold: true, align: "center", mono: true });
  filePathBand(slide, ctx, "Source: src/apk_sbom/matcher.py constants and score_reference_component()", 610);
  footer(slide, ctx);
  note(slide, "Weights are evidence contributions, not probabilities, and some policies can adjust the final decision. The most important defense point is that optional API-reference and opcode tri-gram weights remain zero globally.");
  return slide;
}

function backupReferenceStats(presentation, ctx) {
  const slide = presentation.slides.add();
  page(slide, ctx, "Docker packages the complete Android analysis toolchain while data and outputs stay reproducible", "Backup 3  |  Docker implementation", 34, { dark: true, accent: C.cyan });
  metricTile(slide, ctx, "10,517", "reference coordinate-version rows", 64, 148, 232, C.cyan, { dark: true, h: 112, valueSize: 34 });
  metricTile(slide, ctx, "15.8 GB", "final v2 SQLite database", 314, 148, 232, C.violet, { dark: true, h: 112, valueSize: 34 });
  metricTile(slide, ctx, "/app", "container working directory", 564, 148, 232, C.gold, { dark: true, h: 112, valueSize: 34 });
  metricTile(slide, ctx, ".:/app", "Compose bind mount", 814, 148, 232, C.lime, { dark: true, h: 112, valueSize: 34 });
  metricTile(slide, ctx, "/app/src", "PYTHONPATH", 1064, 148, 154, C.blue, { dark: true, h: 112, valueSize: 23 });
  box(slide, ctx, 64, 288, 550, 292, C.night2, C.lineDark);
  text(slide, ctx, "DOCKERFILE TOOLCHAIN", 88, 312, 240, 22, { size: 12, color: C.cyan, bold: true });
  [
    "Python 3.12 + project requirements",
    "JDK 11 + default JDK",
    "Android SDK, build-tools 36 + legacy 29, D8",
    "Gradle 9.5 plus compatibility versions",
    "Syft, Grype, Trivy, CycloneDX CLI, cdxgen",
    "Source copied to /app; default command checks toolchain",
  ].forEach((item, i) => {
    circle(slide, ctx, 92, 356 + i * 34, 10, i < 4 ? C.cyan : C.gold, "#00000000");
    text(slide, ctx, item, 116, 348 + i * 34, 458, 24, { size: 11, color: "#C0CBD8", bold: true });
  });
  box(slide, ctx, 644, 288, 574, 292, C.white, C.white);
  text(slide, ctx, "REPRODUCIBLE ARTIFACT FLOW", 670, 312, 260, 22, { size: 12, color: C.violet, bold: true });
  [
    ["Host inputs", "data/test_apks  +  datasets", C.gold],
    ["Host reference", "data/reference_db/*.sqlite", C.violet],
    ["Container execution", "docker compose run --rm apk-sbom ...", C.blue],
    ["Host outputs", "data/results/... report.html, JSON, SBOM", C.cyan],
    ["Regression proof", "tests + source-validation + metrics", C.lime],
  ].forEach((row, i) => {
    label(slide, ctx, row[0], 670, 354 + i * 43, 154, row[2], { fill: C.white });
    text(slide, ctx, row[1], 842, 356 + i * 43, 340, 24, { size: 11, color: C.ink, bold: true, mono: i >= 2 });
  });
  filePathBand(slide, ctx, "Files: Dockerfile  |  docker-compose.yml  |  .dockerignore  |  data/reference_db/  |  data/results/", 612, { dark: true });
  footer(slide, ctx, { dark: true });
  note(slide, "The Docker image contains the Android and SBOM toolchain, while Compose bind-mounts the repository at /app so APK inputs, the 15.8 GB reference DB, and generated results remain visible and reusable on the host. The .dockerignore excludes large result, DB, source, and APK directories from the image build context; they are supplied through the bind mount.");
  return slide;
}

function backupApkFamilies(presentation, ctx) {
  const slide = presentation.slides.add();
  page(slide, ctx, "Detailed APK-family classification", "Backup 4", 35, { accent: C.gold });
  const families = [
    ["Clear", "names and code preserved", "exact/high expected", C.lime],
    ["R8 rename", "identifiers rewritten", "structure should survive", C.blue],
    ["R8 shrink", "unused code removed", "lower evidence volume", C.cyan],
    ["R8 optimize", "calls and methods rewritten", "version evidence stressed", C.violet],
    ["Repackage", "namespace flattened", "package signal weakened", C.gold],
    ["Multidex", "several classes*.dex", "all DEX files analyzed", C.blue],
    ["Native-heavy", "many .so files", "hash-only native components", C.coral],
    ["Hidden/protected", "nonstandard DEX or opaque payload", "risk warning, no false Maven claim", C.coral],
  ];
  families.forEach((row, i) => {
    const col = i % 2;
    const r = Math.floor(i / 2);
    const x = 72 + col * 572;
    const y = 146 + r * 112;
    box(slide, ctx, x, y, 540, 88, C.white, row[3]);
    text(slide, ctx, row[0], x + 18, y + 18, 130, 24, { size: 17, color: row[3], bold: true });
    text(slide, ctx, row[1], x + 154, y + 14, 180, 42, { size: 12, color: C.ink, bold: true });
    text(slide, ctx, row[2], x + 346, y + 14, 170, 42, { size: 12, color: C.muted, align: "center" });
  });
  filePathBand(slide, ctx, "Source: docs/evaluation/APK_TYPE_EVALUATION.md  |  data/results/evaluation/apk-type-evaluation.json", 610);
  footer(slide, ctx);
  note(slide, "Use this slide when asked how APK types change expected behavior. The classifier is part of the evaluation interpretation, not an excuse to hide failures.");
  return slide;
}

function backupSourceGapTaxonomy(presentation, ctx) {
  const slide = presentation.slides.add();
  page(slide, ctx, "Source-gap taxonomy separates explanation from actionable matcher work", "Backup 5", 36, { dark: true, accent: C.violet });
  const rows = [
    ["Exact in DB and emitted", "898", "recognized output subset", C.lime],
    ["Exact version in DB", "5,874", "reference exists; not all rows emit", C.cyan],
    ["Artifact-family alias", "1,504", "public/target coordinate overlap", C.blue],
    ["Metadata-only", "734", "BOM or source metadata without bytecode", C.muted],
    ["Source boundary", "277", "native/framework/build-only boundary", C.violet],
    ["Matcher-recall gap", "2,281", "reference exists; matcher did not emit", C.gold],
    ["Missing coordinate/version", "442", "reference growth candidate", C.coral],
    ["Missing coordinate", "72", "coordinate absent entirely", C.coral],
  ];
  rows.forEach((row, i) => {
    const y = 140 + i * 58;
    box(slide, ctx, 72, y, 1136, 44, C.night2, C.lineDark);
    text(slide, ctx, row[0], 92, y + 11, 320, 22, { size: 12, color: row[3], bold: true });
    text(slide, ctx, row[1], 438, y + 8, 110, 26, { size: 17, color: row[3], bold: true, align: "right" });
    text(slide, ctx, row[2], 588, y + 10, 586, 22, { size: 12, color: "#BCC7D5" });
  });
  rationaleBand(slide, ctx, "Actionable", "2,281 matcher-recall rows and 442 missing-reference rows require different engineering responses.", 618, { dark: true, color: C.gold, h: 48 });
  footer(slide, ctx, { dark: true });
  note(slide, "This taxonomy prevents the 5,238 source-gap rows from being mislabeled as one kind of failure. Some are aliases or metadata-only; 2,281 are matcher recall and 442 are missing-reference candidates.");
  return slide;
}

function backupRegressionMatrix(presentation, ctx) {
  const slide = presentation.slides.add();
  page(slide, ctx, "Failed-experiment regression matrix", "Backup 6", 37, { accent: C.coral });
  const rows = [
    ["Global Phase 4 blend", "+10 target opportunities", "6 controlled, 121 real, 10 clean blockers", "Reject global"],
    ["Phase 5 scoped trigger", "4 target improvements", "0 triggered regression/conflict", "Experiment only"],
    ["Coroutines 1.6.4", "20/20 targets fixed", "1 clean + 2 boundary regressions", "Reject shared DB"],
    ["API ref weight 0.05", "No measured benefit", "No metric change", "Disabled"],
    ["Opcode tri-gram 0.02", "No confirmed improvement", "OpenTracks + Conversations regress", "Disabled"],
    ["APK-only reranker", "0 changes", "0 fixes; source alternative visible 7.6%", "Reject"],
    ["Candidate expansion", "134 same-coordinate refs", "selected 1.2.0-alpha01 vs source 1.8.1", "Reject"],
  ];
  rows.forEach((row, i) => {
    const y = 142 + i * 66;
    box(slide, ctx, 72, y, 1136, 52, C.white, i === 1 ? C.gold : C.coral);
    text(slide, ctx, row[0], 90, y + 15, 240, 22, { size: 12, color: C.ink, bold: true });
    text(slide, ctx, row[1], 346, y + 12, 260, 28, { size: 11, color: i === 1 ? C.gold : C.cyan, bold: true });
    text(slide, ctx, row[2], 624, y + 10, 344, 32, { size: 11, color: C.muted });
    label(slide, ctx, row[3], 988, y + 12, 198, i === 1 ? C.gold : C.coral, { fill: i === 1 ? C.paleGold : C.paleCoral });
  });
  footer(slide, ctx);
  note(slide, "The scoped Phase 5 trigger is the interesting middle ground: it retained four improvements without triggered regressions, but it stays experiment-only because the profiles are narrow and learned from a small candidate set.");
  return slide;
}

function backupRandomForest(presentation, ctx) {
  const slide = presentation.slides.add();
  page(slide, ctx, "RandomForest confusion and ablation evidence", "Backup 7", 38, { dark: true, accent: C.blue });
  box(slide, ctx, 72, 146, 548, 438, C.night2, C.lineDark);
  text(slide, ctx, "TEST PER-CLASS F1", 96, 170, 220, 22, { size: 12, color: C.blue, bold: true });
  [
    ["confirmed_exact", 1.000, C.lime],
    ["suggest_report_only", 1.000, C.cyan],
    ["suppress_uncertain", 0.912, C.gold],
    ["boundary_do_not_suggest", 0.803, C.violet],
    ["risk_only", 0.352, C.blue],
    ["mismatch_or_extra", 0.179, C.coral],
  ].forEach((row, i) => {
    text(slide, ctx, row[0], 98, 216 + i * 50, 210, 22, { size: 11, color: C.white, bold: true });
    rect(slide, ctx, 318, 220 + i * 50, 220, 14, "#26344D", "#00000000");
    rect(slide, ctx, 318, 220 + i * 50, 220 * row[1], 14, row[2], "#00000000");
    text(slide, ctx, row[1].toFixed(3), 548, 214 + i * 50, 48, 22, { size: 10, color: row[2], bold: true, align: "right" });
  });
  box(slide, ctx, 650, 146, 558, 438, C.white, C.white);
  text(slide, ctx, "ABLATION MACRO-F1", 674, 170, 220, 22, { size: 12, color: C.violet, bold: true });
  [
    ["all features", 0.708, C.blue],
    ["no overlap counts", 0.710, C.cyan],
    ["no context flags", 0.564, C.gold],
    ["scores only", 0.558, C.violet],
    ["overlap counts only", 0.176, C.coral],
    ["context flags only", 0.162, C.coral],
  ].forEach((row, i) => {
    text(slide, ctx, row[0], 674, 216 + i * 50, 180, 22, { size: 12, color: C.ink, bold: true });
    rect(slide, ctx, 860, 220 + i * 50, 250, 14, "#DFE6EF", "#00000000");
    rect(slide, ctx, 860, 220 + i * 50, 250 * row[1], 14, row[2], "#00000000");
    text(slide, ctx, row[1].toFixed(3), 1120, 214 + i * 50, 54, 22, { size: 10, color: row[2], bold: true, align: "right" });
  });
  filePathBand(slide, ctx, "Metrics: data/results/experiments/ai-r8-assistant/metrics.json", 616, { dark: true });
  footer(slide, ctx, { dark: true });
  note(slide, "The model is excellent on exact and report-only labels but weaker on broad risk and mismatch categories. The ablation shows that no single feature family explains the result; the full structured evidence is useful, but the model remains diagnostic.");
  return slide;
}

function backupTransformer(presentation, ctx) {
  const slide = presentation.slides.add();
  page(slide, ctx, "Transformer corpus, split, and per-class results", "Backup 8", 39, { accent: C.violet });
  metricTile(slide, ctx, "20,523", "MVP-safe structured rows", 72, 146, 246, C.violet, { h: 116, valueSize: 36 });
  metricTile(slide, ctx, "1,704", "structured-token vocabulary", 342, 146, 246, C.blue, { h: 116, valueSize: 36 });
  metricTile(slide, ctx, "1,680", "raw method opcode sequences", 612, 146, 246, C.coral, { h: 116, valueSize: 36 });
  metricTile(slide, ctx, "14", "APKs in raw-opcode corpus", 882, 146, 246, C.gold, { h: 116, valueSize: 40 });
  box(slide, ctx, 72, 292, 540, 276, C.white, C.violet);
  text(slide, ctx, "MVP-SAFE TEST F1", 96, 316, 220, 22, { size: 12, color: C.violet, bold: true });
  [
    ["confirmed exact", 1.000, C.lime],
    ["suggest report-only", 0.974, C.cyan],
    ["suppress uncertain", 0.909, C.gold],
    ["risk only", 0.880, C.blue],
    ["mismatch / extra", 0.766, C.coral],
    ["boundary", 0.764, C.violet],
  ].forEach((row, i) => {
    text(slide, ctx, row[0], 98, 358 + i * 32, 170, 20, { size: 10, color: C.ink, bold: true });
    rect(slide, ctx, 274, 362 + i * 32, 246, 12, "#DFE6EF", "#00000000");
    rect(slide, ctx, 274, 362 + i * 32, 246 * row[1], 12, row[2], "#00000000");
    text(slide, ctx, row[1].toFixed(3), 526, 354 + i * 32, 56, 22, { size: 9, color: row[2], bold: true, align: "right" });
  });
  box(slide, ctx, 642, 292, 566, 276, C.night2, C.night2);
  text(slide, ctx, "RAW OPCODE CASE-HELDOUT", 668, 316, 270, 22, { size: 12, color: C.coral, bold: true });
  text(slide, ctx, "Train 665  |  Validation 175  |  Test 840", 668, 354, 480, 26, { size: 15, color: C.white, bold: true });
  text(slide, ctx, "7 labels  |  120 test sequences per label", 668, 394, 480, 26, { size: 14, color: "#BEC9D7" });
  text(slide, ctx, "Transformer macro-F1  0.110", 668, 448, 300, 26, { size: 18, color: C.coral, bold: true });
  text(slide, ctx, "Opcode-count baseline  0.128", 668, 488, 300, 26, { size: 18, color: C.gold, bold: true });
  label(slide, ctx, "research-only", 990, 454, 170, C.coral, { fill: C.night });
  filePathBand(slide, ctx, "Metrics: metrics-mvp-safe.json  |  ai-r8-raw-opcode-prototype/metrics.json", 610);
  footer(slide, ctx);
  note(slide, "The structured model performs well across all six report labels. The raw opcode corpus uses a stricter case-heldout setup but is still too small: only two APK cases per label, one held out for test. This supports the next-data requirement.");
  return slide;
}

const slides = [
  slide01,
  slide02,
  slide03,
  slide04,
  slideWhyArchitecture,
  (presentation, ctx) => slide05(presentation, ctx, 6),
  slideApkExtractor,
  slideDexAnalyzer,
  slideReferenceDb,
  slideMatcherEvolution,
  slideConfidenceEvolution,
  slideSbomEvolution,
  slideCveEvolution,
  slideReportingEvolution,
  slideLayeredDataset,
  slideDatasetCollection,
  (presentation, ctx) => slide08(presentation, ctx, 17),
  slideDatasetComposition,
  slideEvaluationMethod,
  (presentation, ctx) => slide09(presentation, ctx, 20),
  slideV2UpperBound,
  (presentation, ctx) => slide11(presentation, ctx, 22),
  (presentation, ctx) => slide10(presentation, ctx, 23),
  slideFailedExperiments,
  slideAiFormulation,
  slideRandomForest,
  slideDeepLearning,
  (presentation, ctx) => slide12(presentation, ctx, 28),
  slideDemoFlow,
  slideLimitationsFuture,
  slide13,
  backupModuleMap,
  backupMatcherWeights,
  backupReferenceStats,
  backupApkFamilies,
  backupSourceGapTaxonomy,
  backupRegressionMatrix,
  backupRandomForest,
  backupTransformer,
];

export async function drawSlide(presentation, ctx, number) {
  return slides[number - 1](presentation, ctx);
}
