# Real APK Current Batch Results

This note records the NewPipe/Tusky/K-9/AntennaPod proof-bundle attempts and the Organic Maps/Termux native-heavy limitation cases.

## Summary

| APK | Dataset role | APK/source proof | Report result | Source validation result | Interpretation |
|---|---|---|---|---|---|
| NewPipe `0.28.5` / `1010` | source-validated candidate | APK, SHA-256, F-Droid metadata, source tarball, and Gradle tree collected | 11 Maven components, 4 native file components, OSV 0 | Saved report: 10 confirmed, 1 mismatch, 0 missing; fresh 2026-05-24 control: 9 confirmed, 2 mismatches, 0 missing | Good modern multidex/media candidate, but still partial. Fresh controls keep `startup-runtime` and `lifecycle-runtime-android` as version limitations to investigate before claiming a clean NewPipe result. |
| Tusky `32.2` / `142` | source-validated real APK | APK, SHA-256, F-Droid metadata, source tarball, and Gradle tree collected | 1 Maven component, 16 native file components, OSV 0 | 1 confirmed, 0 mismatches, 0 missing | Clean but sparse source-validated case after adding source-used `retrofit@3.0.0` to calibration. |
| K-9 / Thunderbird Android `18.0` / `39035` | source-linked candidate | APK, SHA-256, F-Droid metadata, source tarball, source version catalog, catalog-only validation, and bounded Gradle retry logs collected | 11 Maven components, 8 native file components, OSV 0 | blocked: resolved Gradle tree not generated | Strong multidex/email/security case, but not admitted as source-validated because K-9's included Gradle build-plugin setup stalls during dependency-tree generation. |
| AntennaPod `3.11.4` / `3110495` | source-validated partial-mismatch | APK, SHA-256, F-Droid metadata, exact GitHub source archive, and Gradle tree collected | 20 Maven components, 4 native file components, OSV 0 | 19 confirmed, 1 mismatch, 0 missing | Strong multidex/media/networking case; calibration fixed WorkManager, remaining AndroidX Core mismatch is a near-tie limitation. |
| Wikipedia Android `r/50586-r-2026-05-12` / `50586` | source-validated partial-mismatch | APK, SHA-256, F-Droid metadata, source tarball, report, and Gradle tree collected | 13 Maven components, 8 native file components, OSV 0 | 11 confirmed, 2 mismatches, 0 missing | Good non-sparse modern app case with multidex plus native MapLibre; not a clean accuracy case because Startup and ViewPager2 remain near-version mismatches. |
| Conversations `2.20.0+free` / `4217704` | source-validated partial-mismatch | APK, SHA-256, F-Droid metadata, source tarball, report, and Gradle tree collected | 9 Maven components, 2 native file components, OSV 0 | 6 confirmed, 2 mismatches, 1 artifact-family nuance | Good messaging/security case with multidex, R8/minify, and native libraries; source-used Gson calibration fixed one mismatch, while two AndroidX near-ties remain honest limitations. |
| Nextcloud Android `33.1.0` / `330010090` | source-validated partial-mismatch | APK, SHA-256, F-Droid metadata, source tarball, report, and Gradle tree collected | 29 Maven components, 12 native file components, OSV 0 | guarded-promoted shared DB: 21 confirmed, 7 mismatches, 1 artifact-family nuance | Large modern cloud-sync case with a broad AndroidX/Compose/Kotlin tree; useful as version-band/reference-coverage evidence, not a clean accuracy case. |
| FairEmail `1.2315` / `2315` | source-validated partial-mismatch | APK, SHA-256, F-Droid metadata, source tarball, report, and no-native validation dependency tree collected | 13 Maven components, 4 native file components, OSV 0 | 7 confirmed, 6 mismatches, 0 missing | Good email/security case. Source validation uses a copied source tree with native build disabled only to bypass missing NDK `27.2.12479018`; count it as Maven dependency validation, not native build validation. |
| OsmAnd~ `5.3.10` / `531003` | source-validated partial-mismatch | APK, SHA-256, F-Droid metadata, source tarball, report, and Gradle dependency tree collected | 25 Maven components, 6 native file components, 4 OSV findings on APK-selected Jackson/Gson versions | 16 confirmed, 9 mismatches, 0 missing | Large maps/native stress case. The dependency tree required F-Droid configuration edits and Gradle 8.10.2; source validation shows useful coverage but keeps Jackson/Gson and several AndroidX/Kotlin versions as mismatches. |
| Organic Maps `2026.05.08-4-FDroid` / `26050804` | limitation/native-heavy | APK, SHA-256, F-Droid metadata, and source tarball collected | 13 Maven components, 4 very large native file components, OSV 0 | not claimed | Shows the native boundary: Java/Kotlin DEX matching works, but native `liborganicmaps.so` versions are hash-only. |
| Termux `0.119.0-beta.3` / `1022` | limitation/native-heavy | APK, SHA-256, F-Droid metadata, and source tarball collected | 5 Maven components, 12 native file components, OSV 0 | not claimed | Shows the packaging/native bootstrap boundary; large native payloads are reported as file hashes only. |

