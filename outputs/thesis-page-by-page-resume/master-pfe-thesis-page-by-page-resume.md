# Master and PFE Thesis Page-by-Page Resume

Prepared as a rehearsal guide in the same style as the presentation page-by-page speech.

Use this file to revise the two thesis PDFs page by page. It is not meant to be memorized word for word. It tells you what each page is doing and how to explain it calmly if the jury points to that page.

Sources used:

- `output/pdf/MASTER-thesis-updated.pdf` - 47 PDF pages.
- `output/pdf/PFE-thesis-updated.pdf` - 124 PDF pages.
- `outputs/graduation-defense-expanded-old-style-deck/output/presentation-speech-page-by-page.md` - style reference.

## Master Thesis - Page-by-Page Resume

### Page 1: Title Page

This page introduces the Master thesis, the institution, the diploma, and the topic: trustworthy SBOM recovery from compiled Android applications. If asked, say that the Master work is the research framing: it studies what makes a recovered SBOM claim trustworthy when the source project and build metadata are missing.

### Page 2: Dedication

This is a personal dedication page. It is not technical, but it shows the academic and personal context of the work. If the jury passes over it, do not spend time here.

### Page 3: Acknowledgements

This page thanks God, family, friends, supervisors, teachers, and the institution. Treat it as formal front matter. It does not need a technical explanation unless someone asks about the supervision context.

### Page 4: English Abstract

This page gives the core Master thesis in one page. The main point is that a syntactically valid SBOM is not automatically trustworthy when reconstructed from a compiled APK. Say that the thesis studies recovered SBOMs as evidence-backed claims, not just as component lists.

### Page 5: French Abstract

This page repeats the abstract in French for the local academic format. If asked, explain the same idea: Android compilation, optimization, obfuscation, reference gaps, and version similarity weaken evidence, so the thesis proposes a trust framework for recovered SBOM claims.

### Page 6: Arabic Abstract

This page gives the Arabic version of the abstract. The technical meaning is unchanged: the thesis argues for explicit evidence, confidence, ambiguity, and validation boundaries when generating SBOM information from a compiled Android artifact.

### Page 7: Contents, Part 1

This page begins the table of contents and shows the thesis structure. The defense point is that the Master thesis moves from introduction to background, then to state of the art, and finally to conclusion and perspectives.

### Page 8: Contents, Part 2

This page continues the table of contents and shows the background and state-of-the-art structure. It is useful because it proves the thesis is organized around SBOM concepts, Android build evidence, attribution, uncertainty, and taxonomy.

### Page 9: Contents, Part 3

This page finishes the table of contents and shows the conclusion chapter. If asked about structure, say that the conclusion answers the research questions and gives future directions for trustworthy recovered SBOMs.

### Page 10: List of Figures

This page lists the two main conceptual figures. The first figure explains how evidence is lost between source dependencies and the final APK. The second figure explains the authority chain from APK evidence to vulnerability interpretation.

### Page 11: List of Tables

This page lists the taxonomy and synthesis tables. It shows that the Master thesis is mainly a structured research synthesis: technique taxonomy, evidence taxonomy, transformation threats, evaluation practices, and study synthesis.

### Page 12: List of Acronyms

This page defines the technical acronyms used in the thesis: APK, DEX, SBOM, CVE, OSV, PURL, R8, SCA, and related terms. If asked, use it to show that the thesis connects Android reverse analysis with supply-chain security vocabulary.

### Page 13: Part I Opening

This page opens Part I, General Introduction. It is only a structural divider, so in rehearsal you should use it as a short transition into the motivation and problem statement.

### Page 14: Chapter 1 Introduction and Context

This page introduces software supply chains and the need for SBOMs when only compiled software is available. The key point is that an APK is not the same as a source dependency graph, so recovered SBOM claims come from indirect evidence.

### Page 15: Problem Statement

This page explains that a detector output can look precise while still being weak as an auditable claim. Say that the real problem is not only detecting a library, but knowing whether the evidence supports identity, exact version, and security interpretation.

### Page 16: Research Question and Supporting Questions

This page presents the central research question and its supporting questions. The key defense phrase is: the thesis asks how heterogeneous APK evidence can be combined while preserving provenance, uncertainty, and authority boundaries.

### Page 17: Scope, Objectives, and Method

This page bounds the Master thesis around component attribution, versioned reference artifacts, and implications for SBOM and vulnerability management. Say that Android is used as the demanding case because compilation, shrinking, optimization, obfuscation, multidex packaging, artifact variants, and incomplete references all change the available evidence.

### Page 18: Part II Opening

