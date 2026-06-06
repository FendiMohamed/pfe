# Real APK Blocker Rescue Workflow

This workflow turns repeated source-linked Gradle blockers into bounded,
documented rescue lanes. It does not change matcher scoring, selected Maven
versions, SBOM component selection, vulnerability labels, reference DB
contents, or source-validated metrics.

## Policy

Blocked APKs are build-system evidence, not matcher failures. A row can move
into source-validated metrics only after all of these artifacts exist:

- APK hash and identity evidence;
- matching source tarball, tag, or commit evidence;
- resolved runtime Gradle dependency tree;
- generated APK-SBOM report;
- `validate-source-deps` output.

If a rescue lane cannot produce the dependency tree, keep the APK in
`source-linked-blocked`, `report-only`, or `limitation` buckets.

## Repeated Blocker Classes

| Class | Typical symptom | Rescue lane | Metric rule |
|---|---|---|---|
| Modern Android plugin/configuration blocker | `compileSdkVersion is not specified`, Gradle plugin API mismatch | validation copy that preserves runtime dependencies and fixes only configuration blockers | count only after runtime tree and source validation |
| Legacy Gradle/JDK blocker | old AGP, JCenter-era wiring, incompatible modern Gradle | JDK 11 plus Gradle 5/6 style lane; patch `sdk.dir`/repository wiring only when needed | count only after validation output |
| Cordova Gradle blocker | Cordova `cordova.gradle` script failure such as `XmlParser` | Cordova validation-copy lane that only reaches runtime dependency resolution | keep blocked if Cordova script cannot expose runtime tree |
| React Native/framework blocker | Node/npm/prebuild/native toolchain needed before Gradle configuration | framework-boundary lane with explicit Node/native prerequisites | keep as framework-blocked unless tree completes |
| Included build-plugin blocker | included Gradle build logic stalls before app module runtime config | repository-order/plugin-isolation bounded retry | keep blocked if included build remains unresolved |
| Native/NDK build blocker | NDK install or native CMake setup blocks dependency tree | validation-only no-native copy when Java/Kotlin runtime deps are unaffected | count Maven deps only; do not claim native build validation |
| Wrong module or variant configuration | generic probes miss real app module or flavor-prefixed runtime configuration | strict module/config profile first; validation copy only if configuration itself then fails | count only after runtime tree and source validation |

## Current Assignments

The active rescue profile config is:

```text
configs/real_apk_blocker_rescue_profiles.json
```

OpenCloud is the first completed test case. Its original blocker was a modern
Gradle/plugin configuration failure around `org/gradle/api/internal/HasConvention`
and `compileSdkVersion is not specified` while configuring `:opencloudApp`. The
rescue lane creates a validation-only source copy, disables KSP/Kotlin/Parcelize
and Detekt/Sonar build-time plugins only for dependency-tree capture, preserves
runtime dependency declarations, and probes the real app configurations:

```text
:opencloudApp:dependencies --configuration originalReleaseRuntimeClasspath
:opencloudApp:dependencies --configuration qaReleaseRuntimeClasspath
:opencloudApp:dependencies --configuration originalDebugRuntimeClasspath
:opencloudApp:dependencies --configuration qaDebugRuntimeClasspath
```

The completed OpenCloud rescue captured `originalReleaseRuntimeClasspath` and
validated 8/22 emitted Maven versions, so OpenCloud is admitted as
source-validated partial evidence.

Waistline is the first completed Cordova lane test case. The rescue lane clones
only `platforms/android`, adds Docker Android SDK `local.properties`, imports
Cordova's Groovy `XmlParser`, aligns Cordova build-tools metadata with Docker
build-tools 36.0.0, replaces the plugin `jcenter()` repository call with the
archived Maven URL, and probes the real app configurations:

```text
:app:dependencies --configuration releaseRuntimeClasspath
:app:dependencies --configuration debugRuntimeClasspath
```

The completed Waistline rescue captured `releaseRuntimeClasspath` and validated
9/15 emitted Maven versions, so Waistline is admitted as source-validated
partial evidence.

