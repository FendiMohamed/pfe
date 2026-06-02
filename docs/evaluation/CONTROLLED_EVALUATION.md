# Controlled Evaluation

This note records the controlled evaluation of the APK-to-SBOM MVP.

## Fixtures

The current fixture builder creates APK-like ZIP files with real DEX code generated from known Maven artifacts. The controlled set now includes the original baseline fixtures plus a generated category batch for clear version-band, R8 rename, R8 shrink, and multi-library multidex cases.

Ground truth:

| Variant | Ground truth | Fixture mode |
|---|---|---|
| `clear` | `com.fasterxml.jackson.core:jackson-databind@2.9.10.8` | library-only D8 fixture |
| `clear` | `com.google.code.gson:gson@2.8.9` | library-only D8 fixture |
| `r8-rename` | `com.google.code.gson:gson@2.8.9` | library-only R8 rename fixture |
| `r8-shrink` | `com.google.code.gson:gson@2.8.9` | library-only R8 shrink fixture |
| `clear` | `com.squareup.okhttp3:okhttp@4.9.1` | library-only D8 fixture |
| `clear` | `com.squareup.retrofit2:retrofit@2.9.0` | library-only D8 fixture |
| `clear` | `commons-codec:commons-codec@1.16.1` | library-only D8 fixture |
| `r8-rename` | `commons-codec:commons-codec@1.16.1` | library-only R8 rename fixture |
| `r8-shrink` | `commons-codec:commons-codec@1.16.1` | library-only R8 shrink fixture |
| `clear` | `com.google.code.gson:gson@2.8.9` + `commons-codec:commons-codec@1.16.1` | controlled multi-library multidex D8 fixture |
| `clear-version-band` | Gson, Jackson Databind, OkHttp, Retrofit, and Commons Codec version variants | generated category batch |
| `r8-rename` | Jackson Databind, OkHttp, and Retrofit variants | generated category batch |
| `r8-shrink` | Jackson Databind, OkHttp, and Retrofit variants | generated category batch |
| `multi-library-multidex` | Gson+Commons Codec, Jackson+Gson, OkHttp+Okio-JVM, Retrofit+OkHttp | generated category batch |

The complete generated batch result is stored in:

```text
data/results/evaluation/generated-apk-category-batch.md
```

Generated files are ignored by Git and live under:

```text
data/test_apks/
data/results/
```

## Current Hybrid MVP Result

Source:

```text
data/results/evaluation/controlled-evaluation.md
```

Representative baseline rows:

| Variant | Ground truth | Detected component | Detected version | Candidate version | Decision |
|---|---|---:|---:|---:|---|
| `clear` | `com.fasterxml.jackson.core:jackson-databind@2.9.10.8` | true | true | true | exact/high |
| `clear` | `com.google.code.gson:gson@2.8.9` | true | true | true | exact/high |
| `r8-rename` | `com.google.code.gson:gson@2.8.9` | true | true | true | candidate/low |
| `r8-shrink` | `com.google.code.gson:gson@2.8.9` | true | true | true | candidate/low |
| `clear` | `com.squareup.okhttp3:okhttp@4.9.1` | true | true | true | exact/high |
| `clear` | `com.squareup.retrofit2:retrofit@2.9.0` | true | true | true | exact/high |
| `clear` | `commons-codec:commons-codec@1.16.1` | true | true | true | exact/high |
| `r8-rename` | `commons-codec:commons-codec@1.16.1` | true | true | true | candidate/low |
| `r8-shrink` | `commons-codec:commons-codec@1.16.1` | true | true | true | candidate/low |
| `clear` | `com.google.code.gson:gson@2.8.9` in multi-library multidex fixture | true | true | true | exact/high |
| `clear` | `commons-codec:commons-codec@1.16.1` in multi-library multidex fixture | true | true | true | likely/medium |

Metrics:

The current controlled dataset has 30 APK fixtures and 35 expected Maven components.

| Metric | Value |
|---|---:|
| Component precision | 1.000 |
| Component recall | 1.000 |
| Version precision | 1.000 |
| Version recall | 1.000 |
| Candidate version recall | 1.000 |

