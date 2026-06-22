# PFE Chapter 3 AI Evidence Snapshot

## Status

- Snapshot date: 2026-06-20
- Branch: `codex/publish-r8-real-apk-checkpoint`
- Commit inspected: `2983d54`
- Evidence class: project-derived report-only ML/DL experiments
- Production authority: deterministic matcher only
- External independent corpus: no

This snapshot freezes the generated evidence used to write PFE Chapter 3. If
any source JSON listed below changes, the chapter metrics and interpretations
must be re-audited.

## Authority Boundary

The current integration gate permits:

- report wording;
- risk and investigation triage;
- strategy routing;
- model status and metric reporting.

It forbids:

- automatic selected-version changes;
- automatic CycloneDX component or version changes;
- automatic CVE/OSV label changes;
- changes to source-validation metrics;
- raw-opcode Transformer decision authority.

The generated integration-gate verdict is:

- report-only ready: true;
- matcher authority ready: false;
- SBOM/CVE authority ready: false;
- current integration level:
  `production-report-only-ai-assistance`.

## Structured Evidence Dataset

The Phase 6A dataset is derived from existing project diagnostics, not from an
external Android ML benchmark.

| Field | Frozen value |
|---|---:|
| Rows | 20,523 |
| Case IDs | 149 |
| Coordinates | 1,370 |
| Train rows / cases | 14,905 / 104 |
| Validation rows / cases | 1,750 / 15 |
| Test rows / cases | 3,868 / 30 |

Rows are grouped by `case_id` before splitting. Ordered case groups are assigned
deterministically to train, validation, and test buckets. Rows belonging to the
same case do not cross these partitions.

### Row Sources

| Source | Rows |
|---|---:|
| Boundary evidence | 11,184 |
| Emitted result | 6,772 |
| Matcher recall | 2,281 |
| Phase 5 diagnostics | 286 |

### Labels

| Label | Rows |
|---|---:|
| `risk_only` | 7,811 |
| `confirmed_exact` | 6,790 |
| `boundary_do_not_suggest` | 3,029 |
| `suggest_report_only` | 1,429 |
| `suppress_uncertain` | 870 |
| `mismatch_or_extra` | 594 |

The labels describe project triage and evidence states. They are not
independently annotated universal APK ground truth.

## Independent-Manifest Boundary

The project-heldout manifest contains:

| Field | Frozen value |
|---|---:|
| Total rows | 31,589 |
| Training-eligible rows | 20,523 |
| Held-out or report-only rows | 11,066 |
| Unique case IDs | 150 |
| Unique coordinates | 1,370 |
| External corpus | false |

The held-out lanes support drift checks, ablation, smoke tests, and
transparency. They do not transform the dataset into an external benchmark.

## Phase 6A Random Forest

### Model

- Type: `RandomForestClassifier`
- Trees: 200
- Maximum depth: 8
- Class weighting: balanced
- Random state: 42
- Input features: 17
- Test macro-F1: 0.7076258526
- Test accuracy: 0.6902792141

### Baselines

| Baseline | Test accuracy |
|---|---:|
| Majority class (`risk_only`) | 0.3834022751 |
| Score-threshold rule | 0.1654601861 |

The generated comparison uses accuracy for these two Phase 6A baselines. The
chapter must not imply that a baseline macro-F1 was generated when it was not.

### Principal Feature Importances

| Feature | Importance |
|---|---:|
| `identity_confidence` | 0.2307472900 |
| `is_boundary_or_limitation` | 0.2170009784 |
| `best_score` | 0.2062738234 |
| `source_rank` | 0.0855398601 |
| `dependency_score` | 0.0679481933 |
| `opcode_score` | 0.0488747618 |

Feature importance describes use by the fitted forest; it does not establish a
causal relation.

### Ablation

