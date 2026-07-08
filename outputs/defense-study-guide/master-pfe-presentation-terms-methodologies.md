# Master/PFE Defense Study Guide: Words, Concepts, and Methodologies

Use this file as a defense vocabulary and methodology cheat sheet. It is based on the Master thesis, the PFE thesis, and the expanded presentation notes.

Sources used:

- `output/pdf/MASTER-thesis-updated.pdf`
- `output/pdf/PFE-thesis-updated.pdf`
- `outputs/graduation-defense-expanded-old-style-deck/output/presentation-speech-page-by-page.md`
- `docs/thesis/DEFENSE_PRESENTATION_GUIDE.md`
- `work/Supervisor_MVP_Proposal.md`
- `work/state of the art/Updated_State_of_the_Art_APK_SBOM.md`
- `docs/project_handbook/decisions/DECISION_RATIONALE.md`
- `docs/project_handbook/research/PAPER_TO_IMPLEMENTATION.md`
- `docs/project_handbook/overview/PROJECT_GOALS_AND_CURRENT_STATE.md`
- `docs/project_handbook/evaluation/DATASETS_METRICS_AND_RESULTS.md`
- `docs/project_handbook/evaluation/FAILED_EXPERIMENTS.md`
- `docs/project_handbook/implementation/AI_R8_AND_HYBRID.md`
- `docs/evaluation/AI_R8_FINAL_EVALUATION.md`

## How To Use This File

Do not memorize definitions word for word. For each concept, make sure you can answer three questions:

1. What does it mean?
2. Why does it matter in my project?
3. What boundary or limitation must I not overclaim?

The safest defense posture is:

> My project recovers useful APK-derived SBOM evidence, but it keeps identity, exact version, vulnerability authority, uncertainty, and validation lane separate.

## The Project In One Minute

The Master thesis defines the trust problem: a recovered SBOM is only useful if each claim exposes its evidence, confidence, provenance, uncertainty, and validation boundary.

The PFE thesis implements the system: a static APK-to-SBOM pipeline that extracts evidence from compiled APKs, compares it with Maven reference profiles, emits CycloneDX SBOM output, queries OSV for vulnerabilities, validates against source evidence when possible, and keeps AI/R8 assistance report-only.

The presentation combines both:

- problem: APKs do not preserve clean dependency metadata;
- approach: static evidence extraction plus Maven reference matching;
- output: CycloneDX, reports, vulnerability evidence, dashboards;
- evaluation: controlled, clean, partial, upper-bound, report-only, and limitation lanes;
- boundary: no fake complete SBOM, no AI authority, no 100% APK-only accuracy claim.

## Core Acronyms You Must Know

| Term | Meaning | In your project | Safe defense sentence |
|---|---|---|---|
| `APK` | Android Package Kit | The compiled Android application you analyze. | "The input is the compiled APK, not the source project." |
| `DEX` | Dalvik Executable | Bytecode files inside APKs, such as `classes.dex`. | "DEX is the main bytecode evidence surface used by the matcher." |
| `SBOM` | Software Bill of Materials | A structured inventory of software components. | "My output is a recovered, confidence-aware SBOM, not a build-generated SBOM." |
| `CycloneDX` | Standard SBOM format | The project emits CycloneDX JSON. | "CycloneDX makes the recovered result interoperable." |
| `PURL` | Package URL | Standard package identifier used in SBOM components. | "PURLs encode Maven package identity in a standard form." |
| `CVE` | Common Vulnerabilities and Exposures | Vulnerability identifier. | "A CVE claim depends on the confidence of the component and version claim." |
| `OSV` | Open Source Vulnerabilities | Vulnerability lookup source used by the project. | "OSV maps package/version evidence to vulnerability records." |
| `R8` | Android shrinker and optimizer | It can rename, shrink, optimize, inline, or remove code. | "R8 is one reason exact-version recovery is hard." |
| `D8` | Android compiler from Java bytecode to DEX | Used when converting Maven JAR/AAR references to comparable DEX. | "D8 helps put references and APK bytecode into a comparable representation." |
| `AAR` | Android Archive | Android library artifact with code, resources, manifest, and rules. | "AARs may contain more than bytecode, so conversion and evidence coverage matter." |
| `JAR` | Java Archive | Java library artifact. | "JARs provide JVM bytecode that can be converted into reference DEX features." |
| `Maven` | Java/Android package ecosystem | Reference components are represented as Maven coordinates. | "The target package identity is usually `group:artifact:version`." |
| `Gradle` | Android build system | Source validation often uses Gradle dependency trees. | "Gradle evidence is used for validation when source is available, not for APK-only production decisions." |
| `API` | Application Programming Interface | API references can be a static evidence feature. | "API evidence can help, but global API weighting was not promoted." |
| `TPL` | Third-Party Library | External library embedded in an app. | "The project recovers third-party library evidence from compiled APKs." |
| `SCA` | Software Composition Analysis | Detecting components and vulnerabilities. | "This is binary-side SCA for APKs, not normal source-side SCA." |
| `SPDX` | Another SBOM standard | Discussed in background/state of the art. | "SPDX is relevant, but the implementation uses CycloneDX." |
| `AI` | Artificial Intelligence | Report-only assistance in this project. | "AI helps triage; it does not select final SBOM components." |
| `ML` | Machine Learning | RandomForest assistant and related training. | "ML output is report-only and guarded." |
| `DL` | Deep Learning | Transformer prototypes. | "DL is research/prototype evidence, not production authority." |
| `F1` | Harmonic mean of precision and recall | Used for AI/model results and literature metrics. | "F1 combines precision and recall, but the thesis metrics are split by evidence lane." |
| `CVSS` | Severity scoring system | Describes vulnerability severity. | "CVSS severity does not prove the vulnerable component is present." |
| `EPSS` | Exploit prediction score | Estimates exploitation likelihood. | "EPSS is downstream context, not package identity evidence." |
| `KEV` | Known exploited vulnerabilities | Catalog of exploited vulnerabilities. | "KEV can prioritize risk only after component/version evidence is credible." |
| `NVD` | National Vulnerability Database | Vulnerability database discussed in background. | "NVD/OSV data must inherit the confidence of the detected package version." |

