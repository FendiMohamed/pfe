# AI-Assisted R8 Method Selection

Status: Phase 6A classical ML implementation added as report-only infrastructure; Phase 6B DL/Transformer remains isolated research prototype scaffolding.

This document explains why the project now uses an AI-assisted R8 layer without allowing AI to become the final SBOM, version, or CVE authority.

## ML vs DL

Classical ML uses manually engineered features and relatively small models. In this project, the Phase 6A assistant uses matcher and diagnostic features that already exist in the evaluation artifacts: score gaps, package/class/method/opcode/literal/dependency signals, matched element counts, R8/minified flags, and clean/partial/boundary case classes.

Deep learning learns representations from larger token or graph inputs. The Phase 6B prototype is LibAttention-inspired: it is designed around opcode/DEX token sequences and a small Transformer encoder. That is useful for demonstrating DL knowledge, but it needs more training data, ablation, and independent validation before it can influence reports.

## Research Basis

LibAttention justifies learned code representations for R8 robustness because it reports improved detection under R8-obfuscated settings. Its strongest fit here is identity and risk assistance, not exact Maven version authority.

ObfDetector and TPL-Benchmark justify caution. Their results show that hard modern obfuscation can sharply reduce version-level reliability. This means an AI layer must be framed as assistance and triage, not as solved exact-version recovery.

LibHunter, SAD, ATVHunter, and LibMD justify explainable multi-scale evidence before trusting AI output. They point toward class dependency structure, opcode/basic-block evidence, call-site behavior, literal/context cues, and probabilistic confidence. Phase 6A uses those signals as feature columns where current artifacts expose them.

## Decision

The default matcher remains unchanged.

Phase 6A is implemented first because it is explainable, fast, compatible with current artifacts, and easy to evaluate by grouped case splits. It trains a `RandomForestClassifier` when optional dependencies are installed and writes report-only suggestions.

Phase 6B is isolated because a Transformer over opcode/DEX sequences is more research-heavy. It is kept out of `generate-report` until it clearly outperforms Phase 6A and passes controlled, clean-real, partial-real, and boundary controls.

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
```

Default artifacts:

```text
data/results/experiments/ai-r8-assistant/training-dataset.json
data/results/experiments/ai-r8-assistant/training-dataset.csv
data/results/experiments/ai-r8-assistant/model.joblib
data/results/experiments/ai-r8-assistant/metrics.json
data/results/experiments/ai-r8-assistant/suggestions.json
docs/evaluation/AI_R8_ASSISTANT_DIAGNOSTICS.md
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
docs/evaluation/AI_R8_DL_PROTOTYPE.md
```

The model family is `torch.nn.TransformerEncoder`, with the task framed as binary or multiclass identity-risk classification. It is not exact-version authority.

## PhD Value

This layer supports a PhD application because it shows the complete AI workflow:

- research-backed method selection;
- dataset construction from real project evidence;
- explicit label taxonomy;
- feature engineering;
- grouped train/validation/test split by APK case;
- RandomForest training path;
- baselines and confusion-matrix reporting;
- report-only deployment boundary;
- isolated DL/Transformer prototype;
- limitations and ablation-ready artifacts.

The important claim is not "AI solved R8 exact versioning." The defensible claim is that the project added a transparent AI-assisted triage layer for hard R8 and matcher-recall cases while preserving SBOM and vulnerability honesty.

