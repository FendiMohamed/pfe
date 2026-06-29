# APK SBOM Recovery Report

## APK

- Path: `data/test_apks/real/F-Droid.apk`
- SHA-256: `985f5181d48bb6bafd54083a048b391271e0ab28385881cc41294fb01a222762`
- Package name: `org.fdroid.fdroid`
- Version: `1.23.2` / code `1023052`
- SDK range: min `23` / target `30`
- Manifest parse status: parsed
- DEX files: 2
- Multidex: true
- Native libraries: 4
- Extraction risk: low
- Obfuscation risk: low (0.20)

## Detection Summary

- DEX files analyzed: 2
- DEX files failed: 0
- Detected Maven components: 23
- Native file components: 4
- Vulnerability findings: 0

## APK Forensic Summary

- ZIP entries: 1119
- Standard DEX files: `classes.dex`, `classes2.dex`
- Nonstandard DEX files: none
- Native ABIs: `arm64-v8a`, `armeabi-v7a`, `x86`, `x86_64`
- Permissions: `android.permission.ACCESS_COARSE_LOCATION`, `android.permission.ACCESS_NETWORK_STATE`, `android.permission.ACCESS_WIFI_STATE`, `android.permission.BLUETOOTH`, `android.permission.BLUETOOTH_ADMIN`, `android.permission.BLUETOOTH_CONNECT`, `android.permission.BLUETOOTH_SCAN`, `android.permission.CAMERA`, `android.permission.CHANGE_NETWORK_STATE`, `android.permission.CHANGE_WIFI_MULTICAST_STATE`, `android.permission.CHANGE_WIFI_STATE`, `android.permission.ENFORCE_UPDATE_OWNERSHIP`, `android.permission.FOREGROUND_SERVICE`, `android.permission.INTERNET`, `android.permission.MANAGE_EXTERNAL_STORAGE`, `android.permission.NFC`, `android.permission.POST_NOTIFICATIONS`, `android.permission.QUERY_ALL_PACKAGES`, `android.permission.READ_EXTERNAL_STORAGE`, `android.permission.RECEIVE_BOOT_COMPLETED`, `android.permission.REQUEST_DELETE_PACKAGES`, `android.permission.REQUEST_INSTALL_PACKAGES`, `android.permission.UPDATE_PACKAGES_WITHOUT_USER_ACTION`, `android.permission.USB_PERMISSION`, `android.permission.WAKE_LOCK`, `android.permission.WRITE_EXTERNAL_STORAGE`, `android.permission.WRITE_SETTINGS`, `org.fdroid.fdroid.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION`, `org.fdroid.fdroid.permission.UPDATE_REPOS`

No extraction indicators were raised.

## Obfuscation Risk

- Level: low
- Score: 0.20
- Reason: At least half of emitted components are low-confidence version candidates.

## Detected Components

