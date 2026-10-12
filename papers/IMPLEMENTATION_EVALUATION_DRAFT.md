# Section 5 — Implementation and Experimental Evaluation (Working Draft)

> **Evidence status.** Results below are transcribed from the retained thesis,
> evaluation documentation, dashboards, and project history. The experiments
> are not rerun for this paper. Some machine-readable row exports, generated
> fixtures, database snapshots, and run manifests are not in this checkout, so
> the manuscript does not claim independent recalculation from raw inputs.

## 5.1 Research questions

The evaluation addresses four questions:

- **RQ1 — Controlled recovery:** How well does the pipeline recover expected
  Maven coordinates and versions in controlled APK fixtures, including
  selected rename, shrink, optimization, and multidex variants?
- **RQ2 — Real-APK version confirmation:** Among Maven versions emitted for
  source-validated real APKs, what fraction agrees with the resolved source
  dependency evidence, and how does this differ between clean and partial
  cases?
- **RQ3 — Coverage and failure causes:** How much of the resolved source
  coordinate/version denominator is emitted exactly, and what documented
  gaps are associated with reference coverage, matcher/reporting, version
  ambiguity, artifact-family variants, metadata-only dependencies, or other
  boundaries?
- **RQ4 — Downstream claim handling:** How does the pipeline preserve evidence
  and uncertainty in CycloneDX and vulnerability reports? This is a workflow
  question, not a vulnerability-detection precision or recall study.

## 5.2 Implementation under evaluation

The command-line application is `apk-sbom-mvp` version 0.1.0 and requires
Python 3.12 or later. APK inspection reads archive and manifest data; DEX
analysis uses Androguard and aggregates features from accessible DEX files.
The reference path downloads versioned Maven artifacts, converts compatible
JAR/AAR inputs to DEX for comparable analysis, and stores component metadata
and features in SQLite. These are the implemented stages; the actual database
snapshot used for each reported result is not present in this checkout.

The matcher aggregates package, class, method, opcode, dependency, literal,
and version-unique evidence with normalized configurable weights. In the
current source defaults, package/class/method/opcode/dependency/literal/
version-unique weights are 0.15/0.45/0.25/0.15/0.10/0.08/0.12; API-reference
and opcode-ngram weights are zero. These parameters are implementation
settings, not learned coefficients or calibrated probabilities. The default
decision path enables a composite family shortlist (margin 0.10 and complete
retained version bands) and a guarded version-unique literal/context near-tie
reranker. The latter requires at least two matched unique features, a unique
score of at least 0.10, an advantage of at least 0.05, raw-score distance no
greater than 0.020, and the identity and minimum raw-score gates.

The output serializer emits CycloneDX 1.5, including Maven Package URLs,
evidence and identity/version properties, and ambiguity details when present.
Native `.so` files become SHA-256-identified file components without Maven
identity/version attribution. OSV lookup is optional at the report command;
reported findings are classified using identity and version evidence, and an
explicit source-validation artifact can further relabel them. The pinned
repository dependencies include Androguard 4.1.3, NetworkX 3.4.2, Requests
2.32.3, Packaging 24.2, Pydantic 2.10.6, and Rich 13.9.4. These are the
declared project dependencies, not a substitute for a frozen environment
manifest from the evaluation runs. The values above describe the current
source defaults; the absent run manifest prevents verification that the
historical result snapshot used these same settings.

Optional R8 experiments, version-band diagnostics, AI suggestions, and
additional structural features are not part of the authoritative default
selection path unless an explicit promotion record enables a narrowly gated
behavior. The CLI describes these additions as opt-in and report-only; they do
not change selected components or versions, CycloneDX content, vulnerability
labels, or source-validation metrics. Section 4 describes the method-level
evidence model; this subsection records concrete implementation behavior.

## 5.3 Experimental protocol and datasets

The project distinguishes controlled fixtures, source-validated real APKs,
source-denominator analysis, source-version-constrained recognition,
no-Maven-signal controls, and boundary examples. Their units and permitted
interpretations differ, so results are reported separately.

### Controlled fixtures

