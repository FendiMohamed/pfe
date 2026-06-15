# APK Testset Inventory And Ground Truth

This file describes the APKs used to test the MVP and how their expected contents are known.
It is meant to support false-positive and false-negative discussion in the thesis and supervisor demo.

## Ground Truth Policy

- Controlled APKs: Exact by construction: each controlled APK records one or more expected Maven artifacts in its .ground-truth.json file.
- Real F-Droid APK: Exact for evaluated components by source validation: the emitted SBOM components are compared with F-Droid's resolved Gradle dependency tree. The full dependency tree has more components than the current calibrated MVP reference scope.
- Source-validated real APKs: Exact for emitted components when the APK is linked to source and a resolved Gradle dependency tree; this now includes F-Droid, OpenTracks, Tusky, and partial-version-mismatch cases such as Conversations.
- Limitation APKs: Not used for precision/recall: limitation APKs exercise forensic warnings and unsupported dynamic/protected packaging behavior.

## Summary

| Field | Value |
|---|---:|
| controlled apks | 72 |
| controlled expected components | 84 |
| controlled detected components | 84 |
| controlled false positive components | 0 |
| controlled false negative components | 0 |
| controlled version mismatches | 0 |
| real apks | 4 |
| limitation apks | 2 |
| fdroid source components total | 203 |
| fdroid evaluated sbom components | 23 |
| fdroid confirmed versions | 23 |
| fdroid version mismatches | 0 |
| fdroid missing coordinates | 0 |
| source validated real apks | 3 |
| partial source validated real apks | 1 |
| real evaluated sbom components | 52 |
| real confirmed versions | 49 |
| real version mismatches | 2 |
| real missing coordinates | 1 |

## Dataset Classification Coverage

The dataset follows the criteria defined in `docs/evaluation/DATASET_DESIGN.md`.

| Layer | APKs | Validation level | Metrics allowed |
|---|---:|---|---|
| controlled | 72 | L1 controlled ground truth | precision, recall, F1, version accuracy, obfuscation robustness |
| limitation | 2 | L3 limitation fixture | forensic warning quality, limitation behavior |
| source-validated-real | 3 | L2 source validated | version correctness, emitted-component source confirmation, emitted-component false positives, candidate mismatch analysis, reference-scope recall only after expected DB-intersection is computed |
| source-validated-real-partial | 1 | L2 source validated partial mismatch | version correctness for emitted components, emitted-component source confirmation, near-version mismatch analysis, artifact-family limitation discussion, reference-scope recall only after expected DB-intersection is computed |

## Controlled APK Fixtures

Controlled fixtures use package `com.example.fixture`, declare exact expected Maven components in `.ground-truth.json`, and currently include both single-DEX/single-library APKs and multi-library multidex APKs. They include no native `.so` files.

