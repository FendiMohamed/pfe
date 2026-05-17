# Updated Synthesis Table: Android TPL Detection, SBOM Tools, and Vulnerability Sources

Purpose: updated supervisor-ready table that separates academic Android TPL detection tools from practical SBOM and vulnerability tools.

Important note: reported accuracy and speed values are not directly comparable across all papers because datasets, hardware, obfuscation settings, and evaluation protocols differ.

## Legend

| Mark | Meaning |
|---|---|
| Strong | Directly useful for this capability. |
| Partial | Useful but limited or indirect. |
| Weak | Not suitable as a primary solution. |
| No | Not supported. |
| Unknown | Not clearly available from accessible paper/tool information. |

## A. Academic Android TPL Detection Tools

| Tool / paper | Year | Main method | Version-level support | Obfuscation / R8 handling | SBOM output | Open-source / reusable? | Strength for MVP | Main limitation |
|---|---:|---|---|---|---|---|---|---|
| LibRadar | 2016 | API frequency, package clustering, large-scale detection. | Weak | Partial for renaming; weak for shrinking/R8. | No | Public/archived implementations exist. | Fast candidate generation. | Not enough for exact version or SBOM. |
| LibScout | 2016 | Reference profiles, package/class/method hierarchy, fuzzy descriptors. | Strong for known versions | Strong for identifier renaming; weaker for dead-code removal/R8. | No standard SBOM | Public GitHub available. | Reference DB and exact-version baseline. | Older and fragile under modern optimization. |
| LibSift | 2016 | Package dependency graph and module decoupling. | No | Partial, because it uses dependency structure. | No | Research availability varies. | Segmentation of app vs library code. | Does not identify exact component/version. |
| LibD | 2017 | Homogeny graph, call/inheritance/inclusion relations, scalable clustering. | Weak | Stronger than package names for renaming. | No | Partial/reproducibility limited. | Graph-based grouping and scalability. | Not a direct SBOM/version detector. |
| ORLIS | 2018 | Fuzzy structural matching using method/class/call-graph style features. | Partial | Designed for common obfuscation; not fully R8-proven. | No | Harder setup. | Obfuscation-resilient matching ideas. | Slower and not standard SBOM-oriented. |
| LibPecker | 2018 | Class dependency signatures and adaptive class similarity. | Partial | Partial against renaming, some control-flow/string changes. | No | Availability varies. | CDG/class structural matching. | Not primarily exact-version/SBOM. |
| LibID | 2019 | CFG/basic-block/class signatures, containment matching, LSH, optimization constraints. | Strong | Handles renaming, shrinking, control-flow randomization, package flattening. | No | Availability varies. | Robust version matching ideas. | Complex to reproduce fully. |
| Obfuscapk | 2020 | APK obfuscation framework. | No | Generates obfuscation cases. | No | Open-source. | Evaluation dataset generation. | Not a detector. |
| ATVHunter | 2021 | CDG module decoupling, CFG coarse filter, opcode/basic-block fine matching. | Strong | Good for common obfuscation; not fully R8-specific. | Partial security report, no standard SBOM | Online/source availability limited. | Best inspiration for version-to-CVE pipeline. | Full database and CFG pipeline are heavy. |
| LibRARIAN | 2021 | Native `.so` version identification using binary features. | Strong for native libraries | Handles stripped native binaries better than simple matching. | No standard SBOM | Research tool/data availability varies. | Native component phase 2. | Separate native-code problem. |
| DroidReach | 2022 | Java-to-native vulnerability reachability analysis. | Not a detector | Not obfuscation-centered. | No | Research availability varies. | Future VEX/reachability extension. | Requires prior component/vulnerability detection. |
| LibScan | 2023 | Class correspondence, method opcode similarity, call-chain opcode similarity, caching. | Strong | Handles several obfuscations but R8 remains challenging. | No | Code availability not clearly reusable. | Staged matcher design. | Complex and still R8-sensitive. |
| LibHunter | 2024 | R8-aware optimization-resilient matching. | Stronger than older tools but still hard | Directly targets R8/shrinking/optimization. | No standard SBOM | GitHub exists, but reuse/license/quality must be checked. | R8 evaluation and design lessons. | Exact version remains difficult under hard R8. |
| LibAttention | 2025 | Feature language model / Transformer over Smali-like features. | Weak/limited | Strong R8-focused library presence detection. | No | Availability unclear. | Future ML extension. | Heavy training, less explainable, not ideal for exact SBOM. |
| SAD | 2025 | CDG node features, class summaries, structural similarity, literal tie-breakers. | Strong | Stronger under obfuscation; still affected by heavy optimization. | No standard SBOM | Availability unclear. | Main inspiration for version-level CDG scoring. | Implementation complexity. |
| LibMD | 2025 | Multi-scale dependency fusion and Bayesian posterior scoring. | Strong, according to accessible abstract/info | Designed for obfuscation and adjacent-version ambiguity. | Reported SBOM-oriented goal | Not publicly released from available info. | Future ideal architecture. | Full paper/code not fully accessible; too complex for first MVP. |
| DroidNative | 2025 | Large-scale native Android library indexing. | Strong for native | Native-focused. | No standard SBOM | Research availability varies. | Future native reference DB. | Not part of first DEX MVP. |
| Revisiting TPL Detection | 2025 | Ground-truth dataset and evaluation of SOTA tools. | Evaluation-focused | Highlights R8/version fragility. | No | Preprint/dataset status should be checked. | Evaluation design. | Not a detector. |
| Robustness Study Against Advanced Obfuscation | 2026 | Evaluation of tools against advanced obfuscation/R8-like transformations. | Evaluation-focused | Shows strong limitations of existing tools. | No | Preprint/to-appear. | Honest limitation and confidence design. | Not a detector. |
| AnchorDiff | 2026 | Binary OSS version identification using anchor-node slicing. | Strong for binary OSS | Binary robustness, not Android-specific. | No | Research availability varies. | Future native/binary version matching. | Not a DEX Android TPL detector. |

