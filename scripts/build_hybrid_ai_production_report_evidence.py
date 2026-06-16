from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from apk_sbom.models import DetectedLibrary  # noqa: E402
from apk_sbom.report import (  # noqa: E402
    DEFAULT_AI_R8_DL_METRICS_JSON,
    DEFAULT_AI_R8_SUGGESTIONS_JSON,
    DEFAULT_HYBRID_MATCHER_ROUTER_JSON,
    load_hybrid_ai_assistance_evidence,
)


DEFAULT_OUTPUT_JSON = Path(
    "data/results/evaluation/hybrid-ai-production-reporting.json"
)
DEFAULT_OUTPUT_DOC = Path("docs/evaluation/HYBRID_AI_PRODUCTION_REPORTING.md")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build the production report-only hybrid/AI reporting evidence artifact."
    )
    parser.add_argument(
        "--hybrid-matcher-router-json",
        default=str(DEFAULT_HYBRID_MATCHER_ROUTER_JSON),
        help="Hybrid matcher router JSON.",
    )
    parser.add_argument(
        "--ai-r8-suggestions-json",
        default=str(DEFAULT_AI_R8_SUGGESTIONS_JSON),
        help="AI R8 suggestions JSON.",
    )
    parser.add_argument(
        "--ai-r8-dl-metrics-json",
        default=str(DEFAULT_AI_R8_DL_METRICS_JSON),
        help="AI R8 DL prototype metrics JSON.",
    )
    parser.add_argument(
        "--output-json",
        default=str(DEFAULT_OUTPUT_JSON),
        help="Output JSON summary.",
    )
    parser.add_argument(
        "--output-doc",
        default=str(DEFAULT_OUTPUT_DOC),
        help="Output Markdown summary.",
    )
    args = parser.parse_args(argv)

    payload = build_payload(
        router_json=Path(args.hybrid_matcher_router_json),
        ai_json=Path(args.ai_r8_suggestions_json),
        dl_json=Path(args.ai_r8_dl_metrics_json),
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
                "output_json": str(output_json),
                "output_doc": str(output_doc),
                "router_rows": payload["dataset"]["hybrid_router"]["router_rows"],
                "ml_suggestion_rows": payload["dataset"]["phase6a_ml"][
                    "suggestion_rows"
                ],
                "dl_production_wiring": payload["dataset"]["phase6b_dl"][
                    "production_wiring"
                ],
                "verdict": payload["verdict"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def build_payload(
    *,
    router_json: Path,
    ai_json: Path,
    dl_json: Path,
) -> dict[str, Any]:
    router = _load_json(router_json)
    ai = _load_json(ai_json)
    dl = _load_json(dl_json)
    router_rows = router.get("rows", [])
    profile_counts = Counter(
        row.get("recommended_profile") for row in router_rows if row.get("recommended_profile")
    )
    priority_counts = Counter(row.get("priority") for row in router_rows if row.get("priority"))
    representative_context = _representative_report_context(router_rows)
    report_payload = load_hybrid_ai_assistance_evidence(
        router_json,
        ai_suggestions_path=ai_json,
        dl_metrics_path=dl_json,
        apk_path=representative_context["apk_path"],
        components=representative_context["components"],
    )
    return {
        "schema_version": "hybrid-ai-production-reporting-v1",
        "verdict": "promoted-to-production-report-only-not-matcher-authority",
        "report_only": True,
        "default_matcher_unchanged": True,
        "production_entrypoint": {
            "command_flag": "--include-hybrid-ai-assistance",
            "json_field": "hybrid_ai_assistance",
            "markdown_heading": "Hybrid AI Matcher Assistance",
            "html_heading": "Hybrid AI Matcher Assistance",
        },
        "guardrails": [
            "The current weighted matcher remains the SBOM authority.",
            "Hybrid router rows explain strategy profiles and prioritization only.",
            "RandomForest suggestions can affect report wording and triage only.",
            "The Transformer prototype is surfaced as disabled production status only.",
            "Detected components, selected versions, SBOM output, vulnerability labels, source-validation metrics, and default matcher scoring stay unchanged.",
        ],
        "sources": {
            "hybrid_matcher_router_json": str(router_json),
            "ai_r8_suggestions_json": str(ai_json),
            "ai_r8_dl_metrics_json": str(dl_json),
        },
        "dataset": {
            "hybrid_router": {
                "router_rows": router.get("summary", {}).get(
                    "router_rows", len(router_rows)
                ),
                "unique_cases": router.get("summary", {}).get("unique_cases", 0),
                "unique_coordinates": router.get("summary", {}).get(
                    "unique_coordinates", 0
                ),
                "profile_counts": dict(sorted(profile_counts.items())),
                "priority_counts": dict(sorted(priority_counts.items())),
                "top_recommended_profiles": router.get("summary", {}).get(
                    "top_recommended_profiles", []
                ),
            },
            "phase6a_ml": {
                "model_type": ai.get("model_type"),
                "model_version": ai.get("model_version"),
                "status": ai.get("status"),
                "suggestion_rows": ai.get("summary", {}).get(
                    "suggestion_rows", len(ai.get("suggestions", []))
                ),
                "recommendation_counts": ai.get("summary", {}).get(
                    "recommendation_counts", {}
                ),
            },
            "phase6b_dl": {
                "model_type": dl.get("model_type"),
                "status": dl.get("status"),
                "production_wiring": dl.get("production_wiring", "disabled"),
                "dataset_rows": dl.get("dataset", {}).get("rows"),
                "test_accuracy": dl.get("test", {}).get("accuracy"),
                "test_macro_f1": dl.get("test", {}).get("macro_f1"),
            },
        },
        "representative_report_context": {
            "apk_path": representative_context["apk_path"],
            "component_coordinates": [
                component.coordinate for component in representative_context["components"]
            ],
            "report_payload_summary": report_payload.get("summary", {})
            if report_payload
            else {},
        },
    }


def _representative_report_context(rows: list[dict[str, Any]]) -> dict[str, Any]:
    p1_rows = [row for row in rows if row.get("priority") == "P1"]
    row = p1_rows[0] if p1_rows else (rows[0] if rows else {})
    coordinate = str(row.get("coordinate") or "example:placeholder")
    group, artifact = _split_coordinate(coordinate)
    version = str(row.get("candidate_version") or row.get("source_version") or "0")
    case_id = str(row.get("case_id") or "representative")
    return {
        "apk_path": f"{case_id}.apk",
        "components": [
            DetectedLibrary(
                group=group,
                artifact=artifact,
                version=version,
                confidence=0.0,
                match_type="hybrid-ai-report-context",
                evidence=[],
            )
        ],
    }


def _split_coordinate(coordinate: str) -> tuple[str, str]:
    if ":" not in coordinate:
        return coordinate, "unknown"
    group, artifact = coordinate.split(":", 1)
    return group, artifact


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_markdown(payload: dict[str, Any]) -> str:
    dataset = payload["dataset"]
    router = dataset["hybrid_router"]
    ml = dataset["phase6a_ml"]
    dl = dataset["phase6b_dl"]
    report_context = payload["representative_report_context"]
    lines = [
        "# Hybrid AI Production Reporting",
        "",
        "Generated by `scripts/build_hybrid_ai_production_report_evidence.py`.",
        "",
        "This artifact documents the production-facing promotion of the hybrid matcher router plus Phase 6 ML/DL evidence into `generate-report` as a guarded report-only assistance layer.",
        "",
        "## Verdict",
        "",
        f"- `{payload['verdict']}`",
        "- This is a production report integration, not automatic matcher promotion.",
        "- The JSON field is `hybrid_ai_assistance`.",
        "- The CLI flag is `--include-hybrid-ai-assistance`.",
        "",
        "## Guardrails",
        "",
    ]
    for guardrail in payload["guardrails"]:
        lines.append(f"- {guardrail}")
    lines.extend(
        [
            "",
            "## Dataset Evidence",
            "",
            f"- Hybrid router rows: `{router['router_rows']}`",
            f"- Hybrid router unique cases: `{router['unique_cases']}`",
            f"- Hybrid router unique coordinates: `{router['unique_coordinates']}`",
            f"- Hybrid router priority counts: `{json.dumps(router['priority_counts'], sort_keys=True)}`",
            f"- ML model: `{ml['model_type']}` / `{ml['model_version']}`",
            f"- ML suggestion rows: `{ml['suggestion_rows']}`",
            f"- ML recommendation counts: `{json.dumps(ml['recommendation_counts'], sort_keys=True)}`",
            f"- DL model: `{dl['model_type']}`",
            f"- DL production wiring: `{dl['production_wiring']}`",
            f"- DL dataset rows: `{dl['dataset_rows']}`",
            f"- DL test macro-F1: `{_number(dl['test_macro_f1'])}`",
            "",
            "## Representative Report Payload Check",
            "",
            f"- Representative APK key: `{report_context['apk_path']}`",
            f"- Representative coordinates: `{', '.join(report_context['component_coordinates'])}`",
            f"- Report payload summary: `{json.dumps(report_context['report_payload_summary'], sort_keys=True)}`",
            "",
            "## Demo Command",
            "",
            "```powershell",
            "apk-sbom generate-report <apk-path> --include-hybrid-ai-assistance --skip-osv",
            "```",
            "",
            "Use OSV normally when presenting CVE behavior; `--skip-osv` is only for a fast local report-generation smoke.",
            "",
            "## Interpretation",
            "",
            "The MVP can now show hybrid strategy routing, RandomForest triage, and Transformer prototype status from the normal report path. The report is transparent about the limit: these signals guide analysis and future matcher experiments, but they are not exact-version or CVE authority.",
            "",
        ]
    )
    return "\n".join(lines)


def _number(value: object) -> str:
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


if __name__ == "__main__":
    raise SystemExit(main())
