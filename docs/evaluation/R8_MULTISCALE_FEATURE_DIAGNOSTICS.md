# R8 Multi-Scale Feature Diagnostics

Verdict: `r8-phase-3-inert-features-complete-scoring-unchanged`.

Phase 3 adds inert feature extraction only. These signals remain available for diagnostics and future scoped experiments, but they are not consumed by matcher scoring or SBOM component selection.

## Feature Tables

| Feature | Source | Reference table | Rows | Components | Report APK distinct/total | Report reference components |
|---|---|---|---:|---:|---:|---:|
| call-chain opcode fingerprints | LibHunter, LibScan | `call_chain_opcode_fingerprints` (present) | 694 | 3 | 231/970 | 3 |
| basic-block opcode fingerprints | ATVHunter, LibID, LibScan | `basic_block_opcode_fingerprints` (present) | 3385 | 3 | 1098/3445 | 3 |
| class-neighbor summaries | SAD | `class_neighbor_summaries` (present) | 200 | 3 | 72/198 | 3 |
| field-operation sequences | SAD | `field_operation_sequences` (present) | 471 | 3 | 153/604 | 3 |
| literal/context features | SAD, LibMD | `literal_context_features` (present) | 826 | 3 | 286/286 | 3 |

## Guardrails

- Phase 3 features are extracted and stored only for diagnostics and scoped experiments.
- Matcher scoring, selected versions, source-validation metrics, vulnerability classification, and SBOM component selection are unchanged.
- No new feature has a default matcher weight or promotion path unless a future scoped experiment passes clean controls.

## Next Actions

- Use the Phase 4 diagnostic result as the guardrail: the first global blend is rejected because it regresses controls.
- Keep features diagnostic-only unless a narrower opt-in hard-case experiment improves a target case and avoids control regressions.
- Promote scoring only as a scoped R8-aware reranker after fresh clean and partial source-validation controls pass.
