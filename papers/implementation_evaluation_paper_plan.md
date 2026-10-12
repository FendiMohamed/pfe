# Implementation and Evaluation Paper Plan

## Status and scope

- **Paper type:** Research paper describing the implemented APK-to-SBOM system
  and its experimental evaluation.
- **Language:** English.
- **Venue and length:** Undecided; keep the plan venue-neutral until selected.
- **Controlling structure:** The supervisor-proposed six-part structure below.
- **Current stage:** First complete working-draft pass of all six supervisor
  sections. Sections 2–6 and a provisional Abstract are synchronized into the
  integrated manuscript. The Abstract is the final edit after evidence
  reconciliation; its current numbers remain explicitly historical.
- **Scope boundary:** Focus on component and version recovery from compiled
  Android APKs. Treat the broader evidence-trust framework as motivation and
  design rationale, not as a second, competing main contribution.

## Provisional title

**Evidence-Gated Recovery of Maven Components from Compiled Android APKs: A
Hybrid Static Analysis Pipeline and Source-Validated Evaluation**

Alternative: **Recovering Maven Components from Compiled Android APKs with
Evidence-Aware Version Attribution**.

## Central argument

An APK-only analyzer can recover useful Maven component and version evidence,
but a detected identity does not by itself establish an exact version or
justify a definitive vulnerability claim. This paper presents a static
pipeline that compares DEX-derived features with versioned Maven reference
profiles, separates component identity from version confidence, exposes
ambiguity, emits CycloneDX, and qualifies OSV findings according to version
evidence. Its evaluation reports controlled and source-validated evidence in
separate lanes and makes coverage and failure boundaries visible.

The paper's empirical contribution is a bounded characterization of where
this implementation succeeds and fails. It will not claim universal accuracy,
complete dependency recovery, or that a valid CycloneDX document guarantees
that every listed component was packaged in the APK.

## Research questions

Use these as working questions and finalize them before writing the evaluation
protocol. Introduce the overall aims in the Introduction; state the final RQs
once in Section 5.1 and map each result subsection back to them.

1. **RQ1 — Controlled recovery:** How accurately does the pipeline recover
   expected Maven coordinates and versions in controlled APK fixtures,
   including selected rename, shrink, optimization, and multidex variants?
2. **RQ2 — Real-APK version confirmation:** Among Maven versions emitted for
   source-validated real APKs, what fraction agrees with the resolved source
   dependency tree, and how does the result differ between clean and partial
   cases?
3. **RQ3 — Coverage and failure causes:** How much of the resolved source
   coordinate/version set is emitted exactly, and how are the un-emitted or
   mismatched rows explained by reference gaps, matcher recall, version ties,
   artifact-family variants, metadata-only dependencies, or scope boundaries?
4. **RQ4 — Downstream claim handling:** How does the system preserve evidence
   and uncertainty in CycloneDX and vulnerability reports? Treat this as a
   workflow/guardrail evaluation, not as a general vulnerability-detection
   accuracy claim.

## Paper sections and required content

### 1. Abstract

Write last. In one compact paragraph state: (1) the APK-only problem, (2) the
implemented approach, (3) evaluation data and metric definitions, (4) principal
results with denominators and evidence classes, and (5) limitations. Do not
use “100% accuracy” without naming the controlled or source-constrained lane.

### 2. Introduction

1. **Context:** SBOMs and vulnerability management; why an auditor may have an
   APK without build files or source.
2. **Problem statement:** Compilation, DEX merging, R8 transformations,
   artifact variants, and similar releases weaken identity/version evidence.
3. **Brief state of the art:** Only enough to establish that prior methods
   address library identity, versions, or obfuscation in different ways. Leave
   comparison and evidence for Section 3.
4. **Approach overview:** Summarize reference-profile construction, hybrid
   matching, uncertainty-aware SBOM output, and source-based evaluation.
5. **Contributions and scope:** State concrete contributions and exclusions.
6. **Paper organization:** One sentence per remaining section.

