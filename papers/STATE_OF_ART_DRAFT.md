# Section 3 — State of the Art (Working Draft)

> **Citation status.** The prose uses provisional author–year citations tied to
> the verified local bibliography. The venue and citation style remain open.
> The original review corpus is kept distinct from the post-freeze literature
> update noted in Section 3.4.

## 3.1 Review scope and comparison dimensions

This section synthesizes a structured mapping review of methods for recovering
third-party components from compiled Android applications, with emphasis on
library identity, exact-version attribution, build transformations, and
downstream SBOM or vulnerability use. The thesis protocol (version 1.0,
frozen 21 June 2026) searched ACM Digital Library, IEEE Xplore, SpringerLink,
ScienceDirect, USENIX, and arXiv; Google Scholar supported discovery and
citation chaining. Search terms combined Android/APK/DEX, component/SBOM,
recovery tasks, and transformation/version/vulnerability concepts. The seed
corpus was assembled iteratively before the protocol was frozen. Its original
database-specific query counts and deduplication flow were not retained, so
this review does not claim an exhaustive selection process or a systematic
review with a complete screening-flow count. Full-text claims in the core
synthesis rely on the 15 Tier A studies inspected under the protocol; five
Tier B records served as supplementary search leads, not independent support
for precise quantitative claims (Kitchenham & Charters, 2007; Zhan et al.,
2021b).

The comparison uses task granularity, evidence representation, version
support, transformation coverage, output, ground-truth construction, unit of
analysis, and artifact availability. We distinguish library-family presence
from exact-version detection and vulnerability interpretation. Reported
metrics remain attached to their original datasets and definitions; they are
not pooled into a ranking. A post-freeze search update is identified
separately where relevant.

## 3.2 Android library identity detection

Android TPL detectors use several overlapping evidence families. Profile-based
methods create reference signatures from known libraries and compare them
with code in an APK. LibScout represents a library through a profile hierarchy
and fuzzy method descriptors, which can tolerate some identifier changes
(Backes et al., 2016). Graph and class-structure methods reduce their reliance
on package names: LibD uses relations among classes and opcode-derived
fingerprints, while ORLIS uses a coarse call-graph-based filter followed by
class signatures and class mapping (Li et al., 2017; Wang et al., 2018).
LibPecker and LibID likewise use class dependencies or class correspondence
to identify library code when package layout alone is unreliable (Zhang et
al., 2018, 2019).

Later systems combine coarse candidate generation with more detailed
matching. ATVHunter uses class-dependency information to separate candidate
library code, then combines control-flow filtering and opcode-based matching
for version decisions (Zhan et al., 2021a). LibScan first constructs candidate
class correspondences from code features and refines them with method-opcode
and call-chain-opcode similarity; it also uses early stopping and intermediate
results to control analysis cost (Wu et al., 2023). These methods illustrate a
tradeoff: a coarse stage can make analysis tractable but can cap recall if it
omits a true candidate, while a permissive fine stage can admit false
correspondences. A library-level match should therefore be interpreted in
light of the candidate-generation and class-mapping evidence that produced it.

Learned representations form another line of work. LibAttention trains a
Transformer-based model over Smali-derived input for TPL presence detection
(Pan et al., 2025). This learned presence task is distinct from verifying a
Maven coordinate and its exact release. Across these approaches, the evidence
shift from package names toward signatures, relations, opcodes, and learned
features improves the range of available signals, but no signal is invariant
to every transformation or sufficient on its own for every claim type.

## 3.3 Version identification and adjacent-release ambiguity

Exact-version attribution is a stricter task than detecting that a library
family is present. It requires evidence that distinguishes releases of the
same component, and its success is bounded by whether the correct artifact and
version occur in the reference corpus. ATVHunter connects version detection
with a downstream vulnerability database, combining coarse and fine-grained
bytecode evidence to report vulnerable library versions (Zhan et al., 2021a).
LibScan and LibHunter use increasingly detailed method, opcode, and call
context features; LibHunter specifically examines optimization effects such
as method inlining and call-site optimization (Wu et al., 2023; Xie et al.,
2024).