| APK | Expected component | Library / language | Variant | R8 mode | Obfuscation | DEX | Native | Current result | FP | FN | OSV |
|---|---|---|---|---|---|---:|---:|---|---:|---:|---|
| `controlled-com-fasterxml-jackson-core-jackson-databind-2.9.10.8-clear.apk` | `com.fasterxml.jackson.core:jackson-databind@2.9.10.8` | Jackson JSON databinding / Java | clear | none | none | 1 | 0 | exact/high | 0 | 0 | 3 vulns |
| `controlled-com-google-code-gson-gson-2.8.9-clear.apk` | `com.google.code.gson:gson@2.8.9` | Gson JSON serialization / Java | clear | none | none | 1 | 0 | exact/high | 0 | 0 | not run |
| `controlled-com-google-code-gson-gson-2.8.9-r8-rename.apk` | `com.google.code.gson:gson@2.8.9` | Gson JSON serialization / Java | r8-rename | rename | light | 1 | 0 | candidate/low | 0 | 0 | not run |
| `controlled-com-google-code-gson-gson-2.8.9-r8-shrink.apk` | `com.google.code.gson:gson@2.8.9` | Gson JSON serialization / Java | r8-shrink | shrink | moderate | 1 | 0 | candidate/low | 0 | 0 | not run |
| `controlled-com-squareup-okhttp3-okhttp-4.9.1-clear.apk` | `com.squareup.okhttp3:okhttp@4.9.1` | OkHttp HTTP client / Kotlin/Java | clear | none | none | 1 | 0 | exact/high | 0 | 0 | not run |
| `controlled-com-squareup-retrofit2-retrofit-2.9.0-clear.apk` | `com.squareup.retrofit2:retrofit@2.9.0` | Retrofit HTTP API client / Java/Kotlin | clear | none | none | 1 | 0 | exact/high | 0 | 0 | not run |
| `controlled-commons-codec-commons-codec-1.16.1-clear.apk` | `commons-codec:commons-codec@1.16.1` | Apache Commons Codec utilities / Java | clear | none | none | 1 | 0 | exact/high | 0 | 0 | not run |
| `controlled-commons-codec-commons-codec-1.16.1-r8-rename.apk` | `commons-codec:commons-codec@1.16.1` | Apache Commons Codec utilities / Java | r8-rename | rename | light | 1 | 0 | candidate/low | 0 | 0 | not run |
| `controlled-commons-codec-commons-codec-1.16.1-r8-shrink.apk` | `commons-codec:commons-codec@1.16.1` | Apache Commons Codec utilities / Java | r8-shrink | shrink | moderate | 1 | 0 | candidate/low | 0 | 0 | not run |
| `controlled-multi-gson-2-8-9-commons-codec-1-16-1-clear-multidex.apk` | `com.google.code.gson:gson@2.8.9`<br>`commons-codec:commons-codec@1.16.1` | Gson JSON serialization; Apache Commons Codec utilities / Java | clear | none | none | 329 | 0 | all matched: exact/high, likely/medium | 0 | 0 | not run |
| `generated-commons-codec-1-15-clear.apk` | `commons-codec:commons-codec@1.15` | Apache Commons Codec utilities / Java | clear | none | none | 1 | 0 | exact/high | 0 | 0 | not run |
| `generated-commons-codec-1-16-0-clear.apk` | `commons-codec:commons-codec@1.16.0` | Apache Commons Codec utilities / Java | clear | none | none | 1 | 0 | exact/high | 0 | 0 | not run |
| `generated-commons-codec-1-16-1-r8-inline-stress.apk` | `commons-codec:commons-codec@1.16.1` | Apache Commons Codec utilities / Java | r8-inline-stress | optimize with inline-like call-site stress | moderate | 1 | 0 | exact/high | 0 | 0 | not run |
| `generated-commons-codec-1-16-1-r8-optimize.apk` | `commons-codec:commons-codec@1.16.1` | Apache Commons Codec utilities / Java | r8-optimize | optimize | moderate | 1 | 0 | exact/high | 0 | 0 | not run |
| `generated-commons-codec-1-16-1-r8-rename.apk` | `commons-codec:commons-codec@1.16.1` | Apache Commons Codec utilities / Java | r8-rename | rename | light | 1 | 0 | candidate/low | 0 | 0 | not run |
| `generated-commons-codec-1-16-1-r8-repackage.apk` | `commons-codec:commons-codec@1.16.1` | Apache Commons Codec utilities / Java | r8-repackage | package flattening/repackaging | high | 1 | 0 | candidate/low | 0 | 0 | not run |
| `generated-commons-codec-1-16-1-r8-shrink-optimize.apk` | `commons-codec:commons-codec@1.16.1` | Apache Commons Codec utilities / Java | r8-shrink-optimize | shrink+optimize | high | 1 | 0 | candidate/low | 0 | 0 | not run |
| `generated-commons-codec-1-16-1-r8-shrink.apk` | `commons-codec:commons-codec@1.16.1` | Apache Commons Codec utilities / Java | r8-shrink | shrink | moderate | 1 | 0 | candidate/low | 0 | 0 | not run |
| `generated-gson-2-8-5-clear.apk` | `com.google.code.gson:gson@2.8.5` | Gson JSON serialization / Java | clear | none | none | 1 | 0 | exact/high | 0 | 0 | not run |
| `generated-gson-2-8-6-clear.apk` | `com.google.code.gson:gson@2.8.6` | Gson JSON serialization / Java | clear | none | none | 1 | 0 | exact/high | 0 | 0 | not run |
| `generated-gson-2-8-9-r8-inline-stress.apk` | `com.google.code.gson:gson@2.8.9` | Gson JSON serialization / Java | r8-inline-stress | optimize with inline-like call-site stress | moderate | 1 | 0 | exact/high | 0 | 0 | not run |
| `generated-gson-2-8-9-r8-optimize.apk` | `com.google.code.gson:gson@2.8.9` | Gson JSON serialization / Java | r8-optimize | optimize | moderate | 1 | 0 | exact/high | 0 | 0 | not run |
| `generated-gson-2-8-9-r8-rename.apk` | `com.google.code.gson:gson@2.8.9` | Gson JSON serialization / Java | r8-rename | rename | light | 1 | 0 | candidate/low | 0 | 0 | not run |
| `generated-gson-2-8-9-r8-repackage.apk` | `com.google.code.gson:gson@2.8.9` | Gson JSON serialization / Java | r8-repackage | package flattening/repackaging | high | 1 | 0 | candidate/low | 0 | 0 | not run |
| `generated-gson-2-8-9-r8-shrink-optimize.apk` | `com.google.code.gson:gson@2.8.9` | Gson JSON serialization / Java | r8-shrink-optimize | shrink+optimize | high | 1 | 0 | candidate/low | 0 | 0 | not run |
| `generated-gson-2-8-9-r8-shrink.apk` | `com.google.code.gson:gson@2.8.9` | Gson JSON serialization / Java | r8-shrink | shrink | moderate | 1 | 0 | candidate/low | 0 | 0 | not run |
| `generated-jackson-databind-2-12-7-1-clear.apk` | `com.fasterxml.jackson.core:jackson-databind@2.12.7.1` | Jackson JSON databinding / Java | clear | none | none | 1 | 0 | exact/high | 0 | 0 | not run |
| `generated-jackson-databind-2-13-5-clear.apk` | `com.fasterxml.jackson.core:jackson-databind@2.13.5` | Jackson JSON databinding / Java | clear | none | none | 1 | 0 | exact/high | 0 | 0 | not run |
| `generated-jackson-databind-2-13-5-r8-inline-stress.apk` | `com.fasterxml.jackson.core:jackson-databind@2.13.5` | Jackson JSON databinding / Java | r8-inline-stress | optimize with inline-like call-site stress | moderate | 1 | 0 | exact/high | 0 | 0 | not run |
| `generated-jackson-databind-2-13-5-r8-optimize.apk` | `com.fasterxml.jackson.core:jackson-databind@2.13.5` | Jackson JSON databinding / Java | r8-optimize | optimize | moderate | 1 | 0 | exact/high | 0 | 0 | not run |
| `generated-jackson-databind-2-13-5-r8-rename.apk` | `com.fasterxml.jackson.core:jackson-databind@2.13.5` | Jackson JSON databinding / Java | r8-rename | rename | light | 1 | 0 | candidate/low | 0 | 0 | not run |
| `generated-jackson-databind-2-13-5-r8-repackage.apk` | `com.fasterxml.jackson.core:jackson-databind@2.13.5` | Jackson JSON databinding / Java | r8-repackage | package flattening/repackaging | high | 1 | 0 | candidate/low | 0 | 0 | not run |
| `generated-jackson-databind-2-13-5-r8-shrink-optimize.apk` | `com.fasterxml.jackson.core:jackson-databind@2.13.5` | Jackson JSON databinding / Java | r8-shrink-optimize | shrink+optimize | high | 1 | 0 | candidate/low | 0 | 0 | not run |
| `generated-jackson-databind-2-13-5-r8-shrink.apk` | `com.fasterxml.jackson.core:jackson-databind@2.13.5` | Jackson JSON databinding / Java | r8-shrink | shrink | moderate | 1 | 0 | candidate/low | 0 | 0 | not run |
| `generated-jackson-databind-2-15-2-clear.apk` | `com.fasterxml.jackson.core:jackson-databind@2.15.2` | Jackson JSON databinding / Java | clear | none | none | 1 | 0 | exact/high | 0 | 0 | not run |
| `generated-ktor-client-core-jvm-2-3-12-clear.apk` | `io.ktor:ktor-client-core-jvm@2.3.12` | unknown / unknown | clear | none | none | 1 | 0 | candidate/low | 0 | 0 | not run |
| `generated-ktor-client-okhttp-jvm-2-3-12-clear.apk` | `io.ktor:ktor-client-okhttp-jvm@2.3.12` | unknown / unknown | clear | none | none | 1 | 0 | candidate/low | 0 | 0 | not run |
| `generated-ktor-http-jvm-2-3-12-clear.apk` | `io.ktor:ktor-http-jvm@2.3.12` | unknown / unknown | clear | none | none | 1 | 0 | candidate/low | 0 | 0 | not run |
| `generated-ktor-io-jvm-2-3-12-clear.apk` | `io.ktor:ktor-io-jvm@2.3.12` | unknown / unknown | clear | none | none | 1 | 0 | candidate/low | 0 | 0 | not run |
| `generated-ktor-utils-jvm-2-3-12-clear.apk` | `io.ktor:ktor-utils-jvm@2.3.12` | unknown / unknown | clear | none | none | 1 | 0 | candidate/low | 0 | 0 | not run |
| `generated-multi-gson-2-8-6-commons-codec-1-16-0-clear-multidex.apk` | `com.google.code.gson:gson@2.8.6`<br>`commons-codec:commons-codec@1.16.0` | Gson JSON serialization; Apache Commons Codec utilities / Java | clear | none | none | 315 | 0 | all matched: exact/high, likely/medium | 0 | 0 | not run |
| `generated-multi-jackson-2-13-5-gson-2-8-6-clear-multidex.apk` | `com.fasterxml.jackson.core:jackson-databind@2.13.5`<br>`com.google.code.gson:gson@2.8.6` | Jackson JSON databinding; Gson JSON serialization / Java | clear | none | none | 896 | 0 | all matched: exact/high, likely/medium | 0 | 0 | not run |
| `generated-multi-ktor-okhttp-jvm-2-3-12-stack-clear-multidex.apk` | `io.ktor:ktor-client-okhttp-jvm@2.3.12`<br>`io.ktor:ktor-client-core-jvm@2.3.12`<br>`io.ktor:ktor-http-jvm@2.3.12`<br>`io.ktor:ktor-io-jvm@2.3.12`<br>`io.ktor:ktor-utils-jvm@2.3.12`<br>`com.squareup.okhttp3:okhttp@4.12.0`<br>`com.squareup.okio:okio-jvm@3.7.0` | unknown; OkHttp HTTP client; Okio I/O primitives / unknown; Kotlin/Java | clear | none | none | 1826 | 0 | all matched: candidate/low, likely/medium | 0 | 0 | not run |
| `generated-multi-okhttp-4-10-0-okio-jvm-3-7-0-clear-multidex.apk` | `com.squareup.okhttp3:okhttp@4.10.0`<br>`com.squareup.okio:okio-jvm@3.7.0` | OkHttp HTTP client; Okio I/O primitives / Kotlin/Java | clear | none | none | 429 | 0 | all matched: likely/medium | 0 | 0 | not run |
| `generated-multi-okhttp-4-12-0-okio-jvm-3-7-0-clear-multidex.apk` | `com.squareup.okhttp3:okhttp@4.12.0`<br>`com.squareup.okio:okio-jvm@3.7.0` | OkHttp HTTP client; Okio I/O primitives / Kotlin/Java | clear | none | none | 429 | 0 | all matched: likely/medium | 0 | 0 | not run |
| `generated-multi-retrofit-2-8-1-okhttp-4-9-1-clear-multidex.apk` | `com.squareup.retrofit2:retrofit@2.8.1`<br>`com.squareup.okhttp3:okhttp@4.9.1` | Retrofit HTTP API client; OkHttp HTTP client / Java/Kotlin; Kotlin/Java | clear | none | none | 434 | 0 | all matched: exact/high, likely/medium | 0 | 0 | not run |
| `generated-okhttp-4-10-0-clear.apk` | `com.squareup.okhttp3:okhttp@4.10.0` | OkHttp HTTP client / Kotlin/Java | clear | none | none | 1 | 0 | exact/high | 0 | 0 | not run |
| `generated-okhttp-4-10-0-r8-inline-stress.apk` | `com.squareup.okhttp3:okhttp@4.10.0` | OkHttp HTTP client / Kotlin/Java | r8-inline-stress | optimize with inline-like call-site stress | moderate | 1 | 0 | exact/high | 0 | 0 | not run |
| `generated-okhttp-4-10-0-r8-optimize.apk` | `com.squareup.okhttp3:okhttp@4.10.0` | OkHttp HTTP client / Kotlin/Java | r8-optimize | optimize | moderate | 1 | 0 | exact/high | 0 | 0 | not run |
| `generated-okhttp-4-10-0-r8-rename.apk` | `com.squareup.okhttp3:okhttp@4.10.0` | OkHttp HTTP client / Kotlin/Java | r8-rename | rename | light | 1 | 0 | candidate/low | 0 | 0 | not run |
| `generated-okhttp-4-10-0-r8-repackage.apk` | `com.squareup.okhttp3:okhttp@4.10.0` | OkHttp HTTP client / Kotlin/Java | r8-repackage | package flattening/repackaging | high | 1 | 0 | candidate/low | 0 | 0 | not run |
| `generated-okhttp-4-10-0-r8-shrink-optimize.apk` | `com.squareup.okhttp3:okhttp@4.10.0` | OkHttp HTTP client / Kotlin/Java | r8-shrink-optimize | shrink+optimize | high | 1 | 0 | candidate/low | 0 | 0 | not run |
| `generated-okhttp-4-10-0-r8-shrink.apk` | `com.squareup.okhttp3:okhttp@4.10.0` | OkHttp HTTP client / Kotlin/Java | r8-shrink | shrink | moderate | 1 | 0 | candidate/low | 0 | 0 | not run |
| `generated-okhttp-4-12-0-clear.apk` | `com.squareup.okhttp3:okhttp@4.12.0` | OkHttp HTTP client / Kotlin/Java | clear | none | none | 1 | 0 | exact/high | 0 | 0 | not run |
| `generated-okhttp-4-8-0-clear.apk` | `com.squareup.okhttp3:okhttp@4.8.0` | OkHttp HTTP client / Kotlin/Java | clear | none | none | 1 | 0 | exact/high | 0 | 0 | not run |
| `generated-okhttp-4-9-0-clear.apk` | `com.squareup.okhttp3:okhttp@4.9.0` | OkHttp HTTP client / Kotlin/Java | clear | none | none | 1 | 0 | exact/high | 0 | 0 | not run |
| `generated-okio-jvm-3-0-0-clear.apk` | `com.squareup.okio:okio-jvm@3.0.0` | Okio I/O primitives / Kotlin/Java | clear | none | none | 1 | 0 | exact/high | 0 | 0 | not run |
| `generated-okio-jvm-3-6-0-clear.apk` | `com.squareup.okio:okio-jvm@3.6.0` | Okio I/O primitives / Kotlin/Java | clear | none | none | 1 | 0 | exact/high | 0 | 0 | not run |
| `generated-okio-jvm-3-7-0-clear.apk` | `com.squareup.okio:okio-jvm@3.7.0` | Okio I/O primitives / Kotlin/Java | clear | none | none | 1 | 0 | exact/high | 0 | 0 | not run |
| `generated-okio-jvm-3-7-0-r8-inline-stress.apk` | `com.squareup.okio:okio-jvm@3.7.0` | Okio I/O primitives / Kotlin/Java | r8-inline-stress | optimize with inline-like call-site stress | moderate | 1 | 0 | exact/high | 0 | 0 | not run |
| `generated-okio-jvm-3-7-0-r8-optimize.apk` | `com.squareup.okio:okio-jvm@3.7.0` | Okio I/O primitives / Kotlin/Java | r8-optimize | optimize | moderate | 1 | 0 | exact/high | 0 | 0 | not run |
| `generated-okio-jvm-3-7-0-r8-rename.apk` | `com.squareup.okio:okio-jvm@3.7.0` | Okio I/O primitives / Kotlin/Java | r8-rename | rename | light | 1 | 0 | candidate/low | 0 | 0 | not run |
| `generated-okio-jvm-3-7-0-r8-repackage.apk` | `com.squareup.okio:okio-jvm@3.7.0` | Okio I/O primitives / Kotlin/Java | r8-repackage | package flattening/repackaging | high | 1 | 0 | candidate/low | 0 | 0 | not run |
| `generated-okio-jvm-3-7-0-r8-shrink-optimize.apk` | `com.squareup.okio:okio-jvm@3.7.0` | Okio I/O primitives / Kotlin/Java | r8-shrink-optimize | shrink+optimize | high | 1 | 0 | candidate/low | 0 | 0 | not run |
| `generated-okio-jvm-3-7-0-r8-shrink.apk` | `com.squareup.okio:okio-jvm@3.7.0` | Okio I/O primitives / Kotlin/Java | r8-shrink | shrink | moderate | 1 | 0 | candidate/low | 0 | 0 | not run |
| `generated-retrofit-2-8-1-clear.apk` | `com.squareup.retrofit2:retrofit@2.8.1` | Retrofit HTTP API client / Java/Kotlin | clear | none | none | 1 | 0 | exact/high | 0 | 0 | not run |
| `generated-retrofit-2-8-1-r8-inline-stress.apk` | `com.squareup.retrofit2:retrofit@2.8.1` | Retrofit HTTP API client / Java/Kotlin | r8-inline-stress | optimize with inline-like call-site stress | moderate | 1 | 0 | exact/high | 0 | 0 | not run |
| `generated-retrofit-2-8-1-r8-optimize.apk` | `com.squareup.retrofit2:retrofit@2.8.1` | Retrofit HTTP API client / Java/Kotlin | r8-optimize | optimize | moderate | 1 | 0 | exact/high | 0 | 0 | not run |
| `generated-retrofit-2-8-1-r8-rename.apk` | `com.squareup.retrofit2:retrofit@2.8.1` | Retrofit HTTP API client / Java/Kotlin | r8-rename | rename | light | 1 | 0 | candidate/low | 0 | 0 | not run |
| `generated-retrofit-2-8-1-r8-repackage.apk` | `com.squareup.retrofit2:retrofit@2.8.1` | Retrofit HTTP API client / Java/Kotlin | r8-repackage | package flattening/repackaging | high | 1 | 0 | candidate/low | 0 | 0 | not run |
| `generated-retrofit-2-8-1-r8-shrink-optimize.apk` | `com.squareup.retrofit2:retrofit@2.8.1` | Retrofit HTTP API client / Java/Kotlin | r8-shrink-optimize | shrink+optimize | high | 1 | 0 | candidate/low | 0 | 0 | not run |
| `generated-retrofit-2-8-1-r8-shrink.apk` | `com.squareup.retrofit2:retrofit@2.8.1` | Retrofit HTTP API client / Java/Kotlin | r8-shrink | shrink | moderate | 1 | 0 | candidate/low | 0 | 0 | not run |

