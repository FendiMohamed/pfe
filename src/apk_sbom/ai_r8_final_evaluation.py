from __future__ import annotations

import json
from pathlib import Path


DEFAULT_AI_SUMMARY_JSON = Path("data/results/evaluation/ai-r8-assistant-summary.json")
DEFAULT_AI_METRICS_JSON = Path("data/results/experiments/ai-r8-assistant/metrics.json")
DEFAULT_DL_METRICS_JSON = Path("data/results/experiments/ai-r8-dl-prototype/metrics.json")
DEFAULT_REPORT_ONLY_DEMO_JSON = Path("data/results/evaluation/ai-r8-report-only-demo.json")
DEFAULT_INDEPENDENT_CORPUS_JSON = Path(
    "data/results/experiments/ai-r8-independent-corpus/independent-corpus.json"
)
DEFAULT_RAW_OPCODE_CORPUS_JSON = Path(
    "data/results/experiments/ai-r8-raw-opcode-prototype/raw-opcode-corpus.json"
)
DEFAULT_RAW_OPCODE_TRANSFORMER_METRICS_JSON = Path(
    "data/results/experiments/ai-r8-raw-opcode-prototype/metrics.json"
)
DEFAULT_OUTPUT_JSON = Path("data/results/evaluation/ai-r8-final-evaluation.json")
DEFAULT_OUTPUT_DOC = Path("docs/evaluation/AI_R8_FINAL_EVALUATION.md")


def write_final_evaluation(
    *,
    ai_summary_json: str | Path = DEFAULT_AI_SUMMARY_JSON,
    ai_metrics_json: str | Path = DEFAULT_AI_METRICS_JSON,
    dl_metrics_json: str | Path = DEFAULT_DL_METRICS_JSON,
    report_only_demo_json: str | Path = DEFAULT_REPORT_ONLY_DEMO_JSON,
    independent_corpus_json: str | Path = DEFAULT_INDEPENDENT_CORPUS_JSON,
    raw_opcode_corpus_json: str | Path = DEFAULT_RAW_OPCODE_CORPUS_JSON,
    raw_opcode_transformer_metrics_json: str | Path = (
        DEFAULT_RAW_OPCODE_TRANSFORMER_METRICS_JSON
    ),
    output_json: str | Path = DEFAULT_OUTPUT_JSON,
    output_doc: str | Path = DEFAULT_OUTPUT_DOC,
) -> dict:
    ai_summary = _load_json(ai_summary_json)
    ai_metrics = _load_json(ai_metrics_json)
    dl_metrics = _load_json(dl_metrics_json)
    report_only_demo = _load_json(report_only_demo_json)
    independent_corpus = _load_json(independent_corpus_json)
    raw_opcode_corpus = _load_json(raw_opcode_corpus_json)
    raw_opcode_transformer_metrics = _load_json(raw_opcode_transformer_metrics_json)
    payload = build_final_evaluation(
        ai_summary=ai_summary,
        ai_metrics=ai_metrics,
        dl_metrics=dl_metrics,
        report_only_demo=report_only_demo,
        independent_corpus=independent_corpus,
        raw_opcode_corpus=raw_opcode_corpus,
        raw_opcode_transformer_metrics=raw_opcode_transformer_metrics,
        sources={
            "ai_summary_json": _normalize_path(ai_summary_json),
            "ai_metrics_json": _normalize_path(ai_metrics_json),
            "dl_metrics_json": _normalize_path(dl_metrics_json),
            "report_only_demo_json": _normalize_path(report_only_demo_json),
            "independent_corpus_json": _normalize_path(independent_corpus_json),
            "raw_opcode_corpus_json": _normalize_path(raw_opcode_corpus_json),
            "raw_opcode_transformer_metrics_json": _normalize_path(
                raw_opcode_transformer_metrics_json
            ),
        },
    )

    json_path = Path(output_json)
    doc_path = Path(output_doc)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    doc_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    doc_path.write_text(build_markdown(payload), encoding="utf-8")
    return {
        "output_json": str(json_path),
        "output_doc": str(doc_path),
        "phase6a_test_macro_f1": payload["phase6a_ml"]["test_macro_f1"],
        "phase6b_test_macro_f1": payload["phase6b_dl"]["test_macro_f1"],
        "report_only_guardrail_passed": payload["report_only_proof"][
            "guardrail_passed"
        ],
    }


