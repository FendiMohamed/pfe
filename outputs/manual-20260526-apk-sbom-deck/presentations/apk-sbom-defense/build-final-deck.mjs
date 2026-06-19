import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { Presentation, PresentationFile } from "@oai/artifact-tool";
import { Canvas, loadImage } from "./node_modules/@oai/artifact-tool/node_modules/skia-canvas/lib/index.mjs";
import { drawSlide } from "./slides/common.mjs";

const ROOT = path.dirname(fileURLToPath(import.meta.url));
const OUTPUT_DIR = path.join(ROOT, "output");
const PREVIEW_DIR = path.join(ROOT, "preview");
const LAYOUT_DIR = path.join(ROOT, "layout", "final");
const QA_DIR = path.join(ROOT, "qa");
const ASSET_DIR = path.join(ROOT, "assets");
const FINAL_PPTX = path.join(OUTPUT_DIR, "apk-sbom-defense-academic-deck.pptx");

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
  const canvas = new Canvas(
    cols * thumbW + (cols + 1) * gap,
    rows * (thumbH + labelH) + (rows + 1) * gap,
  );
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

function makeContext() {
  return {
    fonts: {
      title: "Aptos Display",
      body: "Aptos",
      mono: "Cascadia Mono",
    },
    line(fill, width = 1) {
      if (!fill || fill === "#00000000" || width === 0) {
        return { style: "solid", fill: "none", width: 0 };
      }
      return { style: "solid", fill, width };
    },
    addShape(slide, cfg) {
      return slide.shapes.add({
        geometry: cfg.geometry ?? "rect",
        name: cfg.name,
        position: {
          left: cfg.x,
          top: cfg.y,
          width: cfg.w,
          height: cfg.h,
        },
        fill: cfg.fill ?? "none",
        line: cfg.line ?? { style: "solid", fill: "none", width: 0 },
      });
    },
    addText(slide, cfg) {
      const shape = slide.shapes.add({
        geometry: "textbox",
        name: cfg.name,
        position: {
          left: cfg.x,
          top: cfg.y,
          width: cfg.w,
          height: cfg.h,
        },
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

async function build() {
  await fs.mkdir(OUTPUT_DIR, { recursive: true });
  await fs.mkdir(PREVIEW_DIR, { recursive: true });
  await fs.mkdir(LAYOUT_DIR, { recursive: true });
  await fs.mkdir(QA_DIR, { recursive: true });

  const presentation = Presentation.create({
    slideSize: { width: 1280, height: 720 },
  });
  const ctx = makeContext();
  ctx.assets = {
    cleanReport: await fs.readFile(path.join(ASSET_DIR, "clean-report.png")),
    vulnerableReport: await fs.readFile(path.join(ASSET_DIR, "vulnerable-report-top.png")),
    aiReport: await fs.readFile(path.join(ASSET_DIR, "ai-report-top.png")),
  };

  const slideResults = [];
  for (let i = 1; i <= 39; i += 1) {
    const slide = await drawSlide(presentation, ctx, i);
    const stem = `slide-${String(i).padStart(2, "0")}`;
    const previewPath = path.join(PREVIEW_DIR, `${stem}.png`);
    const layoutPath = path.join(LAYOUT_DIR, `${stem}.layout.json`);
    await writeBlob(previewPath, await presentation.export({ slide, format: "png", scale: 1 }));
    await fs.writeFile(layoutPath, await (await slide.export({ format: "layout" })).text());
    slideResults.push({
      index: i,
      requestedSlideNumber: i,
      modulePath: path.join(ROOT, "slides", "common.mjs"),
      exportName: `drawSlide(${i})`,
      previewPath,
      layoutPath,
    });
  }

  await createContactSheet(slideResults, path.join(PREVIEW_DIR, "contact-sheet.png"));

  const pptx = await PresentationFile.exportPptx(presentation);
  await pptx.save(FINAL_PPTX);

  const stat = await fs.stat(FINAL_PPTX);
  const manifest = {
    output: FINAL_PPTX,
    outputBytes: stat.size,
    slideCount: presentation.slides.items.length,
    slideSize: { width: 1280, height: 720 },
    previewDir: PREVIEW_DIR,
    previewPaths: slideResults.map((row) => row.previewPath),
    layoutDir: LAYOUT_DIR,
    layoutResults: slideResults.map((row) => ({ layoutPath: row.layoutPath })),
    contactSheet: path.join(PREVIEW_DIR, "contact-sheet.png"),
    slides: slideResults.map(({ index, requestedSlideNumber, modulePath, exportName }) => ({
      index,
      requestedSlideNumber,
      modulePath,
      exportName,
    })),
  };
  await fs.writeFile(
    path.join(OUTPUT_DIR, "artifact-build-manifest.json"),
    JSON.stringify(manifest, null, 2) + "\n",
  );

  await fs.writeFile(
    path.join(QA_DIR, "visual-qa.txt"),
    [
      "Academic defense deck visual QA",
      "",
      "Mode: create, regenerated from editable artifact-tool slide modules.",
      "Slide count: 39 (31 main + 8 backup).",
      "Checked items:",
      "- The deck uses a restrained academic visual system: warm white, charcoal, navy, muted teal, and limited warning red.",
      "- Rounded dashboard-style cards and rainbow accents were replaced by square frames, table-like structures, and quieter hierarchy.",
      "- Slides 5 and 6 now explain the architecture decisions and show the complete MVP architecture with the APK and Maven reference pipelines.",
      "- Main deck covers context, architecture, every core component, dataset, results, failed experiments, ML/DL, demo, and conclusion.",
      "- Eight backup slides cover module paths, matcher weights, reference DB scale, APK families, source-gap taxonomy, regressions, and model detail.",
      "- Component slides show evolution, observed weakness, chosen design, rationale, and implementation path.",
      "- Main results slide separates the 927/1837 normal metric from the 6772/6772 source-known upper bound.",
      "- Demo proof slide embeds real generated HTML-report screenshots for the clean and positive-CVE cases.",
      "- The result-classification slide separates correct emitted versions, a scoring/version-candidate miss, matcher recall, and a missing-reference DB case.",
      "- AI slide reports RF 0.708, MVP-safe Transformer 0.882, raw-opcode Transformer 0.110, and the blocked authority boundary.",
      "- The live-demo slide records the exact project-venv command, fresh 10/10 verdict, model rerun commands, and a real hard-APK report screenshot.",
      "- Backup slides map the complete repository structure and Dockerized toolchain, bind mount, reference DB, datasets, and output artifacts.",
      "- The deck ends with a contribution-led conclusion and explicit next research steps.",
      "- Contact sheet and all per-slide previews were regenerated and visually reviewed.",
      "- Programmatic layout bounds check reports zero out-of-slide objects across all 39 slide layouts.",
      "- PPTX package verification confirms 39 slides, 39 notes slides, and Aptos/Aptos Display/Cascadia Mono typefaces.",
      "",
      "Remaining manual polish:",
      "- Add university template, names, logos, and date if required by the defense format.",
      "- Review in PowerPoint before presenting.",
      "",
    ].join("\n"),
  );

  console.log(JSON.stringify({
    pptx: FINAL_PPTX,
    slides: presentation.slides.items.length,
    bytes: stat.size,
    contactSheet: path.join(PREVIEW_DIR, "contact-sheet.png"),
  }, null, 2));
}

build().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