## Core Concept Groups

### Source-Generated SBOM vs Recovered SBOM

Source-generated SBOM:

- comes from source code, package managers, lockfiles, or build metadata;
- is usually more authoritative because it sees the dependency graph before compilation.

Recovered SBOM:

- starts only from the compiled APK;
- uses indirect evidence from DEX, manifest, resources, native files, and reference matching;
- must expose confidence and uncertainty.

Defense answer:

> A build-generated SBOM is preferable when source is available. My recovered SBOM is for audit situations where the only available artifact is the APK.

### Component Identity vs Exact Version

Component identity asks:

> Is this library or Maven coordinate present?

Exact version asks:

> Which release is present, and is the evidence strong enough?

Why it matters:

- A library can be easy to identify but hard to version.
- CVE results often depend on exact version.
- Adjacent versions may have almost identical bytecode.

Defense answer:

> Identity evidence and exact-version evidence are different claim strengths. A strong identity claim does not automatically justify a confirmed CVE.

### Trustworthy Claim

A trustworthy recovered claim should expose:

- subject APK;
- component or artifact family;
- claim type: identity, version, bounded version set, native file, risk;
- supporting evidence;
- opposing or missing evidence;
- confidence;
- ambiguity;
- provenance;
- validation lane;
- allowed security interpretation.

Defense answer:

> The Master thesis treats a recovered SBOM row as a claim with evidence, not just a string in a file.

### Evidence Provenance

Provenance means where evidence came from:

- APK bytecode;
- manifest;
- resource strings;
- native files;
- Maven reference artifact;
- source dependency tree;
- generated report;
- validation artifact.

Defense answer:

> Provenance tells the reviewer why the tool believes a component is present and what evidence supported that belief.

### Confidence

Confidence is the system's strength label for a claim. In your thesis, the important split is:

- identity confidence;
- version confidence;
- vulnerability authority.

Defense answer:

> Confidence is not decoration. It controls whether a result is exact, likely, ambiguous, report-only, or should be withheld.

### Ambiguity

Ambiguity appears when multiple candidates are plausible, especially adjacent versions.

Example:

- `androidx.fragment:fragment` version 1.6.1 vs 1.6.2 may be hard to separate if bytecode evidence is nearly identical.

Defense answer:

> Ambiguity is not a reason to force a newer version. It is a reason to preserve alternatives or abstain.

### Abstention

Abstention means refusing to make an exact claim when evidence is too weak.

Possible outputs:

- emit exact coordinate/version;
- emit component identity but not exact version;
- show candidates for analyst review;
- report only a native file hash;
- record a reference gap;
- classify the case as limitation/boundary.

Defense answer:

> Abstention is a safety mechanism. It prevents false precision.

### Authority Boundary

Authority boundary means deciding what is allowed to affect the final SBOM and CVE output.

In your project:

- deterministic matcher: authoritative for selected versions and SBOM components;
- AI/R8 diagnostics: report-only;
- source validation: evaluation evidence;
- source-known v2 lane: upper-bound evaluation.

Defense answer:

> A report-only signal can explain risk, but it cannot silently change selected versions, SBOM components, or vulnerability labels.

## Android And Binary Analysis Concepts

### APK Structure

Important APK regions:

- `AndroidManifest.xml`: package, permissions, components, SDK metadata;
- `classes.dex`, `classes2.dex`: bytecode;
- `resources.arsc`, `res/`, `assets/`: resources and strings;
- `lib/*.so`: native libraries;
- signatures and metadata.

Defense answer:

> No single APK region is a complete dependency inventory, so the analyzer combines multiple evidence surfaces.

### DEX Bytecode

DEX is Android executable bytecode. It contains classes, methods, instructions, references, and literals after compilation.

Why it matters:

- source names may be transformed;
- dependency manifests are gone;
- DEX is the main evidence surface for matching Maven references.

Defense answer:

> DEX analysis lets the tool compare shipped bytecode evidence with reference bytecode profiles.

### R8 Transformations

R8 can:

- rename classes, methods, and fields;
- remove unused code;
- inline methods;
- merge classes;
- simplify constants and instructions;
- shrink resources.