## Evidence Paths

| Artifact | Path |
|---|---|
| Current-batch proof plan | `docs/evaluation/REAL_APK_CURRENT_PROOF_BUNDLE.md` |
| Candidate matrix | `docs/evaluation/REAL_APK_CANDIDATES.md` |
| NewPipe report | `data/results/report-real-newpipe-calibrated-db/report.md` |
| NewPipe Gradle tree | `data/results/source-validation/newpipe/releaseRuntimeClasspath.txt` |
| NewPipe validation | `data/results/source-validation/newpipe-calibrated-db/source-validation.md` |
| Tusky report | `data/results/report-real-tusky-calibrated-db/report.md` |
| Tusky Gradle tree | `data/results/source-validation/tusky/blueReleaseRuntimeClasspath.txt` |
| Tusky validation | `data/results/source-validation/tusky-calibrated-db/source-validation.md` |
| K-9 proof note | `docs/evaluation/K9_THUNDERBIRD_PROOF_BUNDLE.md` |
| K-9 report | `data/results/report-real-k9-thunderbird-android/report.md` |
| K-9 source version catalog | `data/results/source-validation/k9-thunderbird-android/libs.versions.toml` |
| K-9 catalog-only validation | `data/results/source-validation/k9-thunderbird-android/k9-version-catalog-validation.md` |
| K-9 Gradle error log | `data/results/source-validation/k9-thunderbird-android/gradle-error.log` |
| AntennaPod proof note | `docs/evaluation/ANTENNAPOD_PROOF_BUNDLE.md` |
| AntennaPod report | `data/results/report-real-antennapod/report.md` |
| AntennaPod Gradle tree | `data/results/source-validation/antennapod/freeReleaseRuntimeClasspath.txt` |
| AntennaPod validation | `data/results/source-validation/antennapod-report-validation/source-validation.md` |
| KDE Connect proof note | `docs/evaluation/KDE_CONNECT_PROOF_BUNDLE.md` |
| KDE Connect report | `data/results/report-real-kde-connect/report.md` |
| KDE Connect Gradle tree | `data/results/source-validation/kde-connect/releaseRuntimeClasspath.txt` |
| KDE Connect validation | `data/results/source-validation/kde-connect-validation/source-validation.md` |
| Wikipedia Android proof note | `docs/evaluation/WIKIPEDIA_ANDROID_PROOF_BUNDLE.md` |
| Wikipedia Android APK | `data/test_apks/real/wikipedia-android/wikipedia-android.apk` |
| Wikipedia Android source tarball | `data/source/wikipedia-android/source.tar.gz` |
| Wikipedia Android report | `data/results/report-real-wikipedia-android/report.md` |
| Wikipedia Android Gradle tree | `data/results/source-validation/wikipedia-android/fdroidReleaseRuntimeClasspath.txt` |
| Wikipedia Android validation | `data/results/source-validation/wikipedia-android-report-validation/source-validation.md` |
| Conversations proof note | `docs/evaluation/CONVERSATIONS_PROOF_BUNDLE.md` |
| Conversations APK | `data/test_apks/real/conversations/conversations.apk` |
| Conversations source tarball | `data/source/conversations/source.tar.gz` |
| Conversations report | `data/results/report-real-conversations/report.md` |
| Conversations Gradle tree | `data/results/source-validation/conversations/conversationsFreeReleaseRuntimeClasspath.txt` |
| Conversations validation | `data/results/source-validation/conversations-report-validation/source-validation.md` |
| Nextcloud Android proof note | `docs/evaluation/NEXTCLOUD_ANDROID_PROOF_BUNDLE.md` |
| Nextcloud Android APK | `data/test_apks/real/nextcloud-android/nextcloud.apk` |
| Nextcloud Android source tarball | `data/source/nextcloud-android-33.1.0/source.tar.gz` |
| Nextcloud Android report | `data/results/report-real-nextcloud-android/report.md` |
| Nextcloud Android Gradle tree | `data/results/source-validation/nextcloud-android/genericReleaseRuntimeClasspath.txt` |
| Nextcloud Android validation | `data/results/source-validation/nextcloud-android-report-validation/source-validation.md` |
| FairEmail proof note | `docs/evaluation/FAIREMAIL_PROOF_BUNDLE.md` |
| FairEmail report | `data/results/report-real-fairemail/report.md` |
| FairEmail no-native Gradle tree | `data/results/source-validation/fairemail/fdroidReleaseRuntimeClasspath.no-native.txt` |
| FairEmail validation | `data/results/source-validation/fairemail-report-validation/source-validation.md` |
| Aegis proof note | `docs/evaluation/AEGIS_AUTHENTICATOR_PROOF_BUNDLE.md` |
| Aegis report | `data/results/report-real-aegis-authenticator/report.md` |
| Aegis Gradle tree | `data/results/source-validation/aegis-authenticator/releaseRuntimeClasspath.txt` |
| Aegis validation | `data/results/source-validation/aegis-authenticator-report-validation/source-validation.md` |
| Markor proof note | `docs/evaluation/MARKOR_PROOF_BUNDLE.md` |
| Markor report | `data/results/report-real-markor/report.md` |
| Markor Gradle tree | `data/results/source-validation/markor/flavorDefaultReleaseRuntimeClasspath.txt` |
| Markor validation | `data/results/source-validation/markor-report-validation/source-validation.md` |
| OsmAnd proof note | `docs/evaluation/OSMAND_PROOF_BUNDLE.md` |
| OsmAnd report | `data/results/report-real-osmand/report.md` |
| OsmAnd Gradle tree | `data/results/source-validation/osmand/androidFullOpenglArm64ReleaseRuntimeClasspath.txt` |
| OsmAnd validation | `data/results/source-validation/osmand-report-validation/source-validation.md` |
| API/member-reference weight experiment | `data/results/experiments/api-reference-weight/api-reference-weight-summary.md` |
| Organic Maps report | `data/results/report-real-organic-maps-calibrated-db/report.md` |
| Termux report | `data/results/report-real-termux-calibrated-db/report.md` |

