# Presentation Speech Page By Page

## Page 1: Title

Good morning respected jury members, supervisors, and guests. My name is Fendi Mohamed, and I am presenting my graduation project on evidence-based SBOM recovery from compiled Android APKs. The goal is to recover useful software component evidence from APK files, generate CycloneDX SBOM output, and connect that evidence to CVE analysis while being honest about uncertainty.

## Page 2: Introduction

I begin with the practical audit situation: sometimes we receive only the compiled APK, not the source project. The defense story is therefore about recovering useful evidence from that artifact while keeping uncertainty visible.

## Page 3: The Problem

The problem begins when dependency metadata disappears during compilation and packaging. A source project can declare Gradle dependencies, but the released APK contains transformed DEX bytecode, resources, native files, and signatures.

## Page 4: The project answers one practical question

The practical question is whether a compiled APK can become a useful SBOM without pretending weak evidence is certain. Useful means component identities, selected versions when justified, confidence labels, ambiguity, CycloneDX output, and CVE interpretation.

## Page 5: Two theses support one defense story

The Master thesis provides the research framing, state of the art, and trust model. The PFE thesis implements the APK analysis pipeline, reference database, matcher, SBOM generator, OSV lookup, reports, evaluation, and demo evidence.

## Page 6: Background

Before the system design, I define the technical objects because each one gives a different level of evidence.

