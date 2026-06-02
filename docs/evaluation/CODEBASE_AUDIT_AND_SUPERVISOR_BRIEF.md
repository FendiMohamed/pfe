# Codebase Audit And Supervisor Brief

This document is a supervisor-facing audit of the APK-to-SBOM MVP codebase. It checks whether the implemented workflow is data-driven or whether any manual/hardcoded logic is forcing the reported results. It also summarizes the source code structure, architecture choices, state-of-the-art basis, and a repeatable demo method.

## Executive Conclusion

The current MVP workflow is coherent and data-driven:

```text
APK
-> APK inspection and DEX parsing
-> APK feature extraction
-> comparison against a SQLite Maven reference feature DB
-> score and confidence calculation
-> CycloneDX SBOM generation
-> optional OSV vulnerability lookup
-> JSON/Markdown/HTML reports
```

No core runtime code path was found that says, in effect, "if this is F-Droid, output these components" or "if this is the vulnerable demo, output these vulnerabilities." The real report path uses bytecode features from the APK and features from the selected reference database.

There are intentional fixed inputs and heuristics, but they are not hidden result forcing:

- Controlled APK fixtures have known ground truth because they are built by the project for evaluation.
- Calibration configs include source-used F-Droid versions so the reference DB contains versions that can be tested against the real APK.
- Source validation reads the Gradle dependency tree after SBOM generation to verify the emitted SBOM; it does not feed those dependencies into the matcher.
- Artifact-family heuristics prefer overlapping bytecode-bearing artifacts such as `okio-jvm`, `okhttp-android`, and AndroidX Lifecycle target variants when evidence is close. These are documented disambiguation rules, not direct source-result overrides.
- A scoped Compose app-era coherence heuristic can promote or downgrade `runtime-android` only when nearby Compose family artifacts independently support or contradict the same version band. It is intentionally narrow and was regression-tested before promoting `runtime-android@1.10.6`.

The thesis-safe claim is therefore:

> The MVP does not recover a universal complete SBOM for every APK. It recovers known Java/Kotlin Maven libraries that exist in the reference DB, assigns cautious identity/version confidence from bytecode evidence, and validates selected case-study results against source dependency data when available.

## Manual Or Hardcoded Result Audit

| Area | Location | What it does | Affects real `generate-report` output? | Audit conclusion |
|---|---|---|---|---|
| Mock SBOM detection | `src/apk_sbom/sbom.py::make_mock_detection`; `src/apk_sbom/cli.py::generate-mock-sbom` | Emits a fixed Gson component for early CycloneDX testing. | No, unless the explicit `generate-mock-sbom` command is used. | Safe demo/test helper, not part of real matching. |
| Controlled fixture builder | `scripts/build_controlled_apk.py` | Builds APK fixtures from known Maven artifacts and writes `.ground-truth.json`. | No. | Evaluation-only ground truth by construction. |
| Controlled evaluation scripts | `scripts/evaluate_controlled_reports.py`; `scripts/evaluate_baselines.py` | Compare generated reports with ground truth. | No. | Measures results after detection; does not influence detection. |
| Source validation candidates | `src/apk_sbom/source_validation.py::parse_maven_component_spec` | Allows a manually provided candidate to be checked against a Gradle tree. | No, only validates extra candidates after SBOM generation. | Useful for explaining suppressed candidates; not result forcing. |
| Okio artifact-family rule | `src/apk_sbom/matcher.py::ARTIFACT_FAMILY_RULES` | Suppresses overlapping `okio` / `okio-jvm` output when they represent the same family and scores are close. | Yes, as a transparent report disambiguation heuristic. | Acceptable if disclosed. It changes duplicate reporting, not raw score evidence. |
| Compose app-era coherence | `src/apk_sbom/matcher.py::APP_ERA_COHERENCE_RULES` | Uses independently selected Compose family versions to select or downgrade low-confidence Compose Runtime candidates. | Yes, as a transparent version-band heuristic. | Acceptable if disclosed. It is scoped to Compose and requires sibling-family support; it is not a generic newer-version rule. |
| Calibrated real-APK config | `configs/libraries.calibration.json` | Adds F-Droid/OpenTracks source-used versions and Android target variants to the reference DB. | Yes, by improving reference coverage. | This is calibration, not forcing. The matcher still compares bytecode features and source validation verifies after the fact. |
| Expanded latest-only catalog | `configs/popular_android_maven_catalog.json`; `configs/libraries.expanded.json` | Provides broad popular library coverage, often with latest stable versions. | Yes, when that DB is selected. | Useful for stress testing identity discovery. Not thesis-grade version evidence unless calibrated. |
| Test expectations | `tests/*.py` | Assert expected behavior for units and fixtures. | No. | Normal automated testing. |

