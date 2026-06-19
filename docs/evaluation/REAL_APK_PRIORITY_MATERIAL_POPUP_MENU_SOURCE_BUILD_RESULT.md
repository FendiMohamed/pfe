# Real APK Priority MaterialPopupMenu Source Build Result

Date: 2026-06-18

Verdict: `exact-tag-source-artifact-recovered`.

## Result

The remaining JitPack row
`com.github.zawadz88.materialpopupmenu:material-popup-menu@3.4.0` maps to the
exact upstream tag `3.4.0` at commit
`ab65b75faf7b8bdebf1bc29c645e1950eeb55233`.

The original build was blocked by retired Bintray publishing dependencies. In
the isolated validation copy, publishing/docs-only plugins were removed,
JCenter was replaced by Maven Central, and the installed Android 29 SDK was
used. Library sources and runtime dependency declarations were unchanged.

The build produced a bytecode-bearing AAR:

- SHA-256:
  `9534448c2ef20e1cc76b74272955abd406ac3f3eece5ccdd2f8c4b36b9748058`
- D8 conversion: `converted`
- Stored classes: `31`
- Stored methods: `210`

The priority DB now has `2477` components / `1164` coordinates. The catalog
reconciles as `2477 stored + 725 no-bytecode/skipped + 39 unresolved = 3241`.

## Guardrail

The row was appended only to
`data/reference_db/reference_features_real_apk_priority_versions.sqlite`.
Shared calibrated databases were not modified.

## Evidence

- Build/source manifest:
  `data/results/experiments/real-apk-priority-material-popup-menu-source-build/source-build-manifest.json`
- Converted DEX metadata:
  `data/results/experiments/real-apk-priority-material-popup-menu-source-build/dex`
