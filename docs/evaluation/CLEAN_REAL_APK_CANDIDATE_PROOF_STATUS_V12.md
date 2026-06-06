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
| Source root | `data/source/clean-real-apk-candidate-sweep-v12` |
| Validation root | `data/results/source-validation/csv12` |

## Per-APK Status

| App | Version | Proof status | Source | Gradle/dependency tree | Source validation | Next gate |
|---|---|---|---|---|---|---|
| Password Generator | 1.9.0 (48) | source-validated-partial | ok: `data/source/clean-real-apk-candidate-sweep-v12/password-generator/source.tar.gz` | ok: 1 attempted config(s): `data/results/source-validation/csv12/password-generator/root1-passwordgenerator-dependencies-releaseRuntimeClasspath.txt` | ok: 11/16 confirmed, 5 mismatch(es), 0 missing: `data/results/source-validation/csv12/password-generator/source-validation/source-validation.md` | Record as source-validated partial; keep mismatches explicit. |
| Todo Agenda | 4.13.3 (717) | source-validated-partial | ok: `data/source/clean-real-apk-candidate-sweep-v12/todo-agenda/source.tar.gz` | ok: validation-copy; 1 attempted config(s): `data/results/source-validation/csv12/todo-agenda/root1-app-dependencies-releaseRuntimeClasspath.txt` | ok: 10/16 confirmed, 6 mismatch(es), 0 missing: `data/results/source-validation/csv12/todo-agenda/source-validation/source-validation.md` | Record as source-validated partial; keep mismatches explicit. |
| Keep it up | 1.11.1 (20) | source-validated-partial | ok: `data/source/clean-real-apk-candidate-sweep-v12/keep-it-up/source.tar.gz` | ok: 1 attempted config(s): `data/results/source-validation/csv12/keep-it-up/root1-keepitupmain-dependencies-releaseRuntimeClasspath.txt` | ok: 3/5 confirmed, 1 mismatch(es), 1 missing: `data/results/source-validation/csv12/keep-it-up/source-validation/source-validation.md` | Record as source-validated partial; keep mismatches explicit. |
| c3nav | 4.7.0 (18040700) | source-validated-partial | ok: `data/source/clean-real-apk-candidate-sweep-v12/c3nav/source.tar.gz` | ok: 1 attempted config(s): `data/results/source-validation/csv12/c3nav/root1-app-dependencies-releaseRuntimeClasspath.txt` | ok: 7/14 confirmed, 7 mismatch(es), 0 missing: `data/results/source-validation/csv12/c3nav/source-validation/source-validation.md` | Record as source-validated partial; keep mismatches explicit. |

## Rules

- Source tarball checksum success is only a source-availability gate.
- Dependency-tree success is required before `validate-source-deps` can produce source-confirmed counts.
- Framework/native-heavy rows may remain limitation evidence even after source capture.
- Rows with blocked Gradle trees stay out of source-validated metrics.
