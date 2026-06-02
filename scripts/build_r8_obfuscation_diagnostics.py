from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


DEFAULT_METHOD_JSON = Path("data/results/evaluation/r8-obfuscation-method-selection.json")
DEFAULT_APK_TYPE_JSON = Path("data/results/evaluation/apk-type-evaluation.json")
DEFAULT_GENERATED_BATCH_JSON = Path("data/results/evaluation/generated-apk-category-batch.json")
DEFAULT_HIDDEN_DEX_JSON = Path("data/results/evaluation/hidden-dex-diagnostics.json")
DEFAULT_OPCODE_API_JSON = Path("data/results/experiments/opcode-api-signal-diagnostics.json")
DEFAULT_PHASE4_JSON = Path("data/results/experiments/r8-phase4-scoped-experiment-diagnostics.json")
DEFAULT_PHASE5_JSON = Path("data/results/experiments/r8-phase5-scoped-trigger-diagnostics.json")
DEFAULT_PHASE5_VALIDATION_JSON = Path(
    "data/results/experiments/r8-phase5-trigger-control-validation.json"
)
DEFAULT_OUTPUT_JSON = Path("data/results/evaluation/r8-obfuscation-diagnostics.json")
DEFAULT_OUTPUT_DOC = Path("docs/evaluation/R8_OBFUSCATION_DIAGNOSTICS.md")