Defense answer:

> R8 can preserve enough evidence for identity while destroying evidence needed for exact version selection.

### Native Libraries

Native `.so` files are compiled native code.

In your MVP:

- they are reported as hash-backed file artifacts;
- exact Maven/package version identification for native code is out of scope.

Defense answer:

> Native files are visible and reported, but native package-version recovery requires a separate reference and provenance pipeline.

### Hidden or Dynamic Code

Examples:

- hidden DEX;
- encrypted payloads;
- custom class loaders;
- downloaded code after installation;
- protector-style behavior.

Defense answer:

> Static analysis can report risk indicators, but it should not invent Maven components for code it cannot inspect.

## SBOM And Vulnerability Concepts

### CycloneDX

CycloneDX is the SBOM format used by the project. It supports components, package URLs, properties, and vulnerability-oriented workflows.

Defense answer:

> I use CycloneDX because it turns recovered evidence into a standard artifact instead of a private report format.

### Package URL / PURL

A PURL is a standardized package identifier, for example a Maven component.

Defense answer:

> PURL gives the recovered component a standard package identity that can be used by SBOM and vulnerability tools.

### OSV Lookup

OSV maps package ecosystem and version evidence to vulnerability advisories.

Important boundary:

- OSV can only be as reliable as the package/version claim sent to it.

Defense answer:

> The vulnerability layer inherits the confidence of the detected component and version.

### Vulnerability Claim Strength

A vulnerability can be:

- confirmed: strong exact component/version evidence;
- source-confirmed: source validation agrees;
- potential: version or evidence uncertain;
- report-only: useful warning but not authoritative.

Defense answer:

> I do not turn every scanner hit into a confirmed CVE. The CVE claim cannot be stronger than the version evidence.

## Pipeline Concepts From The PFE Thesis

### Static APK-to-SBOM Pipeline

Main stages:

1. inspect APK archive, manifest, DEX, resources, assets, native files;
2. extract packages, classes, methods, opcodes, literals, API references, and structural features;
3. build Maven reference profiles from JAR/AAR artifacts;
4. store reference features in SQLite;
5. match APK evidence to reference features;
6. select component/version candidates with confidence labels;
7. emit CycloneDX SBOM;
8. query OSV;
9. generate JSON, Markdown, and HTML reports;
10. validate results against source dependency trees when available.

Defense answer:

> The contribution is an end-to-end evidence-gated workflow, not only a single matching formula.

### APK Extractor

The extractor:

- checks the APK archive;
- computes hashes;
- finds DEX files;
- detects unusual DEX locations;
- records native files and metadata.

Defense answer:

> The extractor prepares raw application evidence before any matching decision.

### DEX Analyzer

The DEX analyzer extracts:

- package names;
- classes;
- methods;
- opcodes;
- literals;
- API references;
- graph/dependency structures.

Defense answer:

> DEX analysis creates the feature set used to compare APK evidence with Maven reference profiles.

### Reference Database

The reference DB stores features for known Maven coordinates and versions.

Built by:

- selecting Maven artifacts;
- downloading JAR/AAR releases;
- converting bytecode into comparable DEX;
- extracting features;
- storing them in SQLite.

Defense answer:

> Reference coverage directly limits what the matcher can recover. If the exact version is absent, the matcher cannot select it.

### Matcher

The matcher compares APK features with reference features.

Evidence families include:

- package evidence;
- class evidence;
- method evidence;
- opcode evidence;
- literals;
- API references;
- dependency or graph structure;
- version-unique hints.

Defense answer:

> The matcher ranks candidates from multiple evidence families, but the score is a ranking signal, not a formal probability.

### Version Decision

Version decision chooses whether the evidence supports:

- exact version;
- likely version;
- candidate only;
- ambiguous alternatives;
- abstention.

Defense answer:

> The version decision is where the system avoids turning weak evidence into a false exact version.

### Reports

Reports include:

- detected components;
- version decisions;
- evidence links;
- vulnerability findings;
- generated artifacts;
- optional report-only AI/R8 sections.

Defense answer:

> The report shows not only what the tool decided, but why it decided it.

## Methodologies You Must Understand

### 1. Structured Mapping / Literature Taxonomy Methodology

Used mainly in the Master thesis and state of the art.

What it does:

- reviews Android TPL and binary component recovery literature;
- groups tools by technique family;
- extracts evidence sources;
- identifies transformation threats;
- compares evaluation practices;
- derives research gaps.

Defense answer:

> The Master thesis transforms the literature into a trust framework by asking what kind of evidence each technique can safely support.

### 2. Evidence-Based Claim Model

Used mainly in the Master thesis.

What it does:

- treats each recovered component as a claim;
- separates identity, version, evidence provenance, confidence, ambiguity, validation, and security authority.

Defense answer:

> The claim model prevents a recovered SBOM row from looking more certain than the evidence allows.

### 3. Static Analysis Methodology

Used in the PFE implementation.

What it does:

- analyzes APK contents without running the app;
- extracts reproducible evidence from files and DEX bytecode.

Strength:

- deterministic, offline, reproducible.

Limitation:

- cannot fully observe runtime-only, downloaded, protected, or hidden code.

Defense answer:

> Static analysis is appropriate for an offline APK audit, but the thesis reports dynamic and protected-code boundaries explicitly.

### 4. Reference-Profile Matching Methodology

What it does:

- build profiles of known Maven library versions;
- compare APK evidence with these profiles;
- rank candidate coordinates and versions.

Defense answer:

> The method adapts reference-profile library detection into a confidence-aware SBOM workflow.

### 5. Source Validation Methodology

What it does:

- uses source dependency trees when available;
- checks whether emitted Maven rows match resolved source dependencies;
- produces clean, partial, no-signal, or limitation classifications.

Important boundary:

- source validation is evaluation evidence, not normal APK-only production input.

Defense answer:

> Source dependency trees validate emitted results after the fact; they do not secretly force the production matcher answer.

### 6. Split Evaluation Methodology

The evaluation is split because one number would hide too much.

Buckets:

- controlled fixtures;
- clean source-validated real APKs;
- partial source-validated real APKs;
- no-Maven-signal controls;
- source-known upper-bound lane;
- report-only diagnostics;
- limitation/boundary cases.

Defense answer:

> I separate evaluation lanes because controlled fixtures, real APKs, and source-known upper bounds answer different questions.

### 7. Fail-Fast Target/Control Promotion Methodology

Used for experiments and failed promotions.

Process:

1. create isolated experiment;
2. test intended target;
3. test controls;
4. compare with current outputs;
5. promote only if target improves without control regressions;
6. otherwise keep diagnostic/report-only.

Defense answer:

> A signal can be real and still unsafe as a default. That is why failed experiments are part of the contribution.

### 8. Report-Only AI/R8 Methodology

AI and R8 diagnostics:

- can add explanations;
- can suggest risk triage;
- can prioritize review;
- cannot change selected versions;
- cannot change CycloneDX components;
- cannot change CVE labels;
- cannot change source-validation metrics.

Defense answer:

> AI is useful as assistance, but the deterministic matcher remains the authority.

### 9. Source-Version Constrained Upper-Bound Methodology

The v2 lane uses exact source coordinate/version slices.

Meaning:

- tests recognition when correct versions are known and present;
- measures gap categories;
- does not represent general APK-only accuracy.

Defense answer:

> The v2 lane is an upper-bound recognition experiment, not a production accuracy score.

## Decision Map: What We Chose, Why, And What We Did Not Choose

Use this section when the jury asks:

- "Why did you choose this MVP?"
- "Why did you not use another tool or method?"
- "Why did you keep some experiments report-only?"
- "What are the important engineering decisions in the PFE?"

The safest answer pattern is:

1. state the decision;
2. give the evidence or constraint;
3. say what was rejected or deferred;
4. connect it to trustworthiness.

Defense sentence:

> The main decision throughout the project was to prefer bounded, evidence-backed claims over impressive but unsafe claims.

### A. Global Research Direction Decisions

| Decision | Why We Made It | What We Did Not Choose | Defense Answer |
|---|---|---|---|
| Focus on APK-to-SBOM recovery, not only TPL detection | The research gap is that academic detectors identify libraries, while practical security workflows need SBOM, versions, PURLs, and CVE interpretation. | A thesis that only detects library names. | "My contribution connects TPL detection to an auditable SBOM and vulnerability workflow." |
| Make exact version a central problem | CVEs and advisories usually apply to affected version ranges. Library identity alone is not enough. | Name-only or family-only vulnerability reporting. | "Saying `gson` is weaker than saying `pkg:maven/com.google.code.gson/gson@2.8.6`." |
| Treat uncertainty as part of the output | Compiled APKs lose build metadata and may be optimized or obfuscated. Weak evidence should not become a strong security claim. | A forced answer for every candidate. | "Uncertainty is not failure; hidden uncertainty is the danger." |
| Use a hybrid static evidence model | No single signal survives all transformations. Names, opcodes, literals, APIs, dependency structure, and metadata each help in different cases. | Package-only, hash-only, or one-feature detection. | "The system combines signals because each signal has its own failure mode." |
| Keep realistic evaluation lanes separate | Controlled APKs, clean real APKs, partial real APKs, and source-known upper bounds answer different questions. | One global score that mixes easy and hard cases. | "Separated denominators prevent exaggerated performance claims." |
| Preserve negative results | Failed experiments explain why the final MVP is conservative. | Hiding failed experiments or repeatedly retesting unsafe ideas. | "A signal can be real but still unsafe as a default." |

### B. MVP Architecture Decisions

