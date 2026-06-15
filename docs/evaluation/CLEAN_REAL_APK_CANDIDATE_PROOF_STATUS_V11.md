# Real APK Batch Proof Status

This batch artifact advances selected real APK rows through the same proof gates together.
It does not promote any row into source-validated accuracy metrics unless a runtime dependency tree and source-validation output exist.

## Summary

| Field | Value |
|---|---|
| Selected APKs | 5 |
| Source tarballs available | 5 |
| Dependency trees captured | 5 |
| Source validations completed | 5 |
| Script failures | 0 |
| Source root | `data/source/csv11` |
| Validation root | `data/results/source-validation/csv11` |

## Per-APK Status

| App | Version | Proof status | Source | Gradle/dependency tree | Source validation | Next gate |
|---|---|---|---|---|---|---|
| floccus bookmark sync | 5.9.1 (5009001) | source-validated-partial | ok: `data/source/csv11/floccus/source.tar.gz` | ok: 1 attempted config(s): `data/results/source-validation/csv11/floccus/root1-app-dependencies-releaseRuntimeClasspath.txt` | ok: 9/13 confirmed, 4 mismatch(es), 0 missing: `data/results/source-validation/csv11/floccus/source-validation/source-validation.md` | Record as source-validated partial; keep mismatches explicit. |
| Waistline | 3.10.1 (31001) | source-validated-partial | ok: `data/source/csv11/waistline/source.tar.gz` | ok: validation-copy; 1 attempted config(s): `data/results/source-validation/csv11/waistline/root1-app-dependencies-releaseRuntimeClasspath.txt` | ok: 9/15 confirmed, 6 mismatch(es), 0 missing: `data/results/source-validation/csv11/waistline/source-validation/source-validation.md` | Record as source-validated partial; keep mismatches explicit. |
| OpenCloud | 1.2.3 (9) | source-validated-partial | ok: `data/source/csv11/opencloud/source.tar.gz` | ok: validation-copy; 1 attempted config(s): `data/results/source-validation/csv11/opencloud/root1-opencloudApp-dependencies-originalReleaseRuntimeClasspath.txt` | ok: 8/22 confirmed, 14 mismatch(es), 0 missing: `data/results/source-validation/csv11/opencloud/source-validation/source-validation.md` | Record as source-validated partial; keep mismatches explicit. |
| NightDream | 2.11.26 (348) | source-validated-partial | ok: `data/source/csv11/nightdream/source.tar.gz` | ok: 7 attempted config(s): `data/results/source-validation/csv11/nightdream/root1-app-dependencies-fullReleaseRuntimeClasspath.txt` | ok: 15/21 confirmed, 6 mismatch(es), 0 missing: `data/results/source-validation/csv11/nightdream/source-validation/source-validation.md` | Record as source-validated partial; keep mismatches explicit. |
| SambaLite | 2.5.1 (20501) | source-validated-partial | ok: `data/source/csv11/sambalite/source.tar.gz` | ok: 2 attempted config(s): `data/results/source-validation/csv11/sambalite/root1-app-dependencies-debugRuntimeClasspath.txt` | ok: 16/19 confirmed, 3 mismatch(es), 0 missing: `data/results/source-validation/csv11/sambalite/source-validation/source-validation.md` | Record as source-validated partial; keep mismatches explicit. |

## Rules

- Source tarball checksum success is only a source-availability gate.
- Dependency-tree success is required before `validate-source-deps` can produce source-confirmed counts.
- Framework/native-heavy rows may remain limitation evidence even after source capture.
- Rows with blocked Gradle trees stay out of source-validated metrics.
