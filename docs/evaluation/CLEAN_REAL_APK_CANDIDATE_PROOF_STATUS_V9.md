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
| Source root | `data/source/csv9` |
| Validation root | `data/results/source-validation/csv9` |

## Per-APK Status

| App | Version | Proof status | Source | Gradle/dependency tree | Source validation | Next gate |
|---|---|---|---|---|---|---|
| DoliDroid | 3.0.69 (69) | source-validated-partial | ok: `data/source/csv9/dolidroid/source.tar.gz` | ok: validation-copy; 1 attempted config(s): `data/results/source-validation/csv9/dolidroid/root1-app-dependencies-releaseRuntimeClasspath.txt` | ok: 7/14 confirmed, 7 mismatch(es), 0 missing: `data/results/source-validation/csv9/dolidroid/source-validation/source-validation.md` | Record as source-validated partial; keep mismatches explicit. |
| ownCloud | 4.8.0 (48000000) | source-validated-partial | ok: `data/source/csv9/owncloud/source.tar.gz` | ok: validation-copy; 1 attempted config(s): `data/results/source-validation/csv9/owncloud/root1-owncloudApp-dependencies-originalReleaseRuntimeClasspath.txt` | ok: 7/22 confirmed, 14 mismatch(es), 1 missing: `data/results/source-validation/csv9/owncloud/source-validation/source-validation.md` | Record as source-validated partial; keep mismatches explicit. |
| Your local weather | 6.4.0-FOSS (193) | source-validated-partial | ok: `data/source/csv9/your-local-weather/source.tar.gz` | ok: 10 attempted config(s): `data/results/source-validation/csv9/your-local-weather/root1-app-dependencies-fossReleaseRuntimeClasspath.txt` | ok: 15/17 confirmed, 2 mismatch(es), 0 missing: `data/results/source-validation/csv9/your-local-weather/source-validation/source-validation.md` | Record as source-validated partial; keep mismatches explicit. |
| OpenKeychain: Easy PGP | 6.0.4 (60400) | source-validated-partial | ok: `data/source/csv9/openkeychain/source.tar.gz` | ok: validation-copy; 1 attempted config(s): `data/results/source-validation/csv9/openkeychain/root1-OpenKeychain-dependencies-releaseRuntimeClasspath.txt` | ok: 5/12 confirmed, 7 mismatch(es), 0 missing: `data/results/source-validation/csv9/openkeychain/source-validation/source-validation.md` | Record as source-validated partial; keep mismatches explicit. |
| HomeFeed - RSS Widget | 1.3.0 (4) | source-validated-partial | ok: `data/source/csv9/homefeed-rss-widget/source.tar.gz` | ok: 1 attempted config(s): `data/results/source-validation/csv9/homefeed-rss-widget/root1-app-dependencies-releaseRuntimeClasspath.txt` | ok: 11/17 confirmed, 6 mismatch(es), 0 missing: `data/results/source-validation/csv9/homefeed-rss-widget/source-validation/source-validation.md` | Record as source-validated partial; keep mismatches explicit. |

## Rules

- Source tarball checksum success is only a source-availability gate.
- Dependency-tree success is required before `validate-source-deps` can produce source-confirmed counts.
- Framework/native-heavy rows may remain limitation evidence even after source capture.
- Rows with blocked Gradle trees stay out of source-validated metrics.
