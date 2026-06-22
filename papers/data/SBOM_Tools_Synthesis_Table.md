# SBOM Tools Synthesis Table — Android TPL Detection & Vulnerability Mapping

> **Legend:** ★ = Strong/Best-in-class | ✓ = Supported | ◐ = Partial | ✗ = Weak/No | — = N/A or not tested
> **Note:** Metrics come from DIFFERENT evaluations with distinct datasets, ground truths, and protocols. Direct numerical comparison should account for this caveat.

---

## Criteria Definitions

- **Obfuscation coverage**: RN (identifier renaming), PF (package flattening), CFR (control-flow randomization), DCR (dead-code removal), SE (string encryption), MI (method inlining / R8-specific)
- **Module decoupling**: How tool separates library code from app code (package heuristics → fragile; CDG-based → robust)
- **Partial lib handling**: Does the tool produce a similarity score for partially-included libraries, or only a binary match?
- **SBOM output**: Does the tool emit a structured SBOM (CycloneDX, SPDX, custom JSON) or only print library names?
- **CVE mapping**: Does the tool link detected libraries/versions to known vulnerabilities?
- **Transitive deps**: Does the tool resolve nested library dependencies?

---

## Generation 1 — Hash & Package-Based (2016–2018)

### LibRadar (2016)

| Criterion | Value |
|-----------|-------|
| **Detection method** | Android API freq. hashing + package clustering. Whitelist-based. No decompilation. |
| **Library-level F1** | ~66%★ (P=97.9%/R=50%) — Note: original ~77% is inconsistent with P/R |
| **Version-level F1** | ✗ None — clustering only, no version labels |
| **R8 resilience** | ◐ Partial — −86% recall under DashO |
| **Speed** | ~5.5s/app ★ **Fastest** |
| **Obfuscation coverage** | RN, PF — fails CFR, DCR, SE, MI |
| **Module decoupling** | Package name by subtree |
| **Partial lib handling** | ✗ Binary match only |
| **SBOM output** | ✗ Prints names to stdout |
| **CVE mapping** | ✗ |
| **Transitive deps** | ✗ |
| **Open source** | ✓ GitHub (archived) |

### LibScout (2016)

| Criterion | Value |
|-----------|-------|
| **Detection method** | 3-layer Merkle tree (Package→Class→Method). Fuzzy method descriptors. Similarity score 0-1. |
| **Library-level F1** | ~83% (P=97.4%) ★ Best Gen-1 |
| **Version-level F1** | ◐ 64% Group-1; drops to 12.7% on adjacent versions under R8-shr-opt |
| **R8 resilience** | ◐ F1~1% on R8-obf-shr-opt |
| **Speed** | 82s/app (2nd fastest) |
| **Obfuscation coverage** | RN only (100% resilient) — fails PF (−75%), CFR, MI |
| **Module decoupling** | Package + CHA class hierarchy — no CDG |
| **Partial lib handling** | ◐ Score 0-1 similarity for partial libs |
| **SBOM output** | ◐ Version list, no standard SBOM format |
| **CVE mapping** | ◐ Manual — studied 2 CVEs |
| **Transitive deps** | ✗ |
| **Open source** | ✓ GitHub (active) |

### LibD (2017)

| Criterion | Value |
|-----------|-------|
| **Detection method** | Homogeny graph (call/inherit/inclusion). CFG opcode hashing per basic block → hash chain. |
| **Library-level F1** | High — 1,954 libs vs LibRadar's 670; FP 25% vs 60.6% |
| **Version-level F1** | ✗ None — clustering only |
| **R8 resilience** | ✓ Strong for RN, PF by design; CFR, MI untested |
| **Speed** | ◐ 1.4M apps tested; per-app timing not published |
| **Obfuscation coverage** | RN, PF, CFR — MI untested |
| **Module decoupling** | ◐ Homogeny graph (call/inherit/inclusion) |
| **Partial lib handling** | ✗ Instance hash only, no score |
| **SBOM output** | ✗ Library names only |
| **CVE mapping** | ✗ |
| **Transitive deps** | ◐ Homogeny graph captures some inter-package dependency |
| **Open source** | ◐ Code available; reproducibility limited |

### ORLIS (2018)

| Criterion | Value |
|-----------|-------|
| **Detection method** | Two-stage: sdhash filtering over interprocedural features → ssdeep class digests with injective class mapping. |
| **Library-level F1** | ~62-67% (P=71%, R=63%) |
| **Version-level F1** | ✗ Not reported as an exact-version metric |
| **R8 resilience** | ◐ Best Gen-1 obfusc. resilience; not tested on R8 |
| **Speed** | ~1,438s/app ✗ **Slowest** — crashes on 16GB+ apps |
| **Obfuscation coverage** | RN, PF, CFR — SE, MI untested |
| **Module decoupling** | ◐ Class correspondence over call-graph/class-hierarchy-derived features; no CDG |
| **Partial lib handling** | ✓ Injective class mapping can expose partial inclusion |
| **SBOM output** | ✗ Class-level mapping only |
| **CVE mapping** | ✗ |
| **Transitive deps** | ✗ |
| **Open source** | ◐ Published; hard to install (Soot env) |

