# Composite Family-Shortlist Default-Promotion Verification

Date: 2026-06-03.

## Decision

The balanced composite family shortlist is promoted from explicit opt-in to
default matcher/report/SBOM behavior.

The promotion remains guarded:

- keep complete version bands for any retained coordinate family
- use the balanced-context profile with independent-support rescue
- keep the shortlist margin at `0.10`
- keep `--disable-composite-family-shortlist` for pre-promotion baseline
  reproduction
- keep `--enable-composite-family-shortlist-experiment` as a compatibility alias

## Evidence Chain

| Artifact | Result |
|---|---|
| `docs/evaluation/COARSE_TO_FINE_PRUNING_DIAGNOSTICS.md` | Candidate-pressure diagnostic found `8,106` candidate-version slots and recommended staged family pruning. |
| `docs/evaluation/FAMILY_IDENTITY_PREFILTER_SIMULATION.md` | Simple package/class proxy rejected because every reducing margin lost tracked source families. |
| `docs/evaluation/COMPOSITE_FAMILY_SHORTLIST_SIMULATION.md` | Balanced dependency/literal-aware shortlist candidate removed `1,351/8,106` slots with `0` tracked source-family losses. |
| `docs/evaluation/COMPOSITE_FAMILY_SHORTLIST_LIVE_VALIDATION.md` | Live recomputation over `81/81` cases removed `1,347/8,100` reference rows with `0` tracked source-family losses and `0` reportable selected-version changes. |
| `docs/evaluation/COMPOSITE_FAMILY_SHORTLIST_OPT_IN_MATCHER_EXPERIMENT.md` | Full all-case opt-in matcher control kept default disabled, enabled the opt-in path, removed `1,347` rows, and produced `0` reportable selected-version changes. |
| `docs/evaluation/COMPOSITE_FAMILY_SHORTLIST_DEFAULT_PROMOTION_READINESS.md` | Readiness gate passed `11/11` gates and recommended an explicit default-promotion attempt with a disable flag and regression tests. |

## No-Flag Smoke

The promoted default path was exercised without an enable flag:

```text
docker compose run --rm apk-sbom python -m apk_sbom.cli match-apk \
  data/test_apks/generated-gson-2-8-6-clear.apk \
  --db-path data/reference_db/reference_features_phase4_multiscale_calibrated_combined.sqlite \
  --top 10 --min-score 0.05
```

The pre-promotion baseline was reproduced with the disable flag:

```text
docker compose run --rm apk-sbom python -m apk_sbom.cli match-apk \
  data/test_apks/generated-gson-2-8-6-clear.apk \
  --db-path data/reference_db/reference_features_phase4_multiscale_calibrated_combined.sqlite \
  --top 10 --min-score 0.05 \
  --disable-composite-family-shortlist
```

Result:

| Run | Shortlist enabled | Status | Rows removed | Decision rows | Top selected version |
|---|---|---|---:|---:|---|
| no flag | `true` | `enabled` | `31` | `28` | `2.8.6` |
| disable flag | `false` | `disabled` | `0` | `44` | `2.8.6` |

Smoke outputs:

- `data/results/experiments/composite-family-shortlist-default-promoted/generated-gson-default-match.json`
- `data/results/experiments/composite-family-shortlist-default-promoted/generated-gson-disabled-match.json`

## Verification

| Check | Result |
|---|---|
| Focused Docker promotion tests | `56 passed` |
| Full Docker `pytest -q` | `201 passed` |
| Local `python -m compileall src scripts tests` | passed |
| Docker `python -m compileall src scripts tests` | passed |
| `git diff --check` | passed with normal LF/CRLF warnings only |

## Next Work

Keep the default promotion narrow and measured. The next P2 step is to continue
candidate-pruning work only where it adds new evidence beyond the promoted
family shortlist, such as class-subset or class-correspondence diagnostics, then
move to the limited optimization-aware logic track if the pruning lane is stable.
