# Expanded Reference DB Evaluation

Date: 2026-05-20.

This note records the first batch builds and smoke evaluation of the expanded Android/Maven reference catalog.

## Batch Build Status

Input config:

```text
configs/libraries.expanded.json
```

Generated data:

```text
data/reference_db/artifacts_expanded/
data/reference_db/dex_expanded/
data/reference_db/reference_features_expanded.sqlite
data/reference_db/reference_features_combined.sqlite
```

Current expanded-only build:

| Field | Result |
|---|---:|
| Catalog offsets checked | 0-162, all expanded artifact-version entries |
| Unique artifact records in expanded cache | 141 |
| Usable DEX components | 108 |
| Skipped no-bytecode or metadata-only artifacts | 33 |
| Failed artifacts after fixes | 0 |
| Classes | 39,326 |
| Methods | 279,212 |
| Packages | 1,202 |
| Class dependency edges | 100,612 |
| String literals | 51,776 |

The offset-70 batch completed with 10 already-cached artifacts, 0 download failures, and no new unique artifact records. Conversion and feature extraction were rerun after the batch; the expanded-only and combined DB counts stayed unchanged.

The offset-80 batch completed with 7 downloaded artifacts, 3 already-cached artifacts, 0 download failures, 6 newly converted DEX components, and 1 new no-bytecode skip. Conversion and feature extraction were rerun after the batch, raising the expanded-only DB from 32 to 38 usable components.

The offset-90 batch initially failed for `com.google.crypto.tink:tink-android@1.21.0` because the catalog marked it as `aar`; the published Maven Central artifact is a `jar`. After fixing the curated catalog and regenerated expanded config entry, the batch completed with 10 newly converted DEX components and 0 remaining failures.

The offset-100 batch initially failed for `com.google.dagger:dagger-android@2.59.2` because the catalog marked it as `jar`; the published Maven Central artifact is an `aar`. After fixing the curated catalog and expanded config entry, the batch completed with 9 newly converted DEX components and 1 new no-bytecode skip for `com.google.firebase:firebase-analytics@23.2.0`. The offset-110 batch completed with 10 newly converted DEX components and 0 failures.

The final offset-120 pass covered the remaining 43 artifact-version entries through the end of `configs/libraries.expanded.json`. It initially failed for `org.greenrobot:eventbus@3.3.1` because the catalog marked it as `jar`; the published Maven Central artifact is an `aar`. After fixing the curated catalog and expanded config entry, the final pass completed with 41 newly converted DEX components, 2 new no-bytecode skips, and 0 remaining failures.

Combined evaluation DB:

| Field | Result |
|---|---:|
| Components | 133 |
| DEX files | 133 |
| Classes | 46,620 |
| Methods | 346,404 |
| Packages | 1,492 |
| Class dependency edges | 125,301 |
| String literals | 68,300 |

## Issues Found And Fixed

The batch build exposed two important catalog/tooling issues:

| Issue | Resolution |
|---|---|
| Several modern AndroidX/Compose/DataStore AARs have no top-level `classes.jar`. | The converter now treats missing `classes.jar` as a documented `skipped` no-bytecode result instead of a hard failure. |
| `androidx.datastore:datastore-preferences-core` was configured as `aar`, but the direct artifact is a JAR-style coordinate. | The catalog entry was changed to `jar`; after Android target variants and calibration entries were added, `configs/libraries.expanded.json` regenerated successfully with 147/147 resolved coordinates. |
| `com.google.crypto.tink:tink-android` was configured as `aar`, but Maven Central publishes version `1.21.0` as a JAR artifact. | The catalog and expanded config entry were changed to `jar`; the offset-90 batch then downloaded and converted cleanly. |
| `com.google.dagger:dagger-android` was configured as `jar`, but Maven Central publishes version `2.59.2` as an AAR artifact. | The catalog and expanded config entry were changed to `aar`; the offset-100 batch then downloaded and converted cleanly. |
| `org.greenrobot:eventbus` was configured as `jar`, but Maven Central publishes version `3.3.1` as an AAR artifact. | The catalog and expanded config entry were changed to `aar`; the final offset-120 pass then downloaded and converted cleanly. |

