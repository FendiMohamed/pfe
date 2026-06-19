# Research Foundations

## Research problem

Traditional SBOM generation reads source manifests, lock files, or build-system
metadata. APK analysis starts after compilation, when dependency boundaries
have been weakened or erased. Android third-party-library detection research
therefore studies fingerprints that survive compilation and obfuscation.

## Main lessons from the literature

### LibScout

LibScout established the value of version-specific reference profiles and
normalized code signatures. The project adopts the reference-profile idea but
does not assume names survive R8.

### LibRadar and package clustering

Package-level structure is useful for discovering library regions, especially
at scale. It is not sufficient for exact versions because packages are shared
across releases and can be repackaged.

### LibD and graph evidence

Dependency graphs and structural relations survive some renaming better than
raw identifiers. The MVP extracts class dependencies and dependency-shape
features, but uses them as one signal rather than a sole identity oracle.

### ORLIS and coarse-to-fine search

ORLIS supports a two-stage strategy: cheap candidate reduction followed by
more expensive comparison. This appears in the project's diagnostic and
shortlist work. Several shortlist experiments were not promoted because recall
or false-positive controls failed.

### ATVHUNTER

ATVHUNTER reinforces class-dependency graphs and coarse-to-fine detection. The
project adapts this through multi-feature matching and structural diagnostics,
while avoiding claims that one graph representation solves R8 inlining.

### SAD and version tie-breaking

SAD distinguishes stable and changing evidence and motivates version-specific
tie-breakers. The MVP uses version-unique classes, methods, literals, and
literal-context evidence under guarded rules.

### LibAttention

LibAttention shows that learned representations can improve resilience to
obfuscation, but its focus is not reliable exact-version SBOM authority. This
motivated the AI/R8 research layer while also justifying the report-only
boundary.

### LibMD and SBOM orientation

LibMD is the closest conceptual match: multi-scale evidence, probabilistic
reasoning, and SBOM output. Because the tool is unreleased, this project
implements a transparent, reproducible MVP rather than claiming reproduction.

### TPL-Benchmark and systematic assessments

These works show that optimistic results often fall substantially on realistic
datasets. This directly motivated category-separated evaluation and the refusal
to report one polished score as universal accuracy.

### ObfDetector

ObfDetector demonstrates the severity of modern R8 effects, especially for
version-level identification. This supports the project's explicit uncertainty
model, R8 diagnostics, and cautious AI gate.

## Adopt, adapt, reject

The project uses three decision verbs:

- **Adopt** when a method is reproducible and fits the MVP, such as reference
  fingerprints and standard SBOM output.
- **Adapt** when the idea is valuable but the original method or assumptions do
  not fit, such as graph evidence and learned R8 assistance.
- **Reject or defer** when evidence, implementation cost, or promotion tests do
  not justify production use.

## Primary project research sources

- [Impact on project per paper](../../../papers/data/impact_on_project.md)
- [SBOM tools synthesis table](../../../papers/data/SBOM_Tools_Synthesis_Table.md)
- [Paper-to-implementation traceability](../../thesis/PAPER_TO_IMPLEMENTATION_TRACEABILITY.md)
- Detailed state-of-the-art narrative:
  `work/state of the art/Updated_State_of_the_Art_APK_SBOM.md`
- [Structured paper overview](../../../papers/data/papers_overview.json)