## Limitation APK Fixtures

Limitation fixtures are not used for precision/recall. They test whether the MVP reports unsupported dynamic/protected packaging cautiously.

| APK | Limitation type | Extraction risk | Obfuscation risk | DEX analyzed/failed | Indicators | Components | Report |
|---|---|---|---|---:|---|---:|---|
| `controlled-hidden-dex-loader-limitation.apk` | dynamic-code/protector-style packaging | medium | high | 0/2 | nonstandard-dex; tiny-primary-dex; protector-name-hint; large-opaque-assets | 0 | `data/results/report-limitation-hidden-dex-loader/report.json` |
| `simplify-obfuscated-app.apk` | control-flow/string-obfuscation sample | low | medium | 1/0 | none | 3 | `data/results/report-limitation-simplify-obfuscated-app/report.json` |

## Real APK Case Study

### real-fdroid-1.23.2

| Field | Value |
|---|---|
| Dataset layer | source-validated-real |
| Validation level | L2 source validated |
| APK | `data/test_apks/real/F-Droid.apk` |
| APK SHA-256 | `985f5181d48bb6bafd54083a048b391271e0ab28385881cc41294fb01a222762` |
| Download source | F-Droid package repository |
| Package | `org.fdroid.fdroid` |
| Version | `1.23.2` / code `1023052` |
| Release era | modern |
| Language/framework | Android Gradle app using AndroidX/Jetpack, Compose, Ktor, OkHttp, and native AndroidX graphics path libraries |
| Main library families | AndroidX/Jetpack, Compose, Kotlin/Ktor, networking, native hash-only files |
| AndroidX/Jetpack usage | heavy |
| Kotlin/KMP artifacts | present: Ktor/Compose/Android target variants appear in the calibrated DB |
| Source files counted | 246 Java, 168 Kotlin, 305 XML, 11 Gradle files |
| Source repository | `https://gitlab.com/fdroid/fdroidclient` |
| Source reference | `data/source/fdroidclient-1.23.2` |
| Source tag/commit | `1.23.2` |
| APK/source version match | yes: APK versionName 1.23.2 and versionCode 1023052 match the source release metadata |
| Build system | Gradle Android |
| Dependency tree | `data/results/source-validation/fdroid/app-fullReleaseRuntimeClasspath.txt` |
| Dependency tree configuration | `:app:fullReleaseRuntimeClasspath` |
| DEX files | 2 (classes.dex, classes2.dex) |
| Multidex | true |
| Native files | 4 hash-only components |
| Native ABIs | arm64-v8a, armeabi-v7a, x86, x86_64 |
| R8/minification | R8/minification enabled by Android Gradle build config |
| R8 mode | release minification plus resource shrinking; exact optimizer details are treated as source-level evidence |
| Resource shrinking | yes, according to source build config |
| Obfuscation assessment | low risk |
| Packer/protector indicators | none |
| Dynamic loading indicators | none confirmed; nonstandard DEX list is tracked by APK forensic summary |
| Dependency complexity | high (203 source Maven entries parsed) |
| Overlapping artifact families | Okio/Okio-JVM and AndroidX/KMP target variants |
| Vulnerable dependency expected | no confirmed vulnerability in current calibrated OSV result |
| OSV result | 0 vulnerabilities across 0 vulnerable components |
| Source validation | 23/23 confirmed, 0 mismatches, 0 missing |
| Full source dependency tree size | 203 Maven entries parsed |

