# Low-Risk Source-Version Reference Experiment

This experiment tests whether missing source-used versions from the low-risk APK batch can be added safely to the shared calibrated reference database.

The shared DB remains unchanged unless a candidate improves its target APK without regressing current controls.

## Motivation

The low-risk APK batch removed source/build complexity: each selected app has a matching F-Droid source tarball, no native ABI, a modern Gradle root, a captured runtime dependency tree, and completed source validation.

The remaining version mismatches are therefore useful reference-coverage evidence rather than APK acquisition blockers.

## Full Experiment

Experiment DB: `data/reference_db/reference_features_low_risk_source_experiment.sqlite`

Candidate versions:

- `androidx.appcompat:appcompat@1.2.0`
- `androidx.appcompat:appcompat@1.6.1`
- `androidx.core:core@1.3.0`
- `androidx.fragment:fragment@1.3.6`
- `androidx.lifecycle:lifecycle-runtime@2.1.0`
- `androidx.lifecycle:lifecycle-runtime@2.5.1`
- `androidx.lifecycle:lifecycle-viewmodel@2.5.1`
- `androidx.recyclerview:recyclerview@1.0.0`
- `org.jetbrains.kotlinx:kotlinx-coroutines-android@1.6.1`
- `org.jetbrains.kotlinx:kotlinx-coroutines-android@1.6.4`

| Target | Baseline | Full experiment | Outcome |
|---|---:|---:|---|
| Stopwatch | 4/5 confirmed | 4/5 confirmed | unchanged |
| Bubble | 1/7 confirmed | 6/7 confirmed | improved |
| Audio Source | 0/3 confirmed | 3 confirmed, 1 new mismatch | improved but expanded output exposes another older source-version gap |
| Blue Square Speedometer | 0/0 no-Maven-signal | 0/1 confirmed | regressed: new false Maven version claim |

The full expansion is not promotable. It also regresses existing controls including F-Droid, OpenTracks, NewPipe, AntennaPod, KDE Connect, and Aegis.

## Narrow Promotion Checks

Two candidates looked promising when isolated:

| Candidate | Target benefit | Control result | Decision |
|---|---|---|---|
| `androidx.recyclerview:recyclerview@1.0.0` | Bubble improves from 1/7 to 2/7 confirmed | NewPipe regresses from 10/11 to 9/11 confirmed | keep experiment-only |
| `androidx.lifecycle:lifecycle-runtime@2.1.0` | Audio Source improves from 0/3 to 1/3 confirmed | F-Droid, NewPipe, KDE Connect, and Aegis regress | keep experiment-only |

## Interpretation

Growing the reference DB is necessary for credibility, but the current bytecode matcher cannot safely mix every old and new AndroidX version globally. Closely related versions can become stronger candidates for unrelated APKs.

The correct next step is not to freeze reference growth. It is to keep source-used versions available in experiment DBs and improve version-band discrimination before global promotion.

`docs/evaluation/LOW_RISK_VERSION_BAND_DIAGNOSTICS.md` now makes that conflict explicit per coordinate. The full experiment resolves 9 target mismatch rows but introduces 13 new mismatch rows elsewhere. AppCompat, Core, Fragment, Lifecycle Runtime, and Lifecycle ViewModel each show target benefit plus cross-app conflict. RecyclerView and Lifecycle Runtime also fail their narrow current-control gates, so no reference version from this experiment is promoted.

`docs/evaluation/LOW_RISK_VERSION_BAND_TRIGGER_DIAGNOSTICS.md` adds an opt-in AppCompat/Core old-version-steal guard. It flags 7/13 newly introduced mismatch rows for confidence downgrade while blocking 0/9 resolved target rows. This is promising diagnostic evidence, not a production promotion: the guard does not guess replacement versions, does not change default matcher output, and leaves Lifecycle out until its public-vs-Android artifact-family evidence is separated safely.

`docs/evaluation/LIFECYCLE_FAMILY_SEPARATION_DIAGNOSTICS.md` handles that Lifecycle follow-up as a separate opt-in diagnostic. It inspects 5 introduced Lifecycle rows: F-Droid and Aegis have source-version-backed Android-target family evidence suitable for downgrading the public-coordinate claim, NewPipe runtime remains a patch near-tie, and Blue Square plus NewPipe ViewModel stay unresolved. It blocks 0/3 resolved target Lifecycle rows and still does not force replacement versions.

Reports can attach both diagnostics with `generate-report --include-version-band-experiments`. The attachment is report-only: JSON/Markdown/HTML show matching downgrade suggestions, and CycloneDX receives application-level metadata properties. The report still emits the original components and versions.

`docs/evaluation/LOW_RISK_VERSION_BAND_ANNOTATED_REPORTS.md` records the real report check for Stopwatch, Bubble, Audio Source, and Blue Square Speedometer. The annotated report folders preserve the same detected components and CycloneDX components as the baseline low-risk reports; Stopwatch receives one matching AppCompat downgrade annotation.

## Artifacts

- Full target summary: `data/results/experiments/low-risk-source-versions-target/target-summary.md`
- Full control summary: `data/results/experiments/low-risk-source-versions-controls/controls-summary.md`
- RecyclerView target summary: `data/results/experiments/low-risk-source-versions-recyclerview-target/target-summary.md`
- RecyclerView control summary: `data/results/experiments/low-risk-source-versions-recyclerview-controls/controls-summary.md`
- Lifecycle Runtime target summary: `data/results/experiments/low-risk-source-versions-lifecycle-runtime-2-1-0-target/target-summary.md`
- Lifecycle Runtime control summary: `data/results/experiments/low-risk-source-versions-lifecycle-runtime-2-1-0-controls/controls-summary.md`
- Version-band diagnostic: `docs/evaluation/LOW_RISK_VERSION_BAND_DIAGNOSTICS.md`
- Version-band diagnostic JSON: `data/results/experiments/low-risk-version-band-diagnostics.json`
- Scoped trigger diagnostic: `docs/evaluation/LOW_RISK_VERSION_BAND_TRIGGER_DIAGNOSTICS.md`
- Scoped trigger diagnostic JSON: `data/results/experiments/low-risk-version-band-trigger-diagnostics.json`
- Lifecycle family diagnostic: `docs/evaluation/LIFECYCLE_FAMILY_SEPARATION_DIAGNOSTICS.md`
- Lifecycle family diagnostic JSON: `data/results/experiments/lifecycle-family-separation-diagnostics.json`
- Annotated low-risk reports: `docs/evaluation/LOW_RISK_VERSION_BAND_ANNOTATED_REPORTS.md`