## Commands Run

Generate APK reports with the calibrated DB and OSV enabled:

```powershell
docker compose run --rm apk-sbom python -m apk_sbom.cli generate-report data/test_apks/real/newpipe/newpipe.apk --output-dir data/results/report-real-newpipe-calibrated-db --db-path data/reference_db/reference_features_calibrated_combined.sqlite --top 30
docker compose run --rm apk-sbom python -m apk_sbom.cli generate-report data/test_apks/real/tusky/tusky.apk --output-dir data/results/report-real-tusky-calibrated-db --db-path data/reference_db/reference_features_calibrated_combined.sqlite --top 30
docker compose run --rm apk-sbom python -m apk_sbom.cli generate-report data/test_apks/real/organic-maps/organic-maps.apk --output-dir data/results/report-real-organic-maps-calibrated-db --db-path data/reference_db/reference_features_calibrated_combined.sqlite --top 30
docker compose run --rm apk-sbom python -m apk_sbom.cli generate-report data/test_apks/real/termux/termux.apk --output-dir data/results/report-real-termux-calibrated-db --db-path data/reference_db/reference_features_calibrated_combined.sqlite --top 30
docker compose run --rm apk-sbom python -m apk_sbom.cli generate-report data/test_apks/real/k9-thunderbird-android/k9-thunderbird-android.apk --output-dir data/results/report-real-k9-thunderbird-android --db-path data/reference_db/reference_features_calibrated_combined.sqlite --top 30
docker compose run --rm apk-sbom python -m apk_sbom.cli generate-report data/test_apks/real/antennapod/antennapod.apk --output-dir data/results/report-real-antennapod --db-path data/reference_db/reference_features_calibrated_combined.sqlite --top 30
docker compose run --rm apk-sbom python -m apk_sbom.cli generate-report data/test_apks/real/kde-connect/kde-connect.apk --output-dir data/results/report-real-kde-connect --db-path data/reference_db/reference_features_calibrated_combined.sqlite --top 30
docker compose run --rm apk-sbom python -m apk_sbom.cli generate-report data/test_apks/real/conversations/conversations.apk --output-dir data/results/report-real-conversations --db-path data/reference_db/reference_features_calibrated_combined.sqlite --top 30
```

Generate and validate the Tusky source dependency tree:

