# Toolchain

## Tool Choices

| Tool | Role | Why chosen | Main limitation |
|---|---|---|---|
| Python | Main implementation language. | Fast prototyping, good libraries, easy JSON/API/SQLite integration. | Slower than lower-level languages for huge analysis. |
| Python `zipfile` | Raw APK extraction. | APK is a ZIP archive. Simple and reliable for extracting DEX/native files. | Does not decode binary XML/resources. |
| Apktool | Manifest/resources decoding. | Decodes binary XML and resources. | Can be slower and may fail on protected APKs. |
| Androguard | APK/DEX parsing. | Python Android analysis library for classes, methods, opcodes, references. | May be slow or imperfect on unusual APKs. |
| JADX | Manual inspection. | Helps verify decompiled code during debugging. | Not the automated core. |
| Maven Central | Reference library source. | Main ecosystem for Java/Kotlin/Android libraries. | Only covers libraries we download. |
| Android D8 | Convert JAR/AAR to DEX. | Official Android dexer; makes references comparable to APK DEX. | Requires Android build tools setup. |
| SQLite | Local feature DB. | Reproducible, simple, no server needed. | Not ideal for very large-scale indexing. |
| NetworkX | Class dependency graphs. | Easy graph construction and experiments in Python. | Not optimized for massive graphs. |
| scikit-learn | Optional similarity utilities. | Useful for cosine similarity or nearest-neighbor experiments. | Heavy ML is not required for first MVP. |
| CycloneDX JSON | SBOM output. | Standard, scanner-compatible, supports PURL and metadata. | We must generate reliable component evidence. |
| cyclonedx-cli | SBOM validation. | Validates generated BOMs. | Extra dependency. |
| OSV API | Primary vulnerability lookup. | Package/version-oriented, good for Maven/PURL. | Coverage may differ from NVD/GitHub/Sonatype. |
| NVD API | Optional CVE enrichment. | Official CVE/CVSS data source. | Maven-to-CPE mapping is hard. |
| Trivy | Optional SBOM scanner. | Common scanner that can scan SBOMs. | Depends on correct SBOM identity/version. |
| Grype | Optional SBOM scanner. | Good second scanner for comparison. | Depends on correct SBOM identity/version. |
| R8 / ProGuard | Obfuscation evaluation. | Realistic Android obfuscation/shrinking tools. | Heavy R8 remains hard to handle perfectly. |
| Obfuscapk | Optional obfuscation tests. | Black-box APK obfuscation. | Extra setup; not essential for first evaluation. |

## Install/Check Commands To Use Later

These commands are examples; verify paths on the actual machine before using.

```powershell
python --version
java -version
apktool --version
jadx --version
trivy --version
grype version
cyclonedx --version
```

For Python dependencies, the first likely set is:

```text
androguard
networkx
requests
packaging
pydantic
rich
pytest
```

Optional later:

```text
scikit-learn
rapidfuzz
cyclonedx-python-lib
```

## Reuse vs Build

Reuse:

- APK archive extraction
- DEX parsing
- graph utilities
- SBOM validation
- vulnerability APIs
- external scanners

Build ourselves:

- feature schema
- candidate generation
- segmentation strategy
- matching and version scoring
- confidence and evidence reporting
- final APK-to-SBOM workflow

## Current Toolchain Audit

Audit date: 2026-05-18.

No tools were installed during this audit.

### Host Tools

| Tool | Status | Details |
|---|---|---|
| Python | Available | `Python 3.12.0` at `C:\Python312\python.exe`. |
| pip | Available | `pip 23.2.1`. |
| Git | Available | Git 2.42.0.windows.2. Repository initialized on branch `main`; workspace added as a safe directory because of Windows owner SID mismatch. |
| Java | Available | Java 17.0.12 LTS at `C:\Program Files\Java\jdk-17\bin\java.exe`. |
| Docker CLI | Available | Docker CLI 27.5.1. |
| Docker Compose | Available | Docker Compose v2.32.4-desktop.1. |
| Docker daemon | Not reachable | `docker info` cannot connect to Docker engine; likely Docker Desktop is not running or access/elevation is needed. |
| Android SDK / D8 | Missing from PATH | `d8` not found; common Android SDK build-tools folders were not found in the checked locations. |
| Apktool | Missing from PATH | Needed later for decoded manifest/resources. |
| JADX | Missing from PATH | Useful later for manual inspection, not required for first extraction module. |
| Trivy | Missing from PATH | Optional later SBOM scanner. |
| Grype | Missing from PATH | Optional later SBOM scanner. |
| cyclonedx-cli | Available in Docker; missing on host PATH | Used for reproducible SBOM validation in Docker. |

### Python Packages On Host Python

| Package | Status |
|---|---|
| androguard | Missing |
| networkx | Missing |
| requests | Missing |
| packaging | Missing |
| pydantic | Missing |
| rich | Missing |
| pytest | Missing |
| scikit-learn | Missing |
| rapidfuzz | Missing |
| cyclonedx-python-lib / `cyclonedx` module | Missing |

### Audit Conclusion

The Windows host has enough base tooling to start the Docker-based route. Docker Desktop/daemon access required elevated execution from this environment, but the container build now works. The first Docker environment installs the Python packages and CLI dependencies instead of polluting the Windows host.

Immediate next setup tasks:

1. Keep Apktool, D8, Trivy/Grype, and cyclonedx-cli optional at first if they slow down the initial extractor milestone.
2. Use Docker for Androguard-based DEX extraction.
3. Add D8 later when implementing the Maven reference DB converter.

