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
| 7 | `docs/evaluation/AI_R8_MVP_INTEGRATION_GATE.md` | Final answer for whether AI can be integrated into the MVP: report-only yes, matcher/SBOM authority no. |
| 8 | `docs/evaluation/AI_R8_DL_PROTOTYPE_MVP_SAFE.md` | Source-free structured-token Transformer run used by the MVP gate. |
| 9 | `docs/evaluation/AI_R8_INDEPENDENT_CORPUS.md` | Larger project-heldout AI/R8 corpus manifest with training vs heldout partitions. |
| 10 | `docs/evaluation/AI_R8_RAW_OPCODE_CORPUS.md` | Raw DEX/opcode method-sequence corpus prototype for the future Transformer lane. |
| 11 | `docs/evaluation/AI_R8_RAW_OPCODE_TRANSFORMER.md` | Case-heldout raw-opcode Transformer result and baseline comparison, kept research-only. |
| 12 | `docs/evaluation/AI_R8_REPORT_ONLY_DEMO.md` | Proof that AI suggestions are report-only and do not change SBOM content. |
| 13 | `docs/evaluation/HYBRID_AI_PRODUCTION_REPORTING.md` | Production `generate-report --include-hybrid-ai-assistance` integration, guarded as report-only. |
| 14 | `docs/evaluation/FINAL_HYBRID_AI_DEMO_SMOKE.md` | Final real-APK smoke proving the hybrid-AI section is visible while default report outputs stay unchanged. |
| 15 | `docs/evaluation/FINAL_AI_DEFENSE_DEMO.md` | One-command clean/CVE/R8/AI defense verdict and guardrail checks. |
| 16 | `docs/evaluation/HYBRID_MATCHER_ROUTER_V1.md` | Report-only matcher-improvement comparison and hybrid strategy router. |
| 17 | `docs/evaluation/VERSION_BAND_RERANK_EXPERIMENT.md` | First router-driven source-known rerank experiment and controls. |
| 18 | `docs/evaluation/VERSION_BAND_APK_RERANKER_V2.md` | APK-only reranker prototype showing why source-known fixes are not safely promotable yet. |
| 19 | `docs/evaluation/VERSION_BAND_CANDIDATE_EXPANSION_V3.md` | Promotion gate combining source-known, APK-only, and deep candidate expansion evidence. |
| 20 | `docs/evaluation/R8_STRUCTURAL_RECALL_EXPERIMENT.md` | Next router lane: source-context structural recall candidates, guarded as report-only. |
| 21 | `docs/evaluation/R8_APK_STRUCTURAL_PROMOTION_GATE.md` | APK-only structural promotion gate showing why the hybrid R8 lane is not promoted into SBOM emission yet. |
| 22 | `docs/evaluation/R8_STRICT_APK_PROMOTION_GATE_MATRIX.md` | Stricter multi-profile APK-only promotion matrix: 0 production candidates today. |

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
| AI R8 MVP-safe Transformer test macro-F1 | 0.882 |
| AI R8 MVP-safe Transformer test accuracy | 0.907 |
| AI R8 MVP integration gate | report-only ready; matcher/SBOM/CVE authority blocked |
| AI R8 independent corpus rows | 31589 |
| AI R8 independent heldout/report-only rows | 11066 |
| AI R8 raw opcode method-sequence rows | 1680 |
| AI R8 raw opcode APKs analyzed | 14 |
| AI R8 raw opcode Transformer test macro-F1 | 0.110 |
| AI R8 raw opcode count baseline macro-F1 | 0.128 |
| AI R8 raw opcode Transformer verdict | raw-opcode-transformer-research-only-not-promotable |
| Hybrid AI production report status | report-only, matcher authority unchanged |
| Final hybrid AI smoke targets | 2 real APKs |
| Final hybrid AI smoke output comparison | unchanged components, versions, SBOM, vulnerability output |
| Final hybrid AI smoke section visibility | visible in JSON, Markdown, and HTML |
| Hybrid matcher router rows | 7569 |
| Hybrid router P1 rows | 4766 |
| Hybrid router top profile | version-band-rerank, 2180 rows |
| Version-band wrong-version rows in scope | 582 / 636 |
| Version-band source-known fixable rows | 565 |
| Version-band exact controls | 820, all stay exact |
| APK-only reranker safe fixes | 0 |
| APK-only source candidate visibility | 44 / 582 scoped wrong-version rows |
| Candidate expansion v3 verdict | do-not-promote-candidate-expansion-v3 |
| R8 structural recall router rows | 1658 |
| R8 structural report-only candidates | 1000 |
| R8 structural blocked rows | 658 |
| R8 structural control-risk rows | 814 |
| R8 APK-only structural gate pass rows | 219 |
| R8 APK-only structural promotion candidates | 0 |
| R8 strict APK promotion profiles | 5 |
| R8 strict APK promotion candidates | 0 |
| R8 APK-only structural gate verdict | apk-only-structural-gate-blocked-by-controls |

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
The hybrid and AI layer is now integrated into production reports through --include-hybrid-ai-assistance, but it is report-only: it does not change matcher scoring, selected versions, SBOM components, CVE labels, or source-validation metrics.
```

Use:

```text
The AI layer is report-only triage. It demonstrates ML workflow and helps prioritize hard R8/matcher-recall rows, but it does not change SBOM components, selected versions, or CVE labels.
```

Use:

```text
The stricter MVP-safe Transformer removes source-version and source-validation shortcut tokens; it still reaches 0.882 test macro-F1, so it supports report-only risk triage, not automatic matcher authority.
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