```powershell
docker compose run --rm -e GRADLE_USER_HOME=/app/data/source/.gradle-cache-tusky -w /app/data/source/tusky-32.2/source/com.keylesspalace.tusky_142_src.tar.gz apk-sbom sh -c "/opt/gradle/bin/gradle --no-daemon :app:dependencies --configuration blueReleaseRuntimeClasspath > /app/data/results/source-validation/tusky/blueReleaseRuntimeClasspath.txt 2> /app/data/results/source-validation/tusky/gradle-error.log"
docker compose run --rm apk-sbom python -m apk_sbom.cli validate-source-deps --sbom data/results/report-real-tusky-calibrated-db/sbom.cdx.json --dependency-tree data/results/source-validation/tusky/blueReleaseRuntimeClasspath.txt --output-dir data/results/source-validation/tusky-calibrated-db
```

Generate and validate the NewPipe source dependency tree after rebuilding Docker with a JDK:

```powershell
docker compose build --progress=plain
docker compose run --rm apk-sbom sh -c "java -version && javac -version"
docker compose run --rm -e GRADLE_USER_HOME=/app/data/source/.gradle-cache-newpipe -w /app/data/source/newpipe-0.28.5/source/org.schabi.newpipe_1010_src.tar.gz apk-sbom sh -c "/opt/gradle/bin/gradle --no-daemon :app:dependencies --configuration releaseRuntimeClasspath > /app/data/results/source-validation/newpipe/releaseRuntimeClasspath.txt 2> /app/data/results/source-validation/newpipe/gradle-error.log"
docker compose run --rm apk-sbom python -m apk_sbom.cli validate-source-deps --sbom data/results/report-real-newpipe-calibrated-db/sbom.cdx.json --dependency-tree data/results/source-validation/newpipe/releaseRuntimeClasspath.txt --output-dir data/results/source-validation/newpipe-calibrated-db
```

## NewPipe Source Validation Result

NewPipe source validation is now runnable because the Docker image includes `javac`. After adding source-used AndroidX/Okio versions, adding `lifecycle-runtime-android@2.9.4`, and adding matcher-level version disambiguation, the saved `data/results/report-real-newpipe-calibrated-db/` result improved substantially but is still not clean enough to admit as a fully source-validated accuracy case:

```text
SBOM components: 11
Confirmed: 10
Version mismatches: 1
Missing: 0
```

Fixed by the matcher-level pass:

- `androidx.swiperefreshlayout:swiperefreshlayout` now selects `1.2.0` using version-distinctive evidence.
- `androidx.viewpager2:viewpager2` now selects `1.1.0` using version-distinctive evidence.
- `com.squareup.okio:okio-jvm` now selects `3.16.4` using version-distinctive evidence.
- `androidx.lifecycle:lifecycle-runtime-android` now selects `2.9.4` using the bytecode-bearing Android target variant instead of the public no-bytecode coordinate.

Remaining NewPipe mismatch:

- `androidx.startup:startup-runtime` selects `1.1.1`, while the source dependency tree resolves `1.2.0`.

This is useful research evidence: the proof bundle is complete enough to show that the MVP detects real AndroidX/Okio components, and the matcher can improve version selection when there is distinctive evidence. The remaining Startup case should not be forced by recency alone because a generic near-tie rule caused a false version flip on `androidx.concurrent:concurrent-futures`; resolving it safely would need Maven POM/dependency metadata coherence.

## API/member-reference Weight Experiment

On 2026-05-24, a separate calibrated API-reference DB was rebuilt at `data/reference_db/reference_features_calibrated_combined_api_refs.sqlite` with 93 components and 303,709 API/member-reference rows. `generate-report` now accepts `--api-reference-weight`, matching `match-apk`.

The guarded offline experiment in `data/results/experiments/api-reference-weight/` compared weight `0.0` and `0.05` across F-Droid, OpenTracks, Aegis Authenticator, Markor, and NewPipe. The summary now also records version decisions with score gaps at or below `0.001`. Trial weight `0.05` produced no source-validation metric changes:

```text
F-Droid: 23/23 confirmed, unchanged
OpenTracks: 19/19 confirmed, unchanged
Aegis Authenticator: 6/7 confirmed, 1 ViewPager2 mismatch, unchanged
Markor then-current control: 6/19 confirmed, 13 older-dependency mismatches, unchanged
NewPipe fresh control: 9/11 confirmed, 2 mismatches, unchanged
```

Interpretation: API/member-reference overlap is populated and measurable, but a simple global positive weight does not solve the current AndroidX version near-ties. Keep the default weight at `0.0`.

