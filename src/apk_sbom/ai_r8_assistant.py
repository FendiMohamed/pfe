from __future__ import annotations

import csv
import importlib.util
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from statistics import mean
from typing import Iterable


MODEL_VERSION = "ai-r8-assistant-v1"
MODEL_RANDOM_STATE = 42

DEFAULT_EXPERIMENT_DIR = Path("data/results/experiments/ai-r8-assistant")
DEFAULT_TRAINING_DATASET_JSON = DEFAULT_EXPERIMENT_DIR / "training-dataset.json"
DEFAULT_TRAINING_DATASET_CSV = DEFAULT_EXPERIMENT_DIR / "training-dataset.csv"
DEFAULT_MODEL_PATH = DEFAULT_EXPERIMENT_DIR / "model.joblib"
DEFAULT_METRICS_JSON = DEFAULT_EXPERIMENT_DIR / "metrics.json"
DEFAULT_SUGGESTIONS_JSON = DEFAULT_EXPERIMENT_DIR / "suggestions.json"
DEFAULT_DIAGNOSTICS_DOC = Path("docs/evaluation/AI_R8_ASSISTANT_DIAGNOSTICS.md")

DEFAULT_MATCHER_RECALL_DIAGNOSTICS = Path(
    "data/results/evaluation/demo-final-v2-matcher-recall-diagnostics.json"
)
DEFAULT_TRANSPARENCY_EXPORT = Path(
    "data/results/evaluation/demo-final-transparency-export.json"
)
DEFAULT_PHASE5_DIAGNOSTICS = Path(
    "data/results/experiments/r8-phase5-scoped-trigger-diagnostics.json"
)
DEFAULT_R8_OBFUSCATION_DIAGNOSTICS = Path(
    "data/results/evaluation/r8-obfuscation-diagnostics.json"
)

LABELS = [
    "suggest_report_only",
    "suppress_uncertain",
    "risk_only",
    "confirmed_exact",
    "mismatch_or_extra",
    "boundary_do_not_suggest",
]

FEATURE_COLUMNS = [
    "best_score",
    "score_gap_to_best",
    "source_rank",
    "identity_confidence",
    "package_score",
    "class_score",
    "method_score",
    "opcode_score",
    "literal_score",
    "dependency_score",
    "matched_packages",
    "matched_classes",
    "matched_methods",
    "is_r8_or_minified",
    "is_boundary_or_limitation",
    "is_clean_real",
    "is_partial_real",
]

NUMERIC_FEATURES = {
    "best_score",
    "score_gap_to_best",
    "source_rank",
    "identity_confidence",
    "package_score",
    "class_score",
    "method_score",
    "opcode_score",
    "literal_score",
    "dependency_score",
    "matched_packages",
    "matched_classes",
    "matched_methods",
}

BOOLEAN_FEATURES = {
    "is_r8_or_minified",
    "is_boundary_or_limitation",
    "is_clean_real",
    "is_partial_real",
}


@dataclass(frozen=True)
class OptionalMlStatus:
    available: bool
    missing: list[str]


def optional_ml_status() -> OptionalMlStatus:
    missing = [
        package
        for package in ("sklearn", "joblib")
        if importlib.util.find_spec(package) is None
    ]
    return OptionalMlStatus(available=not missing, missing=missing)


def build_training_dataset(
    *,
    matcher_recall_json: str | Path = DEFAULT_MATCHER_RECALL_DIAGNOSTICS,
    transparency_json: str | Path = DEFAULT_TRANSPARENCY_EXPORT,
    phase5_json: str | Path = DEFAULT_PHASE5_DIAGNOSTICS,
    r8_obfuscation_json: str | Path = DEFAULT_R8_OBFUSCATION_DIAGNOSTICS,
) -> dict:
    matcher_payload = _load_json(matcher_recall_json)
    transparency_payload = _load_json(transparency_json)
    phase5_payload = _load_json(phase5_json)
    r8_payload = _load_json_if_exists(r8_obfuscation_json)

    case_flags = _case_flags_by_id(transparency_payload)
    rows: list[dict] = []
    rows.extend(_matcher_recall_dataset_rows(matcher_payload, case_flags))
    rows.extend(_transparency_emitted_dataset_rows(transparency_payload, case_flags))
    rows.extend(_transparency_boundary_dataset_rows(transparency_payload, case_flags))
    rows.extend(_phase5_dataset_rows(phase5_payload, case_flags))
    rows.extend(_r8_boundary_dataset_rows(r8_payload))

    rows = _deduplicate_rows(rows)
    label_counts = Counter(row["label"] for row in rows)
    row_source_counts = Counter(row["row_source"] for row in rows)

    return {
        "schema_version": "ai-r8-training-dataset-v1",
        "model_version": MODEL_VERSION,
        "report_only": True,
        "policy": [
            "Rows are derived from existing matcher-recall, transparency, Phase 5, and R8 diagnostic evidence.",
            "The assistant may suggest report-only wording, suppression, or risk labels.",
            "The assistant must not change selected versions, CycloneDX SBOM output, vulnerability labels, or source-validation metrics.",
        ],
        "sources": {
            "matcher_recall_diagnostics": str(matcher_recall_json),
            "transparency_export": str(transparency_json),
            "phase5_diagnostics": str(phase5_json),
            "r8_obfuscation_diagnostics": str(r8_obfuscation_json),
        },
        "feature_columns": FEATURE_COLUMNS,
        "label_set": LABELS,
        "summary": {
            "rows": len(rows),
            "labels": dict(sorted(label_counts.items())),
            "row_sources": dict(sorted(row_source_counts.items())),
            "case_ids": len({row["case_id"] for row in rows if row["case_id"]}),
            "coordinates": len({row["coordinate"] for row in rows if row["coordinate"]}),
        },
        "rows": rows,
    }