### Source-Confirmed Components

| Component | Version | Match type | APK confidence | Source status |
|---|---:|---|---:|---|
| `androidx.gridlayout:gridlayout` | 1.0.0 | hybrid-exact | 0.972 | confirmed |
| `androidx.localbroadcastmanager:localbroadcastmanager` | 1.0.0 | hybrid-candidate | 0.871 | confirmed |
| `androidx.swiperefreshlayout:swiperefreshlayout` | 1.0.0 | hybrid-likely | 0.870 | confirmed |
| `androidx.concurrent:concurrent-futures` | 1.1.0 | hybrid-candidate | 0.843 | confirmed |
| `androidx.recyclerview:recyclerview` | 1.4.0 | hybrid-likely | 0.832 | confirmed |
| `androidx.appcompat:appcompat` | 1.7.0 | hybrid-likely | 0.815 | confirmed |
| `androidx.lifecycle:lifecycle-viewmodel-android` | 2.8.7 | hybrid-likely | 0.808 | confirmed |
| `com.squareup.okhttp3:okhttp` | 4.12.0 | hybrid-likely | 0.807 | confirmed |
| `androidx.exifinterface:exifinterface` | 1.3.6 | hybrid-likely | 0.792 | confirmed |
| `io.ktor:ktor-client-okhttp-jvm` | 2.3.12 | hybrid-candidate | 0.788 | confirmed |
| `androidx.work:work-runtime` | 2.10.0 | hybrid-likely | 0.775 | confirmed |
| `androidx.fragment:fragment` | 1.6.1 | hybrid-candidate | 0.749 | confirmed |
| `androidx.compose.ui:ui-android` | 1.7.8 | hybrid-candidate | 0.727 | confirmed |
| `org.jetbrains.kotlinx:kotlinx-coroutines-android` | 1.7.3 | hybrid-candidate | 0.706 | confirmed |
| `androidx.lifecycle:lifecycle-runtime-android` | 2.8.7 | hybrid-candidate | 0.677 | confirmed |
| `androidx.activity:activity` | 1.10.1 | hybrid-candidate | 0.633 | confirmed |
| `com.squareup.okio:okio-jvm` | 3.7.0 | hybrid-candidate | 0.587 | confirmed |
| `androidx.lifecycle:lifecycle-livedata` | 2.8.7 | hybrid-candidate | 0.578 | confirmed |
| `org.jetbrains.kotlinx:kotlinx-coroutines-core-jvm` | 1.7.3 | hybrid-candidate | 0.535 | confirmed |
| `com.google.android.material:material` | 1.12.0 | hybrid-candidate | 0.535 | confirmed |
| `androidx.compose.foundation:foundation-android` | 1.7.8 | hybrid-candidate | 0.524 | confirmed |
| `androidx.core:core` | 1.15.0 | hybrid-candidate | 0.500 | confirmed |
| `io.ktor:ktor-http-jvm` | 2.3.12 | hybrid-candidate | 0.456 | confirmed |

