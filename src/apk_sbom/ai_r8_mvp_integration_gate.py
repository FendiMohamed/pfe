from __future__ import annotations

import json
from pathlib import Path
from typing import Any


DEFAULT_AI_METRICS_JSON = Path("data/results/experiments/ai-r8-assistant/metrics.json")
DEFAULT_AI_SUGGESTIONS_JSON = Path(
    "data/results/experiments/ai-r8-assistant/suggestions.json"
)
DEFAULT_STRUCTURED_DL_METRICS_JSON = Path(
    "data/results/experiments/ai-r8-dl-prototype/metrics.json"
)
DEFAULT_MVP_SAFE_DL_METRICS_JSON = Path(
    "data/results/experiments/ai-r8-dl-prototype/metrics-mvp-safe.json"
)
DEFAULT_RAW_OPCODE_DL_METRICS_JSON = Path(
    "data/results/experiments/ai-r8-raw-opcode-prototype/metrics.json"
)
DEFAULT_INDEPENDENT_CORPUS_JSON = Path(
    "data/results/experiments/ai-r8-independent-corpus/independent-corpus.json"
)
DEFAULT_HYBRID_PRODUCTION_JSON = Path(
    "data/results/evaluation/hybrid-ai-production-reporting.json"
)
DEFAULT_FINAL_SMOKE_JSON = Path(
    "data/results/evaluation/final-hybrid-ai-demo-smoke.json"
)
DEFAULT_STRICT_GATE_MATRIX_JSON = Path(
    "data/results/experiments/r8-strict-apk-promotion-gate-matrix.json"
)
DEFAULT_OUTPUT_JSON = Path("data/results/evaluation/ai-r8-mvp-integration-gate.json")
DEFAULT_OUTPUT_DOC = Path("docs/evaluation/AI_R8_MVP_INTEGRATION_GATE.md")


