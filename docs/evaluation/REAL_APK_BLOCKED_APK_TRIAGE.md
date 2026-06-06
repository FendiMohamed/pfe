# Real APK Blocked APK Triage

Generated on 2026-06-06.

This note consolidates the remaining `source-linked-blocked` APK rows so the
next rescue pass can target repeated build-system issues instead of rediscovering
them from scattered proof logs. Primitive FTPd, DoliDroid, RadioDroid,
OpenKeychain, SimpleLogin, Omni Notes, ownCloud, Jitsi Meet, and K-9 /
Thunderbird Android were part of the original 9-row blocked set; Baby Books,
Odysee, and RadarWeather were the later v14 blocked rows. All of those are now
resolved as source-validated partial evidence. v15 later added three blocked
rows, Ultrasonic, RunnerUp, and ImapNotes3; strict module/flavor rescue profiles
also resolved those rows as source-validated partial evidence. v16 added two
current blocked rows, Flying Carpet and FitoTrack, after APK/source/report proof
succeeded but runtime dependency-tree capture failed. This note does not change
matcher scoring, selected versions, SBOM output, vulnerability labels, reference
DB contents, or source-validated metrics.

## Current Blocked Set

The canonical remaining blocked set is:

| APK | Proof status | Current blocker |
|---|---|---|
| Flying Carpet 9.0.8 | `source-linked-blocked` | APK/source/report evidence exists, but 60 attempted runtime configurations failed before dependency-tree capture. The visible failure signature includes `org/gradle/api/artifacts/SelfResolvingDependency`. |
| FitoTrack 15.6 | `source-linked-blocked` | APK/source/report evidence exists, but 60 attempted runtime configurations failed before dependency-tree capture. The visible failure signatures include `org/gradle/api/artifacts/SelfResolvingDependency` and `compileSdkVersion is not specified`. |

All rows from the original blocker triage, the later v14 blocker set, and the
v15 blocker set have resolved runtime dependency trees and `validate-source-deps`
outputs. Flying Carpet and FitoTrack are current v16 blockers and remain
excluded from source-validated metrics.

## Existing Prior Work Found

`docs/evaluation/REAL_APK_BLOCKER_RESCUE_WORKFLOW.md` already defines rescue
profiles for the blocked rows, including the now-resolved Jitsi and K-9 lanes.
It also documents two successful precedents:
OpenCloud for modern Gradle/plugin configuration rescue and Waistline for a
Cordova validation-copy rescue. The files below add per-APK evidence but did not
previously consolidate all 9 original blocked rows into one fix-oriented table:

- `docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_RESULTS_V9.md`
- `docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_STATUS_V9.md`
- `docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_RESULTS_V10.md`
- `docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_STATUS_V10.md`
- `docs/evaluation/CLEAN_REAL_APK_CANDIDATE_PROOF_STATUS_V15.md`
- `docs/evaluation/K9_BLOCKER_DIAGNOSTICS.md`
- `docs/evaluation/JITSI_MEET_PROOF_BUNDLE.md`
- `docs/evaluation/APK_TYPE_EVALUATION.md`

## Fix-Oriented Categories

