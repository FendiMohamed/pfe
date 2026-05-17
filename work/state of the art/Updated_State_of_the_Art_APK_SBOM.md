# Updated State of the Art: Android APK Third-Party Library Detection and SBOM Recovery

Purpose: supervisor-ready state-of-the-art synthesis for the PFE project on extracting and identifying SBOMs from compiled Android APKs.

## 1. Problem Context

Modern Android applications depend heavily on third-party libraries (TPLs). These libraries are usually introduced during development through Gradle/Maven dependencies, but after compilation they are embedded into APK bytecode as DEX classes and methods. In many situations, the source code, Gradle files, and original dependency manifests are unavailable. This makes traditional source-based Software Bill of Materials (SBOM) generation insufficient for compiled APK analysis.

The project problem is therefore:

```text
Given only a compiled Android APK, recover the third-party libraries and their versions,
generate a standard SBOM, and identify vulnerabilities affecting those versions.
```

This requires connecting two research areas:

- Android third-party library detection from compiled APKs.
- SBOM generation and vulnerability analysis using standard component identifiers.

## 2. Why Library Version Detection Matters

Detecting only a library name is not enough for security analysis. Vulnerability databases usually associate CVEs or advisories with affected version ranges. For example, saying that an APK uses `okhttp` is weaker than saying it likely uses:

```text
pkg:maven/com.squareup.okhttp3/okhttp@4.9.0
```

Only the second result can be reliably checked against OSV, NVD, GitHub Advisories, Sonatype, Trivy, or Grype.

This is a central lesson from LibScout, ATVHunter, OSSPolice, Keep me Updated, SAD, and the systematic assessment papers.

## 3. Evolution of Android TPL Detection

### 3.1 Early Fast Detection: Package and API-Based Methods

Early tools such as LibRadar were designed for speed and large-scale app-market analysis. They used package structures, Android API-call frequency, and clustering to detect common libraries.

Strengths:

- Fast and scalable.
- Useful for initial candidate generation.
- Practical for large app markets.

Limitations:

- Weak exact-version detection.
- Fragile under package renaming, flattening, shrinking, and modern R8 optimization.
- Not sufficient for SBOM-quality results.

MVP lesson:

Use this family of ideas only as a cheap candidate filter, not as the final detector.

### 3.2 Reference Profile and Version-Aware Detection

LibScout introduced a stronger idea: build reference profiles from known library versions and compare APK code against those profiles. It uses a hierarchical representation of packages, classes, and methods, with descriptors that are more resilient to identifier renaming than raw names.

Strengths:

- Strong motivation for exact-version detection.
- Good baseline for reference-profile construction.
- Security-oriented use case.

Limitations:

- Older approach.
- Weaker under dead-code elimination, partial inclusion, package flattening, and heavy R8 optimization.

MVP lesson:

The MVP should build a Maven reference database and compare APK features against known library versions, but it should not rely only on LibScout-style profiles.

### 3.3 Library Segmentation and Graph-Based Detection

Tools such as LibSift, LibD, LibPecker, and SAD show that separating app code from library code is a core challenge. Package hierarchy alone is unreliable because libraries can be obfuscated, flattened, split across packages, or partially included.

Graph-based methods use relationships such as:

- class inheritance
- method calls
- field references
- class dependency graphs
- package/module dependency graphs

Strengths:

- More resilient than package-name matching.
- Helps find library modules even when names are changed.
- Useful for partial libraries.

Limitations:

- More expensive than simple package matching.
- Can be affected by aggressive shrinking, method inlining, or class merging.

MVP lesson:

Use class dependency graph (CDG) and dependency-based segmentation as the main structural evidence layer.

### 3.4 Opcode, CFG, and Fine-Grained Version Matching

LibID, ORLIS, LibScan, and ATVHunter move beyond names and package structure by using method-level, opcode-level, CFG-level, or basic-block-level features.

Important examples:

- ORLIS uses obfuscation-resilient method/class information and fuzzy similarity.
- LibID uses CFG/basic-block/class signatures and containment-style matching.
- LibScan uses class correspondence, method opcode similarity, and call-chain opcode similarity.
- ATVHunter uses a two-phase approach: CFG as coarse-grained filtering and opcodes inside CFG basic blocks as fine-grained version evidence.

Strengths:

- Better under identifier renaming.
- More useful for distinguishing library versions.
- Supports partial similarity rather than exact binary matching.

Limitations:

- More expensive to compute.
- Control-flow transformations and R8 optimizations can still reduce accuracy.
- Full CFG/basic-block matching may be too heavy for a first MVP.

MVP lesson:

Implement opcode fingerprints and optional CFG/basic-block features later. Start with method opcode similarity and CDG matching.

### 3.5 Modern R8-Aware Detection

Recent work highlights that R8 is not only a renamer. It can shrink code, inline methods, optimize call sites, merge classes, and remove unused methods/classes. This breaks many older rule-based tools.

Relevant papers:

- LibHunter studies the impact of Android code optimization on TPL detection and proposes optimization-aware matching.
- LibAttention uses a feature language model to improve detection under R8-obfuscated datasets.
- Recent robustness studies show that many tools still perform poorly under advanced obfuscation, especially at version level.

Strengths:

- They directly address modern Android compilation realities.

Limitations:

- R8 remains difficult even for recent tools.
- LibAttention is heavy and less explainable for a first SBOM-oriented MVP.
- LibHunter-style optimization awareness is useful but complex.

MVP lesson:

The MVP should be R8-aware in evaluation and design, but it should not claim full R8-proof detection. It should degrade gracefully by outputting lower confidence, version ranges, or uncertain candidates.

### 3.6 Version-Level Structural Similarity

SAD is especially relevant for the MVP because it targets version-level detection. It builds class dependency graphs, generates candidate app classes, performs class matching using summaries, and identifies versions by comparing the structural similarity of matched subgraphs. It also uses literal/string features as tie-breakers when versions are nearly identical.

Strengths:

- Strong version-level focus.
- Good use of class dependency graph.
- Handles adjacent-version ambiguity better than simple feature overlap.

Limitations:

- Still affected by heavy optimization and method reduction.
- Implementation is more complex than a simple matcher.

MVP lesson:

Adopt the SAD idea in simplified form:

```text
CDG similarity + class summary similarity + opcode similarity + literal tie-breaker
```

### 3.7 Native Libraries

Some APKs include native `.so` libraries. OSSPolice, LibRARIAN, DroidNative, DroidReach, and AnchorDiff show that native library identification is important but technically different from DEX library detection.

Native analysis may require:

- ELF parsing
- symbol extraction
- string extraction
- import/export analysis
- binary similarity
- ABI-aware matching

MVP lesson:

The first MVP should extract and report native `.so` files with hashes, ABI, filenames, and strings where possible. Full native version identification is future work.

## 4. SBOM and Vulnerability Tooling

Academic TPL detectors usually output library names, version candidates, or vulnerability lists. They rarely produce standard SBOM artifacts.

For practical SBOM use, the MVP must include:

- CycloneDX JSON output.
- PURL identifiers for Maven components.
- version confidence.
- evidence fields.
- vulnerability lookup through OSV and optionally NVD/GitHub/Sonatype.
- scanner compatibility with Trivy and/or Grype.

CycloneDX and CISA SBOM guidance justify the need for standard SBOM fields such as component name, version, identifiers, relationships, hashes, author, and timestamp.

## 5. Main Research Gap

The gap is not simply "detect libraries in APKs." Many tools already do some form of TPL detection.

The stronger gap for this PFE is:

```text
Existing SBOM tools are not designed to recover dependencies from obfuscated compiled APK bytecode,
while academic Android TPL detectors are not complete SBOM generators.
```

Therefore, the MVP bridges both:

```text
Android TPL detection techniques
+ standard SBOM generation
+ vulnerability enrichment
```

## 6. Resulting MVP Direction

The best MVP direction is a hybrid static pipeline:

```text
APK
-> extract all DEX, metadata, resources, strings, and native files
-> recover classes, methods, packages, opcodes, and class dependencies
-> segment likely third-party library code
-> compare with a Maven JAR/AAR reference feature database
-> combine metadata, class, opcode, and graph similarity
-> score exact version, version range, or uncertain candidates
-> generate CycloneDX SBOM with evidence and confidence
-> query OSV/NVD/GitHub/Sonatype or scan with Trivy/Grype
```

## 7. Key Papers and How They Influence the MVP

