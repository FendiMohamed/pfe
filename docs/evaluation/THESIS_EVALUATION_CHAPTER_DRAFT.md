# Evaluation and Results Chapter Draft

This chapter evaluates the APK-to-SBOM MVP as a practical static-analysis tool, not as a perfect library/version oracle. The goal is to measure when the tool produces trustworthy Maven package and version evidence, when it produces useful partial evidence, and when it should deliberately avoid a strong claim. This framing follows the main observation from the related work: real Android APKs are diverse, and factors such as R8 optimization, dependency era, multidex packaging, AndroidX/Kotlin target artifacts, native code, and hidden payloads affect version-level detection.

The evaluation is therefore organized by dataset layer and APK family. Clean source-validated cases show the best attainable behavior under strong reference coverage. Partial source-validated cases show the harder real-world behavior that should not be hidden. Blocked and limitation cases are kept visible, but they are excluded from accuracy metrics when the required ground truth is not available or when the case falls outside the exact Maven-version scope.

## Evaluation Objectives

The evaluation answers four questions:

1. Can the MVP recover exact Maven component versions on controlled APKs with known ground truth?
2. Can the MVP produce source-confirmed emitted Maven versions on real APKs when a matching source dependency tree is available?
3. How does behavior change across APK families such as clean Android apps, modern AndroidX/Kotlin apps, R8/minified apps, old-dependency apps, large dependency trees, native-heavy apps, and hidden-code cases?
4. Can the generated CycloneDX SBOM support vulnerability lookup while preserving confidence and uncertainty labels?

The evaluation deliberately avoids using a single perfect-looking score. A global number without the clean/partial/boundary split would hide the most important research result: the same matcher can behave very differently depending on the APK family and the available reference versions.

## Dataset Layers

The controlled dataset contains 72 generated APK fixtures with 84 expected Maven component versions. These fixtures include clear version-band bytecode, R8 rename, R8 shrink, R8 optimize, R8 shrink plus optimize, package flattening/repackaging, inline-like call-site stress, multidex packaging, and multi-library cases. Because the ground truth is known by construction, this layer validates the mechanics of feature extraction, matching, version selection, confidence labeling, SBOM generation, and vulnerability lookup.

The real source-validated dataset contains 100 open-source Android APKs with resolved source dependency evidence. It is split into 5 clean cases and 95 partial cases. The clean cases are F-Droid, OpenTracks, Tusky, Daily Dozen, and QuickDic. The partial cases include NewPipe, AntennaPod, KDE Connect, Wikipedia Android, Conversations, Aegis Authenticator, Markor, Nextcloud Android, FairEmail, VLC, OsmAnd, Material Files, Jitsi Meet, K-9 / Thunderbird Android, the category-growth cases, the low-risk no-native cases, and the clean-candidate sweep rows through v16, including OceanNex, Praktika Vortaro, MsgGo, AF Weather Widget, Study Tracker, Calliope mini, F-Droid Build Status, Password Master, and Todo List (PFA). These partial cases are not discarded; they are the strongest evidence for how the tool behaves on difficult APK families.

The current source-linked blocked set contains Flying Carpet and FitoTrack. Both have APK/source/report evidence from v16, but neither produced a resolved runtime dependency tree, so both are excluded from source-validated metrics. Earlier blocked rows were rescued only after dependency-tree capture and `validate-source-deps` succeeded: Baby Books, Odysee, and RadarWeather moved through targeted v14 validation-only rescue lanes; Poet Assistant moved through a JCenter-to-Maven-Central validation copy at 7/37; Ultrasonic moved through strict `:ultrasonic` module probing at 12/39, RunnerUp through strict `latestReleaseRuntimeClasspath` flavor probing at 16/39, ImapNotes3 through strict `:ImapNotes3` module probing at 11/39, and Password Master through strict `:passwordmaster` probing at 13/18.

Four limitation or boundary cases are also excluded from accuracy metrics: Organic Maps, Termux, the hidden-DEX loader fixture, and the Simplify obfuscated sample. These cases are used to demonstrate scope boundaries. Native `.so` files are reported as hash-only CycloneDX file components, and hidden/nonstandard DEX indicators raise risk warnings instead of producing unsupported Maven package claims.

## Metrics

For controlled APKs, the main metric is exact expected-version confirmation: the number of expected Maven component versions detected with the correct coordinate and version.

For real APKs, the main metric is the emitted Maven version confirmation rate. This means:

```text
confirmed emitted Maven versions / checked emitted Maven versions
```

This metric is intentionally narrower than full dependency recall. It checks whether the Maven components emitted by the tool are confirmed by the source dependency tree. It does not claim that every dependency resolved by Gradle must appear in the APK bytecode or must be recovered by the static matcher.

The validation also records version mismatches and missing or nuanced cases. A mismatch means the emitted coordinate is present in source evidence but the selected version differs. A missing or nuanced case means validation requires extra interpretation, such as a public artifact versus Android-target artifact-family difference.

## Main Results

| Dataset slice | Cases | Checked emitted versions | Confirmed | Mismatches | Missing/nuance | Rate |
|---|---:|---:|---:|---:|---:|---:|
| Controlled APKs | 72 | 84 | 84 | 0 | 0 | 100.0% |
| Clean source-validated real APKs | 5 | 47 | 47 | 0 | 0 | 100.0% |
| Partial source-validated real APKs | 95 | 1755 | 864 | 617 | 274 | 49.2% |
| All source-validated real APKs | 100 | 1802 | 911 | 617 | 274 | 50.6% |

The controlled fixtures confirm that the MVP implementation can recover exact versions when the dependency is represented in the reference database and the bytecode evidence is not ambiguous. The 84/84 result validates the pipeline mechanics across clear version-band, controlled obfuscation, networking/Kotlin-era, Ktor framework, and multidex/multi-library cases, but it is not a claim of perfect real-world coverage.

The clean real APK slice confirms 47/47 emitted Maven versions across 5 APKs. This is the strongest exact-version evidence because the outputs are validated against real source dependency trees. However, these clean cases alone should not be presented as the whole result, because Tusky, Daily Dozen, and QuickDic are sparse and clean cases do not represent all APK families.

The partial real APK slice confirms 864/1755 emitted Maven versions across 95 APKs, for a 49.2% emitted Maven version confirmation rate. These are useful results, not failures. They show that the tool can recover meaningful SBOM evidence on difficult apps, while still exposing version-band ties, artifact-family ambiguity, native hash-only boundaries, and reference-coverage limits.

Across all 100 source-validated real APKs, the tool confirms 911/1802 emitted Maven versions, giving a 50.6% emitted Maven version confirmation rate. This is the best single summary number, but it should always be reported together with the clean/partial split.

## Per-APK Interpretation

F-Droid, OpenTracks, Tusky, Daily Dozen, and QuickDic are clean source-validated cases. F-Droid and OpenTracks validate richer emitted SBOMs, while Tusky, Daily Dozen, and QuickDic are clean but sparse because only one or two Maven components are emitted. These sparse clean rows are useful evidence, but they should not dominate the accuracy story.

NewPipe, AntennaPod, KDE Connect, Wikipedia Android, Conversations, Aegis Authenticator, FairEmail, Nextcloud, VLC Android, OsmAnd, Material Files, Jitsi Meet, Gotify, BetterCounter, Coffee, MedTimer, Doodle, Simple Time Tracker, and KeePassVault represent modern AndroidX/Kotlin, React Native/framework-boundary, native-heavy media, file-manager/network-storage, security/password-manager, and no-native clean-candidate behavior. These apps show that identity recovery is often useful even when exact version selection remains difficult. Coffee is near-clean at 10/11 confirmed, Jitsi validates 5/7 emitted Maven versions while keeping React Native/WebRTC native files hash-only, MedTimer adds a larger no-native multidex row at 12/18 confirmed, and KeePassVault adds dependency-rich no-native security evidence at 8/24 confirmed. They remain partial because their remaining rows mismatch source-resolved versions or require artifact-family nuance. The remaining mismatches are concentrated in near-version AndroidX ties, Compose/Kotlin/coroutines drift, Okio/OkHttp drift, Android-target artifact variants, older source-resolved dependency versions, and version-band cases where bytecode features are very similar across releases.

Markor is an older-dependency profile. A targeted source-used-version experiment can improve Markor, but global inclusion of the broader older-version set regressed cleaner cases. A guarded follow-up promoted only `androidx.core:core@1.9.0`, improving Markor without changing the other controls. This shows that reference coverage helps, but every shared promotion still needs current-control evidence.

Nextcloud Android is the largest modern stress case in the current dataset. Guarded calibration improved it without hiding the remaining risky ties. Versions that improved only Nextcloud but regressed other controls were preserved as experiment evidence instead of being promoted into the shared calibrated database.

