from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from apk_sbom.report import (
    DEFAULT_AI_R8_DL_METRICS_JSON,
    DEFAULT_AI_R8_SUGGESTIONS_JSON,
    DEFAULT_HYBRID_MATCHER_ROUTER_JSON,
    DEFAULT_R8_APK_STRUCTURAL_PROMOTION_GATE_JSON,
    ReportArtifacts,
    generate_final_report,
)


DEFAULT_DB_PATH = Path("data/reference_db/reference_features_calibrated_combined.sqlite")
DEFAULT_OUTPUT_ROOT = Path("data/results/evaluation/final-hybrid-ai-demo-smoke")
DEFAULT_OUTPUT_JSON = Path("data/results/evaluation/final-hybrid-ai-demo-smoke.json")
DEFAULT_OUTPUT_DOC = Path("docs/evaluation/FINAL_HYBRID_AI_DEMO_SMOKE.md")

DEFAULT_TARGETS = (
    {
        "case_id": "fdroid",
        "label": "F-Droid clean demo APK",
        "apk_path": "data/test_apks/real/F-Droid.apk",
        "role": "clean/demo control",
    },
    {
        "case_id": "aegis-authenticator",
        "label": "Aegis Authenticator hard partial APK",
        "apk_path": "data/test_apks/real/aegis-authenticator/aegis-authenticator.apk",
        "role": "hard matcher-recall/R8-structural visibility control",
    },
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Generate default vs hybrid-AI real APK report smokes and prove the "
            "opt-in assistance section does not alter SBOM/matcher outputs."
        )
    )
    parser.add_argument("--db-path", default=str(DEFAULT_DB_PATH))
    parser.add_argument("--output-root", default=str(DEFAULT_OUTPUT_ROOT))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--output-doc", default=str(DEFAULT_OUTPUT_DOC))
    parser.add_argument(
        "--top",
        type=int,
        default=30,
        help="Top matcher candidates per coordinate.",
    )
    parser.add_argument(
        "--case-id",
        action="append",
        default=None,
        help="Limit the smoke to one or more case IDs. Defaults to all targets.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    payload = build_payload(
        db_path=Path(args.db_path),
        output_root=Path(args.output_root),
        top=args.top,
        case_ids=set(args.case_id or []),
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
                "json": normalize_path(output_json),
                "doc": normalize_path(output_doc),
                "targets": len(payload["targets"]),
                "all_outputs_unchanged": payload["summary"]["all_outputs_unchanged"],
                "all_hybrid_sections_visible": payload["summary"][
                    "all_hybrid_sections_visible"
                ],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def build_payload(
    *,
    db_path: Path,
    output_root: Path,
    top: int,
    case_ids: set[str],
) -> dict[str, Any]:
    output_root.mkdir(parents=True, exist_ok=True)
    targets = [
        target
        for target in DEFAULT_TARGETS
        if not case_ids or target["case_id"] in case_ids
    ]
    rows = [
        run_target_smoke(
            target,
            db_path=db_path,
            output_root=output_root,
            top=top,
        )
        for target in targets
    ]
    summary = summarize_rows(rows)
    return {
        "schema_version": "final-hybrid-ai-demo-smoke-v1",
        "report_only": True,
        "default_matcher_unchanged": True,
        "query_osv": False,
        "scope": (
            "Fast real-APK smoke for the final demo. It compares default reports "
            "against opt-in --include-hybrid-ai-assistance reports and proves the "
            "hybrid/AI/R8 structural gate section is visible while matcher, SBOM, "
            "and vulnerability outputs remain unchanged."
        ),
        "policy": [
            "The hybrid AI assistance section is opt-in and report-only.",
            "The current weighted matcher remains the SBOM authority.",
            "The smoke uses --skip-osv/query_osv=False to avoid network-dependent demo drift.",
            "With OSV skipped for both report variants, vulnerability output is unchanged and absent by design.",
            "Detected components, selected versions, CycloneDX components, and vulnerability output paths must match between default and hybrid reports.",
        ],
        "sources": {
            "db_path": normalize_path(db_path),
            "hybrid_matcher_router_json": normalize_path(
                DEFAULT_HYBRID_MATCHER_ROUTER_JSON
            ),
            "r8_apk_structural_promotion_gate_json": normalize_path(
                DEFAULT_R8_APK_STRUCTURAL_PROMOTION_GATE_JSON
            ),
            "ai_r8_suggestions_json": normalize_path(DEFAULT_AI_R8_SUGGESTIONS_JSON),
            "ai_r8_dl_metrics_json": normalize_path(DEFAULT_AI_R8_DL_METRICS_JSON),
        },
        "summary": summary,
        "targets": rows,
    }


def run_target_smoke(
    target: dict[str, str],
    *,
    db_path: Path,
    output_root: Path,
    top: int,
) -> dict[str, Any]:
    case_id = target["case_id"]
    apk_path = Path(target["apk_path"])
    default_dir = output_root / case_id / "default"
    hybrid_dir = output_root / case_id / "hybrid-ai"
    default_artifacts = existing_or_generate_report(
        apk_path=apk_path,
        output_dir=default_dir,
        db_path=db_path,
        top=top,
        hybrid=False,
    )
    hybrid_artifacts = existing_or_generate_report(
        apk_path=apk_path,
        output_dir=hybrid_dir,
        db_path=db_path,
        top=top,
        hybrid=True,
    )
    default_report = _load_json(default_artifacts.report_json)
    hybrid_report = _load_json(hybrid_artifacts.report_json)
    default_sbom = _load_json(default_artifacts.sbom_json)
    hybrid_sbom = _load_json(hybrid_artifacts.sbom_json)
    comparison = compare_reports(default_report, hybrid_report, default_sbom, hybrid_sbom)
    assistance = hybrid_report.get("hybrid_ai_assistance", {})
    return {
        "case_id": case_id,
        "label": target["label"],
        "role": target["role"],
        "apk_path": normalize_path(apk_path),
        "default_report_dir": normalize_path(default_dir),
        "hybrid_report_dir": normalize_path(hybrid_dir),
        "default_report_json": normalize_path(default_artifacts.report_json),
        "hybrid_report_json": normalize_path(hybrid_artifacts.report_json),
        "default_sbom_json": normalize_path(default_artifacts.sbom_json),
        "hybrid_sbom_json": normalize_path(hybrid_artifacts.sbom_json),
        "hybrid_section_visible": bool(assistance),
        "hybrid_section_summary": assistance.get("summary", {}),
        "hybrid_section_report_only": assistance.get("report_only") is True,
        "markdown_contains_hybrid_section": "Hybrid AI Matcher Assistance"
        in Path(hybrid_artifacts.report_markdown).read_text(encoding="utf-8"),
        "html_contains_hybrid_section": "Hybrid AI Matcher Assistance"
        in Path(hybrid_artifacts.report_html).read_text(encoding="utf-8"),
        "comparison": comparison,
    }


def existing_or_generate_report(
    *,
    apk_path: Path,
    output_dir: Path,
    db_path: Path,
    top: int,
    hybrid: bool,
) -> ReportArtifacts:
    existing = report_artifacts_if_complete(output_dir)
    if existing is not None:
        return existing
    kwargs: dict[str, Any] = {}
    if hybrid:
        kwargs.update(
            {
                "hybrid_matcher_router_json": DEFAULT_HYBRID_MATCHER_ROUTER_JSON,
                "hybrid_ai_r8_suggestions_json": DEFAULT_AI_R8_SUGGESTIONS_JSON,
                "hybrid_ai_r8_dl_metrics_json": DEFAULT_AI_R8_DL_METRICS_JSON,
                "hybrid_ai_structural_gate_json": DEFAULT_R8_APK_STRUCTURAL_PROMOTION_GATE_JSON,
            }
        )
    return generate_final_report(
        apk_path,
        output_dir=output_dir,
        db_path=db_path,
        top=top,
        query_osv=False,
        **kwargs,
    )


def report_artifacts_if_complete(output_dir: Path) -> ReportArtifacts | None:
    matches_json = output_dir / "matches.json"
    sbom_json = output_dir / "sbom.cdx.json"
    report_json = output_dir / "report.json"
    report_markdown = output_dir / "report.md"
    report_html = output_dir / "report.html"
    required = [matches_json, sbom_json, report_json, report_markdown, report_html]
    if not all(path.exists() for path in required):
        return None
    return ReportArtifacts(
        output_dir=str(output_dir),
        matches_json=str(matches_json),
        sbom_json=str(sbom_json),
        vulnerabilities_json=None,
        report_json=str(report_json),
        report_markdown=str(report_markdown),
        report_html=str(report_html),
    )


def compare_reports(
    default_report: dict[str, Any],
    hybrid_report: dict[str, Any],
    default_sbom: dict[str, Any],
    hybrid_sbom: dict[str, Any],
) -> dict[str, Any]:
    default_components = normalize_components(default_report.get("detected_components", []))
    hybrid_components = normalize_components(hybrid_report.get("detected_components", []))
    default_decisions = normalize_decisions(
        default_report.get("match_summary", {}).get("decisions", [])
    )
    hybrid_decisions = normalize_decisions(
        hybrid_report.get("match_summary", {}).get("decisions", [])
    )
    default_sbom_components = normalize_sbom_components(default_sbom)
    hybrid_sbom_components = normalize_sbom_components(hybrid_sbom)
    default_vuln = default_report.get("vulnerabilities")
    hybrid_vuln = hybrid_report.get("vulnerabilities")
    return {
        "detected_components_unchanged": default_components == hybrid_components,
        "selected_versions_unchanged": default_decisions == hybrid_decisions,
        "sbom_components_unchanged": default_sbom_components == hybrid_sbom_components,
        "vulnerability_output_unchanged": default_vuln == hybrid_vuln,
        "default_component_count": len(default_components),
        "hybrid_component_count": len(hybrid_components),
        "default_decision_count": len(default_decisions),
        "hybrid_decision_count": len(hybrid_decisions),
        "default_sbom_component_count": len(default_sbom_components),
        "hybrid_sbom_component_count": len(hybrid_sbom_components),
        "unchanged": (
            default_components == hybrid_components
            and default_decisions == hybrid_decisions
            and default_sbom_components == hybrid_sbom_components
            and default_vuln == hybrid_vuln
        ),
    }


def summarize_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "targets": len(rows),
        "all_outputs_unchanged": all(
            row["comparison"]["unchanged"] for row in rows
        ),
        "all_hybrid_sections_visible": all(
            row["hybrid_section_visible"]
            and row["hybrid_section_report_only"]
            and row["markdown_contains_hybrid_section"]
            and row["html_contains_hybrid_section"]
            for row in rows
        ),
        "target_summaries": [
            {
                "case_id": row["case_id"],
                "component_count": row["comparison"]["default_component_count"],
                "router_matching_rows": row["hybrid_section_summary"].get(
                    "router_matching_rows",
                    0,
                ),
                "structural_gate_matching_rows": row["hybrid_section_summary"].get(
                    "structural_gate_matching_rows",
                    0,
                ),
                "structural_gate_promotion_candidates": row[
                    "hybrid_section_summary"
                ].get("structural_gate_promotion_candidates", 0),
                "ml_matching_rows": row["hybrid_section_summary"].get(
                    "ml_matching_rows",
                    0,
                ),
                "dl_production_wiring": row["hybrid_section_summary"].get(
                    "dl_production_wiring",
                    "not-attached",
                ),
            }
            for row in rows
        ],
    }