| MVP Decision | Why We Chose It | Why We Did Not Choose Others |
|---|---|---|
| Static APK analysis first | The common audit scenario gives only the compiled APK; static analysis is reproducible and can inspect the shipped artifact. | Dynamic-analysis-first was deferred because coverage is incomplete, expensive, and depends on runtime behavior. |
| Maven reference database | Exact version recovery needs known coordinate/version references from real JAR/AAR releases. | Direct vulnerability search without versions was rejected because CVE mapping depends on package and version. |
| D8-converted reference bytecode | APK code is DEX, so references should be compared in a DEX-like representation. | Comparing APK DEX directly to source or Java class files would add representation differences unrelated to the library identity. |
| SQLite reference-feature database | It is local, reproducible, inspectable, and suitable for feature tables and experiments. | Remote-only lookup would be less reproducible and would not store the exact extracted evidence used for matching. |
| Weighted interpretable matcher | A simple weighted matcher is explainable in a defense and easier to debug. | A full Bayesian/multi-scale LibMD-style model was deferred because it is more complex and not fully available as a reproducible baseline. |
| Separate identity and version confidence | A library family can be clear while adjacent versions remain ambiguous. | A single confidence score would hide the difference between "this component exists" and "this exact version is proven." |
| Exact, likely, candidate, ambiguous labels | These labels communicate strength of evidence to the analyst. | Returning only one final version would make weak candidates look certain. |
| CycloneDX 1.5 JSON | CycloneDX maps well to components, PURLs, evidence, dependencies, vulnerability workflows, and tooling. | A custom JSON format was rejected because it is not interoperable. SPDX was deferred as an additional exporter, not rejected as invalid. |
| Package URL for Maven identity | PURL normalizes ecosystem, namespace, package, and version. | Free-text component names are ambiguous and weaker for vulnerability lookup. |
| OSV first for vulnerability lookup | OSV is ecosystem-aware and supports Maven package/version queries directly. | NVD/CPE-only matching was not chosen as the primary path because CPE mapping can be ambiguous for Maven libraries. |
| Confirmed vs potential vulnerability labels | CVE certainty must inherit component/version certainty. | The tool does not turn weak version evidence into confirmed CVEs. |
| Native `.so` files as hash-only components | Native version identification needs a separate ELF/symbol/reference pipeline. | The MVP does not invent Maven coordinates or versions from native filenames. |
| Dynamic/hidden/packed code as boundary evidence | If code is not visible in the APK static evidence, the tool can report risk but cannot identify hidden package versions truthfully. | The MVP does not claim to recover code that static analysis cannot see. |

Defense sentence:

> The MVP is static and reference-based because the thesis problem is APK-only recovery; when the evidence is not strong enough, the system reports uncertainty instead of pretending certainty.

### C. PFE Implementation Decisions

| PFE Decision | Why It Matters | What Was Avoided |
|---|---|---|
| Separate APK extractor, DEX analyzer, matcher, version decision, SBOM, OSV, and report stages | Each stage has its own evidence and limits, so the pipeline is easier to debug and defend. | A monolithic detector that hides where the decision came from. |
| Extract APK container evidence first | Manifest, DEX files, resources, native files, hashes, and metadata make the report traceable to the exact input. | Jumping directly to matching without preserving provenance. |
| Aggregate multidex evidence | Many Android apps split code across multiple DEX files. | Single-DEX assumptions. |
| Build references from selected Maven JAR/AAR releases | This gives auditable coordinate/version evidence. | Guessing versions from package names or web search. |
| Store score reasons and alternatives | Alternatives show whether the selected version is clearly separated from close versions. | Reporting only the top candidate without explaining margin or ambiguity. |
| Emit JSON, Markdown, HTML, and CycloneDX artifacts | Humans can inspect the result and tools can consume the SBOM. | A private internal score with no reviewable output. |
| Validate source-linked real APKs with Gradle dependency trees where possible | Source validation checks emitted rows against resolved dependencies. | Presenting source validation as complete dependency recall. |
| Keep clean, partial, blocked, no-Maven, and boundary cases separate | These categories explain different limits. | Counting blocked or partial rows as clean success. |
| Use Docker/demo preflight for defense readiness | The demo should prove the environment, toolchain, and report-only AI guardrails are working. | Relying only on a written report without executable evidence. |

Defense sentence:

> The PFE implementation was organized as an auditable pipeline, so every component in the final report can be traced back to extracted APK evidence, reference evidence, and a decision rule.

### D. Research Papers: What We Adopted And What We Did Not Adopt

| Paper/Tool Family | What We Took | What We Did Not Take | Why |
|---|---|---|---|
| LibRadar | Fast package/API ideas for candidate filtering. | Final version detector. | It is useful for speed but too weak for exact SBOM-quality version recovery. |
| LibScout | Reference profiles and exact-version motivation. | LibScout-style profiles alone. | Modern shrinking, partial inclusion, and R8 require more than package/class/method hierarchy. |
| LibSift / LibD | Segmentation and dependency/graph thinking. | Package-tree-only segmentation. | Library code boundaries can be changed by obfuscation and packaging. |
| ORLIS | Fuzzy structural matching idea. | Full ORLIS-style heavy analysis. | Useful but too complex for first MVP deployment. |
| LibPecker | Class dependency graph evidence. | Claim that CDG alone solves the problem. | CDG helps but can still be affected by inlining, shrinking, and adjacent versions. |
| LibID / LibScan | Opcode and staged matching inspiration. | Full CFG/basic-block implementation as the first core. | Fine-grained matching is useful but expensive; MVP starts with bounded features and diagnostics. |
| ATVHunter | Coarse-to-fine version detection and vulnerability motivation. | A private built-in CVE database as the main authority. | The MVP uses OSV-style external advisory lookup and keeps version confidence visible. |
| SAD | CDG/class-summary/literal tie-breaker direction. | Full clone of the research implementation. | The MVP adapts the idea in simpler, explainable form. |
| LibAttention | ML can help R8-resilient triage. | AI as authoritative version selector. | It is less explainable for exact-version SBOM authority and needs strong training evidence. |
| LibMD | Multi-scale fusion and SBOM-oriented direction. | Full Bayesian multi-scale fusion as implemented core. | It is a future ideal; the MVP uses simpler weighted fusion and report-only diagnostics. |
| OSSPolice / native-library work | Security framing and native awareness. | Full native package/version identification. | Native matching is a separate research problem. |
| TPL-Benchmark / robustness studies | Honest expectations and realistic evaluation. | Inflated old-paper F1 claims as the project standard. | Realistic benchmarks show much lower performance under diverse real conditions. |
| UniBOM / SBOM research direction | Importance of standard SBOM and vulnerability workflows. | Source-only SBOM generation. | The thesis problem is recovering evidence from compiled APKs. |