### 3. State of the Art

1. **Review scope and method:** Identify this as a structured literature
   mapping review unless the recorded search and screening process supports a
   stronger label. State corpus, sources, dates, inclusion criteria, and
   extraction dimensions.
2. **Android library identity detection:** Compare package, class, graph,
   opcode, API, and learned-feature approaches.
3. **Version identification:** Cover reference profiles, version-specific
   features, tie-breaking, and adjacent-release ambiguity.
4. **Obfuscation and build transformations:** Explain renaming, shrinking,
   optimization, inlining, multidex, and artifact-family effects.
5. **SBOM and vulnerability integration:** Compare component discovery,
   standard SBOM output, version provenance, and vulnerability interpretation.
6. **Evaluation practice:** Compare datasets, ground truth, module handling,
   metrics, and tool availability. Do not rank numbers from incompatible
   datasets as if they were directly comparable.
7. **Synthesis and research gap:** State which capabilities exist, their
   limitations, and the specific gap addressed by this implementation. Do not
   claim that no prior work exists unless the review establishes that claim.

### 4. Proposed Approach

Keep this section at the method/design level. Explain the approach
independently of the Python package layout or command-line interface.

1. **Problem model and assumptions:** Input is a compiled APK; primary target
   is Maven/JVM code represented in DEX; a versioned reference set is
   available; source metadata is reserved for evaluation, not normal matching.
2. **Overall workflow:** APK inspection -> DEX feature extraction -> reference
   matching -> component/version decisions -> CycloneDX -> confidence-aware
   vulnerability lookup.
3. **Evidence model:** Describe package, class, method, opcode, dependency
   graph, literal, and version-unique evidence, including their intended roles
   and limitations.
4. **Hybrid matching and decision policy:** Explain score fusion, family
   shortlisting, confidence labels, separate identity/version decisions, and
   the conditions for abstention or candidate status. State that the scoring
   is weighted and interpretable; do not call it Bayesian or probabilistic
   unless that is actually implemented.
5. **Ambiguity and evidence provenance:** Explain competing version sets,
   supporting evidence, and report properties.
6. **Security-output policy:** Explain CycloneDX/PURL output and how version
   confidence affects confirmed versus potential OSV findings.
7. **Architecture figure:** Show modules and data flow without turning source
   code structure into the theoretical model.

The current ML/R8 assistants are not a core version-selection method. If
included, describe them in Section 5 as an auxiliary report-only experiment;
they do not change the official matcher decision or SBOM authority.

### 5. Implementation and Experimental Evaluation

#### 5.1 Research questions

State the finalized RQ1-RQ4 and identify the result subsection that answers
each one.

#### 5.2 Implementation

Describe the actual modules and toolchain: APK/DEX parsing, JAR/AAR download
and D8 conversion, SQLite feature storage, matcher, CycloneDX reporting, OSV
queries, and source-validation utility. Give relevant versions and settings
from a frozen run manifest. Clearly separate default behavior from optional,
diagnostic, experiment-only, and report-only behavior.

#### 5.3 Experimental protocol and datasets

Describe inclusion and exclusion, APK/source pairing, hashes, source tags or
commits, Gradle configurations, validation-copy changes, reference database
contents, and the evaluation workflow. Keep these evidence lanes separate:

- controlled fixtures with manifest ground truth;
- clean source-validated real APKs;
- partial source-validated real APKs;
- source-validated no-Maven-signal controls;
- source-denominator coverage analysis;
- source-version-constrained upper-bound experiments;
- report-only/experiment-only results;
- limitation cases such as native-heavy or hidden-code APKs.

Explain the sampling strategy and test for overlap between APKs used to select
or calibrate reference versions and APKs counted in evaluation. Report held-out
results if available; otherwise state the calibration limitation directly.

#### 5.4 Metrics and baselines

Define numerator, denominator, unit, exclusions, and interpretation before
reporting every metric. At minimum distinguish:

