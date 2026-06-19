# Real APK Priority Lightweight Recovery Result

Date: 2026-06-18

Verdict: `bounded-lightweight-recovery-complete`.

## Result

- Priority catalog slots: `3241`
- Stored bytecode components before this pass: `2424`
- Exact rows recovered from the existing demo-v2 feature DB: `29`
- New Google Maven artifact downloaded, converted, and stored:
  `com.android.support:exifinterface@28.0.0`
- Archived JCenter mirror artifacts recovered and stored: `18`
- Exact-source I2P modules built, converted, and stored: `4`
- Exact-tag MaterialPopupMenu artifacts built, converted, and stored: `1`
- Stored bytecode components after this pass: `2477`
- Stored coordinates after this pass: `1164`
- Downloaded no-bytecode/skipped rows: `725`
- Remaining unresolved/boundary rows: `39`
- Reconciliation: `2477 + 725 + 39 = 3241`

## Coverage Impact

- Exact source-version row coverage: `9657/12082` (`79.9%`), previously
  `9652/12082` (`79.9%`)
- Coordinate row coverage: `10767/12082` (`89.1%`), previously
  `10762/12082` (`89.1%`)

## Lightweight Network Gate

The bounded pass attempted only small plausible artifacts:

- Archived JCenter AAR: `25/25` returned 404.
- Archived JCenter JAR: `25/25` returned 404.
- Aliyun JCenter archive AAR: `18/25` downloaded, converted, and stored.
- Google Maven AAR: `1/5` downloaded; the recovered row converted and stored.
- Four Accompanist/DashClock Google rows remained 404.

No heavy React conversion was attempted.

## Exact-Source I2P Recovery

The exact F-Droid source tarball for I2P `2.11.0` was already available with
SHA-256
`dded22feee758ab414b3d2bd44e95f5f33764b84c5d0de8abd59534409c8d3f2`.
The isolated source copy reports release `2.11.0`, build `1`, producing the
source-observed Maven version `2.11.0-1`.

Docker Gradle `8.13` built only the four required modules:

- `net.i2p:i2p@2.11.0-1`
- `net.i2p:router@2.11.0-1`
- `net.i2p.client:mstreaming@2.11.0-1`
- `net.i2p.client:streaming@2.11.0-1`

All four JARs converted through D8 and stored successfully. The resulting rows
contain `1594` classes and `14946` methods in total. The staging script and
hash manifest are at
`scripts/stage_real_apk_priority_i2p_source_build.py` and
`data/results/experiments/real-apk-priority-i2p-source-build/source-build-manifest.json`.

## Exact-Tag MaterialPopupMenu Recovery

The remaining JitPack row
`com.github.zawadz88.materialpopupmenu:material-popup-menu@3.4.0` has an exact
upstream tag at commit
`ab65b75faf7b8bdebf1bc29c645e1950eeb55233`. Its old build depended on retired
Bintray publishing infrastructure, so the isolated validation copy removed
publishing/docs-only plugins, replaced JCenter with Maven Central, and used the
installed Android 29 SDK. The library sources and runtime dependencies were
unchanged.

The build produced a bytecode-bearing AAR with SHA-256
`9534448c2ef20e1cc76b74272955abd406ac3f3eece5ccdd2f8c4b36b9748058`.
D8 conversion succeeded and feature extraction stored `31` classes and `210`
methods. See
`docs/evaluation/REAL_APK_PRIORITY_MATERIAL_POPUP_MENU_SOURCE_BUILD_RESULT.md`.

## Remaining Boundaries

The 39 remaining rows are not a homogeneous conversion queue:

- alias strings recorded as versions;
- metadata-only modern `kotlin-stdlib-common` rows;
- heavy or repository-local React rows;
- two exhausted JitPack coordinates without exact available build evidence;
- seven old JCenter artifacts that remained 404 even through the mirror.

Fifteen remaining rows occur in more than one APK and 24 are single-observed.
The repeated set is nearly all alias or metadata-only boundaries. These rows
should not be counted as failed bytecode conversions.

## Guardrail

Only
`data/reference_db/reference_features_real_apk_priority_versions.sqlite`
changed. The shared calibrated databases remain unchanged.

## Evidence

- Existing-DB recovery:
  `data/results/evaluation/real-apk-priority-existing-db-recovery.json`
- Lightweight plan:
  `data/results/evaluation/real-apk-priority-lightweight-retry-plan.json`
- Coverage dashboard:
  `docs/evaluation/REFERENCE_DB_COVERAGE_PRIORITY_DASHBOARD.md`
