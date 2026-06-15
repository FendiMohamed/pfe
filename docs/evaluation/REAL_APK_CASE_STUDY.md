# Real APK Case Study

This note records the first real-world APK experiment for the APK-to-SBOM MVP.

Unlike the controlled fixtures, this APK does not have a project-owned ground-truth SBOM. Treat this case study as a practical behavior test, not as a formal precision/recall measurement.

## Input APK

| Field | Value |
|---|---|
| APK | `data/test_apks/real/F-Droid.apk` |
| SHA-256 | `985f5181d48bb6bafd54083a048b391271e0ab28385881cc41294fb01a222762` |
| Size | 12,426,276 bytes |
| DEX files | `classes.dex`, `classes2.dex` |
| Multidex | true |
| Native `.so` files | 4 |

Native files found:

| Path | ABI | Size | SHA-256 |
|---|---|---:|---|
| `lib/arm64-v8a/libandroidx.graphics.path.so` | arm64-v8a | 10,096 | `41e9a793c43a0f4fddb19e33f346bace464f30f888ba7b9eaf96294ea115bfb6` |
| `lib/armeabi-v7a/libandroidx.graphics.path.so` | armeabi-v7a | 7,252 | `41399eba6fc2a60f6f14642375c1824f3cf25eb8fec7397d753730a3ceda3e2b` |
| `lib/x86/libandroidx.graphics.path.so` | x86 | 9,284 | `eb0570b41fd3bff25d8204a967c03bd7550719e768b791f680cc40cbe35f29af` |
| `lib/x86_64/libandroidx.graphics.path.so` | x86_64 | 10,760 | `4e56c996f13670e70082658de7880c4020eabf4f25e43387f88ed78a713fc9f0` |

## Generated Artifacts

Initial report artifacts:

| Artifact | Path |
|---|---|
| Match details | `data/results/report-real-f-droid/matches.json` |
| CycloneDX SBOM | `data/results/report-real-f-droid/sbom.cdx.json` |
| OSV results | `data/results/report-real-f-droid/osv-vulnerabilities.json` |
| JSON report | `data/results/report-real-f-droid/report.json` |
| Markdown report | `data/results/report-real-f-droid/report.md` |

Expanded reference DB report artifacts:

| Artifact | Path |
|---|---|
| Match details | `data/results/report-real-f-droid-expanded-db/matches.json` |
| CycloneDX SBOM | `data/results/report-real-f-droid-expanded-db/sbom.cdx.json` |
| OSV results | `data/results/report-real-f-droid-expanded-db/osv-vulnerabilities.json` |
| JSON report | `data/results/report-real-f-droid-expanded-db/report.json` |
| Markdown report | `data/results/report-real-f-droid-expanded-db/report.md` |

Disambiguated report artifacts:

| Artifact | Path |
|---|---|
| Match details | `data/results/report-real-f-droid-disambiguated/matches.json` |
| CycloneDX SBOM | `data/results/report-real-f-droid-disambiguated/sbom.cdx.json` |
| OSV results | `data/results/report-real-f-droid-disambiguated/osv-vulnerabilities.json` |
| JSON report | `data/results/report-real-f-droid-disambiguated/report.json` |
| Markdown report | `data/results/report-real-f-droid-disambiguated/report.md` |

HTML report artifact:

| Artifact | Path |
|---|---|
| Static HTML report | `data/results/report-real-f-droid-html/report.html` |

Source dependency validation artifacts:

| Artifact | Path |
|---|---|
| Validation summary | `data/results/source-validation/fdroid/validation-summary.md` |
| Full runtime tree | `data/results/source-validation/fdroid/app-fullReleaseRuntimeClasspath.txt` |
| OkHttp dependency insight | `data/results/source-validation/fdroid/insight-okhttp.txt` |
| Okio dependency insight | `data/results/source-validation/fdroid/insight-okio.txt` |
| Ktor OkHttp dependency insight | `data/results/source-validation/fdroid/insight-ktor-client-okhttp-jvm.txt` |
| Ktor HTTP dependency insight | `data/results/source-validation/fdroid/insight-ktor-http-jvm.txt` |

## Source Validation

The F-Droid client source repository was cloned from `https://gitlab.com/fdroid/fdroidclient` at tag `1.23.2`.

| Evidence | Result |
|---|---|
| Source checkout | `data/source/fdroidclient-1.23.2` |
| Tag | `1.23.2` |
| Tag commit | `0ea06b1c1d68765c4a434d0b676b3e0f23f04cb1` |
| APK metadata | package `org.fdroid.fdroid`, versionName `1.23.2`, versionCode `1023052` |
| Source metadata | `app/build.gradle` declares `versionCode 1023052`; `versionName` is generated from the checked-out Git tag. |

Relevant source dependency evidence:

| Source evidence | Meaning |
|---|---|
| `app/build.gradle` line 207: `implementation libs.okhttp` | The app directly depends on OkHttp. |
| `gradle/libs.versions.toml` line 13: `okhttp = "4.12.0"` | The source version for OkHttp is `4.12.0`. |
| `gradle/libs.versions.toml` line 131: `okhttp = { module = "com.squareup.okhttp3:okhttp", version.ref = "okhttp" }` | `libs.okhttp` maps to `com.squareup.okhttp3:okhttp`. |
| `libs/download/build.gradle` line 56: `implementation libs.ktor.client.okhttp` | The download module uses Ktor's OkHttp engine. |
| `gradle/libs.versions.toml` lines 12 and 130 | Ktor is version `2.3.12`, and `libs.ktor.client.okhttp` maps to `io.ktor:ktor-client-okhttp`. |

This turns the real APK case study from an unverified behavior test into a partial ground-truth check:

| MVP result | Source validation | Interpretation |
|---|---|---|
| `com.squareup.okhttp3:okhttp@4.10.0` | Source directly declares `com.squareup.okhttp3:okhttp@4.12.0`. | Library identity is correct, but version is wrong because `4.12.0` is absent from the current reference DB. |
| `com.squareup.okio:okio@2.8.0` | Not directly declared in the source version catalog; Okio is likely transitive through OkHttp/Ktor, but exact source-resolved version was not confirmed here. | Low-confidence candidate; do not treat as confirmed. |
| `com.squareup.okio:okio-jvm@3.0.0` | Not directly declared in the source version catalog; exact source-resolved version was not confirmed here. | Low-confidence candidate; do not treat as confirmed. |

The `gradle/verification-metadata.xml` file contains OkHttp and Okio artifacts, including newer Okio 3.x artifacts, but it is dependency verification metadata rather than a clean dependency lockfile. It is useful supporting evidence, not exact ground truth by itself.

## Initial Detection Result

| Component | MVP version | Decision | Confidence | Source validation | Notes |
|---|---:|---|---:|---|---|
| `com.squareup.okhttp3:okhttp` | 4.10.0 | likely/medium | 0.775 | Partial: component identity confirmed, version incorrect. | Strong evidence selected the nearest available reference version, but the source declares `4.12.0`, which is missing from the reference DB. |
| `com.squareup.okio:okio` | 2.8.0 | candidate/low | 0.557 | Unconfirmed. | Lower-confidence candidate; nearby version `2.9.0` is close, and current DB lacks newer source-relevant Okio 3.x variants. |
| `com.squareup.okio:okio-jvm` | 3.0.0 | candidate/low | 0.472 | Unconfirmed. | Low-confidence candidate; may overlap conceptually with Okio because both artifacts share package-level evidence. |

Uncertain candidates were not included in the SBOM:

| Component | Selected version | Score | Reason for exclusion |
|---|---:|---:|---|
| `com.google.code.gson:gson` | 2.8.5 | 0.170 | No package/class/method evidence; only weak generic opcode/literal similarity. |
| `com.squareup.retrofit2:retrofit` | 2.9.0 | 0.167 | No package/class/method evidence; weak similarity only. |
| `commons-codec:commons-codec` | 1.15 | 0.149 | Very small gap between versions and weak evidence. |
| `com.fasterxml.jackson.core:jackson-databind` | 2.15.2 | 0.142 | Weak evidence and no reliable identity-level overlap. |

## Expanded Reference DB Rerun

After source validation, the reference DB was expanded with:

- `com.squareup.okhttp3:okhttp@4.12.0`
- `com.squareup.okio:okio-jvm@3.6.0`
- `com.squareup.okio:okio-jvm@3.7.0`
- Ktor JVM modules at `2.3.12`: `ktor-client-core-jvm`, `ktor-client-okhttp-jvm`, `ktor-http-jvm`, `ktor-io-jvm`, and `ktor-utils-jvm`

The rebuilt reference feature DB contains 27 components, 27 DEX files, 294 packages, 7,441 classes, 69,220 methods, 3,371 opcode rows, 25,197 class dependency edges, 371 dependency shape rows, and 17,108 string literals.

Expanded report result:

| Component | MVP version | Decision | Confidence | Source validation | Notes |
|---|---:|---|---:|---|---|
| `com.squareup.okhttp3:okhttp` | 4.12.0 | likely/medium | 0.807 | Confirmed. | The matcher now selects the source-declared version after it was added to the reference DB. |
| `io.ktor:ktor-client-okhttp-jvm` | 2.3.12 | likely/medium | 0.788 | Partial/strong. | Source declares Ktor's OkHttp engine at `2.3.12`; the JVM artifact is the bytecode variant used for reference matching. |
| `com.squareup.okio:okio` | 2.8.0 | candidate/low | 0.557 | Unconfirmed. | Still a low-confidence candidate; exact artifact/version should not be treated as ground truth. |
| `com.squareup.okio:okio-jvm` | 3.7.0 | candidate/low | 0.543 | Unconfirmed. | More source-relevant than `3.0.0`, but the gap to `3.6.0` is tiny, so version certainty remains low. |
| `io.ktor:ktor-http-jvm` | 2.3.12 | candidate/low | 0.456 | Likely transitive/supporting evidence. | Useful signal but below the likely threshold. |

