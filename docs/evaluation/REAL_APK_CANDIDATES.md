# Real APK Candidate Selection Table

This file is generated from `configs/real_apk_candidates.json`.
It is the working shortlist for growing the real APK dataset. An APK is not admitted to the source-validated dataset until the proof bundle is complete.

## Admission Rule

- APK file and SHA-256 are stored.
- Source repository URL is recorded.
- Exact source tag or commit is recorded.
- APK versionName/versionCode is compared with source metadata.
- Resolved Gradle dependency tree is stored.
- MVP report is generated.
- Source validation report is generated when source validation is claimed.
- Dataset classification row is present in the inventory.

## Priority Status

| Status | Meaning |
|---|---|
| admitted | Already in the dataset with proof artifacts. |
| first-batch | Recommended first batch after F-Droid. |
| M1-candidate | First milestone candidate; validate these before scaling. |
| M2-candidate | Good expansion candidate after the first 5-20 real APKs work. |
| limitation-candidate | Chosen mainly to test a known boundary such as native-heavy, packed, Flutter, Unity, or dynamic-code behavior. |

## Candidate Summary

| Field | Value |
|---|---:|
| Total candidates | 19 |
| Priority: M1-candidate | 4 |
| Priority: M2-candidate | 4 |
| Priority: admitted | 8 |
| Priority: first-batch | 2 |
| Priority: limitation-candidate | 1 |
| Target layer: limitation | 1 |
| Target layer: source-validated-real | 18 |

## First Batch Recommendation

These are the first five candidates to validate after F-Droid because they cover a balanced mix of simple/medium, media/networking, Kotlin/AndroidX, older/security-sensitive, and native-heavy behavior.

| Priority | App | Package / APK source to verify | Version target | Source repo to verify | Criteria covered | Why useful | Proof |
|---|---|---|---|---|---|---|---|
| admitted | OpenTracks | `de.dennisguse.opentracks`; F-Droid or GitHub release | v4.27.0irreproducible (6653) | `https://codeberg.org/OpenTracksApp/OpenTracks` | simple/medium app, modern, multidex, AndroidX, location/maps, source-validated | Second source-validated real APK: 19/19 emitted SBOM components confirmed against resolved Gradle dependency tree. | complete |
| first-batch | NewPipe | `org.schabi.newpipe`; F-Droid or official GitHub release | 0.28.5 (1010) | `https://github.com/TeamNewPipe/NewPipe` | modern, multidex, media app, Kotlin/Java, likely R8, networking/media dependencies, native .so, source-linked | Popular open-source Android app with rich media and networking dependency profile; dependency-tree generation now works, but current validation exposes version mismatches that need further calibration. | partial-version-mismatch |
| admitted | Tusky | `com.keylesspalace.tusky`; F-Droid or GitHub release | 32.2 (142) | `https://codeberg.org/tusky/Tusky` | modern Kotlin, AndroidX, networking, social client, Mastodon API, single DEX, native .so, source-linked, source-validated, sparse emitted SBOM | Good Kotlin/AndroidX social-client case with real networking dependencies; after adding Retrofit 3.0.0 to calibration, the emitted Retrofit component validates cleanly against source. | complete |
| admitted | K-9 Mail / Thunderbird Android | `com.fsck.k9`; F-Droid or GitHub release | 18.0 (39035) | `https://github.com/thunderbird/thunderbird-android` | older history, modern release, email/security, networking, multidex, native .so, source-linked, source-validated, validation-only included-build rescue | Good old-to-modern evolution case and security-sensitive app. APK/source/report proof is collected, and a validation-only included-build/plugin-lite source copy produced the resolved fossReleaseRuntimeClasspath tree. Source validation confirms 5/11 emitted Maven versions with 6 version mismatches and 0 missing coordinates. | source-validated-partial-mismatch |
| first-batch | Organic Maps | `app.organicmaps`; F-Droid or GitHub release | 2026.05.08-4-FDroid (26050804) | `https://github.com/organicmaps/organicmaps` | native-heavy, maps, C++/Java/Kotlin mix, multidex, native .so boundary, large opaque assets, source-linked | Covers the native hash-only reporting boundary while still being open source; counted as limitation evidence, not source-validated accuracy evidence. | limitation-complete |