This page opens the background part. It is a transition from motivation to concepts. You can say that the next pages define the vocabulary needed before comparing tools.

### Page 19: Chapter 2 Background Introduction

This page explains that a recovered SBOM is a set of claims, not only a file. The chapter defines the concepts needed to talk about trust: evidence, attribution, version authority, provenance, and vulnerability interpretation.

### Page 20: SBOMs and Reconstructed Claims

This page distinguishes authoritative SBOMs from reconstructed SBOMs. The key point is that a valid CycloneDX or SPDX file can still contain weak claims if the component and version evidence are not strong.

### Page 21: Android Applications, Libraries, and Dependencies

This page describes APK regions and the distinction between direct and transitive dependencies. Say that no single APK region is a complete inventory; the analyzer must combine manifest, DEX, resources, metadata, and native files.

### Page 22: Provenance, Uncertainty, and Abstention

This page introduces uncertainty and abstention as normal parts of trustworthy recovery. The important message is that missing references, adjacent versions, and transformed code should produce bounded claims, not forced exact answers.

### Page 23: Figure 2.1 - Build Evidence Loss

This page contains the figure showing how source dependencies become a signed APK and how evidence changes along the way. Explain that a build-time SBOM and a recovered SBOM are related, but not identical.

### Page 24: Figure 2.2 - Authority Chain

This page shows the chain from APK evidence to component identity, exact version, vulnerability lookup, and permitted security interpretation. The key point is that CVE authority depends on the strength of the version claim.

### Page 25: Background Conclusion

This page closes the background chapter. It states that no evidence family is universally authoritative. The thesis will evaluate evidence by origin, transformation resilience, version specificity, independence, coverage, and validation status.

### Page 26: Part III Opening

This page opens the State of the Art part. Use it as the transition: now the thesis moves from concepts to existing Android library detection research.

### Page 27: Chapter 3 State of the Art and Review Protocol

This page introduces the structured mapping protocol and the Android TPL literature corpus. Say that the Master thesis does not only list papers; it extracts technique families, evidence sources, threats, and evaluation practices.

### Page 28: Technique Taxonomy

This page begins the taxonomy of component-recovery techniques. The main idea is that mature tools combine several families, such as package signatures, structural matching, opcode evidence, and learned representations.

### Page 29: Learned Representations and Technique Families

This page continues the technique table and explains learned representations. The defense point is that learned models can help with obfuscation-resilient presence detection, but they do not automatically provide exact-version or vulnerability authority.

### Page 30: Evidence-Source Taxonomy

This page explains evidence families such as descriptors, API surfaces, code structure, literals, and metadata. Say that different evidence types support different claim strengths: some help identity, while fewer reliably separate exact versions.

### Page 31: Transformation Threats

This page introduces transformation threats caused by Android compilation, packaging, and R8. The key message is that obfuscation, shrinking, inlining, package flattening, and partial inclusion weaken evidence in different ways.

### Page 32: Threat Table

This page continues the transformation-threat taxonomy. It shows how each threat affects evidence and what more resilient signals may help. The safe conclusion is that no single signal solves all Android transformations.

### Page 33: Representative Tool Evidence

This page discusses tools such as LibPecker, LibID, and related assessment studies. The point is that structural and reference-based tools are valuable, but their outputs still need uncertainty and validation boundaries before becoming SBOM claims.

### Page 34: Evaluation-Practice Taxonomy

This page explains why evaluation methods matter. Dataset choice, obfuscation setting, module handling, AAR support, and version-identification capability can change results. A single score without denominators is not enough.

### Page 35: Evaluation Boundaries

This page continues the evaluation table and explains the boundary of each validation style. Say that source-known validation is strong for audited cases, but it must not be confused with general APK-only accuracy.

### Page 36: Tier A Study Synthesis, Part 1

This page summarizes representative studies and their trust implications. The key point is that tools provide useful evidence families, but the thesis judges them by what kind of SBOM claim they can safely support.

### Page 37: Tier A Study Synthesis, Part 2

This page continues the study synthesis, including optimization-aware and learning-based work. The important defense line is that obfuscation-resilient identity hints are not the same as exact-version SBOM recovery.

### Page 38: Research Gaps

This page lists major gaps: exact-version authority, reference coverage, transformation coverage, validation transparency, and SBOM-oriented output. Say that these gaps motivate the evidence-trust framework.

### Page 39: State-of-the-Art Conclusion

This page concludes that the missing problem is not only SBOM formatting. A valid SBOM can still be untrustworthy if it hides ambiguity or turns weak identity evidence into exact-version and CVE authority.

### Page 40: Part IV Opening

This page opens the final conclusion part. Use it as the transition from literature synthesis to the thesis answer.

