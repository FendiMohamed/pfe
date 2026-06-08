# Research-Backed Real APK Optimization Plan

Generated on 2026-06-06.

This plan is the working order for the next optimization phase after reaching
and exceeding 100 counted source-validated real APKs. It is deliberately based
on the local paper synthesis and existing project diagnostics, not on random
one-off suggestions. The core rule is:

```text
fix ground-truth blockers first;
separate no-signal and boundary cases from accuracy claims;
measure reference DB coverage against the full source dependency denominator;
build a broad evaluation-only DB for source-observed TPLs and versions;
then improve wrong-version and missing-source rows through gated, paper-backed
signals and guarded promotion.
```

## Current Truth To Preserve

| Metric | Value |
|---|---:|
| Counted source-validated real APKs | 102 |
| Clean source-validated real APKs | 5 |
| Partial source-validated real APKs | 97 |
| Source-validated no-Maven-signal APKs | 4 |
| Current source-linked blocked APKs | 0 |
| Limitation/boundary cases | 4 |
| Confirmed emitted Maven versions | 927/1837 |
| Emitted wrong-version rows | 636 |
| Emitted missing-from-source rows | 274 |
| Dashboard miss rows | 911 |
| Source-tree cases in coverage-first dashboard | 106 |
| Source dependency coordinate+version rows | 12,082 |
| Source rows with coordinate in shared DB | 2,220 / 12,082 (18.4%) |
| Source rows with exact version in shared DB | 1,231 / 12,082 (10.2%) |
| End-to-end exact source recall | 927 / 12,082 (7.7%) |

The dashboard miss-row total is one row higher than `636 + 274` because the
dashboard also keeps a candidate-only wrong-version row for analysis. Do not
mix that dashboard diagnostic count with the official emitted-version numerator
and denominator.

The coverage-first dashboard at
`docs/evaluation/REFERENCE_DB_COVERAGE_FIRST_DASHBOARD.md` is now the required
denominator before further version optimization. The `927/1837` emitted-row
confirmation result is still useful, but it must be described as emitted Maven
version confirmation, not full dependency recall.

The counted real APK metric is `5 clean + 97 partial`. Flying Carpet and
FitoTrack are now source-validated partial rows because runtime dependency trees
and `validate-source-deps` output exist. The current state is `102
source-validated, 0 source-linked blocked`.

## Research Basis

| Source/tool family | Lesson used here | Plan impact |
|---|---|---|
| LibScout | Reference profiles are the backbone for exact Maven version detection, but coverage gaps and obfuscation hurt. | Grow an evaluation-only reference DB for source-observed TPLs/versions first; keep shared calibrated promotion separate. |
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
| Flying Carpet 9.0.8 | Default Gradle lane failed with `org/gradle/api/artifacts/SelfResolvingDependency`. | Resolved by Gradle 8.13 `:app` `releaseRuntimeClasspath`; source validation confirms 11/17 emitted Maven versions. |
| FitoTrack 15.6 | Default Gradle lane failed with `org/gradle/api/artifacts/SelfResolvingDependency`; also `compileSdkVersion is not specified`. | Resolved by Gradle 8.13 `:app` `releaseRuntimeClasspath`; source validation confirms 5/18 emitted Maven versions. |

Optimal lane:

1. Completed: treat both as ground-truth acquisition blockers, not matcher failures.
2. Completed: inspect source modules/configurations first, following the successful strict
   module/flavor rescue pattern used for Ultrasonic, RunnerUp, ImapNotes3, and
   Password Master.
3. Completed: use a source-compatible Gradle 8.13 runtime lane that preserves
   runtime `implementation`/`api` dependencies; no validation-copy source edits
   were needed.
4. Completed: admit only after runtime dependency trees, `validate-source-deps`
   JSON/Markdown, refreshed proof docs, and regenerated thesis/evaluation tables exist.

Why this is optimal:

The blocker rows were not missing Maven coordinates and they were not wrong
version rows. They lacked source-side runtime ground truth. The evidence-backed
fix was the existing rescue workflow, not scorer tuning.

Acceptance gate:

```text
blocked -> source-validated-partial only after dependency tree + validation
blocked -> still blocked if build fixes would alter runtime dependency truth
```

### 2. No-Maven-Signal APKs

Scope:

Prep artifact: `docs/evaluation/NO_MAVEN_SIGNAL_AUDIT_PREP.md`.
Audit artifact: `docs/evaluation/NO_MAVEN_SIGNAL_AUDIT.md`.

| APK | Role |
|---|---|
| Privacy Browser 3.20.1 | AndroidX identity-coverage miss control. |
| Mastodon 2.12.3 | Forked-library/reference-family boundary plus weak direct Gson candidate. |
| monocles browser 1.9.3 | AndroidX identity-coverage miss control. |
| Blue Square Speedometer 1.1.0 | Small-app AndroidX identity-coverage miss control. |

`ProseReader` is also listed in the growth queue as a report-only/no-Maven
candidate, but it is not part of the counted source-validated metric.

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

Current audit outcome:

```text
true no-signal controls -> 0/4
AndroidX identity-coverage miss controls -> 3/4
forked-library/reference-family boundary -> 1/4
```

The automated diagnostic exporter is now
`scripts/build_no_maven_signal_diagnostics.py`; it writes JSON, CSV, and
Markdown artifacts for dashboard seeding. The scoped AndroidX report-only
experiment is also complete in
`docs/evaluation/NO_MAVEN_ANDROIDX_REPORT_ONLY_EXPERIMENT.md`: it surfaces 6
source-backed report-only candidates across Privacy Browser, monocles browser,
and Blue Square Speedometer, keeps 8 weak rows suppressed, and records 0 default
selection, SBOM component, or source-validation metric changes. Mastodon's
separate fork-family audit is complete in
`docs/evaluation/MASTODON_FORK_FAMILY_REPORT_ONLY_AUDIT.md`: it surfaces 2
`me.grishka.litex:*` fork-family report-only suggestions and 1 weak direct Gson
suggestion, keeps 7 fork rows suppressed, and records 0 default/SBOM/metric
changes. Next implementation step: move to limitation/boundary tightening, then
use the no-Maven artifacts to seed dashboard fields without counting diagnostics
as accuracy evidence.

### 3. Limitation And Boundary Cases

Scope:

Boundary dashboard artifact: `docs/evaluation/LIMITATION_BOUNDARY_DASHBOARD.md`.

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

Current boundary-dashboard outcome:

```text
verdict -> boundary-dashboard-ready
explicit limitation/boundary cases -> 4
limitation cases counted in accuracy -> 0
native-heavy limitation cases -> 2
obfuscation limitation cases -> 2
hybrid source-validated boundary cases -> 1
visible limitation Maven components not counted -> 21
limitation native files hash-only -> 17
hybrid native files hash-only -> 13
```

Next implementation step: use the reference DB coverage-first dashboard to grow
an evaluation-only source-observed reference catalog before continuing
wrong-version optimization, while keeping these boundary rows separate from
emitted Maven version accuracy.

### 4. Reference DB Coverage Denominator

Scope:

Coverage artifact:
`docs/evaluation/REFERENCE_DB_COVERAGE_FIRST_DASHBOARD.md`.

Current result:

```text
source-tree cases inspected -> 106
source dependency coordinate+version rows -> 12,082
unique source coordinates -> 1,370
unique source coordinate+version pairs -> 3,391
current shared reference DB components -> 101
current shared reference DB coordinates -> 44
source rows with coordinate in shared DB -> 2,220 / 12,082 (18.4%)
source rows with exact version in shared DB -> 1,231 / 12,082 (10.2%)
source rows emitted with exact source version -> 927 / 12,082 (7.7%)
```

Source-observed catalog result:

```text
source-observed coordinates -> 1,370
source-observed coordinate+version slots -> 3,391
bytecode-buildable coordinates -> 1,361
bytecode-buildable source-version slots -> 3,347
metadata-only BOM skips -> 9
coordinates absent from shared DB -> 1,326
known coordinates with missing source versions -> 41
```

Evaluation-only DB batch status:

```text
batch log -> docs/evaluation/SOURCE_OBSERVED_REFERENCE_DB_BATCH_LOG.md
batches 000-017 source-version slots attempted -> 1500
downloaded artifact metadata records -> 1329
download failures recorded -> 171
bytecode-bearing conversion records -> 954
no-bytecode conversion skips -> 375
evaluation DB path -> data/reference_db/reference_features_source_observed_versions.sqlite
next source-version download offset -> 1500
```

Optimal lane:

1. Treat saved Gradle runtime dependency trees as the source dependency
   denominator.