Overall finding: the runtime heuristics that should be explicitly explained to the supervisor are artifact-family disambiguation for Okio/Okio-JVM, OkHttp public-vs-Android target variants, AndroidX Lifecycle public-vs-Android target variants, and scoped Compose app-era coherence. The strongest real results are the calibrated F-Droid and OpenTracks case studies: 23/23 and 19/19 emitted Maven components were independently validated against source dependency trees with 0 mismatches and 0 missing coordinates.

## Runtime Workflow

The real report command enters through the CLI and then follows one main path:

1. `src/apk_sbom/cli.py`
   Parses commands such as `generate-report`, `match-apk`, `generate-sbom`, and `scan-sbom-osv`.

2. `src/apk_sbom/report.py::generate_final_report`
   Orchestrates the full end-to-end report workflow.

3. `src/apk_sbom/apk_extractor.py::inspect_apk`
   Reads the APK as a ZIP archive, hashes it, detects standard and nonstandard DEX files, records native `.so` files, parses manifest metadata when possible, and builds forensic indicators.

4. `src/apk_sbom/dex_analyzer.py::analyze_apk_dex`
   Parses every standard `classes*.dex` file and extracts packages, classes, methods, opcode histograms, string literals, dependency edges, and dependency graph shape.

5. `src/apk_sbom/matcher.py::match_apk_to_reference_db`
   Loads reference features from SQLite, scores each reference component against APK features, groups candidates by Maven coordinate, separates identity confidence from version confidence, and prepares reportable components.

6. `src/apk_sbom/sbom.py::build_cyclonedx_bom`
   Builds a CycloneDX JSON SBOM with Maven PURLs, evidence, confidence properties, application metadata, and native file components.

7. `src/apk_sbom/vulnerability.py::query_osv_for_libraries`
   Optionally queries OSV for the emitted Maven components, enriches severity, deduplicates advisories, and labels findings as confirmed or potential based on confidence.

8. `src/apk_sbom/report.py`
   Writes `report.json`, `report.md`, `report.html`, and `sbom.cdx.json`.

## Source Code File Map

