# Research-Backed Real APK Optimization Plan

Generated on 2026-06-06.

This plan is the working order for the next optimization phase after reaching
100 counted source-validated real APKs. It is deliberately based on the local
paper synthesis and existing project diagnostics, not on random one-off
suggestions. The core rule is:

```text
fix ground-truth blockers first;
separate no-signal and boundary cases from accuracy claims;
then improve wrong-version and missing-source rows through gated, paper-backed
signals and guarded reference-DB promotion.
```

## Current Truth To Preserve

| Metric | Value |
|---|---:|
| Counted source-validated real APKs | 100 |
| Clean source-validated real APKs | 5 |
| Partial source-validated real APKs | 95 |
| Source-validated no-Maven-signal APKs | 4 |
| Current source-linked blocked APKs | 2 |
| Limitation/boundary cases | 4 |
| Confirmed emitted Maven versions | 911/1802 |
| Emitted wrong-version rows | 617 |
| Emitted missing-from-source rows | 274 |
| Dashboard miss rows | 892 |

The dashboard miss-row total is one row higher than `617 + 274` because the
dashboard also keeps a candidate-only wrong-version row for analysis. Do not
mix that dashboard diagnostic count with the official emitted-version numerator
and denominator.

The 100 real APK metric is `5 clean + 95 partial`. Flying Carpet and FitoTrack
are still source-linked blocked, so the current state is not "100 source
validated and 0 blocked"; it is `100 source-validated, 2 source-linked blocked`.

## Research Basis

| Source/tool family | Lesson used here | Plan impact |
|---|---|---|
| LibScout | Reference profiles are the backbone for exact Maven version detection, but coverage gaps and obfuscation hurt. | Keep the reference DB, but expand it only through guarded source-version experiments. |
| ATVHUNTER | CDG module decoupling plus coarse-to-fine CFG/opcode evidence helps vulnerable-version detection. | Use opcode/basic-block evidence as scoped diagnostics for hard version bands, not as a global weight. |
| LibScan/LibHunter | Opcode and call-chain matching, especially inlining/call-site awareness, improves R8-era robustness. | Apply inlining/call-chain signals to R8/minified and high-obfuscation cases behind control gates. |
| SAD | CDG summaries, stateful/stateless handling, field-operation sequences, and literals are strong adjacent-version signals. | Prioritize literal and class-summary tie-breakers for repeated AndroidX/Kotlin wrong-version bands. |
| LibMD | Multi-scale class/function/basic-block fusion with Bayesian scoring and LDG metadata is the closest SBOM-oriented north star. | Move toward explainable probability/confidence scoring, but keep current-control regression checks before promotion. |
| LibAttention | Learned Smali/code representations help R8 presence detection but do not solve exact version SBOM output. | Defer ML-first detection; use classifier-style signals later for identity/risk, not first for exact versions. |
| TPL-Benchmark and systematic assessments | Realistic datasets expose lower performance and overfitting risk. | Keep clean, partial, blocked, no-signal, and boundary buckets separate; reject single-example "wins". |
| ObfDetector and R8 robustness studies | Advanced obfuscation can collapse version-level accuracy. | Do not claim R8-proof recovery; downgrade confidence or expose ambiguity when evidence is weak. |
| Current MVP diagnostics | Global opcode/API weights and broad source-version DB expansion have already regressed controls. | Only promote narrow, evidence-backed changes that pass the current control matrix. |

## Execution Order

### 1. Source-Linked Blocked APKs

Scope:

| APK | Current blocker | Current status |
|---|---|---|
| Flying Carpet 9.0.8 | `org/gradle/api/artifacts/SelfResolvingDependency`; 60 runtime configuration attempts failed. | Source tarball and APK report exist, but no runtime dependency tree. |
| FitoTrack 15.6 | `org/gradle/api/artifacts/SelfResolvingDependency`; also `compileSdkVersion is not specified`. | Source tarball and APK report exist, but no runtime dependency tree. |

Optimal lane:

1. Treat both as ground-truth acquisition blockers, not matcher failures.
2. Inspect source modules/configurations first, following the successful strict
   module/flavor rescue pattern used for Ultrasonic, RunnerUp, ImapNotes3, and
   Password Master.
