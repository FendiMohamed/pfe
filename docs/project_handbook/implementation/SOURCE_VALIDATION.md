# Source Validation

Primary file:
[source_validation.py](../../../src/apk_sbom/source_validation.py)

## Purpose

For an open-source APK, a Gradle dependency tree provides external evidence
about coordinates and resolved versions. Source validation compares that tree
with components already emitted in a CycloneDX SBOM.

## Inputs

- an MVP-generated CycloneDX JSON SBOM;
- a Gradle dependency output, commonly a runtime classpath tree;
- optional extra candidate coordinates to inspect.

## Statuses

Each emitted Maven component can be classified as:

- **confirmed**: coordinate and version agree;
- **version mismatch**: coordinate exists but resolved source version differs;
- **missing**: emitted coordinate is not found in the supplied tree.

The exact labels in generated artifacts should be used when citing results.

## Critical denominator rule

Source validation checks emitted SBOM rows. Therefore:

```text
confirmed emitted rows / emitted Maven rows
```

is an emitted-version confirmation rate.

It is not:

```text
all source dependencies detected / all source dependencies
```

The latter requires a source-tree denominator and separate reference-coverage
analysis. The project now provides that through coverage-first dashboards.

## Why source and APK views differ

A Gradle tree can include:

- metadata-only artifacts;
- BOMs and platforms;
- compile/runtime modules whose bytecode is absent;
- dependencies removed by shrinking;
- aliases or relocated coordinates.

An APK can also contain repackaged or vendored code that has no direct row in
the selected source tree.

## Command shape

```powershell
docker compose run --rm apk-sbom python -m apk_sbom.cli validate-source-deps `
  --sbom data/results/example/sbom.cdx.json `
  --dependency-tree data/test_apks/real/example/dependencies.txt `
  --output-dir data/results/example/source-validation
```

Use repeatable `--candidate group:artifact@version` for focused checks that are
not already emitted in the SBOM.

## Evidence

- [Real APK source-validation dashboard](../../evaluation/REAL_APK_SOURCE_VALIDATION_DASHBOARD_REPORT.md)
- [Thesis evaluation tables](../../evaluation/THESIS_EVALUATION_TABLES.md)
- [Coverage-first dashboard](../../evaluation/REFERENCE_DB_COVERAGE_FIRST_DASHBOARD.md)
