# APK Dataset Design For Research Evaluation

This document defines how APKs should be selected, classified, and validated for the APK-to-SBOM MVP evaluation. The goal is to make the dataset explain the results: each APK should test a known capability, limitation, or research question.

## Main Principle

Do not collect APKs randomly. Build a layered dataset:

- Controlled APKs prove accuracy under known conditions.
- Source-validated real APKs prove the method on real apps with verifiable dependency evidence.
- Smoke-test real APKs prove scalability and robustness, but not precision/recall.
- Limitation APKs show where the MVP should warn or fail cautiously.

Precision, recall, F1, and version accuracy require ground truth. They should be reported only for controlled APKs and source-validated real APKs.

## Proposed Dataset Layers

| Layer | Target count | Ground truth | Main purpose | Metrics allowed |
|---|---:|---|---|---|
| Controlled APKs | 100 | Exact by construction | Accuracy, R8/obfuscation, multidex, multi-library, vulnerability tests | Precision, recall, F1, version accuracy |
| Source-validated real APKs | 50 | APK linked to source tag plus resolved Gradle dependency tree | Real-world version validation | Precision/recall within reference scope, version correctness, false positives, missing coordinates |
| Smoke-test real APKs | 100-200 | No full dependency ground truth | Scalability and qualitative coverage | Runtime, success rate, parse failures, detected components, vulnerability counts |
| Limitation APKs | 15-20 | Partial/manual | Boundary analysis for packed/native-heavy/nonstandard apps | Limitation behavior, forensic warning quality |

The target is ambitious by design. Build it in milestones:

| Milestone | Controlled | Source-validated real | Smoke real | Limitation |
|---|---:|---:|---:|---:|
| M1 | 25 | 5 | 25 | 5 |
| M2 | 50 | 20 | 75 | 10 |
| M3 | 100 | 50 | 100-200 | 15-20 |

## Classification Criteria

Every APK should be classified using the fields below.

### Identity And Provenance

| Field | Values / format | Why it matters |
|---|---|---|
| Dataset layer | controlled, source-validated-real, smoke-real, limitation | Defines what claims can be made from this APK. |
| App name | text | Human-readable dataset table. |
| APK path | repository path | Reproducibility. |
| Download source | F-Droid, GitHub Releases, IzzyOnDroid, AndroZoo, generated | Legal and reproducible provenance. |
| APK SHA-256 | hash | Ensures the exact binary is identified. |
| Package name | Android package | Links APK identity to source/build metadata. |
| versionName | manifest value | Helps match APK to source release. |
| versionCode | manifest value | Stronger APK/source version check. |
| Release date / era | old, mid, modern, exact date if known | Helps compare old vulnerable libraries vs modern AndroidX/R8 apps. |

### Source Validation Fields

Required for source-validated real APKs:

| Field | Values / format | Why it matters |
|---|---|---|
| Source repository | URL or local path | Proof source exists. |
| Source tag/commit | tag, commit hash, release branch | Prevents comparing APK with wrong source version. |
| APK/source version match | yes, partial, no, unknown | Shows whether versionName/versionCode align. |
| Build system | Gradle Android, Maven, other | Determines whether dependency tree can be reproduced. |
| Dependency tree path | file path | Ground truth for validation. |
| Dependency tree configuration | e.g. `:app:fullReleaseRuntimeClasspath` | Explains which resolved dependency graph was used. |
| Source validation report | file path | Evidence for confirmed/mismatch/missing results. |
| Source validation status | complete, partial, failed, not-applicable | Defines the strength of the result. |

### APK Structure Criteria

| Criterion | Values | Why it matters |
|---|---|---|
| DEX count | number | Tests single DEX vs multidex support. |
| Multidex | true/false | Direct claim: the MVP handles multiple `classes*.dex` files. |
| Nonstandard DEX files | none, assets, res/raw, unusual path | Detects dynamic-code or hidden-code indicators. |
| APK size | bytes/MB | Scalability and complexity proxy. |
| Class count | number | Better complexity measure than APK size. |
| Method count | number | DEX complexity and scalability. |
| Native `.so` count | number | Tests native hash-only reporting boundary. |
| Native ABI list | armeabi-v7a, arm64-v8a, x86, x86_64, etc. | Explains native coverage and architecture. |
| Manifest metadata available | true/false/partial | Needed for app identity and SDK context. |
| Resources available | true/false | Useful for APK completeness and extraction quality. |

