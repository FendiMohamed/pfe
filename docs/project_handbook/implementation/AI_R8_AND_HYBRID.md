# AI/R8 and Hybrid Experiments

## Why AI was added

Hard R8 cases contain patterns across score margins, feature survival,
obfuscation indicators, and diagnostic categories. A learned model may help
triage these cases even when it is not safe to select a version.

## Phase 6A: RandomForest assistant

Primary file:
[ai_r8_assistant.py](../../../src/apk_sbom/ai_r8_assistant.py)

The pipeline builds a labeled dataset from existing project evidence, groups
splits by `case_id`, trains an optional `RandomForestClassifier`, and emits
actions such as:

- suggest report-only;
- suppress uncertain wording;
- risk only;
- boundary/do not suggest.

Current test macro-F1 is `0.708`. The assistant produces report annotations,
not matcher decisions.

## Phase 6B: structured-token Transformer

A small `torch.nn.TransformerEncoder` was trained over structured project
evidence tokens.

- Full structured-token profile: macro-F1 `0.977`.
- MVP-safe/source-free profile: macro-F1 `0.882`, accuracy `0.907`.

The full result is kept as research evidence because contextual shortcuts may
inflate performance. The MVP-safe profile removes source version, raw candidate
version, source rank, source-validation role, and diagnostic-context shortcuts.

## Raw-opcode Transformer

A separate corpus contains `1680` method-level opcode sequences from `14`
APKs. Under a case-heldout split, the Transformer reached macro-F1 `0.110`,
below the opcode-count baseline `0.128`.

This negative result is important: deep learning was trained and measured, but
did not earn promotion.

## Hybrid matcher router

Primary file:
[hybrid_matcher_router.py](../../../src/apk_sbom/hybrid_matcher_router.py)

The router categorizes hard rows and recommends which diagnostic family should
inspect them, such as version-band, structural recall, reference growth, or
boundary handling. It routes investigation; it does not rerank production
components.

## Integration gate

The gate permits AI for report-only risk triage and blocks it from:

- selected-version authority;
- CycloneDX component authority;
- CVE-label authority;
- source-validation metric authority.

The reason is straightforward: no strict APK-only promotion candidate passed
all target/control requirements, and raw-opcode DL did not beat its baseline.

## Reproduce and inspect

- [AI/R8 method selection](../../research/AI_R8_ASSISTED_METHOD_SELECTION.md)
- [Final AI evaluation](../../evaluation/AI_R8_FINAL_EVALUATION.md)
- [MVP integration gate](../../evaluation/AI_R8_MVP_INTEGRATION_GATE.md)
- [Final AI defense demo](../../evaluation/FINAL_AI_DEFENSE_DEMO.md)
- [Experiment and AI commands](../commands/EXPERIMENT_AND_AI_CLI_REFERENCE.md)