| File | Role |
|---|---|
| `src/apk_sbom/__init__.py` | Package marker and version-level import surface. |
| `src/apk_sbom/__main__.py` | Allows `python -m apk_sbom` to run the CLI. |
| `src/apk_sbom/cli.py` | Command-line interface for APK inspection, DEX analysis, Maven download, D8 conversion, reference feature extraction, matching, SBOM generation, OSV scan, source validation, and full reports. |
| `src/apk_sbom/apk_extractor.py` | APK forensic inspection: SHA-256, ZIP entries, standard/misplaced DEX discovery, manifest metadata, resources, native libraries, protector/packer indicators, extraction risk summary. |
| `src/apk_sbom/dex_analyzer.py` | Androguard-backed DEX parser. Extracts class descriptors, packages, methods, opcodes, string literals, class dependency edges, and dependency graph shape. |
| `src/apk_sbom/reference_config.py` | Loads curated Maven library config files and normalizes Maven coordinate metadata. |
| `src/apk_sbom/maven_downloader.py` | Downloads selected Maven artifacts from Maven Central or configured repositories and writes artifact metadata. |
| `src/apk_sbom/reference_converter.py` | Converts downloaded JAR/AAR artifacts to DEX using Android D8 and records converted/skipped/failed status. Handles AAR `classes.jar`. |
| `src/apk_sbom/reference_features.py` | Builds and updates the SQLite reference feature database from converted reference DEX files. |
| `src/apk_sbom/reference_expander.py` | Expands a popular-library catalog into resolved Maven versions using Maven metadata, with stable-version filtering and repository support. |
| `src/apk_sbom/matcher.py` | Core matcher. Scores APK features against reference features using package/class/method overlap, opcode similarity, dependency graph evidence, string literals, and version-unique features. Also computes identity/version confidence and artifact-family disambiguation. |
| `src/apk_sbom/models.py` | Shared dataclasses for detected libraries and evidence, including identity and version confidence/status fields. |
| `src/apk_sbom/sbom.py` | CycloneDX SBOM builder for application metadata, Maven components, evidence properties, confidence properties, and native file components. |
| `src/apk_sbom/vulnerability.py` | OSV query logic, CycloneDX-to-library loading, severity extraction, advisory deduplication, and confirmed/potential vulnerability classification. |
| `src/apk_sbom/source_validation.py` | Post-report validation against a Gradle dependency tree when source is available. Produces JSON/Markdown validation artifacts. |

## Script File Map

| File | Role |
|---|---|
| `scripts/check_toolchain.py` | Checks availability of local/container tools and Python packages. |
| `scripts/build_controlled_apk.py` | Builds controlled APK fixtures with known dependencies and optional R8 variants for evaluation. |
| `scripts/evaluate_controlled_reports.py` | Measures controlled report outputs against `.ground-truth.json` files. |
| `scripts/evaluate_baselines.py` | Compares the hybrid matcher with simpler package/class/hash baselines. |
| `scripts/build_apk_testset_inventory.py` | Generates the thesis-facing APK testset inventory, including controlled ground truth, F-Droid source-confirmed components, obfuscation notes, multidex/native details, and FP/FN fields. |

## Test File Map

| File | What it protects |
|---|---|
| `tests/test_apk_extractor.py` | Multidex/native extraction, manifest metadata, and forensic indicators. |
| `tests/test_dex_analyzer.py` | DEX descriptor parsing, dependency-shape counting, string literal extraction, and parse-error handling. |
| `tests/test_reference_config.py` | Maven config loading, PURL construction, packaging/repository fields, and calibration config sanity. |
| `tests/test_maven_downloader.py` | Maven artifact URLs, filtering, offsets, packaging, repository support, and metadata writing. |
| `tests/test_reference_converter.py` | D8 conversion planning, offset handling, AAR handling, missing-D8 behavior, skipped conversions, and Windows path support. |
| `tests/test_reference_features.py` | SQLite reference extraction, skipped conversion handling, offsets, and DB writing. |
| `tests/test_reference_expander.py` | Popular catalog size, Google Maven support, metadata parsing, stable version selection, and dry-run behavior. |
| `tests/test_matcher.py` | Hybrid scoring, opcode similarity, version-unique tie-breakers, confidence split, one-version confidence cap, and Okio family disambiguation. |
| `tests/test_sbom.py` | CycloneDX Maven component output, evidence/confidence properties, and JSON writing. |
| `tests/test_report.py` | Markdown/HTML/JSON report sections, native library rows, forensic summary, candidate reasons, and escaping. |
| `tests/test_vulnerability.py` | OSV payloads, enrichment, severity, deduplication, confidence-aware confirmed/potential labeling, and CycloneDX loading. |
| `tests/test_source_validation.py` | Gradle dependency tree parsing, confirmed/mismatch/missing validation, and extra-candidate reporting. |

## Architecture Choices And Rationale