The v14 blocker rescue closed three later blocked rows. Baby Books used an
Android-module-only validation copy that pins `:android` and captures
`releaseRuntimeClasspath`, validating 10/29 emitted Maven versions. Odysee used
a Cordova validation copy with Docker SDK metadata and `XmlParser`
compatibility, validating 10/15 emitted Maven versions from `:app`
`releaseRuntimeClasspath`. RadarWeather used an old-AGP validation copy with
AGP-required namespace/BuildConfig settings, validating 5/17 emitted Maven
versions from `:app` `releaseRuntimeClasspath`.

Poet Assistant is now resolved through the JCenter-to-Maven-Central validation
copy lane. The validation copy preserves declared runtime dependencies, replaces
removed `jcenter()` repository method calls only for dependency-tree capture,
and validates 7/37 emitted Maven versions from `:app` `releaseRuntimeClasspath`.

K-9 is now resolved through the included build-plugin lane. Jitsi is now
resolved through the React Native/framework lane. The v15 source-linked blocked
rows are also resolved: Ultrasonic through strict `:ultrasonic` probing,
RunnerUp through strict `latestReleaseRuntimeClasspath` flavor probing, and
ImapNotes3 through strict `:ImapNotes3` probing. The reusable rescue lane for
similar future blockers is strict module/config probing:

```text
:ImapNotes3:dependencies --configuration releaseRuntimeClasspath
:ultrasonic:dependencies --configuration releaseRuntimeClasspath
:app:dependencies --configuration latestReleaseRuntimeClasspath
:passwordmaster:dependencies --configuration releaseRuntimeClasspath
```

For the v15 rows, those strict probes succeeded and produced source-validation
output: Ultrasonic 12/39, RunnerUp 16/39, and ImapNotes3 11/39 confirmed emitted
Maven versions. Password Master from v16 was also resolved by strict
`:passwordmaster` probing and validated 13/18 emitted Maven versions.

The current v16 source-linked blocked rows are Flying Carpet and FitoTrack.
Both have APK/source/report evidence, but Docker proof did not capture a runtime
dependency tree after 60 attempted configurations. Their shared failure class is
modern Gradle/toolchain configuration, including
`org/gradle/api/artifacts/SelfResolvingDependency`; FitoTrack also reports
`compileSdkVersion is not specified`. If strict probes fail or no better app
module/configuration exists, use validation-only copies that preserve runtime
dependency declarations and disable only the build-time configuration that
blocks dependency-tree capture. Keep both rows blocked until dependency-tree
capture and `validate-source-deps` succeed.

## Run Pattern

For a targeted retry:

```powershell
docker compose run --rm apk-sbom python scripts/advance_real_apk_batch_proofs.py --batch-json data/results/evaluation/clean-real-apk-candidate-sweep-v11.json --source-root data/source/csv11 --validation-root data/results/source-validation/csv11 --output-json data/results/evaluation/clean-real-apk-candidate-sweep-v11-opencloud-rescue-status.json --output-doc docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_STATUS_V11_OPENCLOUD_RESCUE.md --attempt-gradle --continue-on-error --slug opencloud --skip-download --skip-extract --gradle-timeout 180
```

The Waistline Cordova retry used:

```powershell
docker compose run --rm apk-sbom python scripts/advance_real_apk_batch_proofs.py --batch-json data/results/evaluation/clean-real-apk-candidate-sweep-v11.json --source-root data/source/csv11 --validation-root data/results/source-validation/csv11 --output-json data/results/evaluation/clean-real-apk-candidate-sweep-v11-waistline-rescue-status.json --output-doc docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_STATUS_V11_WAISTLINE_RESCUE.md --attempt-gradle --continue-on-error --slug waistline --skip-download --skip-extract --gradle-timeout 480
```

After a successful dependency tree, the proof runner invokes
`validate-source-deps` automatically and writes source-validation artifacts
under the row validation directory.

## Interpretation

A successful rescue is source-validation evidence, not a production tool
change. A failed rescue is still useful if it records:

- the blocker class;
- the validation-only edits attempted;
- the exact Gradle task/configuration;
- timeout or failure logs;
- why the row remains outside metrics.