### Extra Candidate Check

| Candidate | MVP version | Source versions | Status |
|---|---:|---|---|
| `com.squareup.okio:okio` | 2.8.0 | 3.7.0 | version-mismatch |
### real-opentracks-v4.27.0irreproducible

| Field | Value |
|---|---|
| Dataset layer | source-validated-real |
| Validation level | L2 source validated |
| APK | `data/test_apks/real/opentracks/opentracks.apk` |
| APK SHA-256 | `e5e51772ec2cd9f1474bc6d8cc6a180f6a286a690dc21226d974eac1c1c6b201` |
| Download source | F-Droid package repository |
| Package | `de.dennisguse.opentracks` |
| Version | `v4.27.0irreproducible` / code `6653` |
| Release era | modern |
| Language/framework | Android Gradle app using AndroidX, Material Components, Kotlin runtime libraries, and WorkManager |
| Main library families | AndroidX/Jetpack, Material Components, Kotlin coroutines/runtime, WorkManager, location/maps support |
| AndroidX/Jetpack usage | heavy |
| Kotlin/KMP artifacts | present as overlapping AndroidX Lifecycle public/Android target variants |
| Source files counted | 294 Java, 0 Kotlin, 221 XML, 2 Gradle files |
| Source repository | `https://codeberg.org/OpenTracksApp/OpenTracks` |
| Source reference | `data/source/opentracks-v4.27.0irreproducible/source/de.dennisguse.opentracks_6653_src.tar.gz` |
| Source tag/commit | `f143aabfbf77d1b71864042fe4f0bbf2b4174f4f` |
| APK/source version match | yes: APK versionName v4.27.0irreproducible and versionCode 6653 match the F-Droid metadata/source build evidence |
| Build system | Gradle Android |
| Dependency tree | `data/results/source-validation/opentracks/fullReleaseRuntimeClasspath.txt` |
| Dependency tree configuration | `irreproducibleReleaseRuntimeClasspath` |
| DEX files | 4 (classes.dex, classes2.dex, classes3.dex, classes4.dex) |
| Multidex | true |
| Native files | 0 hash-only components |
| Native ABIs | none |
| R8/minification | R8/minification disabled by release build config |
| R8 mode | none |
| Resource shrinking | no source-level evidence in current proof bundle |
| Obfuscation assessment | low risk |
| Packer/protector indicators | none |
| Dynamic loading indicators | none confirmed; nonstandard DEX list is tracked by APK forensic summary |
| Dependency complexity | medium (95 source Maven entries parsed) |
| Overlapping artifact families | AndroidX Lifecycle public coordinates and Android target variants |
| Vulnerable dependency expected | no confirmed vulnerability in current calibrated OSV result |
| OSV result | 0 vulnerabilities across 0 vulnerable components |
| Source validation | 19/19 confirmed, 0 mismatches, 0 missing |
| Full source dependency tree size | 95 Maven entries parsed |