| Choice | Why this MVP uses it | Alternative considered | Why not the alternative first |
|---|---|---|---|
| Static APK analysis | It is reproducible, legal for offline APK samples, and matches SBOM recovery from compiled artifacts. | Dynamic runtime instrumentation. | More complex, device/emulator dependent, and less suitable for a first thesis MVP. |
| Python pipeline | Fast iteration, strong libraries, easy Docker execution, good reporting support. | Java/Kotlin-only implementation. | Better Android-native ecosystem, but slower MVP iteration and less convenient data/report scripting. |
| Docker runtime | Makes Androguard, D8, Java, and Python dependencies reproducible for demos. | Host-only setup. | Host tools differ across machines and are harder to defend in a supervisor demo. |
| ZIP/APK inspection plus Androguard | APKs are ZIP files, while DEX parsing needs a specialized parser. | Full decompilation with JADX only. | Decompilation is heavier and less stable; the matcher mainly needs bytecode-level features. |
| Maven reference DB | Version identification needs known reference artifacts. | Search all Maven live during matching. | Online live search would be slow, nondeterministic, and hard to evaluate. |
| D8 reference conversion | APK code is DEX, so references must be compared in DEX form. | Compare JAR bytecode directly. | JVM bytecode and Android DEX are not the same representation. |
| SQLite feature storage | Simple local indexed database, transparent, portable, easy to inspect. | Vector database or large search engine. | Overkill for the MVP and harder to explain scientifically. |
| Weighted hybrid matching | Combines name-sensitive and obfuscation-resilient evidence. | Package-only or hash-only matching. | Too fragile under obfuscation, shading, multidex, and version changes. |
| Separate identity and version confidence | Prevents overclaiming exact versions when identity is stronger than version evidence. | One combined confidence label. | A single label hides the main risk in SBOM vulnerability claims. |
| Calibrated real APK case study | Lets the thesis verify selected real results against source dependencies. | Broad latest-only DB as the main result. | Broad latest-only coverage produced version mismatches and is better framed as a stress test. |
| CycloneDX with PURL | Standard SBOM format and Maven package identity. | Custom JSON only. | Custom JSON is useful internally but weaker for interoperability. |
| OSV first | Direct Maven ecosystem vulnerability lookup with simple API. | NVD CPE mapping first. | CPE mapping for Java/Maven libraries is often harder and less direct. |
| Native `.so` hash-only reporting | Honest MVP boundary: native version detection is a separate research problem. | Full native library identification. | Needs different features and tooling, and would risk widening the frozen scope. |

## State Of The Art Synthesis

| Paper/tool family | Why it matters most | How the MVP uses the lesson |
|---|---|---|
| LibScout | Establishes reference-profile and version-level Android library detection. | Motivates the Maven reference DB and exact-version objective. |
| LibSift / LibD | Show that separating app code from library code and using graph/scalable features is important. | Supports package clustering, dependency features, and avoiding package-name-only logic. |
| LibPecker | Emphasizes class dependency graph and class similarity. | Supports class dependency edge and graph-shape features. |
| LibID | Uses CFG/basic-block/class signatures and studies obfuscation constraints. | Supports structural evidence and cautious obfuscation handling. |
| LibScan | Uses staged matching with class correspondence, method opcode, and call-chain opcode evidence. | Supports hybrid package/class/method/opcode matching rather than one signal. |
| ATVHunter | Connects exact vulnerable library version detection to CVE mapping using CFG/opcode ideas. | Directly supports the MVP goal of versioned SBOM plus vulnerability lookup. |
| SAD | Focuses on version-level TPL detection through class dependency graph, class summaries, and literal tie-breakers. | Supports version-unique classes/methods/strings/dependency edges. |
| LibHunter / LibAttention | Show that modern R8 optimization is a serious challenge and that ML can help but is heavier. | Justifies R8 fixtures, low-confidence labels under shrinking, and deferring ML to future work. |
| OSSPolice / Keep me Updated | Show why exact library versions matter for security and update analysis. | Supports version confidence and vulnerability confirmation rules. |
| LibRARIAN / DroidNative | Show native libraries matter but require separate methods. | Justifies native `.so` hashing without claiming native package/version recovery. |
| CycloneDX / PURL / OSV / Trivy / Grype | Define practical SBOM and scanner interoperability expectations. | Supports CycloneDX output, Maven PURLs, OSV-first vulnerability queries, and optional scanner validation later. |