| Category | APKs | Shared symptom | Likely rescue lane |
|---|---|---|---|
| Removed `jcenter()` method under modern Gradle | DoliDroid, RadioDroid, and OpenKeychain resolved | `Could not find method jcenter() for arguments [] on repository container` | Validation copy that replaces `jcenter()` with Maven Central first, and only uses archived JCenter URL if a dependency is still missing. Then retry the real app runtime configuration. DoliDroid validated at 7/14; RadioDroid validated at 5/39 through the same lane plus Gradle 8.13; OpenKeychain validated at 5/12 after adding missing wrapper settings and AGP-required properties. |
| Modern Gradle or plugin internal API removal | SimpleLogin, Omni Notes, and ownCloud resolved | `org/gradle/util/ConfigureUtil`; `org.gradle.api.artifacts.SelfResolvingDependency`; `org/gradle/api/internal/HasConvention`; Kotlin build flow isolation errors | Validation copy that disables build-time analysis plugins or uses the source wrapper-compatible Gradle lane only for dependency-tree capture. Preserve runtime `implementation` / `api` declarations. SimpleLogin validated after a Detekt-only validation copy plus Docker Gradle 8.13; Omni Notes validated after disabling SonarQube/test-logger/Jacoco analysis wiring and pinning `:omniNotes`; ownCloud validated after disabling Kotlin/KSP/Parcelize/Ktlint/Detekt/Sonar/CycloneDX build-time wiring and pinning `:owncloudApp`. |
| Wrong module/root probing | Primitive FTPd, Ultrasonic, and ImapNotes3 resolved | Generic runner tried root, `:app`, `:mobile`, and `:main`, but source modules are `:primitiveFTPd`, `:ultrasonic`, or `:ImapNotes3` | Primitive FTPd was resolved by adding a strict profile for `:primitiveFTPd:dependencies`; Docker captured `releaseRuntimeClasspath` and source validation confirmed 12/38 emitted Maven versions. Ultrasonic and ImapNotes3 were later resolved by strict `:ultrasonic:dependencies` and `:ImapNotes3:dependencies` profiles, validating 12/39 and 11/39 emitted Maven versions. |
| Variant/configuration probing | RunnerUp resolved | `:app` exists, but generic `releaseRuntimeClasspath` and common flavor names missed the actual app variant; stdout configured `:app` but stderr reports `configuration 'releaseRuntimeClasspath' not found in configuration container for project ':app'` | RunnerUp was resolved with a strict `:app:dependencies --configuration latestReleaseRuntimeClasspath` profile, validating 16/39 emitted Maven versions. |
| Included build-plugin blocker | K-9 / Thunderbird Android resolved | Included `build-plugin` setup stalls or fails before `fossReleaseRuntimeClasspath` | Resolved by a validation-only plugin-lite/runtime-graph copy that preserves `app-k9mail` `fossReleaseRuntimeClasspath`; validation confirms 5/11 emitted Maven versions. |
| React Native/framework toolchain blocker | Jitsi Meet (resolved) | Earlier Gradle-compatible attempt reached React Native setup then failed because `node` was missing. | Resolved after the Docker validation runtime had Node/npm available and Gradle 8.13 captured `:app` `releaseRuntimeClasspath`; source validation confirmed 5/7 emitted Maven versions. |
| Android module/root probing blocker | Baby Books resolved | Generic module probing reached unrelated frontend modules and modern Gradle hit removed APIs before the Android runtime tree. | Resolved by a validation-only copy that pins `:android` and `:library`, adds Docker SDK metadata, and captures `releaseRuntimeClasspath`; validation confirms 10/29 emitted Maven versions. |
| Cordova Gradle blocker | Odysee resolved | Cordova Android Gradle script failed on Groovy `XmlParser` compatibility before runtime tree capture. | Resolved by a Cordova validation copy that adds Docker SDK metadata and `XmlParser` compatibility, then captures `:app` `releaseRuntimeClasspath`; validation confirms 10/15 emitted Maven versions. |
| Old AGP/modern Gradle blocker | RadarWeather resolved | AGP 7.1.1 build logic used Gradle APIs removed by modern Gradle before `:app` runtime tree capture. | Resolved by a validation-only old-AGP copy that upgrades the validation path, adds namespace/BuildConfig settings, and captures `:app` `releaseRuntimeClasspath`; validation confirms 5/17 emitted Maven versions. |
| v16 Gradle internal API/configuration blocker | Flying Carpet and FitoTrack current | `org/gradle/api/artifacts/SelfResolvingDependency`; FitoTrack also reports `compileSdkVersion is not specified` | Try a narrow validation copy or source-wrapper-compatible Gradle lane that preserves runtime dependencies and fixes only build configuration/toolchain blockers. Keep blocked until a runtime dependency tree and source validation exist. |