def build_final_evaluation(
    *,
    ai_summary: dict,
    ai_metrics: dict,
    dl_metrics: dict,
    report_only_demo: dict,
    independent_corpus: dict | None = None,
    raw_opcode_corpus: dict | None = None,
    raw_opcode_transformer_metrics: dict | None = None,
    sources: dict | None = None,
) -> dict:
    ai_model = ai_summary.get("model", {})
    ai_dataset = ai_summary.get("dataset", {})
    ai_ablation = ai_model.get("ablation_study", {}) or ai_metrics.get(
        "ablation_study", {}
    )
    dl_test = dl_metrics.get("test", {})
    dl_dataset = dl_metrics.get("dataset", {})
    demo_comparison = report_only_demo.get("comparison", {})
    independent_summary = (independent_corpus or {}).get("summary", {})
    raw_opcode_summary = (raw_opcode_corpus or {}).get("summary", {})
    raw_opcode_transformer_test = (raw_opcode_transformer_metrics or {}).get("test", {})
    raw_opcode_transformer_comparison = (
        raw_opcode_transformer_metrics or {}
    ).get("baseline_comparison", {})
    report_only_guardrail_passed = all(
        [
            demo_comparison.get("detected_components_unchanged") is True,
            demo_comparison.get("sbom_semantic_content_unchanged") is True,
            demo_comparison.get("vulnerability_labels_unchanged") is True,
            report_only_demo.get("ai_report", {}).get("report_only") is True,
        ]
    )
    return {
        "schema_version": "ai-r8-final-evaluation-v1",
        "report_only": True,
        "production_wiring": {
            "phase6a_generate_report": "opt-in report section only",
            "phase6b_generate_report": "disabled",
            "sbom_or_cve_authority": "none",
        },
        "phase6a_ml": {
            "status": ai_model.get("status") or ai_metrics.get("status"),
            "model_type": ai_model.get("model_type") or ai_metrics.get("model_type"),
            "model_version": ai_model.get("model_version")
            or ai_metrics.get("model_version"),
            "dataset_rows": ai_dataset.get("rows"),
            "dataset_labels": ai_dataset.get("labels", {}),
            "split": ai_model.get("split") or ai_metrics.get("split", {}),
            "test_macro_f1": ai_model.get("test_macro_f1")
            or ai_metrics.get("test", {}).get("macro_f1"),
            "test_accuracy": ai_metrics.get("test", {}).get("accuracy")
            or ai_ablation.get("all_features", {}).get("test_accuracy"),
            "majority_baseline_test_accuracy": ai_model.get(
                "majority_baseline_test_accuracy"
            ),
            "score_threshold_baseline_test_accuracy": ai_model.get(
                "score_threshold_baseline_test_accuracy"
            ),
            "top_feature_importance": ai_model.get("top_feature_importance", []),
            "ablation_study": ai_ablation,
            "suggestions": ai_summary.get("suggestions", {}),
        },
        "phase6b_dl": {
            "status": dl_metrics.get("status"),
            "model_type": dl_metrics.get("model_type"),
            "task": dl_metrics.get("task"),
            "dataset_rows": dl_dataset.get("rows"),
            "vocab_size": dl_dataset.get("vocab_size"),
            "splits": dl_dataset.get("splits", {}),
            "parameters": dl_metrics.get("parameters", {}),
            "validation_macro_f1": dl_metrics.get("validation", {}).get("macro_f1"),
            "test_macro_f1": dl_test.get("macro_f1"),
            "test_accuracy": dl_test.get("accuracy"),
            "per_class": dl_test.get("per_class", {}),
            "history": dl_metrics.get("history", []),
            "limitations": dl_metrics.get("limits", []),
        },
        "follow_up_corpora": {
            "independent_corpus": {
                "status": "generated" if independent_summary else "missing",
                "rows": independent_summary.get("rows"),
                "training_eligible_rows": independent_summary.get(
                    "training_eligible_rows"
                ),
                "heldout_or_report_only_rows": independent_summary.get(
                    "heldout_or_report_only_rows"
                ),
                "unique_case_ids": independent_summary.get("unique_case_ids"),
                "unique_coordinates": independent_summary.get("unique_coordinates"),
                "external_corpus": independent_summary.get("external_corpus"),
            },
            "raw_opcode_corpus": {
                "status": "generated" if raw_opcode_summary else "missing",
                "apks_analyzed": raw_opcode_summary.get("apks_analyzed"),
                "apks_skipped": raw_opcode_summary.get("apks_skipped"),
                "method_sequence_rows": raw_opcode_summary.get(
                    "method_sequence_rows"
                ),
                "vocab_size": raw_opcode_summary.get("vocab_size"),
            },
            "raw_opcode_transformer": {
                "status": (raw_opcode_transformer_metrics or {}).get("status")
                or "missing",
                "model_type": (raw_opcode_transformer_metrics or {}).get("model_type"),
                "test_macro_f1": raw_opcode_transformer_test.get("macro_f1"),
                "test_accuracy": raw_opcode_transformer_test.get("accuracy"),
                "best_baseline": raw_opcode_transformer_comparison.get(
                    "best_baseline"
                ),
                "best_baseline_test_macro_f1": raw_opcode_transformer_comparison.get(
                    "best_baseline_test_macro_f1"
                ),
                "delta_vs_best_baseline": raw_opcode_transformer_comparison.get(
                    "delta_vs_best_baseline"
                ),
                "verdict": raw_opcode_transformer_comparison.get("verdict"),
            },
            "production_wiring": "disabled",
        },
        "report_only_proof": {
            "guardrail_passed": report_only_guardrail_passed,
            "ai_section_present": report_only_demo.get("ai_report", {}).get(
                "ai_section_present"
            ),
            "matching_rows": report_only_demo.get("ai_report", {}).get(
                "matching_rows"
            ),
            "matching_recommendation_counts": report_only_demo.get(
                "ai_report", {}
            ).get("matching_recommendation_counts", {}),
            "comparison": demo_comparison,
        },
        "presentation_claims": [
            "Phase 6A is a trained, explainable RandomForest report-only assistant.",
            "Phase 6A improves over simple baselines on a grouped case split and exposes feature-importance plus ablation evidence.",
            "Phase 6B is a trained tiny Transformer over structured project-evidence tokens, useful as a DL workflow proof but not as raw APK pretraining.",
            "The follow-up corpus artifacts make the next AI step concrete: a larger project-heldout manifest, a bounded raw DEX/opcode sequence corpus, and an honest raw-opcode Transformer training run.",
            "Neither AI track changes selected versions, CycloneDX SBOM components, vulnerability labels, or source-validation metrics.",
        ],
        "sources": sources or {},
    }