## Docker Runtime Setup

Created files:

- `Dockerfile`
- `docker-compose.yml`
- `requirements.txt`
- `.dockerignore`
- `scripts/check_toolchain.py`

Host-verified commands:

```powershell
docker compose config
$env:PYTHONPATH='src'; python -m apk_sbom.cli --help
python scripts/check_toolchain.py
python -m compileall src scripts tests
```

The Compose file is syntactically valid, but Docker emits warnings because `C:\Users\PC CABA DZ\.docker\config.json` is not accessible. The Docker daemon was also not reachable during `docker info`.

Docker runtime was built successfully with:

```powershell
docker compose build --progress=plain
docker compose run --rm apk-sbom python scripts/check_toolchain.py
```

Container toolchain status:

| Tool/package | Container status |
|---|---|
| Python | Available, 3.12.13 |
| Java runtime | Available, OpenJDK 21 |
| Java compiler (`javac`) | Available, OpenJDK `javac 21.0.11` after rebuilding Docker with `default-jdk-headless`. |
| Android command-line tools | Available in Docker image, installed under `/opt/android-sdk/cmdline-tools/latest`. |
| D8 | Available in Docker image through Android build-tools 36.0.0. |
| Gradle | Available in Docker image, Gradle 9.5.0 under `/opt/gradle`. |
| androguard | Available |
| networkx | Available |
| requests | Available |
| packaging | Available |
| pydantic | Available |
| rich | Available |
| pytest | Available |
| Apktool | Missing, optional for now |
| JADX | Missing, optional/manual host tool later |
| Trivy/Grype | Available in Docker for optional SBOM scanner comparison. |
| Syft/cdxgen | Available in Docker for optional SBOM generation/comparison tooling. |
| cyclonedx-cli | Available in Docker through the standalone CycloneDX CLI binary and `cyclonedx-cli` alias. |

Container tests:

```powershell
docker compose run --rm apk-sbom pytest -q
```

Result after Wikipedia calibration and OkHttp artifact-family disambiguation were added: Docker `pytest -q` reports `73 passed`; Docker `python -m compileall src scripts tests` passed.

Source-validation note after the NewPipe/Tusky batch: Gradle projects with `buildSrc` need a JDK compiler, not only a Java runtime. The Docker image was rebuilt successfully with `default-jdk-headless`, and NewPipe dependency-tree generation now runs.

```text
javac 21.0.11
```

Confirm with:

```powershell
docker compose run --rm apk-sbom sh -c "javac -version"
```

## First CLI Slice

Implemented command:

```powershell
$env:PYTHONPATH='src'
python -m apk_sbom.cli inspect-apk path\to\sample.apk
```

Current output includes:

- APK path, size, and SHA-256
- list of all `classes*.dex`
- `has_multidex`
- manifest presence
- `resources.arsc` presence
- native libraries under `lib/<abi>/*.so` with ABI, filename, size, and SHA-256
- best-effort manifest metadata: package name, versionCode, versionName, minSdk, targetSdk, and permissions when the manifest can be decoded
- forensic summary with standard vs nonstandard DEX files, native ABI summary, extraction-risk level, and packer/protector-style indicators

The archive inspection command uses Python's standard library for ZIP/native/hash handling. Manifest decoding is best effort: text XML is parsed directly, and binary Android XML uses Androguard when available.

## Minimal DEX Feature Slice

Implemented command:

```powershell
$env:PYTHONPATH='src'
python -m apk_sbom.cli analyze-dex path\to\sample.apk
```

Current output includes:

- number of DEX files analyzed
- number of DEX files that failed parsing
- total class count
- total method count
- recovered package names
- aggregate opcode histogram
- per-DEX feature summaries
- parse errors for invalid or unsupported DEX files

This slice uses Androguard inside the Docker runtime. The command records DEX parse failures explicitly instead of silently dropping them.

## Minimal CycloneDX SBOM Slice

Implemented command:

```powershell
$env:PYTHONPATH='src'
python -m apk_sbom.cli generate-mock-sbom path\to\sample.apk --output data\results\mock-sbom.cdx.json
```

Current output:

- CycloneDX JSON, spec version 1.5
- APK metadata component with SHA-256 and extraction properties
- one mocked Maven library component
- Maven PURL
- confidence, match type, and evidence stored as CycloneDX properties
- dependency edge from the APK component to the detected library

The mock component is temporary. It validates the SBOM output contract before the real matcher is connected.

## Reference Catalog Expansion Slice

Implemented command:

```powershell
$env:PYTHONPATH='src'
python -m apk_sbom.cli expand-reference-config --catalog configs\popular_android_maven_catalog.json --output configs\libraries.expanded.json --latest-count 1
```

Docker equivalent:

```powershell
docker compose run --rm apk-sbom python -m apk_sbom.cli expand-reference-config --catalog configs/popular_android_maven_catalog.json --output configs/libraries.expanded.json --latest-count 1
```

Useful preview command:

```powershell
docker compose run --rm apk-sbom python -m apk_sbom.cli expand-reference-config --limit 5 --latest-count 1 --dry-run --quiet
```

Current behavior:

- reads a curated Android/Maven coordinate catalog from `configs/popular_android_maven_catalog.json`
- supports Maven Central and per-library repository URLs such as Google Maven
- supports per-library packaging, so AAR and JAR artifacts can coexist in one config
- fetches `maven-metadata.xml` and selects the latest stable version by default
- filters alpha, beta, RC, milestone, preview, EAP, dev, and snapshot versions unless `--include-prerelease` is set
- writes a normal downloader-compatible config at `configs/libraries.expanded.json`
- can write a full expansion summary with `--summary-output`

