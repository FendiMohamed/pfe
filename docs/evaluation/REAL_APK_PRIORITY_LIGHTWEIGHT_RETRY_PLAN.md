# Real APK Priority Lightweight Retry Plan

This is a bounded, value-first recovery pass. It retries only small plausible Google/JCenter artifacts and defers heavy, metadata-only, alias, and exhausted repository boundaries.

## Summary

- Remaining after local existing-DB recovery: `63`
- Lightweight retry slots: `30`
- JCenter retry slots: `25`
- Google Maven retry slots: `5`
- Deferred boundary slots: `33`

## Deferred Classes

- `defer-alias-version`: `12`
- `defer-exhausted-jitpack`: `3`
- `defer-heavy-or-parent-boundary`: `4`
- `defer-no-jvm-bytecode-boundary`: `10`
- `defer-special-repository-boundary`: `4`

## Guardrail

Only `data/reference_db/reference_features_real_apk_priority_versions.sqlite` may receive recovered rows. The shared calibrated DB remains unchanged.
