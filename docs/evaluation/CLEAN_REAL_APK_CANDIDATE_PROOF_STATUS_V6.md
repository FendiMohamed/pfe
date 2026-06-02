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
| Source root | `data/source/csv6` |
| Validation root | `data/results/source-validation/csv6` |

## Per-APK Status

| App | Version | Proof status | Source | Gradle/dependency tree | Source validation | Next gate |
|---|---|---|---|---|---|---|
| microMathematics Plus | 2.23.3 (325) | source-validated | ok: `data/source/csv6/micromathematics-plus/source.tar.gz` | ok: `data/results/source-validation/csv6/micromathematics-plus/docker-app-releaseRuntimeClasspath-gradle8.13.txt` | ok: 4/16 confirmed, 12 mismatch(es), 0 missing: `data/results/source-validation/csv6/micromathematics-plus/source-validation-gradle8.13/source-validation.md` | Record as source-validated partial; keep mismatches explicit. |
| Retro Music | 6.6.0 (10660) | source-validated | ok: `data/source/csv6/retro-music/source.tar.gz` | ok: `data/results/source-validation/csv6/retro-music/docker-app-fdroidReleaseRuntimeClasspath-gradle8.14.3.txt` | ok: 4/6 confirmed, 2 mismatch(es), 0 missing: `data/results/source-validation/csv6/retro-music/source-validation-gradle8.14.3/source-validation.md` | Record as source-validated partial; keep mismatches explicit. |
| Broccoli | 1.4.4 (1040400) | source-validated | ok: `data/source/csv6/broccoli/source.tar.gz` | ok: `data/results/source-validation/csv6/broccoli/docker-app-fdroidReleaseRuntimeClasspath-gradle8.13.txt` | ok: 11/20 confirmed, 9 mismatch(es), 0 missing: `data/results/source-validation/csv6/broccoli/source-validation-gradle8.13/source-validation.md` | Record as source-validated partial; keep mismatches explicit. |
| Diaguard | 3.15.1 (68) | source-validated | ok: `data/source/csv6/diaguard/source.tar.gz` | ok: `data/results/source-validation/csv6/diaguard/docker-app-demoReleaseRuntimeClasspath-gradle8.13.txt` | ok: 2/5 confirmed, 3 mismatch(es), 0 missing: `data/results/source-validation/csv6/diaguard/source-validation-gradle8.13/source-validation.md` | Record as source-validated partial; keep mismatches explicit. |
| LibreTube | 31.4 (70) | source-validated | ok: `data/source/csv6/libretube/source.tar.gz` | ok: `data/results/source-validation/csv6/libretube/docker-app-releaseRuntimeClasspath-gradle9.5.txt` | ok: 9/13 confirmed, 4 mismatch(es), 0 missing: `data/results/source-validation/csv6/libretube/source-validation-gradle9.5/source-validation.md` | Record as source-validated partial; keep mismatches explicit. |

## Rules

- Source tarball checksum success is only a source-availability gate.
- Dependency-tree success is required before `validate-source-deps` can produce source-confirmed counts.
- Framework/native-heavy rows may remain limitation evidence even after source capture.
- Rows with blocked Gradle trees stay out of source-validated metrics.
