# Final V2 Results Section

This section can be inserted into the thesis evaluation chapter after the main emitted-version confirmation results. It explains the final demo v2 reference database, the 106-APK source-version constrained rerun, the remaining gap triage, and the transparency export.

## Why This Section Exists

The main real-APK metric remains the emitted Maven version confirmation rate:

```text
confirmed emitted Maven versions / checked emitted Maven versions
```

That metric is the APK-only MVP output validated against source evidence. The current thesis table reports `927/1837` confirmed emitted Maven versions across `102` source-validated real APKs, or `50.5%`.

The v2 demo package answers a different question:

```text
If the correct source coordinate+version rows are known and present in the reference DB,
can the MVP recognize and report them without version mismatches?
```

This is a source-version constrained upper-bound lane. It is useful for measuring reference coverage, bytecode recognition, report generation, gap categories, and vulnerability-claim transparency. It must not be presented as general APK-only version-selection accuracy.

## V2 Reference Database Growth

The final v2 reference database was built after the source-observed and priority reference-growth work. The growth process deliberately recorded failed, no-bytecode, and source-boundary rows rather than hiding them.

| Metric | Value |
|---|---:|
| Final v1 demo DB components | 10493 |
| V2 DB components | 10517 |
| New bytecode-bearing components stored | 24 |
| Retry slots attempted | 87 |
| Downloaded slots | 46 |
| Downloaded no-bytecode slots | 22 |
| Unavailable/source-boundary slots | 41 |
| Previous source-gap rows now reference-covered | 25 |

The v2 DB remains a local evaluation artifact:

```text
data/reference_db/reference_features_demo_final_large_v2.sqlite
```

The tracked evidence for this growth is:

- `docs/evaluation/DEMO_FINAL_FIXABLE_REFERENCE_RETRY_PLAN.md`
- `docs/evaluation/DEMO_FINAL_FIXABLE_REFERENCE_RETRY_STAGE2_PLAN.md`
- `docs/evaluation/DEMO_FINAL_FIXABLE_REFERENCE_GROWTH_RESULT.md`

## 106-APK V2 Source-Version Constrained Rerun

The v2 DB was then used to rerun all `106` real APK cases that have source dependency trees. For each APK, the evaluator created a per-APK reference slice containing only exact coordinate+version rows from that APK's resolved source dependency tree. This makes the run an upper-bound recognition test under known source versions.

| Metric | Value |
|---|---:|
| Source-tree cases rerun | 106 / 106 |
| Emitted rows checked | 6772 |
| Exact confirmations | 6772 |
| Wrong-version emitted rows | 0 |
| Missing emitted rows | 0 |
| Confirmation rate in this constrained lane | 100.0% |
| Source-gap rows | 5238 |
| Source gaps with coordinate in v2 DB | 4222 |
| Source gaps still missing from v2 DB | 1016 |

This result is strong but bounded. It shows that, under source-known exact-version slices, every emitted component row is source-confirmed. It does not mean the APK-only matcher can recover every source dependency or select the correct version from the full large DB without source constraints.

The core artifacts are:

- `docs/evaluation/DEMO_FINAL_LARGE_V2_SOURCE_VERSION_EVALUATION.md`
- `data/results/evaluation/real-apk-demo-final-large-v2-source-version-dashboard.json`
- `data/results/evaluation/real-apk-demo-final-large-v2-source-version-rows.csv`
- `data/results/evaluation/real-apk-demo-final-large-v2-source-version-gaps.csv`

## Remaining Source Gaps

The source dependency denominator contains `12082` source dependency rows. The v2 transparency export classifies each row so the thesis can explain why a source dependency is not simply counted as a false negative.

| Source coverage class | Rows | Interpretation |
|---|---:|---|
| `exact-version-in-db-and-emitted` | 898 | Source row was represented and emitted exactly. |
| `exact-version-in-db` | 5874 | Exact row exists in the DB but was not emitted in this lane's source coverage view. |
| `matcher-recall-gap` | 2281 | Exact source version exists but matcher/reporting did not emit it. |
| `artifact-family-alias` | 1504 | Source coordinate maps to a target/sibling bytecode artifact. |
| `metadata-only` | 734 | BOM, annotation, compiler, lint, or metadata/source-only rows. |
| `source-boundary` | 277 | Project-module, relocated, common-source, or platform boundary rows. |
| `missing-coordinate-or-version` | 442 | Plausibly bytecode-bearing rows still missing from the reference DB. |
| `missing-coordinate` | 72 | Coordinate absent from the v2 DB. |