The fresh NewPipe `lifecycle-runtime-android` drift is now explained: adding Aegis's source-used `lifecycle-runtime-android@2.9.0` reference created a micro-tie. For NewPipe, `2.9.0` scores `0.400626` and the source-correct `2.9.4` scores `0.400602`, a `0.000024` gap. Aegis has the same pattern, but `2.9.0` is source-correct there. Therefore a generic newer-patch tie-break would fix NewPipe and regress Aegis. The next matcher work needs a stronger app-era or dependency-coherence signal, not recency alone.

Follow-up metadata and matcher work completed:

- Maven POM files are now downloaded and parsed into artifact metadata.
- POM dependency rows flow through conversion metadata into the SQLite reference feature DB.
- The matcher loads those POM dependencies with reference candidates.
- A focused Startup metadata check showed that `startup-runtime@1.1.1` declares `androidx.annotation:annotation@1.1.0`, while `startup-runtime@1.2.0` declares `androidx.annotation:annotation@1.8.1`.
- The calibrated combined DB stores 549 Maven dependency rows after the guarded Nextcloud promotion refresh.
- A conservative POM coherence tie-breaker was added, but it only applies to close candidate-level ties when another independently selected APK-side component supports a POM dependency version.

Interpretation: this is useful version-context evidence, but it is not enough by itself to force NewPipe from `1.1.1` to `1.2.0`. The new rule correctly stays dormant for the current NewPipe/Antennapod/KDE near-ties because the required independent supporting coordinates are not present in the emitted evidence.

Fresh POM-coherence regression validation:

| APK | SBOM components | Confirmed | Mismatches | Missing |
|---|---:|---:|---:|---:|
| F-Droid | 23 | 23 | 0 | 0 |
| OpenTracks | 19 | 19 | 0 | 0 |
| Tusky | 1 | 1 | 0 | 0 |
| NewPipe | 10 | 9 | 1 | 0 |
| AntennaPod | 20 | 19 | 1 | 0 |
| KDE Connect | 9 | 8 | 1 | 0 |

## Tusky Calibration Result

Tusky originally selected `com.squareup.retrofit2:retrofit@2.9.0`, while the source tree resolved `3.0.0`. Adding `retrofit@3.0.0` to `configs/libraries.calibration.json` and rebuilding the calibrated DB resolved the mismatch:

```text
SBOM component: com.squareup.retrofit2:retrofit@3.0.0
Source resolved: com.squareup.retrofit2:retrofit@3.0.0
Result: confirmed
```

Tusky should be presented carefully: it is a clean source-validated case for the one emitted Maven component, but it is sparse because the current matcher emits only Retrofit from a much larger source dependency tree.

## K-9 / Thunderbird Android Source-Linked Result

K-9 / Thunderbird Android `18.0` is collected as a source-linked candidate, but it is not source-validated yet:

```text
Maven SBOM components: 11
Native file components: 8
OSV vulnerabilities: 0
Source validation: 5/11 confirmed, 6 mismatches, 0 missing
```

The APK/source proof is strong: manifest package `com.fsck.k9`, versionName `18.0`, and versionCode `39035` match the F-Droid build record. F-Droid metadata points to commit `23016c71d2f075700a0e258b9fe374bd06d8257b`, subdir `app-k9mail`, and flavor `foss`.

The source version catalog check confirms some emitted versions, including AppCompat `1.7.1`, RecyclerView `1.4.0`, Fragment `1.8.9`, and Okio `3.16.4` through artifact-family mapping. It also exposed likely mismatches that needed resolved-tree validation, including SwipeRefreshLayout `1.1.0` vs selected `1.2.0`, Lifecycle `2.10.0` vs selected `2.6.2`, and LocalBroadcastManager `1.1.0` vs selected `1.0.0`. The catalog-only validation result remains historical partial evidence: 3 exact confirmations, 2 exact catalog mismatches, 1 artifact-family confirmation, 1 artifact-family mismatch, and 4 not-in-catalog emitted components.

Dependency-tree generation was first attempted with Gradle `9.5.0`, a temporary source-declared Gradle `9.4.0`, and a fresh validation-only source copy where the included build-plugin repositories prefer `google()` and `mavenCentral()` before `gradlePluginPortal()`. Those attempts stalled after K-9's included `build-plugin` setup. The later 2026-06-05 validation-only plugin-lite/runtime-graph copy generated `fossReleaseRuntimeClasspath` at `data/results/source-validation/k9-thunderbird-android/fossReleaseRuntimeClasspath.plugin-lite-runtimegraph-composefix.txt`; source validation at `data/results/source-validation/k9-thunderbird-android-report-validation/source-validation.md` promotes K-9 to source-validated partial, not clean evidence.