## M1 Source-Validated Shortlist

These APKs are the best first milestone candidates because they are open-source, Android/Gradle based, and cover different MVP criteria.

| Priority | App | Package / APK source to verify | Version target | Source repo to verify | Criteria covered | Why useful | Proof |
|---|---|---|---|---|---|---|---|
| admitted | F-Droid Client | `org.fdroid.fdroid`; data/test_apks/real/F-Droid.apk | 1.23.2 | `https://gitlab.com/fdroid/fdroidclient` | modern, multidex, R8/minify, AndroidX/Jetpack, Kotlin/Java, native .so, source-validated | Current proof model: 23/23 emitted SBOM components confirmed against source dependency tree. | complete |
| admitted | OpenTracks | `de.dennisguse.opentracks`; F-Droid or GitHub release | v4.27.0irreproducible (6653) | `https://codeberg.org/OpenTracksApp/OpenTracks` | simple/medium app, modern, multidex, AndroidX, location/maps, source-validated | Second source-validated real APK: 19/19 emitted SBOM components confirmed against resolved Gradle dependency tree. | complete |
| first-batch | NewPipe | `org.schabi.newpipe`; F-Droid or official GitHub release | 0.28.5 (1010) | `https://github.com/TeamNewPipe/NewPipe` | modern, multidex, media app, Kotlin/Java, likely R8, networking/media dependencies, native .so, source-linked | Popular open-source Android app with rich media and networking dependency profile; dependency-tree generation now works, but current validation exposes version mismatches that need further calibration. | partial-version-mismatch |
| admitted | Tusky | `com.keylesspalace.tusky`; F-Droid or GitHub release | 32.2 (142) | `https://codeberg.org/tusky/Tusky` | modern Kotlin, AndroidX, networking, social client, Mastodon API, single DEX, native .so, source-linked, source-validated, sparse emitted SBOM | Good Kotlin/AndroidX social-client case with real networking dependencies; after adding Retrofit 3.0.0 to calibration, the emitted Retrofit component validates cleanly against source. | complete |
| admitted | K-9 Mail / Thunderbird Android | `com.fsck.k9`; F-Droid or GitHub release | 18.0 (39035) | `https://github.com/thunderbird/thunderbird-android` | older history, modern release, email/security, networking, multidex, native .so, source-linked, source-validated, validation-only included-build rescue | Good old-to-modern evolution case and security-sensitive app. APK/source/report proof is collected, and a validation-only included-build/plugin-lite source copy produced the resolved fossReleaseRuntimeClasspath tree. Source validation confirms 5/11 emitted Maven versions with 6 version mismatches and 0 missing coordinates. | source-validated-partial-mismatch |
| first-batch | Organic Maps | `app.organicmaps`; F-Droid or GitHub release | 2026.05.08-4-FDroid (26050804) | `https://github.com/organicmaps/organicmaps` | native-heavy, maps, C++/Java/Kotlin mix, multidex, native .so boundary, large opaque assets, source-linked | Covers the native hash-only reporting boundary while still being open source; counted as limitation evidence, not source-validated accuracy evidence. | limitation-complete |
| M1-candidate | AntennaPod | `de.danoeh.antennapod`; F-Droid | 3.11.4 (3110495) | `https://github.com/AntennaPod/AntennaPod` | modern, media, networking, AndroidX, multidex, native .so, source-linked, source-validated, partial-version-mismatch | Good real app with podcast/media/networking dependencies. Source validation confirms 19/20 emitted Maven components with one AndroidX Core near-tie mismatch. | partial-version-mismatch |
| M1-candidate | KDE Connect | `org.kde.kdeconnect_tp`; F-Droid | 0f3cc84446065102c064f78d4276bb4ebd00d3c9 | `https://invent.kde.org/network/kdeconnect-android` | modern, AndroidX/Kotlin/Java, networking, permissions-heavy, multidex, native-.so, R8/shrink release | Good cross-device/networking app with F-Droid build provenance. | partial-version-mismatch |
| M1-candidate | Wikipedia Android | `org.wikipedia`; F-Droid | r/50586-r-2026-05-12 (50586) | `https://github.com/wikimedia/apps-android-wikipedia` | large modern app, AndroidX, networking, multidex, native .so, MapLibre, source-linked, source-validated partial-mismatch | Good complex real-world dependency tree. APK/source proof, calibrated MVP report, and resolved Gradle dependency-tree validation are collected. The result is useful as a source-validated partial-version-mismatch case, not a clean accuracy case. | source-validated-partial-mismatch |
| admitted | VLC Android | `org.videolan.vlc`; F-Droid | 3.7.1 (13070106) | `https://code.videolan.org/videolan/vlc-android` | native-heavy, media, large APK, multidex, native .so boundary, source-linked, source-validated, partial-version-mismatch | Excellent native-heavy media case: the report emits Maven dependencies and hash-only native file components, while source validation exposes many older-version mismatches. | source-validated-partial-mismatch |
| admitted | OsmAnd~ | `net.osmand.plus`; F-Droid | 5.3.10 (531003) | `https://github.com/osmandapp/OsmAnd` | native-heavy, maps, large APK, AndroidX, multidex, source-linked, source-validated partial-mismatch | Large maps/native stress case. APK/source/report/dependency-tree proof is collected; validation confirms 16/25 emitted Maven versions, with 9 version mismatches and 0 missing coordinates. | source-validated-partial-mismatch |
| M1-candidate | Conversations | `eu.siacs.conversations`; F-Droid | 7346a14dcedb155762133ea3ec512fdf34b57876 | `https://codeberg.org/iNPUTmice/Conversations` | communication/security, networking, older codebase history, multidex, R8/minify release, native libraries | Good old/modern messaging and dependency-validation case. | source-validated-partial-mismatch |
| admitted | Material Files | `me.zhanghai.android.files`; F-Droid | 1.7.4 (39) | `https://github.com/zhanghai/MaterialFiles` | file manager, network storage, single DEX, AndroidX, native .so, source-linked, source-validated partial-mismatch, validation-only native build bypass | Adds a file-manager/network-storage/native-JNI APK family. APK/source/report/dependency-tree proof is collected; validation confirms 0/2 emitted SBOM versions, with 2 AndroidX version mismatches and 0 missing coordinates. | source-validated-partial-mismatch |
| admitted | Jitsi Meet | `org.jitsi.meet`; F-Droid | 26.0.0 (26000004) | `https://github.com/jitsi/jitsi-meet` | React Native, framework boundary, native-heavy, WebRTC, Hermes, multidex, modern dependencies, source-validated, native hash-only boundary | Tests a React Native/native-heavy framework boundary where the emitted Maven subset is source-validated but React Native/WebRTC/Hermes native libraries remain hash-only boundary evidence. | partial-version-mismatch |