The dedicated v2 gap triage summarizes the `5238` non-emitted source-gap rows:

| Triage bucket | Rows |
|---|---:|
| Target-artifact alias boundary | 1460 |
| Metadata/source-only boundary | 734 |
| Matcher-recall candidate | 2281 |
| Missing-reference candidate | 442 |
| Common source/platform boundary | 209 |
| Relocated-coordinate boundary | 49 |
| Already covered by emitted sibling | 44 |
| Project-module boundary | 19 |

The important point is that the remaining work is no longer just "add more versions." The final actionable set has two different technical meanings:

- `442` rows are remaining missing-reference candidates.
- `2281` rows are matcher-recall candidates where exact versions already exist in the DB.

The matcher-recall result is especially important for future work. The diagnostic found `1425` source-context report-only suggestions across `46` cases and `552` coordinates. These should be used for analysis and dashboards, not promoted into default SBOM components without a separate APK-only control run.

## Phase 6 AI-Assisted R8 Triage

The final v2 transparency artifacts also became the training evidence for a report-only AI assistance layer. This is not a replacement for the matcher and it is not a source of confirmed SBOM versions. It is a supervised triage layer for hard R8/minified and matcher-recall rows.

| Metric | Value |
|---|---:|
| Training rows | 20523 |
| Case IDs | 149 |
| Coordinates | 1370 |
| Phase 6A model | RandomForestClassifier |
| Phase 6A test macro-F1 | 0.708 |
| Report-only suggestions | 13736 |
| Phase 6B model | torch.nn.TransformerEncoder |
| Phase 6B structured-token test macro-F1 | 0.977 |

The Phase 6A model may recommend report-only wording such as `suggest_report_only`, `suppress_uncertain`, or `risk_only`. It may not change selected versions, CycloneDX SBOM output, vulnerability labels, or source-validation metrics. The Phase 6B Transformer is a trained structured-token research prototype, not raw smali pretraining; the production report may surface its status, but production decision wiring remains disabled. The combined evidence file is `docs/evaluation/AI_R8_FINAL_EVALUATION.md`; the dedicated report-only proof is `docs/evaluation/AI_R8_REPORT_ONLY_DEMO.md`, which shows that opt-in AI suggestions add an AI section to the report while leaving detected components and normalized SBOM content unchanged.

The follow-up R8 structural recall experiment reports `1000` source-context structural recall candidates from `1658` router rows, but keeps them report-only because same-coordinate wrong-version and false-positive controls remain in scope. This supports transparent hard-R8 triage without converting source-context evidence into APK-only SBOM authority.

## Vulnerability Claim Transparency

The final transparency export also classifies vulnerability rows:

| Vulnerability claim strength | Rows |
|---|---:|
| `not-queried` | 93 |
| `report-only` | 75 |
| `potential` | 64 |

This prevents the thesis from collapsing every scanner row into a confirmed CVE claim. A vulnerability can be treated as source-confirmed only when the component and version evidence support that conclusion. Otherwise it remains potential or report-only.

## How To Write The Result

Recommended wording:

```text
The normal APK-only/source-validated metric confirms 927/1837 emitted Maven versions across 102 source-validated real APKs. To evaluate reference coverage and recognition under known source versions, a separate v2 source-version constrained lane reran 106 source-tree APK cases against exact source coordinate+version slices from a grown 10517-component reference DB. In that bounded lane, all 6772 emitted rows were exact source confirmations, with zero wrong-version emitted rows and zero missing emitted rows. The remaining 5238 source-gap rows were then classified into metadata/source-only, alias/boundary, missing-reference, and matcher-recall buckets.
```

Avoid this wording:

```text
The tool reached 100% accuracy on 106 real APKs.
```

That would be misleading because the v2 run uses source-known exact-version slices. The honest claim is narrower and stronger: the final MVP now has a transparent upper-bound evaluation package, a row-level gap taxonomy, and a clear next-work split between remaining reference coverage and matcher recall.

## Thesis Takeaway

The final v2 package strengthens the thesis because it shows that the project did not hide missing dependencies or force exact versions. It records:

- what was emitted and confirmed;
- what was present in the source tree but not emitted;
- what is metadata/source-only or artifact-family boundary;
- what is still missing from the DB;
- what requires matcher recall improvements;
- which vulnerability rows are potential or report-only.

This is the clearest answer to the concern that high accuracy with low DB coverage would look like cheating. The thesis now exposes both the strong result and the remaining denominator.