2. Build a source-observed catalog from every coordinate that appears in those
   trees. This is now generated at
   `docs/evaluation/SOURCE_OBSERVED_REFERENCE_CATALOG.md`, with build inputs at
   `configs/source_observed_reference_catalog.json` and
   `configs/libraries.source_observed_versions.json`.
3. Fetch Maven Central / Google Maven metadata for those coordinates and record
   every published version, including prereleases when source trees use them.
4. Build every bytecode-bearing JAR/AAR version into a broad evaluation-only DB;
   record metadata-only/no-bytecode artifacts as skips, not as silent failures.
5. Evaluate with three separate metrics:
   emitted-component confirmation,
   reference DB coordinate/exact-version coverage,
   and end-to-end exact source dependency recall.
6. Only after this denominator is visible should the wrong-version queue become
   the main optimization lane again.

Why this is optimal:

The user's concern is correct: high accuracy on emitted components can look good
while most source dependencies are outside the reference DB. The honest fix is
not to lower the accuracy claim or hide missing TPLs. The honest fix is to make
coverage a first-class metric, expand the search space in an evaluation-only
DB, and then optimize version selection with the real denominator visible.

Acceptance gate:

```text
coverage DB -> evaluation-only until source dependency recall and control drift are measured
shared calibrated DB -> only for source-supported versions with documented promotion evidence
accuracy wording -> emitted confirmation, DB coverage, and end-to-end recall stay separate
```

### 5. Wrong-Version Rows

Scope:

There are 636 emitted wrong-version rows. These are the highest-value accuracy
optimization rows because the emitted coordinate is source-present, but the
selected version differs from the source-resolved version.

Initial priority coordinates from the dashboard:

| Coordinate family | Why it comes first |
|---|---|
| `org.jetbrains.kotlin:kotlin-stdlib` | 56 wrong-version rows; repeated Kotlin era/version-band drift. |
| `androidx.core:core-ktx` and `androidx.core:core` | 99 combined rows; common AndroidX near-version confusion. |
| `org.jetbrains.kotlinx:kotlinx-coroutines-*` | 91 combined rows; repeated source/tool selected version bands. |
| `androidx.activity`, `androidx.fragment`, `androidx.lifecycle:*` | High-volume AndroidX bands with adjacent-version ambiguity. |
| `androidx.viewpager2:viewpager2` | 27 wrong-version rows; known beta/stable ambiguity from earlier proof bundles. |
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

The tool already uses a hybrid approach. The next gain should not be reported
as full accuracy until the coverage denominator is visible. Adding every
source-observed version belongs first in an evaluation-only DB; then the
wrong-version lane can decide which exact versions are distinguishable, which
must stay ambiguous, and which are unsafe to promote.

Acceptance gate:

```text
promote only if target rows improve and controlled/clean/partial/no-Maven/boundary controls do not regress
reject if the change creates new missing-source emissions or false version flips
```

Current wrong-version dashboard outcome:

```text
artifact -> docs/evaluation/WRONG_VERSION_OPTIMIZATION_DASHBOARD.md
verdict -> wrong-version-dashboard-ready
emitted wrong-version rows -> 636
unique coordinates -> 38
unique APK cases -> 96
source-linked blocked rows in scope -> 0
metric changes -> 0
P1 Kotlin/coroutines lane -> 147 rows across 3 coordinates and 66 APK cases
P1 AndroidX core/activity/fragment/lifecycle lane -> 259 rows across 9 coordinates and 83 APK cases
P2 ViewPager2/support AndroidX lane -> 157 rows across 13 coordinates and 80 APK cases
P2 CVE-sensitive networking/JSON lane -> 38 rows across 6 coordinates and 27 APK cases
```

The dashboard keeps all rows diagnostic/reporting-only. The first isolated
source-version/reference-DB experiment is now recorded at
`docs/evaluation/WRONG_VERSION_P1_COROUTINES_ANDROID_1_6_4_EXPERIMENT.md`.
It tests `org.jetbrains.kotlinx:kotlinx-coroutines-android@1.6.4`: all 20
target rows are fixed, but shared DB promotion is rejected because F-Droid
regresses from source-confirmed `1.7.3` to `1.6.4` and Organic Maps/Termux
limitation-boundary report-only component sets change. That result remains
valuable as proof that "add one source version and promote it globally" is not
enough. The next wrong-version experiment should wait behind the coverage-first
evaluation-only DB lane unless it is explicitly scoped as a diagnostic.

