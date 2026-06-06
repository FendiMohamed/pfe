# Developer Runbook

## Current Status

The MVP scope is frozen. The first extraction, reference DB, and overlap matching slices are available:

```text
APK -> archive/DEX feature JSON -> Maven reference DB -> ranked overlap candidates
```

It detects:

- all `classes*.dex` files
- multidex status
- `AndroidManifest.xml`
- `resources.arsc`
- native libraries under `lib/<abi>/*.so`
- SHA-256 hashes
- APK forensic summary, including nonstandard DEX files, extraction-risk indicators, native ABI summary, and manifest package/version/SDK/permission hints when decodable
- DEX classes, methods, packages, opcode histograms, dependency edges, and string literals when Androguard is available
- reference library/version candidates using package, class, method, opcode, class dependency graph, string literal, and version-unique evidence
- per-library version decisions with confidence labels
- CycloneDX SBOM generation from real matcher decisions
- OSV vulnerability lookup for Maven components in the SBOM
- confirmed/potential vulnerability finding labels based on APK-side identity and version confidence
- OSV severity parsing and deduplication by OSV/GHSA/CVE identity
- final JSON/Markdown report generation
- native `.so` hash-only CycloneDX file components and report rows
- controlled clear/R8 fixture generation and evaluation

## Host Commands

Run CLI help:

```powershell
$env:PYTHONPATH='src'
python -m apk_sbom.cli --help
```

Inspect an APK:

```powershell
$env:PYTHONPATH='src'
python -m apk_sbom.cli inspect-apk data\test_apks\sample.apk
```

Analyze DEX features:

```powershell
$env:PYTHONPATH='src'
python -m apk_sbom.cli analyze-dex data\test_apks\sample.apk
```

Generate a mock CycloneDX SBOM:

```powershell
$env:PYTHONPATH='src'
python -m apk_sbom.cli generate-mock-sbom data\test_apks\sample.apk --output data\results\mock-sbom.cdx.json
```

Preview Maven reference downloads:

```powershell
$env:PYTHONPATH='src'
python -m apk_sbom.cli download-maven --config configs\libraries.json --dry-run
```

Resolve the 100+ coordinate reference catalog into a downloader config:

```powershell
$env:PYTHONPATH='src'
python -m apk_sbom.cli expand-reference-config --catalog configs\popular_android_maven_catalog.json --output configs\libraries.expanded.json --latest-count 1
```

Build the expanded reference DB in controlled batches:

```powershell
$env:PYTHONPATH='src'
python -m apk_sbom.cli download-maven --config configs\libraries.expanded.json --output-root data\reference_db\artifacts_expanded --limit 10 --offset 0 --quiet
python -m apk_sbom.cli convert-reference-dex --artifact-root data\reference_db\artifacts_expanded --output-root data\reference_db\dex_expanded --limit 10 --quiet
python -m apk_sbom.cli extract-reference-features --dex-root data\reference_db\dex_expanded --db-path data\reference_db\reference_features_expanded.sqlite --reset --quiet
```

For later batches, increase `--offset` on the download command by the batch size, then rerun conversion over the expanded artifact cache and feature extraction without `--reset`:

```powershell
$env:PYTHONPATH='src'
python -m apk_sbom.cli download-maven --config configs\libraries.expanded.json --output-root data\reference_db\artifacts_expanded --limit 10 --offset 10 --quiet
python -m apk_sbom.cli convert-reference-dex --artifact-root data\reference_db\artifacts_expanded --output-root data\reference_db\dex_expanded --quiet
python -m apk_sbom.cli extract-reference-features --dex-root data\reference_db\dex_expanded --db-path data\reference_db\reference_features_expanded.sqlite --quiet
```

Keep generated expanded artifacts under `data/reference_db/`, which is ignored by Git. The `--offset` option is also available on conversion and feature extraction for advanced/manual slicing, but the safest repeatable workflow is to let those stages revisit the local cache and skip or upsert existing records.

Current expanded batch progress has checked all artifact-version entries in `configs/libraries.expanded.json` through final offset `162`. The full expanded cache has 141 artifact records, 108 usable DEX components, 33 no-bytecode/metadata-only skips, and 0 failures. Use additional batch commands only after changing `configs/libraries.expanded.json` or adding new catalog entries.

Build the calibrated F-Droid reference slice:

```powershell
$env:PYTHONPATH='src'
python -m apk_sbom.cli download-maven --config configs\libraries.calibration.json --output-root data\reference_db\artifacts_calibration --quiet
python -m apk_sbom.cli convert-reference-dex --artifact-root data\reference_db\artifacts_calibration --output-root data\reference_db\dex_calibration --quiet
python -m apk_sbom.cli extract-reference-features --dex-root data\reference_db\dex_calibration --db-path data\reference_db\reference_features_calibration.sqlite --reset --quiet
python -m apk_sbom.cli extract-reference-features --dex-root data\reference_db\dex --db-path data\reference_db\reference_features_calibrated_combined.sqlite --reset --quiet
python -m apk_sbom.cli extract-reference-features --dex-root data\reference_db\dex_calibration --db-path data\reference_db\reference_features_calibrated_combined.sqlite --quiet
```