### Page 41: General Conclusion

This page states the main Master conclusion: APK-to-SBOM recovery is a claim-authority problem, not only a detection problem. The thesis favors evidence trails, confidence boundaries, and explicit abstention.

### Page 42: Answers to Research Questions

This page begins the research-question answer table. The main point is that each supporting question is answered with a boundary: available evidence, combination methods, and claim strength all depend on transformation and validation context.

### Page 43: Continued Research-Question Answers

This page continues the answer table, especially what an auditable security-relevant claim must include. Say that a proper claim needs subject APK, component, artifact family, version or version set, supporting evidence, opposing evidence, provenance, and permitted interpretation.

### Page 44: Future Works

This page gives future research directions: native and dynamic attribution, human factors, explainability, calibrated fusion, and better evaluation protocols. The key message is that future authority must be earned by evidence, not assumed.

### Page 45: Bibliography, Part 1

This page begins the references. In defense, you normally do not explain bibliography pages unless asked. If asked, say that the thesis cites SBOM guidance, supply-chain security standards, Android documentation, and Android TPL research.

### Page 46: Bibliography, Part 2

This page continues the bibliography with Android, OWASP, review methodology, and library-detection references. The useful defense point is that the background and method are grounded in both standards and research papers.

### Page 47: Bibliography, Part 3

This page finishes the bibliography with key Android third-party-library detection works. If asked about novelty, say that the Master thesis builds on these works but shifts the question from "was a library detected?" to "what claim can be trusted?"

## PFE Thesis - Page-by-Page Resume

### Page 1: Title Page

This page introduces the Engineering thesis: evidence-based SBOM recovery from compiled Android APKs. The important distinction is that this is the implementation thesis. It builds and evaluates the tool that follows the trust principles defined by the Master work.

### Page 2: Dedication

This is the personal dedication page. It is formal front matter, not part of the technical argument. Move quickly if rehearsing.

### Page 3: Acknowledgements

This page thanks God, family, supervisors, teachers, classmates, and the institution. It frames the work personally and academically, but it does not need technical explanation.

### Page 4: English Abstract

This page gives the full PFE story in one page. The thesis implements a static APK-to-SBOM pipeline, separates identity from exact-version confidence, emits CycloneDX, queries OSV, validates with source trees, and keeps AI/R8 assistance report-only.

### Page 5: French Abstract

This page repeats the same engineering contribution in French. The key idea is that binary-only Android analysis cannot rely on source code, build manifests, or package-manager metadata, so the system uses APK evidence, Maven references, confidence labels, and guarded vulnerability interpretation.

### Page 6: Arabic Abstract

This page gives the Arabic abstract. If asked, explain that the message is the same: the pipeline recovers bounded component evidence from compiled APKs and prefers explicit uncertainty over unsupported exact claims.

### Page 7: Contents, Part 1

This page begins the table of contents. It shows the thesis starts with the general introduction and then moves into background. Use it to show the thesis is structured as a complete engineering report.

### Page 8: Contents, Part 2

This page continues the contents through Chapter 1 and Chapter 2. It shows the early chapters define objectives, methodology, APK internals, Software Bills of Materials, vulnerability concepts, and evidence recovery.

### Page 9: Contents, Part 3

This page continues the contents into AI and state of the art. The defense point is that AI is treated as background and assistance, not as the main authority of the SBOM system.

### Page 10: Contents, Part 4

This page shows the state-of-the-art comparison and its limitations. It prepares the reader for why the MVP needs both technical detection and evidence-governance rules.

### Page 11: Contents, Part 5

This page shows the implementation and evaluation chapter contents. It proves that the PFE thesis is not only conceptual: it includes modules, commands, datasets, metrics, demo evidence, AI/R8 evaluation, failed experiments, and discussion.

### Page 12: Contents, Part 6

This page finishes the contents with the conclusion and appendix. The appendix matters because it provides reproducibility commands and artifact traceability.

### Page 13: List of Figures, Part 1

This page lists the major figures in the introduction, background, architecture, and implementation. It shows that the thesis uses diagrams to explain supply-chain context, evidence loss, APK structure, and system flow.

### Page 14: List of Figures, Part 2

This page lists the dashboard and demo screenshots. These figures are important in defense because they prove the system produces real reports, not only metrics in a table.

### Page 15: List of Tables, Part 1

This page lists tables covering SBOM standards, vulnerability concepts, evidence sources, state-of-the-art comparison, evidence families, modules, and matcher weights. The key point is that the thesis uses tables to connect concepts to implementation.

### Page 16: List of Tables, Part 2

