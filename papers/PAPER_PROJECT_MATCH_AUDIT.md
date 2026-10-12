# Paper-to-Project Match Audit

## Overall verdict

The paper is substantially consistent with the project, but it is not yet a complete technical account of the implementation.

It accurately presents the project as:

- an APK-to-Maven component/version evidence pipeline;
- a static DEX-based analysis workflow;
- a CycloneDX SBOM producer;
- an optional OSV vulnerability-reporting workflow;
- an evidence-aware system separating identity, exact version, ambiguity, native files, and vulnerability interpretation;
- an evaluation with separate controlled, clean, partial, source-denominator, and source-version-constrained lanes;
- a conservative system whose rejected experiments are part of the contribution.

The numerical claims match the retained 20 June 2026 evaluation snapshot:

- 84/84 expected rows across 72 controlled fixtures;
- 47/47 emitted rows across five clean APK cases;
- 880/1,790 emitted rows across 97 partial APK cases;
- 927/1,837 across 102 source-validated APKs;
- 927/12,082 source-denominator rows across 106 source-tree cases;
- 6,772/6,772 in the source-version-constrained upper-bound analysis.

The correct status is: **faithful working paper based on the retained snapshot; final implementation-traceability pass still required.**

## 1. What the paper explains correctly

### Problem and scope

The manuscript correctly explains that the input is a compiled APK and that source dependency declarations, build metadata, and the original dependency graph are usually unavailable. It correctly discusses D8, R8, shrinking, renaming, optimization, multidex packaging, AAR contents, native libraries, and inaccessible code.

### Central design principle

The paper correctly identifies the central contribution as evidence separation:

- component-family identity;
- exact-version evidence;
- ambiguity and alternatives;
- native-file handling;
- downstream vulnerability interpretation.

This matches the matcher, report, SBOM, and vulnerability modules. It also correctly states that confidence labels are rule-based summaries, not calibrated probabilities.

### Implemented workflow

The paper correctly describes:

1. APK inspection;
2. DEX parsing and feature extraction;
3. comparison with versioned Maven reference profiles;
4. candidate ranking;
5. separate identity/version decisions;
6. CycloneDX serialization;
7. optional OSV lookup.

It correctly explains that source dependency trees are used for validation and are not silently used to provide candidate versions in the ordinary APK-only matcher.

### Evaluation structure and values

The manuscript correctly keeps these evidence lanes separate:

- controlled expected-version confirmation;
- emitted-version agreement in real APKs;
- source-denominator coverage;
- source-version-constrained recognition;
- vulnerability workflow demonstrations.

The reported values and their qualifiers match the retained thesis/evaluation records. The distinction between the earlier 30-fixture/35-component checkpoint and the later 72-fixture/84-row snapshot is also correct.

### Rejected experiments

The paper correctly records that global R8 blending, broader AI/structural signals, unsafe reference promotions, and generic APK-only version-band expansion were not granted default authority after regression or validation concerns.

### Vulnerability claims

The F-Droid and Jackson examples are correctly presented as workflow demonstrations, not vulnerability precision, recall, exploitability, or population-risk measurements.

## 2. What is under-explained

### Promoted default matcher behavior

The manuscript says “weighted evidence fusion” but does not clearly name the two promoted default behaviors documented by the project:

- the composite family shortlist;
- the guarded version-unique literal/context reranker.

These should be named in Section 4 because they explain the production/default path.

### Evidence features

The implementation extracts and/or evaluates:

- package, class, and method overlap;
- opcode features;
- class-dependency evidence;
- string literals and literal context;
- API references;
- structural fingerprints;
- version-unique features;
- POM/dependency metadata;
- artifact-family information.

The paper should include a short table identifying which signals are extracted, which contribute to the default aggregate, and which remain optional or diagnostic.

### Implementation modules

The paper should connect the method to the source code with one concise implementation table covering:

- APK extraction and DEX analysis;
- Maven download/reference conversion;
- SQLite reference storage;
- matching and scoring;
- report/CycloneDX serialization;
- vulnerability classification.

It does not need to list every file, but this would make the claimed implementation easier to verify.

### Status contracts

The paper should explicitly state the status vocabulary:

- identity: confirmed, likely, candidate, uncertain;
- version: exact, likely, candidate, uncertain.

It should repeat that confidence labels are rule-based and not probabilities.

### Reference database role

The paper should explain more clearly that reference coverage is a first-order limit:

- an absent coordinate or release cannot be emitted as a reference-backed exact result;
- JAR/AAR artifacts may be converted to comparable DEX evidence;
- Android-target artifact variants can cause apparent version mismatches;
- adding references can improve one APK while regressing another.

### APK-family behavior

The thesis work contains useful family-level analysis for modern AndroidX/Kotlin, R8/minified, multidex, old dependencies, native-heavy apps, large dependency trees, framework-boundary cases, hidden-code cases, and no-native cases. The paper mentions these boundaries but does not show enough representative examples.

## 3. Snapshot release-control issue

The project also contains later priority-recovery and source-build records with values around 9,656–9,657 exact source-version rows out of 12,082. These are not automatically contradictions: they belong to later or different recovery lanes.

The paper currently freezes the 20 June 2026 PFE snapshot. Before submission, add an explicit sentence:

> Unless otherwise stated, the numerical results in this paper are transcribed from the retained PFE evaluation snapshot dated 20 June 2026 and are not merged with later project recovery experiments.

Do not merge later values without a matching frozen database, input manifest, run identifier, and denominator contract.

## 4. Required final corrections

1. Add the snapshot boundary and provenance to the evaluation protocol.
2. Add a production matcher table covering default, optional, diagnostic, and rejected signals.
3. Add the identity/version status vocabulary.
4. Add one compact APK-family result table.
5. Verify that commit 2983d54 is the correct implementation/evaluation snapshot; otherwise replace it with the correct identifier.
6. Keep the terms emitted-version confirmation, source-denominator coverage, source-version-constrained upper bound, and workflow demonstration. Do not replace them with accuracy, precision, recall, complete recovery, or vulnerability detection performance.

## 5. Final judgment

### Does the paper explain the project?

Yes, at the level of research question, architecture, evidence policy, evaluation logic, and recorded conclusions.

### Does it fully document what was built?

Not yet. It under-describes the promoted matcher defaults, feature families, status contracts, module responsibilities, and APK-family analysis.

### Do the numbers match?

Yes, when interpreted as the frozen 20 June 2026 retained snapshot.

### Are there direct contradictions?

No direct contradiction was found between the manuscript and that retained snapshot. Later project records use different recovery lanes and must remain explicitly outside the paper snapshot or be integrated through a new frozen release package.

**Recommended status: technically faithful working paper; final implementation-traceability and snapshot-release pass required before submission.**