| Component | Version | Candidate reasons | Identity confidence | Version confidence | Match type | Vulnerabilities |
|---|---:|---|---|---|---|---|
| `androidx.gridlayout:gridlayout` | 1.0.0 | package, class, method, opcode, graph, literals, version-unique | confirmed/high (0.983) | exact/high (0.972) | hybrid-exact | 0 |
| `androidx.localbroadcastmanager:localbroadcastmanager` | 1.0.0 | package, class, method, opcode, graph, literals | confirmed/high (0.962) | candidate/low (0.871) | hybrid-candidate | 0 |
| `androidx.swiperefreshlayout:swiperefreshlayout` | 1.0.0 | package, class, method, opcode, graph, literals, version-unique | confirmed/high (0.919) | likely/medium (0.870) | hybrid-likely | 0 |
| `androidx.concurrent:concurrent-futures` | 1.1.0 | package, class, method, opcode, graph, literals | confirmed/high (0.937) | candidate/low (0.843) | hybrid-candidate | 0 |
| `androidx.recyclerview:recyclerview` | 1.4.0 | package, class, method, opcode, graph, literals, version-unique | likely/medium (0.835) | likely/medium (0.832) | hybrid-likely | 0 |
| `androidx.appcompat:appcompat` | 1.7.0 | package, class, method, opcode, graph, literals, version-unique | likely/medium (0.802) | likely/medium (0.815) | hybrid-likely | 0 |
| `androidx.lifecycle:lifecycle-viewmodel-android` | 2.8.7 | package, class, method, opcode, graph, literals, version-unique, artifact-family | likely/medium (0.822) | likely/medium (0.808) | hybrid-likely | 0 |
| `com.squareup.okhttp3:okhttp` | 4.12.0 | package, class, method, opcode, graph, literals, version-unique | likely/medium (0.802) | likely/medium (0.807) | hybrid-likely | 0 |
| `androidx.exifinterface:exifinterface` | 1.3.6 | package, class, method, opcode, graph, literals, version-unique | likely/medium (0.813) | likely/medium (0.792) | hybrid-likely | 0 |
| `io.ktor:ktor-client-okhttp-jvm` | 2.3.12 | package, class, method, opcode, graph, literals | likely/medium (0.877) | candidate/low (0.788) | hybrid-candidate | 0 |
| `androidx.work:work-runtime` | 2.10.0 | package, class, method, opcode, graph, literals, version-unique | likely/medium (0.757) | likely/medium (0.752) | hybrid-likely | 0 |
| `androidx.fragment:fragment` | 1.6.1 | package, class, method, opcode, graph, literals, version-unique | likely/medium (0.763) | candidate/low (0.749) | hybrid-candidate | 0 |
| `androidx.compose.ui:ui-android` | 1.7.8 | package, class, method, opcode, graph, literals, version-unique | likely/medium (0.744) | candidate/low (0.727) | hybrid-candidate | 0 |
| `org.jetbrains.kotlinx:kotlinx-coroutines-android` | 1.7.3 | package, class, method, opcode, graph, literals, version-unique | candidate/low (0.674) | candidate/low (0.706) | hybrid-candidate | 0 |
| `androidx.lifecycle:lifecycle-runtime-android` | 2.8.7 | package, class, method, opcode, graph, literals, version-unique, artifact-family | likely/medium (0.707) | candidate/low (0.676) | hybrid-candidate | 0 |
| `androidx.activity:activity` | 1.10.1 | package, class, method, opcode, graph, literals, version-unique | candidate/low (0.648) | candidate/low (0.633) | hybrid-candidate | 0 |
| `androidx.lifecycle:lifecycle-livedata` | 2.8.7 | package, class, method, opcode, graph, literals, version-unique | candidate/low (0.585) | candidate/low (0.578) | hybrid-candidate | 0 |
| `com.squareup.okio:okio-jvm` | 3.7.0 | package, class, method, opcode, graph, literals, version-unique, artifact-family | candidate/low (0.584) | candidate/low (0.543) | hybrid-candidate | 0 |
| `org.jetbrains.kotlinx:kotlinx-coroutines-core-jvm` | 1.7.3 | package, class, method, opcode, graph, literals, version-unique | candidate/low (0.547) | candidate/low (0.535) | hybrid-candidate | 0 |
| `com.google.android.material:material` | 1.12.0 | package, class, method, opcode, graph, literals, version-unique | candidate/low (0.558) | candidate/low (0.535) | hybrid-candidate | 0 |
| `androidx.compose.foundation:foundation-android` | 1.7.8 | package, class, method, opcode, graph, literals, version-unique | candidate/low (0.534) | candidate/low (0.524) | hybrid-candidate | 0 |
| `androidx.core:core` | 1.15.0 | package, class, method, opcode, graph, literals, version-unique | candidate/low (0.533) | candidate/low (0.509) | hybrid-candidate | 0 |
| `io.ktor:ktor-http-jvm` | 2.3.12 | package, class, method, opcode, graph, literals | candidate/low (0.517) | candidate/low (0.456) | hybrid-candidate | 0 |

## Native Libraries

| Path | ABI | Size | SHA-256 |
|---|---|---:|---|
| `lib/arm64-v8a/libandroidx.graphics.path.so` | arm64-v8a | 10096 | `41e9a793c43a0f4fddb19e33f346bace464f30f888ba7b9eaf96294ea115bfb6` |
| `lib/armeabi-v7a/libandroidx.graphics.path.so` | armeabi-v7a | 7252 | `41399eba6fc2a60f6f14642375c1824f3cf25eb8fec7397d753730a3ceda3e2b` |
| `lib/x86/libandroidx.graphics.path.so` | x86 | 9284 | `eb0570b41fd3bff25d8204a967c03bd7550719e768b791f680cc40cbe35f29af` |
| `lib/x86_64/libandroidx.graphics.path.so` | x86_64 | 10760 | `4e56c996f13670e70082658de7880c4020eabf4f25e43387f88ed78a713fc9f0` |

## Version Decisions

