# Real APK Batch Proof Status

This batch artifact advances selected real APK rows through the same proof gates together.
It does not promote any row into source-validated accuracy metrics unless a runtime dependency tree and source-validation output exist.

## Summary

| Field | Value |
|---|---|
| Selected APKs | 3 |
| Source tarballs available | 3 |
| Dependency trees captured | 3 |
| Source validations completed | 3 |
| Script failures | 0 |
| Source root | `data/source/clean-real-apk-candidate-sweep-v14` |
| Validation root | `data/results/source-validation/csv14` |

## Per-APK Status

| App | Version | Proof status | Source | Gradle/dependency tree | Source validation | Next gate |
|---|---|---|---|---|---|---|
| Baby Books | 0.9.2 (12) | source-validated-partial | ok: `data/source/clean-real-apk-candidate-sweep-v14/baby-books/source.tar.gz` | ok: validation-copy; 1 attempted config(s): `data/results/source-validation/csv14/baby-books/root1-android-dependencies-releaseRuntimeClasspath.txt` | ok: 10/29 confirmed, 18 mismatch(es), 1 missing: `data/results/source-validation/csv14/baby-books/source-validation/source-validation.md` | Record as source-validated partial; keep mismatches explicit. |
| Odysee | 0.0.124 (124) | source-validated-partial | ok: `data/source/clean-real-apk-candidate-sweep-v14/odysee/source.tar.gz` | ok: validation-copy; 1 attempted config(s): `data/results/source-validation/csv14/odysee/root1-app-dependencies-releaseRuntimeClasspath.txt` | ok: 10/15 confirmed, 5 mismatch(es), 0 missing: `data/results/source-validation/csv14/odysee/source-validation/source-validation.md` | Record as source-validated partial; keep mismatches explicit. |
| RadarWeather | 6.7 (67) | source-validated-partial | ok: `data/source/clean-real-apk-candidate-sweep-v14/radarweather/source.tar.gz` | ok: validation-copy; 1 attempted config(s): `data/results/source-validation/csv14/radarweather/root1-app-dependencies-releaseRuntimeClasspath.txt` | ok: 5/17 confirmed, 12 mismatch(es), 0 missing: `data/results/source-validation/csv14/radarweather/source-validation/source-validation.md` | Record as source-validated partial; keep mismatches explicit. |

## Rules

- Source tarball checksum success is only a source-availability gate.
- Dependency-tree success is required before `validate-source-deps` can produce source-confirmed counts.
- Framework/native-heavy rows may remain limitation evidence even after source capture.
- Rows with blocked Gradle trees stay out of source-validated metrics.
