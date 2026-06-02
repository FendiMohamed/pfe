# Architecture Decisions Log

## Scope Approval

Status: approved/frozen.

The current MVP scope is now treated as approved for implementation:

- standard single APK files
- multidex support
- Java/Kotlin Maven libraries
- selected Maven reference DB
- metadata/class/opcode/CDG-based matching
- version confidence scoring
- CycloneDX SBOM output
- OSV vulnerability lookup first, with optional Trivy/Grype scan
- native `.so` extraction and hashing only in the first MVP

The first MVP explicitly excludes packed/encrypted APKs, dynamic code loading, commercial protectors, full native version identification, all-library global coverage, and perfect heavy R8 recovery.

## Decision 1: Use A Hybrid Static Pipeline

Decision: The MVP uses static APK analysis with multiple feature families: metadata, classes, opcodes, and class dependency graphs.

Reason: Package names and hashes are too fragile. Recent papers show stronger results when combining structural and opcode features.

Rejected alternatives:

- Package-name-only matching.
- Hash-only matching.
- Dynamic analysis as the first approach.

## Decision 2: Use Maven Reference Versions

Decision: The MVP compares APK code against a local reference DB built from selected Maven JAR/AAR versions.

Reason: SBOM generation requires library identity and version. Version-level tools such as LibScout, ATVHunter, LibID, LibScan, and SAD depend on reference comparison.

Rejected alternatives:

- Detecting only library names.
- Searching vulnerabilities without exact package versions.

## Decision 3: Use CycloneDX First

Decision: Generate CycloneDX JSON as the first SBOM format.

Reason: CycloneDX works well with PURL and vulnerability scanners such as Trivy and Grype.

Rejected alternatives:

- Custom JSON only.
- SPDX as the first format.

## Decision 4: Use OSV First For Vulnerability Lookup

Decision: Query OSV first using Maven package/version or PURL.

Reason: OSV is package/version-oriented and fits Maven better than NVD/CPE-only lookup.

Rejected alternatives:

- NVD-only lookup.
- Manual CVE search.

## Decision 5: Treat Obfuscation As Confidence-Affecting

Decision: The MVP is obfuscation-aware, not obfuscation-proof.

Reason: Recent R8-aware papers show that heavy R8 optimization remains hard even for advanced tools.

Expected behavior:

- Clear APK: exact version when evidence is strong.
- Light obfuscation: exact or likely version.
- Shrinking/R8: low-confidence candidate or uncertain output.
- Packing/dynamic loading: unsupported or low-confidence status.
