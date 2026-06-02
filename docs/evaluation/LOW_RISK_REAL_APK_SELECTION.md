# Low-Risk Real APK Selection

This note records the APKs chosen when the goal is to avoid source/build blockers during real-APK proof-bundle testing.

## Selection Rule

Prefer candidates with all of these properties:

- exact F-Droid APK and source tarball metadata
- no native ABI in the APK manifest
- small APK and source tarball
- normal Gradle root with an app module
- modern Android Gradle Plugin or wrapper
- quick runtime dependency-tree success
- no Flutter, React Native, browser, game-engine, CMake, or large native framework markers

## Selected Batch

| App | Package | Version | Result | Why selected |
|---|---|---|---|---|
| Stopwatch | `com.github.muellerma.stopwatch` | 1.6 (7) | source-validated partial: 4/5 confirmed | Small no-native app, modern Gradle, quick `:app` runtime dependency tree, nonzero Maven evidence. |
| Bubble | `org.woheller69.level` | 3.4 (34) | source-validated partial: 1/7 confirmed | Small no-native utility app, modern Gradle, quick dependency tree, useful source-version mismatch evidence. |
| Audio Source | `fr.dzx.audiosource` | 1.5 (7) | source-validated partial: 0/3 confirmed | Small no-native app, modern Gradle, quick dependency tree, compact AndroidX mismatch control. |
| Blue Square Speedometer | `net.nhiroki.bluesquarespeedometer` | 1.1.0 (13) | source-validated no-Maven-signal: 0/0 | Operationally clean source/build/report control, but not accuracy evidence because the report emits no Maven components. |

Proof status: `docs/evaluation/LOW_RISK_REAL_APK_PROOF_STATUS.md`.

Reference-coverage follow-up: `docs/evaluation/LOW_RISK_SOURCE_VERSION_EXPERIMENT.md`.

The missing source-used versions were added to a separate experiment DB. The broad expansion improved Bubble and Audio Source, but it regressed existing controls. Narrow checks for `androidx.recyclerview:recyclerview@1.0.0` and `androidx.lifecycle:lifecycle-runtime@2.1.0` also regressed controls, so the shared calibrated DB remains unchanged.

## Rejected During Preflight

| Candidate type | Examples | Reason |
|---|---|---|
| Old Gradle/JCenter apps | None remaining from this low-risk note | DNG Processor and Private DNS Quick Tile were rescued in the legacy follow-up, but both are no-Maven-signal controls rather than accuracy evidence. |
| Dependency resolution stalls | CalEF, Local NLP Backend, Intent Intercept, Crazyflie Client, Virtual Host, WiFi Walkie Talkie | Declared dependencies and modern-looking source, but dependency-tree probing exceeded the hard timeout. |
| Zero-Maven report controls | Easy Open Link, personalDNSfilter, uNote | Source/build/report gates work, but the APK report emits no Maven components, so they are useful only as smoke/no-signal controls. |

## Legacy Rescue Follow-Up

| App | Package | Version | Result | Why it stays outside accuracy metrics |
|---|---|---|---|---|
| DNG Processor | `amirz.dngprocessor` | 5 (5) | source-validated no-Maven-signal: 0/0 emitted Maven components, source tree resolves 2 Maven components | JDK 11 plus Gradle 5.1.1 and a validation-only SDK-path copy rescue the dependency tree, but the APK report emits no Maven SBOM components. |
| Private DNS Quick Tile | `com.jpwolfso.privdnsqt` | 1.5 (6) | source-validated no-Maven-signal: 0/0 emitted Maven components, source tree resolves 2 Maven components | JDK 11 plus the source-declared Gradle 6.1.1 rescues the dependency tree, but the APK report emits no Maven SBOM components. |