Current expansion result after calibration on 2026-05-20:

| Field | Result |
|---|---:|
| Catalog coordinates | 147 |
| Resolved coordinates | 147 |
| Failed coordinates | 0 |
| Artifact versions selected | 163 |
| AAR coordinates | 94 |
| JAR coordinates | 53 |
| Google Maven coordinates | 90 |

Generated files:

```text
configs/popular_android_maven_catalog.json
configs/libraries.expanded.json
configs/libraries.calibration.json
data/results/reference-expansion/expanded-summary.json
```

The expanded config has now been fully downloaded, converted, and extracted in controlled batches. Continue to use batches only when regenerating the config or adding new catalog entries, because they make download failures, D8 failures, and false-positive risk easier to isolate.

Current expanded batch result on 2026-05-20:

| Field | Result |
|---|---:|
| Catalog offsets checked | 0-162, all expanded artifact-version entries |
| Unique artifact records in expanded cache | 141 |
| Usable DEX components | 108 |
| Skipped no-bytecode/metadata-only artifacts | 33 |
| Failed artifacts | 0 |
| Expanded DB classes | 39,326 |
| Expanded DB methods | 279,212 |
| Expanded DB class dependencies | 100,612 |
| Expanded DB string literals | 51,776 |
| Combined evaluation DB components | 133 |
| Combined evaluation DB methods | 346,404 |

The offset-70 batch completed on 2026-05-20 with 10 `existing` download results, 0 failures, and no new unique artifact records. Re-running conversion and feature extraction kept the expanded DB and combined DB counts unchanged.

The offset-80 batch completed on 2026-05-20 with 7 downloaded artifacts, 3 existing artifacts, 0 failures, 6 newly converted DEX components, and 1 new no-bytecode skip. The converted refresh included Jackson 2.21.x, Glide 5.0.7, AndroidX Work Runtime 2.10.0, and SwipeRefreshLayout 1.0.0 records.

The offset-90 batch initially failed on `com.google.crypto.tink:tink-android@1.21.0` because the catalog marked it as an AAR, but the published Maven Central POM uses JAR packaging. After changing `tink-android` to `jar` in both the curated catalog and expanded config, the batch completed with 10 converted DEX components and 0 failures.

The offset-100 batch initially failed on `com.google.dagger:dagger-android@2.59.2` because the catalog marked it as a JAR, but Maven Central publishes it as an AAR. After changing `dagger-android` to `aar` in both configs, the batch completed with 9 converted DEX components, 1 Firebase Analytics no-bytecode skip, and 0 failures. The offset-110 batch downloaded and converted 10 additional usable DEX components.

The final offset-120 pass covered the remaining 43 artifact-version entries through the end of the expanded config. It initially failed on `org.greenrobot:eventbus@3.3.1` because the catalog marked it as a JAR, but Maven Central publishes it as an AAR. After changing `eventbus` to `aar` in both configs, the final pass completed with 41 newly converted DEX components, 2 new no-bytecode skips (`com.squareup.okhttp3:okhttp@5.3.2` and `io.insert-koin:koin-core@4.2.1`), and 0 failures.

Generated expanded-batch artifacts:

```text
data/reference_db/artifacts_expanded/
data/reference_db/dex_expanded/
data/reference_db/reference_features_expanded.sqlite
```

These are generated data and are ignored by Git.

Recommended next batch pattern:

```powershell
The expanded config has now been fully checked. Use the command pattern above only after changing `configs/libraries.expanded.json` or adding new catalog entries.
docker compose run --rm apk-sbom python -m apk_sbom.cli convert-reference-dex --artifact-root data/reference_db/artifacts_expanded --output-root data/reference_db/dex_expanded --quiet
docker compose run --rm apk-sbom python -m apk_sbom.cli extract-reference-features --dex-root data/reference_db/dex_expanded --db-path data/reference_db/reference_features_expanded.sqlite --quiet
```

Expanded F-Droid smoke validation with a combined 58-component DB produced 18 SBOM components: 7 version-confirmed, 11 coordinate-present but version-mismatched, and 0 missing from the source dependency tree. This means identity coverage improved, but latest-only AndroidX reference versions are not sufficient for version-level claims. Keep the focused validated DB as the default demo DB until the expanded DB has multiple/source-used versions.

Current calibrated validation with a 91-component combined DB covers three clean source-validated real APKs plus four partial-version-mismatch proofs. F-Droid emits 23 SBOM components and validates 23/23, OpenTracks emits 19 and validates 19/19, and Tusky emits 1 and validates 1/1 after adding `com.squareup.retrofit2:retrofit@3.0.0`. NewPipe validates 10/11, AntennaPod validates 19/20, KDE Connect validates 8/9, and Wikipedia Android validates 11/13 after adding `gson@2.10.1`, `okhttp-android@5.3.2`, and generic OkHttp public-vs-Android target disambiguation. These latest runs have 0 missing coordinates and 0 OSV vulnerabilities. Tusky should be described as clean but sparse; NewPipe, AntennaPod, KDE Connect, and Wikipedia should be described as source-validated partial-mismatch cases.

