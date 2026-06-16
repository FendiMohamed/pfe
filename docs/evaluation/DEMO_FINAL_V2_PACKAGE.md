# Demo Final V2 Package

This package is the current thesis/demo evidence set for the grown v2 reference DB. It is source-version constrained and evaluation-only: it proves what the MVP can recognize when the correct source coordinate+version set is known, not unconstrained APK-only version-selection accuracy.

## Current Result

| Metric | Value |
|---|---:|
| Reference DB components | 10517 |
| Source-tree cases rerun | 106 / 106 |
| Emitted rows checked | 6772 |
| Exact confirmations | 6772 |
| Wrong-version rows | 0 |
| Missing emitted rows | 0 |
| Confirmation rate | 100.0% |
| Source-gap rows | 5238 |
| Explained or boundary source-gap rows | 2515 |
| Actionable source-gap rows | 2723 |
| Missing-reference candidate rows | 442 |
| Matcher-recall candidate rows | 2281 |
| Matcher report-only suggestions | 1425 |

## Core Artifacts

| Purpose | Artifact |
|---|---|
| Final demo checklist | `docs/evaluation/FINAL_DEMO_CHECKLIST.md` |
| MVP readiness summary | `docs/evaluation/DEMO_FINAL_MVP_READINESS.md` |
| V2 evaluation report | `docs/evaluation/DEMO_FINAL_LARGE_V2_SOURCE_VERSION_EVALUATION.md` |
| V2 evaluation dashboard | `data/results/evaluation/real-apk-demo-final-large-v2-source-version-dashboard.json` |
| V2 emitted rows | `data/results/evaluation/real-apk-demo-final-large-v2-source-version-rows.csv` |
| V2 source gaps | `data/results/evaluation/real-apk-demo-final-large-v2-source-version-gaps.csv` |
| V2 gap triage | `docs/evaluation/DEMO_FINAL_LARGE_V2_SOURCE_GAP_TRIAGE.md` |
| V2 gap triage JSON | `data/results/evaluation/demo-final-large-v2-source-gap-triage.json` |
| V2 matcher recall diagnostic | `docs/evaluation/DEMO_FINAL_V2_MATCHER_RECALL_DIAGNOSTICS.md` |
| V2 matcher recall JSON | `data/results/evaluation/demo-final-v2-matcher-recall-diagnostics.json` |
| Transparency report | `docs/evaluation/DEMO_FINAL_TRANSPARENCY_REPORT.md` |
| Transparency JSON export | `data/results/evaluation/demo-final-transparency-export.json` |
| Vulnerability rows | `data/results/evaluation/demo-final-transparency-vulnerability-rows.csv` |
| AI R8 compact summary | `docs/evaluation/AI_R8_ASSISTANT_SUMMARY.md` |
| AI R8 final ML/DL evaluation | `docs/evaluation/AI_R8_FINAL_EVALUATION.md` |
| AI R8 DL prototype | `docs/evaluation/AI_R8_DL_PROTOTYPE.md` |
| AI R8 report-only demo | `docs/evaluation/AI_R8_REPORT_ONLY_DEMO.md` |
| Hybrid AI production reporting | `docs/evaluation/HYBRID_AI_PRODUCTION_REPORTING.md` |
| Hybrid matcher router | `docs/evaluation/HYBRID_MATCHER_ROUTER_V1.md` |
| Version-band rerank experiment | `docs/evaluation/VERSION_BAND_RERANK_EXPERIMENT.md` |
| APK-only version-band reranker v2 | `docs/evaluation/VERSION_BAND_APK_RERANKER_V2.md` |
| Version-band candidate expansion v3 | `docs/evaluation/VERSION_BAND_CANDIDATE_EXPANSION_V3.md` |

## How To Present It

Use the v2 result as a transparent upper-bound lane:

1. The DB was grown from source-observed real APK dependency slots, with failed/no-bytecode/source-boundary rows recorded rather than hidden.
2. The 106 source-tree cases were rerun against exact source coordinate+version slices from the v2 DB.
3. Every emitted row in that constrained lane was source-confirmed exact, while non-emitted source rows were separated into metadata/source-only, alias, missing-reference, and matcher-recall buckets.
4. Vulnerability rows remain tagged as source-confirmed, potential, report-only, or not queried; do not collapse them into one CVE count.

The honest limitation is still important: the production unconstrained large-DB matcher needs stronger recall/pruning before these source-known suggestions can become default SBOM components.

## Phase 6 AI Assistance

The v2 package now has an optional AI-assisted R8 triage layer. It is trained from the existing transparency, matcher-recall, and R8 diagnostic artifacts and remains report-only:

- dataset rows: `20523`;
- Phase 6A model: `RandomForestClassifier`;
- Phase 6A test macro-F1: `0.708`;
- report-only suggestions: `13736`;
- Phase 6B model: `torch.nn.TransformerEncoder`;
- Phase 6B structured-token test macro-F1: `0.977`;
- no selected-version, SBOM, vulnerability-label, or source-validation metric changes.

Use `docs/evaluation/AI_R8_FINAL_EVALUATION.md` as the single AI/ML/DL evidence entry point, `docs/evaluation/AI_R8_ASSISTANT_SUMMARY.md` for the compact Phase 6A numbers, and `docs/evaluation/AI_R8_REPORT_ONLY_DEMO.md` as the no-change proof. Regenerate the combined package with:

```powershell
apk-sbom ai-r8-final-eval
```

`docs/evaluation/HYBRID_AI_PRODUCTION_REPORTING.md` records the production-facing report integration. `generate-report --include-hybrid-ai-assistance` now attaches a `hybrid_ai_assistance` JSON block plus Markdown/HTML "Hybrid AI Matcher Assistance" section. It combines the hybrid router, Phase 6A RandomForest suggestions, and Phase 6B Transformer status, while keeping the current weighted matcher as the SBOM authority.

```powershell
apk-sbom generate-report <apk-path> --include-hybrid-ai-assistance
```

This is promoted only as report-only production assistance. It does not change matcher scoring, selected versions, SBOM components, vulnerability labels, source-validation metrics, or the disabled DL production-wiring status.

## Hybrid Matcher Router

`docs/evaluation/HYBRID_MATCHER_ROUTER_V1.md` compares the current weighted matcher with LibScout/LibD/LibPecker/SAD/ORLIS/LibHunter/ATVHunter/LibAttention/LibMD-style strategies, then routes the current hard rows to safe experimental profiles.

- router rows: `7569`;
- unique cases: `105`;
- unique coordinates: `849`;
- P1 routed rows: `4766`;
- largest profiles: `version-band-rerank` (`2180`), `r8-structural-recall` (`1658`), `alias-boundary-map` (`1553`), `boundary-hash-only` (`974`), `coarse-to-fine-recall` (`701`), and `reference-growth-first` (`442`).

This is also report-only. It does not change matcher scoring, selected versions, SBOM components, vulnerability labels, or source-validation metrics. Regenerate it with:

```powershell
apk-sbom hybrid-matcher-router
```

The first router-driven experiment is `docs/evaluation/VERSION_BAND_RERANK_EXPERIMENT.md`. It uses the router's version-band profile and the v2 source-known lane to measure an upper-bound rerank opportunity:

- baseline wrong-version rows in scope: `582` / `636`;
- source-known fixable wrong-version rows: `565`;
- blocked scoped wrong-version rows: `17`;
- exact control rows in scope: `820`, all staying exact in the source-known slice;
- false-positive extra-emission controls in scope: `120`.

This is promising evidence for the next matcher improvement, but it is not a production matcher result. Regenerate it with:

```powershell
apk-sbom version-band-rerank-experiment
```

The follow-up APK-only reranker prototype is `docs/evaluation/VERSION_BAND_APK_RERANKER_V2.md`. It does not use source versions to choose candidates; it uses only baseline APK report alternatives and sibling version-era anchors, then uses source validation only to label the outcome:

- rows evaluated: `1522`;
- wrong-version rows in scope: `582`;
- exact controls: `820`;
- false-positive extra-emission controls: `120`;
- APK-only reranker changes: `0`;
- APK-only wrong-version fixes: `0`;
- exact-control regressions: `0`;
- source version visible in baseline alternatives: `44/582` wrong-version rows (`7.6%`).

Verdict: `reject-apk-only-reranker-no-safe-fixes`. This explains why the source-known opportunity is real but not yet safely promotable as APK-only matcher logic. Regenerate it with:

```powershell
apk-sbom version-band-apk-reranker
```

The v3 promotion gate is `docs/evaluation/VERSION_BAND_CANDIDATE_EXPANSION_V3.md`. It combines the source-known result, APK-only result, and a bounded deep same-coordinate scoring pilot. The pilot expanded `androidx.activity:activity` to `134` same-coordinate references for Cryptomator Lite, but both scoring profiles selected `1.2.0-alpha01` while the source-validation version was `1.8.1`. Verdict: `do-not-promote-candidate-expansion-v3`.

Regenerate it with:

```powershell
apk-sbom version-band-candidate-expansion
```