Run the calibrated F-Droid case study:

```powershell
$env:PYTHONPATH='src'
python -m apk_sbom.cli generate-report data\test_apks\real\F-Droid.apk --output-dir data\results\report-real-f-droid-calibrated-db --db-path data\reference_db\reference_features_calibrated_combined.sqlite --skip-osv --top 30
python -m apk_sbom.cli validate-source-deps --sbom data\results\report-real-f-droid-calibrated-db\sbom.cdx.json --dependency-tree data\results\source-validation\fdroid\app-fullReleaseRuntimeClasspath.txt --output-dir data\results\source-validation\fdroid-calibrated --candidate com.squareup.okio:okio@2.8.0
```

Download Maven reference artifacts:

```powershell
$env:PYTHONPATH='src'
python -m apk_sbom.cli download-maven --config configs\libraries.json
```

Preview reference DEX conversion:

```powershell
$env:PYTHONPATH='src'
python -m apk_sbom.cli convert-reference-dex --dry-run --limit 3
```

Convert downloaded reference artifacts to DEX once D8 is available:

```powershell
$env:PYTHONPATH='src'
python -m apk_sbom.cli convert-reference-dex
```

Extract reference DEX features into SQLite:

```powershell
$env:PYTHONPATH='src'
python -m apk_sbom.cli extract-reference-features --reset
```

Rank reference library versions for an APK using package/class/method/opcode evidence:

```powershell
$env:PYTHONPATH='src'
python -m apk_sbom.cli match-apk data\test_apks\sample.apk --top 10
```

Generate a CycloneDX SBOM from real matcher output:

```powershell
$env:PYTHONPATH='src'
python -m apk_sbom.cli generate-sbom data\test_apks\sample.apk --output data\results\sbom.cdx.json
```

Query OSV for Maven components in the generated SBOM:

```powershell
$env:PYTHONPATH='src'
python -m apk_sbom.cli scan-sbom-osv data\results\sbom.cdx.json --output data\results\osv-vulnerabilities.json
```

Use `--no-enrich` if you only want the querybatch response without fetching individual advisory aliases/summaries.

OSV results include both raw advisory counts and confidence-aware finding labels. Exact/high version evidence is reported as `confirmed`; low-confidence candidate versions are reported as `potential`.

Generate all report artifacts in one run:

```powershell
$env:PYTHONPATH='src'
python -m apk_sbom.cli generate-report data\test_apks\sample.apk --output-dir data\results\report
```

This writes `matches.json`, `sbom.cdx.json`, `report.json`, `report.md`, and `report.html`. Use `--skip-osv` for offline/local runs.

Validate a CycloneDX SBOM against a source dependency tree when source is available:

```powershell
$env:PYTHONPATH='src'
python -m apk_sbom.cli validate-source-deps --sbom data\results\report\sbom.cdx.json --dependency-tree data\results\source-validation\app-fullReleaseRuntimeClasspath.txt --output-dir data\results\source-validation\app
```

Build controlled Gson fixtures:

```powershell
$env:PYTHONPATH='src'
python scripts\build_controlled_apk.py --coordinate com.google.code.gson:gson --version 2.8.9 --variant clear
python scripts\build_controlled_apk.py --coordinate com.google.code.gson:gson --version 2.8.9 --variant r8-rename
python scripts\build_controlled_apk.py --coordinate com.google.code.gson:gson --version 2.8.9 --variant r8-shrink
```

Build the controlled multi-library multidex fixture:

```powershell
$env:PYTHONPATH='src'
python scripts\build_controlled_apk.py --coordinate com.google.code.gson:gson --version 2.8.9 --dependency commons-codec:commons-codec@1.16.1 --name controlled-multi-gson-2-8-9-commons-codec-1-16-1-clear-multidex --variant clear --multidex-mode file-per-class
```

Evaluate controlled reports:

```powershell
$env:PYTHONPATH='src'
python scripts\evaluate_controlled_reports.py
```

Compare simple baselines:

```powershell
$env:PYTHONPATH='src'
python scripts\evaluate_baselines.py
```

Run syntax check:

```powershell
python -m compileall src scripts tests
```

## Supervisor Demo

Use this section for a short, stable meeting demo. Do not rebuild the reference DB live; the calibrated DB is already built.

For the full graduation-day rehearsal sequence, open `docs/evaluation/GRADUATION_DEMO_REHEARSAL.md` first. It lists the clean F-Droid proof, vulnerable Jackson proof, K-9/Jitsi partial-boundary proofs, Simplify obfuscation limitation, and surprise-APK fallback wording.

Start from the workspace:

```powershell
cd "C:\Users\PC CABA DZ\Documents\pfe-final"
```

### Graduation-Day Arbitrary APK Fallback

Use this when someone gives you an APK that is not part of the prepared evaluation set. It runs offline by default and writes a small readiness summary alongside the normal report artifacts:

```powershell
python scripts\run_graduation_demo_report.py path\to\app.apk --output-dir data\results\graduation-demo\app
```