## B. SBOM Standards, Generators, and Vulnerability Tools

| Tool / standard | Role | How it helps MVP | Why chosen / considered | Limitation for APK reverse SBOM |
|---|---|---|---|---|
| CycloneDX | SBOM standard | Primary SBOM output format. | Security-oriented, scanner-compatible, supports rich component metadata. | It is a format, not a detector. |
| SPDX | SBOM standard | Future secondary export. | Strong license/compliance ecosystem. | More work; not first output format. |
| CISA SBOM Minimum Elements | SBOM quality guidance | Checklist for fields and quality. | Helps justify required SBOM metadata. | General guidance, not APK-specific. |
| PURL | Package identifier format | Encodes Maven component identity. | Fits `pkg:maven/group/artifact@version` and works well with CycloneDX/OSV. | Requires correct component and version detection. |
| cdxgen | SBOM generator | Baseline/reference for CycloneDX workflows. | Practical SBOM tool ecosystem. | Source/package-manager oriented; compiled APK DEX inference remains hard. |
| Syft | SBOM generator | Baseline for archive/filesystem SBOM generation. | Produces CycloneDX/SPDX; useful comparison. | Not designed for obfuscated DEX library version recovery. |
| blint | Binary linter/SBOM helper | Inspiration for binary/native evidence. | Useful for binary inspection ideas. | Not specialized for Android DEX TPL versioning. |
| Trivy | Vulnerability scanner | Scans generated CycloneDX SBOM. | Common DevSecOps scanner. | Depends on correct PURL/version in SBOM. |
| Grype | Vulnerability scanner | Alternative SBOM scanner. | Good second scanner for comparison. | Depends on correct component identity. |
| OSV API | Vulnerability API | Primary package/version vulnerability lookup. | Works well with package ecosystems and version ranges. | Coverage differs by ecosystem/advisory source. |
| NVD API | Official CVE/CVSS source | Optional enrichment. | Official CVE database. | Maven-to-CPE mapping can be difficult. |
| GitHub Advisory DB | Vulnerability database | Optional GHSA enrichment. | Good open-source advisory coverage. | Requires API handling and may overlap with OSV. |
| Sonatype OSS Index / Guide | Vulnerability database | Optional Maven coordinate lookup. | Useful package-centered vulnerability data. | API/service state and coverage should be documented. |
| Android R8 | Shrinker/optimizer/obfuscator | Evaluation and threat model. | Modern Android release builds often use R8. | Not a detector. |
| ProGuard | Obfuscator/shrinker | Evaluation variant. | Common historical baseline. | Less representative than modern R8 alone. |
| Obfuscapk | Obfuscation generator | Optional robustness testing. | Generates controlled APK obfuscation cases. | Extra setup; may not represent all real protectors. |

## C. What The Table Means For The MVP

The updated synthesis leads to these decisions:

| MVP decision | Supported by | Final choice |
|---|---|---|
| Use static APK analysis | Android TPL detection papers | Analyze compiled APKs without source code. |
| Support multidex | Systematic assessment papers | Extract all `classes*.dex`. |
| Build Maven reference DB | LibScout, ATVHunter, LibID, LibScan, SAD | Compare APK features against known versions. |
| Use candidate filtering | LibRadar, ATVHunter, LibScan | Fast metadata/package/class filtering first. |
| Use class dependency graph | LibPecker, SAD, LibMD | CDG is the main structural feature. |
| Use opcode similarity | LibID, LibScan, ATVHunter | Adds version-sensitive evidence. |
| Use confidence scoring | SAD, LibHunter, robustness studies | Avoid false exact-version claims. |
| Generate CycloneDX SBOM | CycloneDX, CISA, cdxgen, Trivy/Grype | Standard machine-readable output. |
| Query vulnerabilities after versioning | ATVHunter, OSSPolice, OSV, NVD | Exact version enables CVE/advisory lookup. |
| Keep native versioning as future work | LibRARIAN, DroidNative, AnchorDiff | First MVP only extracts/hashes native `.so`. |

## D. Main Correction Compared With The Old Table

The old table was useful but mixed two categories:

```text
academic Android TPL detectors
and
SBOM/vulnerability tools
```

The updated table separates them because most academic detectors do not emit standard SBOMs, while SBOM tools usually do not recover obfuscated compiled APK dependencies by themselves.

