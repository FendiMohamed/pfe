# Master Thesis Structured Literature Review Protocol

Protocol version: 1.0  
Frozen on: 2026-06-21  
Thesis track: Master  
Review type: structured literature mapping review

## 1. Purpose and Status

This protocol governs the literature evidence used by the master thesis
*Towards Trustworthy SBOM Recovery from Compiled Android Applications: An
Evidence-Based Component Attribution Framework*.

The review is intentionally described as a **structured mapping review**, not
as a completed systematic literature review. The existing corpus was assembled
iteratively during the research and PFE phases. Freezing this protocol makes
all subsequent screening, extraction, classification, and synthesis decisions
auditable. A later database refresh may extend the corpus, but it must preserve
the rules below and record the date, query, result count, and screening
decisions.

## 2. Review Questions

- **RQ-R1:** Which evidence sources are used to identify Android third-party
  components from compiled applications?
- **RQ-R2:** Which techniques support library identity, exact-version
  attribution, or both?
- **RQ-R3:** Which compilation, optimization, obfuscation, packaging, and
  dependency transformations threaten each evidence source?
- **RQ-R4:** How do studies construct ground truth and evaluate library-level,
  version-level, and vulnerability-related claims?
- **RQ-R5:** How do studies represent confidence, ambiguity, provenance,
  abstention, partial inclusion, and conflicting evidence?
- **RQ-R6:** Which gaps prevent recovered component claims from becoming
  trustworthy, auditable SBOM statements?

## 3. Search Scope and Strategy

### 3.1 Sources

The primary search sources are ACM Digital Library, IEEE Xplore, SpringerLink,
ScienceDirect, USENIX, and arXiv. Google Scholar is used only for discovery and
citation chaining. Standards and platform documentation are collected
separately from OWASP CycloneDX, SPDX, the Package URL project, Android
Developers, and other authoritative publishers.

### 3.2 Date and Language Scope

- Publication period: 2015 through the search date.
- Frozen protocol date: 2026-06-21.
- Language: English full text.
- Publication types: peer-reviewed conference and journal papers, theses,
  benchmark or empirical-study papers, and clearly identified preprints when
  no archival version is available.

### 3.3 Search Concept Blocks

Queries combine at least one term from each relevant block:

1. **Platform:** `Android`, `APK`, `DEX`, `Dalvik`.
2. **Component:** `"third-party library"`, `TPL`, `"software component"`,
   `dependency`, `SBOM`, `"software bill of materials"`.
3. **Task:** `detect*`, `identif*`, `recogn*`, `recover*`, `attribut*`,
   `fingerprint*`, `match*`.
4. **Threat or specificity:** `obfuscat*`, `R8`, `ProGuard`, `optim*`,
   `shrink*`, `inlin*`, `version*`, `vulnerab*`.

Canonical query:

```text
(Android OR APK OR DEX OR Dalvik)
AND ("third-party library" OR TPL OR "software component" OR dependency
     OR SBOM OR "software bill of materials")
AND (detect* OR identif* OR recogn* OR recover* OR attribut*
     OR fingerprint* OR match*)
AND (obfuscat* OR R8 OR ProGuard OR optim* OR shrink* OR inlin*
     OR version* OR vulnerab*)
```

Database-specific syntax may be adapted without changing the four concept
blocks. Backward and forward snowballing is performed from included studies,
surveys, and benchmarks.

## 4. Eligibility Rules

### 4.1 Inclusion Criteria

A publication is eligible when it:

1. addresses component, library, package, or version recovery from Android
   binaries or evaluates tools that do;
2. proposes, studies, or evaluates evidence obtainable from compiled
   artifacts, reference libraries, package metadata, or related dependency
   knowledge;
3. contributes a detection method, benchmark, empirical assessment, taxonomy,
   or SBOM-oriented framework relevant to compiled-artifact attribution;
4. provides enough methodological information to extract at least the task,
   evidence source, evaluation basis, and limitations; and
5. has an accessible English title and abstract, with full text preferred.

### 4.2 Exclusion Criteria

A publication is excluded when it:

1. requires source dependency manifests as the only authority and does not
   study binary recovery;
2. concerns malware-family classification, clone detection, or vulnerability
   scanning without a component-attribution contribution;
3. is a tutorial, slide deck, blog post, product page, or duplicate record;
4. reports no separable Android result;
5. lacks enough information to identify its method or evaluation basis; or
6. is a shorter version of an included extended study and adds no distinct
   method, dataset, or result.

