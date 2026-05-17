# Updated MVP Architecture Comparison Table

Purpose: supervisor-ready decision matrix explaining what architecture was chosen, why, what was rejected, and which papers/tools support each decision.

## 1. Candidate Architectures Considered

| Candidate architecture | Description | Pros | Cons | Decision |
|---|---|---|---|---|
| Package-name scanner | Search package names such as `com.squareup.okhttp3` in APK classes. | Very fast, easy to implement. | Fails under renaming, package flattening, shading, and partial inclusion; weak version detection. | Rejected as core; used only as weak evidence. |
| Hash-based scanner | Match exact hashes of classes/files/libraries. | Precise when code is unchanged. | Breaks under recompilation, shrinking, obfuscation, R8, partial inclusion. | Rejected as core; use hashes as optional evidence. |
| Source-based SBOM generator | Use Gradle/package manifests to generate SBOM. | Strong when source is available. | Project goal is compiled APKs without source/Gradle files. | Rejected as primary approach. |
| Existing detector wrapper only | Run one academic tool and convert output to SBOM. | Faster to prototype if tool works. | Tools are often old, hard to run, not SBOM-oriented, incomplete, or not exact-version/R8 robust. | Rejected as the main contribution. |
| Deep learning first | Train/finetune a model like LibAttention. | Promising under R8. | Requires large training data, less explainable, weak for exact version/SBOM evidence, too heavy for one month. | Future work. |
| Full native binary analysis first | Focus on `.so` matching using native binary similarity. | Important for many APKs. | Separate research problem; not enough time for first MVP. | Future work; first MVP extracts/hashes native files. |
| Hybrid static APK-to-SBOM pipeline | Combine DEX extraction, Maven reference DB, segmentation, class/opcode/CDG matching, confidence, CycloneDX, CVE lookup. | Balanced, explainable, paper-backed, realistic for PFE. | Still limited under heavy R8, packed APKs, and missing reference versions. | Chosen. |

## 2. Chosen Architecture

```text
APK
-> extract DEX, manifest, resources, strings, native files
-> parse DEX into classes, methods, opcodes, dependencies
-> build class dependency graph
-> segment likely third-party library modules
-> generate library candidates
-> compare against Maven reference feature DB
-> score library and version candidates
-> decide exact version, version range, or uncertain result
-> generate CycloneDX SBOM with PURL, evidence, and confidence
-> query vulnerabilities and/or scan SBOM
-> produce final report
```

## 3. Decision Matrix

| Architecture level | Chosen option | Why chosen | Evidence from papers/tools | Rejected alternatives | Difficulty |
|---|---|---|---|---|---|
| Input scope | Single compiled APK, multidex supported. | Realistic and central to problem. | Systematic assessment papers show ignoring multidex causes missed libraries. | AAB/split APK first; source projects only. | Low |
| APK extraction | Python `zipfile` plus Apktool when decoding is needed. | APK is ZIP; resources/manifest may need decoding. | Practical tooling requirement. | Custom APK parser. | Low |
| DEX parsing | Androguard. | Python-friendly DEX classes/methods/opcodes extraction. | Allows implementation of LibScan/SAD/ATVHunter-inspired features. | Custom DEX parser; decompiler-only pipeline. | Medium |
| Manual inspection | JADX. | Useful for debugging and verifying ground truth. | Not a research dependency, but practical. | Rely only on raw DEX output. | Low |
| Reference library source | Maven Central. | Most Java/Kotlin Android TPLs are distributed through Maven/Gradle. | LibScout, ATVHunter, LibID, LibScan, SAD all need reference versions. | Unknown app-market clustering only. | Medium |
| Reference conversion | Android D8. | Converts JAR/AAR classes into DEX-like form comparable to APK DEX. | Matches compiled artifact analysis direction. | Compare APK DEX directly against JAR bytecode. | Medium |
| Feature storage | SQLite. | Simple, reproducible, enough for PFE scope. | Engineering choice, not research novelty. | PostgreSQL/graph DB/vector DB first. | Low |
| Segmentation | Package plus dependency-graph clustering. | Reduces app-code noise before matching. | LibSift, LibD, LibPecker, SAD. | Treat whole APK as one block. | Medium/High |
| Candidate generation | Metadata, package clues, strings, class/method overlap, API profiles. | Fast search-space reduction. | LibRadar, OSSPolice, ATVHunter staged filtering. | Exhaustive compare against every version. | Medium |
| Core DEX matching | Class similarity, opcode similarity, CDG structural similarity. | Good balance of explainability and resilience. | LibPecker, LibID, LibScan, ATVHunter, SAD, LibMD. | Package-only, hash-only, ML-only. | High |
| Version scoring | Weighted fusion plus margin thresholds. | Avoids false exact-version claims. | SAD, LibHunter, systematic assessment, robustness studies. | Always force exact version. | High |
| Obfuscation response | Confidence-aware partial matching. | Obfuscation cannot always be fully solved. | LibHunter, LibAttention, ICSE 2026 robustness study. | Claim R8-proof detection. | High |
| Native handling | Extract/hash/list `.so` files only in first MVP. | Provides visibility without derailing scope. | OSSPolice, LibRARIAN, DroidNative. | Full native version detection first. | Low/Medium |
| SBOM output | CycloneDX JSON. | Standard, scanner-compatible, security-oriented. | CycloneDX, CISA SBOM guidance, cdxgen, Trivy/Grype. | Custom JSON only; SPDX first. | Medium |
| Component ID | PURL for Maven components. | Best identifier for Maven package/version. | PURL ecosystem, CycloneDX, OSV. | CPE-only. | Low |
| Vulnerability lookup | OSV first; NVD/GitHub/Sonatype optional. | OSV fits package/version lookup. | OSV, NVD, GitHub Advisories, Sonatype. | NVD-only lookup. | Medium |
| SBOM scanning | Trivy/Grype optional. | Demonstrates scanner compatibility. | Trivy, Grype. | Manual vulnerability list only. | Low/Medium |
| Evaluation | Controlled APKs, clear/R8/ProGuard variants, baselines. | Needed for academic validation. | Systematic assessment, LibHunter, Obfuscapk. | Test only on one real APK. | Medium/High |