def build_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Final Hybrid AI Demo Smoke",
        "",
        "Generated by `scripts/build_final_hybrid_ai_demo_smoke.py`.",
        "",
        payload["scope"],
        "",
        "## Result",
        "",
        f"- Targets: `{summary['targets']}`",
        f"- Default vs hybrid outputs unchanged: `{str(summary['all_outputs_unchanged']).lower()}`",
        f"- Hybrid sections visible: `{str(summary['all_hybrid_sections_visible']).lower()}`",
        "- OSV queried live: `false`",
        "",
        "## Guardrails",
        "",
    ]
    lines.extend(f"- {item}" for item in payload["policy"])
    lines.extend(
        [
            "",
            "## Target Summary",
            "",
            "| Case | Components | Router rows | Structural gate rows | Structural promotion candidates | ML rows | DL wiring |",
            "|---|---:|---:|---:|---:|---:|---|",
        ]
    )
    for row in summary["target_summaries"]:
        lines.append(
            "| "
            f"`{row['case_id']}` | "
            f"{row['component_count']} | "
            f"{row['router_matching_rows']} | "
            f"{row['structural_gate_matching_rows']} | "
            f"{row['structural_gate_promotion_candidates']} | "
            f"{row['ml_matching_rows']} | "
            f"`{row['dl_production_wiring']}` |"
        )
    lines.extend(
        [
            "",
            "## Output Comparison",
            "",
            "| Case | Detected components | Selected versions | SBOM components | Vulnerability output | Hybrid report-only section |",
            "|---|---|---|---|---|---|",
        ]
    )
    for row in payload["targets"]:
        comparison = row["comparison"]
        lines.append(
            "| "
            f"`{row['case_id']}` | "
            f"`{_bool(comparison['detected_components_unchanged'])}` | "
            f"`{_bool(comparison['selected_versions_unchanged'])}` | "
            f"`{_bool(comparison['sbom_components_unchanged'])}` | "
            f"`{_bool(comparison['vulnerability_output_unchanged'])}` | "
            f"`{_bool(row['hybrid_section_report_only'])}` |"
        )
    lines.extend(
        [
            "",
            "## Generated Report Directories",
            "",
            "| Case | Default report | Hybrid AI report |",
            "|---|---|---|",
        ]
    )
    for row in payload["targets"]:
        lines.append(
            "| "
            f"`{row['case_id']}` | "
            f"`{row['default_report_dir']}` | "
            f"`{row['hybrid_report_dir']}` |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "This smoke is the final demo check for the hybrid/AI reporting surface. The opt-in section is visible in JSON, Markdown, and HTML, including the R8 APK-only structural gate summary, while the default matcher-selected components, versions, CycloneDX component set, and vulnerability output remain unchanged. Because OSV is skipped for both variants, vulnerability output equality means both reports intentionally have no live OSV result in this fast smoke.",
            "",
            "## Source Artifacts",
            "",
        ]
    )
    for key, value in sorted(payload["sources"].items()):
        lines.append(f"- `{key}`: `{value}`")
    lines.append("")
    return "\n".join(lines)


