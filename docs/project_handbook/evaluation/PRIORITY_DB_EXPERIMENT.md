# Priority Reference Database Experiment

## Motivation

The shared calibrated DB covered only `10.2%` of exact source dependency rows.
An all-Maven/all-versions build was too large and slow for the deadline.

The priority lane instead selected exact coordinate/version slots observed in
the 106 source trees.

## What was built

Catalog:

- `3241` observed coordinate/version slots;
- `1339` coordinates;
- `1132` repeated versions.

Recovered evaluation DB:

- `2477` bytecode-bearing components;
- `1164` coordinates;
- `725` downloaded but no-bytecode/skipped rows;
- `39` unresolved or boundary rows.

Reconciliation:

```text
2477 + 725 + 39 = 3241
```

Recovery methods included normal Maven downloads, cached complete rows, an
archive mirror for legacy JCenter artifacts, and isolated source builds for
four I2P modules and MaterialPopupMenu.

## Coverage benefit

| Metric | Shared baseline | Priority DB |
|---|---:|---:|
| Exact source-row coverage | `1231/12082` (`10.2%`) | `9657/12082` (`79.9%`) |
| Coordinate source-row coverage | `2220/12082` (`18.4%`) | `10767/12082` (`89.1%`) |

This proves the database contains many more relevant source-observed versions.
It does not prove safe unconstrained matching.

## Production-style preflight

The first target was I2P.

| Run | Emitted | Confirmed | Wrong version | Missing from source |
|---|---:|---:|---:|---:|
| Shared baseline | 18 | 10 | 8 | 0 |
| Broad package shortlist | 111 | 72 | 25 | 14 |
| Strict package shortlist | 51 | 26 | 16 | 9 |

The broad run recovered all four intended I2P 2.11.0-1 modules, but candidate
emission became severely overbroad. The strict run still emitted almost three
times the baseline and retained only two intended modules.

## Fail-fast decision

The matrix stopped before:

- RadioDroid target;
- clean F-Droid control;
- partial AntennaPod control;
- no-Maven Mastodon control;
- Organic Maps boundary control.

The regression was already sufficient to reject production promotion.

## What the result teaches

Reference coverage and candidate-emission quality are independent. A larger DB
can contain the right answer and still make an unconstrained matcher worse if
the retrieval gate admits too many related components.

## Current status

- Keep the DB as an evaluation and coverage asset.
- Do not copy its rows into the shared calibrated DB.
- Do not claim `79.9%` as APK detection accuracy.
- A stronger APK-only candidate-emission gate would be required before another
  full rerun; this work was judged not worth the current deadline cost.

## Proof

- [Priority catalog](../../evaluation/REAL_APK_PRIORITY_REFERENCE_CATALOG.md)
- [Lightweight recovery result](../../evaluation/REAL_APK_PRIORITY_LIGHTWEIGHT_RECOVERY_RESULT.md)
- [Coverage dashboard](../../evaluation/REFERENCE_DB_COVERAGE_PRIORITY_DASHBOARD.md)
- [Target/control preflight](../../evaluation/REAL_APK_PRIORITY_TARGET_CONTROL_PREFLIGHT.md)
