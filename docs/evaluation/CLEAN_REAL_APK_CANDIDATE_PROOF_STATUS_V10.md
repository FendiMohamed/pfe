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
| Source root | `data/source/csv10` |
| Validation root | `data/results/source-validation/csv10` |

## Per-APK Status

| App | Version | Proof status | Source | Gradle/dependency tree | Source validation | Next gate |
|---|---|---|---|---|---|---|
| Etar - OpenSource Calendar | 1.0.55 (55) | source-validated-partial | ok: `data/source/csv10/etar/source.tar.gz` | ok: 1 attempted config(s): `data/results/source-validation/csv10/etar/root1-app-dependencies-releaseRuntimeClasspath.txt` | ok: 15/38 confirmed, 2 mismatch(es), 21 missing: `data/results/source-validation/csv10/etar/source-validation/source-validation.md` | Record as source-validated partial; keep mismatches explicit. |
| RadioDroid | 0.86 (96) | source-validated-partial | ok: `data/source/csv10/radiodroid/source.tar.gz` | ok: validation-copy; 1 attempted config(s): `data/results/source-validation/csv10/radiodroid/root1-app-dependencies-freeReleaseRuntimeClasspath.txt` | ok: 5/39 confirmed, 15 mismatch(es), 19 missing: `data/results/source-validation/csv10/radiodroid/source-validation/source-validation.md` | Record as source-validated partial; keep mismatches explicit. |
| SimpleLogin Anti-spam | 1.22.0 (12200) | source-validated-partial | ok: `data/source/csv10/simplelogin/source.tar.gz` | ok: validation-copy; 1 attempted config(s): `data/results/source-validation/csv10/simplelogin/root1-app-dependencies-fdroidReleaseRuntimeClasspath.txt` | ok: 9/39 confirmed, 13 mismatch(es), 17 missing: `data/results/source-validation/csv10/simplelogin/source-validation/source-validation.md` | Record as source-validated partial; keep mismatches explicit. |
| Omni Notes | 6.3.1 (331) | source-validated-partial | ok: `data/source/csv10/omni-notes/source.tar.gz` | ok: validation-copy; 1 attempted config(s): `data/results/source-validation/csv10/omni-notes/root1-omniNotes-dependencies-fossReleaseRuntimeClasspath.txt` | ok: 4/39 confirmed, 16 mismatch(es), 19 missing: `data/results/source-validation/csv10/omni-notes/source-validation/source-validation.md` | Record as source-validated partial; keep mismatches explicit. |
| Primitive FTPd | 8.1 (70) | source-validated-partial | ok: `data/source/csv10/primitive-ftpd/source.tar.gz` | ok: 1 attempted config(s): `data/results/source-validation/csv10/primitive-ftpd/root1-primitiveFTPd-dependencies-releaseRuntimeClasspath.txt` | ok: 12/38 confirmed, 4 mismatch(es), 22 missing: `data/results/source-validation/csv10/primitive-ftpd/source-validation/source-validation.md` | Record as source-validated partial; keep mismatches explicit. |

## Rules

- Source tarball checksum success is only a source-availability gate.
- Dependency-tree success is required before `validate-source-deps` can produce source-confirmed counts.
- Framework/native-heavy rows may remain limitation evidence even after source capture.
- Rows with blocked Gradle trees stay out of source-validated metrics.
