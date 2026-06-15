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

## How To Present It

Use the v2 result as a transparent upper-bound lane:

1. The DB was grown from source-observed real APK dependency slots, with failed/no-bytecode/source-boundary rows recorded rather than hidden.
2. The 106 source-tree cases were rerun against exact source coordinate+version slices from the v2 DB.
3. Every emitted row in that constrained lane was source-confirmed exact, while non-emitted source rows were separated into metadata/source-only, alias, missing-reference, and matcher-recall buckets.
4. Vulnerability rows remain tagged as source-confirmed, potential, report-only, or not queried; do not collapse them into one CVE count.

The honest limitation is still important: the production unconstrained large-DB matcher needs stronger recall/pruning before these source-known suggestions can become default SBOM components.