Defense sentence:

> I did not blindly choose one paper to copy; I converted the literature into requirements, then kept only the parts that fit an explainable APK-to-SBOM MVP.

### E. Non-Promoted Or Rejected Experiment Decisions

| Experiment/Alternative | Decision | Why We Did Not Promote It |
|---|---|---|
| Global opcode tri-gram weight | Kept at default `0.0`; diagnostic only. | It regressed controls without improving confirmed versions. |
| Global API-reference weight | Kept at default `0.0`. | It added complexity without measured source-validation gain. |
| Generic newer-version rule | Rejected globally. | Release recency is not bytecode evidence and caused regressions. |
| Broad POM coherence override | Diagnostic/narrow only. | Metadata can explain ambiguity but should not override APK evidence generically. |
| Broad artifact-family rules | Scoped only. | General expansion introduced unsafe assumptions. |
| Global multi-scale R8 blend | Rejected as global scorer. | It improved some targets but caused controlled, real, and clean-real regressions. |
| Phase 5 scoped R8 trigger | Report-only/experiment-only. | Promising target improvements were not enough to silently alter the frozen MVP. |
| Source-used reference additions | Guarded subsets only. | Adding correct source versions can still change candidate competition and overfit to apps. |
| Fragment `1.6.2` promotion | Kept experiment-only. | The evidence did not beat the shared `1.6.1` row strongly enough under target/control gates. |
| Priority DB broad package shortlist | Not promoted. | It improved coverage but expanded false candidate emission in I2P preflight. |
| Raw-opcode Transformer | Research-only negative result. | Macro-F1 `0.110` was below the `0.128` opcode-count baseline. |
| Hidden DEX/protector recovery | Boundary/risk report only. | Static indicators do not prove Maven package/version identity. |
| Native version identification | Future work. | Needs a separate native reference/provenance pipeline. |

Defense sentence:

> I did not promote experiments just because they helped one target. I required target improvement without control regressions.

### F. AI/ML/DL Decisions

| Decision | Why | What It Cannot Do |
|---|---|---|
| Use RandomForest as report-only assistant | It can triage structured evidence and explain feature importance. | It cannot select versions or change SBOM/CVE authority. |
| Keep structured-token Transformer as research/report-only evidence | MVP-safe source-free profile performed well enough for assistance. | It cannot become authority until it passes strict APK-only promotion gates. |
| Keep full structured-token result as research evidence | Shortcut features may inflate performance. | It cannot be used as production proof. |
| Treat raw-opcode Transformer as negative result | It underperformed the simple baseline. | It cannot justify a DL-first matcher. |
| Keep AI behind the integration gate | Auditability requires deterministic matcher authority. | AI cannot change selected version, CycloneDX component, CVE label, or source-validation metric. |

Defense sentence:

> AI was evaluated, but the evidence supports assistance, not authority.

### G. The Most Important "Why Not" Answers

**Why not use only package names?**

Because package names can be renamed, flattened, shaded, or partially removed, and they do not prove exact version.

**Why not use only hashes?**

Because real APKs often contain optimized or partial library code, so exact whole-artifact hashes are too brittle.

**Why not use dynamic analysis first?**

Because runtime coverage is incomplete and harder to reproduce. Static analysis fits the APK-only audit scenario better.

**Why not claim full R8 support?**

Because R8 can inline, shrink, merge, and remove code. Even recent tools struggle with exact versions under heavy optimization.

**Why not let AI decide versions?**

Because the SBOM and CVE result must be auditable. AI can help triage, but final authority needs deterministic evidence gates.

**Why not promote the large priority DB?**

Because more references improved coverage but also increased false candidates in preflight. Coverage alone is not safety.

**Why not count v2 as normal APK-only accuracy?**

Because v2 uses source-known coordinate/version constraints. It is an upper-bound recognition experiment, not an APK-only production score.

**Why not identify exact native library versions?**

Because `.so` files need a separate native binary provenance pipeline. The MVP reports hashes and boundary evidence honestly.

### H. One-Minute Decision Summary

If the jury asks for a global summary, say:

> The Master thesis showed that APK-to-SBOM recovery is difficult because compiled APKs lose dependency metadata and R8 can destroy many simple signals. The PFE therefore chose a static, evidence-based MVP: extract APK and DEX evidence, compare it with a Maven reference database, rank candidates with interpretable features, separate identity from version confidence, emit CycloneDX with PURLs, query OSV, and validate with source evidence where possible. We did not choose package-only matching, forced version guesses, AI authority, broad heuristic promotion, or full native recovery because they would create unsafe claims. The project contribution is not pretending to solve every APK; it is producing useful SBOM evidence with clear boundaries.

## Evaluation Terms And Numbers

| Term | Meaning | Number in your thesis |
|---|---|---:|
| Controlled fixtures | Generated APKs with known expected versions | `72` APKs, `84/84` expected versions |
| Clean source-validated real APKs | Favorable real APKs with all emitted rows confirmed | `5` APKs, `47/47` |
| Partial source-validated real APKs | Real APKs with useful but incomplete exact confirmation | `97` APKs, `880/1790` |
| Overall emitted-version confirmation | Confirmed emitted rows over checked emitted rows | `927/1837`, `50.5%` |
| Full source-denominator exact emission | Exact emitted rows over all source dependency rows | `927/12082`, `7.7%` |
| Shared DB exact-version coverage | Source rows whose exact version exists in shared DB | `1231/12082`, `10.2%` |
| Source-known v2 lane | Upper-bound constrained recognition | `6772/6772` |
| Source-gap rows | Source rows not emitted in the v2 transparency view | `5238` |
| Missing-reference candidates | Rows still plausibly missing from reference DB | `442` |
| Matcher-recall candidates | Exact versions exist but matcher/reporting did not emit them | `2281` |
| RandomForest | Report-only ML assistant | macro-F1 `0.708` |
| MVP-safe Transformer | Report-only/risk-triage candidate | macro-F1 `0.882` |
| Raw-opcode Transformer | Negative research result | `0.110`, below baseline `0.128` |

Safe sentence:

> The normal real-APK metric is emitted Maven version confirmation, not full dependency recall.

## Metrics You May Be Asked About

### Precision

Of what the tool predicted as positive, how much was correct.

Defense note:

> Precision matters for avoiding false vulnerability reports.

### Recall

Of what truly exists, how much the tool recovered.

Defense note:

> Full dependency recall is hard from APKs because not every source dependency survives as distinguishable bytecode.

### F1

Harmonic mean of precision and recall.

Defense note:

> F1 is useful for ML and literature comparisons, but my thesis also uses evidence-lane-specific metrics.

### Accuracy

Overall correct predictions over all predictions.

Defense note:

> Accuracy can be misleading in imbalanced settings, so the thesis reports clearer evidence-specific ratios.

### Macro-F1

F1 averaged across classes equally.

Defense note:

> Macro-F1 is useful for AI labels because it does not let the largest class dominate the score.

### Confirmation Rate

In your thesis, this is often:

```text
confirmed emitted Maven versions / checked emitted Maven versions
```

Defense answer:

> It measures correctness among emitted Maven rows; it is not full source dependency recall.

## State-of-the-Art Tools And Papers

| Tool/Paper | What you need to know | Safe answer |
|---|---|---|
| LibScout | Reference-profile library/version matching. | "It motivates reference profiles, but my work adds SBOM/CVE output and evidence boundaries." |
| LibRadar | Package/signature-style Android library detection. | "Useful for identity-style detection, weaker for trustworthy exact-version SBOM claims." |
| LibD | Library detection with package/structural ideas. | "It contributes detection evidence but does not solve the full SBOM trust problem." |
| ORLIS | Obfuscation-resilient library detection using similarity/fuzzy ideas. | "It motivates resilience but still needs SBOM authority boundaries." |
| LibPecker | Class-dependency and adaptive similarity. | "It shows structural relations help, but thresholds and uncertainty remain important." |
| LibID | Consistent class correspondence and version identification. | "It motivates exact-version reasoning under transformations." |
| ATVHUNTER | Version detection for vulnerability identification. | "It connects version recovery to vulnerability risk, close to my motivation." |
| LibScan/LibHunter | Optimization-aware and structural detection. | "They motivate handling R8 and optimization as first-class threats." |
| LibAttention | Learned R8-resilient library presence. | "It motivates AI/R8 assistance, but presence detection is not exact-version SBOM authority." |
| SAD | Strong version-level structural reasoning. | "It motivates multi-scale features, but results remain dataset/protocol dependent." |
| TPL-Benchmark | Realistic benchmark warning against inflated claims. | "It supports my decision to keep evidence lanes and denominators separate." |
| UniBOM | SBOM workflow direction. | "Related to SBOMs, but my work focuses on APK-side recovery." |
| LibMD | SBOM-oriented direction, unreleased. | "It supports the need for SBOM output, but my implementation is a bounded MVP." |

## Failed And Non-Promoted Experiment Concepts

### Global Opcode Tri-Gram Weight

Idea:

- add global opcode n-gram scoring.

Result:

- regressed controls without confirmed-version gain.

Defense answer:

> Opcode evidence is useful diagnostically, but the global weight was unsafe as a default.

### Global API-Reference Weight

Idea:

- add API/member-reference overlap globally.

Result:

- no measured source-validation improvement.

Defense answer:

> I did not promote it because complexity without measured benefit is not enough.

### Generic Newer-Version Rule

Idea:

- prefer newer version in close ties.

Problem:

- recency is not bytecode evidence.

Defense answer:

> A newer release may look plausible, but without APK evidence it can create wrong-version claims.

### Broad Multi-Scale R8 Blend

Idea:

- globally blend call-chain, basic-block, class-neighbor, field-operation, and context evidence.

Result:

- real improvements but also controlled and clean-real regressions.

Defense answer:

> A method that helps one target but regresses controls is not safe for production.

### Raw-Opcode Transformer

Result:

- macro-F1 `0.110`, below opcode-count baseline `0.128`.

Defense answer:

> I kept it as an honest negative result and future-work evidence.

## AI/ML/DL Concepts

### RandomForestClassifier

Classical ML model using many decision trees.

In your project:

- trained on structured project evidence rows;
- integrated as report-only suggestions;
- macro-F1 around `0.708`.

Defense answer:

> RandomForest is explainable enough for triage, but not authoritative enough for SBOM decisions.

### Transformer Encoder

Deep learning sequence model based on attention.

In your project:

- structured-token Transformer: high score, research status;
- MVP-safe Transformer: removes source/version shortcut tokens, macro-F1 around `0.882`;
- raw-opcode Transformer: negative result.

Defense answer:

> The Transformer work proves an AI workflow, but the production path keeps it report-only.

### Training Rows

Rows used to train the AI/R8 assistance layer.

Important numbers:

- `20523` training rows;
- larger project-heldout corpus: `31589` rows;
- raw opcode corpus: `1680` method sequences from `14` APKs.

Defense answer:

> The AI evidence is real, but its authority is deliberately limited.

### Feature Importance

RandomForest can show which features influence decisions.

Important examples:

- identity confidence;
- boundary/limitation flag;
- best score;
- dependency score;
- opcode score;
- package score;
- literal score.

Defense answer:

> Feature importance helps explain triage, but it does not promote the model into SBOM authority.

## Dangerous Confusions To Avoid

| Do not confuse | Correct distinction |
|---|---|
| Build-generated SBOM vs recovered SBOM | Build SBOM uses source/build metadata; recovered SBOM uses APK evidence. |
| Component identity vs exact version | Identity can be strong while exact version is uncertain. |
| CVE lookup vs CVE confirmation | OSV can return vulnerabilities, but confirmation depends on version evidence. |
| `927/1837` vs `927/12082` | First is emitted-version confirmation; second is full source-denominator exact emission. |
| `6772/6772` vs APK-only accuracy | `6772/6772` is source-version constrained upper-bound recognition. |
| Report-only vs authoritative | Report-only can explain but cannot change selected components or CVE labels. |
| Source validation vs production detection | Source validation checks outputs after the fact; production detection starts from APK evidence. |
| Reference gap vs matcher failure | Missing reference means the correct version may not exist in the DB; matcher failure means it existed but was not emitted. |
| Native file reporting vs native package recovery | Hashing `.so` files is not the same as naming native package versions. |
| AI assistance vs AI decision | AI helps triage; deterministic matcher keeps authority. |

## Short Jury Answers For Common Concept Questions

### What is the main concept of the Master thesis?

> Trustworthy recovered SBOM claims. It defines what evidence, confidence, provenance, ambiguity, validation lane, and security authority a recovered claim must expose.

### What is the main concept of the PFE thesis?

> An implemented static APK-to-SBOM pipeline that recovers bounded Maven component evidence, emits CycloneDX, maps OSV vulnerabilities, and reports uncertainty.

### Why is exact version hard?

> Adjacent versions can share almost identical bytecode, and R8 can remove or transform the small evidence that separates them.

### Why is a partial SBOM useful?

> Because confirmed partial evidence is better than a fake complete inventory. It supports triage and exposes gaps honestly.

### Why do you keep failed experiments?

> They prove that I did not promote signals just because they helped one case. A safe method must pass target and control evidence.

### Why is AI report-only?

> Because security outputs need reproducible authority. AI can explain and prioritize, but it cannot silently change selected versions or CVE labels.

### What is the biggest limitation?

> Reference coverage and matcher recall under transformed or adjacent-version APK evidence, plus native and dynamic-code boundaries.

### What is your safest closing sentence?

> The project does not claim perfect APK dependency recovery. It demonstrates an evidence-gated way to recover useful SBOM and vulnerability evidence while making uncertainty explicit.

## Final 20 Terms To Revise Before The Defense

1. SBOM
2. recovered SBOM
3. CycloneDX
4. PURL
5. APK
6. DEX
7. R8
8. Maven coordinate
9. reference database
10. identity confidence
11. version confidence
12. ambiguity
13. abstention
14. provenance
15. source validation
16. emitted-version confirmation
17. full source denominator
18. source-known upper-bound lane
19. report-only AI
20. target/control promotion gate

If you can explain those 20 clearly, you can answer most technical defense questions.