Related conference and journal versions remain separate publication units only
when they contribute distinct evidence. Otherwise, they form one study family,
and the more complete version is the synthesis authority.

## 5. Screening and Evidence Tiers

Screening has four stages:

1. deduplicate by title, DOI, authors, and study family;
2. screen title and abstract;
3. screen full text against the eligibility criteria;
4. assign an evidence tier and record the decision.

Evidence tiers:

- **Tier A — full-text verified:** a local full text was inspected and
  structured extraction is permitted.
- **Tier B — supplementary record:** metadata or a structured research note
  exists, but the local full text has not yet been verified. It may guide
  search and gap identification, but it cannot independently support precise
  quantitative conclusions.
- **Tier C — contextual authority:** standards, official documentation, and
  project artifacts. These inform definitions or framework design but are not
  counted as primary studies.
- **Excluded:** the exclusion reason is recorded and the item is not used in
  synthesis.

## 6. Data Extraction Schema

Each included publication is extracted using the following fields:

- bibliographic identity and stable identifier;
- study family and evidence tier;
- research objective and task level;
- output granularity: family, library, class, version, SBOM, or vulnerability;
- required inputs and reference-corpus assumptions;
- module decoupling or segmentation method;
- evidence families: names, package structure, API use, opcodes, control flow,
  call/dependency graphs, literals, resources, native code, metadata, learned
  representations, or cross-component relations;
- matching, ranking, classification, or fusion method;
- confidence, threshold, ambiguity, abstention, and provenance behavior;
- covered transformations: renaming, package flattening, shrinking,
  optimization, control-flow rewriting, method inlining, repackaging,
  multidex, partial inclusion, and dynamic/native loading;
- ground-truth construction and dataset composition;
- evaluation unit and reported metrics;
- library-level and version-level results kept in separate fields;
- reproducibility and artifact availability;
- SBOM format and vulnerability-mapping support;
- threats, limitations, and explicit negative findings;
- adoption, adaptation, or rejection relevance to the proposed framework.

Missing or unreported fields are recorded as `NR`; they are not inferred.

## 7. Quality Assessment

Each Tier A publication is scored `1` (yes), `0.5` (partial), or `0` (no) on:

1. clear research objective;
2. reproducible method description;
3. described dataset and ground truth;
4. explicit task unit and metrics;
5. stated transformation or obfuscation conditions;
6. separation of identity and version claims;
7. available implementation, data, or artifact;
8. acknowledged limitations or threats to validity.

The score controls synthesis weight, not automatic inclusion. A technically
important historical study with incomplete reporting may remain in the map,
but uncertainty about its evidence must be visible.

### 7.1 Completed Tier A Scores

The vectors below list Q1--Q8 in the order defined above. Totals are out of
eight and measure reporting quality, not scientific importance.

| ID | Study | Q1--Q8 vector | Total |
|---|---|---|---:|
| S01 | LibScout | 1, 1, 1, 1, 1, 1, 1, 1 | 8.0 |
| S02 | LibD | 1, 1, 0.5, 1, 0.5, 0.5, 0.5, 1 | 6.0 |
| S03 | LibPecker | 1, 1, 1, 1, 1, 0.5, 0.5, 1 | 7.0 |
| S04 | ORLIS | 1, 1, 1, 1, 1, 0.5, 0.5, 1 | 7.0 |
| S05 | LibID | 1, 1, 1, 1, 1, 1, 0.5, 1 | 7.5 |
| S06 | ASE 2020 assessment | 1, 1, 1, 1, 1, 1, 1, 1 | 8.0 |
| S07 | Systematic assessment | 1, 1, 1, 1, 1, 1, 0.5, 1 | 7.5 |
| S08 | ATVHUNTER | 1, 1, 1, 1, 1, 1, 0.5, 1 | 7.5 |
| S09 | LibScan | 1, 1, 1, 1, 1, 1, 0.5, 1 | 7.5 |
| S10 | Ramirez thesis | 1, 1, 1, 1, 0.5, 1, 0.5, 1 | 7.0 |
| S11 | LibHunter | 1, 1, 1, 1, 1, 1, 0.5, 1 | 7.5 |
| S12 | LibAttention | 1, 1, 1, 1, 1, 1, 0.5, 1 | 7.5 |
| S13 | SAD | 1, 1, 1, 1, 1, 1, 0.5, 1 | 7.5 |
| S17 | TPL-Benchmark | 1, 1, 1, 1, 1, 1, 1, 1 | 8.0 |
| S18 | UniBOM | 1, 1, 0.5, 0.5, 0.5, 0.5, 1, 0.5 | 5.5 |