3. If strict probing still fails, create validation-only Gradle/toolchain copies
   that preserve runtime `implementation`/`api` dependencies and patch only the
   build-system blockers.
4. Keep both excluded until all admission gates exist: runtime dependency tree,
   `validate-source-deps` JSON/Markdown, refreshed proof docs, and regenerated
   thesis/evaluation tables if counts change.

Why this is optimal:

The blocker rows are not missing Maven coordinates and they are not wrong
version rows. They lack source-side runtime ground truth. The evidence-backed
fix is the existing rescue workflow, not scorer tuning.

Acceptance gate:

```text
blocked -> source-validated-partial only after dependency tree + validation
blocked -> still blocked if build fixes would alter runtime dependency truth
```

### 2. No-Maven-Signal APKs

Scope:

| APK | Role |
|---|---|
| Privacy Browser 3.20.1 | Source-validated no-Maven-signal control. |
| Mastodon 2.12.3 | Source-validated no-Maven-signal control. |
| monocles browser 1.9.3 | Source-validated no-Maven-signal control. |
| Blue Square Speedometer 1.1.0 | Source-validated no-Maven-signal control. |

`ProseReader` is also listed in the growth queue as a report-only/no-Maven
candidate, but it is not part of the 100 counted source-validated metric.

Optimal lane:

1. For each row, compare the resolved source runtime dependency tree with the
   generated report.
2. If the source runtime tree genuinely has no Maven dependencies that should
   appear in DEX, keep the row as a no-signal/false-positive control.
3. If source Maven dependencies exist but the APK report emits no Maven
   components, route the row to identity coverage analysis:
   package/class presence, CDG/class dependency evidence, opcode/literal
   evidence, and reference DB coverage.
4. Do not force components into the report just to improve recall; the value of
   these cases is proving that the tool can remain quiet when evidence is weak.

Why this is optimal:

LibRadar/LibD-style family detection can be useful for candidate generation, but
the MVP is an SBOM tool. A no-Maven-signal row should become an accuracy case
only if source evidence shows Maven bytecode should have been detected.

Acceptance gate:

```text
true no-signal -> keep as no-Maven control
source deps present -> create identity-coverage diagnostic before changing DB or scoring
```

### 3. Limitation And Boundary Cases

Scope:

| Case | Boundary |
|---|---|
| Organic Maps 2026.05.08-4 | Native-heavy `.so` boundary. |
| Termux 0.119.0-beta.3 | Native/bootstrap boundary. |
| Hidden DEX loader fixture | Nonstandard/dynamic code-loading boundary. |
| Simplify obfuscated sample | Heavy obfuscation limitation sample. |

Jitsi Meet remains a counted source-validated partial APK for its Maven
components, but its React Native/WebRTC/Hermes native files stay hash-only
framework/native boundary evidence.

Optimal lane:

1. Keep native `.so` files as CycloneDX file components with hashes, path, ABI,
   size, and extraction evidence.
2. Keep hidden/protector-style DEX cases as risk and limitation evidence unless
   the code is statically visible and source validation exists.
3. Add framework classification fields for React Native, Cordova, Flutter,
   Unity/game-engine, and native-heavy apps before treating absent Maven output
   as a detector miss.
4. Do not count boundary cases in Maven version accuracy metrics.

Why this is optimal:

The literature separates Java/Kotlin TPL detection from native and protected
payload analysis. ObfDetector and R8 robustness studies support conservative
confidence and boundary reporting; LibAttention-style learned detection may
help later, but it does not provide exact Maven versions for SBOM claims.

Acceptance gate:

```text
boundary case -> report scope and risk clearly
boundary case -> no Maven accuracy claim unless source-visible Maven ground truth exists
```

### 4. Wrong-Version Rows

Scope:

There are 617 emitted wrong-version rows. These are the highest-value accuracy
optimization rows because the emitted coordinate is source-present, but the
selected version differs from the source-resolved version.

Initial priority coordinates from the dashboard:

| Coordinate family | Why it comes first |
|---|---|
| `org.jetbrains.kotlin:kotlin-stdlib` | 54 wrong-version rows; repeated Kotlin era/version-band drift. |
| `androidx.core:core-ktx` and `androidx.core:core` | 96 combined rows; common AndroidX near-version confusion. |
| `org.jetbrains.kotlinx:kotlinx-coroutines-*` | 87 combined rows; repeated source/tool selected version bands. |
| `androidx.activity`, `androidx.fragment`, `androidx.lifecycle:*` | High-volume AndroidX bands with adjacent-version ambiguity. |
| `androidx.viewpager2:viewpager2` | Known beta/stable ambiguity from earlier proof bundles. |
| Okio/OkHttp/Gson/Jackson families | Lower volume but CVE/SBOM impact is higher when exact versions matter. |

Optimal lane:

1. Split wrong-version rows by root cause:
   source version missing from reference DB, near-identical adjacent bytecode,
   artifact-family mismatch, R8/minified evidence loss, or dependency/POM
   coherence conflict.
2. Use the dashboard CSV as the queue, sorted by repeated coordinate and repeated
   source version, not by a single favorite APK.
3. For source-version absence, create isolated reference DB experiments and
   compare against the current control matrix before promotion.
4. For adjacent-version ambiguity, use the strongest paper-backed tie-breakers:
   SAD-style literals/class summaries/field-operation evidence, LibMD-style
   multi-scale probability, ATVHUNTER/LibScan opcode and basic-block diagnostics,
   and LibHunter call-chain/inlining evidence for R8/minified cases.
5. Keep global opcode/API weights disabled unless a scoped per-coordinate or
   high-obfuscation trigger passes controls.
6. Preserve ambiguity output when evidence cannot safely separate nearby
   versions.

Why this is optimal:

The tool already uses a hybrid approach. The next gain is not "add every version"
or "newer wins"; prior experiments showed that those regress controls. The
research-backed path is better evidence plus guarded promotion.

Acceptance gate:

```text
promote only if target rows improve and controlled/clean/partial controls do not regress
reject if the change creates new missing-source emissions or false version flips
```

### 5. Missing-From-Source Rows

Scope:

There are 274 emitted missing-from-source rows. These are different from
wrong-version rows: the tool emitted a coordinate that the resolved source
runtime tree does not contain.

Optimal lane:

1. Treat missing-from-source rows as over-emission or artifact-family nuance
   until proven otherwise.
2. Do not expand the reference DB to fix these rows; more reference versions can
   make over-emission worse.
3. Use the promoted composite family shortlist, class-correspondence diagnostics,
   confidence thresholds, and artifact-family suppression diagnostics before
   changing matcher scores.
4. Split rows into:
   low-confidence candidates that should be downgraded,
   public-vs-Android target artifact-family nuances,
   transitive/source-tree interpretation issues,
   and true false positives.
5. Keep candidate-only diagnostics separate from emitted SBOM components so the
   dashboard can show pressure without inflating official error counts.

Why this is optimal:

Missing-source rows are precision problems, not coverage problems. The
coarse-to-fine and family-shortlist diagnostics align with ORLIS/ATVHUNTER/
LibScan staged filtering, while the MVP's contribution is keeping default
output stable until a live control pass is clean.

Acceptance gate:

```text
reduce emitted missing-source rows without losing confirmed source-present rows
candidate diagnostics may grow; emitted SBOM false positives should not
```

### 6. Reference DB Growth

Scope:

Reference DB growth should target source-present wrong-version rows first. It
should not be used to explain blocked, boundary, true no-signal, or
missing-from-source rows.

Optimal lane:

1. Build a DB growth queue from dashboard wrong-version rows:
   coordinate, source version, selected version, APK count, APK family, and
   existing ambiguity evidence.
2. Run isolated experiment DBs for top repeated source versions.
3. Compare experiments against controlled fixtures, clean real APKs, high-value
   partial rows, R8/minified rows, and historical regression guards.
4. Promote in the smallest safe unit:
   singleton version first, then coordinate-family bundle only if singleton
   promotion is insufficient and controls remain clean.
5. Record rejected versions as useful evidence, not as failed work.