| Component | Selected version | Identity | Version | Score | Gap | Alternatives |
|---|---:|---|---|---:|---:|---|
| `androidx.gridlayout:gridlayout` | 1.0.0 | confirmed/high (0.983) | exact/high (0.972) | 0.972 | 0.084 | 1.1.0 (0.889) |
| `androidx.localbroadcastmanager:localbroadcastmanager` | 1.0.0 | confirmed/high (0.962) | candidate/low (0.871) | 0.871 | 0.000 | 1.1.0 (0.871) |
| `androidx.swiperefreshlayout:swiperefreshlayout` | 1.0.0 | confirmed/high (0.919) | likely/medium (0.870) | 0.870 | 0.189 | 1.2.0 (0.681) |
| `androidx.concurrent:concurrent-futures` | 1.1.0 | confirmed/high (0.937) | candidate/low (0.843) | 0.843 | 0.002 | 1.3.0 (0.841) |
| `androidx.recyclerview:recyclerview` | 1.4.0 | likely/medium (0.835) | likely/medium (0.832) | 0.832 | 0.098 | 1.2.1 (0.733) |
| `androidx.appcompat:appcompat` | 1.7.0 | likely/medium (0.802) | likely/medium (0.815) | 0.815 | 0.092 | 1.7.1 (0.723) |
| `androidx.lifecycle:lifecycle-viewmodel-android` | 2.8.7 | likely/medium (0.822) | likely/medium (0.808) | 0.808 | 0.222 | 2.10.0 (0.587) |
| `com.squareup.okhttp3:okhttp` | 4.12.0 | likely/medium (0.802) | likely/medium (0.807) | 0.807 | 0.074 | 4.10.0 (0.733), 4.9.1 (0.703), 4.9.0 (0.703) |
| `androidx.exifinterface:exifinterface` | 1.3.6 | likely/medium (0.813) | likely/medium (0.792) | 0.792 | 0.094 | 1.4.2 (0.699) |
| `io.ktor:ktor-client-okhttp-jvm` | 2.3.12 | likely/medium (0.877) | candidate/low (0.788) | 0.788 | 0.788 | none |
| `androidx.lifecycle:lifecycle-runtime` | 2.6.2 | likely/medium (0.851) | candidate/low (0.766) | 0.766 | 0.766 | none |
| `androidx.work:work-runtime` | 2.10.0 | likely/medium (0.757) | likely/medium (0.752) | 0.752 | 0.152 | 2.11.2 (0.600) |
| `androidx.fragment:fragment` | 1.6.1 | likely/medium (0.763) | candidate/low (0.749) | 0.749 | 0.071 | 1.5.4 (0.678), 1.8.9 (0.650) |
| `androidx.compose.ui:ui-android` | 1.7.8 | likely/medium (0.744) | candidate/low (0.727) | 0.727 | 0.195 | 1.11.2 (0.532) |
| `org.jetbrains.kotlinx:kotlinx-coroutines-android` | 1.7.3 | candidate/low (0.674) | candidate/low (0.706) | 0.706 | 0.146 | 1.9.0 (0.560) |
| `androidx.lifecycle:lifecycle-viewmodel` | 2.6.2 | likely/medium (0.775) | candidate/low (0.685) | 0.685 | 0.685 | none |
| `androidx.lifecycle:lifecycle-runtime-android` | 2.8.7 | likely/medium (0.707) | candidate/low (0.676) | 0.676 | 0.090 | 2.10.0 (0.586) |
| `androidx.activity:activity` | 1.10.1 | candidate/low (0.648) | candidate/low (0.633) | 0.633 | 0.074 | 1.8.0 (0.560), 1.13.0 (0.485) |
| `androidx.lifecycle:lifecycle-livedata` | 2.8.7 | candidate/low (0.585) | candidate/low (0.578) | 0.578 | 0.096 | 2.10.0 (0.482), 2.6.2 (0.428) |
| `com.squareup.okio:okio` | 2.8.0 | candidate/low (0.639) | candidate/low (0.557) | 0.557 | 0.016 | 2.9.0 (0.540) |
| `com.squareup.okio:okio-jvm` | 3.7.0 | candidate/low (0.584) | candidate/low (0.543) | 0.543 | 0.004 | 3.6.0 (0.540), 3.0.0 (0.474) |
| `org.jetbrains.kotlinx:kotlinx-coroutines-core-jvm` | 1.7.3 | candidate/low (0.547) | candidate/low (0.535) | 0.535 | 0.079 | 1.9.0 (0.456) |
| `com.google.android.material:material` | 1.12.0 | candidate/low (0.558) | candidate/low (0.535) | 0.535 | 0.072 | 1.13.0 (0.463) |
| `androidx.compose.foundation:foundation-android` | 1.7.8 | candidate/low (0.534) | candidate/low (0.524) | 0.524 | 0.211 | 1.11.2 (0.314) |
| `androidx.core:core` | 1.15.0 | candidate/low (0.533) | candidate/low (0.509) | 0.509 | 0.047 | 1.18.0 (0.462) |
| `io.ktor:ktor-http-jvm` | 2.3.12 | candidate/low (0.517) | candidate/low (0.456) | 0.456 | 0.456 | none |
| `io.ktor:ktor-client-core-jvm` | 2.3.12 | candidate/low (0.513) | uncertain/uncertain (0.442) | 0.442 | 0.442 | none |
| `io.ktor:ktor-utils-jvm` | 2.3.12 | candidate/low (0.474) | uncertain/uncertain (0.419) | 0.419 | 0.419 | none |
| `org.jetbrains.kotlin:kotlin-stdlib` | 2.2.10 | candidate/low (0.465) | uncertain/uncertain (0.418) | 0.418 | 0.418 | none |
| `io.ktor:ktor-io-jvm` | 2.3.12 | candidate/low (0.468) | uncertain/uncertain (0.417) | 0.417 | 0.417 | none |
| `androidx.compose.runtime:runtime-android` | 1.11.2 | uncertain/uncertain (0.401) | uncertain/uncertain (0.362) | 0.362 | 0.362 | none |
| `androidx.core:core-ktx` | 1.18.0 | uncertain/uncertain (0.334) | uncertain/uncertain (0.248) | 0.248 | 0.248 | none |
| `androidx.compose.material3:material3-android` | 1.4.0 | uncertain/uncertain (0.242) | uncertain/uncertain (0.209) | 0.209 | 0.209 | none |
| `com.google.code.gson:gson` | 2.8.5 | uncertain/uncertain (0.159) | uncertain/uncertain (0.170) | 0.170 | 0.012 | 2.8.9 (0.158), 2.8.6 (0.155) |
| `com.squareup.retrofit2:retrofit` | 2.9.0 | uncertain/uncertain (0.151) | uncertain/uncertain (0.167) | 0.167 | 0.019 | 2.8.1 (0.148) |
| `androidx.compose.ui:ui-tooling-preview-android` | 1.11.2 | uncertain/uncertain (0.180) | uncertain/uncertain (0.150) | 0.150 | 0.150 | none |
| `commons-codec:commons-codec` | 1.15 | uncertain/uncertain (0.151) | uncertain/uncertain (0.149) | 0.149 | 0.000 | 1.16.0 (0.149), 1.16.1 (0.148) |
| `androidx.datastore:datastore-preferences-android` | 1.2.1 | uncertain/uncertain (0.160) | uncertain/uncertain (0.145) | 0.145 | 0.145 | none |
| `androidx.datastore:datastore-core-android` | 1.2.1 | uncertain/uncertain (0.152) | uncertain/uncertain (0.143) | 0.143 | 0.143 | none |
| `com.fasterxml.jackson.core:jackson-databind` | 2.15.2 | uncertain/uncertain (0.139) | uncertain/uncertain (0.142) | 0.142 | 0.000 | 2.9.10.8 (0.142), 2.12.7.1 (0.141), 2.13.5 (0.141) |
| `androidx.viewpager2:viewpager2` | 1.0.0 | uncertain/uncertain (0.132) | uncertain/uncertain (0.134) | 0.134 | 0.134 | none |
| `androidx.startup:startup-runtime` | 1.1.1 | uncertain/uncertain (0.114) | uncertain/uncertain (0.114) | 0.114 | 0.114 | none |
| `androidx.compose.material:material-android` | 1.11.2 | uncertain/uncertain (0.106) | uncertain/uncertain (0.109) | 0.109 | 0.109 | none |

## Vulnerabilities

No vulnerabilities were returned by the configured source.

## Artifacts

- Match details: `data/results/demo-osv-clean-fdroid/matches.json`
- CycloneDX SBOM: `data/results/demo-osv-clean-fdroid/sbom.cdx.json`
- JSON report: `data/results/demo-osv-clean-fdroid/report.json`
- Markdown report: `data/results/demo-osv-clean-fdroid/report.md`
- HTML report: `data/results/demo-osv-clean-fdroid/report.html`
- OSV results: `data/results/demo-osv-clean-fdroid/osv-vulnerabilities.json`

## Limitations

- This MVP only detects libraries present in the local Maven reference DB.
- Heavy R8 optimization, reflection, packed APKs, encrypted DEX, and dynamic loading remain limited or unsupported.
- Native `.so` files are hashed, but native component version identification is not implemented in the first MVP.