### Source-Confirmed Components

| Component | Version | Match type | APK confidence | Source status |
|---|---:|---|---:|---|
| `androidx.gridlayout:gridlayout` | 1.1.0 | hybrid-exact | 0.994 | confirmed |
| `androidx.viewpager2:viewpager2` | 1.0.0 | hybrid-exact | 0.989 | confirmed |
| `androidx.recyclerview:recyclerview` | 1.2.1 | hybrid-exact | 0.988 | confirmed |
| `androidx.core:core` | 1.18.0 | hybrid-exact | 0.932 | confirmed |
| `org.jetbrains.kotlinx:kotlinx-coroutines-core-jvm` | 1.9.0 | hybrid-exact | 0.925 | confirmed |
| `androidx.fragment:fragment` | 1.5.4 | hybrid-likely | 0.914 | confirmed |
| `androidx.startup:startup-runtime` | 1.1.1 | hybrid-likely | 0.909 | confirmed |
| `com.google.android.material:material` | 1.13.0 | hybrid-likely | 0.898 | confirmed |
| `androidx.localbroadcastmanager:localbroadcastmanager` | 1.0.0 | hybrid-candidate | 0.886 | confirmed |
| `androidx.concurrent:concurrent-futures` | 1.1.0 | hybrid-candidate | 0.880 | confirmed |
| `androidx.appcompat:appcompat` | 1.7.1 | hybrid-candidate | 0.871 | confirmed |
| `androidx.lifecycle:lifecycle-runtime` | 2.6.2 | hybrid-candidate | 0.858 | confirmed |
| `androidx.lifecycle:lifecycle-viewmodel` | 2.6.2 | hybrid-candidate | 0.853 | confirmed |
| `org.jetbrains.kotlin:kotlin-stdlib` | 2.2.10 | hybrid-candidate | 0.848 | confirmed |
| `androidx.activity:activity` | 1.8.0 | hybrid-candidate | 0.844 | confirmed |
| `androidx.lifecycle:lifecycle-livedata` | 2.6.2 | hybrid-likely | 0.829 | confirmed |
| `androidx.work:work-runtime` | 2.11.2 | hybrid-likely | 0.808 | confirmed |
| `androidx.core:core-ktx` | 1.18.0 | hybrid-candidate | 0.797 | confirmed |
| `org.jetbrains.kotlinx:kotlinx-coroutines-android` | 1.9.0 | hybrid-candidate | 0.672 | confirmed |
### real-tusky-32.2