Most important papers for explaining the MVP:

1. ATVHunter, because it is closest to the thesis goal: Android third-party library version evidence linked to vulnerabilities.
2. SAD, because it supports version-level structural matching and tie-breakers beyond package names.
3. LibScout, because it explains the reference-profile idea and why known library versions are needed.
4. LibHunter, because it explains why R8/optimization limits must be handled honestly.
5. LibScan / LibID / LibPecker, because together they justify opcode, CFG/structural, and dependency graph features.
6. The systematic assessment papers, because they justify evaluating precision/recall, false positives, false negatives, obfuscation, and version-level accuracy separately.

## Current Evidence For The MVP

| Evaluation slice | What it proves | Current result |
|---|---|---|
| Controlled APK fixtures | Known dependencies can be recovered under clear and R8 fixture conditions. | 9/9 expected components detected; 0 false positives; 0 false negatives; 0 version mismatches in the inventory. |
| Calibrated F-Droid case study | Real APK results can be source-validated when the reference DB contains source-used versions. | 23 Maven SBOM components; source validation confirmed 23/23 versions; 0 mismatches; 0 missing. |
| Calibrated OpenTracks case study | A second real APK validates the workflow on a different AndroidX app profile. | 19 Maven SBOM components; source validation confirmed 19/19 versions; 0 mismatches; 0 missing. |
| Full expanded latest-only F-Droid stress test | Broad identity coverage without version calibration can produce version mismatches. | 26 Maven SBOM components; 12 confirmed; 13 version mismatches; 1 missing. |
| Clean OSV demo | A real calibrated APK can return no vulnerabilities after OSV lookup. | F-Droid demo returns 0 vulnerable components / 0 vulnerabilities. |
| Vulnerable OSV demo | The vulnerability layer works when a vulnerable Maven version is detected. | Jackson Databind `2.9.10.8` returns 3 confirmed HIGH advisories. |

## Demo Method For Supervisor Meeting

Run the demo from the project root in Docker.

### 1. Health Check

```powershell
docker compose run --rm apk-sbom pytest -q
```

Expected result:

```text
all tests pass
```

Latest Docker verification after the Lifecycle update: `63 passed`.

### 2. Clean Real APK Demo With OSV

```powershell
docker compose run --rm apk-sbom python -m apk_sbom.cli generate-report data/test_apks/real/F-Droid.apk --output-dir data/results/demo-osv-clean-fdroid --db-path data/reference_db/reference_features_calibrated_combined.sqlite --top 30
```

Open:

- `data/results/demo-osv-clean-fdroid/report.html`
- `data/results/demo-osv-clean-fdroid/report.md`
- `data/results/demo-osv-clean-fdroid/sbom.cdx.json`

Explain:

- The APK is multidex and includes native `.so` files, which are reported as hash-only file components.
- The report includes forensic indicators, manifest metadata, candidate reasons, identity confidence, version confidence, and obfuscation risk.
- OSV returned 0 vulnerabilities for the calibrated F-Droid emitted components.

### 3. Validate The Clean Real APK Against Source

```powershell
docker compose run --rm apk-sbom python -m apk_sbom.cli validate-source-deps --sbom data/results/demo-osv-clean-fdroid/sbom.cdx.json --dependency-tree data/results/source-validation/fdroid/app-fullReleaseRuntimeClasspath.txt --output-dir data/results/source-validation/demo-osv-clean-fdroid --candidate com.squareup.okio:okio@2.8.0
```

Open:

- `data/results/source-validation/demo-osv-clean-fdroid/source-validation.md`

Explain:

- `confirmed` means the emitted SBOM coordinate and selected version were found in the resolved Gradle dependency tree.
- The current calibrated F-Droid result confirms 23/23 emitted Maven components with 0 mismatches and 0 missing coordinates; OpenTracks confirms 19/19 with 0 mismatches and 0 missing.
- The optional `--candidate com.squareup.okio:okio@2.8.0` demonstrates that a suppressed overlapping candidate is checked separately and shown as a mismatch, not hidden.