K-9 / Thunderbird Android is now source-validated partial after a validation-only plugin-lite included-build rescue. It confirms 5/11 emitted Maven versions and remains a partial case, not clean evidence, because the source tree had to be reduced only for dependency-tree capture. Organic Maps and Termux demonstrate native-heavy boundaries, Jitsi Meet keeps React Native/WebRTC/Hermes native files as hash-only boundary evidence, and the hidden-DEX fixture demonstrates nonstandard code-loading risk. These cases are important for thesis credibility because they show where the MVP refuses to overclaim.

## SBOM and Vulnerability Results

The MVP emits CycloneDX SBOMs with Maven package URLs, versions, confidence properties, evidence summaries, and native file components. Native `.so` files are represented as file components with hashes, sizes, paths, and ABIs, not as Maven package/version claims.

The vulnerability workflow is demonstrated with one clean negative case and one controlled positive case. The calibrated F-Droid report emits source-confirmed Maven components and returns 0 OSV vulnerabilities. The controlled vulnerable Jackson Databind fixture detects `com.fasterxml.jackson.core:jackson-databind@2.9.10.8`, and OSV returns 3 confirmed HIGH advisories: `CVE-2020-36518`, `CVE-2022-42003`, and `CVE-2022-42004`.

Vulnerability results are confidence-aware. A high-confidence exact version can support a confirmed finding. A low-confidence or ambiguous version candidate should be treated as a potential finding until source validation or stronger evidence confirms it.

## Discussion

The results support the main design choice of the MVP: combine static bytecode features with calibrated reference evidence, confidence labels, and explicit scope boundaries. The tool is strongest when the reference database contains the source-used version and when bytecode features differ enough across versions. It remains useful but less exact when multiple nearby AndroidX or Kotlin-era versions share almost identical bytecode evidence.

The partial cases are especially important. Hiding them would make the tool look cleaner, but it would weaken the research. The state of the art already shows that Android library detection and version identification degrade under realistic conditions. Reporting partial results by APK family makes the evaluation more honest and more useful: it shows what kind of APKs the MVP handles well, what kind of APKs produce near-version uncertainty, and where future work should focus.

The experiments also show why generic recency rules are risky. Several source-used versions improved one app but regressed others. Therefore, the MVP keeps risky ties visible unless there is independent evidence such as coherent dependency metadata, app-era support, or source validation.

The reporting layer now treats near-version uncertainty as a first-class output. Feature-equivalent ties and very close version-score ties without matched version-unique evidence are labeled as version ambiguity in the report evidence, rather than being hidden behind a single exact-looking version. The ambiguous version set is also exported as structured report data and a CycloneDX component property, so downstream consumers can distinguish a strong exact version from a nearby-version hypothesis. This improves the tool by reducing unsupported certainty while preserving the selected candidate for downstream SBOM and vulnerability workflows.

## Threats to Validity

The real APK dataset is still smaller than the long-term target. It is diverse enough for MVP evidence, but it does not replace a larger benchmark with dozens of source-validated apps and hundreds of smoke-test APKs.

Source dependency trees are strong validation evidence, but they are not perfect bytecode ground truth. Gradle may resolve dependencies that are not packaged into the final APK, and some dependencies may be transformed, shaded, optimized, or removed during the build.

The reference database affects results directly. If the correct version is absent, the matcher may choose a nearby version or report ambiguity. Adding more versions can improve one APK while regressing another, so expansion must be calibrated and regression-tested.

Native library identification is outside the current exact Maven-version scope. The MVP reports native files with hashes and metadata, but it does not identify native package names or versions.

Commercial packers, dynamic code loading, and hidden DEX payloads are not solved by this MVP. The intended behavior for these cases is to raise extraction and obfuscation risk indicators, not to invent unsupported SBOM claims.

## Conclusion

The MVP demonstrates a credible APK-to-SBOM pipeline: it extracts compiled APK evidence, matches third-party Maven libraries, estimates versions with confidence labels, emits CycloneDX SBOMs, and supports OSV vulnerability lookup. It achieves perfect confirmation on the controlled fixture layer and clean source-validated real APK layer, while the harder real APK layer confirms 864/1755 emitted Maven versions and exposes the remaining uncertainty honestly.

The main result is not that the tool is perfect. The main result is that it is useful, measurable, and transparent about uncertainty. That makes it a stronger PFE contribution than a cosmetically perfect score, because it reflects how Android library detection behaves in realistic conditions.