- controlled coordinate/version precision and recall;
- emitted Maven version confirmation rate against source trees;
- full source coordinate/version coverage;
- source-version-constrained upper-bound confirmation;
- no-signal case counts, excluded from zero-denominator accuracy rates;
- vulnerability workflow examples, separate from vulnerability accuracy.

Report simple baselines only where their inputs, scope, and comparison protocol
are comparable. Include threshold/confidence interpretation and per-APK or
per-family distributions alongside aggregates.

#### 5.5 Results

Organize results by RQ, not by development chronology. Show controlled results,
clean/partial real results, coverage and gap categories, then bounded
CycloneDX/OSV examples. Put the source-version-constrained result in a visibly
separate upper-bound subsection. Include negative or rejected experiments only
where they explain a design decision or limitation.

#### 5.6 Discussion

Answer each RQ directly. Interpret the difference between confirming emitted
versions and recovering the full source dependency set. Discuss what reference
coverage, matcher recall, version similarity, artifact-family ambiguity, and
confidence gating contribute to the observed results.

#### 5.7 Threats to validity

Address the categories that apply:

- **Internal:** reference calibration overlap, threshold selection, database
  snapshot, evaluator correctness, validation-copy modifications, and
  nondeterministic external vulnerability API responses.
- **External:** F-Droid/source-available sample selection, app-family
  imbalance, unsupported ecosystems, native-heavy apps, protectors, and
  dynamic code.
- **Construct:** Gradle runtime dependencies are a proxy for packaged code;
  emitted-version confirmation is not full recall; confidence labels are not
  calibrated probabilities unless calibration evidence supports that claim.
- **Conclusion:** denominators, sparse clean cases, non-independent APKs,
  multiple APKs per family, and uncertainty in source-dependency resolution.

### 6. Conclusion

Summarize the method, answer the central problem, give the strongest bounded
findings, state limitations, and list concrete future work. Do not introduce
new results or imply that the upper-bound lane is production performance.

### References and optional appendices

Use primary academic papers, official standards, and official tool/API
documentation. If venue limits permit, include supplementary per-APK tables,
full feature/parameter definitions, protocol details, hashes, run manifests,
and reproduction commands in appendices or an artifact package.

## Provisional result values and safeguards

The following are values documented in current thesis artifacts, not yet
submission-ready measurements:

| Evidence lane | Documented result | Required language / safeguard |
|---|---:|---|
| Controlled | 84/84 expected versions across 72 fixtures | Scope to generated controlled fixtures; refresh exact fixture/evaluator files |
| Clean source-validated | 47/47 emitted Maven versions across 5 APKs | Show that three cases are sparse; do not generalize from this slice alone |
| Partial source-validated | 880/1,790 emitted versions across 97 APKs | Call this emitted-version confirmation; explain mismatches and exclusions |
| Combined source-validated | 927/1,837 across 102 APKs | Not full dependency recall or broad population accuracy |
| Full source denominator | 927/12,082 documented as 7.7%; shared DB exact-version coverage 1,231/12,082 documented as 10.2% | Use the 106-case source-tree scope (102 Maven-emitting cases plus four no-Maven-signal controls); keep the 110-case transparency inventory separate |
| Source-version constrained | 6,772/6,772 across 106 source-tree cases | Upper-bound recognition only; source versions constrain candidate references |
| OSV demonstrations | F-Droid: zero returned; Jackson 2.9.10.8: three confirmed advisories | Functional examples only, not vulnerability precision/recall |

## Current evidence and reproducibility checkpoint

The theses, evaluation dashboards, controlled-evaluation notes, task history,
and decision records provide the recorded evidence used by the paper. The
current checkout does not contain every row-level export, generated fixture,
reference-database snapshot, or run manifest, so the paper must distinguish
documented results from independent recalculation. No experiment rerun is
required for the manuscript.

Before Results text is treated as final:

1. Cite the exact thesis/evaluation record and snapshot provenance for each
   number, including the 20 June 2026 PFE snapshot where applicable.