def write_training_dataset(
    payload: dict,
    *,
    json_path: str | Path = DEFAULT_TRAINING_DATASET_JSON,
    csv_path: str | Path = DEFAULT_TRAINING_DATASET_CSV,
) -> dict:
    json_output = Path(json_path)
    csv_output = Path(csv_path)
    json_output.parent.mkdir(parents=True, exist_ok=True)
    csv_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    _write_dataset_csv(payload.get("rows", []), csv_output)
    return {
        "training_dataset_json": str(json_output),
        "training_dataset_csv": str(csv_output),
        "rows": len(payload.get("rows", [])),
    }


def train_ai_r8_assistant(
    *,
    dataset_json: str | Path = DEFAULT_TRAINING_DATASET_JSON,
    model_path: str | Path = DEFAULT_MODEL_PATH,
    metrics_json: str | Path = DEFAULT_METRICS_JSON,
) -> dict:
    dataset = _load_json(dataset_json)
    rows = dataset.get("rows", [])
    metrics_output = Path(metrics_json)
    metrics_output.parent.mkdir(parents=True, exist_ok=True)

    ml_status = optional_ml_status()
    if not ml_status.available:
        metrics = _missing_optional_dependency_metrics(dataset, ml_status)
        metrics_output.write_text(
            json.dumps(metrics, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return metrics

    # Imports are intentionally local so the default CLI remains usable without
    # installing optional ML dependencies.
    from joblib import dump
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import classification_report, confusion_matrix, f1_score

    split = deterministic_group_split(rows)
    train_rows = [rows[index] for index in split["train_indices"]]
    validation_rows = [rows[index] for index in split["validation_indices"]]
    test_rows = [rows[index] for index in split["test_indices"]]

    train_x, train_y = feature_matrix_and_labels(train_rows)
    validation_x, validation_y = feature_matrix_and_labels(validation_rows)
    test_x, test_y = feature_matrix_and_labels(test_rows)

    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=8,
        class_weight="balanced",
        random_state=MODEL_RANDOM_STATE,
    )
    model.fit(train_x, train_y)

    validation_pred = list(model.predict(validation_x)) if validation_rows else []
    test_pred = list(model.predict(test_x)) if test_rows else []
    baseline = _baseline_metrics(train_y, validation_y, test_y, validation_rows, test_rows)

    metrics = {
        "schema_version": "ai-r8-assistant-metrics-v1",
        "model_version": MODEL_VERSION,
        "status": "trained",
        "model_type": "RandomForestClassifier",
        "report_only": True,
        "feature_columns": FEATURE_COLUMNS,
        "parameters": {
            "n_estimators": 200,
            "max_depth": 8,
            "class_weight": "balanced",
            "random_state": MODEL_RANDOM_STATE,
        },
        "dataset": dataset.get("summary", {}),
        "split": {
            "train_rows": len(train_rows),
            "validation_rows": len(validation_rows),
            "test_rows": len(test_rows),
            "train_cases": _count_cases(train_rows),
            "validation_cases": _count_cases(validation_rows),
            "test_cases": _count_cases(test_rows),
        },
        "validation": _classification_metrics(
            validation_y,
            validation_pred,
            classification_report,
            confusion_matrix,
            f1_score,
        ),
        "test": _classification_metrics(
            test_y,
            test_pred,
            classification_report,
            confusion_matrix,
            f1_score,
        ),
        "baseline_comparison": baseline,
        "limits": [
            "The model is trained from project diagnostic labels, not independent ground truth for all possible APKs.",
            "Predictions are report-only and cannot confirm exact Maven versions.",
            "SBOM component selection, selected versions, vulnerability labels, and source-validation metrics remain unchanged.",
        ],
    }

    model_output = Path(model_path)
    model_output.parent.mkdir(parents=True, exist_ok=True)
    dump(
        {
            "model": model,
            "feature_columns": FEATURE_COLUMNS,
            "label_set": LABELS,
            "model_version": MODEL_VERSION,
            "report_only": True,
        },
        model_output,
    )
    metrics["model_path"] = str(model_output)
    metrics_output.write_text(
        json.dumps(metrics, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return metrics


def build_ai_r8_suggestions(
    *,
    dataset_json: str | Path = DEFAULT_TRAINING_DATASET_JSON,
    model_path: str | Path = DEFAULT_MODEL_PATH,
    metrics_json: str | Path = DEFAULT_METRICS_JSON,
    output_json: str | Path = DEFAULT_SUGGESTIONS_JSON,
) -> dict:
    dataset = _load_json(dataset_json)
    metrics = _load_json_if_exists(metrics_json)
    rows = dataset.get("rows", [])
    model_output = Path(model_path)
    suggestions_output = Path(output_json)
    suggestions_output.parent.mkdir(parents=True, exist_ok=True)

    ml_status = optional_ml_status()
    model_bundle = None
    if ml_status.available and model_output.exists():
        from joblib import load

        model_bundle = load(model_output)

    suggestions = []
    if model_bundle is None:
        for row in rows:
            suggestion = _heuristic_suggestion_from_label(row)
            if suggestion is not None:
                suggestions.append(suggestion)
        status = "heuristic-label-fallback"
        model_type = metrics.get("model_type", "missing-optional-ml-dependency")
    else:
        model = model_bundle["model"]
        probabilities = _predict_probabilities(model, rows)
        predictions = list(model.predict([feature_vector(row) for row in rows]))
        for row, predicted_label, confidence in zip(rows, predictions, probabilities):
            suggestion = _suggestion_from_prediction(row, str(predicted_label), confidence)
            if suggestion is not None:
                suggestions.append(suggestion)
        status = "model-predictions"
        model_type = "RandomForestClassifier"

    action_counts = Counter(row["recommendation"] for row in suggestions)
    coordinate_counts = Counter(row["coordinate"] for row in suggestions)
    payload = {
        "schema_version": "ai-r8-suggestions-v1",
        "model_version": MODEL_VERSION,
        "model_type": model_type,
        "status": status,
        "enabled": True,
        "report_only": True,
        "source_dataset": str(dataset_json),
        "source_model": str(model_output) if model_output.exists() else None,
        "summary": {
            "dataset_rows": len(rows),
            "suggestion_rows": len(suggestions),
            "recommendation_counts": dict(sorted(action_counts.items())),
            "top_coordinates": [
                {"coordinate": coordinate, "rows": count}
                for coordinate, count in coordinate_counts.most_common(20)
            ],
        },
        "suggestions": suggestions,
    }
    suggestions_output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return payload


def write_ai_r8_diagnostics(
    *,
    dataset_json: str | Path = DEFAULT_TRAINING_DATASET_JSON,
    metrics_json: str | Path = DEFAULT_METRICS_JSON,
    suggestions_json: str | Path = DEFAULT_SUGGESTIONS_JSON,
    output_doc: str | Path = DEFAULT_DIAGNOSTICS_DOC,
) -> dict:
    dataset = _load_json_if_exists(dataset_json)
    metrics = _load_json_if_exists(metrics_json)
    suggestions = _load_json_if_exists(suggestions_json)
    output = Path(output_doc)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        build_ai_r8_diagnostics_markdown(dataset, metrics, suggestions),
        encoding="utf-8",
    )
    return {
        "diagnostics_doc": str(output),
        "dataset_rows": dataset.get("summary", {}).get("rows", 0),
        "suggestion_rows": suggestions.get("summary", {}).get("suggestion_rows", 0),
        "metrics_status": metrics.get("status", "missing"),
    }


def build_ai_r8_diagnostics_markdown(
    dataset: dict,
    metrics: dict,
    suggestions: dict,
) -> str:
    dataset_summary = dataset.get("summary", {})
    metrics_status = metrics.get("status", "missing")
    suggestion_summary = suggestions.get("summary", {})
    lines = [
        "# AI R8 Assistant Diagnostics",
        "",
        "Generated by `scripts/build_ai_r8_assistant_diagnostics.py`.",
        "",
        "This artifact documents the Phase 6A report-only ML assistant. It does not change detected components, selected versions, CycloneDX SBOM output, vulnerability labels, or source-validation metrics.",
        "",
        "## Dataset",
        "",
        f"- Rows: `{dataset_summary.get('rows', 0)}`",
        f"- Case IDs: `{dataset_summary.get('case_ids', 0)}`",
        f"- Coordinates: `{dataset_summary.get('coordinates', 0)}`",
        "",
        "| Label | Rows |",
        "|---|---:|",
    ]
    for label, count in sorted(dataset_summary.get("labels", {}).items()):
        lines.append(f"| `{label}` | {count} |")

    lines.extend(
        [
            "",
            "## Model",
            "",
            f"- Status: `{metrics_status}`",
            f"- Model type: `{metrics.get('model_type', 'RandomForestClassifier')}`",
            f"- Model version: `{metrics.get('model_version', MODEL_VERSION)}`",
            "- Report-only: `true`",
        ]
    )
    if metrics_status == "skipped-missing-optional-dependency":
        lines.extend(
            [
                f"- Missing optional packages: `{', '.join(metrics.get('missing_optional_dependencies', []))}`",
                "- Install with `pip install -e .[ml]` to train the RandomForest model.",
            ]
        )
    else:
        test_metrics = metrics.get("test", {})
        lines.extend(
            [
                f"- Test macro-F1: `{test_metrics.get('macro_f1', 'n/a')}`",
                f"- Baselines: `{json.dumps(metrics.get('baseline_comparison', {}), sort_keys=True)}`",
            ]
        )

    lines.extend(
        [
            "",
            "## Suggestions",
            "",
            f"- Suggestion rows: `{suggestion_summary.get('suggestion_rows', 0)}`",
            f"- Recommendation counts: `{json.dumps(suggestion_summary.get('recommendation_counts', {}), sort_keys=True)}`",
            "",
            "## Guardrails",
            "",
            "- AI recommendations are limited to `suggest_report_only`, `suppress_uncertain`, and `risk_only` style report wording.",
            "- `confirmed_exact` rows are training labels, not an allowed AI authority in reports.",
            "- Boundary rows remain unsafe and must not become positive suggestions.",
            "- The assistant is useful for triage and thesis/PhD evidence, not as an exact-version oracle.",
            "",
        ]
    )
    return "\n".join(lines)


def feature_vector(row: dict) -> list[float]:
    features = row.get("features", {})
    vector = []
    for name in FEATURE_COLUMNS:
        value = features.get(name, 0)
        if name in BOOLEAN_FEATURES:
            vector.append(1.0 if bool(value) else 0.0)
        else:
            vector.append(_safe_float(value))
    return vector


def feature_matrix_and_labels(rows: list[dict]) -> tuple[list[list[float]], list[str]]:
    return [feature_vector(row) for row in rows], [str(row.get("label", "")) for row in rows]


def deterministic_group_split(rows: list[dict]) -> dict:
    groups: dict[str, list[int]] = defaultdict(list)
    for index, row in enumerate(rows):
        case_id = str(row.get("case_id") or f"row-{index}")
        groups[case_id].append(index)
    ordered_groups = sorted(groups.items(), key=lambda item: item[0])
    train: list[int] = []
    validation: list[int] = []
    test: list[int] = []
    for position, (_, indices) in enumerate(ordered_groups):
        bucket = position % 10
        if bucket in (0, 1):
            test.extend(indices)
        elif bucket == 2:
            validation.extend(indices)
        else:
            train.extend(indices)
    if not validation and train:
        validation.append(train.pop())
    if not test and train:
        test.append(train.pop())
    return {
        "train_indices": train,
        "validation_indices": validation,
        "test_indices": test,
    }


def _matcher_recall_dataset_rows(payload: dict, case_flags: dict[str, dict]) -> list[dict]:
    rows = []
    for index, row in enumerate(payload.get("rows", [])):
        case_id = str(row.get("case_id") or "")
        label = _label_from_matcher_recall(row)
        flags = case_flags.get(case_id, {})
        rows.append(
            _make_row(
                row_id=f"matcher-recall:{index}:{case_id}:{row.get('coordinate')}:{row.get('source_version')}:{row.get('best_version')}",
                case_id=case_id,
                coordinate=row.get("coordinate"),
                source_version=row.get("source_version"),
                candidate_version=row.get("best_version"),
                row_source="matcher-recall",
                label=label,
                features={
                    "best_score": row.get("best_score"),
                    "score_gap_to_best": row.get("score_gap_to_best"),
                    "source_rank": row.get("source_rank"),
                    "identity_confidence": row.get("identity_confidence"),
                    "package_score": row.get("package_score"),
                    "class_score": row.get("class_score"),
                    "method_score": row.get("method_score"),
                    "opcode_score": row.get("opcode_score"),
                    "literal_score": row.get("literal_score"),
                    "dependency_score": row.get("dependency_score"),
                    "matched_packages": row.get("matched_packages"),
                    "matched_classes": row.get("matched_classes"),
                    "matched_methods": row.get("matched_methods"),
                    **flags,
                },
                context={
                    "app": row.get("app"),
                    "recall_status": row.get("recall_status"),
                    "next_action": row.get("next_action"),
                },
            )
        )
    return rows


def _transparency_emitted_dataset_rows(payload: dict, case_flags: dict[str, dict]) -> list[dict]:
    rows = []
    for index, row in enumerate(payload.get("emitted_result_rows", [])):
        case_id = str(row.get("case_id") or "")
        result_class = str(row.get("result_class") or "")
        label = "confirmed_exact" if result_class == "exact-confirmed" else "mismatch_or_extra"
        flags = case_flags.get(case_id, {})
        rows.append(
            _make_row(
                row_id=f"emitted-result:{index}:{case_id}:{row.get('coordinate')}:{row.get('detected_version')}",
                case_id=case_id,
                coordinate=row.get("coordinate"),
                source_version=row.get("source_versions"),
                candidate_version=row.get("detected_version"),
                row_source="emitted-result",
                label=label,
                features={
                    "best_score": row.get("confidence"),
                    "identity_confidence": row.get("confidence"),
                    **flags,
                },
                context={
                    "app": row.get("app"),
                    "match_type": row.get("match_type"),
                    "result_class": result_class,
                    "version_mismatch_reason": row.get("version_mismatch_reason"),
                },
            )
        )
    return rows


def _transparency_boundary_dataset_rows(payload: dict, case_flags: dict[str, dict]) -> list[dict]:
    rows = []
    for index, row in enumerate(payload.get("source_dependency_rows", [])):
        label = _label_from_transparency_source_row(row)
        if label not in {"boundary_do_not_suggest", "mismatch_or_extra", "risk_only"}:
            continue
        case_id = str(row.get("case_id") or "")
        flags = case_flags.get(case_id, {})
        rows.append(
            _make_row(
                row_id=f"source-boundary:{index}:{case_id}:{row.get('coordinate')}:{row.get('source_version')}",
                case_id=case_id,
                coordinate=row.get("coordinate"),
                source_version=row.get("source_version"),
                candidate_version=row.get("matcher_best_version"),
                row_source="boundary",
                label=label,
                features={
                    "best_score": row.get("matcher_best_score"),
                    "source_rank": row.get("matcher_source_score"),
                    **flags,
                    "is_boundary_or_limitation": (
                        flags.get("is_boundary_or_limitation", False)
                        or label == "boundary_do_not_suggest"
                    ),
                },
                context={
                    "app": row.get("app"),
                    "coverage_class": row.get("coverage_class"),
                    "gap_class": row.get("gap_class"),
                    "reason_label": row.get("reason_label"),
                    "triage_bucket": row.get("triage_bucket"),
                },
            )
        )
    return rows


def _phase5_dataset_rows(payload: dict, case_flags: dict[str, dict]) -> list[dict]:
    rows = []
    for index, row in enumerate(payload.get("rows", [])):
        case_id = _case_id_from_phase5_row(row)
        decision = row.get("trigger_decision", {}) or {}
        label = _label_from_phase5_row(row)
        flags = case_flags.get(case_id, _flags_from_phase5_row(row))
        rows.append(
            _make_row(
                row_id=f"phase5:{index}:{case_id}:{row.get('coordinate')}:{row.get('baseline_selected_version')}:{row.get('diagnostic_selected_version')}",
                case_id=case_id,
                coordinate=row.get("coordinate"),
                source_version=row.get("source_versions"),
                candidate_version=row.get("diagnostic_selected_version"),
                row_source="phase5",
                label=label,
                features={
                    "best_score": decision.get("top_score"),
                    "score_gap_to_best": decision.get("score_margin"),
                    "identity_confidence": decision.get("top_score"),
                    "matched_packages": len(decision.get("reason_codes") or []),
                    "matched_classes": decision.get("supporting_feature_families"),
                    "matched_methods": decision.get("supporting_feature_families"),
                    **flags,
                },
                context={
                    "case": row.get("case"),
                    "role": row.get("role"),
                    "row_type": row.get("row_type"),
                    "trigger_outcome": row.get("trigger_outcome"),
                    "trigger_apply": bool(decision.get("apply")),
                    "reason_codes": decision.get("reason_codes") or [],
                    "blocked_by": decision.get("blocked_by") or [],
                },
            )
        )
    return rows


def _r8_boundary_dataset_rows(payload: dict) -> list[dict]:
    rows = []
    if not payload:
        return rows
    for index, row in enumerate(payload.get("classifier_gap_rows", []) or []):
        rows.append(
            _make_row(
                row_id=f"r8-boundary:{index}:{row.get('case_id') or row.get('case')}:{row.get('coordinate')}",
                case_id=str(row.get("case_id") or row.get("case") or ""),
                coordinate=row.get("coordinate"),
                source_version=row.get("source_version"),
                candidate_version=row.get("candidate_version"),
                row_source="boundary",
                label="risk_only",
                features={
                    "is_r8_or_minified": True,
                    "is_boundary_or_limitation": True,
                },
                context=row,
            )
        )
    return rows


def _make_row(
    *,
    row_id: str,
    case_id: str,
    coordinate: object,
    source_version: object,
    candidate_version: object,
    row_source: str,
    label: str,
    features: dict,
    context: dict | None = None,
) -> dict:
    return {
        "row_id": _compact_id(row_id),
        "case_id": str(case_id or ""),
        "coordinate": str(coordinate or ""),
        "source_version": _stringify_version(source_version),
        "candidate_version": _stringify_version(candidate_version),
        "row_source": row_source,
        "label": label,
        "features": normalize_features(features),
        "context": context or {},
    }


def normalize_features(features: dict) -> dict:
    normalized = {}
    for name in FEATURE_COLUMNS:
        if name in BOOLEAN_FEATURES:
            normalized[name] = bool(features.get(name, False))
        else:
            normalized[name] = _safe_int(features.get(name)) if name in {
                "source_rank",
                "matched_packages",
                "matched_classes",
                "matched_methods",
            } else _safe_float(features.get(name))
    return normalized


def _label_from_matcher_recall(row: dict) -> str:
    next_action = str(row.get("next_action") or "").lower()
    recall_status = str(row.get("recall_status") or "").lower()
    if "source-context-report-only-suggestion" in next_action or "report-only" in recall_status:
        return "suggest_report_only"
    if "inspect-report-filter" in next_action or "suppressed-uncertain" in recall_status:
        return "suppress_uncertain"
    if "boundary" in recall_status or "do-not-suggest" in next_action:
        return "boundary_do_not_suggest"
    if "mismatch" in recall_status or "extra" in recall_status:
        return "mismatch_or_extra"
    return "risk_only"


def _label_from_transparency_source_row(row: dict) -> str:
    reason = str(row.get("reason_label") or "").lower()
    coverage = str(row.get("coverage_class") or "").lower()
    triage = str(row.get("triage_bucket") or "").lower()
    if "boundary" in reason or "boundary" in coverage or "boundary" in triage:
        return "boundary_do_not_suggest"
    if "metadata" in reason or "source-only" in reason:
        return "boundary_do_not_suggest"
    if "alias" in reason or "alias" in coverage or "alias" in triage:
        return "boundary_do_not_suggest"
    if "reference-missing" in reason or "missing-coordinate" in coverage:
        return "boundary_do_not_suggest"
    if "wrong-version" in reason or "version-mismatch" in reason:
        return "mismatch_or_extra"
    if "not-emitted" in reason or "matcher-recall" in reason:
        return "risk_only"
    return "confirmed_exact" if reason == "exact-confirmed" else "risk_only"


def _label_from_phase5_row(row: dict) -> str:
    decision = row.get("trigger_decision", {}) or {}
    outcome = str(row.get("trigger_outcome") or "")
    phase4_outcome = str(row.get("phase4_outcome") or "")
    if decision.get("apply") and "target-improvement" in outcome:
        return "suggest_report_only"
    if "regression" in phase4_outcome or "blocked" in outcome:
        return "suppress_uncertain"
    if row.get("row_type") == "controlled":
        return "confirmed_exact"
    return "risk_only"


def _case_flags_by_id(payload: dict) -> dict[str, dict]:
    flags = {}
    for case in payload.get("dataset_cases", []):
        case_id = str(case.get("case_id") or "")
        if not case_id:
            continue
        text = " ".join(
            str(case.get(key) or "")
            for key in (
                "role",
                "dataset_classification",
                "apk_family",
                "feature_labels",
                "r8_obfuscation_profile",
                "obfuscation_risk",
                "extraction_risk",
                "framework_profile",
                "metric_bucket",
            )
        ).lower()
        role = str(case.get("role") or "").lower()
        flags[case_id] = {
            "is_r8_or_minified": any(
                token in text
                for token in ("r8", "minified", "obfuscat", "protected", "shrink")
            ),
            "is_boundary_or_limitation": any(
                token in text
                for token in ("boundary", "limitation", "hidden", "protected", "excluded")
            ),
            "is_clean_real": "clean" in role and "source-validated" in role,
            "is_partial_real": "partial" in role and "source-validated" in role,
        }
    return flags


def _flags_from_phase5_row(row: dict) -> dict:
    text = " ".join(
        [
            str(row.get("case") or ""),
            str(row.get("role") or ""),
            str(row.get("row_type") or ""),
            " ".join(str(tag) for tag in row.get("tags") or []),
        ]
    ).lower()
    return {
        "is_r8_or_minified": any(
            token in text for token in ("r8", "minified", "obfuscat", "shrink")
        ),
        "is_boundary_or_limitation": any(
            token in text for token in ("boundary", "limitation", "hidden", "protected")
        ),
        "is_clean_real": "clean" in text and "source-validated" in text,
        "is_partial_real": "partial" in text and "source-validated" in text,
    }


def _case_id_from_phase5_row(row: dict) -> str:
    case = str(row.get("case") or "")
    if not case:
        return ""
    return _compact_case_id(case)


def _compact_case_id(value: str) -> str:
    return "-".join("".join(char.lower() if char.isalnum() else " " for char in value).split())


def _deduplicate_rows(rows: Iterable[dict]) -> list[dict]:
    seen = set()
    deduped = []
    for row in rows:
        key = row["row_id"]
        if key in seen:
            continue
        seen.add(key)
        deduped.append(row)
    return deduped


def _write_dataset_csv(rows: list[dict], output: Path) -> None:
    fieldnames = [
        "row_id",
        "case_id",
        "coordinate",
        "source_version",
        "candidate_version",
        "row_source",
        "label",
        *FEATURE_COLUMNS,
    ]
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            record = {key: row.get(key, "") for key in fieldnames[:7]}
            record.update(row.get("features", {}))
            writer.writerow(record)


def _missing_optional_dependency_metrics(dataset: dict, status: OptionalMlStatus) -> dict:
    labels = dataset.get("summary", {}).get("labels", {})
    rows = dataset.get("rows", [])
    return {
        "schema_version": "ai-r8-assistant-metrics-v1",
        "model_version": MODEL_VERSION,
        "status": "skipped-missing-optional-dependency",
        "model_type": "RandomForestClassifier",
        "report_only": True,
        "missing_optional_dependencies": status.missing,
        "install_hint": "pip install -e .[ml]",
        "dataset": dataset.get("summary", {}),
        "split": {
            "train_rows": 0,
            "validation_rows": 0,
            "test_rows": 0,
        },
        "validation": {
            "macro_f1": None,
            "per_class": {},
            "confusion_matrix": [],
        },
        "test": {
            "macro_f1": None,
            "per_class": {},
            "confusion_matrix": [],
        },
        "baseline_comparison": {
            "majority_class": _majority_label(labels),
            "score_threshold_rule": _score_threshold_baseline_preview(rows),
        },
        "limits": [
            "Optional ML dependencies are not installed in this environment.",
            "No trained model was written.",
            "Dataset and report-only suggestion generation remain available for review.",
        ],
    }


def _classification_metrics(
    y_true: list[str],
    y_pred: list[str],
    classification_report,
    confusion_matrix,
    f1_score,
) -> dict:
    if not y_true:
        return {
            "macro_f1": None,
            "per_class": {},
            "confusion_matrix": [],
        }
    report = classification_report(
        y_true,
        y_pred,
        labels=LABELS,
        output_dict=True,
        zero_division=0,
    )
    return {
        "macro_f1": f1_score(y_true, y_pred, labels=LABELS, average="macro", zero_division=0),
        "per_class": {
            label: {
                "precision": report.get(label, {}).get("precision", 0.0),
                "recall": report.get(label, {}).get("recall", 0.0),
                "f1": report.get(label, {}).get("f1-score", 0.0),
                "support": report.get(label, {}).get("support", 0),
            }
            for label in LABELS
        },
        "confusion_matrix": confusion_matrix(y_true, y_pred, labels=LABELS).tolist(),
        "labels": LABELS,
    }


def _baseline_metrics(
    train_y: list[str],
    validation_y: list[str],
    test_y: list[str],
    validation_rows: list[dict],
    test_rows: list[dict],
) -> dict:
    majority = Counter(train_y).most_common(1)[0][0] if train_y else "risk_only"
    return {
        "majority_class": {
            "label": majority,
            "validation_accuracy": _accuracy(validation_y, [majority] * len(validation_y)),
            "test_accuracy": _accuracy(test_y, [majority] * len(test_y)),
        },
        "score_threshold_rule": {
            "description": "best_score >= 0.75 -> suggest_report_only, boundary flag -> boundary_do_not_suggest, otherwise risk_only",
            "validation_accuracy": _accuracy(
                validation_y,
                [_score_threshold_prediction(row) for row in validation_rows],
            ),
            "test_accuracy": _accuracy(
                test_y,
                [_score_threshold_prediction(row) for row in test_rows],
            ),
        },
    }


def _score_threshold_prediction(row: dict) -> str:
    features = row.get("features", {})
    if features.get("is_boundary_or_limitation"):
        return "boundary_do_not_suggest"
    if _safe_float(features.get("best_score")) >= 0.75:
        return "suggest_report_only"
    if _safe_float(features.get("best_score")) >= 0.50:
        return "risk_only"
    return "suppress_uncertain"


def _score_threshold_baseline_preview(rows: list[dict]) -> dict:
    if not rows:
        return {"preview_rows": 0}
    predictions = Counter(_score_threshold_prediction(row) for row in rows)
    return {
        "preview_rows": len(rows),
        "prediction_counts": dict(sorted(predictions.items())),
    }


def _accuracy(y_true: list[str], y_pred: list[str]) -> float | None:
    if not y_true:
        return None
    return sum(1 for true, pred in zip(y_true, y_pred) if true == pred) / len(y_true)


def _count_cases(rows: list[dict]) -> int:
    return len({row.get("case_id") for row in rows if row.get("case_id")})


def _predict_probabilities(model, rows: list[dict]) -> list[float]:
    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba([feature_vector(row) for row in rows])
        classes = list(model.classes_)
        predictions = list(model.predict([feature_vector(row) for row in rows]))
        confidences = []
        for predicted, row_probabilities in zip(predictions, probabilities):
            confidences.append(float(row_probabilities[classes.index(predicted)]))
        return confidences
    return [0.0 for _ in rows]


def _heuristic_suggestion_from_label(row: dict) -> dict | None:
    label = str(row.get("label") or "")
    if label == "confirmed_exact":
        return None
    if label == "boundary_do_not_suggest":
        return _suggestion_from_prediction(row, "boundary_do_not_suggest", 1.0)
    if label in {"suggest_report_only", "suppress_uncertain", "risk_only"}:
        return _suggestion_from_prediction(row, label, 0.5)
    return None


def _suggestion_from_prediction(
    row: dict,
    predicted_label: str,
    confidence: float,
) -> dict | None:
    if predicted_label == "confirmed_exact":
        return None
    recommendation = {
        "suggest_report_only": "suggest_report_only",
        "suppress_uncertain": "suppress_uncertain",
        "risk_only": "risk_only",
        "mismatch_or_extra": "risk_only",
        "boundary_do_not_suggest": "risk_only",
    }.get(predicted_label)
    if recommendation is None:
        return None
    return {
        "row_id": row.get("row_id"),
        "case_id": row.get("case_id"),
        "coordinate": row.get("coordinate"),
        "source_version": row.get("source_version"),
        "candidate_version": row.get("candidate_version"),
        "row_source": row.get("row_source"),
        "training_label": row.get("label"),
        "model_recommendation_label": predicted_label,
        "recommendation": recommendation,
        "confidence": round(float(confidence), 6),
        "report_only": True,
        "allowed_effects": [
            "report wording",
            "triage prioritization",
            "future matcher-recall investigation",
        ],
        "forbidden_effects": [
            "selected version change",
            "CycloneDX SBOM component change",
            "vulnerability label change",
            "source-validation metric change",
        ],
        "features": row.get("features", {}),
        "context": row.get("context", {}),
    }


def _majority_label(labels: dict) -> str | None:
    if not labels:
        return None
    return max(labels.items(), key=lambda item: item[1])[0]


def _safe_float(value: object) -> float:
    if value is None or value == "":
        return 0.0
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _safe_int(value: object) -> int:
    if value is None or value == "":
        return 0
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return 0


def _stringify_version(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        return ",".join(str(item) for item in value)
    return str(value)


def _compact_id(value: str) -> str:
    return value.replace("\n", " ").replace("\r", " ").strip()


def _load_json(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _load_json_if_exists(path: str | Path) -> dict:
    source = Path(path)
    if not source.exists():
        return {}
    return _load_json(source)