An APK is the compiled Android application package. It is ZIP-compatible and can contain the AndroidManifest.xml file, resources, assets, signatures, one or more DEX files, and native libraries under lib/<abi>/*.so. In this project, the APK is the input artifact. We analyze it statically, without installing or executing it.

DEX means Dalvik Executable. It is the Android bytecode format produced after Java or Kotlin code is compiled and converted by D8 or transformed by R8. DEX is the main evidence surface because it contains classes, methods, fields, instructions, strings, API references, and dependency-like structural relations.

APK extraction is the first technical step. It opens the APK, verifies the archive, hashes the file, finds DEX files, records native files, decodes manifest metadata, and records risk indicators such as multidex, hidden DEX paths, native-heavy packages, or protected payload indicators. Extraction preserves provenance before any library decision is made.

APK analysis, especially DEX analysis, turns the extracted bytecode into comparable features: package names, classes, methods, opcode counts, opcode tri-grams, literals, class dependencies, API references, and diagnostic structural features. This is not yet an SBOM. It is evidence used by the matcher.

An SBOM, or Software Bill of Materials, is a structured inventory of software components. Here it is a recovered APK-derived SBOM, not the original Gradle dependency graph. That distinction matters because compiled APKs may lose, merge, shrink, or transform dependency boundaries.

CycloneDX is the SBOM standard used by the MVP. I chose it because it supports components, versions, hashes, Package URLs, properties, evidence, and vulnerability-tool interoperability. PURL, or Package URL, is the normalized package identifier, for example pkg:maven/group/artifact@version. It connects a Maven component to vulnerability services.

A CVE is a public vulnerability identifier. The tool queries OSV using package and version evidence. A CVE result is only trustworthy if the component identity and exact version are trustworthy. A weak version guess cannot become a confirmed vulnerability.

R8 is Android's shrinker, optimizer, and obfuscator. It can rename classes, remove unused code, inline methods, merge structures, and optimize bytecode. This is why exact version recovery is hard. R8 may leave enough evidence for library identity while destroying evidence needed for exact version selection.

Finally, confidence is the decision layer. The system separates identity confidence, version confidence, and vulnerability authority. Confidence is not decoration. It decides whether a result is exact, likely, candidate, uncertain, report-only, or withheld.

## Page 7: An SBOM is useful only when its claims are trustworthy

An SBOM format such as CycloneDX makes the result machine-readable, but the format alone does not prove the component is present. The trust comes from the evidence behind the component identity and exact version.

## Page 8: Android compilation changes the evidence before analysis

Android compilation transforms Java and Kotlin dependencies into DEX. D8 performs bytecode conversion, and R8 can rename, shrink, inline, optimize, and merge code, so the analyzer sees the shipped artifact rather than the original dependency tree.

## Page 9: The trust boundary has three decisions

The system separates component identity, exact version, and vulnerability authority. This prevents a plausible library match from automatically becoming a confirmed exact-version CVE claim.

## Page 10: State of the Art

The related-work section explains where my method comes from and why the contribution is not simply another detector. The literature gives useful signals, but also shows why exact version recovery is fragile.

## Page 11: Research Positioning

I position the project between Android third-party library detection and practical SBOM/CVE workflows. Prior work often detects libraries, while this project focuses on auditable SBOM output and confidence-aware vulnerability interpretation.

## Page 12: The literature evolves through three evidence families

The first family uses names, hashes, package signatures, and profiles. The second uses structure, graphs, opcodes, and fuzzy matching. The third uses learned representations for R8 and obfuscation. Each generation improves one weakness but does not remove the need for evidence gates.

## Page 13: The main gap is trustworthy version authority

The gap is not only finding a library family. The hard part is deciding whether the exact version is strong enough for SBOM and CVE authority, especially after R8 and partial library inclusion.

## Page 14: Related works solve parts of the problem, not the whole workflow

Here I compare the main related works by what they are best at and where they stop. LibRadar is fast, LibScout motivates version profiles, structural tools improve matching, LibAttention helps R8 presence detection, and SBOM-oriented tools guide the output direction. None of them alone gives the complete APK-to-CycloneDX-to-CVE workflow implemented here.

## Page 15: The limits of prior tools become MVP requirements

This slide turns limitations into design requirements. If names are fragile, names become weak evidence. If adjacent versions are hard, identity and version confidence must be separated. If many tools lack SBOM output, the MVP must emit CycloneDX and PURLs.

## Page 16: Realistic benchmarks reset the comparison baseline

I do not compare only against optimistic paper numbers. TPL-Benchmark and obfuscation studies show that realistic datasets and advanced R8 reduce performance strongly, especially for exact version recovery. That is why my evaluation separates denominators instead of giving one inflated score.

## Page 17: The Master thesis turns state of the art into requirements

The Master thesis converts the literature into engineering requirements: multi-signal matching, explicit confidence, CycloneDX output, PURL identity, and confirmed-versus-potential CVE labels.

## Page 18: Contribution

Now I move from related work to my contribution. The contribution is a working evidence-gated APK-to-SBOM pipeline, not a claim that every APK can be perfectly reconstructed.

## Page 19: Project Objective

The objective is to start from a compiled APK and produce a security artifact that a human can inspect and a tool can consume. The artifact includes detected Maven components, versions when supported, CycloneDX output, OSV findings, and evidence reports.

## Page 20: Architecture Decisions

The architecture decisions follow from the research: static analysis first, Maven reference profiles, DEX-to-DEX comparison, CycloneDX output, OSV lookup, and confidence instead of forced precision.

## Page 21: System Architecture

The architecture has two main lanes that meet at the matcher: the APK evidence lane and the Maven reference lane. The full cycle starts from the target APK and ends with a CycloneDX SBOM, vulnerability output, and human-readable reports.

In the APK lane, the first step is inspection and extraction. The tool reads the APK as the shipped artifact, records the hash and manifest metadata, finds classes.dex and classes2.dex if the app is multidex, records native .so files by ABI and hash, and flags extraction risks. This was a deliberate decision because the report must be traceable to the exact input file.

The second step is DEX analysis. The analyzer parses every discovered DEX and extracts comparable bytecode evidence: packages, classes, methods, fields, opcodes, opcode tri-grams, literals, API references, and class dependency structure. I chose static DEX analysis because the thesis scenario is APK-only audit. It is reproducible and does not depend on runtime coverage.

In the Maven reference lane, the system builds reference profiles from known Maven JAR and AAR releases. Those references are converted to DEX-like evidence with D8, then the same feature extraction logic is applied. This is important because APK code is DEX, so comparing APK DEX to DEX-like references reduces representation mismatch.

The extracted reference features are stored in a local SQLite reference database. I chose a local reference DB because it is reproducible, inspectable, and lets the matcher compare exact coordinate/version profiles without relying on a remote lookup during analysis.

The matcher then compares APK evidence with reference evidence. It ranks candidate coordinates and versions using multiple feature families, not only package names. Package names can help, but they can be renamed, flattened, shaded, or partially removed. The matcher keeps score reasons, alternatives, and score gaps so the report can explain why a version was selected or why it remained uncertain.

After matching, the confidence gate decides what can be emitted. This is one of the most important architecture decisions. A strong identity match is not automatically an exact version. The system separates identity confidence from version confidence, and CVE authority follows those confidence labels.

Accepted Maven detections become CycloneDX components with PURLs and evidence properties. Native files become hash-backed file observations, not invented Maven packages. Then the vulnerability layer queries OSV, but only exact or high-confidence version evidence can support confirmed CVE findings.

The final reporting layer writes JSON, Markdown, HTML, CycloneDX, OSV results, and optional source-validation output. This is why the architecture is not a black-box detector. Every final claim can be traced back to APK evidence, reference evidence, a matcher decision, and a confidence boundary.

The main design decision is conservative: when the evidence is strong, emit a useful SBOM row; when the evidence is weak, expose uncertainty instead of pretending certainty. AI and R8 assistance stay report-only because they can guide review, but they do not change selected versions, SBOM components, or CVE labels.

## Page 22: The contribution is not only a detector

The project is not only a list of detected libraries. It extracts evidence, builds references, matches candidates, chooses versions carefully, emits CycloneDX, queries OSV, and generates reviewable reports.

## Page 23: Implementation

The implementation section follows the PFE thesis. I describe how the main modules work and how the evaluation proves the system behavior without hiding limits.

## Page 24: APK Extractor

The APK extractor unpacks the APK and records container evidence: DEX files, manifest, resources, native files, hashes, and metadata. This makes every report traceable to the analyzed input.

## Page 25: DEX Analyzer

The DEX analyzer extracts code-level evidence: packages, classes, methods, opcode fingerprints, literals, API references, and dependency structure. These features become the basis for matching.

## Page 26: Reference Database

The reference database stores features from selected Maven JAR and AAR releases. Because exact version claims need known references, reference coverage directly affects what the tool can recover.

## Page 27: Matcher

The matcher compares APK evidence with reference evidence and ranks candidates. It uses multiple evidence families, but it does not force every top candidate into a confirmed version.

## Page 28: Version Decision

The version decision stage checks whether the best candidate is strong and separated from alternatives. If versions are too close, the report preserves ambiguity instead of inventing certainty.

## Page 29: SBOM Generator

The SBOM generator emits accepted components in CycloneDX JSON using Maven PURLs. CycloneDX gives interoperability, while the surrounding report preserves confidence and evidence.

## Page 30: CVE and OSV

The vulnerability step queries OSV using package and version evidence. Confirmed CVEs require sufficiently strong component and version evidence; weaker cases remain potential or report-only.

## Page 31: Reports

The report layer is central because it shows what the system decided and why. JSON, Markdown, HTML, CycloneDX, and OSV artifacts are generated from the same evidence.

## Page 32: The implemented command produces a report bundle

On this page, I explain the implemented command produces a report bundle and connect it back to the same principle: APK-derived SBOM claims must stay tied to visible evidence, confidence, and validation boundaries.

## Page 33: Dataset Design

The dataset is layered. Controlled APKs answer whether the pipeline works under known ground truth, clean real APKs show favorable real cases, partial real APKs expose limits, and boundary cases prevent overclaiming.

## Page 34: Dataset Collection

For real APKs, source links and dependency trees were collected when possible. The point is not only to run many APKs, but to know which outputs can be verified.

## Page 35: APK Classification

APK classification explains why not all APKs support the same claim strength. The statistics on this page are not just labels. They explain why the evaluation is split into controlled, clean, partial, source-known, and boundary lanes.

A clear APK is the favorable case. The relevant library bytecode is visible, not heavily transformed, and the matcher can usually compare it with Maven references using package, class, method, opcode, graph, literal, and version-unique evidence.

A multidex APK contains more than one DEX file, such as classes.dex and classes2.dex. The implementation must aggregate evidence across all standard DEX files because a library can be split across them. If we only analyzed one DEX file, we could miss components or weaken the score.

An R8 case means the APK was affected by shrinking, renaming, optimization, inlining, or merging. R8 may preserve enough evidence to say that a library family exists, but it can destroy the small differences that separate adjacent versions. This is why R8 cases are important in the thesis and why exact version claims need confidence gates.

A native-heavy APK contains important .so libraries. The MVP records native files by path, ABI, size, and hash, but it does not invent Maven versions for native code. Native version attribution would need a separate ELF, symbol, and native-reference pipeline.

A hidden-code or protected case may contain encrypted payloads, nonstandard DEX locations, custom class loading, or code downloaded at runtime. Static analysis can report this as risk or boundary evidence, but it cannot truthfully identify Maven package versions that are not visible in the analyzed bytecode.

A source-boundary case appears when the source dependency tree contains rows that do not necessarily become visible APK bytecode, such as BOMs, build-only dependencies, annotation processors, source-only rows, removed dependencies, or dependencies optimized away by shrinking. These rows matter for source-denominator analysis, but they should not be counted as normal APK matching failures without explanation.

So when I explain the stats, I should say: classification keeps the evaluation honest. Clear and controlled cases test whether the pipeline works. Partial and R8 cases test realistic difficulty. Native and hidden-code cases define boundaries. Source-boundary cases explain why full source dependency recall is a different question from emitted SBOM confirmation.

## Page 36: Dataset Composition

This page summarizes the dataset groups used in the evaluation. The important point is that controlled, clean, partial, source-known, and boundary lanes are reported separately.

## Page 37: Evaluation Methodology

The evaluation methodology separates three questions that are easy to confuse.

The first question is exact expected-version recovery. This is the controlled-fixture question. I already know the expected Maven versions before running the tool, and I ask whether the pipeline recovers them. In the current evaluation, the controlled fixtures recover 84 out of 84 expected Maven versions. This proves the mechanics work under controlled conditions, but it is not a universal real-world accuracy claim.

The second question is emitted-version confirmation. This is the normal real-APK metric. The tool emits Maven SBOM rows from APK evidence, then I compare those emitted rows against source dependency trees when source is available. The denominator is the emitted Maven rows that were checked, not the full source dependency tree. This gives 927 confirmed rows out of 1837 emitted source-validated rows, or 50.5 percent. The clean subset is 47 out of 47 across 5 real APKs, and the partial subset is 880 out of 1790 across 97 real APKs.

The third question is full source-denominator exact emission. This is stricter. It asks how many source dependency rows were exactly emitted by the APK-only pipeline. With the shared baseline, that is 927 out of 12082, or 7.7 percent. This number is lower because many source rows are not visible as APK bytecode, not present in the shared reference DB, or not recoverable by the current matcher.

The fourth related question is the source-known upper-bound lane. There, the correct coordinate/version slice is known from source, and the experiment asks whether the matcher can recognize those versions when the search space is constrained. That result is 6772 out of 6772 emitted rows exact, with 5238 remaining source-gap rows classified separately. This is an upper bound, not APK-only production accuracy.

The key sentence I should say is: these denominators answer different questions. Mixing them would exaggerate the tool. Controlled accuracy, emitted-row confirmation, full source recall, and source-known recognition must stay separate.

## Page 38: The evaluation separates controlled results, real APKs, and upper bounds

The headline numbers are deliberately separated: 84 out of 84 controlled expected versions, 47 out of 47 clean real emitted versions, 880 out of 1790 partial real emitted versions, and 927 out of 1837 source-validated emitted rows overall.

## Page 39: Evaluation Results

The results show that the pipeline works well where evidence and references are strong, while real APKs still expose ambiguity and coverage limits. This is a useful result because it says exactly where the system is reliable.

## Page 40: Upper-Bound Experiment

The source-known v2 lane asks a different question from the normal APK-only workflow. It asks: if the correct coordinate and version slice is known from source, can the matcher recognize it? This is why I call it an upper-bound experiment.

Implementation-wise, the process starts by collecting source dependency trees from real APK projects. Those Gradle dependency trees provide known Maven coordinates and resolved versions. From that source evidence, the experiment builds or selects a reference slice that contains the exact source-known versions.

Then the same APK evidence pipeline is used: inspect the APK, extract DEX evidence, compute comparable features, match against the reference profiles, emit rows, and validate the output. The difference is the candidate space. In the source-known lane, the matcher is helped by knowing which versions are relevant from source, so it does not face the full unconstrained APK-only ambiguity.

The output is a transparency-style evaluation: 6772 out of 6772 emitted rows were exact, with zero wrong-version emitted rows and zero missing emitted rows in that constrained emitted lane. At the same time, 5238 source-gap rows remain classified separately. Those gap rows are not hidden. They are split into boundary or explained rows, missing-reference candidates, and matcher-recall candidates.

The interpretation is important. This experiment does not mean the production APK-only tool has 100 percent accuracy. It means that if the correct versions are available and the search space is constrained, the evidence model can recognize them very well. So the lane helps separate reference-coverage gaps, matcher-recall gaps, and source-boundary gaps.

In defense language: the upper-bound result tells us what the system can recognize under favorable source-known conditions. The normal emitted-version metric tells us what the APK-only tool can responsibly emit without that source knowledge.

## Page 41: After the results, the MVP compares differently from related work

After the implementation and results, the comparison changes. Related works usually report detector metrics, while this project reports SBOM artifacts, confidence labels, source-validation lanes, and vulnerability authority.

## Page 42: The contribution is practical evidence control, not a universal best score

The fair claim is not that this MVP beats every detector on every metric. The fair claim is that it completes a practical APK-to-SBOM workflow and exposes where the evidence is strong, weak, or missing.

## Page 43: Failed Experiments

Failed experiments are included because they protect the production tool. A signal can help one target but still be unsafe globally if it creates regressions in controls.

The global opcode tri-gram weight tested whether opcode n-grams should affect the main score. A small weight of 0.02 regressed OpenTracks and Conversations without improving confirmed versions, so the default stayed 0.0 and the signal remained diagnostic.

The global API-reference weight tested API and member-reference overlap as a general score component. A 0.05 weight changed no source-validation metrics in the guarded slice, so there was no measured benefit to justify adding complexity as a production default.

The generic newer-version or recency rule tested whether close adjacent-version ties should prefer the newer release. It helped selected rows such as Activity, ViewPager2, Concurrent Futures, or Lifecycle, but it regressed other apps. Release date is not bytecode evidence, so this rule was rejected globally.

Broad POM coherence tested whether dependency metadata should override ambiguous bytecode ranking. It helped explain some cases, but the generic rule was not clean enough. The decision was to keep POM coherence diagnostic or narrowly scoped, not a broad override.

Global artifact-family rules tested whether family-level rules could be expanded across Android, JVM, KTX, and runtime artifacts. Okio, OkHttp, and Lifecycle supported some narrow rules, but a broad expansion introduced unsafe assumptions, so only scoped tested families were preserved.

The global Phase 4 multi-scale blend tested call-chain, basic-block, class-neighbor, field-operation, and context evidence as a global scorer. It produced 4 real target improvements, but also 6 controlled regressions, 30 source-validated real regressions, and 8 clean-real regressions. That is exactly the kind of result that looks promising locally but is unsafe globally, so the scorer was rejected and the features remained inert for research.

The Phase 5 scoped R8 trigger had 4 target improvements and no triggered regression in its validation gates. However, that was still not enough to silently change the frozen MVP. It stayed experiment-only and report-only until broader proof exists.

Source-used reference additions improved target cases by adding exact versions observed in source trees, but broad additions can change candidate competition in other apps and overfit to the evaluated cases. Only guarded subsets can be promoted; experimental databases stay separate.

The Fragment 1.6.2 experiment compared a nearly identical version against the shared 1.6.1 row. The feature differences were too small to justify shared DB promotion under target and control gates, so it remained experiment-only.

The priority DB broad package shortlist improved exact source-row coverage to 79.9 percent, but the I2P preflight failed fast: output expanded from 18 rows to 111, with 25 mismatches and 14 rows absent from source. That showed that more references can increase noise if candidate control is weak.

The raw-opcode Transformer was a deep-learning experiment over method-level opcode sequences. It reached only 0.110 test macro-F1, below the opcode-count baseline of 0.128. That is why it is presented as negative evidence and not as a DL-first detector.

Hidden DEX or protector recovery was rejected as a Maven package/version claim. Static indicators can report risk, but they cannot prove the identity and version of hidden code. Native version identification was also deferred because .so version attribution needs a separate native reference and provenance pipeline.

The conclusion for this page is: the MVP is conservative because every promoted signal had to survive controls. Failed experiments are not wasted work; they explain why the final tool is safer and more honest.

## Page 44: AI Problem Formulation

Before using machine learning, I first defined the task very carefully. The AI task is not to choose the final Maven version. The task is supervised multiclass classification over existing project evidence rows.

Each training example is one matcher or transparency row. The input features describe what the deterministic system already observed: match scores, score gaps, identity confidence, version confidence, overlap counts, dependency evidence, boundary flags, source-validation context, and diagnostic signals. The output label is a report role, such as confirmed_exact, suggest_report_only, suppress_uncertain, risk_only, mismatch_or_extra, or boundary_do_not_suggest.

The important methodology decision is the split. I did not randomly mix similar rows into train and test. The dataset is grouped by case_id so that related rows from the same APK case do not leak across splits. The corpus used 20,523 training-eligible rows, 149 grouped case IDs, and 1,370 Maven coordinates, with 104 train cases, 15 validation cases, and 30 test cases.

So, when I present the AI part, I should say: AI is learning how to classify evidence quality and triage hard cases. It is not learning permission to emit final SBOM components.

## Page 45: Classical ML

The first AI model is RandomForestClassifier. A Random Forest is an ensemble of decision trees. One decision tree predicts a label by asking a sequence of feature questions, for example whether confidence is high, whether a boundary flag exists, or whether the score gap is small. A single tree can overfit, so Random Forest trains many trees on different samples and feature subsets, then combines their votes. This gives a more stable model and also gives feature-importance values, which are useful in a defense.

The ML workflow was: build labeled rows from project evidence, extract structured numeric and categorical features, group the data by case_id, train the RandomForest with class-balancing, compare it to simple baselines, evaluate on held-out test cases, inspect feature importance and ablations, then integrate it only as report annotations.

The result was a test macro-F1 of 0.708 and test accuracy of 0.690. This is clearly above the majority baseline accuracy of 0.383 and the simple score-threshold baseline of 0.165. The important features included identity confidence, boundary flags, best score, source rank, and dependency score. The model produced 13,736 report-only suggestions.

The defense conclusion is: RandomForest is useful because the evidence is tabular and explainable, but it remains report-only. It can suggest where a reviewer should look; it cannot change selected versions, CycloneDX components, or CVE labels.

## Page 46: Deep Learning

The deep-learning part uses Transformer encoders. A Transformer is a neural sequence model based on attention. Instead of reading features only as separate columns, it can read a sequence of tokens and learn which tokens should pay attention to each other. This is useful when the meaning depends on combinations of evidence, such as confidence, boundary status, score gaps, and report context.

I tested two DL directions. The first direction used structured project-evidence tokens. Each evidence row was converted into a token sequence, then trained with a small torch.nn.TransformerEncoder. The MVP-safe run used a 1-layer encoder with d_model 64 and 4 attention heads. The split was 14,905 training rows, 1,750 validation rows, and 3,868 test rows.

The full structured-token Transformer reached 0.977 test macro-F1 and 0.992 test accuracy, but I do not present it as production authority because shortcut context may inflate the score. Therefore I also trained the MVP-safe profile, which removes source-version, raw candidate-version, source-rank, source-validation-role, and diagnostic-context shortcut tokens. That stricter profile reached 0.882 test macro-F1 and 0.907 test accuracy.

The second direction was a raw-opcode Transformer. That corpus had 1,680 method-level opcode sequences from 14 APKs, evaluated with a case-heldout split. It reached only 0.110 test macro-F1, below the opcode-count logistic-regression baseline of 0.128. This is an honest negative result: raw method opcodes alone are not enough yet.

The defense conclusion is: the structured Transformer proves a useful DL workflow for report-only triage, while the raw-opcode Transformer shows why I did not promote deep learning as the production APK detector.

## Page 47: AI Integration Gate

The AI integration gate is the safety boundary. The allowed role is assistance: AI can annotate risk, suggest report-only investigation, help prioritize difficult R8 or matcher-recall rows, and improve the human-readable report. The forbidden role is authority: AI cannot change selected versions, detected components, CycloneDX SBOM output, CVE or OSV labels, or source-validation metrics.

This gate exists because the output is a security artifact. A wrong AI prediction could create a false CVE claim or hide a real vulnerable version. Also, no strict APK-only AI promotion candidate passed all target and control requirements, and the raw-opcode DL model did not beat its baseline.

So the sentence I should use in the defense is: AI helps decide where to look, but the deterministic evidence gate decides what enters the SBOM and what becomes a confirmed vulnerability claim.

## Page 48: Live Demo Transition

Now I will move from slides to the live demonstration. I will not show static screenshots in the deck. Instead, I will open the generated artifacts directly.

Demo steps and commands:

1. Readiness check:

```powershell
python scripts\run_final_ai_defense_demo.py --refresh
```

Expected result: 10 out of 10 checks passed, ready true, and matcher authority for AI remains false. What I should say here is: this command is a defense preflight. It checks that the generated demo artifacts exist, the toolchain is ready, and the AI layer is still report-only. It is not the long 106-APK evaluation.

2. Clean APK report:

Open `data/results/report-real-f-droid-final-demo-osv/report.html`. This is the clean F-Droid case: package `org.fdroid.fdroid`, version `1.23.2`, 2 DEX files, multidex true, 4 native libraries, extraction risk low, obfuscation risk low, 23 detected Maven components, 4 native file components, and 0 vulnerability findings.

When I show the detected components, I should follow the report order and explain that the table is sorted by the emitted evidence strength. The 23 Maven components are: `androidx.gridlayout:gridlayout` 1.0.0, `androidx.localbroadcastmanager:localbroadcastmanager` 1.0.0, `androidx.swiperefreshlayout:swiperefreshlayout` 1.0.0, `androidx.concurrent:concurrent-futures` 1.1.0, `androidx.recyclerview:recyclerview` 1.4.0, `androidx.appcompat:appcompat` 1.7.0, `androidx.lifecycle:lifecycle-viewmodel-android` 2.8.7, `com.squareup.okhttp3:okhttp` 4.12.0, `androidx.exifinterface:exifinterface` 1.3.6, `io.ktor:ktor-client-okhttp-jvm` 2.3.12, `androidx.work:work-runtime` 2.10.0, `androidx.fragment:fragment` 1.6.1, `androidx.compose.ui:ui-android` 1.7.8, `org.jetbrains.kotlinx:kotlinx-coroutines-android` 1.7.3, `androidx.lifecycle:lifecycle-runtime-android` 2.8.7, `androidx.activity:activity` 1.10.1, `com.squareup.okio:okio-jvm` 3.7.0, `androidx.lifecycle:lifecycle-livedata` 2.8.7, `org.jetbrains.kotlinx:kotlinx-coroutines-core-jvm` 1.7.3, `com.google.android.material:material` 1.12.0, `androidx.compose.foundation:foundation-android` 1.7.8, `androidx.core:core` 1.15.0, and `io.ktor:ktor-http-jvm` 2.3.12.

Then open `data/results/report-real-f-droid-final-demo-osv/sbom.cdx.json`. I should say: this is the machine-readable output. The report page is for humans; CycloneDX is for tools. The components are encoded with Maven identity, versions, PURLs, hashes where applicable, and confidence properties.

Then open `data/results/source-validation/fdroid-final-demo-osv/source-validation.md`. The key result is that the source tree contained 203 parsed source components, and all 23 SBOM Maven components were confirmed, with 0 version mismatches and 0 missing SBOM components. I should be careful: this validates the emitted SBOM rows against source evidence. It does not mean the APK-only pipeline recovered every source dependency.

The clean-demo message is: the MVP can produce a useful recovered SBOM for a real F-Droid APK, show native file observations without overclaiming versions, and produce zero confirmed vulnerabilities when OSV returns none for the emitted components.

3. Positive CVE report:

Open `data/results/demo-osv-vulnerable-jackson-databind/report.html`. This controlled vulnerable APK has 1 DEX file, 0 native libraries, extraction risk low, obfuscation risk low, and 1 detected Maven component. The component is `com.fasterxml.jackson.core:jackson-databind` version 2.9.10.8 with confirmed/high identity confidence 1.000, exact/high version confidence 1.000, match type hybrid-exact, and 3 confirmed vulnerabilities.

Then open `data/results/demo-osv-vulnerable-jackson-databind/osv-vulnerabilities.json`. I should say: OSV is queried using the PURL `pkg:maven/com.fasterxml.jackson.core/jackson-databind@2.9.10.8`. Because the version evidence is exact/high, the vulnerabilities are confirmed, not only potential. The three HIGH findings are CVE-2020-36518, CVE-2022-42003, and CVE-2022-42004.

The positive-demo message is: the same pipeline that stays quiet for the clean F-Droid case produces confirmed CVE findings when exact package and version evidence is strong.

4. Optional command used to regenerate reports, if asked:

```powershell
docker compose run --rm apk-sbom python -m apk_sbom.cli generate-report <apk> --output-dir <result-dir> --db-path <reference-db> --top 30
```

If they ask why I do not regenerate everything live, I should say: report generation can be rerun, but long evaluations and large reference-DB rebuilds are not rerun during the defense because they are time-consuming and already saved as artifacts.

5. Optional regression proof, if asked:

```powershell
docker compose run --rm apk-sbom pytest -q
```

Final sentence for the demo: the live demo shows the final artifacts, not screenshots; the important proof is the chain from APK evidence, to SBOM, to source validation, to OSV vulnerability classification, while AI remains report-only.

## Page 49: Conclusion

In conclusion, the project recovers useful APK-derived SBOM evidence without overstating certainty. The limitations are not hidden; they are part of the contribution.

## Page 50: Limitations and Future Work

The main limitations are reference coverage, matcher recall in difficult real APKs, R8 inlining, native version attribution, hidden code, and the need for larger independent AI/R8 corpora.

## Page 51: The main limitations define the next research work

On this page, I explain the main limitations define the next research work and connect it back to the same principle: APK-derived SBOM claims must stay tied to visible evidence, confidence, and validation boundaries.

## Page 52: Final Closing

My final message is that the project does not claim perfect APK reverse engineering. It provides an implemented, auditable, confidence-aware APK-to-SBOM workflow that is honest about where its evidence is strong and where it must abstain.