The wrapper is fail-soft by default for live demos: if the underlying report cannot be generated, it still writes `demo-readiness.json` and `demo-readiness.md` with the exception type, safe wording, and next steps, then exits successfully so the terminal demo remains explainable. Use `--strict-exit` when running it in automation and a failed report should return a non-zero status.

Docker equivalent:

```powershell
docker compose run --rm apk-sbom python scripts/run_graduation_demo_report.py path/to/app.apk --output-dir data/results/graduation-demo/app
```

Open these first:

```text
data/results/graduation-demo/app/demo-readiness.md
data/results/graduation-demo/app/report.html
data/results/graduation-demo/app/sbom.cdx.json
```

Optional OSV-enabled run, only when network access is available:

```powershell
python scripts\run_graduation_demo_report.py path\to\app.apk --output-dir data\results\graduation-demo\app-osv --query-osv
```

Source-validation-aware run, only when the matching source-validation artifact already exists:

```powershell
python scripts\run_graduation_demo_report.py path\to\app.apk --output-dir data\results\graduation-demo\app-source-aware --source-validation-json data\results\source-validation\app\source-validation.json
```

Safe wording for this path:

```text
This is an APK-only recovery report. I can show extracted evidence, candidate Maven components, native file hashes, and the generated CycloneDX SBOM. I will not claim source-validated recall unless I also provide a source-validation artifact for this APK/source pair.
```

If a live APK fails before report generation, use:

```text
The wrapper did not hide the failure. It wrote a readiness artifact with the exception type and message, so I can explain the input or environment boundary instead of pretending an SBOM was generated.
```

1. Prove the project is healthy:

```powershell
docker compose run --rm apk-sbom pytest -q
```

Expected result:

```text
63 passed
```

2. Generate the final calibrated F-Droid report with OSV enabled:

```powershell
docker compose run --rm apk-sbom python -m apk_sbom.cli generate-report data/test_apks/real/F-Droid.apk --output-dir data/results/report-real-f-droid-final-demo-osv --db-path data/reference_db/reference_features_calibrated_combined.sqlite --top 30
```

Expected OSV result for the current calibrated F-Droid SBOM:

```text
Vulnerable components: 0
Vulnerabilities: 0
```

If internet access or the OSV API is unavailable during the meeting, use the offline fallback by adding `--skip-osv` and writing to `data/results/report-real-f-droid-final-demo`.

3. Validate the generated SBOM against the F-Droid source dependency tree:

```powershell
docker compose run --rm apk-sbom python -m apk_sbom.cli validate-source-deps --sbom data/results/report-real-f-droid-final-demo-osv/sbom.cdx.json --dependency-tree data/results/source-validation/fdroid/app-fullReleaseRuntimeClasspath.txt --output-dir data/results/source-validation/fdroid-final-demo-osv --candidate com.squareup.okio:okio@2.8.0
```

Expected validation summary:

```text
SBOM components: 23
Confirmed: 23
Version mismatch: 0
Missing: 0
Extra candidate com.squareup.okio:okio@2.8.0: version-mismatch
```

Open these artifacts:

```text
data/results/report-real-f-droid-final-demo-osv/report.html
data/results/report-real-f-droid-final-demo-osv/report.md
data/results/report-real-f-droid-final-demo-osv/sbom.cdx.json
data/results/report-real-f-droid-final-demo-osv/osv-vulnerabilities.json
data/results/source-validation/fdroid-final-demo-osv/source-validation.md
docs/evaluation/APK_TESTSET_INVENTORY.md
```

Optional second real-APK proof, using OpenTracks:

```powershell
docker compose run --rm apk-sbom python -m apk_sbom.cli generate-report data/test_apks/real/opentracks/opentracks.apk --output-dir data/results/report-real-opentracks-calibrated-db --db-path data/reference_db/reference_features_calibrated_combined.sqlite --top 30
docker compose run --rm apk-sbom python -m apk_sbom.cli validate-source-deps --sbom data/results/report-real-opentracks-calibrated-db/sbom.cdx.json --dependency-tree data/results/source-validation/opentracks/fullReleaseRuntimeClasspath.txt --output-dir data/results/source-validation/opentracks-calibrated-db
```

Expected OpenTracks result:

```text
SBOM components: 19
Confirmed: 19
Version mismatch: 0
Missing: 0
OSV vulnerabilities: 0
```

Current batch artifacts for discussion:

```text
docs/evaluation/REAL_APK_CURRENT_BATCH_RESULTS.md
docs/evaluation/REAL_APK_CURRENT_PROOF_BUNDLE.md
data/results/report-real-newpipe-calibrated-db/report.html
data/results/source-validation/newpipe-calibrated-db/source-validation.md
data/results/report-real-tusky-calibrated-db/report.html
data/results/source-validation/tusky-calibrated-db/source-validation.md
data/results/report-real-conversations/report.html
data/results/source-validation/conversations-report-validation/source-validation.md
data/results/report-real-organic-maps-calibrated-db/report.html
data/results/report-real-termux-calibrated-db/report.html
```

Use NewPipe to show a realistic partial-version-mismatch proof bundle:

```powershell
docker compose run --rm apk-sbom python -m apk_sbom.cli generate-report data/test_apks/real/newpipe/newpipe.apk --output-dir data/results/report-real-newpipe-calibrated-db --db-path data/reference_db/reference_features_calibrated_combined.sqlite --top 30
docker compose run --rm -e GRADLE_USER_HOME=/app/data/source/.gradle-cache-newpipe -w /app/data/source/newpipe-0.28.5/source/org.schabi.newpipe_1010_src.tar.gz apk-sbom sh -c "/opt/gradle/bin/gradle --no-daemon :app:dependencies --configuration releaseRuntimeClasspath > /app/data/results/source-validation/newpipe/releaseRuntimeClasspath.txt 2> /app/data/results/source-validation/newpipe/gradle-error.log"
docker compose run --rm apk-sbom python -m apk_sbom.cli validate-source-deps --sbom data/results/report-real-newpipe-calibrated-db/sbom.cdx.json --dependency-tree data/results/source-validation/newpipe/releaseRuntimeClasspath.txt --output-dir data/results/source-validation/newpipe-calibrated-db
```

Expected current status:

```text
SBOM components: 11
Confirmed: 10
Version mismatch: 1
Missing: 0
OSV vulnerabilities: 0
```

Explain the remaining NewPipe mismatch carefully: Maven POM dependency metadata is now captured and stored in the reference DB path, and the focused Startup check distinguishes `startup-runtime@1.1.1` from `1.2.0` through their declared `androidx.annotation` dependency versions. The MVP has a conservative POM coherence tie-breaker, but it does not use that metadata alone to force the result because the earlier generic "choose newer near-tie" idea caused a false flip on `androidx.concurrent:concurrent-futures`.

Use Tusky as a clean but sparse source-validated case after Retrofit calibration:

```powershell
docker compose run --rm apk-sbom python -m apk_sbom.cli generate-report data/test_apks/real/tusky/tusky.apk --output-dir data/results/report-real-tusky-calibrated-db --db-path data/reference_db/reference_features_calibrated_combined.sqlite --top 30
docker compose run --rm apk-sbom python -m apk_sbom.cli validate-source-deps --sbom data/results/report-real-tusky-calibrated-db/sbom.cdx.json --dependency-tree data/results/source-validation/tusky/blueReleaseRuntimeClasspath.txt --output-dir data/results/source-validation/tusky-calibrated-db
```

Expected current status:

```text
SBOM components: 1
Confirmed: 1
Version mismatch: 0
Missing: 0
Confirmed: com.squareup.retrofit2:retrofit@3.0.0
```

Use Organic Maps and Termux as limitation/native-heavy evidence. They are useful to explain native hash-only reporting, not version-accurate native SBOM recovery:

```powershell
docker compose run --rm apk-sbom python -m apk_sbom.cli generate-report data/test_apks/real/organic-maps/organic-maps.apk --output-dir data/results/report-real-organic-maps-calibrated-db --db-path data/reference_db/reference_features_calibrated_combined.sqlite --top 30
docker compose run --rm apk-sbom python -m apk_sbom.cli generate-report data/test_apks/real/termux/termux.apk --output-dir data/results/report-real-termux-calibrated-db --db-path data/reference_db/reference_features_calibrated_combined.sqlite --top 30
```

Wikipedia Android is a source-validated partial-version-mismatch case. Reproduce it with:

```powershell
docker compose run --rm apk-sbom python -m apk_sbom.cli generate-report data/test_apks/real/wikipedia-android/wikipedia-android.apk --output-dir data/results/report-real-wikipedia-android --db-path data/reference_db/reference_features_calibrated_combined.sqlite --top 30
docker compose run --rm -e GRADLE_USER_HOME=/app/data/source/.gradle-cache-wikipedia apk-sbom sh -lc "rm -rf /tmp/wikipedia-source && mkdir -p /tmp/wikipedia-source /app/data/results/source-validation/wikipedia-android && tar -xzf /app/data/source/wikipedia-android/source.tar.gz -C /tmp/wikipedia-source && cd /tmp/wikipedia-source/org.wikipedia_50586_src.tar.gz && /opt/gradle/bin/gradle --no-daemon :app:dependencies --configuration fdroidReleaseRuntimeClasspath > /app/data/results/source-validation/wikipedia-android/fdroidReleaseRuntimeClasspath.txt 2> /app/data/results/source-validation/wikipedia-android/gradle-error.log"
docker compose run --rm apk-sbom python -m apk_sbom.cli validate-source-deps --sbom data/results/report-real-wikipedia-android/sbom.cdx.json --dependency-tree data/results/source-validation/wikipedia-android/fdroidReleaseRuntimeClasspath.txt --output-dir data/results/source-validation/wikipedia-android-report-validation
```

Expected current status:

```text
SBOM components: 13
Confirmed: 11
Version mismatch: 2
Missing: 0
OSV vulnerabilities: 0
```

Use `docs/evaluation/WIKIPEDIA_ANDROID_PROOF_BUNDLE.md`, `data/results/report-real-wikipedia-android/report.html`, and `data/results/source-validation/wikipedia-android-report-validation/source-validation.md` for the evidence.

