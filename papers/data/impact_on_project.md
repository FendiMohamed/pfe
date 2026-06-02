# Impact on Project — Per-Paper Analysis

> How each paper informs the design of an SBOM extraction tool for compiled Android APKs

## Generation 1 Papers

### LibScout (Backes+ 2016)
**Adopt**: Fuzzy descriptors for renaming resilience. 3-layer Merkle tree profiling structure. Similarity scoring 0-1 for partial matches.
**Reject**: Package-based module decoupling. Assumption that Merkle trees survive R8 optimizations.
**Adapt**: Profile generation methodology — use original SDKs from Maven Central as ground truth.
**Impact**: Provides pre-R8 baseline for version-level detection. The 12.7% F1 under R8 confirms that pure structural profiling is insufficient.

### LibRadar (2016)
**Adopt**: Speed-optimized scanning for first-pass filtering in a hybrid pipeline.
**Reject**: Clustering-based detection (no version labels). Single-dex assumption.
**Impact**: Confirms that hybrid pipelines (fast pre-scan + deep verify) are the right architecture.

### LibD (Li+ 2017)
**Adopt**: Homogeny graph concept as precursor to CDG. Opcode hashing for rename-resilient feature extraction. Ghost call detection.
**Reject**: =10 app threshold (not applicable for library identification in single APK). Clustering-only (no version detection).
**Adapt**: Build CDG from class dependency relations (inherits, implements, calls).
**Impact**: Validates that structural dependency graphs survive obfuscation better than naming conventions.

### ORLIS (Wang+ 2018)
**Adopt**: Two-stage architecture (coarse filter + fine match). Jaccard similarity for partial library inclusion.
**Reject**: sdhash/ssdeep-based matching (too slow). CFG-only features (not sufficient).
**Adapt**: Replace expensive similarity digests with lightweight opcode hashing + CDG matching.
**Impact**: Two-stage pattern is proven; we must implement with more efficient matching algorithms.

## Generation 2 Papers

### ATVHUNTER (Zhan+ 2021)
**Adopt**: CDG-based module decoupling. Two-phase detection (coarse CFG ? fine opcode). Feature weighting for unique code emphasis. Fuzzy rolling hash for similarity. Vulnerability DB construction methodology.
**Reject**: Partial R8 coverage (DashO only). No standard SBOM format.
**Adapt**: Extend fine-grained matching to handle method inlining by R8. Add CycloneDX output format.
**Impact**: Closest complete pipeline to our goal (detection ? version ? CVE mapping). CDG decoupling is proven at 93.4% library-level F1.

## Generation 3 Papers

### LibAttention (Pan+ 2025)
**Adopt**: Pre-training on raw bytecode (200M Smali tokens) reduces labeled data needs. SDK structural vocabulary for feature extraction.
**Reject**: Binary-only output (no version detection). Full ML pipeline for a standalone detection tool.
**Adapt**: Use as first-pass filter for R8-obfuscated apps before version identification.
**Impact**: Confirms ML can learn obfuscation patterns. But lack of version detection means it's insufficient alone for SBOM.

### SAD (Zhou+ 2025)
**Adopt**: Stateful/stateless class distinction. Field Operation Sequence matching for stateful classes. CDG neighbor feature aggregation. Literal feature tie-breaking for adjacent versions.
**Reject**: CDG-only approach (needs multi-scale fusion for R8 inlining resilience).
**Adapt**: Combine stateful/stateless matching with Bayesian version scoring.
**Impact**: Current SOTA for version-level detection. The 84.82% F1 is the benchmark to beat. The -10pp under inlining confirms the remaining gap.

### LibMD (Zhang+ 2025)
**Adopt**: Multi-scale fusion (CDG + function calls + basic blocks). Bayesian probability scoring. Library Dependency Graph (LDG) for transitive deps. Explicit SBOM generation.
**Reject**: (No direct rejection — this is the closest approach to our goal)
**Adapt**: Implement as open-source with CycloneDX output. Add TPL-Benchmark evaluation.
**Impact**: MOST RELEVANT PAPER. The multi-scale fusion architecture is the foundation for our MVP. Bayesian scoring addresses adjacent-version disambiguation. LDG concept handles transitive dependencies.

### LibScope (Zhan+ ICSE 2026)
**Adopt**: Global set-level matching to avoid local maxima. Bloom filter for compact feature representation.
**Reject**: (Pending full publication for detailed assessment)
**Impact**: Novel matching paradigm that could improve accuracy in our fine-grained matching stage.

## Surveys & Benchmarks

### Systematic Assessment (Zhan+ TSE 2021)
**Adopt**: Six-criteria evaluation framework. Multidex handling patch. .aar preprocessing. CDG > package structure.
**Reject**: Pre-R8 evaluation methods.
**Adapt**: Use 6-criteria framework for our own evaluation. Implement multidex loop in pipeline.

### TPL-Benchmark (Gu+ 2025)
**Adopt**: Realistic F1 baseline (~60%). 6K-app ground truth dataset. Standardized evaluation protocol. Recognition that R8 >50% shrink causes catastrophic failures.
**Reject**: (No direct rejection — this is the benchmark we must measure against)
**Adapt**: Evaluate our MVP against TPL-Benchmark. Aim to beat the 60.15% realistic maximum.

### Ramirez Thesis (2024)
**Adopt**: F-Droid as ground truth source. Hybrid pipeline recommendation. Android-first focus (iOS is ~10y behind).
**Reject**: Direct tool dependencies (tools will be adapted).
**Impact**: Confirms Android focus is correct. F-Droid methodology validated.

### ObfDetector (Pan+ ICSE 2026)
**Adopt**: Recognition that version-level F1 < 10% under advanced obfuscation. Package hierarchy obfuscation as critical blind spot. Systematic failure analysis framework.
**Reject**: (No direct rejection — this diagnoses problems our MVP must solve)
**Adapt**: Ensure our MVP specifically tests against package hierarchy obfuscation and R8 optimization at varying shrink ratios.