| Field | Value |
|---|---|
| Dataset layer | source-validated-real |
| Validation level | L2 source validated |
| APK | `data/test_apks/real/tusky/tusky.apk` |
| APK SHA-256 | `3e8fcc49a80d4c30ab6f6037e51402c77e2694d27ec19ae5b8a93cd08b6caffa` |
| Download source | F-Droid package repository |
| Package | `com.keylesspalace.tusky` |
| Version | `32.2` / code `142` |
| Release era | modern |
| Language/framework | Android Gradle social client using Kotlin, AndroidX, Retrofit, OkHttp, Moshi, Coil, Glide, and native image/security libraries |
| Main library families | AndroidX/Jetpack, networking, Retrofit/OkHttp, Moshi, image loading, native hash-only files |
| AndroidX/Jetpack usage | heavy |
| Kotlin/KMP artifacts | present in the source tree through modern AndroidX/Kotlin dependencies |
| Source files counted | 4 Java, 465 Kotlin, 382 XML, 5 Gradle files |
| Source repository | `https://codeberg.org/tusky/Tusky` |
| Source reference | `data/source/tusky-32.2/source/com.keylesspalace.tusky_142_src.tar.gz` |
| Source tag/commit | `ff0c9f58874fafc72a53789f079ce0dc1a7e9207` |
| APK/source version match | yes: APK versionName 32.2 and versionCode 142 match the F-Droid metadata/source build evidence |
| Build system | Gradle Android |
| Dependency tree | `data/results/source-validation/tusky/blueReleaseRuntimeClasspath.txt` |
| Dependency tree configuration | `blueReleaseRuntimeClasspath` |
| DEX files | 1 (classes.dex) |
| Multidex | false |
| Native files | 16 hash-only components |
| Native ABIs | arm64-v8a, armeabi-v7a, x86, x86_64 |
| R8/minification | R8/minification enabled by release build config |
| R8 mode | release minification plus resource shrinking |
| Resource shrinking | yes, according to source build.gradle |
| Obfuscation assessment | low risk |
| Packer/protector indicators | native-heavy |
| Dynamic loading indicators | none confirmed; nonstandard DEX list is tracked by APK forensic summary |
| Dependency complexity | high (261 source Maven entries parsed) |
| Overlapping artifact families | Retrofit/OkHttp/Okio and AndroidX/KMP target variants |
| Vulnerable dependency expected | no confirmed vulnerability in current calibrated OSV result |
| OSV result | 0 vulnerabilities across 0 vulnerable components |
| Source validation | 1/1 confirmed, 0 mismatches, 0 missing |
| Full source dependency tree size | 261 Maven entries parsed |