## Former v15 Per-APK Triage

| APK | Current evidence | Blocker class | Main failure signature | Recommended next action |
|---|---|---|---|---|
| Ultrasonic 4.9.0 | APK report, F-Droid source tarball, runtime dependency tree, and source validation now exist. | Wrong module/root probing. | Generic probing missed the real `:ultrasonic` source module. | Resolved by strict `:ultrasonic:dependencies --configuration releaseRuntimeClasspath`; source validation confirms 12/39 emitted Maven versions, with 10 mismatches and 17 missing. |
| RunnerUp 2.11.0.1 | APK report, F-Droid source tarball, runtime dependency tree, and source validation now exist. | Variant/configuration probing. | Generic probing missed the flavor-prefixed `latestReleaseRuntimeClasspath` runtime configuration. | Resolved by strict `:app:dependencies --configuration latestReleaseRuntimeClasspath`; source validation confirms 16/39 emitted Maven versions, with 4 mismatches and 19 missing. |
| ImapNotes3 v1.4-07 | APK report, F-Droid source tarball, runtime dependency tree, and source validation now exist. | Wrong module/root probing. | Generic probing missed the real `:ImapNotes3` source module. | Resolved by strict `:ImapNotes3:dependencies --configuration releaseRuntimeClasspath`; source validation confirms 11/39 emitted Maven versions, with 6 mismatches and 22 missing. |

## Resolved From This Triage

