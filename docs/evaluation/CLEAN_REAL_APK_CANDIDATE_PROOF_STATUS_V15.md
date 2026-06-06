# Real APK Batch Proof Status

This batch artifact advances selected real APK rows through the same proof gates together.
It does not promote any row into source-validated accuracy metrics unless a runtime dependency tree and source-validation output exist.

## Summary

| Field | Value |
|---|---|
| Selected APKs | 8 |
| Source tarballs available | 8 |
| Dependency trees captured | 8 |
| Source validations completed | 8 |
| Script failures | 0 |
| Source root | `data/source/clean-real-apk-candidate-sweep-v15` |
| Validation root | `data/results/source-validation/csv15` |

## Per-APK Status

| App | Version | Proof status | Source | Gradle/dependency tree | Source validation | Next gate |
|---|---|---|---|---|---|---|
| Clock | 2.29 (2032) | source-validated-partial | ok: `data/source/clean-real-apk-candidate-sweep-v15/clock/source.tar.gz` | ok: 1 attempted config(s): `data/results/source-validation/csv15/clock/root1-app-dependencies-releaseRuntimeClasspath.txt` | ok: 11/38 confirmed, 6 mismatch(es), 21 missing: `data/results/source-validation/csv15/clock/source-validation/source-validation.md` | Record as source-validated partial; keep mismatches explicit. |
| Poet Assistant | 1.31.1 (113101) | source-validated-partial | ok: `data/source/clean-real-apk-candidate-sweep-v15/poet-assistant/source.tar.gz` | ok: validation-copy; 1 attempted config(s): `data/results/source-validation/csv15/poet-assistant/root1-app-dependencies-releaseRuntimeClasspath.txt` | ok: 7/37 confirmed, 9 mismatch(es), 21 missing: `data/results/source-validation/csv15/poet-assistant/source-validation/source-validation.md` | Record as source-validated partial; keep mismatches explicit. |
| Ultrasonic | 4.9.0 (131) | source-validated-partial | ok: `data/source/clean-real-apk-candidate-sweep-v15/ultrasonic/source.tar.gz` | ok: 1 attempted config(s): `data/results/source-validation/csv15/ultrasonic/root1-ultrasonic-dependencies-releaseRuntimeClasspath.txt` | ok: 12/39 confirmed, 10 mismatch(es), 17 missing: `data/results/source-validation/csv15/ultrasonic/source-validation/source-validation.md` | Record as source-validated partial; keep mismatches explicit. |
| FTPClient | 3.0.1 (27) | source-validated-partial | ok: `data/source/clean-real-apk-candidate-sweep-v15/ftpclient/source.tar.gz` | ok: 1 attempted config(s): `data/results/source-validation/csv15/ftpclient/root1-app-dependencies-releaseRuntimeClasspath.txt` | ok: 13/39 confirmed, 4 mismatch(es), 22 missing: `data/results/source-validation/csv15/ftpclient/source-validation/source-validation.md` | Record as source-validated partial; keep mismatches explicit. |
| RunnerUp | 2.11.0.1 (23000372) | source-validated-partial | ok: `data/source/clean-real-apk-candidate-sweep-v15/runnerup/source.tar.gz` | ok: 1 attempted config(s): `data/results/source-validation/csv15/runnerup/root1-app-dependencies-latestReleaseRuntimeClasspath.txt` | ok: 16/39 confirmed, 4 mismatch(es), 19 missing: `data/results/source-validation/csv15/runnerup/source-validation/source-validation.md` | Record as source-validated partial; keep mismatches explicit. |
| Json List | 1.10 (1000) | source-validated-partial | ok: `data/source/clean-real-apk-candidate-sweep-v15/json-list/source.tar.gz` | ok: 1 attempted config(s): `data/results/source-validation/csv15/json-list/root1-app-dependencies-releaseRuntimeClasspath.txt` | ok: 14/38 confirmed, 5 mismatch(es), 19 missing: `data/results/source-validation/csv15/json-list/source-validation/source-validation.md` | Record as source-validated partial; keep mismatches explicit. |
| ImapNotes3 | v1.4-07 (10407) | source-validated-partial | ok: `data/source/clean-real-apk-candidate-sweep-v15/imapnotes3/source.tar.gz` | ok: 1 attempted config(s): `data/results/source-validation/csv15/imapnotes3/root1-ImapNotes3-dependencies-releaseRuntimeClasspath.txt` | ok: 11/39 confirmed, 6 mismatch(es), 22 missing: `data/results/source-validation/csv15/imapnotes3/source-validation/source-validation.md` | Record as source-validated partial; keep mismatches explicit. |
| Forecastie | 1.23 (75) | source-validated-partial | ok: `data/source/clean-real-apk-candidate-sweep-v15/forecastie/source.tar.gz` | ok: 1 attempted config(s): `data/results/source-validation/csv15/forecastie/root1-app-dependencies-releaseRuntimeClasspath.txt` | ok: 3/37 confirmed, 10 mismatch(es), 24 missing: `data/results/source-validation/csv15/forecastie/source-validation/source-validation.md` | Record as source-validated partial; keep mismatches explicit. |

## Rules

- Source tarball checksum success is only a source-availability gate.
- Dependency-tree success is required before `validate-source-deps` can produce source-confirmed counts.
- Framework/native-heavy rows may remain limitation evidence even after source capture.
- Rows with blocked Gradle trees stay out of source-validated metrics.
