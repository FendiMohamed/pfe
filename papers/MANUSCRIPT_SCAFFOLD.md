# Evidence-Gated Recovery of Maven Components from Compiled Android APKs

**Working manuscript scaffold — English, venue-neutral**

> **Current status:** This early scaffold is a planning aid. The authoritative
> integrated manuscript now contains a first working draft of all six
> sections, an inlined reference list, Figure 1, and Tables 1–2. Use
> `INTEGRATED_MANUSCRIPT_DRAFT.md`, `implementation_evaluation_paper_plan.md`,
> and `PAPER_READINESS_AUDIT.md` for current progress and release gates.

## 1. Abstract — finalize last

State the APK-only problem, the implemented static APK-to-SBOM pipeline, the
separation of identity/version confidence, the controlled and source-validated
evaluation lanes, the principal bounded results, and the main limitations.
The integrated manuscript contains a provisional working abstract using the
retained lane-specific values. Use the terms “controlled expected-version
confirmation” and “emitted Maven version confirmation” with their denominators.
Revise it as the final manuscript edit after the raw-artifact and run-manifest
gate is resolved.

## 2. Introduction

### 2.1 Context

Software supply-chain analysis often has to operate on a compiled APK without
the original build files. An SBOM consumer nevertheless needs component
identity, version evidence, provenance, and a defensible interpretation of
vulnerability findings.

### 2.2 Problem

DEX merging, multidex packaging, R8 renaming/shrinking/optimization/inlining,
artifact-family variants, adjacent releases, native code, and hidden code make
APK-only component and version recovery uncertain. A high similarity score is
not automatically proof of an exact version or vulnerability applicability.

### 2.3 Approach and contribution preview

Introduce the hybrid static pipeline, versioned Maven reference profiles,
weighted evidence fusion, confidence and ambiguity reporting, CycloneDX
output, and confidence-aware OSV workflow. State that the empirical
contribution is a bounded characterization of success and failure across
controlled and source-validated lanes.

### 2.4 Contributions and scope

1. An implemented APK-to-CycloneDX workflow for Maven/JVM evidence recovery.
2. A decision policy separating component identity, version confidence, and
   downstream vulnerability interpretation.
3. A lane-separated evaluation covering controlled fixtures, clean and partial
   source-validated APKs, source coverage, constrained recognition, and
   explicit boundaries.
4. A failure and evidence taxonomy that preserves ambiguity instead of hiding
   it behind a single version claim.

### 2.5 Organization

Section 3 reviews related work. Section 4 describes the approach. Section 5
reports implementation and evaluation. Section 6 concludes with limitations
and future work.

## 3. State of the Art

Use [STATE_OF_ART_DRAFT.md](STATE_OF_ART_DRAFT.md),
[PAPER_EVIDENCE_MATRIX.md](PAPER_EVIDENCE_MATRIX.md), and
[LITERATURE_CITATION_REGISTER.md](LITERATURE_CITATION_REGISTER.md).

## 4. Proposed Approach

Use [PROPOSED_APPROACH_DRAFT.md](PROPOSED_APPROACH_DRAFT.md). Add Figure 1
from [PAPER_FIGURE_TABLE_SPEC.md](PAPER_FIGURE_TABLE_SPEC.md) and verify all
module descriptions against the final implementation snapshot.

## 5. Implementation and Experimental Evaluation

Use [IMPLEMENTATION_EVALUATION_DRAFT.md](IMPLEMENTATION_EVALUATION_DRAFT.md).
The integrated manuscript already includes RQ1–RQ4, dataset strata, denominator
definitions, and main emitted-version results. Per-family/source-gap visuals
and the fuller failure taxonomy remain pending the row-level evaluation data;
do not infer their missing values.

### Required result wording

- `84/84` refers only to expected versions in 72 controlled fixtures.
- `47/47`, `880/1790`, and `927/1837` refer to emitted Maven version
  confirmation against source evidence.
- `927/12082` is source-denominator coverage for the 106-case source-tree
  layer, not emitted precision or general recall.
- `6772/6772` is a source-version-constrained upper-bound recognition result.
- OSV examples demonstrate workflow behavior, not vulnerability accuracy.

## 6. Conclusion

Summarize the bounded contribution: the implementation can produce useful
Maven and CycloneDX evidence, exact confirmation is strongest in controlled and
clean lanes, partial real APKs expose version and coverage limits, and the
report preserves uncertainty and explicit native/hidden-code boundaries.
State future work as reference coverage, APK-only recall, calibration overlap
control, transformation-aware matching, and independent artifact release.

## Integration checklist

- [ ] Select venue and citation style.
- [ ] Verify bibliographic metadata for every external study.
- [ ] Freeze implementation commit, toolchain, database snapshot, and hashes.
- [ ] Restore or regenerate raw reports, source-validation exports, and row-level
      coverage data.
- [ ] Generate every table and figure from one machine-readable snapshot.
- [ ] Run the final claim-contract audit.
- [ ] Write the abstract after all result wording is frozen.
