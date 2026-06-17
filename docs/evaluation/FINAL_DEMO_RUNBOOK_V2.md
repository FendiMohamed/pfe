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
docs/evaluation/AI_R8_FINAL_EVALUATION.md
docs/evaluation/AI_R8_INDEPENDENT_CORPUS.md
docs/evaluation/AI_R8_RAW_OPCODE_CORPUS.md
docs/evaluation/AI_R8_RAW_OPCODE_TRANSFORMER.md
docs/evaluation/AI_R8_REPORT_ONLY_DEMO.md
docs/evaluation/HYBRID_AI_PRODUCTION_REPORTING.md
docs/evaluation/FINAL_HYBRID_AI_DEMO_SMOKE.md
```

Say:

```text
After the transparent v2 evaluation, I added a report-only AI layer for hard R8 and matcher-recall triage. Phase 6A trains a RandomForest on 20,523 existing evaluation rows and reaches 0.708 test macro-F1. Phase 6B trains an isolated tiny Transformer over structured project-evidence tokens and reaches 0.977 test macro-F1. I also built a larger 31,589-row project-heldout corpus manifest, a raw DEX/opcode prototype corpus with 1,680 method-level opcode sequences from 14 APKs, and a case-heldout raw-opcode Transformer training run. The raw-opcode Transformer reaches 0.110 test macro-F1, below the opcode-count baseline at 0.128, so it is kept as honest research-only evidence. The integrated production report can surface the Transformer status, but production wiring stays disabled and neither AI track can change selected versions, SBOM components, CVE labels, or source-validation metrics.
```

Then add:

```text
The demo proof runs the same APK with and without AI suggestions. The AI report section appears, but detected components and normalized SBOM content stay unchanged.
```

Then add:

```text
The hybrid/AI production flag is --include-hybrid-ai-assistance. It adds the hybrid router, RandomForest suggestions, and Transformer status to report JSON, Markdown, and HTML under hybrid_ai_assistance. This is promoted only as report assistance; the current weighted matcher remains the SBOM authority.
```

Then add:

```text
The final real-APK smoke compares default and hybrid-AI reports for F-Droid and Aegis Authenticator. In both cases, detected components, selected versions, CycloneDX components, and vulnerability output remain unchanged, while the hybrid assistance section is visible in JSON, Markdown, and HTML.
```

Optional regeneration command:

```powershell
apk-sbom ai-r8-final-eval
python scripts\build_hybrid_ai_production_report_evidence.py
python scripts\build_final_hybrid_ai_demo_smoke.py
```

### 7. Optional Hybrid Matcher Improvement Plan

Open:

```text
docs/evaluation/HYBRID_MATCHER_ROUTER_V1.md
```

Say:

```text
I compared the current weighted matcher against tool-family strategies from the literature: profile/hash matching, package-independent clustering, structural similarity, CFG/fuzzy hashing, coarse-to-fine matching, vulnerability-oriented review, learned representations, and SBOM/CVE fusion. The result is not a new default matcher yet; it is a report-only router that tells us which safe experiment profile fits each hard row family.
```

Then add:

```text
For the current v2 artifacts, the router produced 7,569 rows across 105 cases and 849 coordinates. It prioritizes 4,766 P1 rows, mainly version-band rerank, R8 structural recall, alias/boundary mapping, coarse-to-fine recall, and the 442 remaining reference-growth candidates. It does not change selected versions, SBOM components, CVE labels, or source-validation metrics.
```

Optional regeneration command:

```powershell
apk-sbom hybrid-matcher-router
```

Then open:

```text
docs/evaluation/VERSION_BAND_RERANK_EXPERIMENT.md
```

Say:

```text
The first router-driven experiment is the version-band rerank lane. It covers 582 of the current 636 normal wrong-version rows, and 565 of those become source-known fixable when the v2 source-known slice selects the source version. The controls are visible too: 820 exact rows stay exact, and 120 false-positive extra emissions remain blocking controls because a version reranker cannot create source evidence.
```

Then add:

```text
This is promising evidence for matcher improvement, but it is still an upper-bound source-known experiment. It is not APK-only production accuracy and it is not promoted into default matcher scoring.
```

Optional regeneration command:

```powershell
apk-sbom version-band-rerank-experiment
```

Then open:

```text
docs/evaluation/VERSION_BAND_APK_RERANKER_V2.md
```

Say:

```text
I then tested the stricter APK-only version of the idea. This prototype does not use source versions to choose candidates. It uses only baseline APK report alternatives and sibling version-era anchors. It evaluated 1,522 rows and made zero safe changes: zero fixes, zero exact-control regressions, and zero false-positive-control changes. The key blocker is candidate visibility: only 44 of 582 scoped wrong-version rows expose the source version as a baseline alternative.
```

Then add:

```text
That is why I keep the source-known result as an upper-bound opportunity and reject the APK-only reranker for promotion today. The next matcher work must expand independent same-coordinate candidates and add stronger version-specific evidence before retrying.
```

Optional regeneration command:

```powershell
apk-sbom version-band-apk-reranker
```

Then open:

```text
docs/evaluation/VERSION_BAND_CANDIDATE_EXPANSION_V3.md
```

Say:

```text
I also ran a deeper candidate-expansion pilot instead of stopping at the old report alternatives. For a representative Activity wrong-version row, I expanded to 134 same-coordinate references from the v2 large DB. The result still selected an old wrong version, not the source-validated version. That blocks promotion because candidate visibility alone is not enough; we need stronger version-specific evidence.
```

Then add:

```text
So the honest conclusion is: version-band reranking is a real opportunity, but not ready as APK-only production logic. That is why I then evaluated the router's R8 structural recall lane separately as report-only matcher-recall transparency.
```

Optional regeneration command:

```powershell
apk-sbom version-band-candidate-expansion
```

### 8. Optional R8 Structural Recall Lane

Open:

```text
docs/evaluation/R8_STRUCTURAL_RECALL_EXPERIMENT.md
```

Say:

```text
After the version-band promotion gate blocked automatic reranking, I evaluated the router's R8 structural recall lane. It focuses on rows where opcode and structural evidence are strong while class and method names are weak. It found 1,000 source-context report-only candidates from 1,658 router rows, but it is not promoted into SBOM emission because the same coordinate space still has 581 wrong-version controls and 233 false-positive controls.
```

Then add:

```text
This is the right kind of AI/hybrid use for the MVP: it improves transparency and prioritization for hard R8 rows without pretending source-context suggestions are APK-only version authority.
```

Optional regeneration command:

```powershell
apk-sbom r8-structural-recall-experiment
```

Then open:

```text
docs/evaluation/R8_APK_STRUCTURAL_PROMOTION_GATE.md
```

Say:

```text
Because the source-context R8 structural recall lane looked useful, I tested a stricter APK-only structural promotion gate. The gate uses source-free APK-side evidence: high opcode similarity, literal support, dependency support, weak class/method names, and AI only as triage. It passes 219 high-evidence rows, and all 219 are posthoc source-exact, but zero rows satisfy the production promotion controls.
```

Then add:

```text
The blockers are explicit: 65 gate-pass rows are blocked by same-coordinate wrong-version or false-positive controls, and 154 are blocked because zero-risk coordinates have no representative exact emitted control. So the hybrid R8 lane is useful for reports and prioritization, but not promoted into automatic SBOM emission yet.
```

Optional regeneration command:

```powershell
apk-sbom r8-apk-structural-promotion-gate
```

Then add:

```text
The stricter promotion matrix tests five APK-only profiles. The baseline profile reproduces 219 gate-pass rows, but strict control requirements leave zero eligible production rows; higher-confidence profiles pass zero rows. This is why the hybrid R8 lane is useful evidence but not promoted as SBOM authority today.
```

Optional regeneration command:

```powershell
python scripts\build_r8_strict_apk_promotion_gate_matrix.py
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
| Is the DL model a production APK detector? | No. The structured-token Transformer is a PhD/AI workflow proof, and the raw-opcode Transformer is an early case-heldout experiment that does not beat the opcode-count baseline. Both stay report-only. |
| Why not replace the matcher with one research method? | Different APK conditions fail differently. The router keeps the current matcher as the control baseline and chooses scoped experiments per row family, such as version-band rerank for adjacent AndroidX/Kotlin versions or R8 structural recall for strong opcode but weak name evidence. |
| Did the version-band experiment fix wrong versions? | In the source-known upper-bound slice, 565 scoped wrong-version rows become fixable and 820 exact controls stay exact. It is not promoted because an APK-only full-DB reranker still has to prove it can choose those versions without source constraints. |
| Did the APK-only reranker work? | No, and that is useful evidence. It made 0 safe fixes because only 44/582 scoped wrong-version rows expose the source version as a baseline alternative. The result blocks promotion and points to candidate-generation and version-specific evidence as the next work. |
| Can candidate expansion make it promotable? | Not yet. The v3 deep probe expanded a representative Activity row to 134 same-coordinate references, but generic similarity selected an old wrong version. Candidate expansion must be paired with stronger version-specific evidence before promotion. |
| Did R8 structural recall work? | It worked as report-only transparency: 1,000 source-context structural recall candidates are visible. It is not SBOM promotion because same-coordinate wrong-version and false-positive controls remain. |
| Can the R8 structural lane be promoted after the APK-only gate? | Not yet. The APK-only gate passes 219 high-evidence rows, but 65 are blocked by same-coordinate control risk and 154 lack representative exact emitted controls, leaving 0 production promotion candidates. The stricter five-profile matrix also leaves 0 production candidates. |
| What is the next technical improvement? | Turn report-only structural recall into APK-only evidence by adding independent structural controls, then rerun exact, wrong-version, false-positive, boundary, and CVE-sensitive gates. |

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