## FairEmail Source Validation Result

FairEmail `1.2315` is a completed source-validation proof with remaining AndroidX version mismatches:

```text
Maven SBOM components: 13
Native file components: 4
OSV vulnerabilities: 0
Source validation: 7 confirmed, 6 mismatches, 0 missing
```

The APK/source proof is strong: manifest package `eu.faircode.email`, versionName `1.2315`, and versionCode `2315` match the F-Droid build record. F-Droid metadata points to commit `5d3dea660e8bb1aa0082e78f338123d0fd8c4287`, subdir `app`, and flavor `fdroid`.

The original source Gradle run still tries to install Android NDK `27.2.12479018`, so validation uses `data/results/source-validation/fairemail/source-no-native/`, a validation-only source copy with native build disabled only for Maven runtime dependency resolution. The resolved tree at `data/results/source-validation/fairemail/fdroidReleaseRuntimeClasspath.no-native.txt` validates 7/13 emitted Maven versions, with 6 AndroidX version mismatches and 0 missing coordinates. Count FairEmail as `source-validated-partial` for Java/Kotlin Maven dependencies, not as native build validation.

## Aegis Authenticator Source Validation Result

Aegis Authenticator `3.4.2` is a completed source-validation proof with one remaining version mismatch:

```text
SBOM components: 7
Confirmed: 6
Version mismatches: 1
Missing: 0
OSV vulnerabilities: 0
```

The exact F-Droid APK/source metadata points to commit `59d5c640d6a2d0d16f243dbdd735758eed65bc63`, subdir `app`, and Gradle build `yes`. APK inspection confirms package `com.beemdevelopment.aegis`, versionName `3.4.2`, versionCode `81`, 2 standard DEX files, multidex true, 8 small native barcode-scanning libraries, minSdk 23, targetSdk 35, and low extraction risk.

The Gradle source tree required two practical workarounds: the F-Droid source archive is tar-formatted despite the `.tar.gz` suffix, and the build script calls `git rev-parse`, so a temporary Git snapshot was created under `/tmp` for dependency-tree generation. Cached Gradle `8.13` generated `releaseRuntimeClasspath`; project Gradle `9.5.0` was too new for this build script's `exec` usage.

Adding source-used `androidx.lifecycle:lifecycle-runtime-android@2.9.0` to calibration fixed the Lifecycle mismatch. The remaining mismatch is `androidx.viewpager2:viewpager2`: selected `1.0.0`, source resolved `1.1.0`. Do not count Aegis as a clean version-accuracy case until that is handled or explicitly left as an AndroidX near-version limitation.

## Markor Source Validation Result

Markor `2.16.1` is a completed source-validation proof with many version mismatches:

```text
SBOM components: 19
Confirmed: 7
Version mismatches: 12
Missing: 0
OSV vulnerabilities: 0
```

The exact F-Droid APK/source metadata points to commit `f33eb6a8dfb210f27bfe7294430d4d39b795bd0f`, subdir `app`, and Gradle flavor `flavorDefault`. APK inspection confirms package `net.gsantner.markor`, versionName `2.16.1`, versionCode `163`, 2 standard DEX files, multidex true, 0 native files, minSdk 18, targetSdk 35, and a medium extraction-risk warning caused by an asset filename containing `shell`: `assets/prism/components/prism-shell-session.min.js`.

The Gradle source tree required the F-Droid prebuild edit to remove `-XX:MaxPermSize=512m` from `gradle.properties`, cached Gradle `8.13`, and a temporary Git snapshot because the source tarball has no `.git` directory but the build calls Git during configuration.

Markor is useful older-dependency drift evidence: identity is often right and 0 coordinates are missing, but exact versions are still partial because the shared reference/calibration set must avoid pulling newer apps toward older AndroidX/Kotlin versions. Do not count Markor as a clean version-accuracy case.

A targeted source-used-version calibration experiment added Markor's older dependency stack and improved Markor from 6/19 to 19/19 confirmed versions. That result is preserved at `data/results/report-real-markor-source-calibrated/` and `data/results/source-validation/markor-source-calibrated/`. A guarded follow-up then tested the three queued Markor coverage gaps: the combined set improved Markor to 9/19 but regressed 7 controls, while `androidx.core:core@1.9.0` alone improved Markor to 7/19 and left the current-control matrix unchanged. The lesson is that reference coverage fixes version matching only when paired with app-era or dependency-coherence safeguards.