This page continues the table list with evaluation, failed experiments, research-question answers, future work, and reproducibility artifacts. Say that the thesis deliberately makes evidence boundaries and traceability visible.

### Page 17: List of Acronyms

This page defines the project vocabulary: APK, DEX, AAR, SBOM, CVE, OSV, PURL, R8, AI, ML, DL, and related terms. It is useful if the jury asks for a quick technical definition.

### Page 18: Part I Opening

This page opens Part I, General Introduction. It is a structural divider, so use it only as a quick transition into the thesis motivation.

### Page 19: Chapter 1 Context

This page explains the software-supply-chain context. Modern applications depend on many libraries, and auditors may only see the final APK. The thesis asks how to recover useful component and vulnerability evidence from that binary artifact.

### Page 20: Figure 1.1 and Supply-Chain View

This page shows the path from application source and dependencies to the delivered APK and the auditor. Say that the analyzer works on the delivered APK side, where the original dependency graph is no longer directly visible.

### Page 21: R8 and Problem Details

This page explains how Android build transformations can rename, shrink, inline, merge, and remove evidence. The important message is that exact-version recovery is harder than simple library presence detection.

### Page 22: Figure 1.2 and Recovery Boundary

This page contrasts source-based SBOM generation with binary-only recovery. The defense point is that the recovered SBOM must expose what is observed and bounded, because it is not the same as a build-generated dependency inventory.

### Page 23: Research Problem and End-to-End Gap

This page explains that vulnerabilities inherit the confidence of the component and version evidence. It also introduces the engineering gap: existing library detectors rarely produce a full audited SBOM and CVE workflow.

### Page 24: Objectives

This page gives the general and specific objectives. The key sentence is that the project designs, implements, and evaluates a static evidence-based system that recovers a bounded CycloneDX SBOM and supports confidence-aware vulnerability analysis.

### Page 25: Methodology Overview

This page explains the implementation method: reference construction, APK analysis, matching, SBOM generation, CVE mapping, validation, and reporting. Say that each stage is separated so evidence and limits remain auditable.

### Page 26: Thesis Organization

This page summarizes the remaining chapters. It tells the reader where to find background, AI, state of the art, solution design, implementation, evaluation, conclusion, and reproducibility evidence.

### Page 27: Part II Opening

This page opens the technical background part. Use it as the transition from project motivation to the technical foundation.

### Page 28: Chapter 2 Introduction

This page explains that APK-to-SBOM recovery connects supply-chain security, Android packaging, bytecode analysis, vulnerability data, and evidence fusion. It sets up the concepts used by the MVP.

### Page 29: Software Supply Chains

This page explains direct and transitive dependencies and why a source project gives a richer supply-chain view than a released binary. The key point is that the APK only preserves part of the dependency evidence.

### Page 30: SBOM Definition and Provenance

This page defines SBOMs and explains that binary-only recovery is narrower than full build provenance. Say that the MVP still adds value because it makes recovered claims auditable.

### Page 31: SBOM Standards Table

This page compares SBOM-standard dimensions, especially SPDX and CycloneDX. The PFE uses CycloneDX because it is practical for component inventory, PURLs, vulnerabilities, and report integration.

### Page 32: SBOM Use Cases and Limits

This page explains why SBOMs matter: vulnerability triage, license review, incident response, policy checking, and asset correlation. The limitation is that SBOM quality depends on correct component and version claims.

### Page 33: Vulnerability Concepts

This page distinguishes CVE, CVSS, EPSS, KEV, and vulnerability concepts. The key defense point is that vulnerability data cannot fix an incorrect package identity or version decision.

### Page 34: JAR, AAR, and Maven Dependencies

This page explains Android and Java library packaging. Say that JAR, AAR, and Maven coordinates give the project a concrete way to identify library artifacts as `group:artifact:version`.

### Page 35: APK Structure

This page describes AndroidManifest.xml, classes.dex files, resources, assets, native libraries, signatures, and metadata. The pipeline extracts evidence from these regions, but DEX bytecode is the main source for Maven component matching.

### Page 36: Nonstandard and Dynamically Loaded Code

This page explains hidden DEX, custom class loaders, downloaded code, encrypted payloads, and native code. The MVP reports these as risk or boundary evidence instead of inventing unsupported package-version claims.

### Page 37: R8 Transformations

This page lists R8 transformations such as renaming, shrinking, optimization, inlining, and class merging. The defense message is simple: R8 can destroy the evidence needed to separate exact versions.

### Page 38: Static Analysis and Recoverable DEX Evidence

This page explains why the MVP is static: reproducible, offline, and connected to the shipped APK. The trade-off is that runtime-only or protected code may remain invisible.

