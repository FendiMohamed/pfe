# State of the Art: Android Third-Party Library Detection & SBOM Extraction

> **Project**: SBOM Extraction & CVE Detection from Compiled Android APKs
> **Date**: May 2026
> **Papers reviewed**: 15 (2016–2026)

---

## 1. Problem Context

Third-party libraries (TPLs) constitute 60-80% of code in modern Android applications [Wang+, Zhan+]. They are statically linked into DEX bytecode during compilation, losing file boundaries, version metadata, and provenance information. Modern obfuscation tools (ProGuard, DashO, Allatori, Android R8) further compound the problem through identifier renaming, package flattening, control-flow randomization, string encryption, dead-code removal, and method inlining.

The Android compilation pipeline transforms source code (Java/Kotlin) → `.class` bytecode → DEX (Dalvik Executable) via D8/R8 compiler → APK. During this process:
- Libraries lose individual file boundaries (merged into `classes.dex`)
- Version numbers and package names may be obfuscated
- R8 (default since AGP 3.4.0) applies aggressive code shrinking, optimization, and inlining

A 2025 study of 500K+ Google Play APKs found a **13% increase in obfuscation from 2016 to 2023**, with ProGuard and Allatori as the most common tools [Niroshan+ 2025]. The ObfDetector study [Pan+ ICSE 2026] found that **over half of 77,504 Google Play apps** use R8 as their compiler.

---

## 2. Taxonomy of Detection Approaches

### 2.1 By Methodology

| Category | Description | Tools |
|----------|-------------|-------|
| **Whitelist-based** | Match known package names | Early malware/repackaging detectors |
| **Clustering-based** | Group similar code across apps → detect popular libs | LibRadar, LibD, WuKong, LibExtractor |
| **Similarity comparison** | Build fingerprint DB of known libs → match against app | LibScout, ORLIS, ATVHUNTER, SAD, LibMD, LibPecker, LibScope, Libra, LibScan, LibHunter, LIBLOOM |
| **ML-based** | Train model to recognize lib code from features | LibAttention (Transformer) |
| **Hybrid** | Combine static + runtime analysis | Kaufmann (2026) — LibPecker + Frida |

### 2.2 By Feature Type

| Feature Level | Examples | Resilience |
|---------------|----------|------------|
| **Package names/I density** | Package subtrees, name strings | ✗ Fragile — broken by RN, PF |
| **API calls** | Android API frequency | ◐ Partial — survives RN, broken by PF |
| **Method signatures** | Fuzzy descriptors, Merkle hashes | ◐ Partial — 100% RN resilient, broken by MI |
| **Control Flow Graphs** | CFG structure, opcode sequences | ✓ Strong — survives RN, PF, CFR |
| **Class Dependency Graphs** | CDG edges (extends, implements) | ✓ Strong — survives RN, PF, CFR, partial DCR |
| **Multi-scale graphs** | CDG + function calls + basic blocks | ✓ Strongest — survives all including MI |
| **Learned embeddings** | Transformer on Smali tokens | ✓ Learns all patterns from data |

---

## 3. Detailed Paper Analysis

### 3.1 Generation 1: Hash & Package-Based (2016–2018)

#### LibScout — Backes, Bugiel, Derr (CCS 2016)

**Method**: Builds 3-layer Merkle tree profiles from library SDKs (Package → Class → Method). Uses **fuzzy descriptors** — method signatures where custom types are replaced with an `X` placeholder (e.g., `open(Activity, bool)` → `(android.app.Activity, bool, X)X`). Class Hierarchy Analysis (CHA) for module understanding. Similarity score 0-1 for partial matches.

**Results**: 
- 100% resilient to identifier renaming
- 97.4% precision at library level
- Version-level: 64% Group-1 F1; **drops to 12.7%** on adjacent versions under R8-shrink-opt
- Processing: 82s/app; 2.8s/lib for profile generation
- Database: 164 libraries, 2,065 versions
- Security findings: ~190d vulnerability window for Facebook SDK; 3.7B installs affected by crypto API misuse

**Limitations**: Only handles RN. Fails package flattening (−75%). No CDG. Package-structure-based module decoupling is fragile. No standard SBOM format. No transitive deps.

