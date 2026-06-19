# Real APK Priority Target/Control Preflight

Date: 2026-06-18

Verdict: `fail-fast-large-db-report-regression`.

## Scope

The planned preflight used:

- targets: I2P and RadioDroid;
- controls: clean F-Droid, partial AntennaPod, no-Maven Mastodon, and
  limitation/boundary Organic Maps;
- evaluation-only DB:
  `data/reference_db/reference_features_real_apk_priority_versions.sqlite`;
- shared calibrated DBs kept unchanged.

The matrix stopped on the first target regression, so RadioDroid and the four
controls were not run.

## I2P Baseline

The current shared-DB source validation has:

| Checked | Confirmed | Wrong version | Missing from source |
|---:|---:|---:|---:|
| 18 | 10 | 8 | 0 |

## Broad Priority Shortlist

Settings:

- minimum package overlap: `1`;
- total reference limit: `750`;
- per-coordinate limit: `5`;
- minimum matcher score: `0.05`.

Result:

| Checked | Confirmed | Wrong version | Missing from source |
|---:|---:|---:|---:|
| 111 | 72 | 25 | 14 |

All four intended exact-source rows were recovered:

- `net.i2p:i2p@2.11.0-1`
- `net.i2p:router@2.11.0-1`
- `net.i2p.client:mstreaming@2.11.0-1`
- `net.i2p.client:streaming@2.11.0-1`

However, component output increased from `18` to `111`, and `14` emitted rows
were absent from the source dependency tree. This is a severe precision
regression.

## Strict Priority Shortlist

Settings:

- minimum package overlap: `2`;
- total reference limit: `300`;
- per-coordinate limit: `2`;
- minimum matcher score: `0.05`.

Result:

| Checked | Confirmed | Wrong version | Missing from source |
|---:|---:|---:|---:|
| 51 | 26 | 16 | 9 |

The stricter shortlist still emitted nearly three times the baseline component
count and introduced `9` source-missing rows. It also retained only two of the
four intended I2P rows (`i2p` and `router`), dropping `mstreaming` and
`streaming`.

## Decision

- Stop the target/control matrix immediately.
- Do not treat the priority DB as a production-style replacement for the
  shared calibrated DB.
- Do not promote any priority rows into the shared calibrated DB from this
  preflight.
- Keep the priority DB as an evaluation/reference-coverage asset.
- The next safe engineering task is a stronger APK-only shortlist or
  candidate-emission gate that prevents broad package-overlap false positives
  before any 106-case rerun.

## Evidence

- Broad report:
  `data/results/experiments/real-apk-priority-reference-db/report-real-i2p/report.json`
- Broad validation:
  `data/results/experiments/real-apk-priority-reference-db/source-validation/i2p/source-validation.json`
- Strict report:
  `data/results/experiments/real-apk-priority-reference-db-strict-preflight/report-real-i2p/report.json`
- Strict validation:
  `data/results/experiments/real-apk-priority-reference-db-strict-preflight/source-validation/i2p/source-validation.json`