Interpretation:

- The clear APK path works end to end across six Maven coordinates and multiple version bands: exact version, CycloneDX component, and report output.
- R8 rename and R8 shrink are included in the SBOM as low-confidence `candidate` detections across Gson, Commons Codec, Jackson Databind, OkHttp, and Retrofit, not overclaimed exact detections.
- The controlled multi-library multidex fixtures exercise 315 to 896 standard `classes*.dex` files per fixture, report 0 DEX parse failures, and detect all expected components.
- The promotion from uncertain to candidate is driven by strong string-literal/opcode evidence and version-unique literal evidence; this keeps the claim cautious while preserving useful SBOM output.

## Baseline Comparison

Source:

```text
data/results/evaluation/baseline-evaluation.md
```

| Baseline | Component precision | Component recall | Version precision | Version recall |
|---|---:|---:|---:|---:|
| Package overlap | 0.900 | 0.818 | 0.700 | 0.636 |
| Class overlap | 0.857 | 0.545 | 0.857 | 0.545 |
| DEX hash | 1.000 | 0.455 | 1.000 | 0.455 |

Interpretation:

- Exact DEX hash is useful only for clear fixtures.
- Class overlap is also mostly clear-fixture only in this R8 setup.
- Package overlap has strong component recall, but it misidentifies the Commons Codec R8 version as `1.15`, reducing version precision.
- The current hybrid matcher is more useful than package-only matching on this controlled set because it keeps version-level correctness for the Commons Codec R8 cases and still catches R8 shrink where simple class/hash evidence disappears. It remains cautious by labeling the R8 detections as low-confidence candidates.

## Real Vulnerability Demo

The controlled Jackson Databind fixture demonstrates the full security path:

```text
APK
-> exact/high detection of com.fasterxml.jackson.core:jackson-databind@2.9.10.8
-> CycloneDX SBOM generation
-> live OSV lookup
-> CVE aliases in the Markdown report
```

Generated report:

```text
data/results/report-jackson-databind-2.9.10.8-clear/report.md
```

OSV findings:

| Advisory | CVE alias | Summary |
|---|---|---|
| `GHSA-57j2-w4cx-62h2` | `CVE-2020-36518` | Deeply nested json in jackson-databind |
| `GHSA-jjjh-jjxp-wpff` | `CVE-2022-42003` | Uncontrolled Resource Consumption in Jackson-databind |
| `GHSA-rgv9-q543-rqg4` | `CVE-2022-42004` | Uncontrolled Resource Consumption in FasterXML jackson-databind |

## Class Dependency Graph And Literal Slice

The reference DB now stores class dependency edges, structural shape features, and string literals:

| Feature | Rows |
|---|---:|
| Class dependency edges | 21,757 |
| Dependency shape rows | 266 |
| String literal rows | 13,402 |

The current CDG score combines exact dependency-edge coverage with a lower-confidence structural shape similarity. The literal slice then adds generic string-literal overlap plus version-unique literal evidence. Together, these signals let the R8 fixtures keep the correct Gson `2.8.9` as a low-confidence SBOM candidate even when class and method names are no longer reliable.

## Limitations

- These are small synthetic fixtures, not real apps.
- The current expanded set covers six Maven coordinates and five R8-tested libraries; it is broader than the first demo, but still not a large benchmark.
- The current fixtures are library-only because the Docker image has Java runtime tools but not `javac`.
- The R8 rename fixture is not equivalent to all real-world R8 configurations.
- The R8 shrink fixture remains a hard case: the correct version is recovered only as low-confidence candidate evidence, not as an exact version.
- Current scores are not calibrated on a large dataset.

## Next Improvements Suggested By This Evaluation

1. Evaluate real APKs from F-Droid or another legal sample source.
2. Expand the reference DB to 30-50 popular libraries and more versions per library.
3. Add R8 variants for OkHttp, Retrofit, and Jackson if build/runtime complexity stays manageable.
4. Report exact, likely, candidate, and uncertain outcomes separately in the final paper.
5. Calibrate thresholds on a larger dataset before making stronger R8 claims.
