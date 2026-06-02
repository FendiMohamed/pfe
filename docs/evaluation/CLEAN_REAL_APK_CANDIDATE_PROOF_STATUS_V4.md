# Real APK Batch Proof Status

This batch artifact advances selected real APK rows through the same proof gates together.
It does not promote any row into source-validated accuracy metrics unless a runtime dependency tree and source-validation output exist.

## Summary

| Field | Value |
|---|---|
| Selected APKs | 1 |
| Source tarballs available | 1 |
| Dependency trees captured | 1 |
| Source validations completed | 1 |
| Script failures | 0 |
| Source root | `data/source/csv4` |
| Validation root | `data/results/source-validation/csv4` |

## Per-APK Status

| App | Version | Proof status | Source | Gradle/dependency tree | Source validation | Next gate |
|---|---|---|---|---|---|---|
| Privacy Browser | 3.20.1 (81) | source-validated-no-maven-signal | ok: `data/source/csv4/privacy-browser/source.tar.gz` | ok | ok: 0/0 confirmed, 0 mismatch(es), 0 missing: `data/results/source-validation/csv4/privacy-browser/source-validation-gradle9.5/source-validation.json` | Record as successful no-Maven-signal control; do not use as accuracy evidence. |

## Rules

- Source tarball checksum success is only a source-availability gate.
- Dependency-tree success is required before `validate-source-deps` can produce source-confirmed counts.
- Framework/native-heavy rows may remain limitation evidence even after source capture.
- Rows with blocked Gradle trees stay out of source-validated metrics.