### Build And Obfuscation Criteria

| Criterion | Values | Why it matters |
|---|---|---|
| Build type | debug, release, unknown | Release builds are more likely minified/optimized. |
| R8 / ProGuard status | none, ProGuard, R8, unknown | Core research dimension. |
| R8 mode | rename, shrink, optimize, full mode, unknown | Separates light and moderate/hard cases. |
| Obfuscation level | none, light, moderate, heavy, protected/packed, unknown | Explains expected confidence behavior. |
| Minification evidence | source config, APK package patterns, report indicators, unknown | Records why an APK is classified as obfuscated. |
| Resource shrinking | yes, no, unknown | Can affect string/resource evidence. |
| Packer/protector indicators | none, suspected, confirmed | Defines limitation cases. |
| Dynamic loading indicators | none, suspected, confirmed | Static APK analysis limitation. |

Recommended interpretation:

| Level | Meaning | Expected MVP behavior |
|---|---|---|
| none | Clear build, names mostly preserved | Exact/high or likely matches are plausible. |
| light | R8/ProGuard renaming, little shrinking | Detection should survive but may lower confidence. |
| moderate | R8 shrink/optimize removes some library code | Candidate/low confidence is acceptable. |
| heavy | Strong shrinking, inlining, package flattening, or custom protection | MVP should avoid overclaiming exact versions. |
| protected/packed | Encrypted/packed/dynamic code | MVP should report risk indicators, not claim full recovery. |

### Technology And Dependency Profile

| Criterion | Values | Why it matters |
|---|---|---|
| Primary language | Java, Kotlin, mixed, other | Kotlin/Java affects dependency ecosystem. |
| Framework type | Android native, Jetpack Compose, Flutter, React Native, Unity, hybrid | Non-Java/Kotlin frameworks may move code outside normal DEX evidence. |
| AndroidX / Jetpack usage | none, light, heavy | Important modern Android dependency category. |
| Kotlin/KMP artifacts | none, present, heavy | KMP metadata and `*-android` variants are known reference DB issues. |
| Main library families | networking, JSON, image loading, database, DI, logging, crypto, media, maps, ads | Helps stratify results by dependency type. |
| Expected third-party dependency count | number or range | Helps evaluate SBOM completeness. |
| Transitive dependency complexity | low, medium, high | Dependency trees often include many resolved transitive components. |
| Overlapping artifact families | none, Okio/Okio-JVM, AndroidX wrappers, KMP variants, other | Tests disambiguation logic. |
| Known vulnerable dependency expected | yes, no, unknown | Needed for vulnerability evaluation. |

### Validation Level

Use one validation level per APK:

| Level | Name | Meaning | Metrics allowed |
|---|---|---|---|
| L1 | Controlled ground truth | APK generated by us; exact dependencies known. | Full precision/recall/F1/version accuracy. |
| L2 | Source validated | APK linked to source tag/commit and resolved dependency tree. | Precision/recall within reference scope and version correctness. |
| L3 | Source available, not fully validated | Source exists but exact tag/build tree is missing or partial. | Qualitative checks only unless completed. |
| L4 | Smoke only | APK analyzed without ground truth. | Runtime, success/failure, detections, OSV counts. |
| L5 | Limitation case | APK intentionally chosen for hard/unsupported behavior. | Limitation behavior, warnings, failure analysis. |

## Controlled APK Design

The controlled dataset should be generated from known Maven artifacts. A practical design is:

```text
20 Maven coordinates x 5 controlled variants = 100 APKs
```

Suggested variants:

| Variant | Purpose |
|---|---|
| clear-single | Baseline exact matching. |
| r8-rename | Light obfuscation. |
| r8-shrink | Moderate obfuscation and partial library survival. |
| multi-library | Tests false positives and multiple dependency reporting. |
| multidex | Tests extraction and matching across several DEX files. |

Suggested library families:

| Family | Example coordinates |
|---|---|
| JSON | `com.google.code.gson:gson`, `com.fasterxml.jackson.core:jackson-databind`, `com.squareup.moshi:moshi` |
| Networking | `com.squareup.okhttp3:okhttp`, `com.squareup.retrofit2:retrofit`, `io.ktor:ktor-client-okhttp-jvm` |
| Kotlin / serialization | `org.jetbrains.kotlinx:kotlinx-serialization-json-jvm`, `org.jetbrains.kotlinx:kotlinx-coroutines-core-jvm` |
| AndroidX / Jetpack | `androidx.core:core`, `androidx.appcompat:appcompat`, `androidx.work:work-runtime`, `androidx.lifecycle:lifecycle-runtime-android` |
| Images | `com.github.bumptech.glide:glide`, `io.coil-kt:coil` |
| DI / utilities | `com.google.dagger:dagger`, `com.jakewharton.timber:timber`, `commons-codec:commons-codec` |
| Security / crypto | `org.bouncycastle:bcprov-jdk18on`, `com.google.crypto.tink:tink-android` |

Controlled APKs should store `.ground-truth.json` files with:

- expected Maven coordinate
- expected version
- variant
- R8/ProGuard configuration
- whether multidex was enabled
- expected vulnerable advisories when relevant

## Source-Validated Real APK Design

For the 50 source-validated real APK target, prefer:

- F-Droid packages
- GitHub Releases with APK assets and matching source tags
- IzzyOnDroid entries with clear source links

Each APK must have a proof bundle:

| Proof item | Required? |
|---|---|
| APK file and SHA-256 | yes |
| Source repository URL | yes |
| Source tag/commit | yes |
| versionName/versionCode comparison | yes |
| Gradle dependency tree | yes |
| Generated report folder | yes |
| Source validation report | yes |
| Dataset classification row | yes |

The paper should distinguish:

- full source dependency tree size
- number of SBOM components emitted by the MVP
- number of emitted components confirmed by source validation
- version mismatches
- missing coordinates
- extra/suppressed candidates

## Smoke-Test Real APK Design

Smoke APKs are used for scale and robustness, not precision/recall.

Allowed claims:

- report generation success rate
- median/mean runtime
- DEX parse failure rate
- number of APKs with multidex
- number of APKs with native `.so` files
- number of APKs with nonstandard DEX indicators
- number of detected Maven components
- number of OSV vulnerable components
- confidence distribution

Do not claim false positives, false negatives, precision, or recall without ground truth.

## Limitation APK Design

Limitation APKs should be intentionally difficult. Good categories:

| Category | Why include it |
|---|---|
| Flutter | Main app logic may be native/Dart, not normal Java/Kotlin libraries. |
| React Native | JavaScript bundle and native bridge change the dependency profile. |
| Unity | Heavy native/game engine code; Java/Kotlin SBOM recovery is limited. |
| Native-heavy apps | Tests `.so` hash-only reporting boundary. |
| Packed/protected apps | Tests forensic risk indicators and cautious failure. |
| Dynamic-code apps | Tests nonstandard DEX/dynamic loading limitation. |
| Very large apps | Tests runtime and scalability. |

The correct result for a limitation APK may be a warning, partial report, or low-confidence output. That is valuable if documented honestly.

## Paper Reporting Template

Use separate tables for each layer:

| Layer | APKs | Ground truth | Source | Main claim |
|---|---:|---|---|---|
| Controlled | 100 | exact by construction | generated Maven fixtures | accuracy and robustness under known conditions |
| Source-validated real | 50 | source tag plus Gradle dependency tree | F-Droid/GitHub/IzzyOnDroid | real-world version validation |
| Smoke real | 100-200 | none/full not available | F-Droid/IzzyOnDroid/AndroZoo | scalability and report generation |
| Limitation | 15-20 | partial/manual | selected hard APKs | scope and failure-mode analysis |