## AntennaPod Source Validation Result

AntennaPod `3.11.4` is a completed source-validation proof with one remaining version mismatch:

```text
SBOM components: 20
Confirmed: 19
Version mismatches: 1
Missing: 0
OSV vulnerabilities: 0
```

The exact F-Droid APK/source metadata points to commit `6c3492af7239b46e8c9933ff04984fcdd07c3a6f`, subdir `app`, and flavor `free`. The F-Droid source tarball did not contain enough root Gradle files for dependency resolution, so the exact GitHub commit archive was used to generate `freeReleaseRuntimeClasspath` with Gradle wrapper `8.13`.

Adding source-used `androidx.work:work-runtime@2.10.3` and `androidx.core:core@1.16.0` to calibration improved validation from 18/20 to 19/20 confirmed. The remaining mismatch is `androidx.core:core`: selected `1.15.0`, source resolved `1.16.0`, with only a 0.005 raw score gap. Do not force this with a generic newer-version rule; resolving it safely likely needs dependency metadata coherence or stronger version-distinctive evidence.

## KDE Connect Source Validation Result

KDE Connect `1.35.5` is a completed source-validation proof with one remaining version mismatch:

```text
SBOM components: 9
Confirmed: 8
Version mismatches: 1
Missing: 0
OSV vulnerabilities: 0
```

The exact F-Droid APK/source metadata points to commit `0f3cc84446065102c064f78d4276bb4ebd00d3c9`. APK inspection confirms package `org.kde.kdeconnect_tp`, versionName `1.35.5`, versionCode `13505`, 2 standard DEX files, multidex true, 4 native `libandroidx.graphics.path.so` file components, minSdk 23, targetSdk 35, and low extraction risk.

Docker Gradle `9.5.0` generated the root `releaseRuntimeClasspath` from the F-Droid source tarball. Source validation confirms 8/9 emitted components. The remaining mismatch is `androidx.viewpager2:viewpager2` selected `1.1.0` vs source `1.1.0-beta02`.

This is useful diversity evidence because the release build has R8/minify and resource shrinking enabled. It should be presented as a partial-version-mismatch case, not a clean accuracy case. A temporary attempt to add `viewpager2@1.1.0-beta02` to calibration did not improve validation and shifted selection to an older candidate, so it was removed. The earlier Lifecycle runtime mismatch is fixed by scoped artifact-family coherence, which selects the bytecode-bearing Android target variant only as a low-confidence candidate when identity evidence is already present.

## Conversations Source Validation Result

Conversations `2.20.0+free` is a completed source-validation proof with partial version mismatches:

```text
SBOM components: 9
Confirmed: 6
Version mismatches: 2
Missing/artifact-family nuance: 1
OSV vulnerabilities: 0
```

The exact F-Droid APK/source metadata points to commit `7346a14dcedb155762133ea3ec512fdf34b57876` and Gradle flavors `conversations` plus `free`. APK inspection confirms package `eu.siacs.conversations`, versionName `2.20.0+free`, versionCode `4217704`, 2 standard DEX files, multidex true, 2 native arm64-v8a libraries, minSdk 23, targetSdk 36, and low extraction risk.

Docker Gradle `9.5.0` generated `conversationsFreeReleaseRuntimeClasspath` from the F-Droid source archive. The source archive is an uncompressed tar despite the `.tar.gz` filename, so the reproducible extraction command uses `tar -xf`.

Adding source-used `com.google.code.gson:gson@2.13.1` to `configs/libraries.calibration.json` and rebuilding the calibrated DB improved validation from 5/9 confirmed to 6/9 confirmed. The remaining mismatches are `androidx.concurrent:concurrent-futures` selected `1.1.0` vs source `1.3.0`, and `androidx.startup:startup-runtime` selected `1.1.1` vs source `1.2.0`. Both are close-score AndroidX version ambiguities and should not be forced by recency alone.

The remaining missing item is `androidx.lifecycle:lifecycle-runtime-android@2.9.4`, while the Gradle source tree reports public coordinate `androidx.lifecycle:lifecycle-runtime@2.6.2`. Treat this as an artifact-family validation nuance rather than a clean confirmed version.

## Nextcloud Android Source Validation Result

Nextcloud Android `33.1.0` is a completed source-validation proof with remaining version mismatches:

```text
SBOM components: 29
Confirmed before guarded promotion: 15
Confirmed after guarded promotion: 21
Version mismatches after guarded promotion: 7
Missing/artifact-family nuance: 1
OSV vulnerabilities: 0
```

