# PFE: SBOM Extraction & CVE Detection from Compiled Android APKs

## Goal

Build a tool that analyzes compiled Android APKs (potentially obfuscated), extracts a **Software Bill of Materials (SBOM)** — i.e., identifies third-party libraries and their exact versions — and maps them to known **CVEs** for vulnerability assessment.

## Research Baseline

### Core Problem

Third-party libraries (TPLs) make up >60% of Android app code [Wang+]. They're statically linked into DEX bytecode during compilation, losing version metadata and file boundaries. Obfuscation (ProGuard, R8, DashO, Allatori) further complicates identification via renaming, inlining, control-flow flattening, and dead-code removal.

### Key Papers (2016–2026)

| Paper | Year | Venue | Approach | Key Result |
|-------|------|-------|----------|------------|
| **LibScout** [Backes+] | 2016 | CCS | Merkle tree + fuzzy descriptors | 100% renaming resilient; version-level F1 12.7% under R8 |
| **LibRadar** | 2016 | ICSE | API freq hashing + clustering | Fastest (~5.5s/app); no version detection |
| **LibD** [Li+] | 2017 | ICSE | Homogeny graph + opcode hashing | 1,954 libs found (vs 670); ghost calls |
| **ORLIS** [Wang+] | 2018 | MOBILESoft | Two-stage CFG + ssdeep/sdhash | ~90% precision; slowest (1,438s/app) |
| **Zhan+ (Are We There Yet)** | 2020 | ASE | Empirical comparison of 5 tools | Multidex blind spot; CDG > package structure |
| **ATVHUNTER** [Zhan+] | 2021 | ICSE | CDG + two-phase CFG→opcode | 93.4% lib-F1; 88.8% version-F1; 87.5% apps vulnerable |
| **Systematic Assessment** [Zhan+] | 2021 | TSE | 9 tools, 6 criteria | Most comprehensive survey; multidex/.aar/entrypoint patches |
| **Libra** [Tomassi+] | 2023 | ISC | CTPH piecewise fuzzy hashing | 88% non-obf F1; 50-87% obfuscated |
| **Ramirez** | 2024 | Thesis | Android vs iOS empirical study | iOS detection 10y behind; hybrid pipeline recommended |
| **LibAttention** [Pan+] | 2025 | SANER | Transformer on 200M Smali tokens | +30% F1 over rules on R8; **no version detection** |
| **SAD** [Zhou+] | 2025 | EASE | CDG + stateful/stateless class matching | **97.6% lib-F1**; 84.8% version-F1 (best) |
| **LibMD** [Zhang+] | 2025 | Info. Fusion | Multi-scale fusion + Bayesian scoring | **Only explicit SBOM tool**; metrics unreleased |
| **UniBOM** [Safronov+] | 2025 | IoT | Multi-modal SBOM pipeline | SBOM template; not Android-specific |
| **TPL-Benchmark** [Gu+] | 2025 | arXiv | 10 tools, 6K apps, ground truth | **Real F1 ≈ 60%** (not 83-97%) — dramatic correction |
| **LibScope** [Zhan+] | 2026 | ICSE | Bloom filter + global iterative matching | Set-level matching; 9.1% acceptance rate |
| **ObfDetector** [Pan+] | 2026 | ICSE | Study on 77K apps; advanced obfuscation | **F1 < 50% lib, < 10% version** under adv. obfuscation |

### Key Surveys & Benchmarks

- **Zhan+ (ASE 2020 / TSE 2021)**: Systematic assessment of 9+ tools on 6 criteria. CDG > package structure. Multidex blind spot.
- **Ramirez (2024)**: Android vs iOS comparison. Hybrid pipeline recommended.
- **Gu+ (TPL-Benchmark 2025)**: **Most important empirical finding** — real-world F1 caps at ~60% (vs 83-97% claimed). Ground truth for 6K apps.
- **Pan+ (ObfDetector ICSE 2026)**: 77K apps analyzed. F1 < 10% at version-level under advanced obfuscation.

### Open Challenges

1. **R8 method inlining resilience**: Even SAD loses −10pp; most tools untested
2. **Realistic F1 is ~60%**: Prior papers inflated numbers by testing on easy datasets
3. **Version-level detection < 10%**: Under advanced obfuscation (ObfDetector ICSE 2026)
4. **Transitive dependencies**: ~47.3% of TPLs depend on others
5. **Partial library inclusion**: Most tools produce binary yes/no, not confidence scores
6. **No standard SBOM output**: Only LibMD (unreleased) generates structured SBOM
7. **Package hierarchy obfuscation**: Critical blind spot identified by ObfDetector

## Task List

### Phase 1: Research & Baseline (Current)

- [x] Collect papers (10 papers collected)
- [ ] Deep-read all papers, extract structured data to `papers/data/`
- [ ] Fix synthesis table: add LibPecker, LIBLOOM; correct LibRadar F1
- [ ] Write explicit "Impact on Project" per paper
- [ ] Produce v2 of synthesis table with ground-truth column, library coverage, license info

### Phase 2: Tool Evaluation

- [ ] Install and benchmark existing tools (LibScout, LibRadar, SAD, ATVHUNTER if available)
- [ ] Build ground-truth dataset from F-Droid open-source apps
- [ ] Test against R8-obfuscated apps
- [ ] Document precision/recall/F1 per tool

### Phase 3: Prototype Design

- [ ] Design architecture: module decoupling → signature extraction → version matching → SBOM generation → CVE lookup
- [ ] Choose approach (CDG-based + multi-scale fusion + Bayesian scoring)
- [ ] Implement MVP: APK decompilation → TPL identification → version estimation → SBOM (CycloneDX) → CVE mapping (NVD/OSV/EPSS)

### Phase 4: Evaluation

- [ ] Evaluate against ground-truth dataset
- [ ] Compare with existing tools
- [ ] Measure R8 resilience
- [ ] Write scientific paper

## MCP Servers (Recommended)

### Essential

| Server | Purpose | Install |
|--------|---------|---------|
| `cve-mcp` | NVD + EPSS + KEV + OSV + GitHub Advisory (23 tools) | `npx -y cve-mcp` |
| `sequential-thinking` | Complex multi-step reasoning for paper analysis | `npx -y @modelcontextprotocol/server-sequential-thinking` |

### Useful

| Server | Purpose | Install |
|--------|---------|---------|
| `apktool-mcp-server` | APK decompilation and analysis (needs apktool installed) | `uvx apktool-mcp-server` |
| `memory` | Persistent knowledge graph across sessions | `npx -y @modelcontextprotocol/server-memory` |

### For MVP Implementation

| Server | Purpose | Install |
|--------|---------|---------|
| `android-security-analyzer` | Static analysis of Android source (remote, hosted) | Remote URL |

## OpenCode Config

See `opencode.json` in project root for MCP configuration.
