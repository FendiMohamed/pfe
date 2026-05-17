# Merged Paperguide Synthesis for the APK-to-SBOM MVP

Source batches:

- Batch 1: LibScout, ATVHunter, SAD, LibScan, LibHunter.
- Batch 2: Systematic Assessment, Automated TPL Detection, LibPecker, LibID, LibAttention.

Purpose: merge the two Paperguide outputs into a final, cautious synthesis for the approved MVP architecture.

Important caution: Paperguide output is useful for synthesis, but final thesis claims should cite the original papers. Some claims below are intentionally softened where the papers do not clearly prove full R8 support or standard SBOM output.

## 1. Final Ranked List of Most Important Papers

| Rank | Paper / tool | Why it matters for the MVP | Main use in our architecture |
|---:|---|---|---|
| 1 | ATVHunter | Closest to our end goal: version-level TPL detection followed by vulnerability mapping. | Two-stage candidate-to-version design, opcode/CFG evidence, CVE workflow. |
| 2 | SAD | Strongest direct support for version-level structural matching and adjacent-version disambiguation. | CDG similarity, class summaries, structural version scoring, literal tie-breakers. |
| 3 | LibHunter | Most important for R8/optimization awareness. | R8 evaluation design, confidence degradation under optimization, future R8-aware matching. |
| 4 | LibScan | Strong staged matching design using class correspondence, method opcode similarity, and call-chain opcode similarity. | Hybrid matcher design, opcode/call-chain evidence. |
| 5 | LibScout | Foundational for reference profiles and exact-version motivation. | Maven reference DB, version candidates, partial-match fallback. |
| 6 | Systematic Assessment | Best evaluation framework for Android TPL detection tools. | Metrics, baselines, multidex/AAR/obfuscation limitations. |
| 7 | Automated TPL Detection: Are We There Yet? | Practical comparison of tools and common failures. | Evaluation criteria and hybrid-tool justification. |
| 8 | LibID | Version-aware and obfuscation-resilient matching using class dependencies, CFGs, constraints. | Robust matching ideas, version-level evaluation, but avoid BIP-heavy first MVP. |
| 9 | LibPecker | Strong support for class dependency matching under partial/customized libraries. | CDG/class dependency matching. |
| 10 | LibAttention | Best support for discussing ML-based R8 resilience, but not first MVP core. | Future work and R8 discussion. |

## 2. Final Comparison Table

