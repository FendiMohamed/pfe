# AI-Assisted R8 Method Selection

Status: Phase 6A classical ML implementation is trained and report-only; Phase 6B DL/Transformer is trained as an isolated structured-token research prototype; a stricter MVP-safe/source-free Transformer run now exists; follow-up corpus artifacts include a larger project-heldout manifest, a bounded raw DEX/opcode method-sequence corpus, and an honest case-heldout raw-opcode Transformer run.

This document explains why the project now uses an AI-assisted R8 layer without allowing AI to become the final SBOM, version, or CVE authority.

## ML vs DL

Classical ML uses manually engineered features and relatively small models. In this project, the Phase 6A assistant uses matcher and diagnostic features that already exist in the evaluation artifacts: score gaps, package/class/method/opcode/literal/dependency signals, matched element counts, R8/minified flags, and clean/partial/boundary case classes.

Deep learning learns representations from larger token or graph inputs. The Phase 6B prototype is LibAttention-inspired and uses a small Transformer encoder. In the current implementation, its main trained model uses a structured-token view of project evidence rows rather than raw smali pretraining. A stricter MVP-safe profile removes source-version tokens, raw candidate-version tokens, source-validation-only flags, source-rank features, and diagnostic context labels; it still reaches test macro-F1 `0.882` on the 20,523-row local dataset, so it is useful as report-only risk-triage evidence. A bounded raw DEX/opcode corpus and raw-opcode Transformer run also exist, but the case-heldout raw-opcode result does not beat the opcode-count baseline. It therefore needs larger independent collection, richer context, model iteration, and validation before it can influence reports.

## Research Basis

LibAttention justifies learned code representations for R8 robustness because it reports improved detection under R8-obfuscated settings. Its strongest fit here is identity and risk assistance, not exact Maven version authority.

ObfDetector and TPL-Benchmark justify caution. Their results show that hard modern obfuscation can sharply reduce version-level reliability. This means an AI layer must be framed as assistance and triage, not as solved exact-version recovery.

LibHunter, SAD, ATVHunter, and LibMD justify explainable multi-scale evidence before trusting AI output. They point toward class dependency structure, opcode/basic-block evidence, call-site behavior, literal/context cues, and probabilistic confidence. Phase 6A uses those signals as feature columns where current artifacts expose them.

## Decision

The default matcher remains unchanged.

Phase 6A is implemented first because it is explainable, fast, compatible with current artifacts, and easy to evaluate by grouped case splits. It trains a `RandomForestClassifier` when optional dependencies are installed and writes report-only suggestions.

Phase 6B is isolated because a Transformer path is more research-heavy. The current trained prototype classifies identity-risk labels from structured evidence tokens, `docs/evaluation/AI_R8_DL_PROTOTYPE_MVP_SAFE.md` records the stricter source-free structured-token run, `docs/evaluation/AI_R8_RAW_OPCODE_CORPUS.md` provides raw opcode sequences, and `docs/evaluation/AI_R8_RAW_OPCODE_TRANSFORMER.md` records the first case-heldout raw-opcode training run. It remains kept out of matcher/SBOM authority because the integration gate only approves report-only assistance; a future raw-code model would need to outperform simple baselines and pass controlled, clean-real, partial-real, and boundary controls.

## Authority Boundaries

The AI assistant may recommend:

- `suggest_report_only`
- `suppress_uncertain`
- `risk_only`

The AI assistant may not:

- emit confirmed exact versions;
- change CycloneDX SBOM components;
- change selected versions;
- change OSV/CVE labels;
- change source-validation metrics.

`confirmed_exact` is a training label only. It teaches the model what strong rows look like, but it is not an allowed AI report action.

## Phase 6A Implementation

Commands:

```powershell
apk-sbom ai-r8-build-dataset
apk-sbom ai-r8-train
apk-sbom ai-r8-suggest
apk-sbom ai-r8-final-eval
apk-sbom ai-r8-integration-gate
```

Default artifacts:

```text
data/results/experiments/ai-r8-assistant/training-dataset.json
data/results/experiments/ai-r8-assistant/training-dataset.csv
data/results/experiments/ai-r8-assistant/model.joblib
data/results/experiments/ai-r8-assistant/metrics.json
data/results/experiments/ai-r8-assistant/suggestions.json
docs/evaluation/AI_R8_ASSISTANT_DIAGNOSTICS.md
docs/evaluation/AI_R8_FINAL_EVALUATION.md
docs/evaluation/AI_R8_MVP_INTEGRATION_GATE.md
```

Optional dependency:

```powershell
pip install -e .[ml]
```

If `scikit-learn` and `joblib` are unavailable, the command writes an explicit skipped metrics file and the suggestion builder uses a conservative label fallback. This preserves reproducibility on minimal machines while making the missing training dependency visible.

## Report Integration

Report integration is opt-in:

```powershell
apk-sbom generate-report --include-ai-r8-suggestions --ai-r8-suggestions-json data/results/experiments/ai-r8-assistant/suggestions.json
```

The report adds:

```text
AI-Assisted R8 Suggestions
Report-only: true
```

The JSON report adds `ai_r8_assistance` only when the flag is used. Default reports remain unchanged.

The final ML/DL evidence package can be regenerated from the MVP CLI:

```powershell
apk-sbom ai-r8-final-eval
```

This command combines the Phase 6A RandomForest metrics, Phase 6B Transformer prototype metrics, follow-up corpus evidence, and report-only guardrail proof. `apk-sbom ai-r8-integration-gate` then answers the MVP question directly: report-only AI assistance is ready, but matcher/SBOM/CVE authority is not. These commands still do not change matcher scoring, SBOM output, or vulnerability labels.

## Phase 6B Prototype

The DL prototype is intentionally not a default CLI command and is not wired into `generate-report`.

Scripts:

```text
scripts/build_ai_r8_token_corpus.py
scripts/train_ai_r8_tiny_transformer.py
```

Output:

```text
data/results/experiments/ai-r8-dl-prototype/metrics.json
data/results/experiments/ai-r8-dl-prototype/metrics-mvp-safe.json
data/results/experiments/ai-r8-dl-prototype/token-corpus.json
data/results/experiments/ai-r8-dl-prototype/token-corpus-mvp-safe.json
docs/evaluation/AI_R8_DL_PROTOTYPE.md
docs/evaluation/AI_R8_DL_PROTOTYPE_MVP_SAFE.md
```

The model family is `torch.nn.TransformerEncoder`, with the task framed as multiclass identity-risk classification. It is not exact-version authority. The full structured-token model reaches test macro-F1 `0.977`; the MVP-safe/source-free structured-token model reaches test macro-F1 `0.882`; the raw-opcode Transformer reaches only `0.110`, below its opcode-count baseline `0.128`. Therefore the current MVP can present DL as report-only AI assistance and PhD-ready experimentation, while raw DEX/opcode DL remains future work rather than a production APK detector.

## PhD Value

This layer supports a PhD application because it shows the complete AI workflow:

- research-backed method selection;
- dataset construction from real project evidence;
- explicit label taxonomy;
- feature engineering;
- grouped train/validation/test split by APK case;
- RandomForest training path;
- baselines, feature importance, ablation, and confusion-matrix reporting;
- report-only deployment boundary;
- isolated trained DL/Transformer prototype;
- limitations and ablation-ready artifacts.

The important claim is not "AI solved R8 exact versioning." The defensible claim is that the project added a transparent AI-assisted triage layer for hard R8 and matcher-recall cases while preserving SBOM and vulnerability honesty.
