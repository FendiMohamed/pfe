# No-Maven-Signal Audit

Generated on 2026-06-06 from the four source-validated no-Maven-signal rows in
`docs/evaluation/NO_MAVEN_SIGNAL_AUDIT_PREP.md`.

## Summary

All four rows have source/runtime Maven dependency trees, but the APK reports
emit zero Maven SBOM components. The report-level candidate lists are not empty:
they contain weak identity candidates below the current SBOM emission threshold.
Therefore these rows are not "package missing from source" problems and should
not be fixed by forcing components into the SBOM.

The main split is:

| Bucket | Rows | Meaning |
|---|---:|---|
| AndroidX identity-coverage miss controls | 3 | Source/runtime AndroidX dependencies overlap report candidates, but candidate scores stay below emission confidence. |
| Forked-library/reference-family boundary | 1 | Source resolves forked `me.grishka.litex` UI libraries, while report candidates mostly point at upstream AndroidX families; only Gson overlaps directly. |
| True no-Maven runtime-dependency controls | 0 | None of these four source trees are dependency-free at runtime. |

These rows should stay outside source-validated emitted-version accuracy metrics
until an experiment proves that promotion improves recall without adding false
SBOM components on the current controls.

## Matcher Policy Evidence

`src/apk_sbom/matcher.py` currently labels version candidates below `0.45` as
`uncertain` unless they satisfy the obfuscation-resilient literal/package
evidence lane. Identity candidates can become low `candidate` evidence when
identity confidence is at least `0.45`, but low candidates are still not the same
as emitted SBOM components.

The observed no-Maven reports match that policy: candidate scores exist, but the
top scores are roughly `0.27` to `0.37`, with very low class/method coverage for
the source-used families.

## Per-APK Classification

| APK | Source Maven components | Report candidates | Source/candidate overlap | Top candidate evidence | Classification | Next diagnostic |
|---|---:|---:|---:|---|---|---|
| Privacy Browser 3.20.1 | 87 | 10 | 5/5 candidate coordinates overlap source | `androidx.swiperefreshlayout:swiperefreshlayout:1.0.0`, score `0.371413`; package `1.0`, class `0.055556`, method `0.231579`, opcode `0.906028`, literal `1.0` | `identity-coverage-miss` | Browser/WebView AndroidX diagnostic: inspect why package/opcode/literal evidence is present but class/method identity is too weak to emit. |
| Mastodon 2.12.3 | 20 | 10 | 1/3 candidate coordinates overlap source | `androidx.recyclerview:recyclerview:1.2.1`, score `0.288090`; direct overlap candidate is `com.google.code.gson:gson:2.8.9`, score `0.266870` | `forked-library-boundary` plus weak direct Gson identity | Fork-family/reference diagnostic for `me.grishka.litex:*`; separate Gson weak-identity check. Do not tune global AndroidX scoring from this row. |
| monocles browser 1.9.3 | 84 | 10 | 5/5 candidate coordinates overlap source | `androidx.swiperefreshlayout:swiperefreshlayout:1.0.0`, score `0.369899`; package `1.0`, class `0.055556`, method `0.226316`, opcode `0.901941`, literal `1.0` | `identity-coverage-miss` | Same browser/WebView AndroidX diagnostic as Privacy Browser; compare shared browser evidence before changing scoring. |
| Blue Square Speedometer 1.1.0 | 54 | 10 | 4/5 candidate coordinates overlap source | `androidx.startup:startup-runtime:1.1.1`, score `0.359615`; package `1.0`, class `0.2`, method `0.269231`, opcode `0.743625`, literal `0.5` | `identity-coverage-miss` | Small-app AndroidX diagnostic; useful as a low-noise control for any candidate promotion experiment. |

## Interpretation

Privacy Browser, monocles browser, and Blue Square Speedometer are likely
candidate-suppression cases rather than missing-source cases. Their source
dependency trees contain AndroidX runtime libraries, and the report candidate
lists find overlapping AndroidX coordinates. The conservative behavior comes
from weak class/method identity and scores below the emit threshold.

