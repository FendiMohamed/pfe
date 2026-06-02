# OsmAnd Proof Bundle

## Classification

OsmAnd~ `5.3.10` / `531003` is a source-validated partial native-heavy maps case.

It is useful because it combines a very large APK, eight DEX files, AndroidX/Kotlin dependencies, and a substantial native payload. It should not be presented as a clean exact-version accuracy case.

## Inputs

| Item | Value |
|---|---|
| APK | `data/test_apks/real/osmand/osmand.apk` |
| APK SHA-256 | `27f1eb82d288a9939b7c0bdd0fb94f78749824ffc753d32d421e01cbe487e5e0` |
| Source tarball | `data/source/osmand-5.3.10/source.tar.gz` |
| Source tarball SHA-256 | `a27e94ecb241db75c7fc49f8541fff6d71be6b830f3f16d476f39c879d2d155a` |
| F-Droid metadata | `data/test_apks/real/osmand/fdroid-metadata.yml` |
| F-Droid build log | `data/results/source-validation/osmand/fdroid-build-531003.log.gz` |
| Source tag | `v5.3.10` |
| Source subdir | `android/OsmAnd` |
| F-Droid flavors | `android`, `full`, `opengl`, `arm64` |
| F-Droid NDK | `r28c` |

The source archive uses a misleading `.tar.gz` suffix but is extracted with plain `tar -xf`.

## APK Inspection

`inspect-apk` confirms:

- package `net.osmand.plus`
- versionName `5.3.10`
- versionCode `531003`
- minSdk `24`
- targetSdk `35`
- 8 standard DEX files
- 6 `arm64-v8a` native libraries
- medium extraction risk only because map icon asset names contain the substring `shell`

Native files are reported as hash-only CycloneDX file components:

- `libOsmAndCoreWithJNI.so`
- `libQt5Core.so`
- `libQt5Network.so`
- `libQt5Sql.so`
- `libc++_shared.so`
- `libosmand.so`

## Report Result

The calibrated report is stored at `data/results/report-real-osmand/`.

Summary:

- 25 Maven SBOM components
- 6 native file components
- 4 OSV findings from APK-selected Maven versions
- 0 DEX parse failures

OSV returned 3 advisories for `com.fasterxml.jackson.core:jackson-databind@2.9.10.8` and 1 advisory for `com.google.code.gson:gson@2.8.5`. Source validation shows both coordinates are present but resolved to different source versions, so these findings should be discussed with the source-validation mismatch caveat.

## Source Validation

The dependency tree was generated with:

```sh
sh /app/data/results/source-validation/osmand/run-gradle-deps.sh
```

The script applies only the F-Droid configuration edits needed for dependency resolution and uses cached Gradle `8.10.2`. Gradle `9.5.0` fails before dependency resolution because the OsmAnd build script uses `XmlParser`.

Validation output:

| Metric | Count |
|---|---:|
| Source components parsed | 143 |
| SBOM Maven components | 25 |
| Confirmed versions | 16 |
| Version mismatches | 9 |
| Missing coordinates | 0 |

Interpretation: OsmAnd is source-validated for emitted Maven dependency comparison, but partial because several selected versions differ from the resolved source dependency tree. The case strengthens the evaluation as a native-heavy maps stress test and should stay out of the clean-real bucket.
