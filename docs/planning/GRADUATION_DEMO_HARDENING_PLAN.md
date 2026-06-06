# Graduation Demo Hardening Plan

## Objective

Make the APK intake flow safe for arbitrary graduation-day APKs. The tool should produce useful evidence, clear limits, and a reproducible report even when the APK is old, modern, obfuscated, native-heavy, framework-heavy, or missing source code.

The demo goal is not to claim perfect recovery for every APK. The goal is to show a flexible APK-to-SBOM workflow that:

- accepts a normal APK path,
- writes JSON, CycloneDX, Markdown, and HTML artifacts when analysis succeeds,
- explains offline/network and source-validation gaps,
- flags native, framework, and obfuscation boundaries,
- avoids calling an APK clean or source-validated without source evidence.

## Current Baseline

`apk_sbom.cli generate-report` already supports APK-only report generation. It can write matcher output, a CycloneDX SBOM, a JSON report, a Markdown report, and an HTML report. OSV lookup is optional, and source validation is accepted only as a separate JSON input.

The real-APK evaluation lane is now source-validation aware. Current thesis-facing docs record 91 source-validated real APKs and 0 current source-linked blocked APKs. That is good evidence for the evaluation chapter, but the live demo needs a separate hardening layer because a professor may provide an APK with no source tree, no dependency tree, no network, or framework/native code outside the Maven matching surface.

## Phase 1: APK-Only Safe Report Wrapper

Add a small wrapper script for live demos:

```powershell
python scripts\run_graduation_demo_report.py path\to\app.apk --output-dir data\results\graduation-demo\app
```

The wrapper should default to offline-safe behavior:

- do not query OSV unless `--query-osv` is explicitly passed,
- call the existing report generator with the calibrated combined reference DB,
- write `demo-readiness.json` and `demo-readiness.md`,
- classify the run as APK-only evidence, source-validation-aware evidence, framework/native boundary, obfuscation-risk boundary, no-Maven-signal, or failed-before-report,
- keep all claim boundaries visible.

Status: implemented in `scripts/run_graduation_demo_report.py`. The wrapper now writes `readiness_level`, `demo_outcome`, `supervisor_wording`, risk indicators, source-validation counts when supplied, and next-step guidance.

## Phase 2: Demo-Safe Readiness Summary

The readiness summary should answer the questions a supervisor is likely to ask:

- Did the APK parse?
- How many DEX files were analyzed?
- How many Maven components were detected?
- Were native libraries present?
- Was OSV run or intentionally skipped?
- Was source validation supplied?
- What is safe to claim from this run?
- What must be described as a limitation?

## Phase 3: Failure Handling

If report generation fails, the wrapper should still create a minimal readiness artifact that includes:

- APK path,
- output directory,
- failure status,
- exception type and message,
- the next suggested explanation for the demo.

This makes a live failure presentable instead of silent or confusing.

Status: implemented. The wrapper is fail-soft by default for live demos and still writes readiness artifacts if report generation raises an exception; `--strict-exit` preserves a non-zero exit code for CI or automation.

## Phase 4: Curated Demo Set

Keep a small set of known demo APKs:

- one clean/simple case with Maven evidence,
- one controlled vulnerable case,
- one real APK with partial/source-validation-aware evidence,
- one boundary case such as native-heavy or framework-heavy.

The curated set is for rehearsals. The wrapper remains the safety net for arbitrary APKs.

Status: refreshed. `docs/evaluation/GRADUATION_DEMO_REHEARSAL.md` now indexes the clean F-Droid proof, vulnerable Jackson proof, K-9/Jitsi partial-boundary proofs, Simplify limitation evidence, and a controlled APK-only smoke output under `data/results/graduation-demo/controlled-gson-smoke/`.

## Phase 5: Runbook And Supervisor Script

Update the runbook with:

- the default offline demo command,
- the optional OSV-enabled command,
- the source-validation-aware command,
- the exact wording for APK-only vs source-validated claims.

## Guardrails

- Do not claim source validation unless a source-validation artifact is supplied.
- Do not claim complete dependency recall for arbitrary APKs.
- Do not claim exact versions for uncertain candidates.
- Do not make network access required for the basic demo.
- Treat native libraries as hash-only file evidence unless a separate native analysis lane exists.
- Treat React Native, Flutter, Cordova, Unity, and similar frameworks as explicit boundary categories when the Maven signal is thin.

Current verification:

- `docker compose run --rm apk-sbom pytest tests/test_graduation_demo_report.py -q`
- `python -m compileall scripts\run_graduation_demo_report.py tests\test_graduation_demo_report.py`
- `python scripts\build_graduation_demo_rehearsal.py`

## Acceptance Criteria

- Any valid APK should either produce report artifacts or a minimal failure summary.
- OSV is optional and visibly marked as skipped when not run.
- APK-only reports clearly say they are not source-validated.
- Native/framework/obfuscation boundaries appear in the readiness summary.
- The implementation has focused tests for classification behavior.
- `python -m compileall src scripts tests` passes.
- `git diff --check` exits cleanly except for known repository line-ending warnings.