Use Conversations as another source-validated partial-version-mismatch case with multidex, R8/minify, native libraries, and a source dependency tree:

```powershell
docker compose run --rm apk-sbom python -m apk_sbom.cli generate-report data/test_apks/real/conversations/conversations.apk --output-dir data/results/report-real-conversations --db-path data/reference_db/reference_features_calibrated_combined.sqlite --top 30
docker compose run --rm -e GRADLE_USER_HOME=/app/data/source/.gradle-cache-conversations apk-sbom sh -lc "rm -rf /app/data/source/conversations/extracted && mkdir -p /app/data/source/conversations/extracted /app/data/results/source-validation/conversations && tar -xf /app/data/source/conversations/source.tar.gz -C /app/data/source/conversations/extracted && cd /app/data/source/conversations/extracted/eu.siacs.conversations_4217704_src.tar.gz && /opt/gradle/bin/gradle --no-daemon dependencies --configuration conversationsFreeReleaseRuntimeClasspath > /app/data/results/source-validation/conversations/conversationsFreeReleaseRuntimeClasspath.txt 2> /app/data/results/source-validation/conversations/gradle-error.log"
docker compose run --rm apk-sbom python -m apk_sbom.cli validate-source-deps --sbom data/results/report-real-conversations/sbom.cdx.json --dependency-tree data/results/source-validation/conversations/conversationsFreeReleaseRuntimeClasspath.txt --output-dir data/results/source-validation/conversations-report-validation
```

Expected current status:

```text
SBOM components: 9
Confirmed: 6
Version mismatch: 2
Missing/artifact-family nuance: 1
OSV vulnerabilities: 0
```

Use `docs/evaluation/CONVERSATIONS_PROOF_BUNDLE.md`, `data/results/report-real-conversations/report.html`, and `data/results/source-validation/conversations-report-validation/source-validation.md` for the evidence. Explain that source-used `gson@2.13.1` calibration fixed one mismatch, while the remaining AndroidX near-ties are kept as honest limitations rather than forced by recency.

Explain these points:

- The input is only the compiled APK: `data/test_apks/real/F-Droid.apk`.
- The tool extracts DEX, manifest metadata, native files, forensic indicators, and bytecode features.
- It matches APK bytecode against a calibrated Maven reference DB.
- It separates component identity confidence from selected-version confidence.
- It emits a CycloneDX SBOM with evidence and confidence properties.
- It queries OSV for the 23 calibrated Maven components; the current result is 0 returned vulnerabilities.
- Source validation confirms all 23 emitted Maven component versions against F-Droid's resolved Gradle dependency tree.
- The suppressed `com.squareup.okio:okio@2.8.0` candidate is intentionally shown as a mismatch to prove the final SBOM avoided that old weak candidate.
- `docs/evaluation/APK_TESTSET_INVENTORY.md` explains the APK testset ground truth, including controlled fixture packages/versions, F-Droid source-confirmed versions, R8/obfuscation notes, multidex/native details, and FP/FN comparison fields.

### OSV Positive And Negative Demo

Use these two reports when you want to prove that the OSV layer can show both outcomes.

Negative/clean case, using the calibrated real F-Droid APK:

```powershell
docker compose run --rm apk-sbom python -m apk_sbom.cli generate-report data/test_apks/real/F-Droid.apk --output-dir data/results/demo-osv-clean-fdroid --db-path data/reference_db/reference_features_calibrated_combined.sqlite --top 30
docker compose run --rm apk-sbom python -m apk_sbom.cli validate-source-deps --sbom data/results/demo-osv-clean-fdroid/sbom.cdx.json --dependency-tree data/results/source-validation/fdroid/app-fullReleaseRuntimeClasspath.txt --output-dir data/results/source-validation/demo-osv-clean-fdroid --candidate com.squareup.okio:okio@2.8.0
```

If Docker is unavailable, use the already regenerated final clean report at `data/results/report-real-f-droid-final-demo-osv/`; the separate `demo-osv-clean-fdroid` folder may need refreshing.

Expected result:

```text
Detected Maven components: 23
OSV vulnerable components: 0
OSV vulnerabilities: 0
Source validation: 23/23 confirmed, 0 mismatches, 0 missing
```

Positive/vulnerable case, using the controlled Jackson APK:

```powershell
docker compose run --rm apk-sbom python -m apk_sbom.cli generate-report data/test_apks/controlled-com-fasterxml-jackson-core-jackson-databind-2.9.10.8-clear.apk --output-dir data/results/demo-osv-vulnerable-jackson-databind --db-path data/reference_db/reference_features.sqlite --top 10
```

Expected result:

```text
Detected Maven components: 1
OSV vulnerable components: 1
OSV vulnerabilities: 3 confirmed HIGH
CVE-2020-36518, CVE-2022-42003, CVE-2022-42004
```

Open these paired artifacts:

```text
data/results/demo-osv-clean-fdroid/report.html
data/results/demo-osv-clean-fdroid/osv-vulnerabilities.json
data/results/source-validation/demo-osv-clean-fdroid/source-validation.md
data/results/demo-osv-vulnerable-jackson-databind/report.html
data/results/demo-osv-vulnerable-jackson-databind/osv-vulnerabilities.json
```

