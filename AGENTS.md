# Project: Android SBOM & CVE Extraction from APKs

## Project Structure

```
pfe/
├── README.md               # Project definition, baseline, task list
├── opencode.json           # MCP server config
├── AGENTS.md               # This file
├── project description.pdf
├── ressources/
│   ├── old-internships-reports-from-other-students/
│   └── papers/             # 9 research papers (PDFs)
├── work/
│   ├── state of the art/   # Current summaries + synthesis table
│   └── Technical Note.pdf
├── papers/
│   └── data/               # Structured extracted data per paper
├── src/                    # Prototype code (future)
├── datasets/               # Ground truth datasets (future)
└── docs/                   # Additional documentation
```

## Key Facts

- **Goal**: Extract SBOM from compiled/obfuscated Android APKs → detect CVEs
- **Current state**: Research phase — 15 papers deeply read, structured data extracted
- **Papers analyzed**: LibScout, LibRadar, LibD, ORLIS, LibPecker (ASE2020), ATVHUNTER, LibAttention, SAD, LibMD, LibScope, Libra, LibScan/LibHunter, LIBLOOM, Systematic Assessment (TSE2021), TPL-Benchmark, ObfDetector, Ramirez Thesis, UniBOM
- **Key challenge**: R8 obfuscation — version-level F1 drops to <10% under advanced obfuscation (ObfDetector ICSE 2026)
- **Critical finding**: Realistic F1 ceiling is ~60% (TPL-Benchmark 2025), not 83-97% as prior papers claimed
- **Only SBOM tool**: LibMD (unreleased)
- **MVP target**: Multi-scale CDG fusion + Bayesian scoring + CycloneDX SBOM + CVE mapping

## Structured Data

All paper analyses stored in `papers/data/`:
- `papers_overview.json` — all 15 papers structured data (generations, tools, research gaps)
- `SBOM_Tools_Synthesis_Table.md` — corrected comparison table with new tools
- `state_of_the_art.md` — comprehensive state of the art document
- `impact_on_project.md` — explicit adoption/rejection/adapt decision per paper
- Individual JSON files per Gen-1 paper (LibScout, LibD, ORLIS, LibAttention, Zhan2020)
- `papers_6-10_analysis.json` — Gen2/3 papers detailed analysis

## Available MCP Tools (configured in opencode.json)

- `cve-mcp`: CVE lookup (NVD, EPSS, KEV, OSV, GitHub Advisory) — 23 tools
- `sequential-thinking`: Complex reasoning chains
- `memory`: Persistent knowledge graph
- `apktool-mcp`: APK decode/analysis (disabled, needs apktool)
- `android-security-analyzer`: Source code static analysis (disabled, remote)

## Research Baseline

- Best version-level F1 (reported): SAD at 84.8%
- Best version-level F1 (realistic, TPL-Benchmark): LibHunter at 76.48% recall
- Best library-level F1 (realistic, TPL-Benchmark): LibPecker at 60.15%
- Best R8 resilience: LibAttention (+30% over rules) but no versions
- Only explicit SBOM tool: LibMD (unreleased, 2025)
- Biggest finding: Existing tools over-report F1 by 20-40 percentage points
- All tools lack: transitive dependency resolution, standard SBOM format output, R8 method inlining resilience

## Task Priority

1. ✅ Search for additional papers online (5 new papers found: TPL-Benchmark, ObfDetector, LibScope, Libra, UniBOM)
2. ✅ Deep-read all 15 papers → structured data extraction in `papers/data/`
3. ✅ Fixed synthesis table errors (Removed libradar F1 math error, added missing tools)
4. ✅ Write explicit Impact on Project per paper
5. ✅ Comprehensive state of the art written
6. ⬜ Begin tool evaluation on TPL-Benchmark dataset
7. ⬜ Install existing tools (LibScout, LibPecker, etc.) for baseline
8. ⬜ Design and implement MVP prototype