The exact F-Droid APK/source metadata points to source tag `stable-33.1.0`, subdir `app`, and Gradle flavor `generic`. APK inspection confirms package `com.nextcloud.client`, versionName `33.1.0`, versionCode `330010090`, minSdk `28`, targetSdk `36`, 6 standard DEX files, multidex true, low extraction risk, and 12 native files across four ABIs: `libandroidx.graphics.path.so`, `libconscrypt_jni.so`, and `libpl_droidsonroids_gif.so`.

The report at `data/results/report-real-nextcloud-android/` emits 29 Maven components plus 12 native file components. Docker Gradle `9.5.0` generated `genericReleaseRuntimeClasspath`. The fresh pre-promotion control under `data/results/experiments/current-shared-db-control/` confirmed 15/29 emitted versions; the canonical source validation at `data/results/source-validation/nextcloud-android-report-validation/` now reflects the guarded-promoted shared DB and confirms 21/29 emitted versions.

Most mismatches are modern version-band/reference-coverage gaps: the source tree resolves versions such as `gson@2.13.2`, `okio-jvm@3.9.0`, Compose `1.10.6`, Kotlin `2.3.10`, RecyclerView `1.3.2`, Activity `1.9.2`, and Concurrent Futures `1.2.0`, while the shared DB only contains nearby older/newer choices. Two mismatches are stronger matcher evidence because the source version exists in the DB but was not selected: `androidx.startup:startup-runtime` selected `1.2.0` vs source `1.1.1`, and `androidx.swiperefreshlayout:swiperefreshlayout` selected `1.0.0` vs source `1.2.0`.

Nextcloud is useful large-modern-app evidence, but it should not be counted as a clean version-accuracy case. It reinforces the same conclusion as Markor from the other direction: broad reference coverage needs app-era or dependency-coherence safeguards before many source-version bands are mixed globally.

A guarded source-used-version calibration experiment added 11 Nextcloud source versions to a separate DB at `data/reference_db/reference_features_nextcloud_experiment_combined.sqlite`. This improved Nextcloud from fresh-control 15/29 confirmed to 24/29 confirmed, reducing mismatches from 13 to 4, but regressed F-Droid, NewPipe, and AntennaPod. A narrower six-version subset was then promoted to the shared calibrated DB: Compose foundation/UI/tooling-preview `1.10.6`, RecyclerView `1.3.2`, Gson `2.13.2`, and Kotlin stdlib `2.3.10`. The promoted DB improves Nextcloud to 21/29 confirmed and leaves the other 10 current-control cases unchanged; see `data/results/experiments/nextcloud-current-control-comparison/guarded-promotion-vs-previous-control.md`. The remaining mismatches are exactly the cases that need stronger app-era/dependency-coherence evidence before global promotion.

## OsmAnd Source Validation Result

OsmAnd~ `5.3.10` is a completed source-validation proof with native-heavy maps stress characteristics:

```text
SBOM components: 25
Confirmed: 16
Version mismatches: 9
Missing: 0
Native file components: 6
OSV findings: 4 on APK-selected Jackson/Gson versions
```

The exact F-Droid APK/source metadata points to source tag `v5.3.10`, subdir `android/OsmAnd`, Gradle flavors `android`, `full`, `opengl`, `arm64`, and NDK `r28c`. APK inspection confirms package `net.osmand.plus`, versionName `5.3.10`, versionCode `531003`, minSdk `24`, targetSdk `35`, 8 standard DEX files, multidex true, and 6 arm64-v8a native libraries.

The source archive is an uncompressed tar despite the `.tar.gz` filename. Dependency-tree generation used `data/results/source-validation/osmand/run-gradle-deps.sh`, which applies validation-only F-Droid configuration edits and uses cached Gradle `8.10.2`. Docker Gradle `9.5.0` is not source-compatible here because the build script still uses `XmlParser`.

Source validation confirms 16/25 emitted Maven versions, with 9 version mismatches and 0 missing coordinates. The report's OSV findings come from APK-selected Jackson/Gson versions; source validation shows those coordinates resolve to different source versions, so discuss them as scanner-triage evidence with the source mismatch caveat rather than as a clean source-confirmed vulnerability result.

## Limitation Interpretation

Organic Maps and Termux are intentionally not source-validation accuracy claims. They are limitation evidence:

- the extractor handles large, multidex/native-heavy APKs without DEX parse failure;
- reports include native file components with ABI, size, and SHA-256;
- MVP scope does not identify native `.so` package names or versions;
- vulnerability claims remain limited to detected Maven components, not native payloads.