| Paper / tool | Main contribution | MVP influence |
|---|---|---|
| LibRadar | Fast package/API-based detection. | Candidate generation only. |
| LibScout | Reference profiles and version-aware detection. | Maven reference DB and version objective. |
| LibSift | Module decoupling. | App/library segmentation. |
| LibD | Scalable graph-based market detection. | Graph-based grouping and scalability lessons. |
| ORLIS | Obfuscation-resilient fuzzy structural matching. | Robust matching fallback. |
| LibPecker | Class dependency signatures. | CDG matching. |
| LibID | Obfuscated TPL identification using signatures and constraints. | Robust signatures and containment scoring. |
| LibScan | Class correspondence, method opcode, call-chain opcode matching. | Staged hybrid matcher. |
| ATVHunter | CFG/opcode version detection and vulnerability mapping. | Coarse-to-fine matching and CVE enrichment. |
| SAD | Version-level class structural similarity. | CDG structural version scoring and tie-breakers. |
| LibHunter | R8-aware detection under optimization. | R8 evaluation and confidence handling. |
| LibAttention | ML-based R8-resilient detection. | Future work, not first MVP core. |
| LibMD | Multi-scale fusion and Bayesian scoring. | Future ideal; MVP uses simpler weighted fusion. |
| OSSPolice | Java/native OSS detection and security/license analysis. | SBOM/security framing and native awareness. |
| Keep me Updated | Library update and vulnerability motivation. | Justifies exact versions for remediation. |
| LibRARIAN / DroidNative | Native library version analysis. | Native support as phase 2. |

## 8. Paper-by-Paper Summaries

This section gives a compact researcher-style resume of the most important papers and tools. Exact author lists should be verified from the final bibliography before thesis submission, but the summaries below are aligned with the paper content and the MVP architecture decisions.

### 8.1 LibRadar: Fast and Accurate Detection of Third-Party Libraries in Android Apps

- What it does: LibRadar detects third-party libraries in Android apps using scalable package/API-based signatures.
- Who wrote it: Ma et al., ICSE Companion 2016.
- Why it was created: Earlier approaches based on package names or manual whitelists were not scalable enough for large app markets.
- How it works: It extracts Android API-call frequency and package-level features, then clusters similar library candidates across large app collections.
- Key findings: It is fast and useful for large-scale detection, but it is not designed for exact version-level SBOM recovery.
- Impact on our project: We use the LibRadar idea only as a candidate-generation layer. It is too weak as the final detector because our MVP needs versions, evidence, and confidence.

### 8.2 LibScout: Reliable Third-Party Library Detection in Android and its Security Applications

- What it does: LibScout identifies third-party libraries and their versions in Android APKs.
- Who wrote it: Backes, Derr, and collaborators from CISPA/Saarland University, CCS 2016.
- Why it was created: Security analysis needs exact library versions, not only library names, because CVEs affect specific version ranges.
- How it works: It builds profiles from known library versions using a package-class-method hierarchy and fuzzy descriptors that are more resilient to identifier renaming than raw names.
- Key findings: LibScout is strong against basic identifier renaming and useful for studying vulnerable/outdated libraries, but it is weaker under dead-code elimination, package flattening, and modern R8 optimization.
- Impact on our project: It justifies the Maven reference DB and exact-version objective. We adopt the idea of reference profiles but combine it with stronger graph/opcode features.

### 8.3 LibSift: Automated Detection of Third-Party Libraries in Android Applications

- What it does: LibSift separates application code from third-party library code.
- Who wrote it: Wang et al., APSEC 2016.
- Why it was created: A detector first needs to know which parts of an APK are app code and which parts are library code.
- How it works: It uses package dependency graphs and module decoupling to identify likely library modules without relying only on known library names.
- Key findings: Dependency-based segmentation improves the ability to separate app code from TPL code.
- Impact on our project: It supports adding a library segmentation stage before expensive matching against the reference database.

### 8.4 LibD: Scalable and Precise Third-Party Library Detection in Android Markets

- What it does: LibD detects third-party libraries at large market scale.
- Who wrote it: Li et al., 2017.
- Why it was created: Package-name-based tools miss obfuscated or structurally changed libraries.
- How it works: It uses graph-style relations such as call, inheritance, and inclusion relations to group library instances and improve resilience to name-based obfuscation.
- Key findings: It scales to very large app datasets and improves detection compared with simple package-based approaches.
- Impact on our project: It supports the idea that package trees alone are not enough. Our MVP should consider dependency relations when segmenting and matching.

### 8.5 ORLIS: Obfuscation-Resilient Library Detection for Android

