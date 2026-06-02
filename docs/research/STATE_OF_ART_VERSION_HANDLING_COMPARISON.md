# State-of-the-Art Version Handling Comparison

This note compares how the main Android third-party library detection papers and tools in the project state of the art handle a recurring problem:

- broader reference/version coverage can improve some APKs
- but more candidate versions can also increase adjacent-version confusion, false flips, and unstable cross-APK behavior

The goal here is not to rank papers by headline F1, but to document how each approach deals with version ambiguity, reference coverage growth, and realistic evaluation pressure.

## Comparison Table

| Tool / paper | Exact versioning? | How it handles many-version ambiguity | What it does not fully solve | Comparison with our tool |
| --- | --- | --- | --- | --- |
| LibRadar | No | Mostly avoids the problem by detecting library families rather than stable exact versions. Useful as a fast candidate-generation layer. | Does not provide exact version labels, so it does not really solve adjacent-version confusion. | Our tool goes further by making version decisions and exporting uncertainty instead of stopping at family detection. |
| LibD | No | Also mostly sidesteps the issue because it is clustering-oriented and not designed for exact per-APK version recovery. | No exact version disambiguation strategy. | Our tool addresses the harder SBOM case directly and treats version mismatches as first-class evidence. |
| LibScout | Yes | Builds reference profiles from known library versions using package-class-method hierarchy and fuzzy descriptors. This is the classic reference-database approach. | Weakens under dead-code elimination, package flattening, and modern R8 optimization; no strong cross-APK safeguard against broad version expansion. | Our tool keeps the reference-DB idea, but adds guarded promotions, uncertainty output, and regression checks before shared DB changes. |
| ORLIS | Limited / indirect | Uses a two-stage pipeline: coarse candidate filtering first, then finer structural matching. This reduces the candidate set before expensive comparison. | Does not provide a strong explicit adjacent-version disambiguation policy and is heavy to run. | Our tool uses the same staged spirit, but is more explicit about uncertainty and source-validated regression safety. |
| LibPecker | Partial | Improves structural matching through class dependency signatures, which helps with partial library inclusion and coarse family separation. | Realistic benchmark results show version-level performance remains limited; it does not present a strong explicit version-tie policy. | Our tool borrows the "structure matters" lesson but adds APK-visible ambiguity reporting and guarded calibration. |
| ATVHunter | Yes | Uses a large Maven-based TPL database, CDG/module decoupling, coarse CFG filtering, then fine opcode/basic-block matching. Fine-grained evidence is intended to support vulnerable-version detection. | Still depends on the quality and coverage of the reference database; our notes do not show a paper-level policy for preventing global regressions when adding versions. | Similar coarse-to-fine philosophy, but our tool is stricter about refusing generic "newer near-tie wins" rules and about checking controls before promoting new versions. |
| LibScan | Limited / practical | Uses staged class, method-opcode, and call-chain-opcode matching to improve precision and keep the search manageable. | Later R8-focused work still shows optimization pressure remains a problem; no explicit global coverage-promotion discipline is documented in our notes. | Similar staged filtering idea, but our tool exposes unresolved version bands instead of silently forcing a likely winner. |
| LibHunter | Yes | Adds optimization-aware matching to handle shrinking, inlining, and call-site optimization under modern Android builds. | Improves results but does not fully solve version confusion under realistic optimized builds. | Stronger on optimization awareness than our current MVP, but our tool is more explicit about uncertainty, safe partial results, and shared-DB regression control. |
| LibAttention | No exact versioning | Uses an ML model to improve library detection under R8-obfuscated settings. | No exact version output, so it does not solve SBOM-grade version ambiguity by itself. | Our tool is weaker on learned obfuscation resilience, but stronger for explainable version claims and SBOM-ready output. |
| SAD | Yes | Explicitly targets adjacent-version confusion using CDGs, candidate class mappings, class summaries, stateful/stateless handling, and literal features as tie-breakers. | Still acknowledges difficult heavy-optimization cases; tie-breaking improves disambiguation but does not guarantee stability across all APK families. | This is the closest paper-level match to our conservative tie-breaking approach. Our tool is stricter about leaving risky ties unresolved when independent support is missing. |
| LibMD | Yes | Treats adjacent-version ambiguity as a core problem. Uses multi-scale fusion across class, function-call, and basic-block dependency evidence plus Bayesian scoring and LDG metadata. | Full implementation details and open evaluation artifacts were not fully available during our review; cross-APK promotion safety is not a focus of our notes. | Conceptually the closest ideal to our direction. Our current tool is simpler, but more operationally conservative: guarded promotions, explicit ambiguity sets, and current-control checks are already documented and enforced. |
| TPL-Benchmark | Benchmark, not detector | Handles the problem by exposing it. Uses a stronger and more realistic benchmark to show that version-level and library-level performance are lower than earlier papers suggested. | Does not provide the algorithmic fix itself. | Strongly aligned with our evaluation style: realistic controls, honest partial cases, and resistance to overfitted improvement claims. |
| Revisiting Third-Party Library Detection | Benchmark / reassessment | Rebuilds or strengthens ground truth and re-evaluates tools under more realistic conditions, showing weaker version performance than earlier claims suggested. | Again, this diagnoses the problem more than it solves it. | Reinforces our policy of keeping clean and partial evidence separate and not promoting app-specific gains into global truth without checks. |
| ObfDetector / advanced obfuscation robustness studies | Benchmark / failure analysis | Shows that modern obfuscation and R8-era transformations can break exact version detection badly, especially at version level. | Primarily diagnostic; it explains why naive scaling of versions is risky but does not provide a full general cure. | Supports our decision to export confidence and ambiguity instead of forcing exact-looking answers in risky cases. |
| Our tool | Yes | Uses calibrated reference evidence, bytecode features, artifact-family coherence, ambiguity export, conservative tie-breaking, and guarded reference-DB promotion with current-control regression checks. Near-tie candidates remain visible when no independent evidence cleanly separates them. | Still limited by reference coverage gaps, AndroidX/Kotlin version bands with nearly identical bytecode, artifact-family nuance, and strong optimization/obfuscation cases. | The main difference is not that we found a magical detector. It is that we made cross-APK stability and uncertainty handling explicit policy, not an afterthought. |