This also revealed a key calibration rule: many modern AndroidX/KMP libraries publish metadata or wrapper coordinates, while the APK bytecode may correspond to Android target variants such as `*-android`. The MVP now skips metadata-only artifacts safely, and the calibrated slice adds Android target coordinates intentionally.

## F-Droid Smoke Evaluation

The full expanded/latest-only combined DB was run on F-Droid after completing the expanded catalog.

Command output folder:

```text
data/results/report-real-f-droid-full-expanded-db/
```

Source validation output:

```text
data/results/source-validation/fdroid-full-expanded/
```

Result against the F-Droid source dependency tree:

| Group | Components | Confirmed | Version mismatch | Missing |
|---|---:|---:|---:|---:|
| SBOM components | 26 | 12 | 13 | 1 |
| Extra suppressed candidate | 1 | 0 | 1 | 0 |

Confirmed full-expanded SBOM components:

| Component | Version |
|---|---:|
| `androidx.localbroadcastmanager:localbroadcastmanager` | 1.0.0 |
| `androidx.swiperefreshlayout:swiperefreshlayout` | 1.0.0 |
| `io.ktor:ktor-client-okhttp-jvm` | 2.3.12 |
| `com.squareup.okhttp3:okhttp` | 4.12.0 |
| `androidx.work:work-runtime` | 2.10.0 |
| `androidx.recyclerview:recyclerview` | 1.4.0 |
| `androidx.preference:preference` | 1.2.1 |
| `com.squareup.okio:okio-jvm` | 3.7.0 |
| `androidx.cardview:cardview` | 1.0.0 |
| `io.reactivex.rxjava3:rxandroid` | 3.0.2 |
| `io.ktor:ktor-http-jvm` | 2.3.12 |
| `io.ktor:ktor-client-core-jvm` | 2.3.12 |

Full-expanded interpretation:

- The full expanded DB increased identity coverage from 18 broad/latest-only SBOM components in the earlier smoke run to 26 components.
- Most mismatches are coordinates that are present in F-Droid source but where the expanded DB only has a newer latest-stable reference version, for example AndroidX, KotlinX, SLF4J, and Glide.
- One emitted coordinate, `org.bouncycastle:bcprov-jdk18on@1.84`, was not found in the provided F-Droid dependency tree and should be treated as a broad-DB false positive or unresolved source-tree limitation until separately investigated.
- This result strengthens the calibration argument: expanding identity coverage is useful, but exact SBOM version claims need multiple versions or source-used versions.

## Earlier Broad Smoke Evaluation

The smoke validation below was run on the earlier 58-component combined DB. The latest combined DB has 59 components after the offset-60 batch, but this broad/latest-only validation has not been rerun because the calibrated DB is the stronger source-validated result.

Command output folder:

```text
data/results/report-real-f-droid-combined-expanded-db/
```

Source validation output:

```text
data/results/source-validation/fdroid-combined-expanded/
```

Result against the F-Droid source dependency tree:

| Group | Components | Confirmed | Version mismatch | Missing |
|---|---:|---:|---:|---:|
| SBOM components | 18 | 7 | 11 | 0 |
| Extra suppressed candidate | 1 | 0 | 1 | 0 |

Interpretation:

- The expanded DB improved identity coverage: the extra AndroidX coordinates emitted by the matcher were present in the source dependency tree, so they were not pure false-positive identities.
- Version accuracy degraded for many expanded AndroidX components because the expanded catalog currently stores only the latest stable version per coordinate, while F-Droid resolves older versions.
- The matcher now caps confidence for one-version coordinates: unless a single-version reference is an almost complete match, it is reported as a low-confidence `candidate`, not `likely` or `exact`.
- The focused seed DB is still better for source-confirmed version claims. The expanded DB should remain an evaluation/stress DB until it includes multiple versions per coordinate or source-used versions for real case studies.

## Confirmed Combined SBOM Components

