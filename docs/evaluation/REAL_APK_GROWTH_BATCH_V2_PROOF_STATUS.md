# Real APK Growth Batch V2 Proof Status

This batch artifact advances all 8 real APK smoke rows through the same proof gates together.
It does not promote any row into source-validated accuracy metrics unless a runtime dependency tree and source-validation output exist.

## Summary

| Field | Value |
|---|---|
| Selected APKs | 8 |
| Source tarballs available | 8 |
| Dependency trees captured | 4 |
| Source validations completed | 4 |
| Script failures | 0 |
| Source root | `data/source/real-apk-growth-batch-v2` |
| Validation root | `data/results/source-validation/real-apk-growth-batch-v2` |

## Per-APK Status

| App | Version | Proof status | Source | Gradle/dependency tree | Source validation | Next gate |
|---|---|---|---|---|---|---|
| LocalSend | 1.17.0 (583) | gradle-blocked | ok: `data/source/real-apk-growth-batch-v2/localsend/source.tar.gz` | blocked: no Gradle root found in extracted source | blocked-until-dependency-tree: Run validate-source-deps after a runtime dependency tree is captured. | Investigate Gradle configuration/toolchain blocker. |
| OpenVPN for Android | 0.7.64 (219) | source-validated-partial | ok: `data/source/real-apk-growth-batch-v2/openvpn-for-android/source.tar.gz` | ok: validation-copy; 1 attempted config(s): `data/results/source-validation/real-apk-growth-batch-v2/openvpn-for-android/root1-main-dependencies-uiOvpn23ReleaseRuntimeClasspath.txt` | ok: 13/20 confirmed, 7 mismatch(es), 0 missing: `data/results/source-validation/real-apk-growth-batch-v2/openvpn-for-android/source-validation/source-validation.md` | Record as source-validated partial; keep mismatches explicit. |
| KeePassDX | 4.4.3 (44300) | gradle-blocked | ok: `data/source/real-apk-growth-batch-v2/keepassdx/source.tar.gz` | blocked: no attempted Gradle configuration succeeded; 14 attempted config(s) | blocked-until-dependency-tree: Run validate-source-deps after a runtime dependency tree is captured. | Investigate Gradle configuration/toolchain blocker. |
| Gadgetbridge | 0.91.1 (248) | source-validated-partial | ok: `data/source/real-apk-growth-batch-v2/gadgetbridge/source.tar.gz` | ok: 1 attempted config(s): `data/results/source-validation/real-apk-growth-batch-v2/gadgetbridge/root1-app-dependencies-mainlineReleaseRuntimeClasspath.txt` | ok: 17/21 confirmed, 4 mismatch(es), 0 missing: `data/results/source-validation/real-apk-growth-batch-v2/gadgetbridge/source-validation/source-validation.md` | Record as source-validated partial; keep mismatches explicit. |
| DAVx5 | 4.5.12-ose (405120004) | source-validated-partial | ok: `data/source/real-apk-growth-batch-v2/davx5/source.tar.gz` | ok: 1 attempted config(s): `data/results/source-validation/real-apk-growth-batch-v2/davx5/root1-app-ose-dependencies-oseReleaseRuntimeClasspath.txt` | ok: 3/5 confirmed, 2 mismatch(es), 0 missing: `data/results/source-validation/real-apk-growth-batch-v2/davx5/source-validation/source-validation.md` | Record as source-validated partial; keep mismatches explicit. |
| Shelter | 1.9.1 (445) | source-validated-partial | ok: `data/source/real-apk-growth-batch-v2/shelter/source.tar.gz` | ok: validation-copy; 1 attempted config(s): `data/results/source-validation/real-apk-growth-batch-v2/shelter/root1-app-dependencies-releaseRuntimeClasspath.txt` | ok: 3/3 confirmed, 0 mismatch(es), 0 missing: `data/results/source-validation/real-apk-growth-batch-v2/shelter/source-validation/source-validation.md` | Record as source-validated partial; keep mismatches explicit. |
| TheXTech | 1.3.7.2 (1030702) | gradle-blocked | ok: `data/source/real-apk-growth-batch-v2/thextech/source.tar.gz` | blocked: no Gradle root found in extracted source | blocked-until-dependency-tree: Run validate-source-deps after a runtime dependency tree is captured. | Investigate Gradle configuration/toolchain blocker. |
| Fennec F-Droid | 151.0.2 (1510220) | gradle-blocked | ok: `data/source/real-apk-growth-batch-v2/fennec-fdroid/source.tar.gz` | blocked: no Gradle root found in extracted source | blocked-until-dependency-tree: Run validate-source-deps after a runtime dependency tree is captured. | Investigate Gradle configuration/toolchain blocker. |

## Rules

- Source tarball checksum success is only a source-availability gate.
- Dependency-tree success is required before `validate-source-deps` can produce source-confirmed counts.
- Framework/native-heavy rows may remain limitation evidence even after source capture.
- Rows with blocked Gradle trees stay out of source-validated metrics.