Why this is optimal:

LibScout and ATVHUNTER show the need for broad reference profiles. TPL-Benchmark
and current project experiments show why broad expansion without controls can
overfit and regress. Guarded promotion is the correct middle path.

Acceptance gate:

```text
source-version addition -> isolated improvement + zero harmful current-control drift
unsafe addition -> keep in experiment DB and dashboard queue, not shared calibrated DB
```

### 7. Dashboard Optimization

Scope:

The current dashboard seed already has Markdown, JSON, case CSV, and miss-row
CSV outputs. The next dashboard should expose every detail needed for dataset
growth and reference DB planning.

Required views:

| View | Purpose |
|---|---|
| Overview KPIs | 100 source-validated, 2 blocked, 4 no-Maven, 4 boundary, 911/1802 confirmed. |
| Per-APK classification | Show bucket, APK family, framework/native/R8 labels, validation ratio, evidence paths. |
| Blocker board | Flying Carpet/FitoTrack rescue state, failure signature, next attempted lane, admission gate. |
| No-Maven board | True no-signal controls vs rows needing identity-coverage diagnostics. |
| Boundary board | Native/framework/hidden-code cases excluded from Maven accuracy. |
| Wrong-version heatmap | Coordinate/version bands, source versions seen, selected versions seen, APK families affected. |
| Missing-source table | Emitted coordinate, confidence, family nuance, APK family, downgrade/suppression candidate. |
| Reference DB queue | Candidate source versions, expected benefit, control status, promote/reject decision. |
| Regression gate history | Before/after metrics for any DB/scorer experiment. |

Optimization principles:

1. Use source-validated metrics as the primary truth.
2. Keep emitted rows, candidate-only rows, no-Maven controls, and boundary cases
   visually separate.
3. Make every dashboard action trace back to a proof artifact or experiment
   artifact.
4. Add run IDs and trend snapshots before adding more charts.

Acceptance gate:

```text
dashboard answers: what is blocked, what is no-signal, what is boundary,
what is wrong-version, what is missing-source, and what can safely grow the DB
```

## Work Queue

| Priority | Work item | Primary artifact to update | Success metric |
|---:|---|---|---|
| 1 | Rescue Flying Carpet and FitoTrack dependency trees. | `REAL_APK_BLOCKED_APK_TRIAGE.md`, proof-status docs, source-validation outputs. | Blocked count drops from 2 if validation gates pass. |
| 2 | Audit the four no-Maven-signal rows. | Dashboard case CSV/report plus per-row diagnostics. | Each row labeled true no-signal or identity-coverage miss. |
| 3 | Tighten boundary/framework labeling. | APK type evaluation and dashboard classifications. | Boundary rows stay excluded, but dashboard explains why. |
| 4 | Build wrong-version coordinate queue from dashboard CSV. | Source-version candidate queue and guarded DB workflow. | Top repeated coordinates have experiment-ready source-version bundles. |
| 5 | Run isolated DB experiments for the top source-version bands. | Experiment summaries and comparison reports. | Confirmed count improves without control regressions. |
| 6 | Run missing-source suppression/downgrade diagnostics. | Candidate-pruning and family/artifact diagnostics. | Missing-source emitted rows decrease without losing confirmed rows. |
| 7 | Add dashboard run history and promotion status fields. | Dashboard JSON/CSV and report. | Dashboard can drive future dataset and DB-growth sessions directly. |

## Stop Conditions

Stop and document instead of promoting when:

- a build rescue changes the runtime dependency truth;
- a DB addition helps one APK but regresses an existing clean or partial control;
- a scorer change reduces missing rows by hiding true source-present components;
- an obfuscation/native/framework case lacks source-visible Maven ground truth;
- a dashboard metric combines counted source-validated rows with report-only or
  boundary rows.

## Thesis Claim

This plan supports the thesis story that the MVP is an honest hybrid
APK-to-SBOM pipeline: it recovers exact Maven versions when evidence is strong,
keeps useful partial results visible, refuses to hide blocked or boundary cases,
and improves through paper-backed signals plus guarded reference growth rather
than unsupported exact-version guesses.
