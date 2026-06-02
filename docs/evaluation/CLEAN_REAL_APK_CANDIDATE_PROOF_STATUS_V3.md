# Real APK Batch Proof Status

This batch artifact advances selected real APK rows through the same proof gates together.
It does not promote any row into source-validated accuracy metrics unless a runtime dependency tree and source-validation output exist.

## Summary

| Field | Value |
|---|---|
| Selected APKs | 1 |
| Source tarballs available | 0 |
| Dependency trees captured | 0 |
| Source validations completed | 0 |
| Script failures | 1 |
| Source root | `data/source/csv3` |
| Validation root | `data/results/source-validation/csv3` |

## Per-APK Status

| App | Version | Proof status | Source | Gradle/dependency tree | Source validation | Next gate |
|---|---|---|---|---|---|---|
| Simple Time Tracker | n/a (n/a) | failed | failed | unknown | unknown | Find source tag/repo proof or keep source-linked smoke only. |

## Rules

- Source tarball checksum success is only a source-availability gate.
- Dependency-tree success is required before `validate-source-deps` can produce source-confirmed counts.
- Framework/native-heavy rows may remain limitation evidence even after source capture.
- Rows with blocked Gradle trees stay out of source-validated metrics.