The retained evaluation record describes a staged controlled-set expansion:
an earlier checkpoint covered 30 generated APK fixtures and 35 expected Maven
components; the later thesis-facing snapshot covers 72 fixtures and 84
expected component/version rows. The later aggregate is used below as the
final recorded controlled result. The fixtures cover clear cases and selected
package-flattening, rename, shrink, optimization, multidex, and multi-library
variants. The paper transcribes the recorded results; it does not claim a new
run or independent recalculation from the generated fixture batch.

### Source-validated real APKs

The retained primary real-APK summary covers 102 source-validated APKs that
emitted Maven rows: five clean cases and 97 partial cases. Four additional
source-validated APKs emitted no Maven component rows. Those controls are
reported separately and excluded from rates whose denominator is emitted
Maven rows. Source dependency trees are used to validate emitted coordinates
and versions, but remain source-side evidence: they do not prove that each
resolved dependency is present in the final packaged APK.

The source-denominator layer contains 106 source-tree cases (the 102
Maven-emitting cases plus four no-signal controls). The broader 110-case
transparency inventory also includes four native-heavy, hidden-code, or
obfuscation boundary examples. Those four cases do not expand the 106-case
source-tree denominator or the 102-case emitted-version denominator.

Some dependency trees were collected using validation-only copies, selected
Gradle configurations, or toolchain/build-rescue modifications. The current
checkout does not contain all source trees or the per-case validation exports
needed to enumerate and independently verify every modification. The final
protocol table must therefore identify the source tag/commit, APK hash,
configuration, and validation-copy changes for each included case when the
raw package is restored.

**Table 2 — Evaluation strata and metric eligibility (retained snapshots).**

| Evidence stratum | Cases | Checked unit or denominator | Metric eligibility and qualifier |
|---|---:|---|---|
| Controlled fixtures | 72 | 84 expected component/version rows | Final recorded controlled-set snapshot after the earlier 30-fixture/35-component checkpoint; expected-row confirmation in generated fixtures only |
| Clean source-validated | 5 | 47 emitted Maven version rows | Emitted-version confirmation; sparse clean cases limit generalization |
| Partial source-validated | 97 | 1,790 emitted Maven version rows | Emitted-version confirmation; report partial stratum separately |
| Combined Maven-emitting set | 102 | 1,837 emitted Maven version rows | Combined emitted-version confirmation; not full source dependency recall |
| No-Maven-signal controls | 4 | Zero emitted Maven rows | Case-level control only; no emitted-row rate is defined |
| Full source-denominator layer | 106 | 12,082 source coordinate/version rows | Source-denominator coverage, reported separately from emitted-row confirmation |
| Source-version-constrained analysis | 106 | 6,772 source-constrained emitted rows | 6,772/6,772 upper-bound recognition using per-APK exact source-version slices; not ordinary APK-only performance |
| Additional boundary cases | 4 additional, within the 110-case inventory | Native-heavy, hidden-code, or obfuscation boundary evidence | Limitation examples only; outside the 106-case source-tree denominator and 102-case emitted-row set |

The 106 source-tree cases comprise the 102 Maven-emitting cases and four
no-signal controls. The broader 110-case inventory adds four boundary cases;
it does not change the denominator of either source-tree measure. The counts
above are transcribed from the retained thesis and evaluation records. The
machine-readable package needed to regenerate every aggregate is not present
in this checkout, so the paper identifies these as documented snapshots.

### Coverage and source-version-constrained analyses

The shared-reference coverage snapshot uses 12,082 source coordinate/version
rows across the 106 source-tree cases. Its dashboard records 2,220 rows whose
coordinate occurs in the shared database and 1,231 rows whose exact source
version occurs there. These are historical coverage counts, not precision
measurements. A separate source-version-constrained v2 experiment used a
10,517-component evaluation database and per-APK reference slices restricted
to exact source-known coordinate/version pairs. That restriction makes the
experiment an upper-bound recognition analysis, not normal APK-only matching.

The associated v2 gap summary classifies 5,238 source-gap rows. Among its
diagnostic categories, 2,281 are matcher-recall candidates and 442 are
missing-reference candidates; the other rows include artifact-family,
metadata/source-only, source/platform, and related boundaries. These
classifications are retained snapshot summaries and require the row-level
exports and matching database to reproduce.

### Vulnerability workflow cases

