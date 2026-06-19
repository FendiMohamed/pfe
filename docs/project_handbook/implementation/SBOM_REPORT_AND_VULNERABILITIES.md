# SBOM, Reports, and Vulnerabilities

## CycloneDX generation

Primary file: [sbom.py](../../../src/apk_sbom/sbom.py)

`build_cyclonedx_bom()` translates accepted detections into CycloneDX 1.5.
Maven components include group, artifact, version, PURL, confidence evidence,
and ambiguity properties. Native observations are represented as file
components with hashes.

Uncertain detections are excluded by default. `--include-uncertain` is useful
for analysis, but the resulting SBOM must be presented as containing uncertain
components.

## Vulnerability scanning

Primary file:
[vulnerability.py](../../../src/apk_sbom/vulnerability.py)

The scanner:

1. extracts Maven PURLs from the SBOM;
2. sends an OSV `querybatch` request;
3. optionally retrieves advisory details;
4. deduplicates IDs and aliases;
5. extracts severity information;
6. classifies findings according to component certainty.

`--no-enrich` avoids per-advisory detail requests. It is faster and reduces
network calls, but produces less descriptive output.

## Final report

Primary file: [report.py](../../../src/apk_sbom/report.py)

`generate-report` orchestrates extraction, analysis, matching, SBOM generation,
optional OSV lookup, and report rendering. It writes JSON, Markdown, and HTML.

The report includes:

- APK and manifest summary;
- forensic indicators;
- detected components and evidence;
- version uncertainty;
- SBOM and vulnerability sections;
- optional source-validation labels;
- optional report-only R8, version-band, AI, and hybrid evidence.

## Report-only means non-authoritative

Flags such as `--include-ai-r8-suggestions` and
`--include-hybrid-ai-assistance` attach diagnostics to the report. They do not
change:

- matcher scores;
- selected versions;
- CycloneDX components;
- vulnerability labels;
- source-validation metrics.

This invariant is directly tested in the AI report-only demo.

## Offline and deterministic runs

Use `--skip-osv` when:

- network access is unavailable;
- you are testing matcher behavior;
- you need deterministic local timing;
- vulnerability results are not part of the experiment.

The SBOM and report are still generated.

## Evidence

- [AI report-only demo](../../evaluation/AI_R8_REPORT_ONLY_DEMO.md)
- [Controlled evaluation and vulnerable Jackson proof](../../evaluation/CONTROLLED_EVALUATION.md)
- [Final demo checklist](../../evaluation/FINAL_DEMO_CHECKLIST.md)
