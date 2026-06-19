# Reference Databases and Ground Truth

## Reference database

The matcher needs examples of known library releases. The reference pipeline:

1. downloads a Maven JAR or AAR;
2. converts its bytecode to DEX with D8;
3. extracts the same features used for APK analysis;
4. stores them in SQLite under a coordinate and version.

The DB contains feature tables for components, packages, classes, methods,
opcodes, n-grams, dependencies, literals, API references, multi-scale
diagnostics, and POM dependency metadata.

## Closed-world effect

If version `X` is absent from the DB, the matcher cannot rank it directly. It
may choose a nearby release, emit an ambiguity, or miss the component.

Reference coverage and matching accuracy are therefore distinct:

- **reference coverage** asks whether the known source coordinate/version is in
  the DB;
- **matcher recovery** asks whether APK evidence selects it correctly.

## Ground truth types

### Controlled ground truth

The project builds APK fixtures with known dependencies and transformations.
This gives exact expected versions and controlled R8 conditions.

### Source-validated real APK ground truth

For open-source apps, Gradle dependency trees are compared with emitted SBOM
components. This validates emitted rows but does not prove recall of every
source dependency.

### Boundary evidence

Some APKs expose native, hidden, protected, or no-Maven behavior that cannot be
fairly scored as ordinary Maven version detection. They remain visible in
separate limitation buckets.

## Shared versus experimental DBs

The shared calibrated DB supports the stable MVP. New rows or new DBs are
tested in isolated files first. Promotion requires:

- target improvement;
- no clean or partial regressions;
- no-Maven and boundary controls;
- acceptable runtime and candidate volume;
- reproducible proof artifacts.

The 2477-component priority DB improved source-row coverage to `79.9%` but
failed its production-style preflight because package-based candidate emission
created too many false positives. It remains evaluation-only.

## Safety warning

`extract-reference-features --reset` deletes and recreates the selected SQLite
DB. Never point it at the shared calibrated DB during an experiment.

## Evidence

- [Reference feature implementation](../../../src/apk_sbom/reference_features.py)
- [Coverage-first dashboard](../../evaluation/REFERENCE_DB_COVERAGE_FIRST_DASHBOARD.md)
- [Priority coverage dashboard](../../evaluation/REFERENCE_DB_COVERAGE_PRIORITY_DASHBOARD.md)
- [Priority preflight](../../evaluation/REAL_APK_PRIORITY_TARGET_CONTROL_PREFLIGHT.md)
- [Safe experiment rules](../operations/SAFE_EXPERIMENT_RULES.md)