### LibPecker (2020) — *New addition*

| Criterion | Value |
|-----------|-------|
| **Detection method** | Class dependency hashing + adaptive similarity thresholds + weighted class similarity |
| **Library-level F1** | ~60% on real-world (per TPL-Benchmark 2025) — best among 10 tools on that benchmark |
| **Version-level F1** | ~49% (per TPL-Benchmark 2025) |
| **R8 resilience** | ✓ Best Gen-1 against obfuscation (per Zhan ASE 2020) |
| **Speed** | Slow — weighted similarity comparison is time-consuming |
| **Obfuscation coverage** | RN, PF, CFR |
| **Module decoupling** | Class dependency edges |
| **Partial lib handling** | ◐ Weighted similarity |
| **SBOM output** | ✗ |
| **Open source** | ◐ Partially available |

---

## Generation 2 — CDG-Based & Version-Aware (2021)

### ATVHUNTER (2021)

| Criterion | Value |
|-----------|-------|
| **Detection method** | CDG module decoupling → coarse CFG filter → fine opcode fuzzy rolling hash + feature weighting |
| **Library-level F1** | 93.4% ✓ (P=98.6%, R=88.8%) |
| **Version-level F1** | 88.8% ✓★ Best at release (P=90.6%, R=87.2%) |
| **R8 resilience** | ◐ DashO only — 99.3% under RN+PF; −24% DCR; MI untested |
| **Speed** | 66s/app ✓ Two-stage avoids full DB scan |
| **Obfuscation coverage** | RN, PF, CFR, DCR — MI untested |
| **Module decoupling** | CDG ✓ **Best among Gen-2** |
| **Partial lib handling** | ✓ Fuzzy rolling hash → % similarity |
| **SBOM output** | ◐ CVE-linked version list; no standard SBOM format |
| **CVE mapping** | ✓ 1,180 CVEs, 224 security bugs, 189K TPLs, 3M versions |
| **Transitive deps** | ◐ CDG partially captures dependency chains |
| **Open source** | ◐ Online service; source partially released |

---

## Generation 3 — R8-Aware & SBOM-Oriented (2024–2026)

### LIBLOOM (2021/2023) — *New addition*

| Criterion | Value |
|-----------|-------|
| **Detection method** | Two-stage Bloom filter + entropy-based metric for package flattening detection |
| **Library-level F1** | ~52-56% (per TPL-Benchmark) |
| **Version-level F1** | ~74% (baseline for SAD comparison) |
| **Speed** | ✓ Fastest profiling (12,394 sigs in 33 min = 0.16s/lib) |
| **Module decoupling** | Bloom filter on package features |
| **Partial lib handling** | ◐ Entropy metric for flattened packages |
| **Open source** | ✓ Available |

### LibScan/LibHunter (2023) — *New addition*

| Criterion | Value |
|-----------|-------|
| **Detection method** | Opcode + call chain similarity. LibHunter adds inlining simulation + call-site optimization handling |
| **Library-level F1** | Not independently verified |
| **Version-level F1** | ◐ LibHunter: 76.48% recall (per TPL-Benchmark) |
| **Speed** | 46s/app (LibScan) |
| **R8 resilience** | ✓ LibHunter specifically handles R8 inlining via simulation |
| **Open source** | ◐ Partial |

### LibAttention (SANER 2025)

| Criterion | Value |
|-----------|-------|
| **Detection method** | Pre-train Transformer on 200M Smali tokens → fine-tune binary classifier |
| **Library-level F1** | ~39% on non-obfuscated (below top tools) |
| **Version-level F1** | ✗ **None** — binary presence/absence only |
| **R8 resilience** | ✓ **Best overall** — +30% F1 over rule-based under R8-obf-shr-opt |
| **Speed** | ~472s/app (AndroGuard preprocessing dominates) |
| **Obfuscation coverage** | ✓ All R8 modes: RN, PF, CFR, DCR, SE, MI |
| **Module decoupling** | ◐ Implicit — model learns boundaries |
| **Partial lib handling** | ✗ Binary output |
| **SBOM output** | ✗ No version → no CVE → no SBOM |
| **CVE mapping** | ✗ Presence only |
| **Transitive deps** | ✗ |
| **Open source** | ◐ Code described; full release unclear |

### SAD (EASE 2025)