### 4. Vulnerable APK Demo With OSV

```powershell
docker compose run --rm apk-sbom python -m apk_sbom.cli generate-report data/test_apks/controlled/controlled-com-fasterxml-jackson-core-jackson-databind-2.9.10.8-clear.apk --output-dir data/results/demo-osv-vulnerable-jackson-databind --db-path data/reference_db/reference_features.sqlite --top 10
```

Open:

- `data/results/demo-osv-vulnerable-jackson-databind/report.html`

Explain:

- The detected component is `com.fasterxml.jackson.core:jackson-databind@2.9.10.8`.
- OSV returns 3 confirmed HIGH advisories: `CVE-2020-36518`, `CVE-2022-42003`, and `CVE-2022-42004`.
- This shows the positive vulnerability path, while the F-Droid demo shows the clean/no-vulnerability path.

## What To Tell The Supervisor

The best short explanation is:

> The MVP is not using a hidden dependency list to print a report. It extracts bytecode features from the APK, compares them against DEX features generated from Maven artifacts, scores candidate libraries and versions, emits a CycloneDX SBOM with confidence/evidence, and queries OSV. For the real F-Droid and OpenTracks case studies, I then validate the generated SBOMs against source dependency trees. That validation confirms all emitted Maven components and versions in both cases.

Important limitations to state clearly:

- The reference DB controls what can be detected.
- Heavy R8, packing, dynamic loading, and commercial protectors are not fully solved.
- Native `.so` files are hashed and reported, not version-identified.
- The calibrated F-Droid result is a strong case study, not proof of universal accuracy on all APKs.
- Broad latest-only expansion improves identity discovery but cannot be used for exact version claims without calibration.

## Meeting Email Draft

Subject: Request for meeting to review APK-to-SBOM MVP results

Dear Professor,

I hope you are doing well.

I would like to request a meeting to present the current state of my PFE/master MVP on extracting SBOMs from compiled Android APKs.

The implementation now includes APK inspection, multidex DEX analysis, Maven reference database construction, bytecode feature matching, version confidence scoring, CycloneDX SBOM generation, OSV vulnerability lookup, Markdown/HTML reports, and source dependency validation for a real APK case study.

The main validated results are the calibrated F-Droid and OpenTracks case studies. F-Droid emits 23 Maven SBOM components and validates 23/23; OpenTracks emits 19 and validates 19/19. Both have 0 mismatches and 0 missing coordinates. I also prepared a paired OSV demo: one clean real APK with 0 vulnerabilities and one controlled vulnerable Jackson Databind APK where OSV returns 3 confirmed HIGH advisories.

I would like to show you the workflow, the generated reports, the evaluation results, and the code audit confirming that the reports are produced from bytecode/reference matching rather than manually forced outputs.

Please let me know when you would be available for a short review meeting.

Best regards,

[Your Name]

## Suggested Attachments Or Links

- `docs/evaluation/CODEBASE_AUDIT_AND_SUPERVISOR_BRIEF.md`
- `docs/evaluation/MVP_RESULTS_SUMMARY.md`
- `docs/evaluation/APK_TESTSET_INVENTORY.md`
- `docs/evaluation/CONTROLLED_EVALUATION.md`
- `docs/evaluation/EXPANDED_REFERENCE_DB.md`
- `data/results/demo-osv-clean-fdroid/report.html`
- `data/results/source-validation/demo-osv-clean-fdroid/source-validation.md`
- `data/results/demo-osv-vulnerable-jackson-databind/report.html`

## Final Audit Statement

The codebase is ready to present as an MVP with explicit scope boundaries. It should be presented as a modular static-analysis prototype backed by Android library-detection literature and SBOM standards. The strongest evidence is the combination of controlled fixtures, calibrated real-APK source validation, confidence-aware reporting, and the positive/negative OSV demonstrations.
