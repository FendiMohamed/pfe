# SBOM, CycloneDX, PURL, OSV, and CVEs

## SBOM

A Software Bill of Materials lists software components and relevant evidence.
For this project, the principal components are detected Maven libraries and
observed native files.

An APK-derived SBOM is an observation of compiled evidence. It is not identical
to a source-generated Gradle dependency lock file.

## CycloneDX

The project emits CycloneDX 1.5 JSON. CycloneDX provides a standard schema for:

- components;
- versions;
- package identifiers;
- hashes;
- properties and evidence;
- relationships and vulnerability-tool interoperability.

## Package URL

A Maven Package URL looks like:

```text
pkg:maven/com.google.code.gson/gson@2.10.1
```

It gives vulnerability services a normalized ecosystem, namespace, artifact,
and version. A PURL is only as reliable as the underlying identification.

## CVE, OSV, EPSS, and KEV

- **CVE** is a public vulnerability identifier.
- **OSV** provides ecosystem-aware vulnerability queries and is the service
  used directly by the MVP.
- **EPSS** estimates exploitation probability.
- **KEV** lists vulnerabilities known to be exploited.

The core pipeline queries OSV. Other sources can enrich analysis, but they are
not substitutes for correct component identity and version.

## Confirmed versus potential vulnerabilities

The project avoids this invalid chain:

```text
weak version guess -> exact PURL -> definite CVE
```

Instead:

- strong identity plus exact/high version confidence can support a confirmed
  vulnerability match;
- uncertain versions produce potential findings;
- source validation can confirm, mismatch, or mark a component missing from the
  supplied dependency tree.

## Why version ambiguity matters

If candidates `1.6.1` and `1.6.2` are indistinguishable, their vulnerability
status may differ. Selecting one silently can create either a false alarm or a
missed advisory. The SBOM therefore carries confidence and ambiguity evidence.

## Code and proof

- [sbom.py](../../../src/apk_sbom/sbom.py)
- [vulnerability.py](../../../src/apk_sbom/vulnerability.py)
- [report.py](../../../src/apk_sbom/report.py)
- [Controlled evaluation and vulnerable Jackson proof](../../evaluation/CONTROLLED_EVALUATION.md)
- [Final demo package](../../evaluation/DEMO_FINAL_V2_PACKAGE.md)