### Page 39: Identity Versus Version

This page makes one of the central distinctions. A tool may strongly identify `androidx.fragment:fragment` but still not safely distinguish 1.6.1 from 1.6.2. This is why identity confidence and version confidence are separate.

### Page 40: Evidence Table Example

This page shows how different observations support different outputs. Strong distinctive evidence can justify exact version; weak or tied evidence may justify identity only, a candidate set, or abstention.

### Page 41: Static Evidence Sources

This page lists APK evidence sources and their limits: archive paths, manifest data, DEX packages/classes/methods/opcodes/literals, resources, native files, and metadata. Say that the matcher fuses evidence but respects failure modes.

### Page 42: Fusion, Conflict, and Abstention

This page explains that a narrow score margin is ambiguity, not permission to prefer a newer version. The analyzer may emit exact claims, bounded claims, warnings, or no package/version claim depending on evidence strength.

### Page 43: Chapter 3 AI Introduction

This page opens the AI background chapter. The thesis positions AI as assistance for noisy and complex evidence, not as automatic SBOM authority.

### Page 44: Classification Basics

This page explains machine-learning classification, labels, features, training, and evaluation. It prepares the reader to understand why the later AI layer is treated as a supervised classification problem.

### Page 45: Feature Representations

This page explains structured features and token-like representations. In this project, structured evidence rows can feed AI assistance, while raw opcode sequences are harder and less mature.

### Page 46: Classical Machine Learning

This page introduces decision trees and Random Forests. The key point is that classical ML can be interpretable and useful for triage, but it still needs guardrails before it affects security outputs.

### Page 47: Transformer Encoders

This page introduces Transformer encoders and attention. Say that the thesis explores Transformers as a research prototype, but it does not let a high score override deterministic SBOM authority.

### Page 48: Evaluation Metrics

This page defines precision, recall, F1, accuracy, and confusion-matrix concepts. These definitions matter because the thesis reports different metrics for controlled fixtures, real APK confirmation, and AI experiments.

### Page 49: AI Chapter Conclusion

This page closes the AI background chapter. It states that AI can support APK-to-SBOM analysis but must remain bounded by validation and authority rules.

### Page 50: Part III Opening

This page opens Part III, State of the Art. It is a structural divider, so use it only as a short transition into the related-work review.

### Page 51: Chapter 4 Review Scope

This page defines the state-of-the-art scope: Android third-party library identification, exact-version detection, obfuscation-resilient similarity, SCA, and vulnerability mapping. The PFE uses this review to justify the MVP design.

### Page 52: Evolution of Tool Families

This page explains the evolution from package/reference signatures to structural similarity and then learned representations. Say that later approaches often keep fast signatures but add deeper evidence for difficult cases.

### Page 53: Version-Level and Structural Methods

This page discusses tools such as LibID and methods that use obfuscation-aware or structural matching. The key point is that version-level claims are possible but fragile and protocol-dependent.

### Page 54: Learned and R8-Resilient Methods

This page explains learned approaches and their value under R8-style transformed datasets. The important boundary is that presence detection and exact-version SBOM recovery are not the same task.

### Page 55: Method-by-Method Synthesis

This page begins the synthesis of representative approaches. The defense point is that the PFE did not copy one detector; it selected useful ideas and adapted them under evidence gates.

### Page 56: SAD and Strong Version Reasoning

This page discusses SAD and other strong version-level methods. Say that these works motivate multi-scale and structural evidence, but their reported results still depend on dataset and evaluation protocol.

### Page 57: Capability Comparison Table

This page compares tools by goal, evidence, version level, optimization focus, and output. The key conclusion is that most tools are detectors, not complete evidence-governed SBOM and CVE workflows.

### Page 58: Trade-Offs and Limitations

This page explains the trade-off between fast approaches, structural robustness, cost, and reference dependence. The PFE responds with a bounded pipeline and explicit confidence labels rather than one universal score.

### Page 59: Limitations and Impact on MVP

This page explains that existing approaches often do not treat unsupported native code, hidden code, or no-signal cases as first-class outcomes. The MVP therefore includes boundary reporting and abstention.

### Page 60: Research Gap and Positioning

This page lists the final gaps: exact-version fragility, mixed denominators, limited SBOM output, reference gaps, and weak authority boundaries. This is the direct bridge to the proposed solution.

### Page 61: Part IV Opening

This page opens the Contribution part. Use it as the transition from research gap to system design.

### Page 62: Chapter 5 Proposed Solution

This page introduces the static evidence-gated pipeline. The system transforms a compiled APK into a CycloneDX SBOM and confidence-aware vulnerability report while separating extraction, matching, version decisions, and reporting.