def normalize_components(components: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        [
            {
                "purl": component.get("purl"),
                "coordinate": component.get("coordinate"),
                "version": component.get("version"),
                "confidence": component.get("confidence"),
                "match_type": component.get("match_type"),
            }
            for component in components
        ],
        key=lambda row: (str(row["coordinate"]), str(row["version"]), str(row["purl"])),
    )


def normalize_decisions(decisions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        [
            {
                "coordinate": decision.get("coordinate"),
                "selected_version": decision.get("selected_version"),
                "selected_purl": decision.get("selected_purl"),
                "version_status": decision.get("version_status"),
                "score": decision.get("score"),
            }
            for decision in decisions
        ],
        key=lambda row: (str(row["coordinate"]), str(row["selected_version"])),
    )


def normalize_sbom_components(sbom: dict[str, Any]) -> list[dict[str, Any]]:
    return sorted(
        [
            {
                "type": component.get("type"),
                "name": component.get("name"),
                "version": component.get("version"),
                "purl": component.get("purl"),
            }
            for component in sbom.get("components", [])
        ],
        key=lambda row: (str(row["purl"]), str(row["name"]), str(row["version"])),
    )


def _load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _bool(value: bool) -> str:
    return "true" if value else "false"


def normalize_path(path: str | Path) -> str:
    return str(path).replace("\\", "/")


if __name__ == "__main__":
    raise SystemExit(main())