## What the Papers Actually Did

The papers and tools in the state of the art mostly fall into four groups.

### 1. Tools that mostly avoid the issue

LibRadar and LibD are important historically, but they are not strong examples of exact version disambiguation. They mainly help with library-family detection, clustering, or candidate generation rather than stable version recovery.

### 2. Tools that reduce the candidate set first

ORLIS, ATVHunter, and LibScan all use a coarse-to-fine pattern. This is a practical way to make the search space smaller before expensive or detailed matching. It helps, but it is not the same thing as a principled answer to "what if many nearby versions look almost the same?"

### 3. Tools that add explicit disambiguation signals

The strongest direct answers in the literature are:

- SAD: class-structural matching plus literal tie-breakers for adjacent versions
- LibMD: multi-scale fusion plus Bayesian probability scoring
- LibHunter: optimization-aware matching for modern R8-style transformations

These papers do not pretend the problem disappears. They add better evidence so that more ties can be separated safely.

### 4. Benchmarks and reassessments that expose the problem

TPL-Benchmark, the systematic assessment, revisiting studies, and modern obfuscation robustness studies are important because they show that older reported scores were often measured under easier conditions. Their main contribution is not a new tie-breaker. Their contribution is forcing the field to confront the real difficulty of exact versioning on realistic APKs.

## How Our Tool Differs

Our tool is closest in spirit to the LibScout -> SAD -> LibMD line, but with a stronger operational rule:

- do not promote new reference versions globally just because they help one APK
- do not force a near-tie to the newer version just because it "sounds likely"
- keep ambiguity visible when the APK evidence is too similar across nearby versions
- require current-control regression checks before shared DB promotion

That is the clearest difference between our implementation practice and the way most papers are described in the repo notes. The papers usually propose better matching signals. Our tool also adds a repo-level safety policy for shared reference growth.

## Practical Thesis Takeaway

The literature does not show a universal cure for version-space growth. Instead, it shows a progression:

1. detect library families
2. use better structure-aware matching
3. add tie-breakers or Bayesian scoring for adjacent versions
4. evaluate on more realistic datasets and admit that performance drops

Our tool fits into that progression, but its distinctive contribution is methodological honesty:

- exact when evidence is strong
- partial when identity is useful but version selection is still risky
- ambiguous when nearby versions are feature-equivalent
- conservative when a new reference addition helps one APK but threatens others

## Source Notes Used

- `papers/data/SBOM_Tools_Synthesis_Table.md`
- `papers/data/impact_on_project.md`
- `work/state of the art/Updated_State_of_the_Art_APK_SBOM.md`
- `docs/thesis/PAPER_TO_IMPLEMENTATION_TRACEABILITY.md`
- `docs/evaluation/THESIS_EVALUATION_CHAPTER_DRAFT.md`
