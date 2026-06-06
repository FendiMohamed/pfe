# Real APK Batch Proof Status

This batch artifact advances selected real APK rows through the same proof gates together.
It does not promote any row into source-validated accuracy metrics unless a runtime dependency tree and source-validation output exist.

## Summary

| Field | Value |
|---|---|
| Selected APKs | 11 |
| Source tarballs available | 11 |
| Dependency trees captured | 9 |
| Source validations completed | 9 |
| Script failures | 0 |
| Source root | `data/source/clean-real-apk-candidate-sweep-v16` |
| Validation root | `data/results/source-validation/csv16` |

## Per-APK Status

| App | Version | Proof status | Source | Gradle/dependency tree | Source validation | Next gate |
|---|---|---|---|---|---|---|
| OceanNex for DigitalOcean | 1.0.0 (100) | source-validated-partial | ok: `data/source/clean-real-apk-candidate-sweep-v16/oceannex/source.tar.gz` | ok: 5 attempted config(s): `data/results/source-validation/csv16/oceannex/root1-app-dependencies-freeReleaseRuntimeClasspath.txt` | ok: 16/21 confirmed, 5 mismatch(es), 0 missing: `data/results/source-validation/csv16/oceannex/source-validation/source-validation.md` | Record as source-validated partial; keep mismatches explicit. |
| Praktika Vortaro | 0.26 (26) | source-validated-partial | ok: `data/source/clean-real-apk-candidate-sweep-v16/praktika-vortaro/source.tar.gz` | ok: 1 attempted config(s): `data/results/source-validation/csv16/praktika-vortaro/root1-app-dependencies-releaseRuntimeClasspath.txt` | ok: 0/1 confirmed, 1 mismatch(es), 0 missing: `data/results/source-validation/csv16/praktika-vortaro/source-validation/source-validation.md` | Record as source-validated partial; keep mismatches explicit. |
| MsgGo | 3.9 (26000309) | source-validated-partial | ok: `data/source/clean-real-apk-candidate-sweep-v16/msggo/source.tar.gz` | ok: 1 attempted config(s): `data/results/source-validation/csv16/msggo/root1-app-dependencies-releaseRuntimeClasspath.txt` | ok: 1/4 confirmed, 3 mismatch(es), 0 missing: `data/results/source-validation/csv16/msggo/source-validation/source-validation.md` | Record as source-validated partial; keep mismatches explicit. |
| AF Weather Widget | 3.2 (23) | source-validated-partial | ok: `data/source/clean-real-apk-candidate-sweep-v16/af-weather-widget/source.tar.gz` | ok: 1 attempted config(s): `data/results/source-validation/csv16/af-weather-widget/root1-app-dependencies-releaseRuntimeClasspath.txt` | ok: 13/18 confirmed, 5 mismatch(es), 0 missing: `data/results/source-validation/csv16/af-weather-widget/source-validation/source-validation.md` | Record as source-validated partial; keep mismatches explicit. |
| Study Tracker | 1.0.7 (7) | source-validated-partial | ok: `data/source/clean-real-apk-candidate-sweep-v16/study-tracker/source.tar.gz` | ok: 1 attempted config(s): `data/results/source-validation/csv16/study-tracker/root1-app-dependencies-releaseRuntimeClasspath.txt` | ok: 3/15 confirmed, 12 mismatch(es), 0 missing: `data/results/source-validation/csv16/study-tracker/source-validation/source-validation.md` | Record as source-validated partial; keep mismatches explicit. |
| Calliope mini | 2.0.9 (27) | source-validated-partial | ok: `data/source/clean-real-apk-candidate-sweep-v16/calliope-mini/source.tar.gz` | ok: 1 attempted config(s): `data/results/source-validation/csv16/calliope-mini/root1-app-dependencies-releaseRuntimeClasspath.txt` | ok: 11/18 confirmed, 7 mismatch(es), 0 missing: `data/results/source-validation/csv16/calliope-mini/source-validation/source-validation.md` | Record as source-validated partial; keep mismatches explicit. |
| Flying Carpet | 9.0.8 (21) | gradle-blocked | ok: `data/source/clean-real-apk-candidate-sweep-v16/flying-carpet/source.tar.gz` | blocked: no attempted Gradle configuration succeeded; 60 attempted config(s) | blocked-until-dependency-tree: Run validate-source-deps after a runtime dependency tree is captured. | Investigate Gradle configuration/toolchain blocker. |
| FitoTrack | 15.6 (1560) | gradle-blocked | ok: `data/source/clean-real-apk-candidate-sweep-v16/fitotrack/source.tar.gz` | blocked: no attempted Gradle configuration succeeded; 60 attempted config(s) | blocked-until-dependency-tree: Run validate-source-deps after a runtime dependency tree is captured. | Investigate Gradle configuration/toolchain blocker. |
| F-Droid Build Status | 5.14.0 (118) | source-validated-partial | ok: `data/source/clean-real-apk-candidate-sweep-v16/fdroid-build-status/source.tar.gz` | ok: 1 attempted config(s): `data/results/source-validation/csv16/fdroid-build-status/root1-app-dependencies-releaseRuntimeClasspath.txt` | ok: 16/24 confirmed, 8 mismatch(es), 0 missing: `data/results/source-validation/csv16/fdroid-build-status/source-validation/source-validation.md` | Record as source-validated partial; keep mismatches explicit. |
| Password Master | 1.5.1 (15) | source-validated-partial | ok: `data/source/clean-real-apk-candidate-sweep-v16/password-master/source.tar.gz` | ok: 1 attempted config(s): `data/results/source-validation/csv16/password-master/root1-passwordmaster-dependencies-releaseRuntimeClasspath.txt` | ok: 13/18 confirmed, 5 mismatch(es), 0 missing: `data/results/source-validation/csv16/password-master/source-validation/source-validation.md` | Record as source-validated partial; keep mismatches explicit. |
| Todo List (PFA) | 3.4.0 (103) | source-validated-partial | ok: `data/source/clean-real-apk-candidate-sweep-v16/todo-list-pfa/source.tar.gz` | ok: 1 attempted config(s): `data/results/source-validation/csv16/todo-list-pfa/root1-app-dependencies-releaseRuntimeClasspath.txt` | ok: 9/17 confirmed, 8 mismatch(es), 0 missing: `data/results/source-validation/csv16/todo-list-pfa/source-validation/source-validation.md` | Record as source-validated partial; keep mismatches explicit. |

## Rules

- Source tarball checksum success is only a source-availability gate.
- Dependency-tree success is required before `validate-source-deps` can produce source-confirmed counts.
- Framework/native-heavy rows may remain limitation evidence even after source capture.
- Rows with blocked Gradle trees stay out of source-validated metrics.
