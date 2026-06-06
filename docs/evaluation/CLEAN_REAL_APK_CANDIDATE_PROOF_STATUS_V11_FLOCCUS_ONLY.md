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
| Source root | `data/source/csv11` |
| Validation root | `data/results/source-validation/csv11` |

## Per-APK Status

| App | Version | Proof status | Source | Gradle/dependency tree | Source validation | Next gate |
|---|---|---|---|---|---|---|
| floccus bookmark sync | 5.9.1 (5009001) | source-validated-partial | ok: `data/source/csv11/floccus/source.tar.gz` | ok: 1 attempted config(s): `data/results/source-validation/csv11/floccus/root1-app-dependencies-releaseRuntimeClasspath.txt` | ok: 9/13 confirmed, 4 mismatch(es), 0 missing: `data/results/source-validation/csv11/floccus/source-validation/source-validation.md` | Record as source-validated partial; keep mismatches explicit. |

## Rules

- Source tarball checksum success is only a source-availability gate.
- Dependency-tree success is required before `validate-source-deps` can produce source-confirmed counts.
- Framework/native-heavy rows may remain limitation evidence even after source capture.
- Rows with blocked Gradle trees stay out of source-validated metrics.