For real APKs, regenerate the source-validation-aware OSV triage before making vulnerability claims:

```powershell
python scripts\build_osv_source_validation_triage.py
```

The generated `docs/evaluation/OSV_SOURCE_VALIDATION_TRIAGE.md` separates `source-confirmed` advisories from `source-version-mismatch` and `report-only` advisories. Treat only the source-confirmed rows as source-validated vulnerability evidence; mismatch and report-only rows are useful scanner signals, not final vulnerability conclusions.

When a report already has a matching source-validation artifact, regenerate it with source-aware vulnerability labels:

```powershell
docker compose run --rm apk-sbom python -m apk_sbom.cli generate-report data/test_apks/real/osmand/osmand.apk --output-dir data/results/report-real-osmand --db-path data/reference_db/reference_features_calibrated_combined.sqlite --top 30 --source-validation-json data/results/source-validation/osmand-report-validation/source-validation.json
```

This writes `source-confirmed`, `source-version-mismatch`, `source-missing`, or `not-source-validated` fields into `osv-vulnerabilities.json` and exposes the same caveat in `report.md` and `report.html`.

### Real APK Dataset Growth

Regenerate the real APK candidate matrix and first-batch proof checklists:

```powershell
python scripts\build_real_apk_candidate_matrix.py
python scripts\scaffold_real_apk_proof.py
```

Regenerate the dataset criteria coverage matrix:

```powershell
python scripts\build_dataset_coverage_matrix.py
```

Open these planning artifacts:

```text
docs/evaluation/REAL_APK_CANDIDATES.md
docs/evaluation/REAL_APK_PROOF_BUNDLE_PLAN.md
docs/evaluation/DATASET_COVERAGE_MATRIX.md
data/results/evaluation/real-apk-proof/index.md
```

Admission rule: F-Droid, OpenTracks, Tusky, Daily Dozen, and QuickDic are clean source-validated cases, with Tusky, Daily Dozen, and QuickDic labeled as sparse. NewPipe, AntennaPod, KDE Connect, Wikipedia Android, Conversations, Aegis Authenticator, Markor, Nextcloud Android, FairEmail, VLC, OsmAnd, Material Files, Jitsi Meet, K-9/Thunderbird Android, Cryptomator Lite, Easy Xkcd, MoneyWallet, Foxy Droid, and the admitted no-native clean-candidate partial rows are source-validated partial-version-mismatch cases. Do not count native-heavy limitations, hidden-code limitations, or report-only/no-Maven-signal clean-candidate rows as source-validated accuracy cases until the per-app proof checklist contains the APK hash, source tag/commit, dependency tree, generated report, and source-validation output.

K-9 / Thunderbird Android `18.0` is now source-validated partial: APK/source/report/version-catalog proof exists, the report emits 11 Maven components plus 8 native file components with OSV 0, and the plugin-lite/runtime-graph validation copy generated `fossReleaseRuntimeClasspath`. Source validation at `data/results/source-validation/k9-thunderbird-android-report-validation/source-validation.md` confirms 5/11 emitted Maven versions, with 6 mismatches and 0 missing. Use `docs/evaluation/K9_THUNDERBIRD_PROOF_BUNDLE.md` and `docs/evaluation/K9_BLOCKER_DIAGNOSTICS.md` as the evidence notes; do not present K-9 as clean because the dependency tree was captured from a validation-only included-build reduction.

FairEmail `1.2315` is a source-validated partial-version-mismatch case for Java/Kotlin Maven dependencies: APK/source/report proof exists, the report emits 13 Maven components plus 4 native `libfairemail.so` file components with OSV 0, and validation confirms 7/13 emitted Maven versions with 6 AndroidX version mismatches and 0 missing coordinates. The original source Gradle run still tries to install Android NDK `27.2.12479018`, so the dependency tree was generated from `data/results/source-validation/fairemail/source-no-native/`, a validation-only source copy with native build disabled only for Maven runtime dependency resolution. Use `docs/evaluation/FAIREMAIL_PROOF_BUNDLE.md`, `data/results/report-real-fairemail/report.html`, and `data/results/source-validation/fairemail-report-validation/source-validation.md` for the evidence; do not claim native build validation.

Aegis Authenticator `3.4.2` is a completed source-validation proof but not a clean case: the report emits 7 Maven components plus 8 native barcode-scanning file components with OSV 0, and source validation confirms 6/7 versions with 1 mismatch and 0 missing after adding source-used `androidx.lifecycle:lifecycle-runtime-android@2.9.0` to calibration. Use `docs/evaluation/AEGIS_AUTHENTICATOR_PROOF_BUNDLE.md`, `data/results/report-real-aegis-authenticator/report.html`, and `data/results/source-validation/aegis-authenticator-report-validation/source-validation.md` for the evidence. The remaining mismatch is `androidx.viewpager2:viewpager2` selected `1.0.0` while source resolves `1.1.0`; do not force it with a generic newer-version rule.