Then report metrics separately:

| Metric | Dataset layer |
|---|---|
| Precision, recall, F1 | controlled and source-validated only |
| Version accuracy | controlled and source-validated only |
| Obfuscation robustness | controlled R8/ProGuard variants plus real APK labels |
| Multidex handling | controlled multidex plus source-validated/smoke multidex APKs |
| Vulnerability correctness | controlled vulnerable APKs plus source-validated vulnerable apps if available |
| Scalability | all real smoke APKs |
| Limitation behavior | limitation APKs |

## Current Dataset Status

The current dataset is the M0 seed:

| Layer | Current count | Evidence |
|---|---:|---|
| Controlled APKs | 72 | `.ground-truth.json` files under `data/test_apks/`, including clear version-band, R8 rename, R8 shrink, R8 optimize, package flattening/repackaging, inline-like stress, and multi-library multidex fixtures |
| Source-validated real APKs | 12 | Current thesis-facing source-validated set is summarized in `docs/evaluation/APK_TYPE_EVALUATION.md`; clean and partial-version-mismatch cases are reported separately |
| Smoke-test real APKs | 0 | not started |
| Limitation APKs | 3 | Native-heavy and hidden-code boundary cases are summarized in `docs/evaluation/APK_TYPE_EVALUATION.md` |

The current source-validated proof model includes F-Droid, OpenTracks, Tusky, AntennaPod, and KDE Connect:

- APK: `data/test_apks/real/F-Droid.apk`
- Source: `data/source/fdroidclient-1.23.2`
- Dependency tree: `data/results/source-validation/fdroid/app-fullReleaseRuntimeClasspath.txt`
- Validation report: `data/results/source-validation/fdroid-final-demo-osv/source-validation.md`
- Current result: 23/23 emitted Maven SBOM components confirmed, 0 mismatches, 0 missing
- APK: `data/test_apks/real/opentracks/opentracks.apk`
- Source: `data/source/opentracks-v4.27.0irreproducible/source/de.dennisguse.opentracks_6653_src.tar.gz`
- Dependency tree: `data/results/source-validation/opentracks/fullReleaseRuntimeClasspath.txt`
- Validation report: `data/results/source-validation/opentracks-calibrated-db/source-validation.md`
- Current result: 19/19 emitted Maven SBOM components confirmed, 0 mismatches, 0 missing
- APK: `data/test_apks/real/tusky/tusky.apk`
- Source: `data/source/tusky-32.2/source/com.keylesspalace.tusky_142_src.tar.gz`
- Dependency tree: `data/results/source-validation/tusky/blueReleaseRuntimeClasspath.txt`
- Validation report: `data/results/source-validation/tusky-calibrated-db/source-validation.md`
- Current result: 1/1 emitted Maven SBOM component confirmed, 0 mismatches, 0 missing; this is clean but sparse and should not be presented as broad dependency recall
- APK: `data/test_apks/real/antennapod/antennapod.apk`
- Source: `data/source/antennapod/github-source.tar.gz` for F-Droid commit `6c3492af7239b46e8c9933ff04984fcdd07c3a6f`
- Dependency tree: `data/results/source-validation/antennapod/freeReleaseRuntimeClasspath.txt`
- Validation report: `data/results/source-validation/antennapod-report-validation/source-validation.md`
- Current result: 19/20 emitted SBOM component versions confirmed, 1 mismatch, 0 missing; this is source-validated but should be presented as a partial-version-mismatch case
- APK: `data/test_apks/real/kde-connect/kde-connect.apk`
- Source: `data/source/kde-connect/source.tar.gz` for F-Droid commit `0f3cc84446065102c064f78d4276bb4ebd00d3c9`
- Dependency tree: `data/results/source-validation/kde-connect/releaseRuntimeClasspath.txt`
- Validation report: `data/results/source-validation/kde-connect-validation/source-validation.md`
- Current result: 8/9 emitted SBOM component versions confirmed, 1 mismatch, 0 missing; this is source-validated but should be presented as a partial-version-mismatch case