SAD makes version discrimination explicit through class-dependency graphs,
class summaries, and structural matching, with evidence such as field
operations and literals used to distinguish candidate classes and versions
(Zhou et al., 2025). Its study also defines a stricter version-level metric
that counts additional incorrect versions as false positives. On SAD's
obfuscated dataset, its reported version-level F1 is 84.82%; the value belongs
to that study's dataset and strict metric, and should not be compared directly
with results using another candidate construction or error definition (Zhou
et al., 2025). This accounting difference is consequential: a detector that
finds the right release while also emitting several wrong alternatives does
not provide the same version claim as one that returns only the supported
release.

These studies motivate reporting candidate ambiguity and exact-version
evidence separately from family identity. Adjacent releases may share most
classes and methods; changes in artifact packaging can also alter which
classes appear without changing the underlying project identity. If the
reference database lacks the actual version, an APK-side similarity match
cannot recover it as an exact candidate. Version coverage, matcher behavior,
and false-positive accounting must therefore be visible alongside any
version-level result.

## 3.4 Obfuscation and build transformations

Renaming, package flattening, shrinking, optimization, and method inlining
change different parts of an APK's observable code. Name-based evidence can
fail under renaming; shrinking can remove classes and methods; optimization
can rewrite or inline methods and change the relations on which opcode or
call-chain comparisons depend. Transformation resilience must consequently
be evaluated by transformation and by claim level rather than summarized as
one robustness property.

LibScan evaluates matching under obfuscation and code transformations, while
LibHunter focuses on how optimization strategies alter TPL detection and
introduces features for call-site optimization and inlining (Wu et al., 2023;
Xie et al., 2024). SAD's evaluation separately reports obfuscated and
optimized data, and identifies performance changes between those conditions
(Zhou et al., 2025). Together, the studies show that strong library-level
results do not guarantee equally strong exact-version results under the same
transformations. Small release-specific differences may be the very features
removed or merged by a build pipeline.

After the thesis protocol froze, a new arXiv preprint introduced LibFan, a
learning-based detector that combines context-aware method representations
with functional partitions to address aggressive transformations and partial
library reuse (Fan et al., 2026, preprint). It is a relevant emerging direction
for the transformation and partial-inclusion problem. Because it postdates
the frozen review and has not been incorporated into the original seed-corpus
screening and extraction record, it is cited here as a post-freeze update,
not as part of the 15-study core synthesis or as a directly comparable result.

## 3.5 SBOM and vulnerability integration

Most of the reviewed Android TPL detectors evaluate matching and report
libraries, classes, versions, or vulnerability-related results. Their primary
evaluation targets are not complete, evidence-provenance-rich SBOM records.
ATVHunter demonstrates a version-aware path into vulnerability analysis, but
a vulnerability result still depends on the quality of component and version
attribution (Zhan et al., 2021a). UniBOM is adjacent work on an integrated
binary, filesystem, and source workflow that generates and analyzes SBOMs;
its firmware and IoT settings do not provide Android Maven exact-version
ground truth (Safronov et al., 2025).

This distinction is about evidence and authority, not merely output format. A
standard SBOM can encode component records (OWASP CycloneDX Project, n.d.;
SPDX Workgroup, n.d.), but format conformance alone does not establish that a
guessed component or version is present in an APK.
Likewise, a vulnerability database match against an uncertain version does
not independently confirm that version or show exploitability. The system
studied here therefore treats component evidence, version confidence,
ambiguity, and downstream advisory interpretation as separate report
properties; this is the operational focus of the proposed workflow.

## 3.6 Evaluation practice and research gap

Assessment and benchmark studies demonstrate why detector metrics need their
dataset and ground-truth construction. The systematic assessment evaluates
tools across separate criteria, including candidate-library construction,
effectiveness, efficiency, version identification, obfuscation resilience,
and usability (Zhan et al., 2021b). TPL-Benchmark presents 6,055 APK/source
pairs with version annotations and compares detectors on a defined subset of
that corpus. In its comparison slice, 946 applications and 28,210 valid
mappings are used; LibPecker's reported 60.15% library-level
F1 is specific to that candidate and evaluation protocol, not a general
accuracy ceiling (Gu et al., 2025). Differences in candidate set, reference
database, source mapping, transformation, and treatment of extra versions
make cross-study percentage ranking unsound.