NewPipe was rerun after adding source-used AndroidX/Okio calibration versions, adding the bytecode-bearing `androidx.lifecycle:lifecycle-runtime-android@2.9.4` target variant, and adding matcher-level version disambiguation. It improved from 5/12 confirmed with 7 mismatches to 10/11 confirmed with 1 mismatch in the main calibrated run, but it remains a partial-version-mismatch case because `androidx.startup:startup-runtime` is still selected as `1.1.1` while source resolves `1.2.0`. Wikipedia repeats the same Startup near-tie and adds a ViewPager2 near-version mismatch. Do not force these with a generic newer-near-tie rule; that rule caused a false version flip on `androidx.concurrent:concurrent-futures`. Maven POM dependency metadata is now captured, stored, and available to a conservative tie-breaker, but the tie-breaker correctly stays dormant for Startup because no independently detected supporting dependency is present. KDE Connect adds the same lesson with `viewpager2` beta resolution; its earlier Lifecycle runtime public/target-variant ambiguity is handled by scoped artifact-family coherence.

## Maven Reference Download Slice

Implemented command:

```powershell
$env:PYTHONPATH='src'
python -m apk_sbom.cli download-maven --config configs\libraries.json
```

Useful preview command:

```powershell
$env:PYTHONPATH='src'
python -m apk_sbom.cli download-maven --config configs\libraries.json --dry-run --limit 3
```

Current behavior:

- builds artifact URLs from `configs/libraries.json` or `configs/libraries.expanded.json`
- supports Maven Central by default and per-library repository URLs such as Google Maven
- downloads `.jar` artifacts by default, with per-library `packaging` overrides for AARs
- supports `--limit` and `--offset` for batch downloads
- supports `--quiet` for compact status-count output during large batches
- stores artifacts under `data/reference_db/artifacts/`
- writes one `metadata.json` per artifact with coordinate, PURL, URL, path, SHA-256, size, and packaging
- downloads the companion `.pom` file when available and records POM path, hash, size, parse status, and direct Maven dependency metadata
- skips already downloaded artifacts when both artifact and metadata exist
- reports failures explicitly in JSON output

Download result on 2026-05-18:

- 20 JAR artifacts currently present
- 20 metadata files written
- total downloaded JAR size: 12,125,214 bytes
- current usable JVM-bytecode seed set includes 19 converted reference artifacts

The first non-elevated network attempt failed with a Windows socket permission error, then the same command succeeded with elevated execution.

POM metadata note:

- `download-maven --force` refreshes existing artifact metadata with POM dependency rows.
- `convert-reference-dex` now rewrites existing conversion metadata so refreshed dependency metadata can flow into feature extraction.
- `extract-reference-features` stores parsed POM dependencies in the SQLite `maven_dependencies` table.
- The matcher loads those dependency rows with reference candidates and has a conservative POM coherence tie-breaker. It only applies to close candidate-level version ties when another independently selected APK-side component supports a candidate's POM dependency version; it does not use POM metadata alone to force a version.

Verification example:

```powershell
docker compose run --rm apk-sbom python -m apk_sbom.cli download-maven --config configs/libraries.calibration.json --output-root data/reference_db/artifacts_calibration --coordinate androidx.startup:startup-runtime --force --quiet
docker compose run --rm apk-sbom python -m apk_sbom.cli convert-reference-dex --artifact-root data/reference_db/artifacts_calibration --output-root data/reference_db/dex_calibration --coordinate androidx.startup:startup-runtime --quiet
docker compose run --rm apk-sbom python -m apk_sbom.cli extract-reference-features --dex-root data/reference_db/dex_calibration --db-path data/reference_db/reference_features_startup_metadata_check.sqlite --coordinate androidx.startup:startup-runtime --reset --quiet
```

The startup-runtime check stores direct dependencies in SQLite. In the current metadata snapshot, `startup-runtime@1.1.1` declares `androidx.annotation:annotation@1.1.0`, while `startup-runtime@1.2.0` declares `androidx.annotation:annotation@1.8.1`. After refreshing `configs/libraries.calibration.json`, the calibrated combined DB stores 481 Maven dependency rows.

## Reference DEX Conversion Slice

Implemented command:

```powershell
$env:PYTHONPATH='src'
python -m apk_sbom.cli convert-reference-dex --artifact-root data\reference_db\artifacts --output-root data\reference_db\dex
```

Useful preview command:

```powershell
$env:PYTHONPATH='src'
python -m apk_sbom.cli convert-reference-dex --dry-run --limit 3
```

Current behavior:

- discovers downloaded artifact `metadata.json` files
- supports coordinate filtering plus `--limit` and `--offset` for batch conversion
- plans output under `data/reference_db/dex/`
- invokes configurable D8 command with `--min-api 21`
- writes `conversion.json` when DEX files are produced
- supports `.jar` directly and `.aar` by extracting `classes.jar`
- reports D8 failures explicitly in JSON output
- supports `--quiet` for compact status-count output without long D8 warning payloads

Docker D8 setup:

- Android command-line tools package: `commandlinetools-linux-14742923_latest.zip`
- Android build-tools package: `36.0.0`
- `ANDROID_HOME` and `ANDROID_SDK_ROOT`: `/opt/android-sdk`
- `d8` is available on the container PATH.

Conversion result on 2026-05-18:

- 19 reference DEX outputs produced
- 20 conversion metadata files written
- 1 metadata-only artifact skipped: `com.squareup.okio:okio:3.0.0`
- `com.squareup.okio:okio-jvm:3.0.0` added and converted for Okio 3 JVM bytecode
- total generated reference DEX size: 10,424,892 bytes

