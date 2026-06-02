# Conversations Proof Bundle

Conversations is a source-linked, source-validated real APK case for the dataset. It is useful as a realistic messaging/security app with multidex, release minification, networking dependencies, and native libraries.

## Identity Proof

| Field | Result |
|---|---|
| App | Conversations |
| Package | `eu.siacs.conversations` |
| APK | `data/test_apks/real/conversations/conversations.apk` |
| APK SHA-256 | `081772cb77bf8f5d7a1afac4e4846ff104d83becc558ffc7f625af6fba5dade9` |
| F-Droid versionName | `2.20.0+free` |
| F-Droid versionCode | `4217704` |
| Source commit | `7346a14dcedb155762133ea3ec512fdf34b57876` |
| Source repo | `https://codeberg.org/iNPUTmice/Conversations` |
| Source archive | `data/source/conversations/source.tar.gz` |
| Source archive SHA-256 | `b6986ac7f7ec9d87ea3059149ef2563b20d1d1b23dda0c7d8c6764551bcff569` |

The APK manifest matches the F-Droid build metadata: package `eu.siacs.conversations`, versionName `2.20.0+free`, and versionCode `4217704`.

## APK Characteristics

| Field | Result |
|---|---:|
| Standard DEX files | 2 |
| Multidex | true |
| Native libraries | 2 |
| Native ABI | `arm64-v8a` |
| minSdk | 23 |
| targetSdk | 36 |
| Extraction risk | low |
| Obfuscation risk | low (`0.20`) |
| Nonstandard DEX files | 0 |
| OSV vulnerabilities | 0 |

The source release build uses R8/minification:

```gradle
release {
    shrinkResources true
    minifyEnabled true
    proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
}
```

## Source Dependency Tree

The F-Droid source archive is an uncompressed tar file even though the filename ends with `.tar.gz`; use `tar -xf`, not `tar -xzf`.

The validated Gradle configuration is:

```text
conversationsFreeReleaseRuntimeClasspath
```

Evidence path:

```text
data/results/source-validation/conversations/conversationsFreeReleaseRuntimeClasspath.txt
```

## MVP Report

| Artifact | Path |
|---|---|
| Markdown report | `data/results/report-real-conversations/report.md` |
| HTML report | `data/results/report-real-conversations/report.html` |
| CycloneDX SBOM | `data/results/report-real-conversations/sbom.cdx.json` |
| OSV output | `data/results/report-real-conversations/osv-vulnerabilities.json` |
| Source validation | `data/results/source-validation/conversations-report-validation/source-validation.md` |

Current report result:

```text
Detected Maven components: 9
Native file components: 2
OSV vulnerabilities: 0
```

After adding the source-used `com.google.code.gson:gson@2.13.1` reference to calibration, source validation improved to:

```text
SBOM components: 9
Confirmed: 6
Version mismatches: 2
Missing: 1
```

Confirmed components:

- `androidx.exifinterface:exifinterface@1.4.2`
- `com.squareup.retrofit2:retrofit@3.0.0`
- `com.google.code.gson:gson@2.13.1`
- `androidx.swiperefreshlayout:swiperefreshlayout@1.2.0`
- `androidx.appcompat:appcompat@1.7.1`
- `androidx.recyclerview:recyclerview@1.2.1`

Remaining mismatches:

- `androidx.concurrent:concurrent-futures`: selected `1.1.0`, source resolves `1.3.0`.
- `androidx.startup:startup-runtime`: selected `1.1.1`, source resolves `1.2.0`.

Both remaining mismatches are close-score AndroidX version ambiguities. They should not be forced by a generic "choose the newest near-tie" rule because that would risk false version claims on other APKs.

Remaining missing/equivalence nuance:

- `androidx.lifecycle:lifecycle-runtime-android@2.9.4` is emitted as a bytecode-bearing Android target variant, while the Gradle source tree reports the public coordinate `androidx.lifecycle:lifecycle-runtime@2.6.2`. Treat this as an artifact-family validation nuance, not a clean confirmed version.

## Reproduction Commands

Generate the APK report:

```powershell
docker compose run --rm apk-sbom python -m apk_sbom.cli generate-report data/test_apks/real/conversations/conversations.apk --output-dir data/results/report-real-conversations --db-path data/reference_db/reference_features_calibrated_combined.sqlite --top 30
```

Generate the source dependency tree:

```powershell
docker compose run --rm -e GRADLE_USER_HOME=/app/data/source/.gradle-cache-conversations apk-sbom sh -lc "rm -rf /app/data/source/conversations/extracted && mkdir -p /app/data/source/conversations/extracted /app/data/results/source-validation/conversations && tar -xf /app/data/source/conversations/source.tar.gz -C /app/data/source/conversations/extracted && cd /app/data/source/conversations/extracted/eu.siacs.conversations_4217704_src.tar.gz && /opt/gradle/bin/gradle --no-daemon dependencies --configuration conversationsFreeReleaseRuntimeClasspath > /app/data/results/source-validation/conversations/conversationsFreeReleaseRuntimeClasspath.txt 2> /app/data/results/source-validation/conversations/gradle-error.log"
```

Validate the SBOM against source:

```powershell
docker compose run --rm apk-sbom python -m apk_sbom.cli validate-source-deps --sbom data/results/report-real-conversations/sbom.cdx.json --dependency-tree data/results/source-validation/conversations/conversationsFreeReleaseRuntimeClasspath.txt --output-dir data/results/source-validation/conversations-report-validation
```

## Interpretation

Conversations should be presented as a realistic partial-version-mismatch case. It strengthens the dataset diversity because it is a modern security/messaging app with multidex, R8/minify, native libraries, and a source dependency tree. It should not be used as a clean precision claim because the current MVP still has AndroidX near-version ambiguity and one Lifecycle artifact-family validation nuance.