**Impact**: ✅ Establish pre-R8 baseline. Fuzzy descriptors technique reusable. Profile generation approach is proven.

#### LibRadar (ICSE 2016)

**Method**: Android API frequency hashing + package clustering. Whitelist-based. No decompilation needed.

**Results**: Fastest tool (~5.5s/app). No version labels. Low recall (~50%).

**Limitations**: Single-dex only (critical multidex blind spot). Package-structure dependent.

#### LibD — Li et al. (ICSE 2017)

**Method**: Homogeny graph (inclusion, inheritance, call relations) to recover library boundaries. Feature hashing: CFG opcodes per basic block → method hash → class hash → instance fingerprint.

**Results**: 1,954 libs found vs LibRadar's 670 on 1.4M apps. FP rate 25% vs 60.6%. google/gson had 421 packaging variations. Ghost call detection.

**Limitations**: No version detection. Requires ≥10 app occurrence threshold. No partial lib score.

#### ORLIS — Wang et al. (MOBILESoft 2018)

**Method**: Two-stage: sdhash filtering over interprocedural call-graph/class-hierarchy-derived features → ssdeep class digests with injective class mapping.

**Results**: On the paper's FDroidData class-mapping evaluation, average precision = **0.71**, recall = **0.63**, and F1 = **0.67**. Later tool assessments report high analysis cost and difficult deployment.

**Limitations**: Extremely slow. Hard to install (Soot env). No version metrics. Not tested on R8.

#### LibPecker — Zhan et al. (ASE 2020)

**Method**: Class dependency hashing + adaptive similarity thresholds + weighted class similarity.

**Results**: Originally claimed best-obfuscation-resilience. However, TPL-Benchmark (2025) shows real-world F1 = **60.15%** at library level, ~49% at version level — best among 10 tools on that benchmark but far below original claims.

---

### 3.2 Generation 2: CDG-Based & Version-Aware (2021)

#### ATVHUNTER — Zhan et al. (ICSE 2021)

**Method**: CDG-based module decoupling → coarse CFG filter → fine-grained opcode matching with fuzzy rolling hash + feature weighting to emphasize unique code vs boilerplate.

**Results**:
- Library-level F1: **93.4%** (P=98.6%, R=88.8%)
- Version-level F1: **88.8%** (P=90.6%, R=87.2%)
- Speed: 66s/app (two-stage avoids full DB scan)
- Vulnerability DB: 1,180 CVEs, 224 security bugs, 189,545 TPLs, 3,006,676 versions
- Large-scale: 87.5% of 104,446 apps had vulnerable TPLs (53,337 CVEs)

**Limitations**: MI untested. R8 not explicitly tested. Partial source release. No standard SBOM format.

---

### 3.3 Generation 3: R8-Aware & SBOM-Oriented (2024–2026)

#### LibAttention — Pan et al. (SANER 2025)

**Method**: Pre-train Transformer from scratch on 200M Smali tokens from AndroZoo → fine-tune binary classifier. Uses SDK structural vocabulary (reserved types and structural symbols) as features. Compression algorithm maps encoder output to dense low-dimensional vectors.

**Results**:
- **+30% F1 over rule-based tools on R8-obfuscated dataset**
- ~39% F1 on non-obfuscated (below top rule-based tools)
- ~472s/app (AndroGuard preprocessing dominates)
- Found 28 vulnerable TPLs appearing 42,408 times across 10,000 apps

**Critical limitation**: Binary presence/absence only — **no version identification**. Cannot produce SBOMs or map CVEs by version. This makes LibAttention unsuitable as a standalone SBOM solution.

#### SAD — Zhou et al. (EASE 2025)

**Method**: CDG construction → neighbor feature aggregation → **stateful/stateless class splitting**:
- **Stateful classes** (with non-static fields): Field Operation Sequence — tracks method read/write patterns
- **Stateless classes**: Opcode similarity
- **Literal feature tie-breaking** (strings, constants) for adjacent version disambiguation

**Results**:
- Library-level F1: **97.64%** (highest of all reviewed tools)
- Version-level F1: **84.82%** (+10.98% over LIBLOOM)
- Class-level F1: 94.12%
- Speed: ~130s/app. Tested on 1,123 apps with 562 TPLs.