D8 emits warnings for several standalone library JARs because transitive dependencies and Java runtime classes are not passed as a full classpath. The warnings do not block DEX generation for the current MVP feature extraction stage.

## Reference Feature SQLite Slice

Implemented command:

```powershell
$env:PYTHONPATH='src'
python -m apk_sbom.cli extract-reference-features --reset
```

Docker command:

```powershell
docker compose run --rm apk-sbom python -m apk_sbom.cli extract-reference-features --reset
```

Current behavior:

- discovers converted reference `conversion.json` files
- skips metadata-only conversion records by default
- parses each reference `classes.dex` with Androguard
- stores component metadata in SQLite
- stores DEX file metadata, packages, class descriptors, method signatures, opcode histograms, class dependency graph features, and string literals
- supports coordinate filtering, `--limit`, `--offset`, and DB reset
- supports `--quiet` for compact database and status-count output

Extraction result on 2026-05-19:

| Table | Rows |
|---|---:|
| `components` | 19 |
| `dex_files` | 19 |
| `packages` | 220 |
| `classes` | 5,526 |
| `methods` | 55,353 |
| `opcodes` | 2,451 |
| `class_dependencies` | 21,757 |
| `dependency_shapes` | 266 |
| `string_literals` | 13,402 |

SQLite DB path:

```text
data/reference_db/reference_features.sqlite
```

The SQLite DB is generated data and is ignored by Git.

## Package/Class/Method/Opcode Matcher Slice

Implemented command:

```powershell
$env:PYTHONPATH='src'
python -m apk_sbom.cli match-apk path\to\sample.apk --top 10
```

Docker command:

```powershell
docker compose run --rm apk-sbom python -m apk_sbom.cli match-apk data/test_apks/sample.apk --top 10
```

Current behavior:

- analyzes all APK DEX files with class, method, and dependency extraction enabled
- loads component package, class, method, opcode, and class dependency graph features from SQLite
- scores package, class, method, and string literal evidence by reference coverage
- scores opcode evidence with histogram cosine similarity
- uses initial weights: package `0.15`, class `0.45`, method `0.25`, opcode `0.15`, dependency `0.10`, literal `0.08`, and version-unique feature evidence `0.12`
- returns ranked candidates with matched/reference/APK counts for each evidence family
- groups candidates per Maven coordinate and emits an initial version decision with `high`, `medium`, `low`, or `uncertain` confidence
- scores class dependency graph evidence with exact edge coverage plus structural graph/shape similarity
- promotes strong obfuscation-resilient literal/opcode evidence to a low-confidence `candidate`, not an `exact` version

This matcher is strongest on clear APKs and lightly changed libraries. Opcode, CDG shape, string literals, and version-unique literal evidence provide cautious fallback signals when names are less reliable, but heavy R8, inlining, shrinking, and broad structural similarity between nearby versions still require careful calibration.

## Real CycloneDX SBOM Slice

Implemented command:

```powershell
$env:PYTHONPATH='src'
python -m apk_sbom.cli generate-sbom path\to\sample.apk --output data\results\sbom.cdx.json
```

Current behavior:

- runs APK inspection
- runs the package/class/method/opcode matcher
- converts version decisions to CycloneDX library components
- adds native `.so` files as CycloneDX `file` components with SHA-256 hashes and hash-only identification properties
- writes Maven PURL, selected version, confidence, match type, and evidence properties

The Docker runtime now installs CycloneDX CLI, Trivy, Grype, Syft, cdxgen, node, and npm for optional external scanner comparison. Dotnet remains optional and missing because the standalone CycloneDX CLI binary is used. Readiness is recorded in `docs/evaluation/EXTERNAL_SCANNER_VALIDATION_STATUS.md`, and the current CycloneDX/Grype/Trivy SBOM comparison is recorded in `docs/evaluation/EXTERNAL_SCANNER_VALIDATION.md`.

## OSV Vulnerability Lookup Slice

Implemented command:

```powershell
$env:PYTHONPATH='src'
python -m apk_sbom.cli scan-sbom-osv data\results\sbom.cdx.json --output data\results\osv-vulnerabilities.json
```

Current behavior:

- loads Maven library components from CycloneDX JSON
- sends OSV querybatch requests using `ecosystem=Maven`, `name=group:artifact`, and `version`
- optionally enriches returned advisory IDs with individual OSV vulnerability details, including CVE aliases and summaries
- writes a JSON vulnerability summary with component and vulnerability counts
- classifies each returned advisory as `confirmed` only when APK-side identity evidence is strong and version evidence is exact/high confidence
- classifies advisories for low-confidence, candidate, or latest-only version matches as `potential` until source/dependency-tree validation confirms the version
- parses OSV severity when available and deduplicates advisories that share OSV, GHSA, or CVE aliases
- normal tests mock the OSV network call, so the test suite does not depend on internet availability

## Final Report Slice

Implemented command:

```powershell
$env:PYTHONPATH='src'
python -m apk_sbom.cli generate-report path\to\sample.apk --output-dir data\results\report
```

Current behavior:

- runs APK inspection
- runs matcher and version decisions
- writes `matches.json`
- writes `sbom.cdx.json`
- optionally queries OSV and writes `osv-vulnerabilities.json`
- writes combined `report.json`
- writes supervisor-readable `report.md`
- writes static supervisor-friendly `report.html`
- lists native `.so` files as hash-only evidence with path, ABI, size, and SHA-256

For local/offline testing, use `--skip-osv` to avoid a network call.

HTML report behavior:

