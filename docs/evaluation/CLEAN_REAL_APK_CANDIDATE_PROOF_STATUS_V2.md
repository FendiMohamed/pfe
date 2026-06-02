# Real APK Batch Proof Status

This batch artifact advances selected real APK rows through the same proof gates together.
It does not promote any row into source-validated accuracy metrics unless a runtime dependency tree and source-validation output exist.

## Summary

| Field | Value |
|---|---|
| Selected APKs | 1 |
| Source tarballs available | 1 |
| Dependency trees captured | 0 |
| Source validations completed | 0 |
| Script failures | 0 |
| Source root | `data/source/clean-real-apk-candidate-sweep-v2` |
| Validation root | `data/results/source-validation/clean-real-apk-candidate-sweep-v2` |

## Per-APK Status

| App | Version | Proof status | Source | Gradle/dependency tree | Source validation | Next gate |
|---|---|---|---|---|---|---|
| Gotify | 2.10.0 (35) | gradle-blocked | ok: `data/source/clean-real-apk-candidate-sweep-v2/gotify/source.tar.gz` | blocked: Gradle command unavailable; 1 attempted config(s) | blocked-until-dependency-tree: Run validate-source-deps after a runtime dependency tree is captured. | Investigate Gradle configuration/toolchain blocker. |

## Rules

- Source tarball checksum success is only a source-availability gate.
- Dependency-tree success is required before `validate-source-deps` can produce source-confirmed counts.
- Framework/native-heavy rows may remain limitation evidence even after source capture.
- Rows with blocked Gradle trees stay out of source-validated metrics.
