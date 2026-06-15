# Version Uncertainty Reporting

This note records the generic report wording improvement for near-tie and boundary version evidence.

## Status

`generate-report` now writes a `version_uncertainty_summary` block to `report.json` and a matching "Version Uncertainty Summary" section to Markdown and HTML reports.

The section is report-only. It explains existing matcher decisions and does not change matcher scoring, selected versions, emitted SBOM components, vulnerability labels, or source-validation metrics.

## Categories

The report groups existing version-decision evidence into stable labels:

- `explicit-version-ambiguity`: the matcher already emitted an ambiguity reason or ambiguous version set.
- `near-tie`: sibling versions have very close scores.
- `low-confidence-version`: the selected version is a low-confidence or candidate-level claim.
- `uncertain-version`: the matcher could not make a confident version-level claim.
- `single-reference-boundary`: only one reference version was available for the coordinate.
- `policy-selected-version`: the selected version came from an existing guarded selection reason.

## Smoke Evidence

Smoke report:

- JSON: `data/results/experiments/version-uncertainty-reporting-smoke/report-generated-gson-r8-shrink/report.json`
- Markdown: `data/results/experiments/version-uncertainty-reporting-smoke/report-generated-gson-r8-shrink/report.md`
- HTML: `data/results/experiments/version-uncertainty-reporting-smoke/report-generated-gson-r8-shrink/report.html`
- SBOM: `data/results/experiments/version-uncertainty-reporting-smoke/report-generated-gson-r8-shrink/sbom.cdx.json`

Observed summary:

- Version decisions: `26`
- Emitted components: `1`
- Uncertainty rows: `26`
- Category counts: `explicit-version-ambiguity=7`, `near-tie=18`, `low-confidence-version=26`, `single-reference-boundary=7`, `uncertain-version=25`
- Official emitted Maven component remains `com.google.code.gson:gson@2.8.9`

## Guardrail

The new section is explanatory. It should reduce overstatement by telling the reader when exact-version evidence is weak, close-tied, or limited by reference coverage. It must not be used as a replacement-version rule unless a separate guarded promotion test proves that behavior safe.
