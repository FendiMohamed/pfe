# Real APK Priority I2P Source Build Result

Date: 2026-06-18

Verdict: `four-exact-source-modules-recovered`.

## Result

The exact F-Droid source tarball for I2P `2.11.0` was verified at SHA-256
`dded22feee758ab414b3d2bd44e95f5f33764b84c5d0de8abd59534409c8d3f2`.
The source reports release `2.11.0`, build `1`, matching the four unresolved
runtime rows at Maven version `2.11.0-1`.

Docker Gradle `8.13` successfully built:

| Coordinate | Classes | Methods |
|---|---:|---:|
| `net.i2p:i2p@2.11.0-1` | 570 | 5166 |
| `net.i2p:router@2.11.0-1` | 944 | 8933 |
| `net.i2p.client:mstreaming@2.11.0-1` | 17 | 121 |
| `net.i2p.client:streaming@2.11.0-1` | 63 | 726 |

All four JARs converted through D8 and were stored in
`data/reference_db/reference_features_real_apk_priority_versions.sqlite`.
The DB now has `2476` components / `1163` coordinates, with zero duplicate
coordinate-version rows, a passing foreign-key check, and `integrity_check=ok`.

## Coverage Impact

- Exact source-version rows: `9656/12082` (`79.9%`)
- Coordinate-covered source rows: `10766/12082` (`89.1%`)
- Remaining catalog boundaries: `40`
- Reconciliation: `2476 stored + 725 no-bytecode/skipped + 40 unresolved = 3241`

## Guardrail

The shared calibrated databases were not modified. The four rows remain in the
evaluation-only real-APK priority DB.

## Reproduction Evidence

- Staging script:
  `scripts/stage_real_apk_priority_i2p_source_build.py`
- Source/JAR hash manifest:
  `data/results/experiments/real-apk-priority-i2p-source-build/source-build-manifest.json`
- Converted DEX metadata:
  `data/results/experiments/real-apk-priority-i2p-source-build/dex`