Table 1 summarizes representative methods along the dimensions used in this
review. It is a task-and-evidence comparison, not a leaderboard; each study's
quantitative results remain attached to its own dataset and metric.

| Study or line | Main task and evidence | Version/transformation scope | Relevance and comparison limit |
|---|---|---|---|
| LibScout (Backes et al., 2016) | TPL profiling with hierarchical package/class and fuzzy method evidence | Profile-based family and release matching; tolerates some identifier changes | Establishes profile matching as a baseline design; reference coverage bounds possible matches |
| LibD, ORLIS, LibPecker, and LibID (Li et al., 2017; Wang et al., 2018; Zhang et al., 2018, 2019) | Class, dependency-graph, call-graph, and opcode-derived structural signatures | Reduces dependence on package names and addresses selected obfuscation conditions | Shows alternative identity evidence; their datasets and class-correspondence rules are study-specific |
| ATVHunter (Zhan et al., 2021a) | Version detection through dependency-graph separation, control-flow filtering, and opcode matching | Explicit version and vulnerability-identification workflow | Motivates version-aware evidence; does not establish complete native/dynamic coverage or vulnerability precision |
| LibScan (Wu et al., 2023) | Fingerprint-based class correspondence refined by method- and call-chain-opcode similarity | Evaluates selected obfuscation and D8/R8 transformations; includes early stopping | Motivates coarse-to-fine matching; candidate generation and tuned transformation settings affect results |
| LibHunter (Xie et al., 2024) | Empirical analysis of optimization effects with features for inlining and call-site optimization | Focuses on selected R8 optimization strategies and transformation variants | Motivates transformation-specific evaluation; results do not establish universal R8 invariance |
| SAD (Zhou et al., 2025) | Version-level detection using class-dependency graphs, structural summaries, and class matching | Reports obfuscated/optimized conditions and a strict version-level metric | Highlights extra-version false-positive accounting; its reported metrics remain dataset-specific |
| LibAttention (Pan et al., 2025) | Transformer-based representation over Smali for TPL-presence detection | Learned representation evaluated for the study's presence task | Motivates learned evidence; library presence does not itself establish an exact Maven release |
| TPL-Benchmark (Gu et al., 2025) | Multi-tool empirical comparison over version-annotated APK/source pairs | 6,055 pairs overall; a 946-app/28,210-mapping comparison slice | Demonstrates benchmark-construction and denominator sensitivity; its metric is not a cross-study ceiling |
| UniBOM (Safronov et al., 2025) | Integrated binary/filesystem/source SBOM and vulnerability workflow | Firmware/IoT-oriented evaluation rather than Android Maven exact-version ground truth | Motivates end-to-end reporting; does not provide a directly comparable Android version benchmark |

The common methodological lesson is to state what was detected, what counted
as ground truth, the unit and denominator, transformation conditions, and
whether the reference corpus could contain the target release. The same
discipline applies to the present evaluation: controlled fixtures, emitted
version confirmation, full source-denominator coverage, and
source-version-constrained recognition are different evidence lanes and must
remain separate.

Within the reviewed Android TPL and adjacent SBOM corpus, the operational gap
addressed by this paper is the connection between binary-derived component
evidence and a downstream SBOM/vulnerability workflow that preserves
provenance, version uncertainty, coverage limits, and validation class. This
is a bounded characterization of the implementation, not a claim that no
prior detector performs version identification or that the system is
universally novel or superior. The following section describes how the
implementation represents and reports these distinct evidence types.

## Review and citation notes

- The review protocol and extraction scope are documented in the master
  thesis, Appendix A. The frozen seed corpus contains 15 Tier A full-text
  studies and five Tier B supplementary records; the original search-result
  and deduplication counts were not preserved.
- `Fan et al. (2026)` is a post-freeze preprint update. It is not included in
  the frozen corpus counts. Its primary source is arXiv:2609.31409.
- Author–year style is provisional. Final reference formatting and any venue
  requirements remain open until a venue is selected.
