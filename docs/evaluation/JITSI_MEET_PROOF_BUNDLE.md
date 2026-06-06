# Jitsi Meet Proof Bundle

Status: source-validated-partial framework-boundary case.

Jitsi Meet is included as a React Native and native-heavy framework-boundary case. A Docker Gradle `8.13` dependency-tree rescue now validates the emitted Maven components at `5/7` confirmed, `2` mismatches, and `0` missing. It is counted as source-validated partial Maven evidence, while the React Native/WebRTC/Hermes native libraries remain hash-only boundary evidence.

## Identity

| Field | Value |
|---|---|
| App | Jitsi Meet |
| Package | `org.jitsi.meet` |
| Version | `26.0.0` |
| Version code | `26000004` |
| APK source | F-Droid |
| Source repository | `https://github.com/jitsi/jitsi-meet` |
| F-Droid commit | `3db92da369b921d73189dbcb55744f9f5459cac0` |
| F-Droid subdir | `android/app` |
| APK SHA-256 | `72aab4912b08431a2340fc1fb1f181be3a07e8b7ac607e0bb9e4c3814c2e4248` |
| Source tarball SHA-256 | `1a0ea529821300a824809a3dc21051706d8383e55395ba82fbb638ac3a9ea9bf` |

## Collected Artifacts

| Artifact | Path |
|---|---|
| APK | `data/test_apks/real/jitsi-meet/jitsi-meet.apk` |
| APK metadata | `data/test_apks/real/jitsi-meet/metadata.json` |
| F-Droid metadata | `data/test_apks/real/jitsi-meet/fdroid-metadata.yml` |
| Source tarball | `data/source/jitsi-meet/source.tar.gz` |
| MVP report | `data/results/report-real-jitsi-meet/report.json` |
| CycloneDX SBOM | `data/results/report-real-jitsi-meet/sbom.cdx.json` |
| Source dependency attempt script | `data/results/source-validation/jitsi-meet/run-gradle-deps.sh` |
| Gradle exit code | `data/results/source-validation/jitsi-meet/gradle-exit-code.txt` |
| Gradle error log | `data/results/source-validation/jitsi-meet/gradle-error.log` |
| Resolved dependency tree | `data/results/source-validation/jitsi-meet/releaseRuntimeClasspath.txt` |
| Source validation JSON | `data/results/source-validation/jitsi-meet-report-validation/source-validation.json` |
| Source validation summary | `data/results/source-validation/jitsi-meet-report-validation/source-validation.md` |

## APK And Report Summary

| Metric | Value |
|---|---|
| DEX files | 2 |
| Multidex | yes |
| minSdk / targetSdk | 26 / 35 |
| Native libraries | 13, ABI `x86_64` |
| Extraction risk | low |
| Obfuscation risk | low, with low-confidence component warning |
| Maven SBOM components | 7 |
| Native file SBOM components | 13 |
| OSV result | 1 potential advisory, 0 confirmed advisories |

Detected Maven components are all candidate-confidence results:

| Component | Version | Confidence |
|---|---:|---|
| `androidx.startup:startup-runtime` | `1.1.1` | candidate / candidate |
| `com.google.code.gson:gson` | `2.8.6` | candidate / candidate |
| `androidx.fragment:fragment` | `1.6.1` | candidate / candidate |
| `androidx.exifinterface:exifinterface` | `1.3.6` | candidate / candidate |
| `androidx.swiperefreshlayout:swiperefreshlayout` | `1.0.0` | candidate / candidate |
| `androidx.lifecycle:lifecycle-runtime` | `2.6.2` | candidate / candidate |
| `androidx.activity:activity` | `1.10.1` | candidate / candidate |

The report also emits hash-only native file components including React Native/Hermes/WebRTC libraries such as `libhermes.so`, `libreactnative.so`, `libjingle_peerconnection_so.so`, `libjsi.so`, and `librnscreens.so`.

## Source Validation

The source tarball was first redownloaded after a truncated/corrupt transfer. The clean tarball passed listing checks and has the SHA-256 recorded above.

The first dependency-tree attempt with the Docker-provided Gradle `9.5.0` failed because this source build imports `org.gradle.util.VersionNumber`, which is no longer available there. A second attempt used the source-compatible Gradle `8.14` distribution and progressed farther into React Native module configuration.

That earlier Gradle `8.14` attempt failed before producing a resolved dependency tree:

```text
Cannot run program "node" (in directory "/tmp/jitsi-validation/org.jitsi.meet_26000004_src.tar.gz/android"): Exec failed, error: 2 (No such file or directory)
```

That was a toolchain blocker, not an APK identity failure. The blocker was cleared after the Docker validation runtime had Node/npm available and Gradle `8.13` was used for the source-compatible dependency task. The successful run reached `:app:dependencies`, wrote `releaseRuntimeClasspath`, exited `0`, and installed NDK `27.1.12297006` and `26.1.10909125` during React Native module configuration.

Validation command:

```text
python -m apk_sbom.cli validate-source-deps --sbom data/results/report-real-jitsi-meet/sbom.cdx.json --dependency-tree data/results/source-validation/jitsi-meet/releaseRuntimeClasspath.txt --output-dir data/results/source-validation/jitsi-meet-report-validation
```

Validation result:

| Group | Components | Confirmed | Version mismatch | Missing |
|---|---:|---:|---:|---:|
| SBOM components | 7 | 5 | 2 | 0 |
| Extra candidates | 0 | 0 | 0 | 0 |

Confirmed emitted Maven versions:

| Component | Version |
|---|---:|
| `androidx.startup:startup-runtime` | `1.1.1` |
| `com.google.code.gson:gson` | `2.8.6` |
| `androidx.fragment:fragment` | `1.6.1` |
| `androidx.exifinterface:exifinterface` | `1.3.6` |
| `androidx.lifecycle:lifecycle-runtime` | `2.6.2` |

Mismatches:

| Component | SBOM version | Source resolved version |
|---|---:|---:|
| `androidx.swiperefreshlayout:swiperefreshlayout` | `1.0.0` | `1.1.0` |
| `androidx.activity:activity` | `1.10.1` | `1.9.3` |

## Interpretation

Jitsi should be used as source-validated partial framework-boundary evidence:

- It expands the real APK dataset beyond pure Java/Kotlin and native-heavy media into React Native.
- It shows the MVP can emit cautious Maven candidates and validate the subset visible in the resolved source dependency tree.
- Its Gson `2.8.6` coordinate is source-confirmed, but the existing OSV report still records the advisory as potential unless regenerated with source-validation-aware labels.
- Its React Native/WebRTC/Hermes native libraries are still native file hash components, not Maven package/version evidence.