Markor `2.16.1` is a completed source-validation proof but not a clean shared-DB case: the normal report emits 19 Maven components with OSV 0, and source validation confirms 7/19 versions with 12 mismatches and 0 missing after the guarded `androidx.core:core@1.9.0` promotion. Use `docs/evaluation/MARKOR_PROOF_BUNDLE.md`, `data/results/report-real-markor/report.html`, and `data/results/source-validation/markor-report-validation/source-validation.md` for the shared-DB evidence. A targeted source-used-version calibration experiment improves Markor to 19/19 and is preserved under `data/results/report-real-markor-source-calibrated/` and `data/results/source-validation/markor-source-calibrated/`, but the broader older-version set was not kept globally because it regressed newer controls. Markor is useful evidence that reference coverage can fix exact versioning, but only with app-era or dependency-coherence safeguards.

API/member-reference fingerprints are available but disabled by default. DEX analysis and reference extraction now store invoked/field member references in `api_references`, and `match-apk` accepts `--api-reference-weight`. Keep the weight at `0.0` for official calibrated reports until the reference DB is rebuilt with this feature and regression-tested against the clean and partial real APK baselines.

Opcode tri-grams are available but disabled by default. The experiment DB at `data/reference_db/reference_features_calibrated_combined_opcode_ngrams.sqlite` stores `opcode_ngrams`, and `match-apk`/`generate-report` accept `--opcode-ngram-weight`. A clean `0.02` weight matrix in `data/results/experiments/opcode-ngram-weight/` regressed OpenTracks and Conversations without improving the remaining risky ties, so keep the weight at `0.0` for official calibrated reports.

AntennaPod `3.11.4` is a completed source-validation proof but not a clean case: the report emits 20 Maven components plus 4 native `libconscrypt_jni.so` file components with OSV 0, and source validation confirms 19/20 versions with 1 mismatch and 0 missing. Use `docs/evaluation/ANTENNAPOD_PROOF_BUNDLE.md`, `data/results/report-real-antennapod/report.html`, and `data/results/source-validation/antennapod-report-validation/source-validation.md` for the evidence. The remaining mismatch is `androidx.core:core` selected `1.15.0` while source resolves `1.16.0`; do not force it with a generic newer-version rule.

KDE Connect `1.35.5` is a completed source-validation proof but not a clean case: the report emits 9 Maven components plus 4 native `libandroidx.graphics.path.so` file components with OSV 0, and source validation confirms 8/9 versions with 1 mismatch and 0 missing after scoped Lifecycle artifact-family coherence. Use `docs/evaluation/KDE_CONNECT_PROOF_BUNDLE.md`, `data/results/report-real-kde-connect/report.html`, and `data/results/source-validation/kde-connect-validation/source-validation.md` for the evidence. The remaining mismatch is `androidx.viewpager2:viewpager2` selected `1.1.0` while source resolves `1.1.0-beta02`; keep this as honest metadata-coherence evidence rather than forcing recency.

Wikipedia Android `r/50586-r-2026-05-12` is a completed source-validation proof but not a clean case: the report emits 13 Maven components plus 8 native file components with OSV 0, and source validation confirms 11/13 versions with 2 mismatches and 0 missing after adding source-used Gson/OkHttp Android calibration and generic OkHttp artifact-family disambiguation. Use `docs/evaluation/WIKIPEDIA_ANDROID_PROOF_BUNDLE.md`, `data/results/report-real-wikipedia-android/report.html`, and `data/results/source-validation/wikipedia-android-report-validation/source-validation.md` for the evidence. The remaining mismatches are `androidx.startup:startup-runtime` selected `1.1.1` vs source `1.2.0`, and `androidx.viewpager2:viewpager2` selected `1.0.0` vs source `1.1.0`; keep them as honest near-version ambiguity.

Hidden DEX limitation fixture:

```powershell
python scripts/build_limitation_apk.py
docker compose run --rm apk-sbom python -m apk_sbom.cli inspect-apk data/test_apks/limitation/controlled-hidden-dex-loader-limitation.apk
docker compose run --rm apk-sbom python -m apk_sbom.cli generate-report data/test_apks/limitation/controlled-hidden-dex-loader-limitation.apk --output-dir data/results/report-limitation-hidden-dex-loader --db-path data/reference_db/reference_features_calibrated_combined.sqlite --top 30
```

Expected limitation behavior:

```text
Extraction risk: medium
Obfuscation risk: high
DEX files analyzed: 0
DEX files failed: 2
Detected Maven components: 0
Native file components: 1
Indicators: nonstandard-dex, tiny-primary-dex, protector-name-hint, large-opaque-assets
```

Use `docs/evaluation/HIDDEN_DEX_LIMITATION_FIXTURE.md` and `data/results/report-limitation-hidden-dex-loader/report.html` to show that the MVP warns and avoids overclaiming when dynamic/protected-style packaging is detected.

Current coverage-matrix result: 19 criteria tracked, with 0 missing and 0 weak rows. The controlled multidex and controlled multi-library gaps are covered by `data/test_apks/controlled-multi-gson-2-8-9-commons-codec-1-16-1-clear-multidex.apk`, and the heavy obfuscation/protector limitation criterion is covered by `data/test_apks/limitation/controlled-hidden-dex-loader-limitation.apk`.