- What it does: ORLIS detects libraries in obfuscated Android apps using fine-grained structural similarity.
- Who wrote it: Wang and Rountev, MobileSoft 2018.
- Why it was created: Common obfuscators can break tools that rely on names or coarse package structure.
- How it works: It uses obfuscation-resilient method/class-level information and fuzzy structural matching, including similarity measures for partial matches.
- Key findings: It improves resilience to common obfuscation but can be slower and harder to deploy than simpler tools.
- Impact on our project: It motivates robust fallback matching and similarity scoring, but full ORLIS-style analysis is too heavy for the first MVP.

### 8.6 LibPecker: Detecting Third-Party Libraries in Android Applications with High Precision and Recall

- What it does: LibPecker detects TPLs using class dependency signatures.
- Who wrote it: Zhang et al., SANER 2018.
- Why it was created: Library customization and dead-code elimination reduce the reliability of exact matching.
- How it works: It compares class dependency signatures and uses adaptive similarity thresholds to match library classes.
- Key findings: Class dependency information improves precision and recall compared with older package/name approaches.
- Impact on our project: It supports using class dependency graph (CDG) features as a central part of the matcher.

### 8.7 LibID: Reliable Identification of Obfuscated Third-Party Android Libraries

- What it does: LibID identifies obfuscated third-party Android libraries and versions.
- Who wrote it: Published at ISSTA 2019 by the LibID research team.
- Why it was created: ProGuard, shrinking, package flattening, and control-flow randomization make earlier detectors brittle.
- How it works: It uses CFG/basic-block/class signatures, containment-style matching, locality-sensitive hashing, and optimization constraints.
- Key findings: It is more robust than name-based tools under several obfuscation strategies, but advanced transformations remain difficult.
- Impact on our project: It motivates opcode/basic-block evidence and a constraint/confidence-aware matching strategy.

### 8.8 Automated Third-Party Library Detection for Android Applications: Are We There Yet?

- What it does: This paper evaluates multiple Android TPL detection tools under a unified framework.
- Who wrote it: Zhan et al., ICSE/ASE-related empirical evaluation line.
- Why it was created: Earlier tools were evaluated on different datasets, making fair comparison difficult.
- How it works: It compares tools across effectiveness, efficiency, scalability, obfuscation resilience, and usability.
- Key findings: No single tool is best for every scenario. Multidex support, AAR handling, obfuscation resilience, and version identification are common weaknesses.
- Impact on our project: It justifies a hybrid design and gives us evaluation criteria for the MVP.

### 8.9 A Systematic Assessment on Android Third-Party Library Detection Tools

- What it does: This extended study systematically evaluates Android TPL detection tools.
- Who wrote it: Zhan et al., journal/extended version of the tool assessment work.
- Why it was created: Researchers needed a more complete and fair understanding of detection tool strengths and weaknesses.
- How it works: It evaluates tools using criteria such as candidate construction accuracy, effectiveness, efficiency, version identification, obfuscation resilience, and ease of use.
- Key findings: Richer semantic features, such as class dependencies, improve obfuscation resilience. Many tools have low recall under partial imports, obfuscation, and format changes.
- Impact on our project: It gives the evaluation framework for our MVP: library accuracy, version accuracy, obfuscation behavior, scalability, and usability.

### 8.10 OSSPolice: Identifying Open-Source License Violation and 1-Day Security Risk at Large Scale

- What it does: OSSPolice detects reused open-source components in Android apps and links them to license/security risks.
- Who wrote it: Duan et al., CCS 2017.
- Why it was created: Android apps often reuse OSS components without proper license compliance or security updates.
- How it works: It builds hierarchical indexes from OSS projects and compares Java/native artifacts using strings, normalized classes, function features, and exported functions.
- Key findings: It can detect OSS reuse at large scale and shows that vulnerable/open-source components are widely embedded in apps.
- Impact on our project: It supports the SBOM/security framing and shows why both Java and native evidence matter.

### 8.11 Keep me Updated: An Empirical Study of Third-Party Library Updatability on Android

- What it does: This empirical study examines whether Android apps can update outdated or vulnerable third-party libraries.
- Who wrote it: Derr et al., CCS 2017.
- Why it was created: Finding vulnerable libraries is not enough; researchers also need to know whether updates are feasible.
- How it works: It studies library versions, developer practices, update compatibility, and vulnerable library usage at large scale.
- Key findings: Many vulnerable library cases are updateable, and exact version information is critical for remediation.
- Impact on our project: It justifies why the MVP must identify versions and not only library names.

