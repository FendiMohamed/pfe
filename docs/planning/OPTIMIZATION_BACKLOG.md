# MVP Optimization Backlog

Date: 2026-05-20.

This note records optimization ideas to revisit after the current APK-to-SBOM MVP remains stable. The goal is to improve the modular pipeline without reopening the approved architecture.

Current generated cons/improvement plan: `docs/planning/MVP_CONS_IMPROVEMENT_PLAN.md`.

## Work On Now

These items are low-risk because they improve reporting, extraction, or explainability without changing the core matching architecture.

Status: implemented on 2026-05-20. Keep this section as a record of what was considered MVP-safe and why.

| Priority | Improvement | Why it is suitable now |
|---:|---|---|
| 1 | APK extraction forensic summary | Demo-friendly and thesis-friendly. It shows whether the APK is normal, multidex, native-heavy, or suspicious before matching. |
| 2 | Manifest metadata + app package hint | Useful for reports and later app-code vs library-code separation. Keep it as metadata/hint first, not as a hard filter. |
| 3 | Candidate reason field in reports | Improves explainability. The matcher already computes package/class/method/opcode/CDG/literal evidence, so this mostly exposes existing data. |
| 4 | Obfuscation risk field | Useful if reported as a warning, not proof. It supports the R8 limitation story from the controlled evaluation and literature. |
| 5 | OSV severity/dedup | Improves vulnerability report quality with limited algorithmic risk if implemented defensively. |

Recommended safe order:

```text
1. APK extraction forensic summary
2. manifest metadata + app package hint
3. candidate reason field in reports
4. obfuscation risk field
5. OSV severity/dedup
```

## Work On Later

These are research-backed, but they touch feature extraction, storage, scoring, or evaluation more deeply. Do them after the thesis/demo MVP is packaged and stable.

| Priority | Improvement | Why later |
|---:|---|---|
| 6 | Maven POM dependency-coherence scoring | Implemented as a conservative close-tie rule on 2026-05-23. It only fires when another independently selected APK-side component supports a POM dependency version. |
| 7 | API-call/member-reference fingerprints | Feature extraction, reference DB storage, report/matcher CLI weighting, and a calibrated experiment were completed on 2026-05-24. Trial weight `0.05` caused no source-validation metric changes across F-Droid, OpenTracks, Aegis, Markor, and NewPipe, so keep default weight `0.0` until a more targeted scoring rule is designed. |
| 8 | Opcode n-grams | Research-backed and useful under obfuscation, but heavier than current opcode histograms. Needs schema, scoring, and evaluation work. |

## Evidence Basis

- APK extraction and manifest/resource metadata fit the approved pipeline: `APK -> extract DEX, manifest, resources, strings, native files`.
- App/library separation is supported by LibSift and LibD-style segmentation ideas.
- Candidate reasons and confidence evidence align with CycloneDX/CISA expectations for explainable SBOM output.
- Obfuscation risk is supported by LibHunter, LibAttention, and robustness studies showing R8/shrinking makes exact version detection fragile.
- API-call fingerprints and opcode n-grams are supported by LibID, LibScan, ATVHunter, and related opcode/CFG-based detection work.
- Maven POM dependency metadata follows the reference-database/SBOM logic: package versions should be interpreted with dependency context, but the APK-side bytecode evidence must remain the primary signal.
- OSV severity/dedup improves the vulnerability layer while preserving the current OSV-first tooling decision.
