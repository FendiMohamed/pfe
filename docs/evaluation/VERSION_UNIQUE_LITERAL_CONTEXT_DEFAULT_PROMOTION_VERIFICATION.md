# Version-Unique Literal-Context Default Promotion Verification

Date: 2026-06-02.

## Decision

The guarded version-unique literal/context reranker is promoted from explicit
opt-in to default matcher/report/SBOM behavior.

The rule remains narrow:

- require at least `2` matched version-unique literal/context features
- require unique literal/context score `>=0.10`
- require advantage `>=0.05`
- require the candidate to stay within `0.020` raw score of the raw-score leader
- keep `--disable-version-unique-literal-context-reranker` for pre-promotion
  baseline reproduction

## Evidence Chain

| Artifact | Result |
|---|---|
| `docs/evaluation/LITERAL_CONTEXT_VERSION_TIE_DIAGNOSTICS.md` | Raw literal/context ranking rejected: `0` improvements, `2` regressions. |
| `docs/evaluation/VERSION_UNIQUE_LITERAL_CONTEXT_DIAGNOSTICS.md` | Broad one-match version-unique rule rejected: `2` improvements, `2` regressions. |
| `docs/evaluation/VERSION_UNIQUE_LITERAL_CONTEXT_PROMOTION_CANDIDATE.md` | Stricter `>=2` match gate keeps `1` improvement and filters all `3` one-match suggestions. |
| `docs/evaluation/VERSION_UNIQUE_LITERAL_CONTEXT_CURRENT_CONTROL_VALIDATION.md` | Same-DB report/source-validation slice passes: VLC improves `6/26 -> 7/26`; AntennaPod and OsmAnd stay unchanged. |
| `docs/evaluation/VERSION_UNIQUE_LITERAL_CONTEXT_DEFAULT_PROMOTION_READINESS.md` | Broad readiness pass covers `24` controlled and `224` real source-validated rows; all `8` gates pass. |

## No-Flag Real Smoke

The promoted default path was exercised without an enable flag:

```text
docker compose run --rm apk-sbom python -m apk_sbom.cli generate-report \
  data/test_apks/real/vlc-android/vlc-android.apk \
  --output-dir data/results/experiments/version-unique-literal-context-default-promoted/report-real-vlc-android \
  --db-path data/reference_db/reference_features_phase4_multiscale_calibrated_combined.sqlite \
  --top 30 --skip-osv

docker compose run --rm apk-sbom python -m apk_sbom.cli validate-source-deps \
  --sbom data/results/experiments/version-unique-literal-context-default-promoted/report-real-vlc-android/sbom.cdx.json \
  --dependency-tree data/results/source-validation/vlc-android/releaseRuntimeClasspath.txt \
  --output-dir data/results/experiments/version-unique-literal-context-default-promoted/source-validation/vlc-android
```

Result:

| App | Components | Confirmed | Mismatches | Missing |
|---|---:|---:|---:|---:|
| VLC Android `3.7.1` | `26` | `7` | `19` | `0` |

The no-flag report records
`version_unique_literal_context_reranker_enabled=true` and emits
`androidx.recyclerview:recyclerview@1.3.2` as source-confirmed. The report
explains that `1.3.2` replaces raw-score leader `1.2.1` because it has `7/9`
matched version-unique literal/context features while remaining inside the
guarded raw-score margin.

## Verification

| Check | Result |
|---|---|
| Local `python -m compileall src scripts tests` | passed |
| Focused Docker promotion tests | `50 passed` |
| Full Docker `pytest -q` | `178 passed` |
| Docker `python -m compileall src scripts tests` | passed |
| `git diff --check` | passed with normal LF/CRLF warnings only |

## Next Work

Keep the promotion narrow. The systematic guarded reference-DB promotion
workflow is now generated at
`docs/evaluation/GUARDED_REFERENCE_DB_PROMOTION_WORKFLOW.md`. The next
optimization track is P2 coarse-to-fine candidate-pruning diagnostics: measure
candidate-set width, identify noisy close-version comparisons, and propose a
diagnostic-only pruning layer before changing matcher scoring.