RQ4 uses two documented examples: a clean F-Droid report with no returned OSV
findings and a controlled Jackson Databind 2.9.10.8 fixture with three
returned advisories. They demonstrate evidence-qualified report behavior.
Neither example is a vulnerability gold standard, and the first is not
evidence that the APK contains no vulnerable component.

## 5.4 Metrics and denominator contracts

Each reported quantity has a different unit and interpretation:

| Measure | Unit and numerator/denominator | Permitted interpretation |
|---|---|---|
| Controlled expected-version confirmation | Expected component/version rows confirmed among 84 expected rows, across 72 fixtures in the retained thesis snapshot | Controlled behavior only; not real-APK accuracy |
| Emitted-version confirmation | Emitted Maven version rows agreeing with source evidence / checked emitted Maven version rows; 1,837 rows across 102 APKs | Quality of emitted versions; not full dependency recall |
| Source-denominator coverage | Source-observed coordinate/version rows emitted exactly / all source rows; 927/12,082 across 106 source-tree cases | End-to-end coverage against source dependencies; not proof of packaged-code recall |
| Shared-reference coverage | Source rows with coordinate or exact version in the shared DB / 12,082 source rows | Reference-set coverage; not matcher precision |
| Source-version-constrained recognition | Emitted rows confirmed under per-APK exact source-version candidate slices / checked emitted rows; 6,772/6,772 across 106 cases | Upper-bound recognition under known source versions only |

The real-APK primary measure is the **emitted Maven version confirmation
rate**:

```text
confirmed emitted Maven coordinate/version rows
------------------------------------------------
checked emitted Maven coordinate/version rows
```

It counts agreement for rows the tool emitted. It does not count source rows
the tool missed, and it is not named precision, recall, or accuracy. The
source-denominator measure uses a different denominator and must be kept in a
separate table or clearly separated row. Zero-emission controls have no
emitted-row rate; they remain a separate case count. Percentages are secondary
to counts and must use consistent rounding after the source snapshot is
restored.

No cross-paper baseline is included because the published studies use
different candidate construction, reference coverage, transformations, and
false-positive rules. Earlier project baselines on a smaller controlled set
are not merged with the retained 72/84 or real-APK lanes.

## 5.5 Results by research question

### RQ1 — Controlled recovery

The final recorded thesis snapshot reports 84 of 84 expected component/version
rows confirmed across 72 controlled fixtures. The project task history records
an earlier 30-fixture/35-component checkpoint before the controlled inventory
was expanded. Rename and shrink evidence is reported cautiously as a
candidate, rather than as exact-version authority. This result characterizes
the generated fixtures; it does not estimate performance on a population of
Android apps.

### RQ2 — Real-APK emitted-version confirmation

| Stratum | Confirmed / checked emitted versions | APKs | Rate |
|---|---:|---:|---:|
| Clean source-validated | 47/47 | 5 | 100.0% |
| Partial source-validated | 880/1,790 | 97 | 49.2% |
| Combined source-validated | 927/1,837 | 102 | 50.5% |

The clean result comes from only five APKs, and several have sparse emitted
rows. It should not be generalized from this small stratum. The combined
result means that 927 emitted Maven version rows agree with the source-side
validation evidence among 1,837 checked emitted rows. The retained dashboard
classifies 636 rows as version mismatches and 274 as missing from the source
tree. These are not automatically equivalent to packaged-code false positives
because source resolution and APK packaging are different observations.

### RQ3 — Source coverage and failure causes

The retained source-denominator summary reports 927 exact emitted rows among
12,082 source coordinate/version rows across 106 source-tree cases (7.7%). In
the shared-reference snapshot, 2,220/12,082 source rows (18.4%) have a
coordinate represented and 1,231/12,082 (10.2%) have the exact source version
represented. This gap between output confirmation and denominator coverage
shows why an emitted-row rate alone does not characterize end-to-end coverage.

In the separate v2 source-version-constrained analysis, 6,772/6,772 emitted
rows are reported as exact confirmations across the 106 cases. The exact
source-known versions were used to restrict each APK's candidate reference
slice, so this is an upper-bound recognition result, not the APK-only matcher
result. Its 5,238 non-emitted source-gap rows include the documented
2,281 matcher-recall candidates and 442 missing-reference candidates, along
with alias, metadata/source-only, and platform or project boundaries. These
categories should be reported as triage of the retained v2 snapshot, not as a
complete row-level causal attribution without the row-level exports.

