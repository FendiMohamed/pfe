# Research Evidence Map

This file maps papers/tools to MVP architecture decisions.

## Core Evidence

| Source | Main lesson for MVP |
|---|---|
| LibScout | Reference profiles and exact-version matching are useful, but exact-copy style detection is fragile under shrinking/optimization. |
| LibSift | Separating app code from third-party library code is a necessary stage. |
| LibD | Graph-based and scalable clustering ideas help avoid fragile package-name-only detection. |
| ORLIS | Fuzzy/structural matching improves obfuscation resilience but can be expensive. |
| LibPecker | Class dependency graph and class similarity are strong for library detection. |
| LibID | CFG/basic-block/class signatures and optimization constraints improve obfuscation-resilient version identification. |
| LibScan | Staged matching with class correspondence, method opcode similarity, and call-chain opcode similarity is a strong design for hybrid matching. |
| ATVHunter | Coarse CFG filtering plus fine opcode matching supports exact vulnerable library version detection and CVE mapping. |
| SAD | Class dependency graph, class summaries, structural similarity, and literal tie-breakers improve version-level detection. |
| LibHunter | R8 optimization affects TPL detection seriously; evaluation must include R8/shrinking and method inlining limitations. |
| LibAttention | ML can improve R8 resilience, but it is heavier and less explainable for a first MVP. |
| LibMD | Multi-scale feature fusion and Bayesian confidence are a strong future direction; MVP should use a simpler weighted fusion. |
| OSSPolice | Source/reference indexing can support Java and native OSS identification; version identity matters for license and security. |
| Keep me Updated | Exact library versions matter because many vulnerable libraries can be updated. |
| LibRARIAN / DroidNative | Native libraries matter, but native version detection is a separate problem; first MVP can extract/hash `.so` files. |

## Tooling Evidence

| Tool/standard | Main lesson for MVP |
|---|---|
| CISA SBOM guidance | SBOMs need component identity, version, identifiers, relationships, author, timestamp, and automation. |
| CycloneDX | Good first SBOM format for security workflows and scanner interoperability. |
| PURL | Best package identifier for Maven library versions. |
| OSV | Good vulnerability lookup source for package ecosystems. |
| NVD | Official CVE/CVSS source but CPE mapping can be hard for Maven libraries. |
| Trivy / Grype | Useful to prove generated SBOMs can be consumed by real vulnerability scanners. |

## Architecture Claims Supported By Evidence

| Claim | Supporting sources |
|---|---|
| Package names alone are not enough. | LibRadar limitations, LibScout, Systematic Assessment, LibHunter. |
| Version-level detection is harder than library-level detection. | ATVHunter, SAD, LibHunter, Systematic Assessment. |
| Graph and opcode features are better for obfuscation than names. | LibPecker, LibID, LibScan, ATVHunter, SAD. |
| R8 must be treated explicitly as a limitation/evaluation dimension. | LibHunter, LibAttention, robustness studies. |
| SBOM generation requires standard identifiers and evidence, not only library names. | CycloneDX, CISA, cdxgen, Trivy, Grype. |

