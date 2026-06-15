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
| Source root | `data/source/csv5` |
| Validation root | `data/results/source-validation/csv5` |

## Per-APK Status

| App | Version | Proof status | Source | Gradle/dependency tree | Source validation | Next gate |
|---|---|---|---|---|---|---|
| yetCalc | 2.0.8 (24) | source-validated | ok: `data/source/csv5/yetcalc/source.tar.gz` | ok: `data/results/source-validation/csv5/yetcalc/docker-app-releaseRuntimeClasspath-gradle8.13.txt` | ok: 6/17 confirmed, 11 mismatch(es), 0 missing: `data/results/source-validation/csv5/yetcalc/source-validation-gradle8.13/source-validation.md` | Record as source-validated partial; keep mismatches explicit. |
| Loop Habit Tracker | 2.3.1 (20301) | source-validated | ok: `data/source/csv5/loop-habit-tracker/source.tar.gz` | ok: `data/results/source-validation/csv5/loop-habit-tracker/docker-uhabits-android-releaseRuntimeClasspath-gradle8.14.3.txt` | ok: 7/11 confirmed, 4 mismatch(es), 0 missing: `data/results/source-validation/csv5/loop-habit-tracker/source-validation-gradle8.14.3/source-validation.md` | Record as source-validated partial; keep mismatches explicit. |
| QuickDic | 5.8.2 (131) | source-validated-clean | ok: `data/source/csv5/quickdic/source.tar.gz` | ok: `data/results/source-validation/csv5/quickdic/docker-root-releaseRuntimeClasspath-gradle8.14.3.txt` | ok: 2/2 confirmed, 0 mismatch(es), 0 missing: `data/results/source-validation/csv5/quickdic/source-validation-gradle8.14.3/source-validation.md` | Eligible for clean source-validated metrics after doc admission. |
| Cirrus | 4.7 (47) | source-validated | ok: `data/source/csv5/cirrus/source.tar.gz` | ok: `data/results/source-validation/csv5/cirrus/docker-app-releaseRuntimeClasspath-gradle8.13.txt` | ok: 14/19 confirmed, 5 mismatch(es), 0 missing: `data/results/source-validation/csv5/cirrus/source-validation-gradle8.13/source-validation.md` | Record as source-validated partial; keep mismatches explicit. |
| AFWall+ | 4.0.3 (20260301) | source-validated | ok: `data/source/csv5/afwall-plus/source.tar.gz` | ok: `data/results/source-validation/csv5/afwall-plus/docker-app-releaseRuntimeClasspath-gradle8.13.txt` | ok: 12/18 confirmed, 6 mismatch(es), 0 missing: `data/results/source-validation/csv5/afwall-plus/source-validation-gradle8.13/source-validation.md` | Record as source-validated partial; keep mismatches explicit. |

## Rules

- Source tarball checksum success is only a source-availability gate.
- Dependency-tree success is required before `validate-source-deps` can produce source-confirmed counts.
- Framework/native-heavy rows may remain limitation evidence even after source capture.
- Rows with blocked Gradle trees stay out of source-validated metrics.