Use:

```text
The R8 structural recall experiment found 1,000 source-context report-only candidates, but it is not automatic SBOM emission because 581 wrong-version controls and 233 false-positive controls remain in the same coordinate space.
```

Use:

```text
The stricter APK-only structural gate passes 219 high-evidence rows, but zero are production-promotable today: 65 are blocked by same-coordinate control risk and 154 have no representative exact emitted control.
```

Use:

```text
The deeper candidate-expansion pilot also blocks promotion: expanding one representative Activity row to 134 same-coordinate references still selected an old wrong version, so candidate visibility alone is not enough without stronger version-specific evidence.
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
| Hybrid AI production reporting regenerated | report-only production integration, DL production wiring disabled |
| Final hybrid AI demo smoke regenerated | 2 targets, outputs unchanged, hybrid sections visible |
| AI R8 final evaluation regenerated | includes Phase 6A, Phase 6B, MVP-safe Transformer, independent corpus, raw opcode corpus, raw opcode Transformer, integration gate, and report-only proof |
| AI R8 MVP-safe Transformer trained | test macro-F1 0.882, test accuracy 0.907, source-free structured-token profile |
| AI R8 MVP integration gate regenerated | report-only ready, matcher/SBOM/CVE authority blocked |
| AI R8 independent corpus regenerated | 31589 rows, 20523 training-eligible, 11066 heldout/report-only |
| AI R8 raw opcode corpus regenerated | 14 APKs analyzed, 1680 method sequences, 0 skipped |
| AI R8 raw opcode Transformer trained | test macro-F1 0.110, below opcode-count baseline 0.128, research-only |
| V2 dashboard JSON count check | 106 cases, 6772 checked, 0 mismatches, 0 missing |
| Transparency JSON count check | 110 cases, 12082 source rows, 6772 emitted rows, 232 vulnerability rows |
| Hybrid matcher router regenerated | 7569 rows, 4766 P1, top profile version-band-rerank |
| Version-band rerank experiment regenerated | 582 scoped wrong-version rows, 565 source-known fixable, 820 exact controls |
| APK-only version-band reranker regenerated | 1522 rows, 0 fixes, 0 regressions, 44/582 source candidates visible |
| Version-band candidate expansion v3 regenerated | do-not-promote, representative deep probe selected wrong old Activity version |
| R8 structural recall experiment regenerated | 1658 rows, 1000 report-only candidates, 814 control-risk rows |
| R8 APK-only structural promotion gate regenerated | 219 gate-pass rows, 0 promotion candidates, promotion blocked by controls |
| R8 strict APK promotion gate matrix regenerated | 5 profiles, 0 production candidates |
| Deck package validation | current editable deck: 13 slides, including the AI integration gate |

## Do Not Run Live

- Do not rerun the full 106-APK v2 source-version evaluation during the defense.
- Do not rebuild the large DB during the defense.
- Do not query OSV live unless the network is known to work; the clean and vulnerable demo artifacts already exist.

## Safe Optional Commands

```powershell
python scripts\build_demo_final_transparency_export.py
python scripts\build_thesis_artifact_index.py
python scripts\build_graduation_demo_rehearsal.py
python scripts\run_final_ai_defense_demo.py --refresh
apk-sbom ai-r8-final-eval
python scripts\build_hybrid_ai_production_report_evidence.py
apk-sbom hybrid-matcher-router
apk-sbom version-band-rerank-experiment
apk-sbom version-band-apk-reranker
apk-sbom version-band-candidate-expansion
apk-sbom r8-structural-recall-experiment
```
