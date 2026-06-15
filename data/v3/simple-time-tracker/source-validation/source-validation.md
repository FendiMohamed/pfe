# Source Dependency Validation

## Inputs

| Item | Value |
|---|---|
| CycloneDX SBOM | `data/results/evaluation/clean-real-apk-candidate-sweep-v3/report-real-simple-time-tracker/sbom.cdx.json` |
| Gradle dependency tree | `data/v3/simple-time-tracker/docker-app-baseReleaseRuntimeClasspath.txt` |
| Source components parsed | 105 |

## Summary

| Group | Components | Confirmed | Version mismatch | Missing |
|---|---:|---:|---:|---:|
| SBOM components | 12 | 6 | 6 | 0 |
| Extra candidates | 0 | 0 | 0 | 0 |

## SBOM Component Comparison

| Component | SBOM version | Source resolved versions | Result | Match type | Evidence |
|---|---:|---|---|---|---|
| `androidx.viewpager2:viewpager2` | 1.1.0 | 1.1.0-beta02 | version-mismatch | hybrid-likely | `\|    \|    \|              \|    \--- androidx.viewpager2:viewpager2:1.1.0-beta02 (c)` |
| `androidx.appcompat:appcompat` | 1.7.0 | 1.7.0 | confirmed | hybrid-likely | `\|    \|    \|              +--- androidx.appcompat:appcompat:1.6.1 -> 1.7.0` |
| `androidx.startup:startup-runtime` | 1.1.1 | 1.1.1 | confirmed | hybrid-likely | `\|    \|    \|    \|    \|    \|    \|         \|    +--- androidx.startup:startup-runtime:1.1.1` |
| `androidx.lifecycle:lifecycle-runtime` | 2.6.2 | 2.8.4 | version-mismatch | hybrid-candidate | `\|    \|    \|    \|    \|    \|    +--- androidx.lifecycle:lifecycle-runtime:2.6.2 -> 2.8.4` |
| `androidx.recyclerview:recyclerview` | 1.3.2 | 1.3.2 | confirmed | hybrid-candidate | `\|    \|    \|              +--- androidx.recyclerview:recyclerview:1.0.0 -> 1.3.2` |
| `androidx.fragment:fragment` | 1.6.1 | 1.6.2 | version-mismatch | hybrid-candidate | `\|    \|    \|    +--- androidx.fragment:fragment:1.6.2` |
| `org.jetbrains.kotlinx:kotlinx-coroutines-android` | 1.7.3 | 1.7.3 | confirmed | hybrid-candidate | `\|    \|    \|    +--- org.jetbrains.kotlinx:kotlinx-coroutines-android:1.6.4 -> 1.7.3` |
| `androidx.concurrent:concurrent-futures` | 1.1.0 | 1.1.0 | confirmed | hybrid-candidate | `\|    \|    \|    \|    \|    \|    +--- androidx.concurrent:concurrent-futures:1.0.0 -> 1.1.0` |
| `androidx.lifecycle:lifecycle-viewmodel` | 2.6.2 | 2.8.4 | version-mismatch | hybrid-candidate | `\|    \|    \|    \|    \|    \|    \|         \|         +--- androidx.lifecycle:lifecycle-viewmodel:2.8.4 (c)` |
| `androidx.activity:activity` | 1.8.1 | 1.8.2 | version-mismatch | hybrid-candidate | `\|    \|    \|    \|    +--- androidx.activity:activity:1.8.2` |
| `com.google.android.material:material` | 1.12.0 | 1.12.0 | confirmed | hybrid-candidate | `\|    \|    \|         \--- com.google.android.material:material:1.4.0-beta01 -> 1.12.0` |
| `androidx.core:core` | 1.15.0 | 1.13.0 | version-mismatch | hybrid-candidate | `\|    \|    \|    \|    \|    +--- androidx.core:core:1.8.0 -> 1.13.0` |

## Interpretation

- `confirmed` means the Maven coordinate and selected version are present in the resolved source dependency tree.
- `version-mismatch` means the coordinate is present, but the resolved source version differs from the SBOM version.
- `missing` means the coordinate was not found in the provided dependency tree.
- This validates SBOM identity/version against source dependencies when source is available; it does not prove APK bytecode completeness by itself.
