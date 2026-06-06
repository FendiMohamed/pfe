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
| Source root | `data/source/clean-real-apk-candidate-sweep-v16` |
| Validation root | `data/results/source-validation/csv16` |

## Per-APK Status

| App | Version | Proof status | Source | Gradle/dependency tree | Source validation | Next gate |
|---|---|---|---|---|---|---|
| Password Master | 1.5.1 (15) | source-validated-partial | ok: `data/source/clean-real-apk-candidate-sweep-v16/password-master/source.tar.gz` | ok: 1 attempted config(s): `data/results/source-validation/csv16/password-master/root1-passwordmaster-dependencies-releaseRuntimeClasspath.txt` | ok: 13/18 confirmed, 5 mismatch(es), 0 missing: `data/results/source-validation/csv16/password-master/source-validation/source-validation.md` | Record as source-validated partial; keep mismatches explicit. |

## Rules

- Source tarball checksum success is only a source-availability gate.
- Dependency-tree success is required before `validate-source-deps` can produce source-confirmed counts.
- Framework/native-heavy rows may remain limitation evidence even after source capture.
- Rows with blocked Gradle trees stay out of source-validated metrics.