### 8.12 ATVHunter: Reliable Version Detection of Third-Party Libraries for Vulnerability Identification

- What it does: ATVHunter detects precise third-party library versions in Android apps and maps them to vulnerabilities.
- Who wrote it: Zhan et al., 2021.
- Why it was created: Vulnerability identification requires exact TPL versions and a mapping to known vulnerable versions.
- How it works: It builds a large Maven-based TPL database, uses CDG/module decoupling, CFG coarse filtering, and opcode/basic-block fine matching.
- Key findings: It reports strong precision/recall and demonstrates a direct path from version detection to vulnerability reporting.
- Impact on our project: It is one of the strongest models for our pipeline: coarse candidate search, fine version matching, then CVE/advisory enrichment.

### 8.13 Obfuscapk: An Open-Source Black-Box Obfuscation Tool for Android Apps

- What it does: Obfuscapk applies obfuscation transformations to APKs.
- Who wrote it: Aonzo et al., SoftwareX 2020.
- Why it was created: Researchers need reproducible obfuscated APKs to evaluate analysis tools.
- How it works: It decompiles, transforms, rebuilds, and signs APKs using configurable obfuscation modules.
- Key findings: It provides a practical way to generate obfuscation test cases.
- Impact on our project: It can be used later for robustness evaluation, after R8/ProGuard tests.

### 8.14 LibRARIAN / Too Quiet in the Library

- What it does: LibRARIAN identifies native libraries and versions in Android apps.
- Who wrote it: Researchers studying Android native-code security updates, ICSE 2021 line.
- Why it was created: Many APKs include native `.so` libraries that can contain vulnerable outdated code.
- How it works: It compares native binaries using metadata, strings, imports/exports, dependencies, and version strings.
- Key findings: Native library updates are often delayed, and vulnerable native libraries are common in popular apps.
- Impact on our project: It supports extracting native `.so` evidence, but full native version detection should be future work.

### 8.15 DroidReach: Reach Me if You Can

- What it does: DroidReach studies whether vulnerable native code is reachable from Android app code.
- Who wrote it: Researchers from the DroidReach/ESORICS 2022 line.
- Why it was created: Presence of a vulnerable native library does not always mean the vulnerable function is reachable.
- How it works: It analyzes Java-to-native links, JNI mappings, call graphs, and reachability.
- Key findings: Reachability analysis gives more precise vulnerability triage than component presence alone.
- Impact on our project: It is future work after SBOM generation. The MVP first detects components and versions.

### 8.16 LibScan: Towards More Precise Third-Party Library Identification for Android Applications

- What it does: LibScan improves precise TPL identification using staged code similarity.
- Who wrote it: Wu et al., USENIX Security 2023.
- Why it was created: Existing tools still suffer from imprecise matching under obfuscation and partial inclusion.
- How it works: It performs class correspondence detection, method-opcode similarity, call-chain-opcode similarity, and uses optimization such as early stopping/caching.
- Key findings: Staged class/method/call-chain matching improves precision, but later R8-focused work shows modern optimization remains challenging.
- Impact on our project: It strongly influences our hybrid matcher: candidate class matching first, opcode similarity second, call-chain matching as a possible improvement.

### 8.17 LibHunter: How Does Code Optimization Impact Third-Party Library Detection?

- What it does: LibHunter studies and improves TPL detection under Android code optimization, especially R8.
- Who wrote it: Xu/Zhang et al. research team, ASE 2024.
- Why it was created: Many earlier tools were evaluated against older obfuscators but not modern R8 optimization.
- How it works: It studies R8 transformations such as shrinking, method inlining, and call-site optimization, then builds optimization-aware matching logic.
- Key findings: R8 significantly reduces existing tool accuracy, especially at version level. Optimization-aware matching improves results but does not completely solve the problem.
- Impact on our project: It justifies R8 evaluation and confidence-based output. Our MVP should be R8-aware, not claim to be R8-proof.

### 8.18 LibAttention: Android Third-Party Library Detection via Feature Language Model

- What it does: LibAttention applies a feature language model to Android TPL detection.
- Who wrote it: Pan et al., SANER 2025.
- Why it was created: Rule-based detectors break when R8 changes code structure in ways not covered by hand-written matching rules.
- How it works: It pretrains a Transformer-like model on Smali/code features and fine-tunes it for library detection under different obfuscation settings.
- Key findings: It improves detection under R8-obfuscated datasets compared with older rule-based methods.
- Impact on our project: It is strong future work, but not the first MVP core because it requires training data, adds ML complexity, and is less directly explainable for exact-version SBOM evidence.

