# Clean Real APK Candidate Proof Results V11

This v11 sweep continued the clean non-sparse F-Droid search after v10. It adds report evidence for five no-native, source-linked candidates and promotes five honest source-validated partial rows.

## Summary

| Field | Value |
|---|---:|
| Selected candidates | 5 |
| APKs downloaded and SHA-256 verified | 5 |
| Reports generated | 5 |
| Runtime dependency trees captured | 5 |
| Source validations completed | 5 |
| Rows promoted to source-validated metrics | 5 |

## Candidate Outcomes

| App | Version | DEX | Native `.so` | SBOM Maven components | Proof outcome | Metric outcome |
|---|---|---:|---:|---:|---|---|
| floccus bookmark sync | 5.9.1 | 2 | 0 | 13 | Source tarball verified; a floccus-specific proof hint narrowed Gradle probing to `:app:dependencies`; Docker captured `releaseRuntimeClasspath`; source validation confirms 9/13 emitted Maven versions, with 4 version mismatches and 0 missing coordinates. | Source-validated partial; admitted to partial metrics only. |
| Waistline | 3.10.1 | 1 | 0 | 15 | Source tarball verified; a Cordova blocker-rescue profile cloned only `platforms/android`, added Docker SDK `local.properties`, imported Cordova's Groovy `XmlParser`, aligned build-tools metadata with Docker build-tools 36.0.0, replaced the plugin `jcenter()` repository call with the archived Maven URL, and captured `:app` `releaseRuntimeClasspath`; source validation confirms 9/15 emitted Maven versions, with 6 version mismatches and 0 missing coordinates. | Source-validated partial; admitted to partial metrics only. |
| OpenCloud | 1.2.3 | 3 | 0 | 22 | Source tarball verified; a blocker-rescue profile created a validation-only source copy, disabled KSP/Kotlin/Parcelize/Detekt/Sonar build-time plugins only for dependency-tree capture, preserved runtime dependencies, and captured `:opencloudApp` `originalReleaseRuntimeClasspath`; source validation confirms 8/22 emitted Maven versions, with 14 version mismatches and 0 missing coordinates. | Source-validated partial; admitted to partial metrics only. |
| NightDream | 2.11.26 | 2 | 0 | 21 | Source tarball verified; Docker captured `:app` `fullReleaseRuntimeClasspath`; source validation confirms 15/21 emitted Maven versions, with 6 version mismatches and 0 missing coordinates. | Source-validated partial; admitted to partial metrics only. |
| SambaLite | 2.5.1 | 2 | 0 | 19 | Source tarball verified; Docker captured `:app` `debugRuntimeClasspath`; source validation confirms 16/19 emitted Maven versions, with 3 version mismatches and 0 missing coordinates. | Source-validated partial; admitted to partial metrics only. |

## Evidence Artifacts

- Selection: `configs/real_apk_clean_candidate_selection_v11.json`
- Sweep summary: `docs/evaluation/CLEAN_REAL_APK_CANDIDATE_SWEEP_V11.md`
- Sweep JSON: `data/results/evaluation/clean-real-apk-candidate-sweep-v11.json`
- Report root: `data/results/evaluation/clean-real-apk-candidate-sweep-v11/`
- Proof status: `docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_STATUS_V11.md`
- Proof JSON: `data/results/evaluation/clean-real-apk-candidate-sweep-v11-proof-status.json`
- Source/proof roots: `data/source/csv11/`, `data/results/source-validation/csv11/`

## Decision

floccus, Waistline, OpenCloud, SambaLite, and NightDream are admitted as source-validated partial evidence. Do not count them as clean: all five have source-confirmed coordinate identity with remaining version mismatches. The clean non-sparse bucket remains open.

The best immediate continuation is either:

1. start a v12 clean/non-sparse F-Droid sweep with the same proof gates;
2. generalize the blocker rescue profiles for the remaining repeated Gradle classes; or
3. target one of the remaining source-linked blocked rows if build-system diversity evidence is more valuable than adding another sweep.
