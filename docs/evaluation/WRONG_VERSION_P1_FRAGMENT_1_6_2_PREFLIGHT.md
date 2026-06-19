# Wrong-Version P1 Fragment 1.6.2 Preflight

Date: 2026-06-18

Verdict: `scoped-preflight-passed-experiment-only`.

Adding only `androidx.fragment:fragment@1.6.2` to an isolated copy of the
current Phase 4 calibrated DB makes all 10 affected source-backed rows select
their source-resolved version. The representative clean, partial, no-Maven,
and boundary controls do not regress in fresh paired base-versus-experiment
comparisons.

The result is not robust exact-version evidence: every target remains a
low-confidence version candidate, the 1.6.2-versus-1.6.1 gaps are microscopic,
and neither version has matched version-unique APK evidence. Keep the row
experiment-only and keep the shared calibrated DB unchanged.

## Scope

- Coordinate: `androidx.fragment:fragment`
- Existing selected version: `1.6.1`
- Source-backed candidate: `1.6.2`
- Affected source-backed rows: `10`
- Isolated addition: exactly one component row,
  `androidx.fragment:fragment@1.6.2`
- Base DB:
  `data/reference_db/reference_features_phase4_multiscale_calibrated_combined.sqlite`
- Experiment DB:
  `data/reference_db/reference_features_wrong_version_fragment_1_6_2.sqlite`

Historical dashboard reports were generated with older reference DBs, so the
promotion decision uses fresh paired reports from the current Phase 4 base and
the isolated experiment DB.

## Target Coverage

| Case | Selected | Status | Confidence | Gap over 1.6.1 |
|---|---:|---|---:|---:|
| Calliope mini 2.0.9 | 1.6.2 | candidate | 0.796690 | 0.000425 |
| FTPClient 3.0.1 | 1.6.2 | candidate | 0.796818 | 0.000426 |
| LinkDroid for Linkwarden 2.1.9 | 1.6.2 | candidate | 0.795276 | 0.000426 |
| MedTimer 1.22.18 | 1.6.2 | candidate | 0.795270 | 0.000426 |
| Password Master 1.5.1 | 1.6.2 | candidate | 0.798164 | 0.000426 |
| SimpleLogin Anti-spam 1.22.0 | 1.6.2 | candidate | 0.798040 | 0.000425 |
| Simple Time Tracker 1.57 | 1.6.2 | candidate | 0.673117 | 0.000427 |
| VLC Android 3.7.1 | 1.6.2 | candidate | 0.794441 | 0.000428 |
| Working Time Account 2.11.012 | 1.6.2 | candidate | 0.485258 | 0.000006 |
| yetCalc 2.0.8 | 1.6.2 | candidate | 0.794366 | 0.000424 |

Result: `10/10` affected rows select 1.6.2. All remain explicitly ambiguous
with 1.6.1.

## Fresh Paired Target Reports

| Case | Current base | Isolated 1.6.2 DB | Delta |
|---|---|---|---|
| SimpleLogin | 22 components; 9 confirmed; 13 mismatches | 22 components; 10 confirmed; 12 mismatches | +1 confirmed; -1 mismatch |
| yetCalc | 17 components; 6 confirmed; 11 mismatches | 17 components; 7 confirmed; 10 mismatches | +1 confirmed; -1 mismatch |

Only the Fragment result changes in these two sampled full reports.

## Representative Controls

| Control | Lane | Current base | Isolated 1.6.2 DB | Result |
|---|---|---|---|---|
| F-Droid 1.23.2 | clean | 23/23 confirmed; Fragment 1.6.1 | 23/23 confirmed; Fragment 1.6.1 | unchanged |
| AntennaPod 3.11.4 | partial | 20 components; 19 confirmed; Fragment 1.8.9 | same | unchanged |
| Privacy Browser 3.20.1 | no-Maven | 0 Maven components | 0 Maven components | unchanged |
| Organic Maps 2026.05.08-4 | boundary | 13 Maven components; Fragment 1.8.9 | identical component set | unchanged |

Sampled control regressions: `0`.

## Decision

- Keep `androidx.fragment:fragment@1.6.2` in the isolated experiment DB only.
- Do not claim robust exact-version separation between 1.6.1 and 1.6.2.
- Do not change either shared calibrated DB from this experiment.
- Revisit promotion only with independent version evidence or a wider
  current-base control matrix that preserves the zero-regression result.

## Integrity

- Shared calibrated DB SHA-256:
  `DB989F99E0893B350A3CD59B9AEB1ED98903500DF4E8254153A55A3989B24ECA`
- Phase 4 calibrated base SHA-256:
  `2F613CB133F6F0F746C40C80F53EFC9C5894928541CAEC320A4BF024D63206A9`
- Isolated Fragment experiment DB SHA-256:
  `390C345DB31F935F65F648ABABF9E2D1C5E8AB44AAF5C1CB5525955AD0D87E89`

## Evidence

- DB build:
  `data/results/experiments/wrong-version-p1-fragment-1-6-2/db-build.json`
- Fresh target and clean-control experiment:
  `data/results/experiments/wrong-version-p1-fragment-1-6-2/summary.json`
- Fresh current-base counterpart:
  `data/results/experiments/wrong-version-p1-fragment-1-6-2-current-base/summary.json`
- Partial-control pair:
  `data/results/experiments/wrong-version-p1-fragment-1-6-2-controls-base/summary.json`
  and
  `data/results/experiments/wrong-version-p1-fragment-1-6-2-controls-experiment/summary.json`
- No-Maven-control pair:
  `data/results/experiments/wrong-version-p1-fragment-1-6-2-no-maven-base/summary.json`
  and
  `data/results/experiments/wrong-version-p1-fragment-1-6-2-no-maven-experiment/summary.json`
- Boundary-control pair:
  `data/results/experiments/wrong-version-p1-fragment-1-6-2-boundary-base/summary.json`
  and
  `data/results/experiments/wrong-version-p1-fragment-1-6-2-boundary-experiment/summary.json`
