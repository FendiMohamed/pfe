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

## Fixable Reference-Growth V2

After the final source-gap triage, a bounded fixable retry excluded rows already proven no-bytecode and retried only plausibly bytecode-bearing missing-reference slots.

| Item | Value |
|---|---:|
| V2 DB path | `data/reference_db/reference_features_demo_final_large_v2.sqlite` |
| Retry slots attempted | 87 |
| Downloaded slots | 46 |
| Converted slots | 24 |
| Stored new slots | 24 |
| Downloaded no-bytecode slots | 22 |
| V2 DB components | 10517 |
| Source-gap rows now reference-covered | 25 |
| Attempted but unavailable/source-boundary rows | 43 |
| Downloaded no-bytecode source-gap rows | 91 |

Primary artifacts:

- `docs/evaluation/DEMO_FINAL_FIXABLE_REFERENCE_RETRY_PLAN.md`
- `docs/evaluation/DEMO_FINAL_FIXABLE_REFERENCE_RETRY_STAGE2_PLAN.md`
- `docs/evaluation/DEMO_FINAL_FIXABLE_REFERENCE_GROWTH_RESULT.md`
- `configs/libraries.demo_final_fixable_missing_reference_retry.json`
- `configs/libraries.demo_final_fixable_missing_reference_retry_stage2.json`
- `data/results/evaluation/demo-final-fixable-reference-retry-plan.json`
- `data/results/evaluation/demo-final-fixable-reference-retry-stage2-plan.json`
- `data/results/evaluation/demo-final-fixable-reference-growth-result.json`

Interpretation: this grows the reference DB transparently where public bytecode artifacts were recoverable. The full source-version constrained evaluation was rerun against this v2 DB and is now the current demo package.

## Full 106-Case V2 Final Test

| Metric | Value |
|---|---:|
| Source-tree cases tested | 106 / 106 |
| Emitted rows checked | 6772 |
| Exact confirmations | 6772 |
| Wrong-version rows | 0 |
| Missing emitted rows | 0 |
| Confirmation rate | 100.0% |
| Source-gap rows | 5238 |
| Source gaps with coordinate in v2 DB | 4222 |
| Source gaps still missing from v2 DB | 1016 |

Primary artifacts:

- `docs/evaluation/DEMO_FINAL_LARGE_V2_SOURCE_VERSION_EVALUATION.md`
- `data/results/evaluation/real-apk-demo-final-large-v2-source-version-dashboard.json`
- `data/results/evaluation/real-apk-demo-final-large-v2-source-version-rows.csv`
- `data/results/evaluation/real-apk-demo-final-large-v2-source-version-gaps.csv`
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
| Missing-reference candidate | 442 |
| Matcher-recall candidate | 2281 |

Primary artifacts:

- `docs/evaluation/DEMO_FINAL_LARGE_V2_SOURCE_GAP_TRIAGE.md`
- `data/results/evaluation/demo-final-large-v2-source-gap-triage.json`
- `data/results/evaluation/demo-final-large-v2-source-gap-triage.csv`
- `configs/libraries.demo_final_large_v2_remaining_missing_reference_candidates.json`
- `docs/evaluation/DEMO_FINAL_LARGE_SOURCE_GAP_TRIAGE.md`
- `data/results/evaluation/demo-final-large-source-gap-triage.json`
- `data/results/evaluation/demo-final-large-source-gap-triage.csv`
- `configs/libraries.demo_final_large_remaining_missing_reference_candidates.json`

## Matcher Recall Diagnostic

The matcher-recall bucket was scored again against the final per-APK source-version slice DBs. This keeps the diagnostic bounded to source-known evaluation context and does not change SBOM output.

| Matcher-recall status | Rows |
|---|---:|
| Report-only source-context suggestions | 1425 |
| Suppressed uncertain rows | 834 |
| Below-threshold rows | 10 |
| No-bytecode-signal rows | 12 |

Primary artifacts:

- `docs/evaluation/DEMO_FINAL_V2_MATCHER_RECALL_DIAGNOSTICS.md`
- `data/results/evaluation/demo-final-v2-matcher-recall-diagnostics.json`
- `data/results/evaluation/demo-final-v2-matcher-recall-diagnostics.csv`
- `docs/evaluation/DEMO_FINAL_MATCHER_RECALL_DIAGNOSTICS.md`
- `data/results/evaluation/demo-final-matcher-recall-diagnostics.json`
- `data/results/evaluation/demo-final-matcher-recall-diagnostics.csv`

Interpretation: the best safe improvement is to surface the 1425 rows as source-context report-only suggestions in demo/thesis analysis. They should not be promoted into default SBOM components without a separate control run, because 1422 of them are still uncertain by the production matcher.

## Transparency Export

The final demo package also includes row-level JSON/CSV exports that connect dataset role, source dependency coverage, emitted result class, correct source versions, missing-reference rows, matcher-recall rows, and vulnerability claim strength.

Primary artifacts:

- `docs/evaluation/DEMO_FINAL_TRANSPARENCY_REPORT.md`
- `data/results/evaluation/demo-final-transparency-export.json`
- `data/results/evaluation/demo-final-transparency-cases.csv`
- `data/results/evaluation/demo-final-transparency-source-rows.csv`
- `data/results/evaluation/demo-final-transparency-emitted-rows.csv`
- `data/results/evaluation/demo-final-transparency-vulnerability-rows.csv`

Use this export when a supervisor asks why a dependency is not counted, whether a row is missing from the DB, whether the exact version exists but was not emitted, or whether a vulnerability claim is source-confirmed versus report-only/potential.

## Honest Boundary

This is not APK-only version-selection accuracy.

The completed lane is source-version constrained: each APK is evaluated against exact coordinate+version rows already known from that APK's resolved source dependency tree. It is an upper-bound test for bytecode recognition and report generation when the correct source versions are known.

The production-style unconstrained large-DB rerun remains blocked by matcher runtime and regression behavior. Earlier direct/capped/package-overlap probes were either too slow or regressed F-Droid. That limitation is documented in `docs/evaluation/LARGE_COMBINED_REAL_APK_ANALYSIS.md`.

## Demo Recommendation

Use the final demo as:

1. Honest SBOM/CVE MVP demonstration on representative APKs.
2. Source-known v2 large-DB upper-bound evidence across 106 real APK source-tree cases.
3. Transparency evidence showing which source dependencies are metadata/alias boundaries, which are still missing-reference candidates, and which require future matcher recall improvements.

Do not present the 100.0% source-version constrained result as general APK-only detection accuracy.
