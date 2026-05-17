# PFE Final: APK-to-SBOM MVP

This project investigates how to recover Software Bills of Materials (SBOMs) from compiled Android APKs.

The MVP goal is:

```text
Compiled Android APK
-> static extraction of DEX, metadata, and native evidence
-> detection of known Maven third-party libraries
-> version scoring with confidence and evidence
-> CycloneDX SBOM generation
-> vulnerability lookup for detected versions
```

The project is based on two bodies of work:

- Android third-party library detection papers: LibScout, LibD, ORLIS, LibID, LibScan, ATVHunter, SAD, LibHunter, LibAttention, LibMD, and related empirical studies.
- SBOM and vulnerability tooling: CycloneDX, CISA SBOM guidance, PURL, OSV, Trivy, Grype, NVD, and Sonatype/GitHub advisory sources.

## Important Folders

| Path | Purpose |
|---|---|
| `ressources/papers/` | Core local research papers. |
| `work/state of the art/` | Existing state-of-the-art PDFs and comparison matrix. |
| `docs/` | Project memory, architecture, plans, tooling, and evaluation notes. |
| `src/` | Future implementation source code. |
| `data/reference_db/` | Future Maven reference feature database. |
| `data/test_apks/` | Future test APKs and controlled fixtures. |
| `data/results/` | Future experiment outputs, SBOMs, and vulnerability reports. |

## Start Here

1. Read `docs/codex/CODEX_CONTEXT.md`.
2. Read `docs/architecture/MVP_ARCHITECTURE.md`.
3. Follow `docs/planning/IMPLEMENTATION_PLAN.md`.
4. Track work in `TASKS.md`.