Before/after comparison:

| Question | Initial DB result | Expanded DB result | Interpretation |
|---|---|---|---|
| Can the MVP identify OkHttp? | Yes, but as `4.10.0`. | Yes, as `4.12.0`. | Reference coverage fixed the source-confirmed version miss. |
| Can the MVP identify Ktor? | No Ktor references were available. | `ktor-client-okhttp-jvm@2.3.12` likely/medium, `ktor-http-jvm@2.3.12` candidate/low. | Adding source-relevant references exposed Ktor bytecode evidence. |
| Are Okio findings confirmed? | No. | Still no. | Related-artifact overlap is now handled for SBOM output, but exact Okio confirmation still needs dependency-tree validation. |

## Artifact-Family Disambiguation Rerun

The expanded DB still produced overlapping Okio-family candidates:

- `com.squareup.okio:okio@2.8.0`, score `0.557`
- `com.squareup.okio:okio-jvm@3.7.0`, score `0.543`

These artifacts share package and bytecode evidence, but APK DEX matching should prefer the JVM bytecode artifact when the scores are close. The matcher now keeps raw version decisions for auditability but filters detected SBOM/report components through a known artifact-family rule.

Disambiguated report result:

| Component | MVP version | Decision | Confidence | Notes |
|---|---:|---|---:|---|
| `com.squareup.okhttp3:okhttp` | 4.12.0 | likely/medium | 0.807 | Source-confirmed direct dependency and version. |
| `io.ktor:ktor-client-okhttp-jvm` | 2.3.12 | likely/medium | 0.788 | Source-confirmed Ktor OkHttp engine family. |
| `com.squareup.okio:okio-jvm` | 3.7.0 | candidate/low | 0.543 | Kept as the preferred JVM artifact for the Okio family; still low-confidence. |
| `io.ktor:ktor-http-jvm` | 2.3.12 | candidate/low | 0.456 | Likely transitive/supporting Ktor evidence. |

The suppressed `okio@2.8.0` candidate is still visible in `matches.json` and in the raw version-decision table, but it is no longer emitted as a CycloneDX component.

## Gradle Dependency-Tree Validation

To validate the final SBOM against source-resolved dependencies, Gradle was run on the matching F-Droid source tag with the `:app:fullReleaseRuntimeClasspath` configuration. The full dependency tree and targeted `dependencyInsight` outputs are saved under `data/results/source-validation/fdroid/`.

Resolved source evidence:

| Dependency | Source-resolved result | Evidence |
|---|---|---|
| `com.squareup.okhttp3:okhttp` | `4.12.0` | `insight-okhttp.txt` shows `com.squareup.okhttp3:okhttp:4.12.0` in `fullReleaseRuntimeClasspath`. |
| `io.ktor:ktor-client-okhttp-jvm` | `2.3.12` | `insight-ktor-client-okhttp-jvm.txt` shows it via `io.ktor:ktor-client-okhttp:2.3.12` and project `:libs:download`. |
| `io.ktor:ktor-http-jvm` | `2.3.12` | `insight-ktor-http-jvm.txt` shows `io.ktor:ktor-http-jvm:2.3.12`. |
| `com.squareup.okio:okio-jvm` | `3.7.0` | `insight-okio.txt` shows `com.squareup.okio:okio-jvm:3.7.0`; the full tree also shows `com.squareup.okio:okio:3.6.0 -> 3.7.0`. |

Final MVP-to-source comparison:

| MVP SBOM component | MVP decision | Source validation | Interpretation |
|---|---|---|---|
| `com.squareup.okhttp3:okhttp@4.12.0` | likely/medium | Confirmed. | Correct identity and version. |
| `io.ktor:ktor-client-okhttp-jvm@2.3.12` | likely/medium | Confirmed. | Correct identity and version for the JVM bytecode artifact. |
| `com.squareup.okio:okio-jvm@3.7.0` | candidate/low | Confirmed. | Correct source-resolved version, but still low-confidence from APK bytecode evidence. |
| `io.ktor:ktor-http-jvm@2.3.12` | candidate/low | Confirmed. | Correct source-resolved version, but still low-confidence/supporting evidence. |

Suppressed candidate check:

| Candidate | Source validation | Interpretation |
|---|---|---|
| `com.squareup.okio:okio@2.8.0` | Not present in `fullReleaseRuntimeClasspath`; Gradle resolves Okio to `3.7.0`. | Correctly suppressed from the final SBOM. |

This comparison is now automated by the MVP:

```powershell
docker compose run --rm apk-sbom python -m apk_sbom.cli validate-source-deps --sbom data/results/report-real-f-droid-disambiguated/sbom.cdx.json --dependency-tree data/results/source-validation/fdroid/app-fullReleaseRuntimeClasspath.txt --output-dir data/results/source-validation/fdroid-auto --candidate com.squareup.okio:okio@2.8.0
```

Automated validation output:

| Group | Components | Confirmed | Version mismatch | Missing |
|---|---:|---:|---:|---:|
| SBOM components | 4 | 4 | 0 | 0 |
| Extra candidates | 1 | 0 | 1 | 0 |

## Vulnerability Result

OSV was queried for the detected Maven components in the generated CycloneDX SBOM.

Initial report:

| Component | Version | Advisory | CVE alias | Summary |
|---|---:|---|---|---|
| `com.squareup.okio:okio` | 2.8.0 | `GHSA-w33c-445m-f8w7` | `CVE-2023-3635` | Okio Signed to Unsigned Conversion Error vulnerability |
| `com.squareup.okio:okio-jvm` | 3.0.0 | `GHSA-w33c-445m-f8w7` | `CVE-2023-3635` | Okio Signed to Unsigned Conversion Error vulnerability |

Expanded report:

| Component | Version | Advisory | CVE alias | Summary |
|---|---:|---|---|---|
| `com.squareup.okio:okio` | 2.8.0 | `GHSA-w33c-445m-f8w7` | `CVE-2023-3635` | Okio Signed to Unsigned Conversion Error vulnerability |

Disambiguated report:

| Result | Meaning |
|---|---|
| 0 OSV findings | The questionable `okio@2.8.0` component was suppressed from the SBOM, so OSV no longer reports the unconfirmed Okio CVE signal. |

After source validation and the expanded DB rerun, the `CVE-2023-3635` finding should be treated as a discarded potential signal rather than a confirmed vulnerability for this APK.

## Interpretation

This experiment shows that the MVP can process a real multidex APK end to end:

- extract DEX and native files,
- analyze both DEX files,
- match against the local Maven reference DB,
- generate CycloneDX,
- include native `.so` files as hash-only evidence,
- query OSV and recover CVE aliases.

The strongest identity-level detection is OkHttp. Source validation first showed that the app depends on OkHttp `4.12.0`, while the initial MVP emitted `4.10.0`. After adding `4.12.0` to the reference DB, the MVP selected the correct source-confirmed version. This is a concrete positive result: the architecture can recover the correct version when the reference DB contains it.

The Ktor result is also useful: once Ktor `2.3.12` JVM references were added, the MVP detected `ktor-client-okhttp-jvm@2.3.12` with likely/medium confidence, matching the source-level use of the Ktor OkHttp engine.

The Okio detections are still useful but lower-confidence. The new artifact-family rule improves SBOM quality by keeping the JVM artifact and suppressing the overlapping legacy artifact. The source dependency-tree validation confirms `okio-jvm@3.7.0`, but the APK-side matcher should still label it as candidate/low because its bytecode evidence is weaker than OkHttp.

## Limitations

- This case study does not prove accuracy because no ground-truth SBOM is attached.
- The reference DB is small, so many libraries in a real app may be absent from the search space.
- Source validation confirms that missing reference versions can turn a correct library-family detection into an incorrect version decision; the expanded DB rerun fixed this for OkHttp.
- The current matcher can produce overlapping raw candidates for related artifacts, such as `okio` and `okio-jvm`; the SBOM/report component layer now suppresses the known Okio overlap, but this is currently a small hand-coded family rule.
- The current MVP does not automatically resolve Gradle transitive dependencies from source; this case study used Gradle manually as external validation.
- Native `.so` files are included as CycloneDX `file` components with hashes only; no native package/version identification is claimed.
- Trivy/Grype and CycloneDX CLI validation were not run because those tools are still optional/missing in the current container.

## Supervisor-Friendly Takeaway

The real APK experiment supports the MVP architecture as a practical prototype: it works on a multidex APK, produces a standard SBOM, and connects detected versions to vulnerability data. The most important result is the before/after evidence: the initial DB found OkHttp but missed the version; after adding the source-confirmed version, the MVP selected `okhttp@4.12.0`. The artifact-family rerun also shows that vulnerability output improves when overlapping Maven artifacts are handled carefully: the unconfirmed `okio@2.8.0` CVE signal disappeared from the final SBOM result. Finally, the Gradle dependency-tree validation confirms that every Maven component emitted by the final disambiguated SBOM is present in the source-resolved runtime classpath.