## 8. Synthesis Rules

- Use narrative and taxonomy-based synthesis as the default.
- Do not rank incompatible metrics from different datasets as if they formed a
  common leaderboard.
- Never merge library-level, class-level, and version-level results.
- Keep original-paper results separate from independent benchmark results.
- Record whether obfuscation or R8 was absent, simulated, or observed in real
  applications.
- Treat artifact availability and reproducibility as independent dimensions
  from reported accuracy.
- Use Tier B records only for provisional coverage and research-gap mapping.
- Distinguish component identity authority from exact-version authority.
- Distinguish an SBOM claim from a vulnerability conclusion; a CVE statement
  cannot be stronger than its component and version evidence.
- Prefer explicit uncertainty or abstention over a forced exact version.

## 9. Frozen Seed Corpus

The protocol begins with 20 publication units.

### Tier A — 15 locally verified full texts

1. LibScout (2016).
2. LibD (2017).
3. LibPecker (2018).
4. ORLIS (2018).
5. LibID (2019).
6. *Automated Third-Party Library Detection for Android Applications: Are We
   There Yet?* (2020).
7. *A Systematic Assessment on Android Third-Party Library Detection Tools*
   (2021).
8. ATVHUNTER (2021).
9. LibScan (2023).
10. *Empirical Study of Third-Party Library Detection in iOS and Android
    Applications* (2024).
11. LibHunter / *How Does Code Optimization Impact Third-Party Library
    Detection for Android Applications?* (2024).
12. LibAttention (2025).
13. SAD / *Version-Level Third-Party Library Detection in Android Applications
    via Class Structural Similarity* (2025).
14. TPL-Benchmark / *Revisiting Third-Party Library Detection: A Ground Truth
    Dataset and Its Implications Across Security Tasks* (2025).
15. UniBOM / *A Unified SBOM Analysis and Visualisation Tool for IoT Systems
    and Beyond* (2025).

### Tier B — 5 supplementary records pending local full-text verification

16. LibRadar (2016).
17. Libra (2023).
18. LibMD (2025).
19. LibScope / *Towards Global Matches for Third-Party Library Detection in
    Android* (2026).
20. ObfDetector / advanced-obfuscation robustness study (2026).

Tier B records are not promoted to Tier A until their full text, bibliographic
identity, extraction record, and quality assessment have been checked.

## 10. Review Audit Trail

The structured extraction sources currently reside under `papers/data/`.
The primary narrative synthesis is under `papers/state_of_the_art.md`.
Every corpus refresh must append a master-thesis session-log entry containing:

- search date and data sources;
- exact query variants;
- raw result and deduplicated counts;
- newly included and excluded records with reasons;
- tier promotions or demotions;
- changed extraction fields;
- effects on the taxonomy or framework.

This protocol may be amended only by adding a dated change note. Silent changes
to eligibility, evidence tiers, or synthesis rules are prohibited.

## 11. Clarification Note - 2026-06-21 (Version 1.0a)

The full-text screening stage in Section 5 is complete only for records with a
locally verified full text. A record that passes title-and-abstract screening
but lacks a verified local full text remains Tier B pending full-text
eligibility screening, structured extraction, bibliographic checking, and
quality assessment. This note clarifies the operational sequence; it does not
change the eligibility criteria, evidence tiers, or synthesis authority.

The seed corpus was assembled before the protocol freeze. The original
database-specific query executions, raw result counts, and deduplicated flow
were not retained and cannot be reconstructed as an exhaustive selection
history. Every future refresh remains subject to the complete audit-trail
requirements in Section 10.

## 12. Full-Text Promotion Note - 2026-06-21 (Version 1.0b)

TPL-Benchmark and UniBOM were downloaded from their arXiv records, inspected
locally, checked against their embedded bibliographic metadata, extracted
using the protocol schema, and scored under Section 7. They are promoted from
Tier B to Tier A. TPL-Benchmark is direct Android benchmark evidence. UniBOM is
adjacent binary/SBOM evidence and is not used to support Android Maven
exact-version claims. The corpus remains 20 publication units: 15 Tier A and
five Tier B.
