# Final Demo Runbook V2

Use this runbook for the final supervisor/demo flow. It is designed to show a useful APK-to-SBOM MVP without overclaiming APK-only accuracy.

## One-Minute Opening

Say this first:

```text
This tool starts from a compiled Android APK, extracts static bytecode and package evidence, compares it against a Maven reference DB, emits CycloneDX SBOM output, and labels vulnerability findings with evidence strength. The final v2 package has two layers: the normal APK-only/source-validated metric, and a separate source-version constrained upper-bound lane that makes reference coverage and matcher recall transparent.
```

Do not say:

```text
The tool has 100% real-world APK accuracy.
```

The correct v2 claim is:

```text
In the source-version constrained v2 evaluation lane, all 6772 emitted rows across 106 source-tree APK cases were exact source confirmations, with zero wrong-version emitted rows and zero missing emitted rows. This is an upper-bound lane under known source versions, not unconstrained APK-only accuracy.
```

## Open These Files

Open these artifacts in this order:

| Step | File | What to show |
|---:|---|---|
| 1 | `docs/evaluation/FINAL_DEMO_CHECKLIST.md` | Day-of-defense checklist, deck path, exact numbers, and safe/unsafe commands. |
| 2 | `docs/evaluation/DEMO_FINAL_V2_PACKAGE.md` | The current package index and headline numbers. |
| 3 | `docs/thesis/FINAL_V2_RESULTS_SECTION.md` | Thesis-ready wording that separates normal metrics from the v2 upper-bound lane. |
| 4 | `docs/evaluation/DEMO_FINAL_TRANSPARENCY_REPORT.md` | Dataset/source/emitted/vulnerability classifications. |
| 5 | `docs/evaluation/DEMO_FINAL_LARGE_V2_SOURCE_VERSION_EVALUATION.md` | The 106-case v2 rerun result. |
| 6 | `docs/evaluation/DEMO_FINAL_LARGE_V2_SOURCE_GAP_TRIAGE.md` | Why remaining source dependencies are not simply hidden false negatives. |
| 7 | `docs/evaluation/DEMO_FINAL_V2_MATCHER_RECALL_DIAGNOSTICS.md` | The remaining matcher-recall work and report-only suggestions. |
| 8 | `docs/evaluation/DEMO_FINAL_MVP_READINESS.md` | Final readiness summary and honest boundary language. |

For the live SBOM/CVE portion, open:

| Demo | File |
|---|---|
| Clean real APK report | `data/results/report-real-f-droid-final-demo-osv/report.html` |
| Clean real APK SBOM | `data/results/report-real-f-droid-final-demo-osv/sbom.cdx.json` |
| Clean source validation | `data/results/source-validation/fdroid-final-demo-osv/source-validation.md` |
| Controlled vulnerable report | `data/results/demo-osv-vulnerable-jackson-databind/report.html` |
| Real APK vulnerability triage | `docs/evaluation/OSV_SOURCE_VALIDATION_TRIAGE.md` |

## Storyboard

### 1. APK-To-SBOM Pipeline

Show the clean F-Droid report and SBOM:

```text
data/results/report-real-f-droid-final-demo-osv/report.html
data/results/report-real-f-droid-final-demo-osv/sbom.cdx.json
```

Explain:

- input is a compiled APK;
- output is a CycloneDX SBOM;
- Maven PURLs and confidence/evidence properties are included;
- source validation confirms the emitted components for this clean case.

### 2. CVE Lookup Works, But Confidence Matters

Show the vulnerable controlled Jackson report:

```text
data/results/demo-osv-vulnerable-jackson-databind/report.html
```

Expected talking point:

```text
The controlled vulnerable fixture detects jackson-databind 2.9.10.8 and returns three confirmed HIGH advisories: CVE-2020-36518, CVE-2022-42003, and CVE-2022-42004.
```

Then show:

```text
docs/evaluation/OSV_SOURCE_VALIDATION_TRIAGE.md
```

Explain:

```text
For real APKs, vulnerability rows are separated into source-confirmed, source-version-mismatch, potential, and report-only evidence. This prevents a weak or ambiguous version from becoming a fake confirmed CVE.
```

### 3. Normal Real-APK Result

Use the thesis evaluation table for the standard metric:

```text
docs/evaluation/THESIS_EVALUATION_TABLES.md
```

Say:

```text
The normal source-validated real-APK metric is emitted Maven version confirmation rate. Across all 102 source-validated real APKs, 927 of 1837 emitted Maven versions are confirmed. This is not full dependency recall.
```

### 4. Final V2 Upper-Bound Lane

Open:

```text
docs/evaluation/DEMO_FINAL_V2_PACKAGE.md
```

Say:

```text
After growing the reference DB transparently, I reran the 106 source-tree APK cases in a source-version constrained lane. Every emitted row in that bounded lane was exact: 6772 checked, 6772 confirmed, 0 wrong versions, 0 missing emitted rows.
```

Then immediately add:

```text
This is not APK-only production accuracy. It is a source-known upper-bound lane that tells us the pipeline can recognize and report exact rows when the correct source versions are provided in the per-APK reference slice.
```

### 5. Transparency And Remaining Work

Open:

```text
docs/evaluation/DEMO_FINAL_TRANSPARENCY_REPORT.md
```

Use these numbers:

| Category | Rows |
|---|---:|
| Source dependency rows | 12082 |
| Emitted exact rows in v2 lane | 6772 |
| Source-gap rows | 5238 |
| Explained/boundary source-gap rows | 2515 |
| Actionable source-gap rows | 2723 |
| Missing-reference candidates | 442 |
| Matcher-recall candidates | 2281 |
| Matcher report-only suggestions | 1425 |

Explain:

```text
The remaining denominator is visible. Some rows are metadata/source-only or alias boundaries, some still need reference artifacts, and many already exist in the DB but need matcher recall improvements. That is why this is transparent rather than cherry-picked.
```

### 6. Optional AI-Assisted R8 Triage

Open:

```text
docs/evaluation/AI_R8_ASSISTANT_SUMMARY.md
docs/evaluation/AI_R8_REPORT_ONLY_DEMO.md
```

Say:

```text
After the transparent v2 evaluation, I added a report-only AI layer for hard R8 and matcher-recall triage. It trains a RandomForest on 20,523 existing evaluation rows and reaches 0.708 test macro-F1, but it is not allowed to change selected versions, SBOM components, CVE labels, or source-validation metrics.
```

Then add:

```text
The demo proof runs the same APK with and without AI suggestions. The AI report section appears, but detected components and normalized SBOM content stay unchanged.
```

## If They Ask Hard Questions

| Question | Short answer |
|---|---|
| Is the 100% v2 number real accuracy? | It is real for the source-version constrained lane, but it is not APK-only production accuracy. It is an upper-bound recognition test under known source versions. |
| Why is normal real-APK accuracy only 50.5% then? | Because the normal metric validates APK-only emitted components against source trees across hard APKs. The v2 lane changes the evaluation condition by constraining the reference slice to source-known versions. |
| Is this cheating? | No. The thesis reports both denominators: normal emitted-version confirmation and the full source dependency denominator. Missing/reference/matcher gaps are exported row by row. |
| Why not just add every missing dependency? | Some are metadata-only, source-only, aliases, project modules, or unavailable artifacts. Of the current source gaps, only 442 are remaining missing-reference candidates; 2281 are matcher-recall candidates. |
| Why not promote the 1425 matcher suggestions into the SBOM? | They are source-context report-only suggestions. They need separate APK-only controls before becoming default SBOM components. |
| Is the AI model now choosing versions? | No. It is report-only triage. It can suggest wording or review priority, but it cannot change selected versions, SBOM components, vulnerability labels, or metrics. |
| What is the next technical improvement? | Matcher recall and safe pruning/reranking, not blind DB growth. |

## Live Commands Only If Needed

The final demo can be shown from existing artifacts. Do not rebuild the DB live.

Optional health check:

```powershell
docker compose run --rm apk-sbom pytest -q
```

Optional regeneration of the transparency export:

```powershell
python scripts\build_demo_final_transparency_export.py
```

Optional regeneration of the thesis artifact index:

```powershell
python scripts\build_thesis_artifact_index.py
```

Avoid rerunning the full 106-APK v2 evaluation live. It took hours and writes large per-case slice artifacts.

## Closing Line

Use this as the final sentence:

```text
The MVP is not perfect, but it is useful and honest: it produces CycloneDX SBOM evidence from APKs, validates what it can, labels uncertainty, and exports the remaining gaps instead of hiding them.
```