### Page 63: General Architecture Figure

This page shows the architecture from APK evidence and Maven references to matching, SBOM output, OSV lookup, and reports. The key point is that authoritative outputs and report-only diagnostics are separate.

### Page 64: Reference Databases and Evidence Model

This page explains that shared calibrated databases are separate from evaluation-only and experiment-only databases. Say that this separation prevents experimental evidence from silently changing production claims.

### Page 65: Use Cases and Behavioral Diagrams

This page introduces behavioral diagrams for analyst actions, runtime behavior, reference construction, deployment boundaries, and persistent data. It refines the architecture into operational views.

### Page 66: Runtime Flow Diagram

This page shows the pipeline flow: inspect APK, parse DEX, load reference profiles, rank candidates, select versions, and write outputs. Use it to explain the end-to-end path in one picture.

### Page 67: Sequence Diagram

This page shows how the CLI, extractor, analyzer, matcher, reference DB, and report writers interact. The defense point is that the implementation has clear module responsibilities and observable outputs.

### Page 68: Deployment and Authority Boundary

This page explains filesystem, network, Maven acquisition, OSV lookup, and local database boundaries. The most important sentence is that report-only AI and R8 diagnostics may annotate reports but cannot feed the matcher, CycloneDX component set, or vulnerability labels.

### Page 69: Data Model

This page shows the SQLite schema: components, artifact inventory, DEX files, identity features, and related feature tables. Say that the reference DB stores versioned evidence so APK features can be compared against known Maven releases.

### Page 70: Chapter 6 Introduction

This page opens the implementation, evaluation, and discussion chapter. It states that the architecture was implemented as a Python CLI that extracts evidence, matches Maven profiles, emits CycloneDX, queries OSV, and writes reports.

### Page 71: Development Environment

This page lists the development and execution environment. Use it to show the work is reproducible: Python, Androguard, NetworkX, SQLite, Android build tools with D8 conversion, Docker/Compose, CycloneDX, OSV, and Pytest are part of the implementation context.

### Page 72: Implementation Modules

This page maps modules to source files and observable outputs. It is strong defense evidence because it shows the MVP is real code with CLI, extractor, DEX analyzer, reference builder, matcher, SBOM writer, vulnerability scanner, validator, and reporter.

### Page 73: Extraction and DEX Analysis

This page explains APK validation, hashing, standard and unusual DEX discovery, package/class/method/opcode/literal/API extraction, and native-file reporting. Say that this is where raw APK evidence becomes structured analysis data.

### Page 74: Matcher Scoring

This page explains score families and weights. The key point is that the score is a ranking signal, not a calibrated probability, and disabled or missing feature families must not create fake confidence.

### Page 75: SBOM, Vulnerability, Reports, and Commands

This page explains report attachments and the command-line workflow. The guardrail is central: optional AI, R8, version-band, and hybrid sections can explain evidence but cannot modify selected versions or SBOM/CVE labels.

### Page 76: Reference-Database Workflow

This page gives the reproducible reference database build commands. It shows how Maven catalogs are expanded, artifacts are downloaded, converted to DEX, and stored as comparable reference profiles.

### Page 77: Evaluation Layers

This page defines the evaluation layers and permitted claims. Say that controlled fixtures, clean real APKs, partial real APKs, upper-bound lanes, report-only diagnostics, and limitation cases are not mixed into one score.

### Page 78: Regression and Promotion Protocol

This page explains the fail-fast target/control protocol. A change must help the intended target and pass controls before it can affect the default MVP. This is why failed experiments are part of the contribution.

### Page 79: Source-Validated Real-APK Results

This page gives the main emitted-version results: clean and partial APKs are separated before aggregation. The number to remember is `927/1837`, or `50.5%`, as emitted Maven version confirmation, not full dependency recall.

### Page 80: Full Source Denominator and V2 Lane

This page explains source-denominator coverage and reference DB limits. It is where you distinguish `50.5%` emitted confirmation from `7.7%` full source-denominator exact emission and the separate v2 source-known upper bound.

### Page 81: Vulnerability Demonstration

This page explains vulnerability claim levels. A controlled exact component can support a confirmed demo; source-confirmed real emitted versions can support source-confirmed discussion; uncertain or report-only rows must not become confirmed CVEs.

### Page 82: Vulnerability Continuation

This short page closes the vulnerability policy point. The safe line is: a vulnerability is only as strong as the component and version evidence behind it.

### Page 83: Clean F-Droid Dashboard Figure

This page is a screenshot figure for the clean F-Droid report. It shows summary evidence: 23 Maven components, APK metadata, extraction evidence, and zero vulnerability findings. Use it as visual proof of the normal clean report.