- summarizes APK metadata, DEX status, detected Maven components, native file count, and vulnerability lookup status
- displays confidence bars and exact/likely/candidate labels
- displays candidate reason summaries, APK forensic indicators, app package/version/SDK hints, and obfuscation-risk warnings
- includes expandable evidence details for each emitted Maven component
- lists raw version decisions separately, including low-confidence and uncertain decisions for auditability

F-Droid HTML report example:

```text
data/results/report-real-f-droid-html/report.html
```

## Controlled Fixture And Evaluation Slice

Implemented scripts:

```powershell
$env:PYTHONPATH='src'
python scripts\build_controlled_apk.py --coordinate com.google.code.gson:gson --version 2.8.9 --variant clear
python scripts\build_controlled_apk.py --coordinate com.google.code.gson:gson --version 2.8.9 --variant r8-rename
python scripts\build_controlled_apk.py --coordinate com.google.code.gson:gson --version 2.8.9 --variant r8-shrink
python scripts\evaluate_controlled_reports.py
python scripts\build_apk_testset_inventory.py
python scripts\evaluate_baselines.py
```

Docker equivalents:

```powershell
docker compose run --rm apk-sbom python scripts/build_controlled_apk.py --coordinate com.google.code.gson:gson --version 2.8.9 --variant clear
docker compose run --rm apk-sbom python scripts/build_controlled_apk.py --coordinate com.google.code.gson:gson --version 2.8.9 --variant r8-rename
docker compose run --rm apk-sbom python scripts/build_controlled_apk.py --coordinate com.google.code.gson:gson --version 2.8.9 --variant r8-shrink
docker compose run --rm apk-sbom python scripts/evaluate_controlled_reports.py
docker compose run --rm apk-sbom python scripts/build_apk_testset_inventory.py
docker compose run --rm apk-sbom python scripts/evaluate_baselines.py
```

Current controlled fixtures:

| Variant | Ground truth | Current result |
|---|---|---|
| `clear` | `com.fasterxml.jackson.core:jackson-databind@2.9.10.8` | exact/high, detected in SBOM |
| `clear` | `com.google.code.gson:gson@2.8.9` | exact/high, detected in SBOM |
| `r8-rename` | `com.google.code.gson:gson@2.8.9` | candidate/low, detected in SBOM |
| `r8-shrink` | `com.google.code.gson:gson@2.8.9` | candidate/low, detected in SBOM |
| `clear` | `com.squareup.okhttp3:okhttp@4.9.1` | exact/high, detected in SBOM |
| `clear` | `com.squareup.retrofit2:retrofit@2.9.0` | exact/high, detected in SBOM |
| `clear` | `commons-codec:commons-codec@1.16.1` | exact/high, detected in SBOM |
| `r8-rename` | `commons-codec:commons-codec@1.16.1` | candidate/low, detected in SBOM |
| `r8-shrink` | `commons-codec:commons-codec@1.16.1` | candidate/low, detected in SBOM |

Current controlled metrics:

| Metric | Value |
|---|---:|
| Component precision | 1.000 |
| Component recall | 1.000 |
| Version precision | 1.000 |
| Version recall | 1.000 |
| Candidate version recall | 1.000 |

This is a useful early result: the MVP has a working clear-APK path and produces cautious low-confidence candidate behavior under R8 transformations instead of overclaiming exact recovery.

Baseline comparison:

| Baseline | Component recall | Version recall |
|---|---:|---:|
| Package overlap | 0.889 | 0.667 |
| Class overlap | 0.556 | 0.556 |
| Exact DEX hash | 0.556 | 0.556 |

The comparison is documented in `docs/evaluation/CONTROLLED_EVALUATION.md`.

The APK testset inventory is documented in `docs/evaluation/APK_TESTSET_INVENTORY.md` and generated as structured JSON at `data/results/evaluation/apk-testset-inventory.json`. It records each controlled APK's expected Maven component/version, language/library profile, R8/obfuscation variant, DEX/multidex/native details, and current false-positive/false-negative comparison. It also records the calibrated source-validated real APKs: F-Droid has 23/23 source-confirmed emitted Maven components and OpenTracks has 19/19. The inventory keeps the important scope note that source dependency trees contain more entries than the current MVP emits. The inventory also carries the research dataset classification fields from `docs/evaluation/DATASET_DESIGN.md`: dataset layer, validation level, metric eligibility, source proof, release era, R8 mode, native ABI list, AndroidX/KMP profile, dependency family, transitive complexity, overlapping artifact families, and vulnerability expectation.

The real-APK candidate backlog is tracked in `docs/evaluation/REAL_APK_CANDIDATES.md`. Candidate APKs are not admitted into the source-validated dataset until their APK/source tag, version match, Gradle dependency tree, generated report, and source-validation artifacts exist.

The candidate table is generated from `configs/real_apk_candidates.json`:

```powershell
python scripts\build_real_apk_candidate_matrix.py
```

The generator also writes a structured summary to `data/results/evaluation/real-apk-candidates.json`.

First-batch proof checklists are generated with:

```powershell
python scripts\scaffold_real_apk_proof.py
```

Outputs:

- `docs/evaluation/REAL_APK_PROOF_BUNDLE_PLAN.md`
- `data/results/evaluation/real-apk-proof/index.json`
- `data/results/evaluation/real-apk-proof/index.md`
- `data/results/evaluation/real-apk-proof/<candidate-id>/proof-checklist.md`
- `data/results/evaluation/real-apk-proof/<candidate-id>/proof-checklist.json`

