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
| Source root | `data/source/clean-real-apk-candidate-sweep-v15` |
| Validation root | `data/results/source-validation/csv15` |

## Per-APK Status

| App | Version | Proof status | Source | Gradle/dependency tree | Source validation | Next gate |
|---|---|---|---|---|---|---|
| Ultrasonic | 4.9.0 (131) | source-validated-partial | ok: `data/source/clean-real-apk-candidate-sweep-v15/ultrasonic/source.tar.gz` | ok: 1 attempted config(s): `data/results/source-validation/csv15/ultrasonic/root1-ultrasonic-dependencies-releaseRuntimeClasspath.txt` | ok: 12/39 confirmed, 10 mismatch(es), 17 missing: `data/results/source-validation/csv15/ultrasonic/source-validation/source-validation.md` | Record as source-validated partial; keep mismatches explicit. |
| RunnerUp | 2.11.0.1 (23000372) | source-validated-partial | ok: `data/source/clean-real-apk-candidate-sweep-v15/runnerup/source.tar.gz` | ok: 1 attempted config(s): `data/results/source-validation/csv15/runnerup/root1-app-dependencies-latestReleaseRuntimeClasspath.txt` | ok: 16/39 confirmed, 4 mismatch(es), 19 missing: `data/results/source-validation/csv15/runnerup/source-validation/source-validation.md` | Record as source-validated partial; keep mismatches explicit. |
| ImapNotes3 | v1.4-07 (10407) | source-validated-partial | ok: `data/source/clean-real-apk-candidate-sweep-v15/imapnotes3/source.tar.gz` | ok: 1 attempted config(s): `data/results/source-validation/csv15/imapnotes3/root1-ImapNotes3-dependencies-releaseRuntimeClasspath.txt` | ok: 11/39 confirmed, 6 mismatch(es), 22 missing: `data/results/source-validation/csv15/imapnotes3/source-validation/source-validation.md` | Record as source-validated partial; keep mismatches explicit. |

## Rules

- Source tarball checksum success is only a source-availability gate.
- Dependency-tree success is required before `validate-source-deps` can produce source-confirmed counts.
- Framework/native-heavy rows may remain limitation evidence even after source capture.
- Rows with blocked Gradle trees stay out of source-validated metrics.