def build_markdown(payload: dict) -> str:
    ml = payload["phase6a_ml"]
    dl = payload["phase6b_dl"]
    corpora = payload.get("follow_up_corpora", {})
    proof = payload["report_only_proof"]
    lines = [
        "# AI R8 Final Evaluation",
        "",
        "Generated by `apk-sbom ai-r8-final-eval` or `scripts/build_ai_r8_final_evaluation.py`.",
        "",
        "This is the single thesis/demo entry point for the Phase 6 ML/DL layer. It combines the trained Phase 6A RandomForest assistant, the isolated Phase 6B Transformer prototype, the follow-up corpus artifacts, and the report-only guardrail proof.",
        "",
        "## Non-Negotiable Boundary",
        "",
        "- AI output is report-only.",
        "- AI does not change selected versions, detected components, CycloneDX SBOM output, CVE/OSV labels, or source-validation metrics.",
        "- Phase 6B may be surfaced as status-only evidence by the hybrid/AI report flag, but its production decision wiring remains disabled.",
        "",
        "## Phase 6A: Classical ML",
        "",
        "| Field | Value |",
        "|---|---:|",
        f"| Status | `{ml.get('status')}` |",
        f"| Model | `{ml.get('model_type')}` |",
        f"| Dataset rows | `{ml.get('dataset_rows')}` |",
        f"| Test macro-F1 | `{ml.get('test_macro_f1')}` |",
        f"| Test accuracy | `{ml.get('test_accuracy')}` |",
        f"| Majority baseline test accuracy | `{ml.get('majority_baseline_test_accuracy')}` |",
        f"| Score-threshold baseline test accuracy | `{ml.get('score_threshold_baseline_test_accuracy')}` |",
        f"| Suggestion rows | `{ml.get('suggestions', {}).get('suggestion_rows')}` |",
        "",
        "### Feature Importance",
        "",
        "| Feature | Importance |",
        "|---|---:|",
    ]
    for row in ml.get("top_feature_importance", [])[:10]:
        lines.append(f"| `{row.get('feature')}` | {row.get('importance')} |")
    lines.extend(
        [
            "",
            "### Ablation",
            "",
            "| Variant | Features | Test macro-F1 | Test accuracy |",
            "|---|---:|---:|---:|",
        ]
    )
    for name, row in sorted(ml.get("ablation_study", {}).items()):
        lines.append(
            "| "
            f"`{name}` | "
            f"{row.get('feature_count')} | "
            f"{row.get('test_macro_f1')} | "
            f"{row.get('test_accuracy')} |"
        )
    lines.extend(
        [
            "",
            "## Phase 6B: DL Prototype",
            "",
            "| Field | Value |",
            "|---|---:|",
            f"| Status | `{dl.get('status')}` |",
            f"| Model | `{dl.get('model_type')}` |",
            f"| Dataset rows | `{dl.get('dataset_rows')}` |",
            f"| Vocabulary size | `{dl.get('vocab_size')}` |",
            f"| Validation macro-F1 | `{dl.get('validation_macro_f1')}` |",
            f"| Test macro-F1 | `{dl.get('test_macro_f1')}` |",
            f"| Test accuracy | `{dl.get('test_accuracy')}` |",
            "",
            "The DL prototype uses structured project-evidence tokens from the current evaluation rows. It is a complete Transformer training/evaluation workflow, but it is not APK-only exact-version authority.",
            "",
            "## Follow-Up AI Corpora",
            "",
            "| Corpus | Status | Primary value | Secondary value | Notes |",
            "|---|---|---:|---:|---|",
            "| Independent project-heldout manifest | "
            f"`{corpora.get('independent_corpus', {}).get('status')}` | "
            f"{corpora.get('independent_corpus', {}).get('rows')} | "
            f"{corpora.get('independent_corpus', {}).get('heldout_or_report_only_rows')} | "
            "Training rows remain separated from heldout/report-only lanes. |",
            "| Raw DEX/opcode method corpus | "
            f"`{corpora.get('raw_opcode_corpus', {}).get('status')}` | "
            f"{corpora.get('raw_opcode_corpus', {}).get('method_sequence_rows')} | "
            f"{corpora.get('raw_opcode_corpus', {}).get('apks_analyzed')} | "
            "Bounded opcode sequences for future Transformer training; production wiring disabled. |",
            "| Raw DEX/opcode Transformer | "
            f"`{corpora.get('raw_opcode_transformer', {}).get('status')}` | "
            f"{corpora.get('raw_opcode_transformer', {}).get('test_macro_f1')} | "
            f"{corpora.get('raw_opcode_transformer', {}).get('best_baseline_test_macro_f1')} | "
            f"`{corpora.get('raw_opcode_transformer', {}).get('verdict')}` |",
            "",
            "### DL Per-Class Metrics",
            "",
            "| Label | Precision | Recall | F1 | Support |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for label, row in dl.get("per_class", {}).items():
        lines.append(
            "| "
            f"`{label}` | "
            f"{row.get('precision')} | "
            f"{row.get('recall')} | "
            f"{row.get('f1')} | "
            f"{row.get('support')} |"
        )
    lines.extend(
        [
            "",
            "## Report-Only Proof",
            "",
            "| Check | Value |",
            "|---|---:|",
            f"| Guardrail passed | `{proof.get('guardrail_passed')}` |",
            f"| AI section present | `{proof.get('ai_section_present')}` |",
            f"| Matching AI rows | `{proof.get('matching_rows')}` |",
            f"| Recommendation counts | `{json.dumps(proof.get('matching_recommendation_counts', {}), sort_keys=True)}` |",
        ]
    )
    for key, value in sorted(proof.get("comparison", {}).items()):
        lines.append(f"| `{key}` | `{value}` |")
    lines.extend(
        [
            "",
            "## Presentation Claims",
            "",
        ]
    )
    for claim in payload.get("presentation_claims", []):
        lines.append(f"- {claim}")
    lines.extend(
        [
            "",
            "## Source Artifacts",
            "",
        ]
    )
    for key, value in sorted(payload.get("sources", {}).items()):
        lines.append(f"- `{key}`: `{value}`")
    lines.append("")
    return "\n".join(lines)


def _load_json(path: str | Path) -> dict:
    file_path = Path(path)
    if not file_path.exists():
        return {}
    return json.loads(file_path.read_text(encoding="utf-8"))


def _normalize_path(path: str | Path) -> str:
    return Path(path).as_posix()