| Variant | Features | Test macro-F1 |
|---|---:|---:|
| All features | 17 | 0.7076258526 |
| No overlap counts | 14 | 0.7097939916 |
| No context flags | 13 | 0.5639084112 |
| Scores only | 10 | 0.5579001022 |
| Overlap counts only | 3 | 0.1764469757 |
| Context flags only | 4 | 0.1619135612 |

The strongest generated ablation is the no-overlap-count variant, which is
slightly above the all-feature result. This does not justify removing those
features globally; it shows that raw overlap counts add little in this bounded
classification task.

### Weak Classes

The full model performs poorly on the two closely related risk/mismatch
classes:

| Label | Precision | Recall | F1 |
|---|---:|---:|---:|
| `risk_only` | 0.990625 | 0.213756 | 0.351636 |
| `mismatch_or_extra` | 0.100971 | 0.781955 | 0.178848 |

Of 1,483 true `risk_only` test rows, 926 were predicted as
`mismatch_or_extra` and 222 as `boundary_do_not_suggest`. The model is useful
for conservative report triage, but it is not a reliable semantic authority
for these adjacent labels.

## Phase 6B Structured-Token Transformer

### Architecture

- Type: `torch.nn.TransformerEncoder`
- Embedding dimension: 64
- Attention heads: 4
- Encoder layers: 1
- Sequence length: 64 tokens
- Batch size: 128
- Random state: 42

### Full Profile

| Field | Frozen value |
|---|---:|
| Rows | 20,523 |
| Vocabulary size | 5,097 |
| Validation macro-F1 | 0.9478227479 |
| Test macro-F1 | 0.9771840114 |
| Test accuracy | 0.9919855222 |

The full token profile includes raw coordinate tokens, source-version tokens,
raw candidate-version tokens, all structured features, and diagnostic context
labels. These may encode shortcuts closely related to how the training labels
were produced. The result is retained as research workflow evidence, not as
APK-only deployment performance.

### MVP-Safe Profile

The safer profile excludes:

- source-version tokens;
- raw candidate-version tokens;
- raw coordinate token;
- `source_rank`;
- boundary, clean-real, and partial-real role flags;
- diagnostic context labels.

It retains source-free feature buckets, tokenized group/artifact parts,
candidate-version shape, and the R8/minification flag.

| Field | Frozen value |
|---|---:|
| Rows | 20,523 |
| Vocabulary size | 1,704 |
| Validation macro-F1 | 0.8599911170 |
| Test macro-F1 | 0.8821651724 |
| Test accuracy | 0.9069286453 |

This result is more credible for report-only triage than the full-profile
result, but it still uses project-derived labels and a project-heldout split.
Production decision wiring remains disabled.

## Raw-Opcode Transformer

### Dataset and Split

| Field | Frozen value |
|---|---:|
| APKs analyzed | 14 |
| APKs skipped | 0 |
| Method opcode sequences | 1,680 |
| Labels | 7 |
| Vocabulary size | 135 |
| Maximum sequence length | 128 |
| Train rows / APK cases | 665 / 7 |
| Validation rows / APK cases | 175 / 7 |
| Test rows / APK cases | 840 / 7 |

For each label, one APK case is held out for test. Validation rows are selected
deterministically from the remaining training cases because only two APK cases
exist per label. The labels describe R8/real-APK profiles, not library
coordinates or versions.

### Results

| Model | Test macro-F1 | Test accuracy |
|---|---:|---:|
| Majority class | 0.0357142857 | 0.1428571429 |
| Opcode-count logistic regression | 0.1281280997 | 0.1464285714 |
| Raw-opcode Transformer | 0.1098452845 | 0.1464285714 |

The Transformer delta versus the best baseline is -0.0182828153. The generated
verdict is `raw-opcode-transformer-research-only-not-promotable`.

Permitted interpretation: raw method-level opcode sequences alone did not
justify a learned promotion on this small case-heldout corpus. Future work
requires more APK cases, richer class/package context, and APK-level
aggregation.

## Report-Only Integration Proof

A two-target smoke test compared default reports with opt-in hybrid/AI reports
for F-Droid and Aegis Authenticator.

