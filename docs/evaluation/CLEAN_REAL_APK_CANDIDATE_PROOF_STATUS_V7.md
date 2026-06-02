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
| Source root | `data/source/csv7` |
| Validation root | `data/results/source-validation/csv7` |

## Per-APK Status

| App | Version | Proof status | Source | Gradle/dependency tree | Source validation | Next gate |
|---|---|---|---|---|---|---|
| AndStatus | 62.03 (370) | source-validated | ok: `data/source/csv7/andstatus/source.tar.gz` | ok: `data/results/source-validation/csv7/andstatus/docker-app-releaseRuntimeClasspath-gradle8.13.txt` | ok: 12/19 confirmed, 7 mismatch(es), 0 missing: `data/results/source-validation/csv7/andstatus/source-validation-gradle8.13/source-validation.md` | Record as source-validated partial; keep mismatches explicit. |
| Fulguris Web Browser | 2.0.10 (261) | source-validated | ok: `data/source/csv7/fulguris-web-browser/source.tar.gz` | ok: `data/results/source-validation/csv7/fulguris-web-browser/docker-app-slionsFullFdroidReleaseRuntimeClasspath-gradle8.14.3.txt` | ok: 17/21 confirmed, 4 mismatch(es), 0 missing: `data/results/source-validation/csv7/fulguris-web-browser/source-validation-gradle8.14.3/source-validation.md` | Record as source-validated partial; keep mismatches explicit. |
| I2P | 2.11.0 (4745304) | source-validated | ok: `data/source/csv7/i2p/source.tar.gz` | ok: `data/results/source-validation/csv7/i2p/docker-app-legacyReleaseRuntimeClasspath-gradle8.13.txt` | ok: 10/18 confirmed, 8 mismatch(es), 0 missing: `data/results/source-validation/csv7/i2p/source-validation-gradle8.13/source-validation.md` | Record as source-validated partial; keep mismatches explicit. |
| Working Time Account | 2.11.012 (211012) | source-validated | ok: `data/source/csv7/working-time-account/source.tar.gz` | ok: `data/results/source-validation/csv7/working-time-account/docker-app-releaseRuntimeClasspath-gradle9.5.txt` | ok: 12/15 confirmed, 3 mismatch(es), 0 missing: `data/results/source-validation/csv7/working-time-account/source-validation-gradle9.5/source-validation.md` | Record as source-validated partial; keep mismatches explicit. |
| Mastodon | 2.12.3 (182) | source-validated-no-maven-signal | ok: `data/source/csv7/mastodon/source.tar.gz` | ok: `data/results/source-validation/csv7/mastodon/docker-mastodon-releaseRuntimeClasspath-gradle8.13.txt` | ok: 0/0 confirmed, 0 mismatch(es), 0 missing: `data/results/source-validation/csv7/mastodon/source-validation-gradle8.13/source-validation.md` | Record as successful no-Maven-signal control; do not use as accuracy evidence. |

## Rules

- Source tarball checksum success is only a source-availability gate.
- Dependency-tree success is required before `validate-source-deps` can produce source-confirmed counts.
- Framework/native-heavy rows may remain limitation evidence even after source capture.
- Rows with blocked Gradle trees stay out of source-validated metrics.
