# Real APK Batch Proof Status

This batch artifact advances selected real APK rows through the same proof gates together.
It does not promote any row into source-validated accuracy metrics unless a runtime dependency tree and source-validation output exist.

## Summary

| Field | Value |
|---|---|
| Selected APKs | 4 |
| Source tarballs available | 4 |
| Dependency trees captured | 4 |
| Source validations completed | 4 |
| Script failures | 0 |
| Source root | `data/source/clean-real-apk-candidate-sweep-v13` |
| Validation root | `data/results/source-validation/csv13` |

## Per-APK Status

| App | Version | Proof status | Source | Gradle/dependency tree | Source validation | Next gate |
|---|---|---|---|---|---|---|
| OpenTopoMap Viewer | 1.29 (66) | source-validated-partial | ok: `data/source/clean-real-apk-candidate-sweep-v13/opentopomap-viewer/source.tar.gz` | ok: 10 attempted config(s): `data/results/source-validation/csv13/opentopomap-viewer/root1-app-dependencies-fossReleaseRuntimeClasspath.txt` | ok: 13/22 confirmed, 9 mismatch(es), 0 missing: `data/results/source-validation/csv13/opentopomap-viewer/source-validation/source-validation.md` | Record as source-validated partial; keep mismatches explicit. |
| Railway station photos | 16.4.0 (97) | source-validated-partial | ok: `data/source/clean-real-apk-candidate-sweep-v13/railway-station-photos/source.tar.gz` | ok: 1 attempted config(s): `data/results/source-validation/csv13/railway-station-photos/root1-app-dependencies-releaseRuntimeClasspath.txt` | ok: 18/23 confirmed, 5 mismatch(es), 0 missing: `data/results/source-validation/csv13/railway-station-photos/source-validation/source-validation.md` | Record as source-validated partial; keep mismatches explicit. |
| LinkDroid for Linkwarden | 2.1.9 (26) | source-validated-partial | ok: `data/source/clean-real-apk-candidate-sweep-v13/linkdroid/source.tar.gz` | ok: 1 attempted config(s): `data/results/source-validation/csv13/linkdroid/root1-app-dependencies-releaseRuntimeClasspath.txt` | ok: 12/20 confirmed, 8 mismatch(es), 0 missing: `data/results/source-validation/csv13/linkdroid/source-validation/source-validation.md` | Record as source-validated partial; keep mismatches explicit. |
| Quasseldroid | 1.8.0 (1398) | source-validated-partial | ok: `data/source/clean-real-apk-candidate-sweep-v13/quasseldroid/source.tar.gz` | ok: 1 attempted config(s): `data/results/source-validation/csv13/quasseldroid/root1-app-dependencies-releaseRuntimeClasspath.txt` | ok: 14/17 confirmed, 3 mismatch(es), 0 missing: `data/results/source-validation/csv13/quasseldroid/source-validation/source-validation.md` | Record as source-validated partial; keep mismatches explicit. |

## Rules

- Source tarball checksum success is only a source-availability gate.
- Dependency-tree success is required before `validate-source-deps` can produce source-confirmed counts.
- Framework/native-heavy rows may remain limitation evidence even after source capture.
- Rows with blocked Gradle trees stay out of source-validated metrics.