### 6. Missing-From-Source Rows

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

### 7. Reference DB Growth

Scope:

Reference DB growth now has two distinct modes:

- Broad evaluation-only coverage DB: every published bytecode-bearing version
  for every source-observed coordinate.
- Shared calibrated DB: only source-supported versions that pass documented
  promotion evidence.

Reference DB growth should not be used to explain blocked, boundary, true
no-signal, or missing-from-source rows.

Optimal lane:

1. Build a DB growth queue from the coverage-first dashboard:
   source-observed coordinate, all source versions, all metadata-published
   versions, packaging, bytecode/no-bytecode status, and cases affected.
2. Build a broad evaluation-only DB before changing the shared calibrated DB.
3. Separately build a DB growth queue from dashboard wrong-version rows:
   coordinate, source version, selected version, APK count, APK family, and
   existing ambiguity evidence.
4. Run isolated experiment DBs for top repeated source versions.
5. Compare experiments against controlled fixtures, clean real APKs, high-value
   partial rows, R8/minified rows, and historical regression guards.
6. Promote in the smallest safe unit:
   singleton version first, then coordinate-family bundle only if singleton
   promotion is insufficient and controls remain clean.
7. Record rejected versions as useful evidence, not as failed work.

Why this is optimal:

LibScout and ATVHUNTER show the need for broad reference profiles. TPL-Benchmark
and current project experiments show why broad expansion without controls can
overfit and regress. Guarded promotion is the correct middle path.

Acceptance gate:

```text
coverage addition -> broad evaluation-only DB first
source-version promotion -> isolated improvement + documented current-control drift status
unsafe addition -> keep in experiment DB and dashboard queue, not shared calibrated DB
```

### 8. Dashboard Optimization

Scope:

The current dashboard seed already has Markdown, JSON, case CSV, and miss-row
CSV outputs. The next dashboard should expose every detail needed for dataset
growth and reference DB planning.

Required views:

| View | Purpose |
|---|---|
| Overview KPIs | 102 source-validated, 0 blocked, 4 no-Maven, 4 boundary, 927/1837 confirmed. |
| Per-APK classification | Show bucket, APK family, framework/native/R8 labels, validation ratio, evidence paths. |
| Blocker board | Empty current blocker state, plus resolved Flying Carpet/FitoTrack rescue evidence, failure signatures, and admission gate. |
| No-Maven board | True no-signal controls vs rows needing identity-coverage diagnostics. |
| Boundary board | Native/framework/hidden-code cases excluded from Maven accuracy. |
| Wrong-version heatmap | Coordinate/version bands, source versions seen, selected versions seen, APK families affected. |
| Reference coverage board | Source dependency denominator, coordinate coverage, exact-version coverage, and end-to-end source recall. |
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
| 4 | Build the reference DB coverage-first dashboard. | `REFERENCE_DB_COVERAGE_FIRST_DASHBOARD.md`. | Source denominator, coordinate coverage, exact-version coverage, and end-to-end recall are visible. |
| 5 | Continue source-observed evaluation-only DB batches. | `SOURCE_OBSERVED_REFERENCE_CATALOG.md`, `SOURCE_OBSERVED_REFERENCE_DB_BATCH_LOG.md`, source-version config, all-version config, and DB build logs. | Every source-observed TPL coordinate has metadata status and bytecode/no-bytecode result. |
| 6 | Evaluate broad DB against source dependency recall and emitted-component precision. | Coverage dashboard plus source-validation comparison reports. | Recall improves or failure modes are explicit without changing shared DB claims. |
| 7 | Continue wrong-version coordinate queue from dashboard CSV. | Source-version candidate queue and guarded DB workflow. | Top repeated coordinates have experiment-ready source-version bundles. |
| 8 | Run isolated DB experiments for the top source-version bands. | Experiment summaries and comparison reports. | Confirmed count improves with documented control impact. |
| 9 | Run missing-source suppression/downgrade diagnostics. | Candidate-pruning and family/artifact diagnostics. | Missing-source emitted rows decrease without losing confirmed rows. |
| 10 | Add dashboard run history and promotion status fields. | Dashboard JSON/CSV and report. | Dashboard can drive future dataset and DB-growth sessions directly. |

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
