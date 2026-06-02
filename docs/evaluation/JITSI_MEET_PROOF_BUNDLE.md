# Jitsi Meet Proof Bundle

Status: source-linked framework/toolchain-blocked boundary case.

Jitsi Meet is included as a React Native and native-heavy framework-boundary case. It is useful for dataset diversity and limitation analysis, but it is not counted in source-validated Maven version accuracy because the resolved Gradle dependency tree is not available yet.

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
| Gradle error log | `data/results/source-validation/jitsi-meet/gradle-error.log` |
| Partial dependency output | `data/results/source-validation/jitsi-meet/releaseRuntimeClasspath.txt` |

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

## Source Validation Attempt

The source tarball was first redownloaded after a truncated/corrupt transfer. The clean tarball passed listing checks and has the SHA-256 recorded above.

The first dependency-tree attempt with the Docker-provided Gradle `9.5.0` failed because this source build imports `org.gradle.util.VersionNumber`, which is no longer available there. A second attempt used the source-compatible Gradle `8.14` distribution and progressed farther into React Native module configuration.

The Gradle `8.14` attempt failed before producing a resolved dependency tree:

```text
Cannot run program "node" (in directory "/tmp/jitsi-validation/org.jitsi.meet_26000004_src.tar.gz/android"): Exec failed, error: 2 (No such file or directory)
```

This is a toolchain blocker, not an APK identity failure. F-Droid metadata for this build also requires `cmake`, `emscripten`, `esbuild`, `make`, NDK `27.1.12297006`, NDK `26.1.10909125`, `matrix-olm@3.2.3`, and `npm install --build-from-source`. Until the Docker validation environment has the React Native/Node build stack, Jitsi stays source-linked but validation-blocked.

## Interpretation

Jitsi should be used as framework-boundary evidence:

- It expands the real APK dataset beyond pure Java/Kotlin and native-heavy media into React Native.
- It shows the MVP can still emit cautious Maven candidates and native hash-only SBOM file components.
- Its possible Gson advisory is correctly potential, not confirmed, because the APK-side identity and version evidence are low-confidence and source validation is blocked.
- It must not be included in source-validated precision, recall, or emitted Maven version confirmation rates.