| Paper / tool | Problem | Method | Key features | Obfuscation/R8 handling | Version detection | Dataset/metrics signal | Limitations | Reuse in MVP |
|---|---|---|---|---|---|---|---|---|
| LibScout | Package-name matching fails; exact version is needed for security. | Reference profiles from original libraries; class-hierarchy/profile matching. | package/class/method hierarchy, fuzzy descriptors, normalized bytecode, Merkle-style profiles. | Strong against basic identifier renaming; not R8-specific; weaker under heavy shrinking/flattening. | Yes, but sometimes candidate version sets. | 164 libraries, 2,065 versions, thousands of apps in original study. | Incomplete DB; ambiguity; older than R8-focused work. | Reference DB idea, exact-version goal, partial fallback. |
| ATVHunter | Vulnerable TPL versions are hard to identify precisely. | Two-phase detection: CFG coarse filtering, opcode/basic-block fine matching, vulnerability mapping. | CDG candidate splitting, CFG, opcodes in basic blocks, fuzzy hashes. | Handles common obfuscation; R8-specific depth should be stated cautiously. | Yes, central goal. | Large Maven-style DB and vulnerability DB; reports precision/recall/F1. | Full DB is too large for MVP; costly feature extraction. | Coarse-to-fine matching and version-to-CVE pipeline. |
| SAD | Library-level detection is easier than exact version detection; adjacent versions are confusing. | CDG node features, class summaries, matched-subgraph structural similarity. | CDG, class summaries, field operations, method invocation sequences, opcodes, literals. | Stronger under obfuscation; affected by method inlining, heavy optimization, reflection/encryption. | Yes, central goal. | 1,123 apps, 562 TPL versions; library/version F1 reported. | Full CDG-heavy pipeline is complex; tiny version differences remain hard. | CDG version scoring and literal tie-breakers. |
| LibScan | Existing detectors need more precise matching under obfuscation/partial code. | Staged similarity: class correspondence, method opcode, call-chain opcode. | package/class hierarchy, method opcodes, call-chain opcodes. | Handles several obfuscation types, but should not be described as fully R8-robust. | Yes. | Ground-truth and large-scale datasets; precision/recall/F1. | Threshold tuning; advanced obfuscation and optimization still hard. | Method opcode and call-chain matching ideas. |
| LibHunter | R8 optimization changes code structure and hurts TPL detection. | Optimization-aware static matching, focusing on impactful R8 strategies such as inlining/call-site optimization. | class features, method opcodes, strings, cross-inlining evidence. | Directly studies R8/shrinking/optimization; does not cover all possible transformations. | Yes. | R8 prevalence and variant datasets; library/version F1. | R8-focused; not all obfuscators/optimizations. | R8-aware evaluation and confidence policy. |
| Systematic Assessment | Tool comparisons were fragmented and incomplete. | Unified evaluation of public tools on multiple criteria. | compares package hierarchy, class dependencies, signatures, opcodes, APIs, PDG features. | Shows tools handle renaming better than shrinking/package modification; D8/R8 not fully supported by older tools. | Evaluates version-identification accuracy. | 59 TPLs, 221 apps, 2,115 versions, F-Droid and obfuscated datasets. | Older formats/new app formats/AARs/multidex can cause misses. | Evaluation framework and limitation checklist. |
| Automated TPL Detection | Need a fair comparison of tools in real-world conditions. | Empirical evaluation of detection tools. | tool-dependent features across package, graph, method, opcode approaches. | Compares obfuscation resilience. | Evaluates version ability. | Effectiveness, efficiency, obfuscation, usability. | No single best tool. | Justifies hybrid architecture. |
| LibPecker | Detect libraries despite customization/dead-code elimination. | Class dependency signatures, fuzzy class matching, adaptive thresholds. | class inheritance, field dependencies, method prototype dependencies. | Handles several common obfuscations; no R8-specific evaluation in retrieved notes. | Not a primary version detector. | >10K libraries, >20K apps; reports high precision/recall. | Weak for libraries with few code features; package assumptions can fail. | CDG/class dependency matching. |
| LibID | Identify obfuscated third-party libraries and versions. | Binary profiles, class matching, constraints, BIP, LSH. | class dependencies, class signatures, CFGs, package hierarchy. | ProGuard/shrinking/repackaging/control-flow tests; not R8-specific. | Yes. | 69 libraries, 1,444 versions, synthetic and F-Droid apps. | dex2jar dependency; BIP complexity; scalability. | Version-level evaluation and robust matching ideas, not full BIP MVP. |
| LibAttention | Rule-based detectors degrade under R8. | Feature language model / Transformer-like detection. | learned coarse-grained Android code features. | Strong R8 discussion/evaluation; ML approach may generalize better. | No clear version-level method in retrieved notes. | Precision/recall/F1 across R8 modes. | Requires data/training; less explainable; no standard SBOM. | Future work and R8 discussion, not first MVP. |

## 3. MVP Architecture Justification

The merged evidence supports a static, two-stage, repository-backed architecture:

```text
APK
-> extract all DEX files and metadata
-> recover classes, methods, opcodes, and dependency relationships
-> detect candidate libraries using structural and metadata evidence
-> refine to version-level using finer-grained opcode/class/CDG similarity
-> output exact version, version range, or uncertain candidates with confidence
-> generate CycloneDX SBOM
-> query OSV/CVE/advisory sources for detected versions
```

This architecture is justified because:

- LibScout, ATVHunter, LibID, LibScan, and SAD all depend on comparing APK code against known library versions.
- LibSift/LibD/LibPecker/SAD-style ideas show that segmentation and dependency structure are needed before accurate matching.
- LibScan and ATVHunter show that opcode/CFG/basic-block features are useful for version discrimination.
- SAD shows that version-level detection needs structural similarity and tie-breakers because adjacent versions can be almost identical.
- LibHunter and LibAttention show that R8 optimization must be treated as a real threat to accuracy.
- Systematic Assessment and Automated TPL Detection show that no single tool or feature is enough.

The important gap for this PFE is:

```text
Academic Android TPL tools detect libraries/versions,
but they generally do not emit standard CycloneDX/SPDX SBOMs.
SBOM tools generate standard SBOMs,
but they do not reliably recover obfuscated compiled APK dependencies.
```

Therefore, our contribution is the bridge:

```text
evidence-based APK library/version detection -> standard SBOM -> vulnerability lookup
```

## 4. What To Implement In The First Month

### Week 1: Environment and APK extraction

- Run toolchain audit.
- Scaffold Python project.
- Implement APK extraction with multidex support.
- Output JSON summary of:
  - `classes*.dex`
  - manifest/resources presence
  - native `.so` files
  - hashes and file locations.

### Week 2: DEX and reference feature extraction

- Use Androguard to extract:
  - packages
  - classes
  - methods
  - descriptors
  - opcode summaries.