## M2 Expansion Pool

These candidates help reach the 50 source-validated real APK target after the M1 workflow is proven.

| Priority | App | Package / APK source to verify | Version target | Source repo to verify | Criteria covered | Why useful | Proof |
|---|---|---|---|---|---|---|---|
| M2-candidate | Nextcloud Android | `com.nextcloud.client`; F-Droid | 33.1.0 (330010090) | `https://github.com/nextcloud/android.git` | large modern app, networking, AndroidX, Compose, Kotlin, multidex, native libraries, large transitive dependency tree, source-linked, source-validated partial-mismatch | Large modern cloud-sync dependency case. APK/source/report/dependency-tree proof is collected; guarded-promoted shared-DB validation confirms 21/29 emitted SBOM versions with 7 version mismatches and 1 OkHttp public-vs-Android target artifact-family nuance. | source-validated-partial-mismatch |
| M2-candidate | Markor | `net.gsantner.markor`; F-Droid | 2.16.1 (163) | `https://github.com/gsantner/markor` | smaller app, simple baseline, older minSdk, multidex, no native .so, source-linked, source-validated partial-mismatch | Good simple-app baseline for the real dataset. APK/source/report/dependency-tree proof is collected; guarded shared-DB validation now confirms 7/19 emitted SBOM versions with 12 older-dependency version mismatches and 0 missing coordinates. A targeted source-used-version calibration experiment improves Markor to 19/19 but is not kept in full because it regresses newer clean baselines. | source-validated-partial-mismatch |
| M2-candidate | FairEmail | `eu.faircode.email`; F-Droid | 1.2315 (2315) | `https://github.com/M66B/FairEmail.git` | email/security, networking, modern, multidex, AndroidX, native .so, source-linked, source-validated partial, validation-only native build bypass | Good security-sensitive email comparison with K-9. APK/source/report proof is collected, and Maven runtime dependency validation now works through a validation-only source copy with native build disabled. The result is partial: 7/13 emitted Maven versions confirmed, 6 AndroidX version mismatches, and 0 missing coordinates. | source-validated-partial-mismatch |
| M2-candidate | Aegis Authenticator | `com.beemdevelopment.aegis`; F-Droid | 3.4.2 (81) | `https://github.com/beemdevelopment/Aegis` | security/crypto, simpler dependency tree, modern, multidex, AndroidX, native .so, source-linked, source-validated partial-mismatch | Good security/crypto-oriented simpler app. APK/source/report/dependency-tree proof is collected; validation confirms 6/7 emitted SBOM versions with one remaining ViewPager2 mismatch. | source-validated-partial-mismatch |