The current first-batch targets are OpenTracks `v4.27.0irreproducible`/6653, NewPipe `0.28.5`/1010, Tusky `32.2`/142, K-9/Thunderbird Android `18.0`/39035, AntennaPod `3.11.4`/3110495, KDE Connect `1.35.5`/13505, and Organic Maps `2026.05.08-4-FDroid`/26050804. OpenTracks and Tusky are clean source-validated cases; AntennaPod is source-validated with 19/20 confirmed and one AndroidX Core near-tie mismatch; KDE Connect is source-validated with 8/9 confirmed and one ViewPager2 beta-version mismatch; NewPipe has a complete proof attempt but remains a partial-version-mismatch case; K-9 is source-validated partial at 5/11 confirmed after the plugin-lite validation-copy rescue; Organic Maps is limitation-complete.

OpenTracks completed proof status:

| Field | Result |
|---|---|
| APK | `data/test_apks/real/opentracks/opentracks.apk` |
| APK SHA-256 | `e5e51772ec2cd9f1474bc6d8cc6a180f6a286a690dc21226d974eac1c1c6b201` |
| F-Droid metadata | `data/test_apks/real/opentracks/fdroid-metadata.yml` |
| Source tarball | `data/source/opentracks-v4.27.0irreproducible/source.tar.gz` |
| Source commit from F-Droid metadata | `f143aabfbf77d1b71864042fe4f0bbf2b4174f4f` |
| Gradle dependency tree | `data/results/source-validation/opentracks/fullReleaseRuntimeClasspath.txt` |
| Final calibrated MVP report | `data/results/report-real-opentracks-calibrated-db/report.md` |
| Source validation | `data/results/source-validation/opentracks-calibrated-db/source-validation.md` |

OpenTracks is counted as the second completed source-validated APK. Docker Gradle 9.5.0 generated the resolved runtime dependency tree from the extracted F-Droid source tarball. The calibrated report emits 19 Maven components, OSV returns 0 vulnerabilities, and source validation confirms 19/19 versions with 0 mismatches and 0 missing coordinates.

## Real APK Case Study

First real-world APK:

```text
data/test_apks/real/F-Droid.apk
```

Generated report:

```text
data/results/report-real-f-droid/report.md
```

Case-study note:

```text
docs/evaluation/REAL_APK_CASE_STUDY.md
```

Initial summary:

| Field | Result |
|---|---|
| DEX files | 2 |
| Multidex | true |
| Native `.so` files | 4 hash-only file components |
| Maven components included in SBOM | 3 |
| OSV findings | 2 |

Source validation:

| Evidence | Result |
|---|---|
| Source repository | `https://gitlab.com/fdroid/fdroidclient` |
| Checked source tag | `1.23.2` |
| Tag commit | `0ea06b1c1d68765c4a434d0b676b3e0f23f04cb1` |
| APK/source version check | APK `versionCode` is `1023052`; source `app/build.gradle` also declares `versionCode 1023052`. |
| Direct OkHttp dependency | `app/build.gradle` uses `implementation libs.okhttp`; `gradle/libs.versions.toml` maps this to `com.squareup.okhttp3:okhttp` version `4.12.0`. |
| Ktor dependency | `libs/download/build.gradle` uses `libs.ktor.client.okhttp`; `gradle/libs.versions.toml` maps Ktor to `2.3.12`. |

Detected Maven components:

| Component | MVP version | Decision | Confidence | Source validation |
|---|---:|---|---:|---|
| `com.squareup.okhttp3:okhttp` | 4.10.0 | likely/medium | 0.775 | Component identity confirmed, but source version is `4.12.0`; the current reference DB lacks that version, so this is a nearest-known version miss. |
| `com.squareup.okio:okio` | 2.8.0 | candidate/low | 0.557 | Not source-confirmed as an exact version; likely affected by transitive Okio/Ktor evidence and incomplete DB coverage. |
| `com.squareup.okio:okio-jvm` | 3.0.0 | candidate/low | 0.472 | Not source-confirmed as an exact version; needs resolved Gradle dependency tree or expanded 3.x reference versions. |

OSV returned `CVE-2023-3635` for the Okio candidates. After source validation, treat this as a potential vulnerability signal only, not a confirmed finding, because the exact Okio artifact/version has not been validated against the F-Droid source dependency graph.

Interpretation:

- The MVP correctly recovered a real third-party library family from a multidex APK: OkHttp.
- The version result for OkHttp is wrong against source ground truth because `4.12.0` is outside the current reference DB. This is an expected limitation of reference-database methods and a strong argument for expanding the DB before larger real-world evaluation.
- The low-confidence Okio results demonstrate why candidate labels matter: they may point to a real transitive library family, but they should not be used as confirmed CVE evidence without source or dependency-tree validation.

Expanded reference DB rerun:

| Field | Result |
|---|---|
| Added reference artifacts | OkHttp `4.12.0`, Okio JVM `3.6.0`/`3.7.0`, and Ktor JVM `2.3.12` modules. |
| Reference DB after rebuild | 27 components, 27 DEX files, 294 packages, 7,441 classes, 69,220 methods, 25,197 dependency edges, and 17,108 string literals. |
| New report | `data/results/report-real-f-droid-expanded-db/report.md` |
| Maven components included in expanded SBOM | 5 |
| OSV findings in expanded report | 1 potential Okio finding |

Expanded detected Maven components:

| Component | MVP version | Decision | Confidence | Source validation |
|---|---:|---|---:|---|
| `com.squareup.okhttp3:okhttp` | 4.12.0 | likely/medium | 0.807 | Source-confirmed direct dependency and version. |
| `io.ktor:ktor-client-okhttp-jvm` | 2.3.12 | likely/medium | 0.788 | Source-confirmed Ktor OkHttp engine family; JVM artifact is the resolved variant used for bytecode comparison. |
| `com.squareup.okio:okio` | 2.8.0 | candidate/low | 0.557 | Still not source-confirmed as an exact artifact/version. |
| `com.squareup.okio:okio-jvm` | 3.7.0 | candidate/low | 0.543 | More plausible than the initial `3.0.0`, but still low-confidence and not source-confirmed. |
| `io.ktor:ktor-http-jvm` | 2.3.12 | candidate/low | 0.456 | Likely transitive/supporting Ktor evidence; not a direct source declaration. |

The expanded DB fixed the OkHttp version miss: the MVP moved from the nearest available version `4.10.0` to the source-confirmed version `4.12.0`. This is good evidence that the reference-database architecture works as expected, while also showing that DB coverage and related-artifact disambiguation are critical for real APKs.

Artifact-family disambiguation rerun:

| Field | Result |
|---|---|
| New report | `data/results/report-real-f-droid-disambiguated/report.md` |
| Maven components included in SBOM | 4 |
| OSV findings | 0 |
| Disambiguation behavior | Raw decisions still list both `okio@2.8.0` and `okio-jvm@3.7.0`; SBOM/report components keep `okio-jvm@3.7.0` and suppress overlapping `okio@2.8.0`. |

Disambiguated detected Maven components:

| Component | MVP version | Decision | Confidence | Notes |
|---|---:|---|---:|---|
| `com.squareup.okhttp3:okhttp` | 4.12.0 | likely/medium | 0.807 | Source-confirmed direct dependency and version. |
| `io.ktor:ktor-client-okhttp-jvm` | 2.3.12 | likely/medium | 0.788 | Source-confirmed Ktor OkHttp engine family. |
| `com.squareup.okio:okio-jvm` | 3.7.0 | candidate/low | 0.543 | Kept as the JVM bytecode artifact for the Okio family; still low-confidence. |
| `io.ktor:ktor-http-jvm` | 2.3.12 | candidate/low | 0.456 | Likely transitive/supporting Ktor evidence. |

This removes the earlier questionable `okio@2.8.0` SBOM component and therefore removes the unconfirmed Okio CVE signal from the OSV result.

Source dependency-tree validation:

| Field | Result |
|---|---|
| Gradle source configuration | `:app:fullReleaseRuntimeClasspath` |
| Validation output folder | `data/results/source-validation/fdroid/` |
| Summary artifact | `data/results/source-validation/fdroid/validation-summary.md` |

Resolved source comparison:

| MVP SBOM component | Source-resolved dependency | Result |
|---|---|---|
| `com.squareup.okhttp3:okhttp@4.12.0` | `com.squareup.okhttp3:okhttp:4.12.0` | Confirmed. |
| `io.ktor:ktor-client-okhttp-jvm@2.3.12` | `io.ktor:ktor-client-okhttp-jvm:2.3.12` | Confirmed. |
| `com.squareup.okio:okio-jvm@3.7.0` | `com.squareup.okio:okio-jvm:3.7.0` | Confirmed, though APK-side confidence remains low. |
| `io.ktor:ktor-http-jvm@2.3.12` | `io.ktor:ktor-http-jvm:2.3.12` | Confirmed, though APK-side confidence remains low. |

The source dependency tree also confirms that `com.squareup.okio:okio@2.8.0` is not present; Gradle resolves Okio to `3.7.0`, so suppressing the old `okio@2.8.0` SBOM candidate was correct for this APK.

## Source Dependency Validation CLI

Implemented command:

```powershell
$env:PYTHONPATH='src'
python -m apk_sbom.cli validate-source-deps --sbom data\results\report-real-f-droid-disambiguated\sbom.cdx.json --dependency-tree data\results\source-validation\fdroid\app-fullReleaseRuntimeClasspath.txt --output-dir data\results\source-validation\fdroid-auto --candidate com.squareup.okio:okio@2.8.0
```

Docker equivalent:

```powershell
docker compose run --rm apk-sbom python -m apk_sbom.cli validate-source-deps --sbom data/results/report-real-f-droid-disambiguated/sbom.cdx.json --dependency-tree data/results/source-validation/fdroid/app-fullReleaseRuntimeClasspath.txt --output-dir data/results/source-validation/fdroid-auto --candidate com.squareup.okio:okio@2.8.0
```

Current behavior:

- parses Gradle dependency-tree text output such as `:app:fullReleaseRuntimeClasspath`
- loads Maven library components from a CycloneDX SBOM
- compares each SBOM component against source-resolved Maven coordinates and versions
- reports each component as `confirmed`, `version-mismatch`, or `missing`
- optionally checks extra candidates, which is useful for suppressed raw matcher candidates
- writes `source-validation.json` and `source-validation.md`

F-Droid automated validation result:

| Group | Components | Confirmed | Version mismatch | Missing |
|---|---:|---:|---:|---:|
| SBOM components | 4 | 4 | 0 | 0 |
| Extra candidates | 1 | 0 | 1 | 0 |

The extra candidate was `com.squareup.okio:okio@2.8.0`; the source dependency tree resolves `com.squareup.okio:okio` to `3.7.0`, so the tool marks it as a version mismatch rather than a confirmed component.