**Limitations**: −10pp under method inlining (R8's core optimization). Not open source. No SBOM format. No CVE mapping.

#### LibMD — Zhang et al. (Information Fusion 2025)

**Method**: **Multi-scale fusion** across 3 dependency graph levels:
1. Class dependency graph (class-level relations)
2. Function call graph (method-level)
3. Basic block dependency graph (instruction-level)
- Library Dependency Graph (LDG) for transitive dependency representation
- **Bayesian probability scoring** for version disambiguation
- Explicit SBOM generation + CVE mapping pipeline

**Results**: Exceeds single-scale baselines. Specifically designed for R8 inlining/shinking resilience. Exact metrics unverified (tool not publicly released).

**Impact on project**: **Most relevant paper** — only tool with explicit SBOM generation as primary design goal. The multi-scale fusion architecture and Bayesian scoring are directly applicable. LDG concept informs transitive dependency handling.

---

### 3.4 New Papers (2025–2026)

#### TPL-Benchmark — Gu et al. (arXiv 2509.04091, 2025)

**Context**: Beijing University of Posts & Telecommunications + NTU Singapore.

**Key contributions**:
1. **Largest open-source ground truth dataset**: 6,055 apps, 5,756 unique TPLs, 15,274 versions, 62,218 App-TPL mappings
2. Unified evaluation of 10 SOTA tools under identical conditions

**Critical finding**: **Highest F1 among 10 tools is 60.15% (LibPecker)** — dramatically lower than the 83-97% reported in original papers. This resets expectations for the entire field.

Other findings:
- LibHunter: highest recall (81.79% library-level, 76.48% version-level)
- LibLOOM: most practical for profiling (12,394 sigs in 33 min)
- Over half of apps use R8 compiler
- 728 libraries with ≥1 CVE; 3,309 TPL-CVE pairs; 8,115 App-CVE mappings across 1,607 apps

**Impact**: **Every future evaluation must reference this benchmark** to provide realistic comparisons. Prior claims of >90% F1 must be re-examined.

#### ObfDetector — Pan et al. (ICSE 2026)

**Context**: Same group as LibAttention (Shanghai Jiao Tong University). Accepted at ICSE 2026.

**Method**: Builds ObfDetector — static analysis tool detecting identifier renaming, package hierarchy obfuscation, and code optimization. Scans 77,504 Google Play apps + 619 widely-used apps.

**Critical findings**:
- **Library-level F1 < 50%** under advanced obfuscation
- **Version-level F1 < 10%** under advanced obfuscation (catastrophic for SBOM)
- Package hierarchy obfuscation identified as critical blind spot
- Systematic failure analysis identifying architectural root causes

**Impact**: Verifies that existing tools fail catastrophically on real-world obfuscation. The <10% version-level F1 under realistic conditions is the central challenge for any SBOM project.

#### LibScope — Zhan, Ming et al. (ICSE 2026, 9.1% AR)

**Method**: Addresses "local maxima" problem — existing tools match classes independently, ignoring context. Uses Bloom filter feature abstraction + back-and-forth iterative process for global set-level matching.

**Results**: Outperforms SOTA on two benchmarks. Open source on Zenodo. JAR→DEX conversion → profiling → detection pipeline.

#### Libra — Tomassi et al. (ISC 2023)

**Method**: Two-phase: method headers (coarse) → CTPH piecewise fuzzy hashing (fine). Compact instruction encoding.

**Results**: F1 88% non-obfuscated, 50-87% obfuscated. Not open source.

#### UniBOM — Safronov et al. (IoT 2025)

**Method**: Multi-modal SBOM: binary + filesystem + source code analysis. AI-based CVE classification. Historical CPE tracking.

**Relevance**: Architectural template for unified SBOM pipeline. Not Android-specific, but CycloneDX/SPDX output design patterns transfer.

---

## 4. Comparative Synthesis

### 4.1 Performance Summary

| Metric | Best Tool | Value | Context |
|--------|-----------|-------|---------|
| Library-level F1 | SAD (Zhou+ 2025) | **97.64%** | Best reported; 1,123 apps, 562 TPLs |
| Library-level F1 (realistic) | LibPecker (TPL-Benchmark) | **60.15%** | 10 tools, 6K apps — realistic ceiling |
| Version-level F1 | SAD (Zhou+ 2025) | **84.82%** | Best reported; +10.98% over LIBLOOM |
| Version-level F1 (adv. obfuscation) | (none) | **< 10%** | ObfDetector study, 77K apps |
| Speed | LibRadar | **~5.5s/app** | Fastest; no version detection |
| R8 resilience | LibAttention | **+30% F1 over rules** | Binary presence only; no versions |
| CDG robustness | SAD / ATVHUNTER / LibMD | Strong | Survives RN, PF, CFR, partial DCR |
| SBOM output | LibMD (unreleased) | ✓ Explicit | Only tool; CycloneDX unclear |
| CVE mapping | ATVHUNTER | ✓ 1,180 CVEs | Only tool with built-in CVE DB |

### 4.2 Obfuscation Coverage Matrix

| Obfuscation Type | LibScout | LibRadar | LibD | ORLIS | ATVHUNTER | LibAttention | SAD | LibMD | LibScope | Libra |
|-----------------|----------|----------|------|-------|-----------|-------------|-----|-------|---------|-------|
| Renaming (RN) | ✓ 100% | ◐ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ◐ | ◐ |
| Pkg Flattening (PF) | ✗ −75% | ◐ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ◐ | ✗ |
| Ctrl-Flow Rand (CFR) | ✗ | ✗ | ◐ | ✓ | ✓ | ✓ | ✓ | ✓ | ◐ | ◐ |
| Dead Code Removal (DCR) | ✗ | ✗ | ✗ | ✗ | ◐ −24% | ✓ | ✓ | ✓ | ◐ | ◐ |
| String Encryption (SE) | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ | ◐ | ✗ | ✗ |
| Method Inlining (MI) | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ◐ −10pp | ✓ | ✗ | ◐ |

Legend: ✓ Resilient | ◐ Partial | ✗ Not resilient

### 4.3 The F1 Gap Problem

The most important finding across all reviewed papers is the **gap between reported and realistic F1 scores**:

| Source | Claimed Lib-F1 | Realistic Lib-F1 | Ratio |
|--------|---------------|------------------|-------|
| LibScout (original) | ~83% | — | N/A (small dataset) |
| ORLIS (original) | ~62-67% | Consistent | Validated |
| ATVHUNTER (original) | 93.4% | Not on TPL-Bench | Needs re-evaluation |
| SAD (original) | 97.64% | Not on TPL-Bench | Needs re-evaluation |
| TPL-Benchmark (best) | — | **60.15%** | **Benchmark standard** |

The TPL-Benchmark [Gu+ 2025] reveals that when tested on diverse, real-world apps with version-level ground truth, **all tools perform far below their originally reported numbers**. This is due to:
1. Prior evaluations used small, similar datasets
2. Prior evaluations excluded challenging cases (R8-obfuscated, multidex, partial imports)
3. Prior evaluations used relaxed version-level precision metrics

---

## 5. Open Challenges & Research Gaps

| # | Challenge | Severity | Current Best | Target | Evidence |
|---|-----------|----------|-------------|--------|----------|
| 1 | **R8 method inlining** | Critical | −10pp (SAD) | 0pp | ObfDetector ICSE 2026 |
| 2 | **Version F1 under obfuscation** | Critical | <10% (all) | >80% | Pan+ 2026: 77K apps |
| 3 | **Realistic F1 standardization** | High | 60% (best) | >85% | TPL-Benchmark 2025 |
| 4 | **Standard SBOM output** | High | 1 tool (unreleased) | CycloneDX | Only LibMD addresses |
| 5 | **Transitive dependencies** | High | LDG concept only | Full chain | ~47.3% TPLs depend on others |
| 6 | **Partial library confidence** | Medium | Bayesian/SAD per-class | Calibrated | Most tools binary |
| 7 | **Package hierarchy obfuscation** | Medium | Identified but unsolved | Robust | ObfDetector 2026 |

---

## 6. Recommended Architecture for MVP

Based on the state of the art analysis, the MVP should adopt:

### 6.1 Module Decoupling
**Multi-scale CDG** (inspired by LibMD + SAD):
- Level 1: Class dependency graph (extends, implements)
- Level 2: Function call graph 
- Level 3: Basic block dependency
- Stateful/stateless class distinction (SAD)

### 6.2 Version Identification
**Bayesian scoring** (LibMD) + **literal feature tie-breaking** (SAD):
- Probability-based disambiguation of adjacent versions
- Field Operation Sequences for stateful classes
- Literal features (strings, constants) as secondary filter

### 6.3 SBOM Generation
**CycloneDX JSON** format:
- Industry standard, machine-readable
- Includes component name, version, licenses (future)
- Produces CycloneDX BOM 1.4+ format

### 6.4 CVE Mapping
**NVD + OSV integration** (via `cve-mcp` MCP tools):
- Query by package name and version
- CVSS scoring, EPSS exploit probability
- CISA KEV for actively exploited vulns

### 6.5 Evaluation Protocol
**TPL-Benchmark dataset** [Gu+ 2025]:
- 6K+ apps with ground truth version labels
- Compare against realistic 60% F1 baseline
- Report library-level, version-level, and class-level F1
- Test under R8-obfuscation at varying shrink ratios (0%, 25%, 50%, 75%)

### 6.6 Architectural Pattern
**Two-stage pipeline** (validated by ATVHUNTER, ORLIS, Ramirez 2024):
- Stage 1 (Fast): Coarse filtering via graph-level features (CDG hash)
- Stage 2 (Accurate): Fine-grained matching via Bayesian scoring + literal features
- Hybrid approach — handles R8 cases with ML-fallback

---

## 7. References

1. Backes, M., Bugiel, S., & Derr, E. (2016). Reliable Third-Party Library Detection in Android and its Security Applications. *CCS 2016*.
2. Li, M., et al. (2017). LibD: Scalable and Precise Third-party Library Detection in Android Markets. *ICSE 2017*.
3. Wang, Y., et al. (2018). ORLIS: Obfuscation-Resilient Library Detection for Android. *MOBILESoft 2018*.
4. Zhan, X., et al. (2020). Automated Third-Party Library Detection for Android Applications: Are We There Yet? *ASE 2020*.
5. Zhan, X., et al. (2021). ATVHUNTER: Reliable Version Detection of Third-Party Libraries for Vulnerability Identification in Android Applications. *ICSE 2021*.
6. Zhan, X., et al. (2021). A Systematic Assessment on Android Third-party Library Detection Tools. *IEEE TSE 2021*.
7. Tomassi, D.A., et al. (2023). Libra: Library Identification in Obfuscated Android Apps. *ISC 2023*.
8. Marchand Ramirez, P. & Gorla, A. (2024). Empirical Study of Third-Party Library Detection in iOS and Android Applications. *Master's Thesis, UPM*.
9. Pan, D., et al. (2025). Pay Your Attention on Lib! Android Third-Party Library Detection via Feature Language Model. *SANER 2025*.
10. Zhou, B., et al. (2025). Version-level Third-Party Library Detection in Android Applications via Class Structural Similarity. *EASE 2025*.
11. Zhang, Z., et al. (2025). Obfuscation-resilient Detection of Android Third-Party Libraries Using Multi-Scale Code Dependency Fusion. *Information Fusion*.
12. Safronov, V., et al. (2025). UniBOM: A Unified SBOM Analysis and Visualisation Tool for IoT Systems and Beyond. *IoT 2025 / arXiv 2511.22359*.
13. Gu, J., et al. (2025). Revisiting Third-Party Library Detection: A Ground Truth Dataset and Its Implications Across Security Tasks. *arXiv 2509.04091*.
14. Zhan, L., et al. (2026). Towards Global Matches for Third-Party Library Detection in Android. *ICSE 2026*.
15. Pan, D., et al. (2026). An Empirical Study on the Robustness of Android TPL Detection Tools Against Advanced Obfuscation. *ICSE 2026*.
16. Niroshan, A., et al. (2025). An Empirical Study of Code Obfuscation Practices in the Google Play Store. *arXiv 2502.04636*.