### 8.19 SAD: Version-Level Third-Party Library Detection via Class Structural Similarity

- What it does: SAD detects TPLs at version level using class structural similarity.
- Who wrote it: Zhou, Wu, Ling, and collaborators, EASE 2025 / arXiv 2025.
- Why it was created: Existing tools often detect the library family but confuse adjacent versions.
- How it works: It builds CDGs, aggregates node features, generates candidate class mappings, compares class summaries, and uses literal features as tie-breakers.
- Key findings: SAD reports high library-level and version-level F1, especially on obfuscated datasets, while still acknowledging difficult cases under heavy optimization.
- Impact on our project: It is the strongest direct inspiration for version scoring: CDG similarity, class summaries, and literal tie-breakers.

### 8.20 LibMD: Obfuscation-Resilient Detection Using Multi-Scale Code Dependency Fusion

- What it does: LibMD detects Android TPLs using multi-scale dependency fusion and reports an SBOM-oriented goal.
- Who wrote it: Zhang, Luo, and collaborators, Information Fusion 2025.
- Why it was created: Single-scale features fail under obfuscation and adjacent-version ambiguity.
- How it works: It fuses class reference syntax, function mapping, basic-block CFG reconstruction, metadata dependency graphs, and Bayesian posterior scoring.
- Key findings: Accessible information reports improved results over prior tools, but full tables/code were not fully available during our review.
- Impact on our project: It is a future ideal. The MVP will implement a simpler weighted fusion instead of full Bayesian multi-scale fusion.

### 8.21 DroidNative

- What it does: DroidNative builds a large-scale index for Android native libraries.
- Who wrote it: A-Mobile/ASE Workshops 2025 research line.
- Why it was created: Android native library recognition lacks comprehensive reference indexes.
- How it works: It constructs and indexes native library/version information for matching real-world `.so` binaries.
- Key findings: It improves native library recognition compared with earlier approaches.
- Impact on our project: It supports future native reference DB construction. First MVP only extracts and hashes native files.

### 8.22 Revisiting Third-Party Library Detection

- What it does: This work revisits Android TPL detection using a stronger ground-truth dataset.
- Who wrote it: 2025 preprint research team.
- Why it was created: Existing tool evaluations often rely on weak ground truth or outdated assumptions.
- How it works: It builds/evaluates version-level ground truth and compares multiple SOTA tools across security tasks.
- Key findings: Tool performance, especially version-level performance, can be weaker in realistic settings than earlier papers suggest.
- Impact on our project: It reinforces the need for honest evaluation, confidence scores, and clear limitations.

### 8.23 Robustness Study Against Advanced Obfuscation

- What it does: This study evaluates Android TPL detection tools against advanced obfuscation.
- Who wrote it: ICSE 2026 to-appear/preprint research team.
- Why it was created: Older benchmarks often do not reflect modern obfuscation and R8/D8 transformations.
- How it works: It characterizes obfuscation in real apps and evaluates tools under advanced transformations.
- Key findings: Many state-of-the-art tools suffer large performance drops under advanced obfuscation, especially for exact version detection.
- Impact on our project: It supports our decision to be confidence-based and to treat heavy R8 as a limitation/future improvement.

### 8.24 AnchorDiff

- What it does: AnchorDiff identifies binary OSS versions using anchor-node slicing.
- Who wrote it: ICSE 2026 research track authors.
- Why it was created: Binary OSS version identification is difficult when versions differ only slightly.
- How it works: It uses anchor nodes to partition version chains and performs adaptive weighted matching.
- Key findings: It reports strong binary version identification and storage reduction.
- Impact on our project: It is not directly needed for DEX MVP, but it is relevant future work for native `.so` version matching.

## 9. Supervisor-Facing Conclusion

The state of the art supports an MVP that is neither a simple package-name scanner nor a full clone of the most complex research tools. The defensible design is an evidence-based, hybrid static APK-to-SBOM pipeline. It uses existing tools for APK/DEX parsing, SBOM formatting, and vulnerability lookup, while implementing the core matching and version-confidence logic as the project contribution.

The MVP is expected to handle standard compiled APKs with known Java/Kotlin Maven libraries, multidex, and light obfuscation. It does not claim complete support for packed APKs, dynamic loading, full native version recovery, or perfect heavy R8 optimization recovery.
