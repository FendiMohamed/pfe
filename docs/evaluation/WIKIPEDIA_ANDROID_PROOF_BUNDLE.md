# Wikipedia Android Proof Bundle

Status: source-validated partial-version-mismatch case.

## Identity

| Field | Value |
|---|---|
| App | Wikipedia Android |
| Package | `org.wikipedia` |
| F-Droid versionName | `r/50586-r-2026-05-12` |
| F-Droid versionCode | `50586` |
| F-Droid source commit | `40876929c5a84e1a1f968b29184c245582c7ff9a` |
| F-Droid subdir | `app` |
| F-Droid Gradle flavor | `fdroid` |

## Collected Artifacts

| Artifact | Path / value |
|---|---|
| APK | `data/test_apks/real/wikipedia-android/wikipedia-android.apk` |
| APK SHA-256 | `257a76008b01960b21ffe09d4138fd63d8eb73ec388c84f0ceabf559511d893c` |
| F-Droid metadata | `data/test_apks/real/wikipedia-android/fdroid-metadata.yml` |
| APK archive metadata | `data/test_apks/real/wikipedia-android/metadata.json` |
| F-Droid source tarball | `data/source/wikipedia-android/source.tar.gz` |
| Source tarball SHA-256 | `4a9bc8bf3ab0a156dd2891a16bdd2f6a6cdcce42198a5a68767965f2b7f034f0` |
| Extracted source root | `data/source/wikipedia-android/source/org.wikipedia_50586_src.tar.gz` |
| MVP report | `data/results/report-real-wikipedia-android/report.md` |
| CycloneDX SBOM | `data/results/report-real-wikipedia-android/sbom.cdx.json` |
| Gradle dependency tree | `data/results/source-validation/wikipedia-android/fdroidReleaseRuntimeClasspath.txt` |
| Source validation | `data/results/source-validation/wikipedia-android-report-validation/source-validation.md` |

## APK Observed Profile

| Field | Value |
|---|---|
| DEX files | 2 standard files: `classes.dex`, `classes2.dex` |
| Multidex | true |
| Native files | 8 |
| Native ABIs | `arm64-v8a`, `armeabi-v7a`, `x86`, `x86_64` |
| Native library families | `libandroidx.graphics.path.so`, `libmaplibre.so` |
| Manifest/resources | `AndroidManifest.xml` and `resources.arsc` present |

## Source Evidence

The extracted `app/build.gradle` confirms:

- `applicationId 'org.wikipedia'`
- `versionCode 50586`
- `versionName 'r/50586-r-2026-05-12'`
- `minSdk = 23`
- `targetSdk = 36`
- product flavor `fdroid`

The F-Droid build entry uses the same versionCode, versionName, commit, subdir, and Gradle flavor.

## MVP Result

Docker was restarted successfully and the source tarball was re-extracted inside the Linux container before running Gradle.

| Field | Result |
|---|---:|
| Detected Maven components | 13 |
| Native file components | 8 |
| OSV vulnerabilities | 0 |
| Source components parsed | 255 |
| Source-confirmed SBOM versions | 11 |
| Version mismatches | 2 |
| Missing coordinates | 0 |

The Wikipedia run improved after adding source-used `com.google.code.gson:gson@2.10.1` and bytecode-bearing `com.squareup.okhttp3:okhttp-android@5.3.2` to the calibrated reference set. A generic OkHttp public-vs-Android target artifact-family rule now suppresses the overlapping stale `okhttp@4.10.0` SBOM component when `okhttp-android@5.3.2` is the better APK bytecode candidate.

Remaining mismatches:

| Component | MVP version | Source version | Interpretation |
|---|---:|---:|---|
| `androidx.startup:startup-runtime` | 1.1.1 | 1.2.0 | Near-tie already seen in NewPipe; not forced without stronger generic evidence. |
| `androidx.viewpager2:viewpager2` | 1.0.0 | 1.1.0 | AndroidX near-version ambiguity; not forced by source-specific rules. |

Use Wikipedia as a source-validated partial-mismatch case, not as a clean accuracy case.

## Reproduction Commands

```powershell
docker compose run --rm apk-sbom python -m apk_sbom.cli inspect-apk data/test_apks/real/wikipedia-android/wikipedia-android.apk
docker compose run --rm apk-sbom python -m apk_sbom.cli generate-report data/test_apks/real/wikipedia-android/wikipedia-android.apk --output-dir data/results/report-real-wikipedia-android --db-path data/reference_db/reference_features_calibrated_combined.sqlite --top 30
docker compose run --rm -e GRADLE_USER_HOME=/app/data/source/.gradle-cache-wikipedia apk-sbom sh -lc "rm -rf /tmp/wikipedia-source && mkdir -p /tmp/wikipedia-source /app/data/results/source-validation/wikipedia-android && tar -xzf /app/data/source/wikipedia-android/source.tar.gz -C /tmp/wikipedia-source && cd /tmp/wikipedia-source/org.wikipedia_50586_src.tar.gz && /opt/gradle/bin/gradle --no-daemon :app:dependencies --configuration fdroidReleaseRuntimeClasspath > /app/data/results/source-validation/wikipedia-android/fdroidReleaseRuntimeClasspath.txt 2> /app/data/results/source-validation/wikipedia-android/gradle-error.log"
docker compose run --rm apk-sbom python -m apk_sbom.cli validate-source-deps --sbom data/results/report-real-wikipedia-android/sbom.cdx.json --dependency-tree data/results/source-validation/wikipedia-android/fdroidReleaseRuntimeClasspath.txt --output-dir data/results/source-validation/wikipedia-android-report-validation
```
