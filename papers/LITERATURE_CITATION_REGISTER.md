# Literature Citation Register

This register is the metadata checkpoint for the manuscript. It records the
studies already used in the State of the Art draft and prevents project notes
from being mistaken for final bibliographic authority. DOI, publisher URL, and
final citation style remain to be verified before submission.

| Working key | Authors/title metadata source | Primary local source | Use in paper | Metadata status |
|---|---|---|---|---|
| `tpl-benchmark` | `papers/data/papers_overview.json`, `papers/data/tpl_benchmark.json`; BibTeX key `gu2025tplbenchmark` | `ressources/papers/Revisiting Third-Party Library Detection - TPL-Benchmark.pdf` | Benchmark construction, denominator and cross-tool comparability limits | Metadata verified in `thesis/pfe/bib/references.bib`; DOI `10.48550/arXiv.2509.04091` |
| `unibom` | `papers/data/papers_overview.json`, `papers/data/unibom.json`; BibTeX key `safronov2025unibom` | `ressources/papers/UniBOM - Unified Software Bill of Materials.pdf` | Adjacent integrated SBOM and vulnerability workflow | Metadata verified in `thesis/pfe/bib/references.bib`; DOI `10.1145/3770501.3770512` |
| `sad` | `papers/data/papers_overview.json`; BibTeX key `zhou2025sad` | `ressources/papers/Version-level Third-Party Library Detection in Android Applications via Class Structural Similarity.pdf` | Structural evidence and strict version-level metric | Metadata verified in `thesis/pfe/bib/references.bib`; DOI `10.1145/3756681.3756933` |
| `libhunter` | BibTeX key `xie2024libhunter` | `ressources/papers/LibHunter.pdf` | R8 prevalence and inlining/CallSiteOptimization stress | Metadata verified in `thesis/pfe/bib/references.bib`; DOI `10.1145/3691620.3695554` |
| `libscan` | BibTeX key `wu2023libscan` | `ressources/papers/Libscan.pdf` | Coarse-to-fine signatures and transformation-specific version results | Metadata verified in `thesis/pfe/bib/references.bib`; USENIX Security 2023 official URL recorded |
| `atvhunter` | `papers/data/papers_overview.json`, `papers/data/papers_6-10_analysis.json`; BibTeX key `zhan2021atvhunter` | `ressources/papers/ATVHUNTER.pdf` | CDG/CFG/opcode matching and vulnerability-aware workflow | Metadata verified in `thesis/pfe/bib/references.bib`; DOI `10.1109/ICSE43902.2021.00150` |
| `libscout` | `papers/data/libscout.json`, `papers/data/papers_overview.json`; BibTeX key `backes2016libscout` | `ressources/papers/LibScout.pdf` | Profile-based identity/version detection background | Metadata verified in `thesis/pfe/bib/references.bib`; DOI `10.1145/2976749.2978333` |
| `libd` | `papers/data/libd.json`, `papers/data/papers_overview.json`; BibTeX key `li2017libd` | `ressources/papers/LibD.pdf` | Graph/opcode identity detection background | Metadata verified in `thesis/pfe/bib/references.bib`; DOI `10.1109/ICSE.2017.38` |
| `orlis` | `papers/data/orlis.json`, `papers/data/papers_overview.json`; BibTeX key `wang2018orlis` | `ressources/papers/ORLIS.pdf` | Obfuscation-resilient structural matching background | Metadata verified in `thesis/pfe/bib/references.bib`; DOI `10.1145/3197231.3197248` |
| `systematic-assessment` | BibTeX key `zhan2021systematic` | `ressources/papers/A Systematic Assessment on Android Third-Party Library Detection Tools.pdf` | Cross-tool evaluation dimensions and recurring implementation/evaluation limitations | Metadata verified in `thesis/pfe/bib/references.bib`; arXiv `2108.01964` |
| `libattention` | BibTeX key `pan2025libattention` | `ressources/papers/Android Third-Party Library Detection via Feature Language Model.pdf` | Learning-based library-presence approach; not exact-version authority by itself | Metadata verified in `thesis/pfe/bib/references.bib`; DOI `10.1109/SANER64311.2025.00028` |
| `libpecker` | BibTeX key `zhang2018libpecker` | `ressources/papers/LibPecker.pdf` | Class-dependency and adaptive-similarity approach | Metadata verified in `thesis/pfe/bib/references.bib`; DOI `10.1109/SANER.2018.8330204` |
| `libid` | BibTeX key `zhang2019libid` | `ressources/papers/LibID.pdf` | Consistent class correspondence under obfuscation | Metadata verified in `thesis/pfe/bib/references.bib`; DOI `10.1145/3293882.3330563` |
| `review-guidance` | BibTeX key `kitchenham2007guidelines` | `thesis/master/bib/references.bib` | Review-protocol method guidance; not an Android detector study | Metadata verified in master-thesis bibliography; report `EBSE-2007-01` |
| `libfan-postfreeze` | Working key `fan2026libfan`; Fan, Dihao; Zhang, Jian; Shi, Yasai; Luo, Chuan; Liu, Xudong; Liu, Yang; Hu, Chunming; Wang, Xu. “Context-Aware Functional Modeling for Android Third-Party Library Detection.” arXiv:2609.31409, v1, 25 September 2026 | Primary arXiv full text, inspected online 29 September 2026: `https://arxiv.org/abs/2609.31409` | Post-freeze update on context-aware learning and partial-library matching under transformations | Full-text source and author metadata verified; preprint, outside frozen thesis-corpus counts, not integrated into the original screening record |

## Rules for promotion into the manuscript

1. Preserve the verified BibTeX key and DOI/official URL when transferring a
   citation into the manuscript.
2. Cite the local PDF as the reviewed evidence source during drafting; do
   not infer missing metadata from filenames or older project summaries.
3. Attach each quantitative statement to the metric and dataset conditions in
   `papers/PAPER_EVIDENCE_MATRIX.md`.
4. Do not cite the older synthesis tables as substitutes for the primary paper.

## Working reference-list integration — 2026-09-29

- Added `REFERENCES_DRAFT.md` and linked it from the integrated manuscript.
- The working Android Developers author–date suffixes map to the official APK
  Analyzer (n.d.-a), Android library/AAR (n.d.-b), R8 optimization (n.d.-c),
  and D8 conversion (n.d.-d) documentation; titles and URLs were checked
  against the Android Developers site.
- Split the two Zhan et al. 2021 works in the working author–year list and
  synchronized citations across manuscript and detailed drafts. The current
  suffix order follows the reference list: 2021a is ATVHunter and 2021b is the
  systematic assessment; the selected venue may impose its own style details.
- Changed the NIST in-text citation from corporate shorthand to Boyens et al.
  (2022), matching the personal-author record in the thesis bibliography.
- Added the cited OSV API documentation to the working reference list and
  checked the current API page on the OSV project's official documentation.
- Metadata remains venue-provisional; publication-specific metadata checks and
  style conversion remain before submission.

## Thesis bibliography cross-check

The examiner-audited thesis review records a completed check of 46 citation
keys against 46 bibliography entries, with no missing or unused key. This
supports the project’s thesis bibliography as a metadata source, but the paper
must still select and verify only the references actually used in its shorter
State of the Art section.