Mastodon is different. The source tree resolves many `me.grishka.litex:*`
coordinates, which are forked Android UI-library families. The report suggests
upstream AndroidX families and also sees the source-used `gson:2.8.9`, but the
Gson score is only `0.266870`. Treating this as a generic AndroidX no-signal
problem would be misleading; it needs fork-family/reference handling first.

## Optimization Order

1. Add an automated no-Maven diagnostic exporter that joins each report's
   candidate coordinates with the source-validation dependency tree and emits
   overlap counts, top scores, and family notes.
2. Run a scoped AndroidX no-Maven experiment on Privacy Browser, monocles
   browser, and Blue Square Speedometer. Candidate promotion must remain
   report-only until it passes current clean, partial, no-Maven, and boundary
   controls.
3. Run a separate Mastodon fork-family audit for `me.grishka.litex:*` before
   changing AndroidX scoring or reference DB promotion.
4. Keep all four rows out of emitted-version accuracy metrics unless a later
   controlled experiment emits source-confirmed Maven components without adding
   false positives.

## Dashboard Fields To Add Later

The dashboard should expose the no-Maven lane separately from emitted-version
accuracy:

| Field | Purpose |
|---|---|
| `no_maven_classification` | `identity-coverage-miss`, `forked-library-boundary`, or `true-no-signal-control`. |
| `source_candidate_overlap_count` | Number of report candidate coordinates also present in the source runtime tree. |
| `source_candidate_overlap_total` | Number of unique candidate coordinates in the report. |
| `top_candidate_score` | Highest report candidate score, even when no component is emitted. |
| `top_overlap_coordinate` | Best overlapping source/report coordinate. |
| `recommended_lane` | Next experiment lane without changing SBOM output. |

These fields make the dashboard useful for growing the reference DB while
preserving honest metrics: emitted components, candidate-only evidence,
no-Maven controls, and limitation boundaries remain visually separate.

## Generated Artifacts

The first diagnostic exporter is now `scripts/build_no_maven_signal_diagnostics.py`.
It writes:

| Artifact | Use |
|---|---|
| `data/results/evaluation/no-maven-signal-diagnostics.json` | Machine-readable dashboard input. |
| `data/results/evaluation/no-maven-signal-diagnostics.csv` | Spreadsheet/dashboard seed table. |
| `docs/evaluation/NO_MAVEN_SIGNAL_DIAGNOSTICS.md` | Human-readable generated summary. |

The scoped AndroidX report-only experiment is now
`scripts/build_no_maven_androidx_report_only_experiment.py` and the CLI command
`apk-sbom no-maven-androidx-experiment`. It writes:

| Artifact | Use |
|---|---|
| `data/results/experiments/no-maven-androidx-report-only-experiment.json` | Machine-readable report-only experiment output. |
| `docs/evaluation/NO_MAVEN_ANDROIDX_REPORT_ONLY_EXPERIMENT.md` | Human-readable experiment summary. |

Current experiment verdict:

```text
verdict -> no-maven-androidx-report-only-promising-not-promoted
AndroidX identity cases -> 3
candidate overlap rows evaluated -> 14
exact source-version candidate rows -> 10
report-only suggestions -> 6
kept suppressed rows -> 8
default/SBOM/source-validation metric changes -> 0
```

The six source-backed report-only candidates are:

| APK | Candidate |
|---|---|
| Privacy Browser 3.20.1 | `androidx.recyclerview:recyclerview:1.2.1`, `androidx.startup:startup-runtime:1.1.1`, `androidx.swiperefreshlayout:swiperefreshlayout:1.2.0` |
| monocles browser 1.9.3 | `androidx.recyclerview:recyclerview:1.2.1`, `androidx.startup:startup-runtime:1.1.1` |
| Blue Square Speedometer 1.1.0 | `androidx.startup:startup-runtime:1.1.1` |

These remain diagnostics only. They do not change emitted SBOM components or
source-validation metrics.
