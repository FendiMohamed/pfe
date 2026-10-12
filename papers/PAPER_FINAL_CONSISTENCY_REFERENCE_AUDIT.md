# Final Paper Consistency and Reference Audit

## Verdict

The paper is substantively aligned with the project and thesis baseline. I found no numerical contradiction in the retained evaluation snapshot and no clearly wrong primary-paper citation.

The paper now includes the R8 and AI report-only subsection, and the formatted PDF was regenerated after the correction.

Recommended status: technically faithful working paper, with minor editorial and release-control items remaining before submission.

## Findings

### No blocking factual error found

The core claims match the documented thesis/evaluation baseline:

- 84/84 expected rows across 72 controlled fixtures;
- 47/47 across five clean source-validated APKs;
- 880/1,790 across 97 partial source-validated APKs;
- 927/1,837 across 102 Maven-emitting APKs;
- 927/12,082 across 106 source-tree cases;
- 6,772/6,772 in the source-version-constrained upper-bound lane.

The paper correctly labels these as documented snapshots and does not claim a fresh rerun.

### Snapshot boundary

The paper reports the retained PFE evaluation snapshot associated with 20 June 2026 and commit 2983d54. The project also contains separate priority-reference recovery records with approximately 9,656–9,657 exact source-version rows out of 12,082.

Those values are reference-database coverage results, not new end-to-end matcher confirmation results. They must not be merged with 927/1,837 or 927/12,082.

Keep this sentence in the final version:

> Unless otherwise stated, the numerical results in this paper are transcribed from the retained PFE evaluation snapshot dated 20 June 2026 and are not merged with later or separate project recovery experiments.

### Implementation description

The paper accurately describes the workflow but remains compressed. If space allows, add a short implementation table covering APK extraction and DEX analysis, Maven reference conversion, SQLite feature storage, matching and scoring, CycloneDX/report generation, and OSV classification.

The two promoted guarded defaults should also remain named:

- composite family shortlist;
- version-unique literal/context reranker.

### AI and R8

The added subsection correctly presents R8 transformation stress conditions, rejection of the broader Phase-4 R8 blend, the Phase-5 report-only trigger, the Random Forest and Transformer results, the raw-opcode Transformer limitation, and unchanged authoritative outputs in the integration smoke test.

It correctly states that these are project-derived, report-only experiments and not APK-only deployment accuracy.

### Citation abbreviation

The introduction originally cited NTIA as an abbreviation while the reference entry used the full corporate author name. The manuscript and LaTeX source now use the full author name, removing that ambiguity.

### Reference accuracy

The manuscript reference list is supported by the thesis bibliographies, citation register, and local primary-paper PDFs. Spot checks confirmed the metadata for Xie et al. (2024), Zhou et al. (2025), and Safronov et al. (2025). No clearly incorrect DOI, author list, title, or venue was found in the current working list.

### Venue formatting

The references are suitable for a working author–date draft. A final venue may still require different citation style, title capitalization, conference publisher details, consistent arXiv treatment, and a decision about citing the UniBOM conference version or arXiv version. These are release-format decisions, not evidence errors.

## Editorial checks

- Section order follows the supervisor's requested structure.
- Section numbering is consistent after adding the R8/AI subsection.
- Emitted-version confirmation is not called precision, recall, or general accuracy.
- Source validation is distinguished from APK-only inference.
- OSV examples are described as workflow demonstrations.
- Native .so handling is described as hash-only file components.
- The 30/35 and 72/84 counts are described as successive milestones.
- AI and R8 are represented without production authority.

## Files updated

- papers/INTEGRATED_MANUSCRIPT_DRAFT.md
- papers/MANUSCRIPT_TWO_COLUMN.tex
- output/pdf/MANUSCRIPT_TWO_COLUMN.pdf

## Conclusion

The paper matches the documented project work and thesis baseline. No blocking factual or reference error was identified. Before submission, perform the final venue-style pass, confirm the exact implementation snapshot identifier, and preserve the separation between the thesis baseline and later reference-recovery records.