### Page 84: Clean F-Droid Components, Part 1

This page shows the first detected-components panel. The important point is that each component exposes selected version, evidence families, identity confidence, version confidence, match type, vulnerability count, and evidence links.

### Page 85: Clean F-Droid Components, Part 2

This page continues the component list. Say that the dashboard preserves candidate and uncertainty labels instead of pretending every row has the same strength.

### Page 86: F-Droid Version Decisions, Part 1

This page shows selected versions, confidence, scores, score gaps, and alternatives. It is important because version decisions drive vulnerability lookup.

### Page 87: F-Droid Version Decisions, Part 2

This page continues version decisions and shows low-scoring or near-tied rows. The defense point is that uncertainty remains visible in the report.

### Page 88: F-Droid Vulnerabilities and Artifacts

This page closes the clean report figure sequence. It shows zero returned vulnerabilities, native files as hash-backed artifacts, persisted outputs, and explicit limitations.

### Page 89: Vulnerable Jackson Dashboard Start

This page begins the controlled vulnerable Jackson report. It shows one detected Maven component, exact report processing, and three confirmed vulnerability findings.

### Page 90: Jackson Component and Version Decision

This page shows the Jackson component and version evidence. Jackson Databind 2.9.10.8 has exact/high identity and version confidence, while unrelated low-scoring alternatives remain uncertain and are not emitted as components.

### Page 91: Jackson CVE Findings and Artifacts

This page shows the three confirmed high-severity findings: CVE-2020-36518, CVE-2022-42003, and CVE-2022-42004. It proves the end-to-end path from component and version evidence to OSV lookup and persisted artifacts.

### Page 92: Vulnerability Validation and Source Evidence

This page explains why vulnerability scanning cannot be separated from attribution. OSV may correctly report advisories for a selected version, but if the selected version disagrees with source evidence, the vulnerability claim must be downgraded.

### Page 93: AI/R8 Assistance Dataset

This page introduces the report-only AI/R8 dataset with 20,523 training-eligible rows. The key point is that the model learns report actions and triage labels while the deterministic matcher remains the only SBOM authority.

### Page 94: Random Forest Assistant

This page describes the RandomForest assistant: model settings, features, and training setup. Say that it is integrated as report-only assistance because it helps triage but cannot change selected versions or CVE labels.

### Page 95: Random Forest Metrics and Weak Classes

This page discusses detailed ML performance, including weaker classes. Use it honestly: the model is useful, but performance is not uniform enough to become production authority.

### Page 96: Transformer and Raw Opcode Results

This page discusses Transformer-related results and the raw-opcode negative result. The defense point is that a structured-token Transformer can be promising, but the raw-opcode Transformer underperforms a simple baseline and is not promotable.

### Page 97: Aegis R8 Diagnostics Figure

This page shows R8 and obfuscation diagnostics in the Aegis hybrid report. The key message is that obfuscation risk becomes visible to the analyst while remaining report-only.

### Page 98: Hybrid AI Assistance Summary Figure

This page shows the hybrid AI assistance summary for Aegis. It explicitly states that the weighted matcher is the SBOM authority, and that router rows and structural-gate rows remain report-only.

### Page 99: Random Forest and Deep Learning Report Figures

This page shows AI report panels: trained model status, suggestion rows, recommendations, confidence values, and DL status. Say that these panels help analysis but do not alter the authoritative output.

### Page 100: Failed and Non-Promoted Experiments Opening

This page introduces negative experiments as a contribution. The key sentence is that promising changes were rejected when they failed target/control evidence.

### Page 101: Failed Experiment Table

This page lists representative failed or non-promoted experiments: opcode tri-grams, API-reference weights, recency rules, multi-scale R8 blend, source-used references, and more. Say that this protects the MVP from overfitting.

### Page 102: Comparison with Existing Work

This page explains the result of failed experiments and begins comparing with existing tools. The MVP is not presented as a universal best detector; it is an evidence-governed component-recovery and vulnerability-reporting workflow.

### Page 103: Discussion and Research Question Answers

This page starts answering the PFE research questions. The safe answer for exact versions is: yes under bounded conditions, with strong controlled and clean results, but partial real-world recovery remains limited.

### Page 104: Remaining Failure Causes

This page lists reasons for misses and mismatches: metadata-only dependencies, build removal, source/API transformations, false-positive package overlap, native code, hidden code, and reference/matcher gaps.

### Page 105: Threats to Validity

This page explains external validity. The source-tree dataset is diverse but not random, and open-source F-Droid cases are easier to audit than closed-world commercial apps. This is honest scope control.

