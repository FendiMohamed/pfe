# Demo Final MVP Readiness

## Status

The MVP is demo-ready for the honest source-version constrained large-DB evaluation lane.

This means the final demo reference DB was built, the full real-APK source-tree set was rerun, and the reports explicitly separate production APK-only limits from source-known upper-bound results.

## Final Demo DB

| Item | Value |
|---|---:|
| DB path | `data/reference_db/reference_features_demo_final_large.sqlite` |
| Components | 10493 |
| Coordinates | 1139 |
| Base large DB components | 10487 |
| Targeted recovered bytecode rows added | 6 |

The targeted missing-reference retry attempted the remaining high-signal missing-reference candidates from the source-gap triage. It downloaded 121 artifacts, found 92 real 404/source-boundary rows, converted 6 bytecode-bearing rows, skipped 115 no-bytecode/source-wrapper rows, and stored 6 new components in the final demo DB.

## Full 106-Case Final Test

| Metric | Value |
|---|---:|
| Source-tree cases tested | 106 / 106 |
| Emitted rows checked | 6751 |
| Exact confirmations | 6751 |
| Wrong-version rows | 0 |
| Missing emitted rows | 0 |
| Confirmation rate | 100.0% |
| Source-gap rows | 5259 |
| Source gaps with coordinate in final DB | 4219 |
| Source gaps still missing from final DB | 1040 |

Primary artifacts:

- `docs/evaluation/DEMO_FINAL_LARGE_SOURCE_VERSION_EVALUATION.md`
- `data/results/evaluation/real-apk-demo-final-large-source-version-dashboard.json`
- `data/results/evaluation/real-apk-demo-final-large-source-version-rows.csv`
- `data/results/evaluation/real-apk-demo-final-large-source-version-gaps.csv`

## Gap Triage

| Bucket | Rows |
|---|---:|
| Metadata/source-only boundary | 734 |
| Project-module boundary | 19 |
| Source/common/platform boundary | 209 |
| Relocated-coordinate boundary | 49 |
| Target-artifact alias boundary | 1460 |
| Already covered by emitted sibling | 44 |
| Missing-reference candidate | 467 |
| Matcher-recall candidate | 2277 |

Primary artifacts:

- `docs/evaluation/DEMO_FINAL_LARGE_SOURCE_GAP_TRIAGE.md`
- `data/results/evaluation/demo-final-large-source-gap-triage.json`
- `data/results/evaluation/demo-final-large-source-gap-triage.csv`
- `configs/libraries.demo_final_large_remaining_missing_reference_candidates.json`

## Matcher Recall Diagnostic

The matcher-recall bucket was scored again against the final per-APK source-version slice DBs. This keeps the diagnostic bounded to source-known evaluation context and does not change SBOM output.

| Matcher-recall status | Rows |
|---|---:|
| Report-only source-context suggestions | 1422 |
| Suppressed uncertain rows | 833 |
| Below-threshold rows | 10 |
| No-bytecode-signal rows | 12 |

Primary artifacts:

- `docs/evaluation/DEMO_FINAL_MATCHER_RECALL_DIAGNOSTICS.md`
- `data/results/evaluation/demo-final-matcher-recall-diagnostics.json`
- `data/results/evaluation/demo-final-matcher-recall-diagnostics.csv`

Interpretation: the best safe improvement is to surface the 1422 rows as source-context report-only suggestions in demo/thesis analysis. They should not be promoted into default SBOM components without a separate control run, because 1419 of them are still uncertain by the production matcher.

## Honest Boundary

This is not APK-only version-selection accuracy.

The completed lane is source-version constrained: each APK is evaluated against exact coordinate+version rows already known from that APK's resolved source dependency tree. It is an upper-bound test for bytecode recognition and report generation when the correct source versions are known.

The production-style unconstrained large-DB rerun remains blocked by matcher runtime and regression behavior. Earlier direct/capped/package-overlap probes were either too slow or regressed F-Droid. That limitation is documented in `docs/evaluation/LARGE_COMBINED_REAL_APK_ANALYSIS.md`.

## Demo Recommendation

Use the final demo as:

1. Honest SBOM/CVE MVP demonstration on representative APKs.
2. Source-known large-DB upper-bound evidence across 106 real APK source-tree cases.
3. Transparency evidence showing which source dependencies are metadata/alias boundaries, which are still missing-reference candidates, and which require future matcher recall improvements.

Do not present the 100.0% source-version constrained result as general APK-only detection accuracy.
