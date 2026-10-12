# Remaining Audit Scope Classification

The paper foundation does not require line-by-line reading of every historical
file in the checkout. The remaining partial files are classified below so that
no paper-authoritative evidence is silently omitted.

## Paper-relevant partial artifacts

| Artifact | Current treatment | Paper implication |
|---|---|---|
| `src/apk_sbom/cli.py` | Core parser, production dispatch, default flags, report-only routing, OSV/source-validation wiring, and experiment command boundaries audited. | Sufficient for the working implementation description; a final commit snapshot is still required before submission. |
| `docs/evaluation/R8_PHASE4_SCOPED_EXPERIMENT_DIAGNOSTICS.md` | Summary, inputs, generator, outcome policy, and conclusion audited; full row table is retained as historical output. | Use the qualitative rejection decision or attach the matching snapshot identifier; do not combine count sets from different diagnostic records. |
| `docs/thesis/THESIS_ARTIFACT_INDEX.md` | Claim map, main numbers, table sources, writing guardrails, and final checklist audited. | Confirms artifact traceability; raw paths remain historical where absent. |
| Remaining auxiliary experiment tests | Relevant promotion and rejection tests audited where they affect manuscript claims. | Use as gate-policy evidence, never as population results. |

## Historical or archive-only partial artifacts

The duplicate thesis PDFs, thesis ZIP archives, large task/planning files, and
older presentation/export bundles preserve project history or recovery
material. They are not independent evidence for the current paper once the
current source modules, decision ledger, claim contracts, retained evaluation
tables, and thesis conclusions have been reconciled.

## Completion interpretation

The source-grounded **paper-relevant** audit is complete. Remaining partial
files are retained as explicit historical or submission-release dependencies;
they do not block section-by-section working-paper drafting. Raw evaluation
exports, source trees, reference databases, and the frozen run manifest remain
required for independent reproduction and submission-ready numerical claims.