| APK | Fix | Result |
|---|---|---|
| Primitive FTPd 8.1 | Added a strict blocker-rescue profile for `:primitiveFTPd:dependencies` and retried in Docker. | `source-validated-partial`: 12/38 confirmed, 4 mismatches, 22 missing. |
| DoliDroid 3.0.69 | Added a JCenter-to-Maven-Central validation copy and retried `:app:dependencies --configuration releaseRuntimeClasspath` in Docker. | `source-validated-partial`: 7/14 confirmed, 7 mismatches, 0 missing. |
| RadioDroid 0.86 | Added the same JCenter validation copy and a Gradle 8.13 profile hint for AGP compatibility, then retried `:app:dependencies --configuration freeReleaseRuntimeClasspath` in Docker. | `source-validated-partial`: 5/39 confirmed, 15 mismatches, 19 missing. |
| OpenKeychain 6.0.4 | Added an OpenKeychain validation copy that pins `:OpenKeychain`, replaces removed `jcenter()` calls, adds wrapper `settings.gradle`, sets AGP-required BuildConfig/AndroidX properties, and omits unavailable local project wires. | `source-validated-partial`: 5/12 confirmed, 7 mismatches, 0 missing. |
| SimpleLogin Anti-spam 1.22.0 | Added a SimpleLogin validation copy that copies the real `SimpleLogin` Gradle root, disables only Detekt build-time analysis configuration, and uses Docker Gradle 8.13 for `:app` `fdroidReleaseRuntimeClasspath`. | `source-validated-partial`: 9/39 confirmed, 13 mismatches, 17 missing. |
| Omni Notes 6.3.1 | Added an Omni Notes validation copy that disables SonarQube/test-logger/Jacoco build-time analysis wiring, pins the real `:omniNotes` module, and uses Docker Gradle 8.13 for `fossReleaseRuntimeClasspath`. | `source-validated-partial`: 4/39 confirmed, 16 mismatches, 19 missing. |
| ownCloud 4.8.0 | Added an ownCloud validation copy that disables Kotlin/KSP/Parcelize/Ktlint/Detekt/Sonar/CycloneDX build-time wiring, pins the real `:owncloudApp` module, and uses Docker Gradle 8.13 for `originalReleaseRuntimeClasspath`. | `source-validated-partial`: 7/22 confirmed, 14 mismatches, 1 missing. |
| Jitsi Meet 26.0.0 | Re-ran the source-compatible dependency-tree capture after Node/npm became available in Docker, using Gradle 8.13 for `:app` `releaseRuntimeClasspath`. SDK manager installed NDK `27.1.12297006` and `26.1.10909125` during configuration. | `source-validated-partial`: 5/7 confirmed, 2 mismatches, 0 missing. |
| K-9 / Thunderbird Android 18.0 | Added a validation-only plugin-lite/runtime-graph source copy that keeps the `app-k9mail` `fossRelease` runtime graph while disabling build-time quality/test/full-flavor/plugin overhead. Docker Gradle 9.5 captured `fossReleaseRuntimeClasspath`. | `source-validated-partial`: 5/11 confirmed, 6 mismatches, 0 missing. |
| Baby Books 0.9.2 | Added an Android-module-only validation copy that pins `:android`, keeps `:library`, adds Docker SDK metadata, and avoids unrelated frontend/deploy wiring for dependency-tree capture. | `source-validated-partial`: 10/29 confirmed, 18 mismatches, 1 missing. |
| Odysee 0.0.124 | Added a Cordova validation copy with Docker SDK metadata and Groovy `XmlParser` compatibility, then retried `:app:dependencies --configuration releaseRuntimeClasspath` in Docker Gradle 8.14.3. | `source-validated-partial`: 10/15 confirmed, 5 mismatches, 0 missing. |
| RadarWeather 6.7 | Added an old-AGP validation copy that updates the validation-only AGP path, injects required namespace/BuildConfig settings, and captures `:app` `releaseRuntimeClasspath`. | `source-validated-partial`: 5/17 confirmed, 12 mismatches, 0 missing. |
| Poet Assistant 1.31.1 | Added a JCenter-to-Maven-Central validation copy that preserves declared runtime dependencies and replaces removed `jcenter()` repository calls only for dependency-tree capture. | `source-validated-partial`: 7/37 confirmed, 9 mismatches, 21 missing. |
| Ultrasonic 4.9.0 | Added a strict module runtime profile for `:ultrasonic:dependencies` with `releaseRuntimeClasspath`/`debugRuntimeClasspath`, avoiding the generic root/`:app`/`:mobile`/`:main` probes. | `source-validated-partial`: 12/39 confirmed, 10 mismatches, 17 missing. |
| RunnerUp 2.11.0.1 | Added a strict flavor runtime profile for `:app:dependencies` with `latestReleaseRuntimeClasspath`/`latestDebugRuntimeClasspath`. | `source-validated-partial`: 16/39 confirmed, 4 mismatches, 19 missing. |
| ImapNotes3 v1.4-07 | Added a strict module runtime profile for `:ImapNotes3:dependencies` with `releaseRuntimeClasspath`/`debugRuntimeClasspath`, avoiding the generic root/`:app` probes. | `source-validated-partial`: 11/39 confirmed, 6 mismatches, 22 missing. |
| Password Master 1.5.1 | Added a strict module runtime profile for `:passwordmaster:dependencies` with `releaseRuntimeClasspath`/`debugRuntimeClasspath`, avoiding the generic `:app` probe. | `source-validated-partial`: 13/18 confirmed, 5 mismatches, 0 missing. |

## Recommended Next Order

1. Triage Flying Carpet and FitoTrack with the v16 proof logs under `data/results/source-validation/csv16/`.
2. Try strict module/flavor probing only if the source tree exposes a more precise Android app module or runtime configuration; otherwise use a validation-only Gradle/toolchain copy that preserves runtime dependencies.
3. Keep both rows source-linked blocked until dependency-tree capture and `validate-source-deps` succeed.

## Metric Rule

Do not promote any row above until the rescue pass produces:

- resolved runtime dependency tree;
- generated `validate-source-deps` JSON/Markdown output;
- refreshed proof-status/proof-results docs;
- regenerated thesis/evaluation tables if the source-validated counts change.
