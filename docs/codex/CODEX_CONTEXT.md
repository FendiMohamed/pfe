# Codex Context: APK-to-SBOM PFE

Use this file at the beginning of future Codex sessions.

## Project Goal

Build a PFE/master-level MVP for extracting and identifying SBOMs from compiled Android APKs.

The MVP should recover known third-party Java/Kotlin Maven libraries and versions from APK bytecode, emit a CycloneDX SBOM, and query vulnerability sources for the detected versions.

## Current Architecture Decision

The MVP scope is approved and frozen. The chosen architecture is a hybrid static pipeline:

```text
APK
-> extract DEX, manifest, resources, strings, native files
-> parse DEX into classes, methods, opcodes, dependencies
-> segment probable third-party library modules
-> compare against a Maven reference feature DB
-> score library and version candidates
-> emit CycloneDX SBOM with evidence and confidence
-> query vulnerabilities using PURL/version
-> produce final report
```

## MVP Scope

Status: approved/frozen. Do not reopen the architecture unless the supervisor explicitly changes the scope.

The first MVP handles:

- single `.apk` files
- multidex APKs
- Java/Kotlin libraries compiled into DEX
- known Maven/Gradle dependencies present in the reference DB
- light obfuscation such as renaming and some shrinking
- exact version, version range, or uncertain candidate output
- CycloneDX SBOM generation
- OSV vulnerability lookup and optional Trivy/Grype scan

The first MVP does not fully handle:

- packed or encrypted APKs
- dynamic code loading
- commercial anti-reverse-engineering protection
- complete native `.so` version identification
- all Maven libraries
- perfect heavy R8 recovery

## Research Evidence

Main local papers are in `ressources/papers/`.

Important architecture evidence:

- LibScout: reference profiles and exact-version detection.
- LibSift and LibD: library/app code segmentation.
- LibPecker and SAD: class dependency graph and class structural matching.
- LibID, LibScan, and ATVHunter: opcode/CFG/basic-block version evidence.
- LibHunter and LibAttention: R8 is a major modern challenge.
- OSSPolice, Keep me Updated, and LibRARIAN: exact version matters for vulnerability analysis.
- CISA/CycloneDX/Trivy/Grype/OSV: standard SBOM and vulnerability workflow.

See also:

- `work/state of the art/MVP_Architecture_Comparison_Matrix.md`
- `docs/research/EVIDENCE_MAP.md`

## Core Toolchain Decision

Use existing tools for infrastructure:

- Python for the main MVP.
- `zipfile` and Apktool for APK extraction/decoding.
- Androguard for DEX parsing.
- Maven Central for reference libraries.
- Android D8 for JAR/AAR to DEX conversion.
- SQLite for local reference feature storage.
- NetworkX for class dependency graphs.
- CycloneDX JSON for SBOM output.
- OSV API first for vulnerability lookup.
- Trivy/Grype optionally for SBOM scanning.

Build custom logic for:

- feature schema
- candidate generation
- library segmentation
- class/opcode/CDG matching
- version scoring
- confidence and evidence reporting

## Next Step

Implementation sprint 1 has started.

Completed:

- Git repository initialized on branch `main`; `git status` works after adding this workspace as a Git safe directory.
- toolchain audit
- Docker setup files
- Python package scaffold
- first APK extraction module
- `inspect-apk` CLI command for listing `classes*.dex`, manifest/resources presence, and native `.so` files with hashes
- `analyze-dex` CLI command for parsing APK DEX files and reporting class, method, package, and opcode evidence

Current blocker:

- None for the current Python/Androguard runtime. Docker build and container tests succeeded with elevated Docker access.

Next implementation task:

- generate the first minimal CycloneDX SBOM from mocked detection results.

Follow `docs/planning/IMPLEMENTATION_PLAN.md`.

When continuing with Codex, ask it to:

```text
Read docs/codex/CODEX_CONTEXT.md, TASKS.md, and docs/planning/IMPLEMENTATION_PLAN.md, then continue from the next unfinished task.
```
