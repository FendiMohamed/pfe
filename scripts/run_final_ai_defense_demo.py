from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SMOKE_JSON = Path(
    "data/results/evaluation/final-hybrid-ai-demo-smoke.json"
)
DEFAULT_GATE_JSON = Path(
    "data/results/evaluation/ai-r8-mvp-integration-gate.json"
)
DEFAULT_VULNERABLE_REPORT = Path(
    "data/results/demo-osv-vulnerable-jackson-databind/report.json"
)
DEFAULT_OUTPUT_JSON = Path(
    "data/results/evaluation/final-ai-defense-demo.json"
)
DEFAULT_OUTPUT_DOC = Path("docs/evaluation/FINAL_AI_DEFENSE_DEMO.md")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Build the final clean/CVE/R8 AI defense verdict from current "
            "project evidence."
        )
    )
    parser.add_argument("--smoke-json", default=str(DEFAULT_SMOKE_JSON))
    parser.add_argument("--gate-json", default=str(DEFAULT_GATE_JSON))
    parser.add_argument(
        "--vulnerable-report",
        default=str(DEFAULT_VULNERABLE_REPORT),
    )
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--output-doc", default=str(DEFAULT_OUTPUT_DOC))
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Regenerate the cached hybrid smoke and AI integration gate first.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.refresh:
        refresh_evidence()

    payload = build_payload(
        smoke=_load_json(Path(args.smoke_json)),
        gate=_load_json(Path(args.gate_json)),
        vulnerable_report=_load_json(Path(args.vulnerable_report)),
        sources={
            "hybrid_smoke_json": normalize_path(args.smoke_json),
            "integration_gate_json": normalize_path(args.gate_json),
            "vulnerable_report_json": normalize_path(args.vulnerable_report),
        },
    )
    output_json = Path(args.output_json)
    output_doc = Path(args.output_doc)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_doc.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    output_doc.write_text(build_markdown(payload), encoding="utf-8")
    print(
        json.dumps(
            {
                "ready": payload["verdict"]["defense_demo_ready"],
                "json": normalize_path(output_json),
                "doc": normalize_path(output_doc),
                "checks_passed": payload["verdict"]["checks_passed"],
                "checks_total": payload["verdict"]["checks_total"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if payload["verdict"]["defense_demo_ready"] else 1


def refresh_evidence() -> None:
    commands = (
        [sys.executable, "scripts/build_final_hybrid_ai_demo_smoke.py"],
        [sys.executable, "scripts/build_ai_r8_mvp_integration_gate.py"],
        [sys.executable, "scripts/build_ai_r8_final_evaluation.py"],
    )
    for command in commands:
        subprocess.run(command, cwd=PROJECT_ROOT, check=True)


def build_payload(
    *,
    smoke: dict[str, Any],
    gate: dict[str, Any],
    vulnerable_report: dict[str, Any],
    sources: dict[str, str] | None = None,
) -> dict[str, Any]:
    smoke_summary = smoke.get("summary") or {}
    targets = {
        row.get("case_id"): row
        for row in smoke.get("targets") or []
        if row.get("case_id")
    }
    clean = targets.get("fdroid") or {}
    hard = targets.get("aegis-authenticator") or {}
    integration = gate.get("mvp_integration") or {}
    model_decisions = gate.get("model_decisions") or {}
    model_evidence = gate.get("models") or {}
    osv = vulnerable_report.get("osv") or {}

    cves = sorted(
        {
            alias
            for result in osv.get("results") or []
            for vulnerability in result.get("vulnerabilities") or []
            for alias in vulnerability.get("aliases") or []
            if str(alias).startswith("CVE-")
        }
    )
    checks = {
        "clean_case_present": bool(clean),
        "hard_case_present": bool(hard),
        "default_vs_ai_outputs_unchanged": bool(
            smoke_summary.get("all_outputs_unchanged")
        ),
        "ai_sections_visible": bool(
            smoke_summary.get("all_hybrid_sections_visible")
        ),
        "clean_case_has_components": (
            clean.get("comparison", {}).get("default_component_count", 0) > 0
        ),
        "hard_case_has_components": (
            hard.get("comparison", {}).get("default_component_count", 0) > 0
        ),
        "positive_cve_fixture_detected": (
            osv.get("confirmed_vulnerabilities", 0) >= 3
            and len(cves) >= 3
        ),
        "report_only_integration_ready": (
            integration.get("report_only_ready") is True
        ),
        "matcher_authority_blocked": (
            integration.get("matcher_authority_ready") is False
        ),
        "deterministic_matcher_remains_authority": (
            model_decisions.get("matcher_or_sbom_authority", {}).get("decision")
            == "blocked-keep-deterministic-matcher-authority"
        ),
    }
    passed = sum(bool(value) for value in checks.values())
    return {
        "schema_version": "final-ai-defense-demo-v1",
        "scope": (
            "Single defense verdict covering a clean real APK, a controlled "
            "positive-CVE APK, a hard real APK, and the ML/DL integration gate."
        ),
        "verdict": {
            "defense_demo_ready": passed == len(checks),
            "checks_passed": passed,
            "checks_total": len(checks),
            "mvp_integration_level": integration.get(
                "current_mvp_integration_level"
            )
            or integration.get("current_integration_level"),
            "matcher_authority_ready": integration.get(
                "matcher_authority_ready"
            ),
        },
        "checks": checks,
        "demo_cases": {
            "clean_real_apk": summarize_smoke_target(clean),
            "hard_real_apk": summarize_smoke_target(hard),
            "controlled_positive_cve": {
                "apk_path": vulnerable_report.get("apk", {}).get("apk_path"),
                "components": len(
                    vulnerable_report.get("detected_components") or []
                ),
                "confirmed_vulnerabilities": osv.get(
                    "confirmed_vulnerabilities",
                    0,
                ),
                "severity_counts": osv.get("severity_counts") or {},
                "cves": cves,
            },
        },
        "model_evidence": {
            "random_forest": compact_model(
                model_evidence.get("phase6a_random_forest"),
                decision=model_decisions.get("phase6a_random_forest"),
            ),
            "structured_transformer": compact_model(
                model_evidence.get("phase6b_structured_transformer"),
                decision=model_decisions.get("phase6b_structured_transformer"),
            ),
            "mvp_safe_transformer": compact_model(
                model_evidence.get("phase6b_mvp_safe_transformer"),
                decision=model_decisions.get("phase6b_mvp_safe_transformer"),
            ),
            "raw_opcode_transformer": compact_model(
                model_evidence.get("raw_opcode_transformer"),
                decision=model_decisions.get("raw_opcode_transformer"),
            ),
        },
        "guardrail_statement": (
            "AI assistance is integrated into the report surface only. It does "
            "not change matcher-selected versions, CycloneDX components, or "
            "vulnerability labels."
        ),
        "sources": sources or {},
    }


def summarize_smoke_target(row: dict[str, Any]) -> dict[str, Any]:
    comparison = row.get("comparison") or {}
    assistance = row.get("hybrid_section_summary") or {}
    return {
        "case_id": row.get("case_id"),
        "label": row.get("label"),
        "apk_path": row.get("apk_path"),
        "components": comparison.get("default_component_count", 0),
        "outputs_unchanged": comparison.get("unchanged") is True,
        "ai_section_visible": row.get("hybrid_section_visible") is True,
        "ai_report_only": row.get("hybrid_section_report_only") is True,
        "router_matching_rows": assistance.get("router_matching_rows", 0),
        "ml_matching_rows": assistance.get("ml_matching_rows", 0),
        "structural_gate_promotion_candidates": assistance.get(
            "structural_gate_promotion_candidates",
            0,
        ),
    }


def compact_model(
    model: Any,
    *,
    decision: Any = None,
) -> dict[str, Any]:
    if not isinstance(model, dict):
        return {}
    decision_value = (
        decision.get("decision")
        if isinstance(decision, dict)
        else model.get("decision") or model.get("verdict")
    )
    return {
        "rows": model.get("dataset_rows") or model.get("method_sequence_rows"),
        "test_macro_f1": model.get("test_macro_f1"),
        "test_accuracy": model.get("test_accuracy"),
        "decision": decision_value,
    }


def build_markdown(payload: dict[str, Any]) -> str:
    verdict = payload["verdict"]
    cases = payload["demo_cases"]
    lines = [
        "# Final AI Defense Demo",
        "",
        "Generated by `python scripts/run_final_ai_defense_demo.py --refresh`.",
        "",
        payload["scope"],
        "",
        "## Verdict",
        "",
        f"- Defense demo ready: `{str(verdict['defense_demo_ready']).lower()}`",
        f"- Checks passed: `{verdict['checks_passed']}/{verdict['checks_total']}`",
        f"- MVP integration level: `{verdict['mvp_integration_level']}`",
        f"- Matcher authority ready: `{str(verdict['matcher_authority_ready']).lower()}`",
        "",
        "## Demo Cases",
        "",
        "| Lane | Components | Result |",
        "|---|---:|---|",
        (
            f"| Clean real APK | {cases['clean_real_apk']['components']} | "
            "AI section visible; outputs unchanged |"
        ),
        (
            f"| Hard real APK | {cases['hard_real_apk']['components']} | "
            "AI/R8 triage visible; outputs unchanged |"
        ),
        (
            "| Controlled positive CVE | "
            f"{cases['controlled_positive_cve']['components']} | "
            f"{cases['controlled_positive_cve']['confirmed_vulnerabilities']} "
            "confirmed vulnerabilities |"
        ),
        "",
        "## Positive CVEs",
        "",
    ]
    lines.extend(
        f"- `{cve}`" for cve in cases["controlled_positive_cve"]["cves"]
    )
    lines.extend(
        [
            "",
            "## AI Model Evidence",
            "",
            "| Model | Rows | Test macro-F1 | Decision |",
            "|---|---:|---:|---|",
        ]
    )
    for label, model in payload["model_evidence"].items():
        lines.append(
            f"| `{label}` | {model.get('rows', '')} | "
            f"{model.get('test_macro_f1', '')} | "
            f"`{model.get('decision', '')}` |"
        )
    lines.extend(["", "## Safety Checks", ""])
    lines.extend(
        f"- `{key}`: `{str(value).lower()}`"
        for key, value in payload["checks"].items()
    )
    lines.extend(
        [
            "",
            "## Guardrail",
            "",
            payload["guardrail_statement"],
            "",
            "## Source Artifacts",
            "",
        ]
    )
    lines.extend(
        f"- `{key}`: `{value}`"
        for key, value in sorted(payload["sources"].items())
    )
    lines.append("")
    return "\n".join(lines)


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Required demo artifact not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_path(path: str | Path) -> str:
    return str(path).replace("\\", "/")


if __name__ == "__main__":
    raise SystemExit(main())