## Limitation Candidate Pool

These are useful even if full source validation is hard, because they test where the MVP should be cautious.

| Priority | App | Package / APK source to verify | Version target | Source repo to verify | Criteria covered | Why useful | Proof |
|---|---|---|---|---|---|---|---|
| limitation-candidate | Termux | `com.termux`; F-Droid source tarball and APK | 0.119.0-beta.3 (1022) | `https://github.com/termux/termux-app` | native-heavy, unusual packaging, dynamic/tooling boundary, multidex, older targetSdk, source-linked | Useful for limitation analysis rather than pure Maven SBOM accuracy because the APK carries very large native bootstrap payloads. | limitation-complete |

## Selection Balance Targets

| Criterion | Target |
|---|---|
| simple or single dex | 8-10 inside first 50 source-validated real APKs |
| multidex | 15-20 inside first 50 source-validated real APKs |
| modern kotlin androidx | 20-25 inside first 50 source-validated real APKs |
| older release or dependency profile | 8-12 inside first 50 source-validated real APKs |
| native so present | 10-15 inside first 50 source-validated real APKs |
| r8 minification evidence | 20+ inside first 50 source-validated real APKs |
| vulnerable dependency expected | 3-5 inside first 50 source-validated real APKs |
| large complex app | 8-10 inside first 50 source-validated real APKs |
| limitation boundary behavior | 5-8 inside first 50 source-validated real APKs |

Because one APK can cover several criteria, these targets do not add up to 50.

## Next Concrete Step

Create a proof folder for each first-batch candidate:

```text
data/test_apks/real/<app-id>/
data/source/<app-id>-<version-or-tag>/
data/results/source-validation/<app-id>/
data/results/report-real-<app-id>/
```

For each candidate, verify the package name, APK version, source tag or commit, Gradle configuration, dependency tree, report, and source validation before moving its priority to `admitted`.
