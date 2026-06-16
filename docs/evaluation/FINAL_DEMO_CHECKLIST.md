# Final Demo Checklist

Use this as the fast day-of-defense checklist. It points to already-generated artifacts; do not rerun the long 106-APK evaluation live.

## Open First

| Order | Artifact | Purpose |
|---:|---|---|
| 1 | `outputs/manual-20260526-apk-sbom-deck/presentations/apk-sbom-defense/output/apk-sbom-defense-deck.pptx` | Current editable defense deck with the final v2 story. |
| 2 | `docs/evaluation/FINAL_DEMO_RUNBOOK_V2.md` | Exact opening wording, file order, and hard-question answers. |
| 3 | `docs/evaluation/DEMO_FINAL_V2_PACKAGE.md` | Current v2 package index and headline numbers. |
| 4 | `docs/thesis/FINAL_V2_RESULTS_SECTION.md` | Thesis-ready wording that separates normal metrics from the v2 upper-bound lane. |
| 5 | `docs/evaluation/DEMO_FINAL_TRANSPARENCY_REPORT.md` | Row-level dataset/source/emitted/vulnerability classification summary. |
| 6 | `docs/evaluation/AI_R8_FINAL_EVALUATION.md` | Optional Phase 6 AI/ML/DL evidence for PhD-oriented discussion. |
| 7 | `docs/evaluation/AI_R8_REPORT_ONLY_DEMO.md` | Proof that AI suggestions are report-only and do not change SBOM content. |
| 8 | `docs/evaluation/HYBRID_MATCHER_ROUTER_V1.md` | Report-only matcher-improvement comparison and hybrid strategy router. |
| 9 | `docs/evaluation/VERSION_BAND_RERANK_EXPERIMENT.md` | First router-driven source-known rerank experiment and controls. |
| 10 | `docs/evaluation/VERSION_BAND_APK_RERANKER_V2.md` | APK-only reranker prototype showing why source-known fixes are not safely promotable yet. |

## Live Demo Artifacts

| Demo moment | Open |
|---|---|
| Clean APK-to-SBOM report | `data/results/report-real-f-droid-final-demo-osv/report.html` |
| Clean CycloneDX SBOM | `data/results/report-real-f-droid-final-demo-osv/sbom.cdx.json` |
| Clean source validation | `data/results/source-validation/fdroid-final-demo-osv/source-validation.md` |
| Positive CVE report | `data/results/demo-osv-vulnerable-jackson-databind/report.html` |
| Positive CVE OSV JSON | `data/results/demo-osv-vulnerable-jackson-databind/osv-vulnerabilities.json` |
| Real APK CVE triage policy | `docs/evaluation/OSV_SOURCE_VALIDATION_TRIAGE.md` |
| Graduation rehearsal pack | `docs/evaluation/GRADUATION_DEMO_REHEARSAL.md` |

## Numbers To Say

| Claim | Number |
|---|---:|
| Controlled fixtures | 84 / 84 expected Maven versions |
| Normal source-validated emitted-version metric | 927 / 1837 exact emitted Maven versions |
| Clean source-validated real APKs | 47 / 47 emitted Maven versions across 5 APKs |
| Partial source-validated real APKs | 880 / 1790 emitted Maven versions across 97 APKs |
| V2 source-version constrained emitted rows | 6772 / 6772 exact confirmations |
| V2 wrong-version emitted rows | 0 |
| V2 missing emitted rows | 0 |
| V2 source-gap rows | 5238 |
| Explained/boundary source-gap rows | 2515 |
| Actionable source-gap rows | 2723 |
| Missing-reference candidate rows | 442 |
| Matcher-recall candidate rows | 2281 |
| Matcher report-only suggestions | 1425 |
| AI R8 training rows | 20523 |
| AI R8 RandomForest test macro-F1 | 0.708 |
| AI R8 report-only suggestions | 13736 |
| AI R8 Transformer structured-token test macro-F1 | 0.977 |
| Hybrid matcher router rows | 7569 |
| Hybrid router P1 rows | 4766 |
| Hybrid router top profile | version-band-rerank, 2180 rows |
| Version-band wrong-version rows in scope | 582 / 636 |
| Version-band source-known fixable rows | 565 |
| Version-band exact controls | 820, all stay exact |
| APK-only reranker safe fixes | 0 |
| APK-only source candidate visibility | 44 / 582 scoped wrong-version rows |

## Exact Phrases

Use:

```text
The normal real-APK metric is emitted Maven version confirmation, not full dependency recall.
```

Use:

```text
The v2 result is a source-version constrained upper-bound lane. It proves exact recognition when the correct source versions are known, not unconstrained APK-only production accuracy.
```

Use:

```text
The remaining denominator is exported row by row: boundary/source-only rows, missing-reference rows, and matcher-recall rows are not hidden.
```

Use:

```text
The AI layer is report-only triage. It demonstrates ML workflow and helps prioritize hard R8/matcher-recall rows, but it does not change SBOM components, selected versions, or CVE labels.
```

Use:

```text
The DL prototype is a trained structured-token Transformer workflow, not a production APK detector or raw smali pretraining result.
```

Use:

```text
The hybrid matcher router compares the current matcher to research tool families and routes hard rows to safe experiments, but it is a planning artifact, not a production matcher change.
```

Use:

```text
The first version-band rerank experiment is promising because 565 wrong-version rows become source-known fixable, but it is still an upper-bound experiment, not APK-only production accuracy.
```

Use:

```text
The APK-only reranker prototype explains why it is not promoted yet: the current baseline reports expose the source version as an alternative in only 44 of 582 scoped wrong-version rows, and the strict source-free gate makes zero safe changes.
```

Avoid:

```text
The tool has 100% real-world APK accuracy.
```

## Verified Before Defense

| Check | Status |
|---|---|
| Transparency export regenerated | passed |
| Thesis artifact index regenerated | passed |
| Graduation demo rehearsal regenerated | passed |
| V2 dashboard JSON count check | 106 cases, 6772 checked, 0 mismatches, 0 missing |
| Transparency JSON count check | 110 cases, 12082 source rows, 6772 emitted rows, 232 vulnerability rows |
| Hybrid matcher router regenerated | 7569 rows, 4766 P1, top profile version-band-rerank |
| Version-band rerank experiment regenerated | 582 scoped wrong-version rows, 565 source-known fixable, 820 exact controls |
| APK-only version-band reranker regenerated | 1522 rows, 0 fixes, 0 regressions, 44/582 source candidates visible |
| Deck package validation | passed earlier: 12 slides, 12 notes slides |

## Do Not Run Live

- Do not rerun the full 106-APK v2 source-version evaluation during the defense.
- Do not rebuild the large DB during the defense.
- Do not query OSV live unless the network is known to work; the clean and vulnerable demo artifacts already exist.

## Safe Optional Commands

```powershell
python scripts\build_demo_final_transparency_export.py
python scripts\build_thesis_artifact_index.py
python scripts\build_graduation_demo_rehearsal.py
apk-sbom ai-r8-final-eval
apk-sbom hybrid-matcher-router
apk-sbom version-band-rerank-experiment
apk-sbom version-band-apk-reranker
```