- Build small Maven reference DB for selected libraries.
- Convert JAR/AAR to DEX with D8 if available.
- Store metadata/features in SQLite or structured JSON first.

### Week 3: Basic matching and version scoring

- Implement candidate generation:
  - package clues
  - class overlap
  - method overlap
  - metadata/string clues.
- Implement opcode similarity for version ranking.
- Output:
  - exact version if score and margin are strong
  - version range/candidate set if close
  - unknown if weak.

### Week 4: SBOM, vulnerabilities, and evaluation

- Generate CycloneDX JSON with:
  - group/artifact/version
  - PURL
  - confidence
  - evidence.
- Query OSV API for detected versions.
- Optionally scan SBOM with Trivy/Grype.
- Evaluate on controlled APKs:
  - clear build
  - ProGuard/R8 rename
  - R8 shrink if possible.

## 5. What To Leave As Future Work

| Future work | Why not first MVP |
|---|---|
| Full LibHunter-style R8 optimization modeling | Too complex; many transformations and special cases. |
| Full SAD-style CDG-heavy implementation | Valuable but time-consuming; start with simpler graph/class features. |
| Full ATVHunter-scale Maven DB | Too large for one-month MVP; use selected libraries first. |
| LibID-style BIP/LSH solver | Heavy and harder to debug; use simpler weighted scoring first. |
| LibAttention-style ML | Requires training data, infrastructure, and less explainable output. |
| Full native `.so` version detection | Separate binary-analysis problem. |
| Packed/encrypted APK support | Requires unpacking/dynamic analysis, out of scope. |
| Dynamic code loading analysis | Code may not exist inside the APK. |
| Complete support for all Maven libraries | DB coverage problem; expand gradually. |

## 6. Risks and Limitations

| Risk | Impact | Mitigation |
|---|---|---|
| Missing reference library/version | Cannot identify exact version. | Report unknown; expand reference DB gradually. |
| Adjacent versions are almost identical | False exact-version risk. | Use margin thresholds and candidate sets. |
| R8 method inlining/shrinking | Class/method/opcode matches degrade. | Report lower confidence; evaluate R8 separately. |
| Package flattening/repackaging | Segmentation becomes harder. | Use dependency and opcode evidence, not only package names. |
| String encryption | Metadata/string clues disappear. | Treat strings as optional weak evidence. |
| Androguard parsing failures | Feature extraction can fail for some APKs. | Add graceful errors; use JADX manually for debugging. |
| Native libraries | Java/Kotlin SBOM may be incomplete. | Extract/hash native `.so`; full native versioning future work. |
| CVE source mismatch | OSV/NVD/GitHub/Sonatype may disagree. | Store source and mark vulnerability evidence clearly. |
| Overclaiming R8 support | Academic risk. | Say R8-aware/partially evaluated, not R8-proof. |

## 7. Supervisor-Friendly Explanation

The approved MVP is a realistic bridge between Android library detection research and SBOM tooling.

Most Android TPL research tools can detect libraries or versions from APK bytecode, but they generally do not generate standard SBOMs. Most SBOM tools can generate CycloneDX or SPDX when package metadata is available, but they do not solve the problem of recovering dependencies from compiled and possibly obfuscated APKs.

Our MVP combines both directions:

```text
compiled APK
-> static bytecode analysis
-> candidate library detection
-> version scoring with confidence
-> CycloneDX SBOM
-> vulnerability lookup
```

The architecture is supported by the literature:

- LibScout justifies reference profiles and exact-version detection.
- ATVHunter justifies the version-to-vulnerability workflow.
- SAD justifies CDG/class structural version scoring.
- LibScan justifies staged opcode/call-chain matching.
- LibHunter and LibAttention justify careful R8 evaluation.
- Systematic Assessment and Automated TPL Detection justify using multiple evaluation dimensions and avoiding package-name-only detection.

The MVP will not claim perfect recovery for every APK. It will support standard APKs, multidex, selected Maven libraries, and light obfuscation. For uncertain cases, it will output confidence, candidate versions, or unsupported status instead of forcing an exact version. This makes the project technically realistic, academically defensible, and suitable for a one-month implementation sprint.

## 8. Final Implementation Stance

The best first implementation is:

```text
LibScout idea: Maven reference versions
+ LibScan idea: staged class/method/opcode matching
+ SAD idea: structural version scoring and tie-breakers
+ ATVHunter idea: version -> vulnerability lookup
+ LibHunter/LibAttention lesson: R8 is difficult, evaluate honestly
+ CycloneDX/OSV tooling: practical SBOM and CVE output
```

This is the strongest balanced MVP because it is explainable, implementable, and directly tied to the papers.

