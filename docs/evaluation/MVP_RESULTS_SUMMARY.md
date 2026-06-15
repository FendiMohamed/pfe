# MVP Results Summary

Date: 2026-05-21.

This page is a thesis-facing summary of the current APK-to-SBOM MVP results.

## MVP Claim

The MVP demonstrates that a static, reference-database-based APK analysis pipeline can recover useful Maven SBOM components from compiled Android APKs when the relevant library/version exists in the reference DB.

The strongest result is not that the tool identifies every dependency. The strongest result is that source-validated calibration turns bytecode evidence into accurate SBOM components, while broad latest-only coverage improves identity discovery but produces version mismatches.

For the broader evaluation, use `docs/evaluation/APK_TYPE_EVALUATION.md`: it reports results by APK family and validation level, separating clean source-validated cases from partial, blocked, native-heavy, and hidden-code limitation cases.

For thesis-ready result tables, use `docs/evaluation/THESIS_EVALUATION_TABLES.md`: it summarizes 84/84 controlled expected versions across 72 fixtures, 47/47 clean real emitted Maven versions, 880/1790 partial real emitted Maven versions, and 927/1837 overall source-validated emitted Maven versions. The metric is an emitted-version confirmation rate, not full dependency recall. For prose that can be integrated into the thesis, use `docs/evaluation/THESIS_EVALUATION_CHAPTER_DRAFT.md`.

## Implemented Pipeline

```text
APK
-> extract DEX, manifest, resources, strings, native files
-> parse all classes*.dex files
-> compare package/class/method/opcode/CDG/string evidence to Maven reference DB
-> select library/version candidates with confidence
-> emit CycloneDX SBOM
-> query OSV when enabled
-> generate Markdown/HTML/JSON report
```

Native `.so` files are reported as hash-only CycloneDX file components. The MVP does not claim native package/version identification.

## Controlled Evaluation

Controlled fixtures now cover 72 APKs and 84 expected Maven components across Gson, Jackson Databind, OkHttp, Okio-JVM, Retrofit, Commons Codec, and Ktor JVM modules. The generated batch includes clear version-band fixtures, networking/Kotlin-era version-band fixtures, Ktor framework fixtures, R8 rename/shrink/optimize/shrink+optimize/package-flattening/inline-stress fixtures, and multi-library multidex fixtures.

| Metric | Result |
|---|---:|
| Component precision | 1.000 |
| Component recall | 1.000 |
| Version precision | 1.000 |
| Version recall | 1.000 |
| Candidate version recall | 1.000 |

Important interpretation:

- Clear fixtures are detected as exact/high confidence.
- R8 rename and shrink fixtures are detected as low-confidence candidates, not overclaimed exact matches.
- Hybrid evidence outperforms simple package/class/hash baselines on the controlled set.

Primary artifact:

```text
docs/evaluation/CONTROLLED_EVALUATION.md
data/results/evaluation/generated-apk-category-batch.md
```

## F-Droid Case Study

Real APK:

```text
data/test_apks/real/F-Droid.apk
```

The current calibrated DB emitted 23 Maven SBOM components. Source dependency-tree validation confirmed 23/23 component versions with 0 mismatches and 0 missing coordinates.

| DB / Run | SBOM components | Confirmed | Version mismatch | Missing |
|---|---:|---:|---:|---:|
| Focused DB | 4 | 4 | 0 | 0 |
| Earlier latest-only expanded DB | 18 | 7 | 11 | 0 |
| First calibrated DB | 18 | 15 | 3 | 0 |
| Final single-app calibrated DB | 19 | 19 | 0 | 0 |
| Current two-app calibrated DB | 23 | 23 | 0 | 0 |
| Full latest-only expanded DB | 26 | 12 | 13 | 1 |

Primary artifacts:

```text
data/results/report-real-f-droid-calibrated-db/
data/results/source-validation/fdroid-calibrated/
data/results/report-real-f-droid-final-demo/
data/results/source-validation/fdroid-final-demo/
data/results/report-real-f-droid-final-demo-osv/
data/results/source-validation/fdroid-final-demo-osv/
data/results/report-real-f-droid-full-expanded-db/
data/results/source-validation/fdroid-full-expanded/
```

Final supervisor/demo run:

| Field | Result |
|---|---:|
| OSV-enabled report folder | `data/results/report-real-f-droid-final-demo-osv/` |
| OSV-enabled source validation folder | `data/results/source-validation/fdroid-final-demo-osv/` |
| Offline fallback report folder | `data/results/report-real-f-droid-final-demo/` |
| Paired clean OSV demo folder | `data/results/report-real-f-droid-final-demo-osv/` |
| Paired vulnerable OSV demo folder | `data/results/demo-osv-vulnerable-jackson-databind/` |
| APK testset inventory | `docs/evaluation/APK_TESTSET_INVENTORY.md` |
| APK package | `org.fdroid.fdroid` |
| APK version | `1.23.2` |
| APK versionCode | `1023052` |
| DEX files | 2 |
| Native files | 4 |
| Extraction risk | low |
| Obfuscation risk | low |
| SBOM Maven components | 23 |
| Source-confirmed SBOM versions | 23 |
| Version mismatches | 0 |
| Missing coordinates | 0 |
| OSV vulnerable components | 0 |
| OSV vulnerabilities | 0 |