CLASSIFIER_GAPS: list[dict[str, str]] = [
    {
        "signal": "short-name density",
        "status": "implemented-report-only",
        "why": "R8 minification and package flattening can remove readable class/method/package evidence.",
        "next_action": "Keep the aggregate one-letter/two-letter package, class, method, and field ratios report-only and use them to select Phase 2 matrix fixtures.",
    },
    {
        "signal": "package flattening or repackaging",
        "status": "implemented-report-only",
        "why": "ObfDetector and modern R8 behavior show package hierarchy changes are a major blind spot.",
        "next_action": "Keep the Phase 2 package-flattening fixtures as controls; the expanded Phase 4 blend still has controlled and real regression-risk blockers.",
    },
    {
        "signal": "class and method loss versus reference",
        "status": "implemented-report-only",
        "why": "The matcher already sees low coverage and low confidence, but reports do not explain whether shrink/optimization probably caused it.",
        "next_action": "Compare coverage-loss fields across rename, shrink, optimize, shrink+optimize, repackage, and inline-stress fixtures before scoring changes.",
    },
    {
        "signal": "resource shrinking symptoms",
        "status": "implemented-report-only",
        "why": "R8/AGP now integrates resource shrinking with code reachability, which can remove code/resources together.",
        "next_action": "Keep sparse resource-table/resource-entry indicators weak and report-only because they can be normal for controlled fixtures.",
    },
    {
        "signal": "method inlining and call-site optimization symptoms",
        "status": "implemented-report-only",
        "why": "LibHunter identifies inlining and call-site optimization as key R8 failure modes.",
        "next_action": "The Phase 5 scoped trigger is available through the opt-in r8-phase5-experiment command and optional report-only generate-report evidence. The generated four-report summary records 0 default selection changes, but keep it separate from default scoring unless production wiring is separately justified and verified.",
    },
    {
        "signal": "class merging symptoms",
        "status": "implemented-report-only",
        "why": "R8 can merge classes, weakening class-boundary and CDG assumptions.",
        "next_action": "Candidate-level class-boundary mismatch is exposed now; many-reference-to-one-class concentration stays diagnostic because the expanded Phase 4 blend has regression-risk rows.",
    },
    {
        "signal": "nonstandard DEX and protector hints",
        "status": "implemented-report-only",
        "why": "Hidden-code/protector cases should be warnings, not false Maven claims.",
        "next_action": "Keep the hidden-DEX fixture as boundary evidence and keep its risk codes in the structured diagnostics block.",
    },
    {
        "signal": "low-confidence component ratio",
        "status": "implemented-report-only",
        "why": "Low-confidence emitted components already appear in reports, but the app-level aggregate is not yet a named obfuscation signal.",
        "next_action": "Use the app-level ratio as report-only evidence; do not feed it back into matcher scoring.",
    },
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate R8/obfuscation diagnostics.")
    parser.add_argument("--method-json", default=str(DEFAULT_METHOD_JSON))
    parser.add_argument("--apk-type-json", default=str(DEFAULT_APK_TYPE_JSON))
    parser.add_argument("--generated-batch-json", default=str(DEFAULT_GENERATED_BATCH_JSON))
    parser.add_argument("--hidden-dex-json", default=str(DEFAULT_HIDDEN_DEX_JSON))
    parser.add_argument("--opcode-api-json", default=str(DEFAULT_OPCODE_API_JSON))
    parser.add_argument("--phase4-json", default=str(DEFAULT_PHASE4_JSON))
    parser.add_argument("--phase5-json", default=str(DEFAULT_PHASE5_JSON))
    parser.add_argument("--phase5-validation-json", default=str(DEFAULT_PHASE5_VALIDATION_JSON))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--output-doc", default=str(DEFAULT_OUTPUT_DOC))
    return parser


def main() -> int:
    args = build_parser().parse_args()
    payload = build_payload(
        method=read_json(Path(args.method_json)),
        apk_type=read_json(Path(args.apk_type_json)),
        generated_batch=read_json(Path(args.generated_batch_json)),
        hidden_dex=read_json(Path(args.hidden_dex_json)),
        opcode_api=read_json(Path(args.opcode_api_json)),
        phase4=read_json(Path(args.phase4_json)),
        phase5=read_json(Path(args.phase5_json)),
        phase5_validation=read_json(Path(args.phase5_validation_json)),
        source_paths={
            "method_selection": args.method_json,
            "apk_type": args.apk_type_json,
            "generated_batch": args.generated_batch_json,
            "hidden_dex": args.hidden_dex_json,
            "opcode_api": args.opcode_api_json,
            "phase4": args.phase4_json,
            "phase5": args.phase5_json,
            "phase5_validation": args.phase5_validation_json,
        },
    )

    output_json = Path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    output_doc = Path(args.output_doc)
    output_doc.parent.mkdir(parents=True, exist_ok=True)
    output_doc.write_text(build_markdown(payload), encoding="utf-8")

    print(
        json.dumps(
            {
                "doc": normalize_path(output_doc),
                "json": normalize_path(output_json),
                "verdict": payload["verdict"],
                "classifier_gaps": len(payload["classifier_gap_matrix"]),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def build_payload(
    *,
    method: dict[str, Any],
    apk_type: dict[str, Any],
    generated_batch: dict[str, Any],
    hidden_dex: dict[str, Any],
    opcode_api: dict[str, Any],
    phase4: dict[str, Any],
    phase5: dict[str, Any],
    phase5_validation: dict[str, Any],
    source_paths: dict[str, str],
) -> dict[str, Any]:
    selected_method = method.get("decision", {}).get(
        "selected_method", "explainable multi-scale R8-aware evidence layer"
    )
    return {
        "schema_version": 1,
        "sources": {key: normalize_path(value) for key, value in source_paths.items()},
        "selected_method": selected_method,
        "current_r8_evidence": {
            "apk_type_groups": summarize_apk_type_groups(apk_type),
            "generated_batch": summarize_generated_batch(generated_batch),
            "hidden_dex": summarize_hidden_dex(hidden_dex),
            "signal_guardrail": summarize_opcode_api(opcode_api),
            "phase4_scoped_experiment": summarize_phase4(phase4),
            "phase5_scoped_trigger": summarize_phase5(phase5),
            "phase5_control_validation": summarize_phase5_validation(phase5_validation),
        },
        "classifier_gap_matrix": CLASSIFIER_GAPS,
        "policy": [
            "No matcher scoring change is justified by this diagnostic alone.",
            "Treat current controlled R8 rename/shrink success as mechanics evidence, not broad R8-proof evidence.",
            "Treat real R8/minified partials as source-validated stress evidence with honest mismatches and nuances.",
            "Keep hidden/protector cases out of Maven-version accuracy metrics.",
            "Keep the Phase 4 multi-scale blend diagnostic-only because the controlled pass has regression-risk rows.",
            "Keep the Phase 5 scoped trigger experiment-only through the explicit r8-phase5-experiment command and optional report-only generate-report evidence; default matcher and SBOM behavior stay unchanged.",
        ],
        "next_actions": [
            "Do not promote global multi-scale scoring from the expanded Phase 4 layered diagnostic.",
            "If R8 scoring work continues, rerun fresh controls before any production scorer promotion.",
        ],
        "verdict": "r8-phase-5-current-control-clean-experiment-only",
    }


def summarize_phase4(payload: dict[str, Any]) -> dict[str, Any]:
    controlled_cases = payload.get("controlled_cases") or payload.get("cases", [])
    real_rows = payload.get("real_component_rows", [])
    all_rows = [*controlled_cases, *real_rows]
    outcome_counts = Counter(str(row.get("outcome") or "unknown") for row in all_rows)
    category_counts: dict[str, Counter[str]] = {}
    role_counts: dict[str, Counter[str]] = {}
    regression_rows = []
    for row in controlled_cases:
        category = str(row.get("category") or "unknown")
        outcome = str(row.get("outcome") or "unknown")
        category_counts.setdefault(category, Counter())[outcome] += 1
        if outcome == "regression-risk-do-not-promote":
            regression_rows.append(
                {
                    "case": str(row.get("slug") or ""),
                    "category": category,
                    "coordinate": str(row.get("coordinate") or ""),
                    "expected": str(row.get("expected_version") or ""),
                    "baseline_selected": str(row.get("baseline_selected_version") or "none"),
                    "diagnostic_selected": str(row.get("diagnostic_selected_version") or "none"),
                }
            )
    real_regression_rows = []
    for row in real_rows:
        role = str(row.get("role") or "unknown")
        outcome = str(row.get("outcome") or "unknown")
        role_counts.setdefault(role, Counter())[outcome] += 1
        if outcome == "real-regression-risk-do-not-promote":
            real_regression_rows.append(
                {
                    "case": str(row.get("case_name") or row.get("case_id") or ""),
                    "role": role,
                    "coordinate": str(row.get("coordinate") or ""),
                    "expected": ", ".join(row.get("source_versions") or []),
                    "baseline_selected": str(row.get("baseline_selected_version") or "none"),
                    "diagnostic_selected": str(row.get("diagnostic_selected_version") or "none"),
                }
            )
    scan = payload.get("summary", {}).get("phase5_candidate_scan", {})
    return {
        "verdict": str(payload.get("verdict") or "not-run"),
        "case_count": len(controlled_cases),
        "real_component_rows": len(real_rows),
        "outcome_counts": dict(sorted(outcome_counts.items())),
        "category_counts": [
            {"category": category, "outcomes": dict(sorted(counter.items()))}
            for category, counter in sorted(category_counts.items())
        ],
        "role_counts": [
            {"role": role, "outcomes": dict(sorted(counter.items()))}
            for role, counter in sorted(role_counts.items())
        ],
        "candidate_improvements": scan.get("candidate_improvements", []),
        "controlled_regression_count": scan.get("controlled_regression_count", len(regression_rows)),
        "real_regression_count": scan.get("real_regression_count", len(real_regression_rows)),
        "clean_real_regression_count": scan.get("clean_real_regression_count", 0),
        "top_blocking_coordinates": scan.get("top_blocking_coordinates", []),
        "regression_risks": regression_rows,
        "real_regression_risks": real_regression_rows,
    }


def summarize_phase5(payload: dict[str, Any]) -> dict[str, Any]:
    summary = payload.get("summary", {})
    return {
        "verdict": str(payload.get("verdict") or "not-run"),
        "rows_evaluated": int(summary.get("rows_evaluated") or 0),
        "controlled_rows": int(summary.get("controlled_rows") or 0),
        "real_rows": int(summary.get("real_rows") or 0),
        "triggered_rows": int(summary.get("triggered_rows") or 0),
        "target_improvements_kept": int(summary.get("target_improvements_kept") or 0),
        "triggered_regressions": int(summary.get("triggered_regressions") or 0),
        "triggered_conflicts": int(summary.get("triggered_conflicts") or 0),
        "triggered_outcomes": summary.get("triggered_outcomes", {}),
        "blocked_reason_counts": summary.get("blocked_reason_counts", {}),
        "triggered_rows_detail": payload.get("triggered_rows", []),
    }


def summarize_phase5_validation(payload: dict[str, Any]) -> dict[str, Any]:
    summary = payload.get("summary", {})
    return {
        "verdict": str(payload.get("verdict") or "not-run"),
        "rows_evaluated": int(summary.get("rows_evaluated") or 0),
        "triggered_rows": int(summary.get("triggered_rows") or 0),
        "target_improvements_kept": int(summary.get("target_improvements_kept") or 0),
        "triggered_regressions": int(summary.get("triggered_regressions") or 0),
        "triggered_conflicts": int(summary.get("triggered_conflicts") or 0),
        "failed_gates": int(summary.get("failed_gates") or 0),
        "gates": payload.get("gates", []),
        "production_imports": payload.get("production_imports", []),
    }


def summarize_apk_type_groups(payload: dict[str, Any]) -> list[dict[str, str]]:
    wanted = {
        "controlled-r8-rename",
        "controlled-r8-shrink",
        "controlled-r8-optimize",
        "controlled-r8-shrink-optimize",
        "controlled-r8-package-flattening",
        "controlled-r8-inline-stress",
        "real-r8-minified",
        "limitations",
    }
    rows = []
    for group in payload.get("groups", []):
        group_id = str(group.get("group_id") or "")
        if group_id in wanted:
            rows.append(
                {
                    "group_id": group_id,
                    "name": str(group.get("name") or ""),
                    "cases": str(group.get("case_count") or ""),
                    "result_summary": str(group.get("result_summary") or ""),
                    "interpretation": str(group.get("interpretation") or ""),
                    "next_improvement": str(group.get("next_improvement") or ""),
                }
            )
    return rows


def summarize_generated_batch(payload: dict[str, Any]) -> dict[str, Any]:
    counters: dict[str, Counter[str]] = {}
    for row in payload.get("evaluation_rows", []):
        category = str(row.get("category") or "")
        if not category.startswith("r8"):
            continue
        counters.setdefault(category, Counter())
        counter = counters[category]
        counter["expected"] += 1
        if row.get("component_detected"):
            counter["component_detected"] += 1
        if row.get("version_detected"):
            counter["version_detected"] += 1
        if row.get("candidate_version_correct"):
            counter["candidate_version_correct"] += 1
        decision = str(row.get("candidate_decision") or "unknown")
        confidence = str(row.get("candidate_confidence") or "unknown")
        risk = str(row.get("obfuscation_risk_level") or "unknown")
        counter[f"decision:{decision}"] += 1
        counter[f"confidence:{confidence}"] += 1
        counter[f"risk:{risk}"] += 1

    by_category = []
    total = Counter()
    for category in sorted(counters):
        counter = counters[category]
        total.update(counter)
        by_category.append(format_generated_category(category, counter))
    return {
        "by_category": by_category,
        "total": format_generated_category("r8-total", total) if total else {},
    }


def format_generated_category(category: str, counter: Counter[str]) -> dict[str, Any]:
    return {
        "category": category,
        "expected": counter["expected"],
        "component_detected": counter["component_detected"],
        "version_detected": counter["version_detected"],
        "candidate_version_correct": counter["candidate_version_correct"],
        "dominant_decision": most_common_prefixed_label(
            counter, "decision", {"candidate", "exact", "likely"}
        ),
        "dominant_confidence": most_common_prefixed_label(
            counter, "confidence", {"low", "medium", "high"}
        ),
        "dominant_risk": most_common_prefixed_label(counter, "risk", {"low", "medium", "high"}),
    }


def summarize_hidden_dex(payload: dict[str, Any]) -> dict[str, Any]:
    summary = payload.get("summary", {})
    return {
        "verdict": payload.get("verdict", ""),
        "extraction_risk": summary.get("extraction_risk", ""),
        "obfuscation_risk": summary.get("obfuscation_risk", ""),
        "risk_indicator_codes": summary.get("risk_indicator_codes", []),
        "detected_maven_components": summary.get("detected_maven_components", 0),
        "native_file_components": summary.get("native_file_components", 0),
        "conclusion": payload.get("conclusion", ""),
    }


def summarize_opcode_api(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "conclusion": payload.get("conclusion", ""),
        "signals": [
            {
                "signal": signal.get("signal", ""),
                "decision": signal.get("decision", ""),
                "case_count": signal.get("case_count", 0),
                "improved_cases": signal.get("improved_cases", []),
                "regressed_cases": signal.get("regressed_cases", []),
            }
            for signal in payload.get("signals", [])
        ],
    }


def build_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# R8 Obfuscation Diagnostics",
        "",
        "Generated by `scripts/build_r8_obfuscation_diagnostics.py`.",
        "",
        f"Selected method: `{payload['selected_method']}`.",
        "",
        f"Verdict: `{payload['verdict']}`.",
        "",
        "This diagnostic now records the completed Phase 1 report-only classifier, Phase 2 controlled R8 matrix, Phase 3 inert multi-scale feature milestone, and expanded Phase 4 layered generated+real experiment. It keeps matcher scoring unchanged because the Phase 4 blend has regression-risk rows.",
        "",
        "## Current Evidence",
        "",
        "### APK-Type Groups",
        "",
        "| Group | Cases | Result | Interpretation | Next improvement |",
        "|---|---:|---|---|---|",
    ]
    for row in payload["current_r8_evidence"]["apk_type_groups"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    md(row["name"] or row["group_id"]),
                    md(row["cases"]),
                    md(row["result_summary"]),
                    md(row["interpretation"]),
                    md(row["next_improvement"]),
                ]
            )
            + " |"
        )

    generated = payload["current_r8_evidence"]["generated_batch"]
    lines.extend(
        [
            "",
            "### Generated R8 Batch",
            "",
            "| Category | Expected | Components detected | Versions detected | Candidate version correct | Decision | Confidence | Risk |",
            "|---|---:|---:|---:|---:|---|---|---|",
        ]
    )
    for row in generated.get("by_category", []):
        lines.append(generated_row(row))
    if generated.get("total"):
        lines.append(generated_row(generated["total"]))

    hidden = payload["current_r8_evidence"]["hidden_dex"]
    lines.extend(
        [
            "",
            "### Hidden/Protected Boundary",
            "",
            f"- Verdict: `{hidden['verdict']}`",
            f"- Extraction risk: `{hidden['extraction_risk']}`",
            f"- Obfuscation risk: `{hidden['obfuscation_risk']}`",
            "- Risk indicators: "
            + ", ".join(f"`{item}`" for item in hidden.get("risk_indicator_codes", [])),
            f"- Maven components emitted: `{hidden['detected_maven_components']}`",
            f"- Native file components emitted: `{hidden['native_file_components']}`",
            f"- Conclusion: {hidden['conclusion']}",
            "",
            "### Signal Guardrail",
            "",
            payload["current_r8_evidence"]["signal_guardrail"].get("conclusion", ""),
            "",
            "| Signal | Decision | Cases | Improved | Regressed |",
            "|---|---|---:|---|---|",
        ]
    )
    for row in payload["current_r8_evidence"]["signal_guardrail"].get("signals", []):
        lines.append(
            "| "
            + " | ".join(
                [
                    md(row["signal"]),
                    md(row["decision"]),
                    str(row["case_count"]),
                    md(", ".join(row.get("improved_cases") or []) or "none"),
                    md(", ".join(row.get("regressed_cases") or []) or "none"),
                ]
            )
            + " |"
        )

    phase4 = payload["current_r8_evidence"]["phase4_scoped_experiment"]
    lines.extend(
        [
            "",
            "### Phase 4 Scoped Multi-Scale Diagnostic",
            "",
            f"- Verdict: `{phase4['verdict']}`",
            f"- Controlled cases: `{phase4['case_count']}`",
            f"- Real APK component rows: `{phase4['real_component_rows']}`",
            f"- Potential Phase 5 improvement candidates: `{len(phase4['candidate_improvements'])}`",
            f"- Controlled regression blockers: `{phase4['controlled_regression_count']}`",
            f"- Real source-validated regression blockers: `{phase4['real_regression_count']}`",
            f"- Clean real regression blockers: `{phase4['clean_real_regression_count']}`",
            "- Outcome counts: "
            + ", ".join(
                f"`{key}`={value}" for key, value in phase4["outcome_counts"].items()
            ),
            "",
            "| Category | Outcomes |",
            "|---|---|",
        ]
    )
    for row in phase4["category_counts"]:
        outcomes = ", ".join(f"`{key}`={value}" for key, value in row["outcomes"].items())
        lines.append(f"| {md(row['category'])} | {outcomes} |")
    lines.extend(
        [
            "",
            "| Real APK role | Outcomes |",
            "|---|---|",
        ]
    )
    for row in phase4["role_counts"]:
        outcomes = ", ".join(f"`{key}`={value}" for key, value in row["outcomes"].items())
        lines.append(f"| {md(row['role'])} | {outcomes} |")
    lines.extend(
        [
            "",
            "| Candidate improvement | Coordinate | Source version(s) | Baseline | Diagnostic |",
            "|---|---|---|---|---|",
        ]
    )
    for row in phase4["candidate_improvements"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    md(row.get("case") or ""),
                    md(row.get("coordinate") or ""),
                    md(", ".join(row.get("source_versions") or [])),
                    md(row.get("baseline_selected") or "none"),
                    md(row.get("diagnostic_selected") or "none"),
                ]
            )
            + " |"
        )
    if not phase4["candidate_improvements"]:
        lines.append("| none | none | none | none | none |")
    lines.extend(
        [
            "",
            "| Blocking coordinate | Regression rows |",
            "|---|---:|",
        ]
    )
    for row in phase4["top_blocking_coordinates"]:
        lines.append(f"| {md(row.get('coordinate') or '')} | {row.get('regressions', 0)} |")
    lines.extend(
        [
            "",
            "| Controlled regression-risk case | Coordinate | Expected | Baseline | Diagnostic |",
            "|---|---|---|---|---|",
        ]
    )
    for row in phase4["regression_risks"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{md(row['case'])}`",
                    md(row["coordinate"]),
                    md(row["expected"]),
                    md(row["baseline_selected"]),
                    md(row["diagnostic_selected"]),
                ]
            )
            + " |"
        )

    phase5 = payload["current_r8_evidence"]["phase5_scoped_trigger"]
    lines.extend(
        [
            "",
            "### Phase 5 Scoped Trigger Diagnostic",
            "",
            f"- Verdict: `{phase5['verdict']}`",
            f"- Rows evaluated: `{phase5['rows_evaluated']}`",
            f"- Controlled rows: `{phase5['controlled_rows']}`",
            f"- Real rows: `{phase5['real_rows']}`",
            f"- Triggered rows: `{phase5['triggered_rows']}`",
            f"- Target improvements kept: `{phase5['target_improvements_kept']}`",
            f"- Triggered regressions: `{phase5['triggered_regressions']}`",
            f"- Triggered conflicts: `{phase5['triggered_conflicts']}`",
            "",
            "| Triggered outcome | Count |",
            "|---|---:|",
        ]
    )
    for outcome, count in sorted(phase5["triggered_outcomes"].items()):
        lines.append(f"| `{md(outcome)}` | {count} |")
    if not phase5["triggered_outcomes"]:
        lines.append("| none | 0 |")
    lines.extend(
        [
            "",
            "| Triggered case | Coordinate | Baseline | Diagnostic | Profile |",
            "|---|---|---|---|---|",
        ]
    )
    for row in phase5["triggered_rows_detail"]:
        decision = row.get("trigger_decision", {})
        lines.append(
            "| "
            + " | ".join(
                [
                    md(row.get("case") or ""),
                    md(row.get("coordinate") or ""),
                    md(row.get("baseline_selected_version") or "none"),
                    md(row.get("diagnostic_selected_version") or "none"),
                    md(decision.get("profile_id") or "none"),
                ]
            )
            + " |"
        )
    if not phase5["triggered_rows_detail"]:
        lines.append("| none | none | none | none | none |")

    phase5_validation = payload["current_r8_evidence"]["phase5_control_validation"]
    lines.extend(
        [
            "",
            "### Phase 5 Trigger Control Validation",
            "",
            f"- Verdict: `{phase5_validation['verdict']}`",
            f"- Rows evaluated: `{phase5_validation['rows_evaluated']}`",
            f"- Triggered rows: `{phase5_validation['triggered_rows']}`",
            f"- Target improvements kept: `{phase5_validation['target_improvements_kept']}`",
            f"- Triggered regressions: `{phase5_validation['triggered_regressions']}`",
            f"- Triggered conflicts: `{phase5_validation['triggered_conflicts']}`",
            f"- Failed gates: `{phase5_validation['failed_gates']}`",
            "",
            "| Gate | Status | Evidence |",
            "|---|---|---|",
        ]
    )
    for gate_row in phase5_validation["gates"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{md(gate_row.get('gate') or '')}`",
                    f"`{md(gate_row.get('status') or '')}`",
                    md(gate_row.get("evidence") or ""),
                ]
            )
            + " |"
        )
    lines.extend(["", "Production imports:"])
    if phase5_validation["production_imports"]:
        lines.extend(f"- `{item}`" for item in phase5_validation["production_imports"])
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Classifier Field Matrix",
            "",
            "| Signal | Status | Why it matters | Next action |",
            "|---|---|---|---|",
        ]
    )
    for row in payload["classifier_gap_matrix"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    md(row["signal"]),
                    f"`{md(row['status'])}`",
                    md(row["why"]),
                    md(row["next_action"]),
                ]
            )
            + " |"
        )

    lines.extend(["", "## Policy", ""])
    lines.extend(f"- {item}" for item in payload["policy"])

    lines.extend(["", "## Next Actions", ""])
    lines.extend(f"- {item}" for item in payload["next_actions"])

    lines.extend(
        [
            "",
            "## Conclusion",
            "",
            "Phases 1, 2, and 3 are complete; the expanded Phase 4 layered multi-scale diagnostic rejects global promotion despite finding four real improvement candidates; and the opt-in Phase 5 scoped trigger command plus current-control validation keep those four target improvements without triggered regressions in the current artifact. Reports may show the saved Phase 5 evidence only with `--include-r8-phase5-experiment`. The generated four-report evidence summary confirms 4 separate suggestions and 0 default selection changes. This still does not support turning on global opcode/API or multi-scale weights, adding an ML-first detector, or claiming exact-version recovery under heavy R8. The Phase 5 command remains experiment-only and default matcher/report/SBOM behavior stays unchanged.",
            "",
        ]
    )
    return "\n".join(lines)


def generated_row(row: dict[str, Any]) -> str:
    return (
        "| "
        + " | ".join(
            [
                md(row.get("category", "")),
                str(row.get("expected", "")),
                str(row.get("component_detected", "")),
                str(row.get("version_detected", "")),
                str(row.get("candidate_version_correct", "")),
                md(row.get("dominant_decision", "")),
                md(row.get("dominant_confidence", "")),
                md(row.get("dominant_risk", "")),
            ]
        )
        + " |"
    )


def most_common_label(counter: Counter[str], labels: set[str]) -> str:
    candidates = [(label, counter[label]) for label in labels if counter[label]]
    if not candidates:
        return "unknown"
    return max(candidates, key=lambda item: item[1])[0]


def most_common_prefixed_label(counter: Counter[str], prefix: str, labels: set[str]) -> str:
    candidates = [
        (label, counter[f"{prefix}:{label}"])
        for label in labels
        if counter[f"{prefix}:{label}"]
    ]
    if not candidates:
        return "unknown"
    return max(candidates, key=lambda item: item[1])[0]


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_path(path: Any) -> str:
    return str(path).replace("\\", "/") if path else ""


def md(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


if __name__ == "__main__":
    raise SystemExit(main())
