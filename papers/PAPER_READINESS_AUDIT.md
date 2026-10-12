# Paper Readiness Audit

This checklist is the current completion audit for the source-grounded paper
foundation. “Ready” means the requirement has an authoritative project source
and a bounded interpretation. “Pending” means manuscript integration still
requires a missing artifact, external metadata check, or final snapshot.

| Requirement | Authoritative evidence | Status | Remaining action |
|---|---|---|---|
| Supervisor six-section structure | `implementation_evaluation_paper_plan.md` and `PAPER_WRITING_RULES.md` | Ready | Preserve order during manuscript integration |
| English implementation/evaluation direction | Paper plan and session decisions | Ready | Venue-specific style remains open |
| Primary literature review | Full-text audits recorded in `PROJECT_STUDY_INDEX.md`; local PDFs under `ressources/papers/` | Ready for bounded drafting | Verify final DOI/publisher metadata |
| Related-work evidence conditions | `PAPER_EVIDENCE_MATRIX.md` and `LITERATURE_CITATION_REGISTER.md` | Ready for bounded drafting | Convert working keys to final references |
| Claim-by-claim wording audit | `PAPER_CLAIM_AUDIT.md` | Ready for bounded drafting | Apply the release gates during manuscript integration |
| Integrated all-six-section working manuscript | `INTEGRATED_MANUSCRIPT_DRAFT.md` | Draft complete; not submission-ready | Apply venue style, figures, final citations, and reproducibility release conditions |
| Foundation completion audit | `PAPER_FOUNDATION_COMPLETION_AUDIT.md` | Ready for bounded drafting | Resolve submission-release gates for final numerical claims |
| Remaining audit scope classification | `REMAINING_AUDIT_SCOPE_CLASSIFICATION.md` | Complete for paper-relevant scope | Resolve raw-artifact and run-manifest release gates for final submission |
| Implementation description | `PROPOSED_APPROACH_DRAFT.md`, current `src/apk_sbom/`, thesis traceability | Ready for bounded drafting | Freeze final implementation commit/run snapshot |
| RQ1–RQ4 | `IMPLEMENTATION_EVALUATION_DRAFT.md` and paper plan | Ready | Confirm wording after venue selection |
| Controlled evaluation lane | `docs/evaluation/CONTROLLED_EVALUATION.md`, thesis tables, project task history | Ready as documented final snapshot | Describe 30/35 as an earlier checkpoint and 72/84 as the later thesis aggregate |
| Clean/partial real-APK lane | `REAL_APK_SOURCE_VALIDATION_DASHBOARD_REPORT.md`, thesis tables | Ready as documented snapshot | Preserve source-validation scope and denominator qualifiers |
| 102/106/110 membership | `PROJECT_STUDY_INDEX.md`, `FINAL_V2_RESULTS_SECTION.md`, examiner review | Ready | Preserve mapping in all result tables |
| Source-denominator coverage | `REFERENCE_DB_COVERAGE_FIRST_DASHBOARD.md` | Ready as documented snapshot | Cite the dashboard and retain the 106-case scope |
| Source-known upper bound | `FINAL_V2_RESULTS_SECTION.md` and v2 evaluation artifacts | Ready with strict qualifier | Keep source-constrained wording beside the number |
| OSV workflow examples | Evaluation chapter and vulnerability module/tests | Ready as workflow demonstration | Do not present as vulnerability precision/recall |
| Failed/rejected experiments | Decision ledger, examiner review, and R8 diagnostics | Ready with snapshot caveat | Use the qualitative global-rejection decision until the conflicting Phase-4 count snapshots are reconciled by a run manifest |
| Threats to validity | `IMPLEMENTATION_EVALUATION_DRAFT.md`, paper rules | Ready for drafting | Retain database/calibration and source-validation limitations in the final wording |
| Working figures and tables | `PAPER_FIGURE_TABLE_SPEC.md`, integrated Sections 3–5 | Figure 1 and Tables 1–2 drafted; empirical plots/tables pending | Export the workflow figure and generate all raw-result visuals from one frozen machine-readable snapshot after restoration |
| Reproducibility package | Current checkout inventory, thesis tables, evaluation dashboards, and paper plan | Documented results available; machine-readable reproduction package incomplete | Cite retained records as provenance; describe the limits on independent recalculation from this checkout |
| Working author–year reference list | `REFERENCES_DRAFT.md`, `LITERATURE_CITATION_REGISTER.md`, thesis bibliography files, official Android documentation | Ready for working draft | Verify final publisher metadata and apply venue citation style |
| Numerical claim traceability | Retained thesis tables, evaluation dashboards, controlled-evaluation notes, and project history | Ready for documented-snapshot reporting | Preserve the 20 June 2026 PFE snapshot and distinguish recorded values from independent recalculation |

## Current conclusion

The first complete **working-paper draft** of all six supervisor-requested
sections is present in `INTEGRATED_MANUSCRIPT_DRAFT.md`. The numerical results
are documented in the theses and retained evaluation records; no experiment
rerun is required for this paper draft. Some raw exports and the frozen run
manifest are unavailable for independent recalculation. Venue-specific
references, final figures and tables, and the final claim-contract audit
remain.

## Final integration gate

Before calling the paper submission-ready, complete the remaining venue and
figure work and run a final claim-contract check against
`PAPER_EVIDENCE_MATRIX.md`, retaining citations to the documented evidence.
