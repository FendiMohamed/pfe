from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path
from typing import Any


DEFAULT_REFERENCE_DB = Path("data/reference_db/reference_features_phase3_multiscale_gson.sqlite")
DEFAULT_REPORT_JSON = Path(
    "data/results/report-generated-gson-2-8-9-r8-inline-stress-phase3/report.json"
)
DEFAULT_OUTPUT_JSON = Path("data/results/evaluation/r8-multiscale-feature-diagnostics.json")
DEFAULT_OUTPUT_DOC = Path("docs/evaluation/R8_MULTISCALE_FEATURE_DIAGNOSTICS.md")


FEATURE_TABLES: list[dict[str, str]] = [
    {
        "feature": "call-chain opcode fingerprints",
        "table": "call_chain_opcode_fingerprints",
        "source": "LibHunter, LibScan",
        "scope": "method-level invoke opcode order",
    },
    {
        "feature": "basic-block opcode fingerprints",
        "table": "basic_block_opcode_fingerprints",
        "source": "ATVHunter, LibID, LibScan",
        "scope": "basic-block opcode hashes",
    },
    {
        "feature": "class-neighbor summaries",
        "table": "class_neighbor_summaries",
        "source": "SAD",
        "scope": "bucketed in/out class dependency neighborhoods",
    },
    {
        "feature": "field-operation sequences",
        "table": "field_operation_sequences",
        "source": "SAD",
        "scope": "iget/iput/sget/sput opcode order",
    },
    {
        "feature": "literal/context features",
        "table": "literal_context_features",
        "source": "SAD, LibMD",
        "scope": "stable literal plus package/method context hashes",
    },
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate Phase 3 inert R8 multi-scale feature diagnostics.",
    )
    parser.add_argument("--reference-db", default=str(DEFAULT_REFERENCE_DB))
    parser.add_argument("--report-json", default=str(DEFAULT_REPORT_JSON))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--output-doc", default=str(DEFAULT_OUTPUT_DOC))
    return parser


def main() -> int:
    args = build_parser().parse_args()
    payload = build_payload(
        reference_db=Path(args.reference_db),
        report_json=Path(args.report_json),
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
                "features": len(payload["features"]),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def build_payload(*, reference_db: Path, report_json: Path) -> dict[str, Any]:
    report_payload = read_json(report_json)
    report_availability = (
        report_payload.get("match_summary", {}).get("inert_multiscale_features", {})
        if report_payload
        else {}
    )
    return {
        "schema_version": 1,
        "sources": {
            "reference_db": normalize_path(reference_db),
            "report_json": normalize_path(report_json),
        },
        "verdict": "r8-phase-3-inert-features-complete-scoring-unchanged",
        "features": [
            {
                **feature,
                **table_summary(reference_db, feature["table"]),
                "report_apk_availability": feature_availability(
                    report_availability,
                    "apk",
                    feature["table"],
                ),
                "report_reference_availability": feature_availability(
                    report_availability,
                    "reference",
                    feature["table"],
                ),
            }
            for feature in FEATURE_TABLES
        ],
        "policy": [
            "Phase 3 features are extracted and stored only for diagnostics and scoped experiments.",
            "Matcher scoring, selected versions, source-validation metrics, vulnerability classification, and SBOM component selection are unchanged.",
            "No new feature has a default matcher weight or promotion path unless a future scoped experiment passes clean controls.",
        ],
        "next_actions": [
            "Use the Phase 4 diagnostic result as the guardrail: the first global blend is rejected because it regresses controls.",
            "Keep features diagnostic-only unless a narrower opt-in hard-case experiment improves a target case and avoids control regressions.",
            "Promote scoring only as a scoped R8-aware reranker after fresh clean and partial source-validation controls pass.",
        ],
    }


def table_summary(reference_db: Path, table: str) -> dict[str, int | str]:
    if not reference_db.exists():
        return {
            "table_status": "missing-db",
            "rows": 0,
            "components_with_features": 0,
        }
    with sqlite3.connect(reference_db) as connection:
        if not table_exists(connection, table):
            return {
                "table_status": "missing-table",
                "rows": 0,
                "components_with_features": 0,
            }
        row = connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()
        component_row = connection.execute(
            f"SELECT COUNT(DISTINCT component_id) FROM {table}"
        ).fetchone()
    return {
        "table_status": "present",
        "rows": int(row[0]),
        "components_with_features": int(component_row[0]),
    }


def feature_availability(payload: object, section: str, table: str) -> dict[str, int]:
    if not isinstance(payload, dict):
        return {"distinct": 0, "total": 0, "components_with_features": 0}
    section_payload = payload.get(section, {})
    if not isinstance(section_payload, dict):
        return {"distinct": 0, "total": 0, "components_with_features": 0}
    row = section_payload.get(table, {})
    if not isinstance(row, dict):
        return {"distinct": 0, "total": 0, "components_with_features": 0}
    return {
        "distinct": int_value(row.get("distinct")),
        "total": int_value(row.get("total")),
        "components_with_features": int_value(row.get("components_with_features")),
    }


def build_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# R8 Multi-Scale Feature Diagnostics",
        "",
        f"Verdict: `{payload['verdict']}`.",
        "",
        "Phase 3 adds inert feature extraction only. These signals remain available for diagnostics and future scoped experiments, but they are not consumed by matcher scoring or SBOM component selection.",
        "",
        "## Feature Tables",
        "",
        "| Feature | Source | Reference table | Rows | Components | Report APK distinct/total | Report reference components |",
        "|---|---|---|---:|---:|---:|---:|",
    ]
    for feature in payload["features"]:
        apk_availability = feature["report_apk_availability"]
        reference_availability = feature["report_reference_availability"]
        lines.append(
            "| "
            f"{feature['feature']} | "
            f"{feature['source']} | "
            f"`{feature['table']}` ({feature['table_status']}) | "
            f"{feature['rows']} | "
            f"{feature['components_with_features']} | "
            f"{apk_availability['distinct']}/{apk_availability['total']} | "
            f"{reference_availability['components_with_features']} |"
        )

    lines.extend(
        [
            "",
            "## Guardrails",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in payload["policy"])
    lines.extend(["", "## Next Actions", ""])
    lines.extend(f"- {item}" for item in payload["next_actions"])
    return "\n".join(lines) + "\n"


def table_exists(connection: sqlite3.Connection, table: str) -> bool:
    row = connection.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
        (table,),
    ).fetchone()
    return row is not None


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def int_value(value: object) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    try:
        return int(str(value))
    except (TypeError, ValueError):
        return 0


def normalize_path(path: str | Path) -> str:
    return str(path).replace("\\", "/")


if __name__ == "__main__":
    raise SystemExit(main())