For a positive OSV demonstration, the controlled `jackson-databind@2.9.10.8` APK at `data/results/demo-osv-vulnerable-jackson-databind/` detects 1 Maven component and OSV returns 3 confirmed HIGH advisories: `CVE-2020-36518`, `CVE-2022-42003`, and `CVE-2022-42004`.

## OpenTracks Case Study

OpenTracks is the second completed source-validated real APK.

| Field | Result |
|---|---:|
| APK | `data/test_apks/real/opentracks/opentracks.apk` |
| Package | `de.dennisguse.opentracks` |
| APK version | `v4.27.0irreproducible` |
| APK versionCode | `6653` |
| Source commit | `f143aabfbf77d1b71864042fe4f0bbf2b4174f4f` |
| DEX files | 4 |
| Native files | 0 |
| R8/minify source evidence | disabled |
| Source dependency tree | `data/results/source-validation/opentracks/fullReleaseRuntimeClasspath.txt` |
| Report folder | `data/results/report-real-opentracks-calibrated-db/` |
| Source validation folder | `data/results/source-validation/opentracks-calibrated-db/` |
| SBOM Maven components | 19 |
| Source-confirmed SBOM versions | 19 |
| Version mismatches | 0 |
| Missing coordinates | 0 |
| OSV vulnerabilities | 0 |

This case added a useful artifact-family lesson: modern AndroidX Lifecycle publishes public coordinates and Android target variants whose bytecode can overlap. The matcher now uses artifact-family disambiguation plus Lifecycle version-coherence evidence, so the same calibrated DB validates cleanly for both F-Droid and OpenTracks.

## Tusky Case Study

Tusky is the third completed source-validated real APK, but it should be described as a clean sparse case rather than a broad recall result.

| Field | Result |
|---|---:|
| APK | `data/test_apks/real/tusky/tusky.apk` |
| Package | `com.keylesspalace.tusky` |
| APK version | `32.2` |
| APK versionCode | `142` |
| Source commit | `ff0c9f58874fafc72a53789f079ce0dc1a7e9207` |
| DEX files | 1 |
| Native files | 16 |
| R8/minify source evidence | enabled |
| Source dependency tree | `data/results/source-validation/tusky/blueReleaseRuntimeClasspath.txt` |
| Report folder | `data/results/report-real-tusky-calibrated-db/` |
| Source validation folder | `data/results/source-validation/tusky-calibrated-db/` |
| SBOM Maven components | 1 |
| Source-confirmed SBOM versions | 1 |
| Version mismatches | 0 |
| Missing coordinates | 0 |
| OSV vulnerabilities | 0 |

This case demonstrates the calibration workflow clearly: before adding `com.squareup.retrofit2:retrofit@3.0.0`, the MVP selected `retrofit@2.9.0`; after adding the source-used reference and rebuilding the calibrated DB, the emitted component validates as `retrofit@3.0.0`.

## Conversations Case Study

Conversations is a completed source-validated partial-version-mismatch case. It adds a useful messaging/security APK with multidex, R8/minify, native libraries, and a larger source dependency tree.

| Field | Result |
|---|---:|
| APK | `data/test_apks/real/conversations/conversations.apk` |
| Package | `eu.siacs.conversations` |
| APK version | `2.20.0+free` |
| APK versionCode | `4217704` |
| Source commit | `7346a14dcedb155762133ea3ec512fdf34b57876` |
| DEX files | 2 |
| Native files | 2 |
| R8/minify source evidence | enabled |
| Source dependency tree | `data/results/source-validation/conversations/conversationsFreeReleaseRuntimeClasspath.txt` |
| Report folder | `data/results/report-real-conversations/` |
| Source validation folder | `data/results/source-validation/conversations-report-validation/` |
| SBOM Maven components | 9 |
| Source-confirmed SBOM versions | 6 |
| Version mismatches | 2 |
| Missing/artifact-family nuance | 1 |
| OSV vulnerabilities | 0 |

Adding source-used `com.google.code.gson:gson@2.13.1` to the calibration DB improved source validation from 5/9 to 6/9 confirmed. The remaining mismatches are close-score AndroidX version ambiguities (`concurrent-futures` and `startup-runtime`), and the remaining missing item is a Lifecycle public-vs-Android artifact-family nuance.