### Source-Confirmed Components

| Component | Version | Match type | APK confidence | Source status |
|---|---:|---|---:|---|
| `com.squareup.retrofit2:retrofit` | 3.0.0 | hybrid-candidate | 0.193 | confirmed |
### real-conversations-2.20.0-free

| Field | Value |
|---|---|
| Dataset layer | source-validated-real-partial |
| Validation level | L2 source validated partial mismatch |
| APK | `data/test_apks/real/conversations/conversations.apk` |
| APK SHA-256 | `081772cb77bf8f5d7a1afac4e4846ff104d83becc558ffc7f625af6fba5dade9` |
| Download source | F-Droid package repository |
| Package | `eu.siacs.conversations` |
| Version | `2.20.0+free` / code `4217704` |
| Release era | modern app with older codebase history |
| Language/framework | Android messaging/security app using AndroidX, Retrofit, OkHttp, Gson, Conscrypt, WebRTC, Bouncy Castle, and XMPP libraries |
| Main library families | AndroidX/Jetpack, networking, Retrofit/OkHttp, Gson, security/crypto, native WebRTC/Conscrypt files |
| AndroidX/Jetpack usage | heavy |
| Kotlin/KMP artifacts | present through OkHttp/Okio and AndroidX target-variant overlap |
| Source files counted | 854 Java, 0 Kotlin, 493 XML, 5 Gradle files |
| Source repository | `https://codeberg.org/iNPUTmice/Conversations` |
| Source reference | `data/source/conversations/extracted/eu.siacs.conversations_4217704_src.tar.gz` |
| Source tag/commit | `7346a14dcedb155762133ea3ec512fdf34b57876` |
| APK/source version match | yes: APK versionName 2.20.0+free and versionCode 4217704 match the F-Droid metadata/source build evidence |
| Build system | Gradle Android |
| Dependency tree | `data/results/source-validation/conversations/conversationsFreeReleaseRuntimeClasspath.txt` |
| Dependency tree configuration | `conversationsFreeReleaseRuntimeClasspath` |
| DEX files | 2 (classes.dex, classes2.dex) |
| Multidex | true |
| Native files | 2 hash-only components |
| Native ABIs | arm64-v8a |
| R8/minification | R8/minification enabled by release build config |
| R8 mode | release minification plus resource shrinking |
| Resource shrinking | yes, according to source build.gradle |
| Obfuscation assessment | low risk |
| Packer/protector indicators | none |
| Dynamic loading indicators | none confirmed; nonstandard DEX list is tracked by APK forensic summary |
| Dependency complexity | high (136 source Maven entries parsed) |
| Overlapping artifact families | AndroidX near-version ties and Lifecycle public/Android target variants |
| Vulnerable dependency expected | no confirmed vulnerability in current calibrated OSV result |
| OSV result | 0 vulnerabilities across 0 vulnerable components |
| Source validation | 6/9 confirmed, 2 mismatches, 1 missing |
| Full source dependency tree size | 136 Maven entries parsed |

### Source-Confirmed Components

| Component | Version | Match type | APK confidence | Source status |
|---|---:|---|---:|---|
| `androidx.concurrent:concurrent-futures` | 1.1.0 | hybrid-candidate | 0.681 | version-mismatch |
| `androidx.exifinterface:exifinterface` | 1.4.2 | hybrid-candidate | 0.625 | confirmed |
| `com.squareup.retrofit2:retrofit` | 3.0.0 | hybrid-candidate | 0.612 | confirmed |
| `com.google.code.gson:gson` | 2.13.1 | hybrid-candidate | 0.588 | confirmed |
| `androidx.swiperefreshlayout:swiperefreshlayout` | 1.2.0 | hybrid-candidate | 0.554 | confirmed |
| `androidx.startup:startup-runtime` | 1.1.1 | hybrid-candidate | 0.549 | version-mismatch |
| `androidx.appcompat:appcompat` | 1.7.1 | hybrid-candidate | 0.540 | confirmed |
| `androidx.recyclerview:recyclerview` | 1.2.1 | hybrid-candidate | 0.523 | confirmed |
| `androidx.lifecycle:lifecycle-runtime-android` | 2.9.4 | hybrid-candidate | 0.406 | missing |

## Interpretation For FP/FN Analysis

- On controlled APKs, false positives and false negatives can be measured directly because each APK contains exactly one known Maven component/version.
- On the calibrated F-Droid APK, the current thesis-grade claim is version correctness for the 23 emitted SBOM components, validated against source. It is not a claim that all 203 source dependency-tree entries are recovered.
- On the calibrated OpenTracks APK, the claim is version correctness for the 19 emitted SBOM components, validated against the resolved Gradle dependency tree.
- On the calibrated Tusky APK, the one emitted Maven component is source-confirmed after adding the source-used Retrofit 3.0.0 reference. Treat it as a sparse source-validated case, not a broad recall result.
- The full expanded F-Droid smoke test is useful as a stress test because it intentionally shows how latest-only broad references can introduce version mismatches.

## Regeneration Command

```powershell
python scripts/build_apk_testset_inventory.py
```