- targets: 2;
- hybrid sections visible: true;
- detected components unchanged: true;
- selected versions unchanged: true;
- CycloneDX component content unchanged: true;
- vulnerability output unchanged: true;
- default matcher unchanged: true.

The integration flag is `--include-hybrid-ai-assistance`. This proves that AI
evidence can be displayed without obtaining matcher, SBOM, or vulnerability
authority.

## Metric Definitions

For class \(k\):

- precision is \(TP_k / (TP_k + FP_k)\);
- recall is \(TP_k / (TP_k + FN_k)\);
- class F1 is the harmonic mean of precision and recall;
- macro-F1 is the arithmetic mean of class F1 values, giving each label equal
  weight;
- accuracy is the fraction of all rows classified correctly.

Macro-F1 is emphasized because the six structured labels are imbalanced and
the raw-opcode experiment contains seven semantic classes. Accuracy is still
reported because it is used by the generated baselines and integration
artifacts.

## Frozen Artifact Hashes

| Artifact | SHA-256 |
|---|---|
| `data/results/experiments/ai-r8-assistant/training-dataset.json` | `5E7A9C762DC1D4F1F6BA379DFF81F3774E417571E1A7ED3C150ABB029A501507` |
| `data/results/experiments/ai-r8-assistant/metrics.json` | `72D4B7241AE79A57673D90BA72B0351538999F50BFF448345452E49EC6362E57` |
| `data/results/experiments/ai-r8-dl-prototype/token-corpus.json` | `545D455120F912F8DB644EAE343746A38C63490D5DC57972D924A6C133684388` |
| `data/results/experiments/ai-r8-dl-prototype/token-corpus-mvp-safe.json` | `15EBA8314F7F763D9B70D398DB5AEC2DEE1D59A1671330BB5FF53702671F1E44` |
| `data/results/experiments/ai-r8-dl-prototype/metrics.json` | `67F3C3362F3549961291FDD9482052485A63803A35536961D0FED2169A02E077` |
| `data/results/experiments/ai-r8-dl-prototype/metrics-mvp-safe.json` | `9EA2F1F321D8BF553D14E87843AFE83CC36F76D3300AD4D98AB72B0736B23EDB` |
| `data/results/experiments/ai-r8-raw-opcode-prototype/raw-opcode-corpus.json` | `311EFBD8C47FADA78DD41C309F363FE2AF0AC335674B4F5EB9549200FAEF0277` |
| `data/results/experiments/ai-r8-raw-opcode-prototype/metrics.json` | `D10084C8140E202A8F4A2AF7C53E8FF4D2E8D15BC83B297841B124E28961A42C` |
| `data/results/experiments/ai-r8-independent-corpus/independent-corpus.json` | `5BA89C342D079D181CBEA6D1626345BEDED2E0C3253F8297C94052C30CCE5ED9` |
| `data/results/evaluation/ai-r8-mvp-integration-gate.json` | `182C7626C23E1AB373F83E1AD99DB2EEC50A702CC0B736F06DCABE5AEB011931` |
| `data/results/evaluation/final-hybrid-ai-demo-smoke.json` | `D50AE721321AA7BD57E10B26DE1FEBB45FFDC4BBE2EBF5C48E111ECEE1460113` |

## Thesis Claim Boundary

Chapter 3 may state that:

- a trained Random Forest provides useful report-only triage over grouped
  project evidence;
- structured-token Transformers were implemented and evaluated;
- removing source/context shortcuts reduces the Transformer score from 0.977
  to 0.882 macro-F1;
- the raw-opcode Transformer failed to beat logistic regression;
- report integration leaves authoritative outputs unchanged.

Chapter 3 must not state that:

- AI identifies exact Maven versions from unseen APKs;
- 0.977 macro-F1 is deployment performance;
- the dataset is externally independent;
- raw opcode learning improved the matcher;
- AI changes SBOM components or confirms vulnerabilities.
