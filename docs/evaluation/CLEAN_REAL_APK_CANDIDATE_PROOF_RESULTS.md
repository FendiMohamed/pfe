# Clean Real APK Candidate Proof Results

This artifact records the follow-up proof gates for the clean/non-sparse real APK
candidate search. The goal was to find another clean source-validated real APK
after F-Droid, OpenTracks, and sparse Tusky.

## Candidate Sweep

Two small no-native F-Droid sweeps were collected in the first pass:

- Sweep 1: Foxy Droid, WebRadio, Equate.
- Sweep 2: Gotify, BetterCounter, Olauncher, Coffee.

All APKs were SHA-256 checked against the local F-Droid index and reported with
the calibrated combined reference DB. WebRadio and Equate emitted no Maven
components. Olauncher emitted only two low-confidence components. Foxy Droid
emitted six components; it was initially blocked by old Android Gradle Plugin
3.4-era wiring under Docker Gradle 9.5, but a validation-only JCenter URL and
SDK-path copy plus JDK 11 / Gradle 5.1.1 now resolves its dependency tree.

## Source-Validated Rows

The useful source-validated candidates are:

| App | Package | APK | Report | Dependency tree | Source validation | Result |
|---|---|---|---|---|---|---|
| Gotify 2.10.0 | `com.github.gotify` | `data/test_apks/real/gotify/gotify.apk` | `data/results/evaluation/clean-real-apk-candidate-sweep-v2/report-real-gotify/report.json` | `data/results/source-validation/clean-real-apk-candidate-sweep-v2/gotify/docker-app-releaseRuntimeClasspath.txt` | `data/results/source-validation/clean-real-apk-candidate-sweep-v2/gotify/source-validation/source-validation.json` | 11/23 confirmed, 11 mismatches, 1 missing |
| Foxy Droid 1.3 | `nya.kitsunyan.foxydroid` | `data/test_apks/real/foxy-droid/foxy-droid.apk` | `data/results/evaluation/clean-real-apk-candidate-sweep/report-real-foxy-droid/report.json` | `data/results/source-validation/clean-real-apk-candidate-sweep/foxy-droid/docker-root-releaseRuntimeClasspath-gradle5.1.1-jdk11.validation-copy.txt` | `data/results/source-validation/clean-real-apk-candidate-sweep/foxy-droid/source-validation-gradle5.1.1-jdk11-validation-copy/source-validation.json` | 1/6 confirmed, 4 mismatches, 1 missing |
| BetterCounter 6.0.3 | `org.kde.bettercounter` | `data/test_apks/real/bettercounter/bettercounter.apk` | `data/results/evaluation/clean-real-apk-candidate-sweep-v2/report-real-bettercounter/report.json` | `data/results/source-validation/clean-real-apk-candidate-sweep-v2/bettercounter/docker-app-releaseRuntimeClasspath.txt` | `data/results/source-validation/clean-real-apk-candidate-sweep-v2/bettercounter/source-validation/source-validation.json` | 5/7 confirmed, 1 mismatch, 1 missing |
| Coffee 2.26 | `com.github.muellerma.coffee` | `data/test_apks/real/coffee/coffee.apk` | `data/results/evaluation/clean-real-apk-candidate-sweep-v2/report-real-coffee/report.json` | `data/results/source-validation/clean-real-apk-candidate-sweep-v2/coffee/docker-app-releaseRuntimeClasspath.txt` | `data/results/source-validation/clean-real-apk-candidate-sweep-v2/coffee/source-validation/source-validation.json` | 10/11 confirmed, 1 mismatch, 0 missing |

## Interpretation

Coffee is the strongest result from this pass, but it is not clean: the emitted
`org.jetbrains.kotlinx:kotlinx-coroutines-android@1.9.0` row mismatches the
source-resolved `1.10.2`. Gotify is valuable non-sparse modern evidence because
it emits 23 Maven components with no native files, but it is a partial result
with broad AndroidX/Kotlin version-band drift. Foxy Droid is valuable older
toolchain evidence because JDK 11 / Gradle 5.1.1 rescues its dependency tree,
but it remains partial at 1/6. BetterCounter is a compact partial no-native
case.

The clean non-sparse bucket is therefore still open. These rows should be
counted as source-validated partial evidence, not promoted into the clean
source-validated metric.

A third sweep is recorded separately in
`docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_RESULTS_V3.md`. It adds
MedTimer, Doodle, and Simple Time Tracker as additional no-native
source-validated partial rows, but it also leaves the clean non-sparse bucket
open.

## Commands

Reports were generated in Docker, for example:

```powershell
docker compose run --rm apk-sbom python -m apk_sbom.cli generate-report `
  data/test_apks/real/gotify/gotify.apk `
  --output-dir data/results/evaluation/clean-real-apk-candidate-sweep-v2/report-real-gotify `
  --db-path data/reference_db/reference_features_calibrated_combined.sqlite `
  --skip-osv
```

Dependency trees were captured in Docker with `:app:dependencies
--configuration releaseRuntimeClasspath`, then validated with:

```powershell
docker compose run --rm apk-sbom python -m apk_sbom.cli validate-source-deps `
  --sbom data/results/evaluation/clean-real-apk-candidate-sweep-v2/report-real-coffee/sbom.cdx.json `
  --dependency-tree data/results/source-validation/clean-real-apk-candidate-sweep-v2/coffee/docker-app-releaseRuntimeClasspath.txt `
  --output-dir data/results/source-validation/clean-real-apk-candidate-sweep-v2/coffee/source-validation
```