### RQ4 — Evidence-qualified vulnerability reporting

The clean F-Droid example returned no OSV findings; the controlled Jackson
Databind 2.9.10.8 example returned three advisories. In the implementation,
identity/version evidence controls whether a returned advisory is labeled
confirmed or potential, and explicit source validation can add a separate
validation status. The two examples demonstrate workflow behavior only; they
do not estimate vulnerability precision, recall, exploitability, or risk.

### Rejected and report-only experiments

The project retained failed experiments as decision evidence. A global R8
blend was not promoted after regression checks. The examiner/decision-ledger
snapshot and the expanded Phase-4 diagnostics report different improvement and
regression counts and denominators; without the run manifest, this paper
records the qualitative rejection only and does not merge those counts.
Scoped R8 triggers and AI suggestions remain report-only where controls do not
justify changing matcher or SBOM authority. Source-specific reference
additions that improved a target APK but introduced regressions elsewhere
were not promoted globally. An APK-only version-band candidate expansion with
no safe APK-only fixes likewise remains outside the default selection path.
These decisions answer why the shipped pipeline is conservative; they are not
additional population accuracy scores.

## 5.6 Discussion

RQ1 shows strong confirmation in generated fixtures under the final recorded
controlled snapshot. The 30/35 count is an earlier checkpoint before the
inventory was expanded to 72/84. RQ2 shows a higher emitted-version
confirmation rate in the small clean stratum than in the larger partial
stratum, while its aggregate remains an emitted-row measure. RQ3 shows that
reference coverage and matcher/reporting gaps constrain how much of the source
dependency denominator is emitted; the source-version-constrained result
isolates recognition only after source versions restrict the candidate set.
RQ4 confirms that the reporting workflow can preserve evidence qualifications
for example findings, but no vulnerability accuracy conclusion follows.

Taken together, the evidence supports a bounded account of useful version
confirmation with visible reference, transformation, and scope limits. It
does not support universal APK dependency recovery or independent real-world
recall estimates. The rejected experiments also show that an apparent target
improvement is insufficient for default promotion when control or real-app
regressions remain.

## 5.7 Threats to validity

- **Internal validity:** The reference database and its calibration history
  are absent; some evaluated APKs or app families may have contributed to
  reference-version selection. Threshold and promotion choices, evaluator
  behavior, database snapshots, validation-only source copies, and external
  OSV responses can affect the reported outcomes. The incompatible controlled
  and Phase-4 snapshots cannot be reconciled without their matching raw files
  and manifests.
- **External validity:** Source-available and F-Droid apps do not represent all
  Android applications. The sample may be imbalanced by app family and build
  system. Native-heavy apps, commercial protectors, dynamic loading, encrypted
  payloads, and unsupported ecosystems remain outside reliable coverage.
- **Construct validity:** A Gradle runtime dependency tree is source-side
  evidence, not an oracle for code packaged in the final APK. Emitted-version
  confirmation is not full dependency recall. Rule-based confidence labels
  are not calibrated probabilities, and CycloneDX validity does not prove
  attribution correctness.
- **Conclusion validity:** The clean subset is small, APKs may be grouped by
  application family, and rows within an APK are not independent. Missing
  row-level exports prevent recalculating uncertainty or conducting a
  per-family analysis. The retained summaries therefore do not support
  significance claims or population estimates beyond the documented evaluation.

## 5.8 Reproducibility status

The numerical results and experiment decisions are recorded in the PFE and
master theses, evaluation dashboards, controlled-evaluation notes, and project
history. This paper uses those records and does not rerun the experiments. The
current checkout does not include all machine-readable row exports, generated
fixture APKs, reference-database snapshot, APK/source hashes, source revisions,
or frozen run manifest needed to independently regenerate every aggregate.
Accordingly, the paper identifies the figures as documented evaluation
snapshots and does not claim independent recalculation. The PFE evaluation
chapter identifies its principal evidence snapshot as 20 June 2026 and ties it
to implementation commit `2983d54`; the thesis and evaluation records remain
the cited provenance for the reported results.