| Component | Version | Result |
|---|---:|---|
| `com.squareup.okhttp3:okhttp` | 4.12.0 | confirmed |
| `io.ktor:ktor-client-okhttp-jvm` | 2.3.12 | confirmed |
| `androidx.recyclerview:recyclerview` | 1.4.0 | confirmed |
| `androidx.preference:preference` | 1.2.1 | confirmed |
| `androidx.cardview:cardview` | 1.0.0 | confirmed |
| `com.squareup.okio:okio-jvm` | 3.7.0 | confirmed |
| `io.ktor:ktor-http-jvm` | 2.3.12 | confirmed |

## Next Actions

1. Rerun full tests after each matcher/configuration change.
2. Add multiple/source-used versions before using any new expanded coordinate for version-level claims.
3. Keep calibrated real-APK validation separate from broad benchmark claims.
4. Treat OSV findings from low-confidence expanded/latest-only versions as potential, not confirmed.
5. Package the controlled, calibrated, and full-expanded results for the thesis/paper.

## Calibrated Real-APK Slice

After the first smoke evaluation, a calibration config was added:

```text
configs/libraries.calibration.json
```

It contains:

- F-Droid and OpenTracks source-used AndroidX/Kotlin versions for coordinates that previously had version mismatches or missing comparable versions.
- Latest stable versions for comparison.
- Android target variants for KMP/metadata-wrapper libraries, including Compose UI/Foundation, DataStore Android, and Lifecycle Android artifacts.

Generated data:

```text
data/reference_db/artifacts_calibration/
data/reference_db/dex_calibration/
data/reference_db/reference_features_calibration.sqlite
data/reference_db/reference_features_calibrated_combined.sqlite
```

Calibration build result:

| Field | Result |
|---|---:|
| Calibration coordinates | 31 |
| Calibration artifacts | 55 |
| Converted calibration artifacts | 53 |
| Skipped calibration artifacts | 2 |
| Failed calibration artifacts | 0 |
| Calibration DB components | 53 |
| Calibration DB classes | 24,193 |
| Calibration DB methods | 160,865 |
| Calibration DB class dependency edges | 43,004 |
| Calibrated combined DB components | 80 |
| Calibrated combined DB methods | 230,085 |

F-Droid source-validation improvement:

| DB | SBOM components | Confirmed | Version mismatch | Missing |
|---|---:|---:|---:|---:|
| Focused DB | 4 | 4 | 0 | 0 |
| Latest-only expanded combined DB | 18 | 7 | 11 | 0 |
| First calibrated DB | 18 | 15 | 3 | 0 |
| Final single-app calibrated DB | 19 | 19 | 0 | 0 |
| Current two-app calibrated DB | 23 | 23 | 0 | 0 |

OpenTracks source-validation result on the same current calibrated DB:

| APK | SBOM components | Confirmed | Version mismatch | Missing |
|---|---:|---:|---:|---:|
| OpenTracks | 19 | 19 | 0 | 0 |

Final calibrated report:

```text
data/results/report-real-f-droid-calibrated-db/
data/results/source-validation/fdroid-calibrated/
data/results/report-real-f-droid-final-demo-osv/
data/results/source-validation/fdroid-final-demo-osv/
data/results/report-real-opentracks-calibrated-db/
data/results/source-validation/opentracks-calibrated-db/
```

Interpretation:

- Adding more coordinates improved component identity coverage, but latest-only references produced wrong versions for real APKs.
- Adding source-used versions fixed the version mismatch problem for this case study.
- Android target variants matter for modern KMP libraries: direct metadata/wrapper coordinates can have no bytecode, while `*-android` artifacts are bytecode-bearing and match APK DEX evidence.
- The two calibration skips are expected Lifecycle public coordinates whose comparable bytecode is represented by Android target artifacts; they are tracked as skips and do not enter the feature DB.
- The calibrated F-Droid and OpenTracks results are strong evidence for the MVP architecture: reference coverage and version coverage directly control SBOM accuracy.
- These are still real APK case studies, not a broad benchmark. The calibrated DB should be presented as case-study validation, not as proof of universal accuracy.