Load the initial Maven library config:

```powershell
$env:PYTHONPATH='src'
python -c "from apk_sbom.reference_config import load_libraries_config; print([lib.coordinate for lib in load_libraries_config('configs/libraries.json')])"
```

Run toolchain audit:

```powershell
python scripts/check_toolchain.py
```

The host audit currently fails because required Python packages are not installed on Windows. This is expected until the Docker runtime is built.

## Docker Commands

Validate Compose syntax:

```powershell
docker compose config
```

After Docker Desktop is running:

```powershell
docker info
docker compose build
docker compose run --rm apk-sbom python scripts/check_toolchain.py
docker compose run --rm apk-sbom python -m apk_sbom.cli analyze-dex data/test_apks/sample.apk
docker compose run --rm apk-sbom python -m apk_sbom.cli generate-mock-sbom data/test_apks/sample.apk --output data/results/mock-sbom.cdx.json
docker compose run --rm apk-sbom python -m apk_sbom.cli expand-reference-config --catalog configs/popular_android_maven_catalog.json --output configs/libraries.expanded.json --latest-count 1
docker compose run --rm apk-sbom python -m apk_sbom.cli download-maven --config configs/libraries.expanded.json --output-root data/reference_db/artifacts_expanded --limit 10 --offset 0 --quiet
docker compose run --rm apk-sbom python -m apk_sbom.cli convert-reference-dex --artifact-root data/reference_db/artifacts_expanded --output-root data/reference_db/dex_expanded --limit 10 --quiet
docker compose run --rm apk-sbom python -m apk_sbom.cli extract-reference-features --dex-root data/reference_db/dex_expanded --db-path data/reference_db/reference_features_expanded.sqlite --reset --quiet
docker compose run --rm apk-sbom python -m apk_sbom.cli download-maven --config configs/libraries.json --dry-run
docker compose run --rm apk-sbom python -m apk_sbom.cli convert-reference-dex --dry-run --limit 3
docker compose run --rm apk-sbom python -m apk_sbom.cli extract-reference-features --reset
docker compose run --rm apk-sbom python -m apk_sbom.cli match-apk data/test_apks/sample.apk --top 10
docker compose run --rm apk-sbom python -m apk_sbom.cli generate-sbom data/test_apks/sample.apk --output data/results/sbom.cdx.json
docker compose run --rm apk-sbom python -m apk_sbom.cli scan-sbom-osv data/results/sbom.cdx.json --output data/results/osv-vulnerabilities.json
docker compose run --rm apk-sbom python -m apk_sbom.cli generate-report data/test_apks/sample.apk --output-dir data/results/report --skip-osv
docker compose run --rm apk-sbom python -m apk_sbom.cli validate-source-deps --sbom data/results/report/sbom.cdx.json --dependency-tree data/results/source-validation/app-fullReleaseRuntimeClasspath.txt --output-dir data/results/source-validation/app
docker compose run --rm apk-sbom python scripts/build_controlled_apk.py --coordinate com.google.code.gson:gson --version 2.8.9 --variant clear
docker compose run --rm apk-sbom python scripts/build_controlled_apk.py --coordinate com.google.code.gson:gson --version 2.8.9 --variant r8-rename
docker compose run --rm apk-sbom python scripts/build_controlled_apk.py --coordinate com.google.code.gson:gson --version 2.8.9 --variant r8-shrink
docker compose run --rm apk-sbom python scripts/evaluate_controlled_reports.py
docker compose run --rm apk-sbom python scripts/evaluate_baselines.py
```

## External Scanner Validation

External scanner comparison is optional but now reproducible in the Docker runtime for CycloneDX CLI, Trivy, and Grype. Regenerate the readiness artifact with:

```powershell
docker compose run --rm apk-sbom python scripts/build_external_scanner_validation_status.py --environment docker-apk-sbom
```

Run the selected SBOM scanner comparison with:

```powershell
docker compose run --rm apk-sbom python scripts/run_external_scanner_validation.py --timeout 600
```

The generated `docs/evaluation/EXTERNAL_SCANNER_VALIDATION_STATUS.md` checks `cyclonedx`, `cyclonedx-cli`, Trivy, Grype, Syft, cdxgen, and the support runtimes used to install some of them. The current status is `scanner-ready`: all 6 scanner tools are available. Dotnet remains optional and missing because the standalone CycloneDX CLI binary is used. The scanner-run evidence is `docs/evaluation/EXTERNAL_SCANNER_VALIDATION.md`.

## Next Implementation Step

After the full expanded DB build and F-Droid smoke validation, run full verification and choose one of:

```text
package the current MVP results for the thesis/paper
expand another calibrated real-APK case study
optional SBOM validation/scanner integration when cyclonedx-cli, Trivy, Grype, Syft, or cdxgen is installed
```

Expected first DEX feature output:

```json
{
  "dex_files_analyzed": 2,
  "classes_count": 1234,
  "methods_count": 9876,
  "packages": ["okhttp3", "retrofit2", "com.google.gson"]
}
```