### Page 106: Part V Opening

This page opens the General Conclusion part. Use it as the transition from detailed evaluation to the final thesis message.

### Page 107: General Conclusion

This page states the PFE conclusion: useful SBOM evidence can be recovered from compiled APKs, but exact completeness is not guaranteed. The contribution is evidence-gated recovery, not perfect reverse engineering.

### Page 108: Evaluation Synthesis

This page synthesizes the main results and says the contribution is broader than a similarity score. It combines binary evidence extraction, reference construction, attribution, serialization, vulnerability interpretation, source validation, and experiment governance.

### Page 109: Practical Significance

This page explains what the MVP is useful for: evidence recovery and audit support, not replacing a trusted build-generated SBOM. It can recover strong claims, reveal ambiguity, produce interoperable output, and support vulnerability triage.

### Page 110: Research Question Answer Table

This page summarizes answers and boundaries for the research questions. Use it in defense if asked to connect objectives to evidence: each answer includes both what was achieved and what remains bounded.

### Page 111: Future Work Table

This page lists prioritized future work: safer large-catalog retrieval, stronger matcher recall, native/dynamic analysis, better baselines, calibrated confidence, and larger benchmarks. Each future direction requires promotion evidence.

### Page 112: Calibration and Abstention Future Work

This page expands on calibrated evidence and version abstention. Say that current scores rank candidates, but future work should calibrate confidence and abstention thresholds with held-out source-validated cases.

### Page 113: Broader Dataset Future Work

This page calls for broader validation on legacy builds, protected apps, games, cross-platform frameworks, native-heavy apps, and multiple releases. The point is that the next research step is stronger generalization evidence.

### Page 114: Appendix A Opening

This page opens the reproducibility and evidence index. It explains that the appendix records environment, commands, evidence classes, and artifacts needed to reproduce or audit the thesis results.

### Page 115: Reproduction Environment

This page lists the environment: Python version, libraries, Android tools, Docker, SQLite, and supporting utilities. It proves the thesis is backed by a reproducible engineering setup.

### Page 116: Core APK-to-SBOM Commands

This page gives stage-level commands for inspection, DEX analysis, matching, and report generation. Say that each command maps to a pipeline stage and can be rerun for auditing.

### Page 117: Reference Database Construction

This page gives commands for building reference artifacts and generating the SQLite reference database. It shows that the reference evidence is generated systematically, not manually inserted.

### Page 118: Source Validation Command

This page explains source validation with dependency trees. The key boundary is that source validation is an evaluation operation and must not be confused with APK-only production detection.

### Page 119: Dataset and Evidence Inventory

This page defines evidence classes and their permitted interpretations: controlled fixtures, clean real APKs, partial real APKs, source-known upper-bound lanes, report-only diagnostics, and limitation cases.

### Page 120: Claim-to-Artifact Traceability

This page introduces the traceability table. It maps headline claims to primary artifacts so a reviewer can audit where each number came from.

### Page 121: Traceability Table Continuation

This page continues the claim-to-artifact map, including AI authority decisions and generated JSON/report outputs. The defense point is that numbers are not isolated claims; they point to reproducible artifacts.

### Page 122: Bibliography, Part 1

This page begins the bibliography with supply-chain and Software Bills of Materials references. In defense, use it only if asked about standards or foundational sources.

### Page 123: Bibliography, Part 2

This page continues references for PURL, CVE, CWE, NVD, OSV, Android, and supporting technical documentation. It grounds the vulnerability and Android background.

### Page 124: Bibliography, Part 3

This page finishes with AI and Android third-party-library detection references. If asked, say the PFE builds on this research but turns it into a guarded end-to-end component-recovery and CVE workflow.

## Fast Rehearsal Advice

For the Master thesis, keep repeating one idea: a recovered SBOM is only trustworthy when each claim exposes evidence, uncertainty, provenance, and authority boundaries.

For the PFE thesis, keep repeating one idea: the MVP is an implemented evidence-gated APK-to-CycloneDX workflow that recovers useful partial SBOM evidence and refuses to overstate unsupported exact versions.

If the jury asks about weak numbers, do not hide them. Say: the system reports `50.5%` emitted-version confirmation and `7.7%` full source-denominator exact emission because it is honest about the difference between correctness of emitted rows and full dependency recall.

If the jury asks about the `6772/6772` result, say: this is a source-version constrained upper-bound lane, useful for measuring recognition and gap categories, but it is not general APK-only accuracy.

If the jury asks about AI, say: AI is useful for triage and explanation, but it is report-only; it cannot change selected versions, CycloneDX components, vulnerability labels, or source-validation metrics.
