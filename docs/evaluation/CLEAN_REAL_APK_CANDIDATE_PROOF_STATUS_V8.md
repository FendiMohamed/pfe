# Real APK Batch Proof Status

This batch artifact advances selected real APK rows through the same proof gates together.
It does not promote any row into source-validated accuracy metrics unless a runtime dependency tree and source-validation output exist.

## Summary

| Field | Value |
|---|---|
| Selected APKs | 5 |
| Source tarballs available | 5 |
| Dependency trees captured | 3 |
| Source validations completed | 3 |
| Script failures | 0 |
| Source root | `data/source/csv8` |
| Validation root | `data/results/source-validation/csv8` |

## Per-APK Status

| App | Version | Proof status | Source | Gradle/dependency tree | Source validation | Next gate |
|---|---|---|---|---|---|---|
| Drift // Audio | 0.1.0 (1) | source-validated-partial | ok: `data/source/csv8/drift-audio/source.tar.gz` | ok: 1 attempted config(s): `data/results/source-validation/csv8/drift-audio/root1-app-dependencies-releaseRuntimeClasspath.txt` | ok: 7/13 confirmed, 6 mismatch(es), 0 missing: `data/results/source-validation/csv8/drift-audio/source-validation/source-validation.md` | Record as source-validated partial; keep mismatches explicit. |
| JaMuz | 0.6.14 (21) | source-validated-partial | ok: `data/source/csv8/jamuz/source.tar.gz` | ok: 1 attempted config(s): `data/results/source-validation/csv8/jamuz/root1-app-dependencies-releaseRuntimeClasspath.txt` | ok: 14/21 confirmed, 7 mismatch(es), 0 missing: `data/results/source-validation/csv8/jamuz/source-validation/source-validation.md` | Record as source-validated partial; keep mismatches explicit. |
| monocles browser | 1.9.3 (14) | source-validated-no-maven-signal | ok: `data/source/csv8/monocles-browser/source.tar.gz` | ok: 11 attempted config(s): `data/results/source-validation/csv8/monocles-browser/root1-app-dependencies-standardReleaseRuntimeClasspath.txt` | ok: 0/0 confirmed, 0 mismatch(es), 0 missing: `data/results/source-validation/csv8/monocles-browser/source-validation/source-validation.md` | Record as successful no-Maven-signal control; do not use as accuracy evidence. |
| Conceal Mobile | 5.0.4 (50) | gradle-blocked | ok: `data/source/csv8/conceal-mobile/source.tar.gz` | blocked: no attempted Gradle configuration succeeded; 180 attempted config(s) | blocked-until-dependency-tree: Run validate-source-deps after a runtime dependency tree is captured. | Investigate Gradle configuration/toolchain blocker. |
| Ltt.rs | 0.4.4 (19) | gradle-blocked | ok: `data/source/csv8/lttrs/source.tar.gz` | blocked: no attempted Gradle configuration succeeded; 60 attempted config(s) | blocked-until-dependency-tree: Run validate-source-deps after a runtime dependency tree is captured. | Investigate Gradle configuration/toolchain blocker. |

## Rules

- Source tarball checksum success is only a source-availability gate.
- Dependency-tree success is required before `validate-source-deps` can produce source-confirmed counts.
- Framework/native-heavy rows may remain limitation evidence even after source capture.
- Rows with blocked Gradle trees stay out of source-validated metrics.
