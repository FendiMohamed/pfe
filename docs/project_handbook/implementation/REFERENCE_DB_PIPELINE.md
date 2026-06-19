# Reference Database Pipeline

## Purpose

The reference DB is the known-library side of matching. It stores features from
specific Maven releases so APK evidence can be compared against reproducible
coordinate/version examples.

## Step 1: select versions

`expand-reference-config` reads a coordinate catalog and Maven metadata. It can
select the latest stable releases or every published release. Prereleases are
excluded unless explicitly enabled.

Large “all versions” catalogs can contain tens of thousands of slots. They are
valuable for coverage research but expensive to download, convert, extract,
and safely search.

## Step 2: download Maven artifacts

Primary file:
[maven_downloader.py](../../../src/apk_sbom/maven_downloader.py)

`download-maven` stores:

- JAR or AAR bytes;
- metadata JSON;
- SHA-256 hashes;
- POM information and declared dependencies where available.

Existing complete artifacts are reused unless `--force` is supplied.

## Step 3: convert to DEX

Primary file:
[reference_converter.py](../../../src/apk_sbom/reference_converter.py)

D8 converts JAR bytecode to DEX. For AAR files, the converter extracts
`classes.jar` first. Conversion records distinguish:

- converted;
- already existing;
- skipped, such as no bytecode;
- failed.

A POM-only or resource-only artifact is not an honest DEX target.

## Step 4: extract and store features

Primary file:
[reference_features.py](../../../src/apk_sbom/reference_features.py)

The extractor upserts a component by coordinate and version, clears its old
child feature rows, and writes the current feature set transactionally.

Major tables cover:

- components;
- packages, classes, methods;
- opcodes and opcode n-grams;
- class dependencies and dependency shapes;
- literals and API references;
- basic blocks, call chains, class neighbors, field operations, literal
  context;
- POM dependencies.

## Reproducibility artifacts

The pipeline retains metadata beside each stage. This matters because a DB row
without its source artifact and conversion record is difficult to audit.

## Shared and experimental DB policy

Never grow the shared calibrated DB directly during exploratory work. Use a
new SQLite path or a filtered copy, run target and control gates, and only then
consider promotion.

The shared DB has deliberately remained unchanged during the Fragment 1.6.2
and priority DB experiments.

## Read next

- [Reference DB command reference](../commands/REFERENCE_DB_CLI_REFERENCE.md)
- [Build a reference DB workflow](../workflows/BUILD_AND_VALIDATE_WORKFLOWS.md)
- [Reference DB and ground truth](../concepts/REFERENCE_DB_AND_GROUND_TRUTH.md)