| Criterion | Value |
|-----------|-------|
| **Detection method** | CDG + neighbor aggregation → stateful/stateless class split → Field Op Seq vs opcode + literal tie-breaker |
| **Library-level F1** | **97.64% ★ Highest of all reviewed tools** |
| **Version-level F1** | **84.82% ★ Best version-level** (+10.98% over LIBLOOM). Class-level: 94.12% |
| **R8 resilience** | ✓ Strong for RN, PF, CFR, DCR; −10pp under heavy inlining |
| **Speed** | ~130s/app |
| **Obfuscation coverage** | RN, PF, CFR, DCR — weaker on MI |
| **Module decoupling** | CDG + stateful/stateless — most granular |
| **Partial lib handling** | ✓ Per-class confidence scores |
| **SBOM output** | ◐ Version labels only; no standard format |
| **CVE mapping** | ✗ Needs NVD integration |
| **Transitive deps** | ◐ CDG captures some transitive class relations |
| **Open source** | ◐ EASE 2025; availability unclear |

### LibMD (Information Fusion 2025)

| Criterion | Value |
|-----------|-------|
| **Detection method** | Multi-scale fusion: CDG + function call + basic block dependency. Bayesian probability scoring. LDG. |
| **Library-level F1** | ✓ Exceeds single-scale baselines (exact score unverified) |
| **Version-level F1** | ✓ Strong — Bayesian scoring targets adjacent versions |
| **R8 resilience** | ✓ Design: dep. graph stable under R8 shrinking & inlining |
| **Speed** | — N/A (full paper not publicly available) |
| **Obfuscation coverage** | RN, PF, CFR, MI — designed for R8 |
| **Module decoupling** | Multi-scale CDG (3-level) — most robust approach reviewed |
| **Partial lib handling** | ✓ Bayesian confidence score |
| **SBOM output** | **✓ Explicit SBOM** — primary goal |
| **CVE mapping** | ✓ Integrated pipeline |
| **Transitive deps** | ✓ LDG supports transitive modeling |
| **Open source** | ✗ Not publicly released |

### LibScope (ICSE 2026) — *New addition*

| Criterion | Value |
|-----------|-------|
| **Detection method** | Bloom filter feature abstraction + iterative global matching (back-and-forth game) |
| **Status** | Recently accepted ICSE 2026 (9.1% acceptance). Outperforms SOTA on two benchmarks. Open source. |
| **Key innovation** | Set-level matching vs local maxima problem |

### Libra (ISC 2023) — *New addition*

| Criterion | Value |
|-----------|-------|
| **Detection method** | Method headers (coarse) → CTPH piecewise fuzzy hashing (fine) |
| **Library-level F1** | 88% non-obfuscated; 50-87% obfuscated |
| **Key innovation** | CTPH fuzzy hashing resilient to instruction reordering |

---

## Critical Findings from Benchmark Studies

### TPL-Benchmark (Gu+ 2025) — ~6K apps, 10 tools

| Finding | Detail |
|---------|--------|
| **Realistic F1 is ~60%** | Highest library-level F1 among 10 tools is 60.15% (LibPecker) — far below 83-97% claimed in original papers |
| **LibHunter best recall** | 81.79% library-level, 76.48% version-level recall |
| **LibLOOM most practical** | 12,394 signatures in 33 minutes |
| **R8 impact confirmed** | Over half of apps use R8; shrink ratio >50% causes sharp recall drops |
| **728 vulnerable TPLs** | 3,309 TPL-CVE pairs; 8,115 App-CVE mappings across 1,607 apps |

### ObfDetector Study (Pan+ ICSE 2026) — 77K apps

| Finding | Detail |
|---------|--------|
| **Library-level F1 < 50%** | Under advanced obfuscation |
| **Version-level F1 < 10%** | Under advanced obfuscation — catastrophic for SBOM |
| **Package hierarchy obfuscation** | Identified as critical blind spot most tools ignore |

---

## Summary: Recommended Architecture for MVP

| Component | Recommended Approach | Evidence |
|-----------|-------------------|----------|
| **Module decoupling** | Multi-scale CDG (LibMD) + stateful/stateless (SAD) | Robust against RN, PF, CFR |
| **R8 handling** | Multi-scale fusion (3 levels) | Stable under R8 inlining (LibMD) |
| **Version identification** | Bayesian scoring (LibMD) + literal tie-breakers (SAD) | Best disambiguation of adjacent versions |
| **Partial lib scoring** | Per-class confidence (SAD) + Bayesian (LibMD) | Better than global Jaccard |
| **SBOM output** | CycloneDX JSON | Industry standard, machine-readable |
| **CVE mapping** | NVD + OSV (cve-mcp) | Direct integration via MCP tools |
| **Evaluation benchmark** | TPL-Benchmark (Gu+ 2025) | Realistic baseline (~60% target to beat) |
| **Ground truth source** | F-Droid (Ramirez 2024) + TPL-Benchmark | Open-source verified apps |
