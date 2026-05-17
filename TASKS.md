# Project Task Board

Status legend: `todo`, `doing`, `done`, `blocked`.

## Phase 0 - Project Organization

| Status | Task |
|---|---|
| done | Create project memory and planning files. |
| done | Review architecture with supervisor and freeze MVP scope. |
| done | Confirm local availability of Python, Java, Android build tools, D8, Apktool, JADX, Trivy/Grype, and Python dependencies. |
| done | Start Docker Desktop or resolve Docker daemon access before building the runtime container. |
| done | Add Docker setup files for the MVP runtime. |
| done | Decide initial library set for the Maven reference DB. |
| done | Initialize Git repository and verify `git status` works. |

## Phase 1 - End-to-End Skeleton

| Status | Task |
|---|---|
| done | Create Python package structure under `src/`. |
| done | Implement APK extraction: DEX, manifest, resources, native files. |
| done | Implement minimal DEX feature extraction with Androguard. |
| done | Implement Maven reference metadata schema. |
| doing | Generate first minimal CycloneDX SBOM from mocked detection results. |

## Phase 2 - Reference DB And Matching

| Status | Task |
|---|---|
| todo | Download selected Maven JAR/AAR versions. |
| todo | Convert reference libraries to DEX with D8. |
| todo | Extract reference features into SQLite. |
| todo | Implement package/class/method overlap matcher. |
| todo | Implement opcode fingerprint matcher. |
| todo | Implement initial version scorer and confidence thresholds. |

## Phase 3 - SBOM And Vulnerability Output

| Status | Task |
|---|---|
| todo | Generate CycloneDX JSON with PURL, version, evidence, and confidence. |
| todo | Validate generated SBOM with cyclonedx-cli if installed. |
| todo | Query OSV API for detected Maven package versions. |
| todo | Optionally scan generated SBOM with Trivy or Grype. |
| todo | Generate final JSON/Markdown report. |

## Phase 4 - Evaluation And Paper

| Status | Task |
|---|---|
| todo | Build controlled test APKs with known dependencies. |
| todo | Build clear, ProGuard/R8 rename, and R8 shrink variants. |
| todo | Measure library-level and version-level precision/recall/F1. |
| todo | Compare against simple baselines: package-name match, class overlap, hash match. |
| todo | Write results tables and limitation analysis. |

## Stretch Goals

| Status | Task |
|---|---|
| todo | Add class dependency graph matching with NetworkX. |
| todo | Add version tie-breakers using literals and changed classes. |
| todo | Expand reference DB to 30-50 popular libraries. |
| todo | Add basic native `.so` component reporting. |
| todo | Add HTML report or simple dashboard. |
