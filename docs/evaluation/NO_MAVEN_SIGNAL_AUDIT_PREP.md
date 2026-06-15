# No-Maven-Signal Audit Prep

Generated on 2026-06-06 after the v16 blocker rescue.

Audit result: `docs/evaluation/NO_MAVEN_SIGNAL_AUDIT.md` now classifies the four
source-validated no-Maven-signal rows. None are true runtime dependency-free
controls. Privacy Browser, monocles browser, and Blue Square Speedometer are
AndroidX identity-coverage miss controls; Mastodon is a forked-library/reference
family boundary with a weak direct Gson candidate.

This is the next work lane from
`docs/planning/RESEARCH_BACKED_REAL_APK_OPTIMIZATION_PLAN.md`. The blocked APK
lane is complete: Flying Carpet and FitoTrack are now source-validated partial
rows, and the current source-linked blocked count is 0.

## Current Queue

| APK | Bucket | APK Maven components | Source Maven components | DEX | Native `.so` | Evidence |
|---|---|---:|---:|---:|---:|---|
| Privacy Browser 3.20.1 | source-validated no-Maven-signal | 0 | 87 | 1 | 0 | `data/results/evaluation/clean-real-apk-candidate-sweep-v4/report-real-privacy-browser/report.json`; `data/results/source-validation/csv4/privacy-browser/source-validation-gradle9.5/source-validation.json`; `docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_RESULTS_V4.md` |
| Mastodon 2.12.3 | source-validated no-Maven-signal | 0 | 20 | 2 | 0 | `data/results/evaluation/clean-real-apk-candidate-sweep-v7/report-real-mastodon/report.json`; `data/results/source-validation/csv7/mastodon/source-validation-gradle8.13/source-validation.json`; `docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_RESULTS_V7.md` |
| monocles browser 1.9.3 | source-validated no-Maven-signal | 0 | 84 | 1 | 0 | `data/results/evaluation/clean-real-apk-candidate-sweep-v8/report-real-monocles-browser/report.json`; `data/results/source-validation/csv8/monocles-browser/source-validation/source-validation.json`; `docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_RESULTS_V8.md` |
| Blue Square Speedometer 1.1.0 | source-validated no-Maven-signal | 0 | 54 | 1 | 0 | `data/results/evaluation/low-risk-real-apk-batch/report-real-blue-square-speedometer/report.json`; `data/results/source-validation/low-risk-real-apk-batch/blue-square-speedometer/source-validation/source-validation.json`; `docs/evaluation/LOW_RISK_REAL_APK_PROOF_STATUS.md` |

`ProseReader` is a report-only/no-Maven candidate from v16. It is useful as a
side audit row, but it is not part of the counted source-validated
no-Maven-signal metric until source proof exists.

## What This Means

These four rows are not blocked and not source-missing. Each has a resolved
runtime dependency tree with source Maven components, but the APK report emits
zero Maven components. The next question is whether this is correct quiet
behavior because source dependencies do not leave enough DEX evidence, or an
identity-coverage miss caused by reference DB or matcher evidence gaps.

## Work Order

1. For each row, read the report JSON, source-validation JSON, and dependency
   tree.
2. Extract the top source-resolved coordinates from the dependency tree.
3. For each top coordinate, check whether the reference DB contains the
   coordinate/version family and whether the APK report has candidate-level
   evidence below the emission threshold.
4. Label each APK:
   - `true-no-signal-control` when source dependencies appear absent from APK
     DEX evidence or are intentionally compile/build-time only.
   - `identity-coverage-miss` when source runtime libraries likely appear in DEX
     but matcher/reference evidence is too weak to emit.
   - `needs-reference-db-experiment` only when a missing source-used version or
     family is the likely bottleneck.
5. Do not add components directly to SBOM output and do not tune global scoring
   from one row. Any fix must pass the current controlled/clean/partial control
   matrix.

## Suggested First Commands

```powershell
python -m json.tool data\results\evaluation\real-apk-source-validation-dashboard.json > $null
Select-String -Path docs\evaluation\APK_TYPE_EVALUATION.md -Pattern "source-validated-no-maven-signal" -Context 0,1
Get-Content data\results\source-validation\csv4\privacy-browser\docker-app-standardReleaseRuntimeClasspath-gradle9.5.txt -TotalCount 120
Get-Content data\results\evaluation\clean-real-apk-candidate-sweep-v4\report-real-privacy-browser\report.json -TotalCount 160
```

## Acceptance Gate

```text
no-Maven row -> stays control if DEX evidence is genuinely too weak
no-Maven row -> diagnostic issue if source runtime dependencies have clear DEX evidence but no emitted candidate
diagnostic -> experiment only; no shared DB/scoring promotion without current-control regression checks
```
