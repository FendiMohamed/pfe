# Section 2 — Introduction (Working Draft)

## 2.1 Context

Software bills of materials (SBOMs) support inventory and software supply-chain
risk management by recording the components that make up a software product
(NTIA, n.d.; Boyens et al., 2022). An auditor of an Android application may
receive only the delivered APK, without its source tree, dependency
declarations, or build environment. The APK exposes compiled DEX files and
resources, rather than the original resolved dependency graph (Android
Developers, n.d.-a). During the build, D8 converts Java bytecode to DEX, and
R8 can remove, rewrite, and rename code (Android Developers, n.d.-c, n.d.-d).
Android libraries may also be packaged as AARs containing code alongside
resources, manifests, or native libraries, complicating a direct mapping from
visible bytecode to a published Maven artifact (Android Developers, n.d.-b).

For an APK-only analyzer, identifying a likely library is therefore only one
part of the task. The analyzer must also decide whether the available evidence
supports a particular release, communicate uncertainty to downstream SBOM
consumers, and avoid treating a tentative version as definitive vulnerability
evidence. These distinctions matter because a component inventory can guide
security review, but neither an SBOM format nor a vulnerability lookup
establishes that a candidate library is present in the packaged application.

## 2.2 Problem statement

This work studies the recovery of Maven component and version evidence from a
compiled Android APK using a versioned reference set. The target output is an
SBOM that retains the basis and strength of each attribution. We distinguish
three questions: whether evidence supports a component family, whether it
supports one exact published version, and whether that version evidence is
sufficient for a downstream vulnerability report.

The inference is affected by several independent limits. The reference set may
not contain the packaged artifact or release. Adjacent releases can have
similar bytecode; Android packaging can merge code into one or more DEX files;
and shrinking, renaming, optimization, or inlining can remove or alter useful
features (Backes et al., 2016; Wu et al., 2023; Xie et al., 2024). A Maven
coordinate may also be published through multiple JVM or Android artifact
variants. Native libraries, dynamically loaded code, and DEX content that the
parser cannot inspect impose additional boundaries. Thus, component identity,
exact-version attribution, and vulnerability interpretation cannot safely be
collapsed into a single match decision.

Source dependency trees help evaluate the implementation, but they answer a
different question from APK inspection. A resolved dependency may not survive
shrinking and packaging, while the APK can expose packaged code whose Maven
identity is not recoverable from a simple dependency declaration. The source
tree is therefore a validation proxy, not a complete oracle for what code is
present in the binary; this distinction is also reflected in benchmark work on
partial and transformed library code (Android Developers, n.d.-c; Zhan et al.,
2021b; Gu et al., 2025). An APK-only invocation cannot use source-side versions
as candidate hints without changing the task being evaluated. We therefore
keep source validation separate from ordinary APK-only matching and report
source-version-constrained recognition only as an upper-bound analysis.

## 2.3 Related work and motivation

Android third-party-library detection has used package and class profiles,
dependency graphs, opcode and call-chain features, structural similarity, and
learned representations. These methods address overlapping but distinct
tasks: finding a library family, distinguishing its versions, and remaining
useful after build transformations. LibScout established profile-based
matching, while ATVHunter connected version identification with
vulnerability-oriented analysis (Backes et al., 2016; Zhan et al., 2021a).
Later work studies more precise signatures and the effects of optimization
(Wu et al., 2023; Xie et al., 2024), and recent version-level work uses class
structural similarity (Zhou et al., 2025). Systematic assessment and benchmark
work further show why dataset construction, ground-truth units, reference
coverage, and transformation settings must be considered when interpreting
reported results (Zhan et al., 2021b; Gu et al., 2025).

This literature motivates two choices in our study. First, evaluation must
separate controlled fixtures, agreement for versions the tool emitted,
coverage of the full source-derived denominator, and source-version-constrained
recognition. These quantities have different denominators and support
different conclusions. Second, a practical APK-to-SBOM workflow should retain
supporting evidence and ambiguity through reporting, rather than turning every
plausible similarity into an unqualified component or vulnerability claim.
Section 3 develops the comparison and research gap in detail.

## 2.4 Approach overview

The implemented pipeline inspects APK metadata and successfully parsed DEX
files, extracts bytecode-derived features, and compares them with versioned
Maven reference profiles stored in a SQLite database. Its weighted evidence
fusion first shortlists component families and then ranks candidate versions.
It keeps identity evidence separate from version confidence and preserves
close alternatives when the evidence does not justify a single release. The
reporting layer emits CycloneDX components, records native files as
hash-identified file components, and can query OSV using the reported
component/version evidence. An advisory returned by that workflow is treated
as associated evidence, not independent proof of component presence or
exploitability.

The evaluation uses separate evidence lanes. Controlled fixtures measure
recovery against known expected versions. Clean and partial source-validated
APK cases measure agreement for emitted Maven versions. A separate analysis
measures coverage against the full source-derived coordinate/version set,
while a source-version-constrained lane tests recognition when candidate
versions are restricted using source evidence. The latter is reported as an
upper bound, not as normal APK-only performance. Cases with no Maven signal,
native-only or hidden code, and report-only experiments remain explicit
boundaries rather than being forced into an accuracy denominator.

## 2.5 Contributions and scope

This paper makes four bounded contributions:

1. It describes an implemented static pipeline for recovering Maven/JVM
   component and version evidence from compiled Android APKs and emitting
   CycloneDX.
2. It documents an evidence-aware reporting policy that separates component
   identity, exact-version confidence, ambiguity, native-file handling, and
   downstream vulnerability interpretation.
3. It evaluates the implementation through controlled and source-validated
   lanes, with each result tied to its unit, numerator, denominator, and
   coverage limits.
4. It records failure causes and rejected or report-only experiments to
   characterize practical limitations alongside successful cases.

The paper does not claim universal Android dependency recovery, complete
packaged-code recall, calibrated probabilistic confidence, native package or
version attribution, or vulnerability-detection precision. AI/R8 assistants
and structural rerankers remain diagnostic or report-only unless a separately
validated promotion gate changes that status. These scope limits define the
claims made throughout the paper; the numerical results remain provisional
until the corresponding raw artifacts and frozen run manifest are available.

## 2.6 Paper organization

Section 3 presents the structured mapping review and synthesizes the research
gap. Section 4 describes the proposed evidence model, workflow, and decision
policy. Section 5 documents the implementation and experimental evaluation,
including research questions, protocol, results, discussion, and threats to
validity. Section 6 summarizes the findings, limitations, and future work.

> **Citation note:** Author–year citations are a working form linked to the
> verified local bibliography. Adapt the style after selecting a venue; the
> working Android Developers suffixes are mapped in `REFERENCES_DRAFT.md`.