2. Preserve the denominator mapping: 102 Maven-emitting APKs for `927/1837`,
   106 source-tree cases for `927/12082` and the source-known upper bound, and
   110 cases only for the broader transparency inventory.
3. Disclose calibration overlap, validation-only source copies, source-side
   evidence limitations, and unavailable row-level inputs where relevant.
4. If a machine-readable release package is later supplied, use it to check
   arithmetic and regenerate plots; this is a reproducibility enhancement,
   not a prerequisite to reporting the recorded results.
5. Synchronize repeated numbers and terminology across the manuscript from the
   documented evidence matrix.

## Planned figures and tables

- **Figure 1:** Proposed method workflow and evidence flow.
- **Figure 2:** Evaluation lanes and the claims each lane can support.
- **Figure 3:** Per-APK or per-family emitted-version results, with clean and
  partial strata distinguished.
- **Table 1:** Related work dimensions: target, evidence, version support,
  transformations, output, and evaluation limitations.
- **Table 2:** Dataset strata, case counts, ground truth, and metric eligibility.
- **Table 3:** Controlled and source-validated results with denominators.
- **Table 4:** Failure taxonomy and representative examples.
- **Table 5:** Accepted, rejected, disabled, and report-only experiment
  decisions, if within the venue's space limit.

## Current checkpoint

- **Completed:** Paper direction selected; supervisor outline adopted; English
  language selected; initial evidence and reproducibility risks identified;
  source-grounded foundation audited for working-paper drafting.
- **Drafting checkpoint:** The first working drafts of Sections 1–6 are
  present. Sections 2–6 are synchronized to detailed working drafts; the
  Abstract is provisional. Section 4 separates method design from concrete
  module/toolchain details and reflects current source behavior. Section 5
  preserves metric denominators, the documented 30/35 earlier checkpoint and
  later 72/84 controlled snapshot, and report-only experiment boundaries.
- **Evidence gate in progress:** Trace manuscript claims to the retained thesis
  and evaluation records, disclose limits on independent recalculation, and
  resolve evaluation/calibration overlap; denominator membership is frozen as
  102 emitting, 106 source-tree, and 110 transparency-inventory cases.
- **Available drafting sources:** Working drafts for the Introduction, State
  of the Art, Proposed Approach, and Implementation/Experimental Evaluation,
  plus the evidence matrix, citation metadata register, manuscript scaffold,
  and readiness audit are present under `papers/`.
- **Drafting audit completed:** `PAPER_CLAIM_AUDIT.md` now maps the major
  claims in Sections 2–5 to authoritative sources, permitted interpretations,
  and release gates.
- **Integrated manuscript:** `INTEGRATED_MANUSCRIPT_DRAFT.md` contains all six
  sections in supervisor order and is synchronized with the detailed drafts.
  The Abstract is explicitly provisional; reported figures are documented
  thesis/evaluation snapshots with independent-recalculation limits stated.
- **References:** `REFERENCES_DRAFT.md` now provides the working author–year
  entries used in the manuscript; ambiguous same-author/same-year citations
  and official Android documentation suffixes are disambiguated.
- **Tables and figure:** A qualitative related-work comparison (Table 1),
  evaluation-strata/eligibility summary (Table 2), and editable APK-to-SBOM
  workflow diagram (Figure 1) are integrated. Per-family and source-gap plots
  remain pending because their row-level source data are missing.
- **Next writing action:** Finish figures/tables from the documented aggregates,
  complete the claim-contract audit, choose venue-specific citation/style
  rules, and revise the Abstract as the final manuscript edit. Do not infer
  missing per-case data or imply that experiments were rerun.
- **Drafting status:** First full working-paper pass is complete. Evidence
  restoration, snapshot reconciliation, venue formatting, and final audit are
  release tasks rather than unfinished section drafting.
- **Venue decision:** Still open; adjust length, reference style, and artifact
  policy after a target venue is selected.
