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
| Source root | `data/source/csv9` |
| Validation root | `data/results/source-validation/csv9` |

## Per-APK Status

| App | Version | Proof status | Source | Gradle/dependency tree | Source validation | Next gate |
|---|---|---|---|---|---|---|
| ownCloud | 4.8.0 (48000000) | source-validated-partial | ok: `data/source/csv9/owncloud/source.tar.gz` | ok: validation-copy; 1 attempted config(s): `data/results/source-validation/csv9/owncloud/root1-owncloudApp-dependencies-originalReleaseRuntimeClasspath.txt` | ok: 7/22 confirmed, 14 mismatch(es), 1 missing: `data/results/source-validation/csv9/owncloud/source-validation/source-validation.md` | Record as source-validated partial; keep mismatches explicit. |

## Rules

- Source tarball checksum success is only a source-availability gate.
- Dependency-tree success is required before `validate-source-deps` can produce source-confirmed counts.
- Framework/native-heavy rows may remain limitation evidence even after source capture.
- Rows with blocked Gradle trees stay out of source-validated metrics.