## Expanded Reference DB

The expanded catalog contains 147 curated coordinates and 163 artifact-version entries. The completed expanded build checked all entries.

| Field | Result |
|---|---:|
| Unique expanded artifact records | 141 |
| Usable expanded DEX components | 108 |
| No-bytecode / metadata-only skips | 33 |
| Failed artifacts after fixes | 0 |
| Expanded DB classes | 39,326 |
| Expanded DB methods | 279,212 |
| Combined DB components | 133 |
| Combined DB methods | 346,404 |

Catalog fixes made during batch construction:

| Coordinate | Fix |
|---|---|
| `com.google.crypto.tink:tink-android` | AAR -> JAR |
| `com.google.dagger:dagger-android` | JAR -> AAR |
| `org.greenrobot:eventbus` | JAR -> AAR |

## Thesis Interpretation

Use the calibrated F-Droid and OpenTracks results as the main broad real-world validation results. Use Tusky as an additional clean but sparse source-validated case that demonstrates how source validation catches and calibration fixes a version mismatch.

Use the full expanded DB result as a stress-test result:

- It shows that broader reference coverage discovers more real dependency identities.
- It also shows that latest-only references produce version mismatches on real APKs.
- Therefore the thesis can argue that APK-to-SBOM recovery requires both feature matching and version coverage/calibration.

## Confidence Reporting Improvement

The MVP now separates library identity confidence from selected-version confidence.

Example interpretation:

```text
component identity: likely/medium
selected version: candidate/low
```

This matters because the full expanded DB showed that a coordinate can be correctly discovered while the selected latest-only version is wrong for the real APK. The report and SBOM therefore preserve the original overall confidence while also exposing:

- `apk-sbom:mvp:identity-confidence`
- `apk-sbom:mvp:identity-confidence-label`
- `apk-sbom:mvp:identity-status`
- `apk-sbom:mvp:version-confidence`
- `apk-sbom:mvp:version-confidence-label`
- `apk-sbom:mvp:version-status`

Fresh demonstration artifact:

```text
data/results/report-real-f-droid-confidence-split/
```

## Vulnerability Reporting Improvement

OSV lookup is now confidence-aware in the MVP report layer.

The tool still queries OSV by Maven coordinate and selected version, but the returned advisory is labeled according to APK-side evidence:

- `confirmed`: component identity is strong and the selected version is exact/high confidence.
- `potential`: OSV returned an advisory for the selected package/version, but the APK-side version is low-confidence, candidate, or otherwise not exact/high.

This prevents the report from turning a low-confidence version guess into a hard CVE claim. It matches the F-Droid lesson: vulnerability reporting depends on version accuracy, so low-confidence version matches must stay visibly tentative until source/dependency-tree validation confirms them.

The vulnerability layer also parses OSV severity when advisory details expose it and deduplicates advisories that share OSV, GHSA, or CVE identities.

## Extraction And Explainability Improvement

The report now includes APK forensic context before the matching result:

- standard vs nonstandard DEX files
- manifest package/version/SDK/permission hints when the manifest can be decoded
- native ABI summary
- extraction-risk indicators such as nonstandard DEX paths, tiny primary DEX, large opaque assets, or packer/protector-like file names
- candidate reason summaries such as package, class, method, opcode, graph, literals, version-unique, or artifact-family evidence
- an obfuscation-risk warning based on extraction indicators, DEX parse failures, low-confidence component ratio, and structural evidence outweighing package-name evidence

These fields are warnings and explanations, not hard filters. They improve thesis/demo transparency while keeping the approved MVP architecture unchanged.

## Implemented Optimization Summary

| Optimization | Status | Where visible |
|---|---|---|
| APK extraction forensic summary | implemented | `report.json`, `report.md`, `report.html`, CycloneDX application properties |
| Manifest metadata + app package hint | implemented | APK section in reports and CycloneDX application properties |
| Candidate reason field | implemented | Detected components table in Markdown/HTML reports |
| Obfuscation risk field | implemented | APK summary, forensic section, and `report.json` |
| OSV severity/dedup | implemented | OSV JSON and vulnerability tables when OSV lookup is enabled |

## Latest Verification

| Command | Result |
|---|---|
| `python -m compileall src scripts tests` | passed |
| `docker compose run --rm apk-sbom pytest -q` | `212 passed` |
| `docker compose run --rm apk-sbom python -m compileall src scripts tests` | passed |
| `git diff --check` | passed with normal Windows LF/CRLF warnings |

## Current Limitations

- Heavy R8 optimization, packing, dynamic loading, and commercial protectors remain out of scope.
- Native libraries are hash-only evidence.
- Broad latest-only reference versions are not reliable for exact version claims.
- Optional CycloneDX CLI, Trivy, and Grype validation/scanning remain blocked until those tools are installed.