The first real-APK candidate backlog is tracked in:

- `docs/evaluation/REAL_APK_CANDIDATES.md`
- `configs/real_apk_candidates.json`
- `data/results/evaluation/real-apk-candidates.json`
- `docs/evaluation/REAL_APK_PROOF_BUNDLE_PLAN.md`
- `data/results/evaluation/real-apk-proof/`

Regenerate the candidate table with:

```powershell
python scripts/build_real_apk_candidate_matrix.py
```

The dataset criteria coverage matrix is generated at:

- `docs/evaluation/DATASET_COVERAGE_MATRIX.md`
- `data/results/evaluation/dataset-coverage-matrix.json`

Regenerate it with:

```powershell
python scripts/build_dataset_coverage_matrix.py
```

Current matrix summary:

| Status | Count | Meaning |
|---|---:|---|
| Covered criteria | 19 | Current controlled/source-validated/limitation evidence is enough for the current MVP criteria. |
| Missing criteria | 0 | The controlled multidex and controlled multi-library gaps are closed by one exact-ground-truth fixture. |
| Candidate-only criteria | 0 | NewPipe remains a candidate for further calibration, but no criterion is currently missing only because of it. |

Regenerate the first-batch proof checklists with:

```powershell
python scripts/scaffold_real_apk_proof.py
```

The proof scaffold creates one checklist per first-batch candidate. It is only an admission workflow; the APK is still not counted as source-validated until the checklist is completed with the APK hash, source tag/commit, dependency tree, MVP report, and source-validation output.

Current first-batch progress:

| Candidate | Status | Notes |
|---|---|---|
| OpenTracks | complete | APK/source/report/dependency-tree collected; source validation confirms 19/19 emitted components, 0 mismatches, 0 missing, OSV 0 vulnerabilities. |
| NewPipe | partial-version-mismatch | APK/source/report/dependency-tree collected; calibration plus matcher-level version disambiguation improved source validation to 10/11 emitted components confirmed with 1 version mismatch, so it is still not yet a fully clean source-validated case. |
| Tusky | complete | APK/source/report/dependency-tree collected; after Retrofit 3.0.0 calibration, source validation confirms 1/1 emitted component, 0 mismatches, 0 missing, OSV 0 vulnerabilities. |
| K-9 / Thunderbird Android | source-validated-partial | APK/source/report/version-catalog evidence collected; report emits 11 Maven components and 8 native file components with OSV 0; a validation-only plugin-lite/runtime-graph source copy generated `fossReleaseRuntimeClasspath`, and source validation confirms 5/11 emitted Maven versions with 6 mismatches and 0 missing. |
| AntennaPod | partial-version-mismatch | APK/source/report/dependency-tree collected; after adding source-used AndroidX Core and WorkManager versions to calibration, source validation confirms 19/20 emitted components, with one AndroidX Core near-tie mismatch and 0 missing. |
| KDE Connect | partial-version-mismatch | APK/source/report/dependency-tree collected; source validation confirms 8/9 emitted components, with one remaining ViewPager2 beta-version mismatch and 0 missing. |
| Organic Maps | limitation-complete | Native-heavy limitation proof collected; use for native hash-only boundary evidence, not version-accuracy metrics. |

## Next Dataset Tasks

1. Keep NewPipe as a documented partial-version-mismatch limitation case unless Maven POM/dependency metadata coherence is added to resolve the remaining `androidx.startup:startup-runtime` bytecode-equivalent mismatch.
2. Add one limitation APK/fixture with heavy obfuscation, protector, or dynamic-loading indicators.
3. Add one native-heavy boundary APK such as Organic Maps, VLC, or OsmAnd.
4. Scale controlled fixtures from 30 toward 100 only after adding new categories, not just duplicate easy cases.
5. Add the next clean non-sparse source-validated real APK; K-9 can count only after the resolved Gradle tree is generated and source validation is run.
6. Continue scaling toward 50 source-validated real APKs while preserving the clean/partial/blocked/limitation split.