def write_integration_gate(
    *,
    ai_metrics_json: str | Path = DEFAULT_AI_METRICS_JSON,
    ai_suggestions_json: str | Path = DEFAULT_AI_SUGGESTIONS_JSON,
    structured_dl_metrics_json: str | Path = DEFAULT_STRUCTURED_DL_METRICS_JSON,
    mvp_safe_dl_metrics_json: str | Path = DEFAULT_MVP_SAFE_DL_METRICS_JSON,
    raw_opcode_dl_metrics_json: str | Path = DEFAULT_RAW_OPCODE_DL_METRICS_JSON,
    independent_corpus_json: str | Path = DEFAULT_INDEPENDENT_CORPUS_JSON,
    hybrid_production_json: str | Path = DEFAULT_HYBRID_PRODUCTION_JSON,
    final_smoke_json: str | Path = DEFAULT_FINAL_SMOKE_JSON,
    strict_gate_matrix_json: str | Path = DEFAULT_STRICT_GATE_MATRIX_JSON,
    output_json: str | Path = DEFAULT_OUTPUT_JSON,
    output_doc: str | Path = DEFAULT_OUTPUT_DOC,
) -> dict[str, Any]:
    payload = build_payload(
        ai_metrics=_read_json(ai_metrics_json),
        ai_suggestions=_read_json(ai_suggestions_json),
        structured_dl_metrics=_read_json(structured_dl_metrics_json),
        mvp_safe_dl_metrics=_read_json(mvp_safe_dl_metrics_json),
        raw_opcode_dl_metrics=_read_json(raw_opcode_dl_metrics_json),
        independent_corpus=_read_json(independent_corpus_json),
        hybrid_production=_read_json(hybrid_production_json),
        final_smoke=_read_json(final_smoke_json),
        strict_gate_matrix=_read_json(strict_gate_matrix_json),
        sources={
            "ai_metrics_json": _normalize_path(ai_metrics_json),
            "ai_suggestions_json": _normalize_path(ai_suggestions_json),
            "structured_dl_metrics_json": _normalize_path(structured_dl_metrics_json),
            "mvp_safe_dl_metrics_json": _normalize_path(mvp_safe_dl_metrics_json),
            "raw_opcode_dl_metrics_json": _normalize_path(raw_opcode_dl_metrics_json),
            "independent_corpus_json": _normalize_path(independent_corpus_json),
            "hybrid_production_json": _normalize_path(hybrid_production_json),
            "final_smoke_json": _normalize_path(final_smoke_json),
            "strict_gate_matrix_json": _normalize_path(strict_gate_matrix_json),
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
        "output_json": _normalize_path(json_path),
        "output_doc": _normalize_path(doc_path),
        "mvp_report_only_ready": payload["mvp_integration"]["report_only_ready"],
        "mvp_matcher_authority_ready": payload["mvp_integration"][
            "matcher_authority_ready"
        ],
        "recommended_next_step": payload["mvp_integration"]["recommended_next_step"],
    }


def build_payload(
    *,
    ai_metrics: dict[str, Any],
    ai_suggestions: dict[str, Any],
    structured_dl_metrics: dict[str, Any],
    mvp_safe_dl_metrics: dict[str, Any],
    raw_opcode_dl_metrics: dict[str, Any],
    independent_corpus: dict[str, Any],
    hybrid_production: dict[str, Any],
    final_smoke: dict[str, Any],
    strict_gate_matrix: dict[str, Any],
    sources: dict[str, str] | None = None,
) -> dict[str, Any]:
    corpus_summary = independent_corpus.get("summary", {})
    rf = random_forest_summary(ai_metrics, ai_suggestions)
    structured_dl = dl_summary(structured_dl_metrics, name="structured-token-transformer")
    mvp_safe_dl = dl_summary(mvp_safe_dl_metrics, name="mvp-safe-token-transformer")
    raw_opcode_dl = raw_opcode_summary(raw_opcode_dl_metrics)
    report_guardrails = report_only_guardrails(hybrid_production, final_smoke)
    strict_gate = strict_gate_summary(strict_gate_matrix)
    model_decisions = {
        "phase6a_random_forest": decide_random_forest(rf, report_guardrails),
        "phase6b_structured_transformer": decide_structured_dl(structured_dl),
        "phase6b_mvp_safe_transformer": decide_mvp_safe_dl(
            mvp_safe_dl,
            report_guardrails,
        ),
        "raw_opcode_transformer": decide_raw_opcode(raw_opcode_dl),
        "matcher_or_sbom_authority": decide_matcher_authority(
            strict_gate,
            raw_opcode_dl,
            report_guardrails,
        ),
    }
    report_only_ready = (
        model_decisions["phase6a_random_forest"]["decision"]
        == "keep-integrated-report-only"
        and report_guardrails["passed"]
    )
    matcher_ready = model_decisions["matcher_or_sbom_authority"]["decision"] == (
        "candidate-for-guarded-production-authority"
    )
    return {
        "schema_version": "ai-r8-mvp-integration-gate-v1",
        "report_only": True,
        "default_matcher_unchanged": True,
        "largest_local_dataset": {
            "rows": corpus_summary.get("rows"),
            "training_eligible_rows": corpus_summary.get("training_eligible_rows"),
            "heldout_or_report_only_rows": corpus_summary.get(
                "heldout_or_report_only_rows"
            ),
            "unique_case_ids": corpus_summary.get("unique_case_ids"),
            "unique_coordinates": corpus_summary.get("unique_coordinates"),
            "external_corpus": corpus_summary.get("external_corpus"),
            "independence_level": corpus_summary.get("independence_level"),
        },
        "models": {
            "phase6a_random_forest": rf,
            "phase6b_structured_transformer": structured_dl,
            "phase6b_mvp_safe_transformer": mvp_safe_dl,
            "raw_opcode_transformer": raw_opcode_dl,
        },
        "report_only_guardrails": report_guardrails,
        "strict_apk_promotion_gates": strict_gate,
        "model_decisions": model_decisions,
        "mvp_integration": {
            "report_only_ready": report_only_ready,
            "matcher_authority_ready": matcher_ready,
            "sbom_or_cve_authority_ready": False,
            "current_mvp_integration_level": (
                "production-report-only-ai-assistance"
                if report_only_ready
                else "diagnostic-only"
            ),
            "safe_to_integrate_now": [
                "RandomForest report-only suggestions",
                "Hybrid router report-only strategy section",
                "Structured DL status and metrics as research evidence",
            ]
            if report_only_ready
            else [],
            "blocked_from_integration": [
                "automatic matcher selected-version changes",
                "automatic CycloneDX SBOM component or version changes",
                "automatic CVE/OSV vulnerability-label changes",
                "raw-opcode Transformer decision authority",
            ],
            "recommended_next_step": (
                "ship-report-only-ai-in-mvp-and-present-authority-boundary"
                if report_only_ready and not matcher_ready
                else "collect-more-independent-apk-controls-before-promotion"
            ),
        },
        "promotion_policy": [
            "ML/DL may assist report wording, prioritization, and diagnostics.",
            "ML/DL cannot confirm exact Maven versions without matcher/source-free controls.",
            "SBOM and vulnerability outputs remain owned by the deterministic matcher and CVE lookup.",
            "A future production promotion requires nonzero strict APK-only candidates and a live regression suite.",
        ],
        "sources": sources or {},
    }


def random_forest_summary(
    metrics: dict[str, Any],
    suggestions: dict[str, Any],
) -> dict[str, Any]:
    test = metrics.get("test", {})
    ablation = metrics.get("ablation_study", {})
    all_features = ablation.get("all_features", {})
    baselines = metrics.get("baseline_comparison", {})
    majority = baselines.get("majority_class", {})
    threshold = baselines.get("score_threshold_rule", {})
    test_accuracy = test.get("accuracy") or all_features.get("test_accuracy")
    baseline_accuracy = max(
        _float_or_zero(majority.get("test_accuracy")),
        _float_or_zero(threshold.get("test_accuracy")),
    )
    return {
        "status": metrics.get("status"),
        "model_type": metrics.get("model_type"),
        "dataset_rows": metrics.get("dataset", {}).get("rows"),
        "test_macro_f1": test.get("macro_f1"),
        "test_accuracy": test_accuracy,
        "best_baseline_test_accuracy": baseline_accuracy,
        "accuracy_delta_vs_best_baseline": (
            _float_or_zero(test_accuracy) - baseline_accuracy
        ),
        "suggestion_rows": suggestions.get("summary", {}).get("suggestion_rows"),
        "recommendation_counts": suggestions.get("summary", {}).get(
            "recommendation_counts",
            {},
        ),
        "ablation_best_macro_f1": max(
            (_float_or_zero(row.get("test_macro_f1")) for row in ablation.values()),
            default=0.0,
        ),
        "top_feature_importance": metrics.get("feature_importance", [])[:5],
        "authority": "report-only-suggestions",
    }


def dl_summary(metrics: dict[str, Any], *, name: str) -> dict[str, Any]:
    dataset = metrics.get("dataset", {})
    test = metrics.get("test", {})
    return {
        "name": name,
        "status": metrics.get("status"),
        "model_type": metrics.get("model_type"),
        "profile": dataset.get("profile") or metrics.get("profile"),
        "mvp_safe": bool(dataset.get("mvp_safe") or metrics.get("mvp_safe")),
        "dataset_rows": dataset.get("rows"),
        "vocab_size": dataset.get("vocab_size"),
        "test_macro_f1": test.get("macro_f1"),
        "test_accuracy": test.get("accuracy"),
        "validation_macro_f1": metrics.get("validation", {}).get("macro_f1"),
        "production_wiring": metrics.get("production_wiring", "disabled"),
        "authority": "research-status-only",
    }


def raw_opcode_summary(metrics: dict[str, Any]) -> dict[str, Any]:
    comparison = metrics.get("baseline_comparison", {})
    test = metrics.get("test", {})
    dataset = metrics.get("dataset", {})
    return {
        "status": metrics.get("status"),
        "model_type": metrics.get("model_type"),
        "method_sequence_rows": dataset.get("method_sequence_rows"),
        "apks_analyzed": dataset.get("apks_analyzed"),
        "test_macro_f1": test.get("macro_f1"),
        "test_accuracy": test.get("accuracy"),
        "best_baseline": comparison.get("best_baseline"),
        "best_baseline_test_macro_f1": comparison.get(
            "best_baseline_test_macro_f1"
        ),
        "delta_vs_best_baseline": comparison.get("delta_vs_best_baseline"),
        "verdict": comparison.get("verdict"),
        "authority": "research-only-not-matcher-authority",
    }


def report_only_guardrails(
    hybrid_production: dict[str, Any],
    final_smoke: dict[str, Any],
) -> dict[str, Any]:
    smoke_summary = final_smoke.get("summary", {})
    passed = all(
        [
            hybrid_production.get("report_only") is True,
            hybrid_production.get("default_matcher_unchanged") is True,
            hybrid_production.get("verdict")
            == "promoted-to-production-report-only-not-matcher-authority",
            smoke_summary.get("all_outputs_unchanged") is True,
            smoke_summary.get("all_hybrid_sections_visible") is True,
        ]
    )
    return {
        "passed": passed,
        "hybrid_reporting_verdict": hybrid_production.get("verdict"),
        "all_outputs_unchanged": smoke_summary.get("all_outputs_unchanged"),
        "all_hybrid_sections_visible": smoke_summary.get(
            "all_hybrid_sections_visible"
        ),
        "smoke_targets": smoke_summary.get("targets"),
        "default_matcher_unchanged": hybrid_production.get(
            "default_matcher_unchanged"
        ),
    }


def strict_gate_summary(payload: dict[str, Any]) -> dict[str, Any]:
    profiles = payload.get("profiles", [])
    total_eligible_rows = sum(
        int(profile.get("eligible_rows_after_strict_controls") or 0)
        for profile in profiles
    )
    max_gate_pass_rows = max(
        (int(profile.get("gate_pass_rows") or 0) for profile in profiles),
        default=0,
    )
    return {
        "production_promotion": payload.get("production_promotion"),
        "profiles": len(profiles),
        "max_gate_pass_rows_before_controls": max_gate_pass_rows,
        "eligible_rows_after_strict_controls": total_eligible_rows,
        "strict_candidates_available": total_eligible_rows > 0,
        "default_matcher_unchanged": payload.get("default_matcher_unchanged"),
    }


def decide_random_forest(
    rf: dict[str, Any],
    guardrails: dict[str, Any],
) -> dict[str, Any]:
    trained = rf.get("status") == "trained"
    macro_f1 = _float_or_zero(rf.get("test_macro_f1"))
    improves = _float_or_zero(rf.get("accuracy_delta_vs_best_baseline")) > 0
    ready = trained and macro_f1 >= 0.60 and improves and guardrails["passed"]
    return {
        "decision": (
            "keep-integrated-report-only" if ready else "diagnostic-only-retrain-needed"
        ),
        "reason": (
            "trained model beats simple baselines and report-only smoke proves no output changes"
            if ready
            else "model or guardrails did not pass report-only integration criteria"
        ),
        "allowed_authority": ["report wording", "triage prioritization"],
        "forbidden_authority": ["selected versions", "SBOM components", "CVE labels"],
    }


def decide_structured_dl(dl: dict[str, Any]) -> dict[str, Any]:
    macro_f1 = _float_or_zero(dl.get("test_macro_f1"))
    return {
        "decision": (
            "keep-as-research-status-only"
            if macro_f1 >= 0.80
            else "research-only-needs-more-training"
        ),
        "reason": (
            "strong structured-token result but full profile may contain source/context shortcuts"
            if macro_f1 >= 0.80
            else "structured-token result is not strong enough for any MVP claim"
        ),
        "allowed_authority": ["presentation evidence", "future-work comparison"],
        "forbidden_authority": ["report predictions", "matcher scoring", "SBOM output"],
    }


def decide_mvp_safe_dl(
    dl: dict[str, Any],
    guardrails: dict[str, Any],
) -> dict[str, Any]:
    macro_f1 = _float_or_zero(dl.get("test_macro_f1"))
    ready = dl.get("status") == "trained" and macro_f1 >= 0.60 and guardrails["passed"]
    return {
        "decision": (
            "candidate-for-report-only-risk-triage"
            if ready
            else "research-only-not-ready-for-mvp-suggestions"
        ),
        "reason": (
            "source-free structured tokens pass the report-only threshold"
            if ready
            else "source-free structured tokens do not yet justify MVP report suggestions"
        ),
        "allowed_authority": (
            ["future opt-in report-only risk triage"] if ready else ["research evidence"]
        ),
        "forbidden_authority": ["selected versions", "SBOM components", "CVE labels"],
    }


def decide_raw_opcode(raw: dict[str, Any]) -> dict[str, Any]:
    beats_baseline = _float_or_zero(raw.get("delta_vs_best_baseline")) > 0
    return {
        "decision": (
            "research-only-needs-larger-corpus"
            if not beats_baseline
            else "research-only-beats-baseline-but-needs-controls"
        ),
        "reason": raw.get("verdict") or "raw opcode evidence is incomplete",
        "allowed_authority": ["PhD/future-work evidence"],
        "forbidden_authority": ["report suggestions", "matcher scoring", "SBOM output"],
    }


def decide_matcher_authority(
    strict_gate: dict[str, Any],
    raw_opcode: dict[str, Any],
    guardrails: dict[str, Any],
) -> dict[str, Any]:
    ready = all(
        [
            strict_gate.get("strict_candidates_available") is True,
            _float_or_zero(raw_opcode.get("delta_vs_best_baseline")) > 0,
            guardrails.get("passed") is True,
        ]
    )
    return {
        "decision": (
            "candidate-for-guarded-production-authority"
            if ready
            else "blocked-keep-deterministic-matcher-authority"
        ),
        "reason": (
            "strict APK-only gates and raw opcode model both have positive evidence"
            if ready
            else "strict APK-only gates have no production candidates or raw opcode DL is weak"
        ),
        "allowed_authority": (
            ["none until live regression suite passes"]
            if ready
            else ["deterministic matcher remains authority"]
        ),
        "forbidden_authority": ["automatic ML/DL selected-version changes"],
    }


def build_markdown(payload: dict[str, Any]) -> str:
    integration = payload["mvp_integration"]
    corpus = payload["largest_local_dataset"]
    models = payload["models"]
    decisions = payload["model_decisions"]
    lines = [
        "# AI R8 MVP Integration Gate",
        "",
        "Generated by `apk-sbom ai-r8-integration-gate` or `scripts/build_ai_r8_mvp_integration_gate.py`.",
        "",
        "This artifact answers whether the current ML/DL work can be integrated into the MVP after training and evaluation on the largest local AI/R8 evidence set.",
        "",
        "## Verdict",
        "",
        f"- MVP report-only integration ready: `{integration['report_only_ready']}`",
        f"- MVP matcher/SBOM authority ready: `{integration['matcher_authority_ready']}`",
        f"- Current integration level: `{integration['current_mvp_integration_level']}`",
        f"- Recommended next step: `{integration['recommended_next_step']}`",
        "",
        "## Largest Local Dataset",
        "",
        "| Field | Value |",
        "|---|---:|",
    ]
    for key, value in corpus.items():
        lines.append(f"| `{key}` | `{value}` |")
    lines.extend(
        [
            "",
            "## Model Evidence",
            "",
            "| Model | Rows | Test macro-F1 | Test accuracy | Decision |",
            "|---|---:|---:|---:|---|",
        ]
    )
    rows = [
        (
            "Phase 6A RandomForest",
            models["phase6a_random_forest"],
            decisions["phase6a_random_forest"],
        ),
        (
            "Structured-token Transformer",
            models["phase6b_structured_transformer"],
            decisions["phase6b_structured_transformer"],
        ),
        (
            "MVP-safe Transformer",
            models["phase6b_mvp_safe_transformer"],
            decisions["phase6b_mvp_safe_transformer"],
        ),
        (
            "Raw-opcode Transformer",
            models["raw_opcode_transformer"],
            decisions["raw_opcode_transformer"],
        ),
    ]
    for name, model, decision in rows:
        model_rows = (
            model.get("dataset_rows")
            or model.get("method_sequence_rows")
            or model.get("suggestion_rows")
        )
        lines.append(
            "| "
            f"{name} | "
            f"`{model_rows}` | "
            f"`{model.get('test_macro_f1')}` | "
            f"`{model.get('test_accuracy')}` | "
            f"`{decision.get('decision')}` |"
        )
    lines.extend(
        [
            "",
            "## Guardrails",
            "",
            "| Gate | Value |",
            "|---|---:|",
        ]
    )
    for key, value in payload["report_only_guardrails"].items():
        lines.append(f"| `report_only.{key}` | `{value}` |")
    for key, value in payload["strict_apk_promotion_gates"].items():
        lines.append(f"| `strict_apk.{key}` | `{value}` |")
    lines.extend(
        [
            "",
            "## What Can Be Integrated",
            "",
        ]
    )
    for item in integration["safe_to_integrate_now"]:
        lines.append(f"- {item}")
    if not integration["safe_to_integrate_now"]:
        lines.append("- No AI output is ready beyond diagnostics.")
    lines.extend(
        [
            "",
            "## What Stays Blocked",
            "",
        ]
    )
    for item in integration["blocked_from_integration"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## Promotion Policy",
            "",
        ]
    )
    for item in payload["promotion_policy"]:
        lines.append(f"- {item}")
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


def _read_json(path: str | Path) -> dict[str, Any]:
    source = Path(path)
    if not source.exists():
        return {}
    return json.loads(source.read_text(encoding="utf-8"))


def _normalize_path(path: str | Path) -> str:
    return Path(path).as_posix()


def _float_or_zero(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0
