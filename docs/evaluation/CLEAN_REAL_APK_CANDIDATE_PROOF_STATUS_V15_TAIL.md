# Real APK Batch Proof Status

This batch artifact advances selected real APK rows through the same proof gates together.
It does not promote any row into source-validated accuracy metrics unless a runtime dependency tree and source-validation output exist.

## Summary

| Field | Value |
|---|---|
| Selected APKs | 3 |
| Source tarballs available | 3 |
| Dependency trees captured | 2 |
| Source validations completed | 2 |
| Script failures | 0 |
| Source root | `data/source/clean-real-apk-candidate-sweep-v15` |
| Validation root | `data/results/source-validation/csv15` |

## Per-APK Status

| App | Version | Proof status | Source | Gradle/dependency tree | Source validation | Next gate |
|---|---|---|---|---|---|---|
| Json List | 1.10 (1000) | source-validated-partial | ok: `data/source/clean-real-apk-candidate-sweep-v15/json-list/source.tar.gz` | ok: 1 attempted config(s): `data/results/source-validation/csv15/json-list/root1-app-dependencies-releaseRuntimeClasspath.txt` | ok: 14/38 confirmed, 5 mismatch(es), 19 missing: `data/results/source-validation/csv15/json-list/source-validation/source-validation.md` | Record as source-validated partial; keep mismatches explicit. |
| ImapNotes3 | v1.4-07 (10407) | gradle-blocked | ok: `data/source/clean-real-apk-candidate-sweep-v15/imapnotes3/source.tar.gz` | blocked: no attempted Gradle configuration succeeded; 60 attempted config(s) | blocked-until-dependency-tree: Run validate-source-deps after a runtime dependency tree is captured. | Investigate Gradle configuration/toolchain blocker. |
| Forecastie | 1.23 (75) | source-validated-partial | ok: `data/source/clean-real-apk-candidate-sweep-v15/forecastie/source.tar.gz` | ok: 1 attempted config(s): `data/results/source-validation/csv15/forecastie/root1-app-dependencies-releaseRuntimeClasspath.txt` | ok: 3/37 confirmed, 10 mismatch(es), 24 missing: `data/results/source-validation/csv15/forecastie/source-validation/source-validation.md` | Record as source-validated partial; keep mismatches explicit. |

## Rules

- Source tarball checksum success is only a source-availability gate.
- Dependency-tree success is required before `validate-source-deps` can produce source-confirmed counts.
- Framework/native-heavy rows may remain limitation evidence even after source capture.
- Rows with blocked Gradle trees stay out of source-validated metrics.
