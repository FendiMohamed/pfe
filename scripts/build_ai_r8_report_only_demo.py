from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from apk_sbom.ai_r8_assistant import DEFAULT_SUGGESTIONS_JSON  # noqa: E402
from apk_sbom.reference_features import DEFAULT_FEATURE_DB_PATH  # noqa: E402
from apk_sbom.report import generate_final_report  # noqa: E402


DEFAULT_APK = Path("data/test_apks/generated-gson-2-8-9-r8-rename.apk")
DEFAULT_OUTPUT_ROOT = Path("data/results/experiments/ai-r8-report-only-demo")
DEFAULT_OUTPUT_JSON = Path("data/results/evaluation/ai-r8-report-only-demo.json")
DEFAULT_OUTPUT_DOC = Path("docs/evaluation/AI_R8_REPORT_ONLY_DEMO.md")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run a small opt-in report demo proving AI R8 suggestions are report-only."
        ),
    )
    parser.add_argument("--apk", default=str(DEFAULT_APK), help="APK path.")
    parser.add_argument(
        "--db-path",
        default=str(DEFAULT_FEATURE_DB_PATH),
        help="Reference feature DB path.",
    )
    parser.add_argument(
        "--suggestions-json",
        default=str(DEFAULT_SUGGESTIONS_JSON),
        help="AI R8 suggestions JSON.",
    )
    parser.add_argument(
        "--output-root",
        default=str(DEFAULT_OUTPUT_ROOT),
        help="Output root for baseline and AI report runs.",
    )
    parser.add_argument(
        "--output-json",
        default=str(DEFAULT_OUTPUT_JSON),
        help="Summary JSON output.",
    )
    parser.add_argument(
        "--output-doc",
        default=str(DEFAULT_OUTPUT_DOC),
        help="Summary Markdown output.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    output_root = Path(args.output_root)
    baseline_dir = output_root / "baseline"
    ai_dir = output_root / "with-ai"

    baseline = generate_final_report(
        args.apk,
        output_dir=baseline_dir,
        db_path=args.db_path,
        query_osv=False,
    )
    with_ai = generate_final_report(
        args.apk,
        output_dir=ai_dir,
        db_path=args.db_path,
        query_osv=False,
        ai_r8_suggestions_json=args.suggestions_json,
    )

    payload = build_payload(
        apk_path=Path(args.apk),
        db_path=Path(args.db_path),
        suggestions_path=Path(args.suggestions_json),
        baseline_report=Path(baseline.report_json),
        baseline_sbom=Path(baseline.sbom_json),
        ai_report=Path(with_ai.report_json),
        ai_sbom=Path(with_ai.sbom_json),
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
                "sbom_content_unchanged": payload["comparison"][
                    "sbom_semantic_content_unchanged"
                ],
                "components_unchanged": payload["comparison"][
                    "detected_components_unchanged"
                ],
                "ai_section_present": payload["ai_report"]["ai_section_present"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def build_payload(
    *,
    apk_path: Path,
    db_path: Path,
    suggestions_path: Path,
    baseline_report: Path,
    baseline_sbom: Path,
    ai_report: Path,
    ai_sbom: Path,
) -> dict:
    baseline_payload = _load_json(baseline_report)
    ai_payload = _load_json(ai_report)
    baseline_sbom_payload = _load_json(baseline_sbom)
    ai_sbom_payload = _load_json(ai_sbom)
    baseline_components = baseline_payload.get("detected_components", [])
    ai_components = ai_payload.get("detected_components", [])
    ai_assistance = ai_payload.get("ai_r8_assistance", {})
    return {
        "schema_version": "ai-r8-report-only-demo-v1",
        "apk": str(apk_path),
        "db_path": str(db_path),
        "suggestions_json": str(suggestions_path),
        "baseline_report": str(baseline_report),
        "ai_report": str(ai_report),
        "baseline_sbom": str(baseline_sbom),
        "ai_sbom": str(ai_sbom),
        "comparison": {
            "sbom_raw_sha256_unchanged": _sha256(baseline_sbom) == _sha256(ai_sbom),
            "sbom_semantic_content_unchanged": _normalized_sbom(baseline_sbom_payload)
            == _normalized_sbom(ai_sbom_payload),
            "sbom_components_unchanged": baseline_sbom_payload.get("components", [])
            == ai_sbom_payload.get("components", []),
            "detected_components_unchanged": baseline_components == ai_components,
            "vulnerability_labels_unchanged": baseline_payload.get("osv")
            == ai_payload.get("osv"),
            "baseline_component_count": len(baseline_components),
            "ai_component_count": len(ai_components),
        },
        "ai_report": {
            "ai_section_present": "ai_r8_assistance" in ai_payload,
            "report_only": ai_assistance.get("report_only"),
            "model_type": ai_assistance.get("model_type"),
            "model_version": ai_assistance.get("model_version"),
            "matching_rows": ai_assistance.get("summary", {}).get("matching_rows", 0),
            "matching_recommendation_counts": ai_assistance.get("summary", {}).get(
                "matching_recommendation_counts",
                {},
            ),
        },
        "guardrail": (
            "The AI section is report-only and does not change components, selected "
            "versions, SBOM output, vulnerability labels, or source-validation metrics."
        ),
    }


def build_markdown(payload: dict) -> str:
    comparison = payload["comparison"]
    ai_report = payload["ai_report"]
    return "\n".join(
        [
            "# AI R8 Report-Only Demo",
            "",
            "Generated by `scripts/build_ai_r8_report_only_demo.py`.",
            "",
            "This proof runs the same APK twice: once with the normal report path and once with `--include-ai-r8-suggestions` equivalent report wiring.",
            "",
            "## Inputs",
            "",
            f"- APK: `{payload['apk']}`",
            f"- DB: `{payload['db_path']}`",
            f"- Suggestions JSON: `{payload['suggestions_json']}`",
            "",
            "## Result",
            "",
            f"- AI section present: `{ai_report['ai_section_present']}`",
            f"- Report-only: `{ai_report.get('report_only')}`",
            f"- Model: `{ai_report.get('model_type')}` / `{ai_report.get('model_version')}`",
            f"- Matching AI rows: `{ai_report.get('matching_rows')}`",
            f"- Matching recommendation counts: `{json.dumps(ai_report.get('matching_recommendation_counts', {}), sort_keys=True)}`",
            "",
            "## No-Change Guardrail",
            "",
            f"- SBOM semantic content unchanged: `{comparison['sbom_semantic_content_unchanged']}`",
            f"- SBOM components unchanged: `{comparison['sbom_components_unchanged']}`",
            f"- Raw SBOM SHA-256 unchanged: `{comparison['sbom_raw_sha256_unchanged']}`",
            f"- Detected components unchanged: `{comparison['detected_components_unchanged']}`",
            f"- Vulnerability labels unchanged: `{comparison['vulnerability_labels_unchanged']}`",
            f"- Baseline component count: `{comparison['baseline_component_count']}`",
            f"- AI report component count: `{comparison['ai_component_count']}`",
            "",
            "Raw SBOM hashes differ because each CycloneDX file is generated with a fresh `serialNumber` and `metadata.timestamp`; normalized semantic content removes those run-specific fields.",
            "",
            payload["guardrail"],
            "",
        ]
    )


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _normalized_sbom(payload: dict) -> dict:
    normalized = json.loads(json.dumps(payload, sort_keys=True))
    normalized.pop("serialNumber", None)
    metadata = normalized.get("metadata")
    if isinstance(metadata, dict):
        metadata.pop("timestamp", None)
    return normalized


if __name__ == "__main__":
    raise SystemExit(main())