## 4. Tool Choices By Level

| Level | Tool | How it will be used | Why not another option |
|---|---|---|---|
| Main language | Python | CLI, feature extraction, matching, SBOM, APIs. | Java/Kotlin would slow prototyping. |
| Raw extraction | `zipfile` | Extract `classes*.dex`, `lib/`, assets, resources. | Apktool is heavier for raw extraction. |
| Resource decoding | Apktool | Decode manifest/resources when needed. | `zipfile` cannot decode binary XML. |
| DEX analysis | Androguard | Extract classes, methods, opcodes, references. | Custom parser too costly. |
| Debugging | JADX | Manual inspection of APK/reference content. | Decompiler output should not be the core automated feature source. |
| Reference source | Maven Central | Download selected JAR/AAR versions. | GitHub source is inconsistent and not always tied to released APK bytecode. |
| Reference dexing | Android D8 | Convert references to DEX-like features. | JAR bytecode differs from APK DEX. |
| Database | SQLite | Store library/version/features. | Heavy DBs unnecessary for first MVP. |
| Graphs | NetworkX | Build CDG and graph scores. | Custom graph code wastes time. |
| SBOM | CycloneDX JSON | Standard output. | Plain JSON is not an SBOM standard. |
| Validation | cyclonedx-cli | Validate SBOM if installed. | Manual checking is error-prone. |
| Vulnerability lookup | OSV API | Query Maven/PURL package versions. | NVD/CPE mapping is harder. |
| Scanner | Trivy/Grype | Scan generated SBOM. | They are not APK detectors; they consume our SBOM. |
| Obfuscation tests | R8/ProGuard/Obfuscapk | Build/evaluate obfuscated variants. | Clear APKs alone are not enough. |

## 5. What The MVP Will Handle

| Case | Support level | Notes |
|---|---|---|
| Standard single APK | Supported | Primary input. |
| Multidex APK | Supported | Extract all `classes*.dex`. |
| Java/Kotlin Maven dependencies | Supported | Main target. |
| Libraries in reference DB | Supported | Exact/range/uncertain version possible. |
| Identifier renaming | Partial to good | Names are weak evidence; opcodes/CDG help. |
| Package renaming/flattening | Partial | Dependency graph helps but segmentation is harder. |
| Dead-code removal/shrinking | Partial | Similarity and coverage scores degrade gracefully. |
| Heavy R8 method inlining | Limited | Known hard problem. |
| Native `.so` files | Basic extraction/hash only | Full native versioning is future work. |
| Packed/encrypted APK | Not supported | Static analysis cannot see hidden code. |
| Dynamic code loading | Not supported | Code is not present in APK. |
| Libraries absent from DB | Not confidently supported | Can report unknown/uncertain evidence only. |

## 6. Improvement Roadmap After First MVP

| Improvement | Which weakness it fixes | Worth it if time remains? |
|---|---|---|
| Expand reference DB to 30-50 popular libraries. | Limited coverage. | Yes, high value. |
| Add literal and changed-class version tie-breakers. | Adjacent version ambiguity. | Yes, high value. |
| Add stronger R8 evaluation and tuning. | Partial obfuscation/R8 support. | Yes, high value. |
| Add evidence-rich Markdown/HTML report. | Supervisor/demo clarity. | Yes, high value. |
| Add baseline comparison. | Academic validation. | Yes, high value. |
| Add CFG/basic-block matching. | Weakness of simple opcode matching. | Maybe, if core works. |
| Add basic native library identification. | Native `.so` weakness. | Maybe, after DEX MVP. |
| Add SPDX export. | Compliance ecosystem. | Optional. |
| Add ML/LibAttention-style classifier. | R8 robustness. | Not worth it for one month. |
| Add dynamic analysis. | Packed/dynamic APKs. | Not worth it for first PFE MVP. |

## 7. Supervisor-Facing Summary

The chosen MVP is a realistic and academically justified compromise. It does not attempt to outperform every state-of-the-art detector, but it adapts the strongest lessons from recent Android TPL detection research into an end-to-end SBOM workflow:

```text
compiled APK -> evidence-based library/version detection -> CycloneDX SBOM -> vulnerability report
```

This is appropriate for a master PFE because it contains both research depth and a practical security artifact.

