from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_MANIFEST_JSON = Path("configs/guarded_reference_db_promotion_experiments.json")
DEFAULT_OUTPUT_JSON = Path(
    "data/results/experiments/guarded-reference-db-promotion-workflow.json"
)
DEFAULT_OUTPUT_DOC = Path(
    "docs/evaluation/GUARDED_REFERENCE_DB_PROMOTION_WORKFLOW.md"
)
VALID_SCOPES = {"singleton", "tested-bundle"}
CLASSIFICATIONS = ("safe", "app-specific", "regression-risk", "no-change")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Classify isolated reference-DB experiments against current controls "
            "before any shared calibrated DB promotion."
        )
    )
    parser.add_argument("--manifest-json", default=str(DEFAULT_MANIFEST_JSON))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--output-doc", default=str(DEFAULT_OUTPUT_DOC))
    return parser


def main() -> int:
    args = build_parser().parse_args()
    payload = build_payload(manifest_json=Path(args.manifest_json))
    result = write_outputs(
        payload,
        output_json=Path(args.output_json),
        output_doc=Path(args.output_doc),
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


def build_payload(*, manifest_json: Path = DEFAULT_MANIFEST_JSON) -> dict[str, Any]:
    manifest = read_json(manifest_json)
    experiment_rows = []
    for record in manifest.get("experiments", []):
        validate_record(record)
        comparison_path = resolve_input_path(manifest_json, record["comparison_json"])
        experiment_rows.append(
            classify_experiment(record, read_json(comparison_path), comparison_path)
        )
    experiment_rows.sort(key=lambda row: row["id"])
    gates = build_gates(experiment_rows)
    failed_gates = [gate for gate in gates if gate["status"] != "pass"]
    classification_counts = {
        classification: sum(
            1
            for experiment in experiment_rows
            if experiment["classification"] == classification
        )
        for classification in CLASSIFICATIONS
    }
    return {
        "schema_version": 1,
        "verdict": (
            "guarded-reference-db-promotion-workflow-ready"
            if not failed_gates
            else "guarded-reference-db-promotion-workflow-invalid"
        ),
        "scope": (
            "Repeatable policy layer for isolated source-version reference DB "
            "experiments. It consumes fresh current-control comparison JSON and "
            "records whether each singleton or exact tested bundle is safe, "
            "app-specific, regression-risk, or no-change before any shared DB edit."
        ),
        "policy": [
            "Only singleton experiments labeled safe support a per-version shared-DB promotion claim.",
            "A safe tested bundle is clean evidence for that exact bundle only; split it into singleton experiments before making per-version claims.",
            "App-specific experiments may remain useful evidence, but they must not be promoted globally while control regressions remain.",
            "Regression-risk experiments do not demonstrate a target benefit and must not be promoted globally.",
            "No-change experiments do not justify shared-DB promotion.",
        ],
        "sources": {"manifest_json": normalize_path(manifest_json)},
        "summary": {
            "experiments_classified": len(experiment_rows),
            "candidate_version_slots": sum(
                len(experiment["candidate_versions"]) for experiment in experiment_rows
            ),
            "safe_singletons": sum(
                1
                for experiment in experiment_rows
                if experiment["scope"] == "singleton"
                and experiment["classification"] == "safe"
            ),
            "safe_tested_bundles": sum(
                1
                for experiment in experiment_rows
                if experiment["scope"] == "tested-bundle"
                and experiment["classification"] == "safe"
            ),
            "classification_counts": classification_counts,
            "failed_gates": len(failed_gates),
        },
        "safe_singleton_candidates": sorted(
            candidate
            for experiment in experiment_rows
            if experiment["scope"] == "singleton"
            and experiment["classification"] == "safe"
            for candidate in experiment["candidate_versions"]
        ),
        "experiments": experiment_rows,
        "gates": gates,
    }


def classify_experiment(
    record: dict[str, Any],
    comparison: dict[str, Any],
    comparison_path: Path,
) -> dict[str, Any]:
    target_cases = sorted(set(str(case) for case in record["target_cases"]))
    improved_cases = sorted(set(str(case) for case in comparison.get("improved_cases", [])))
    regressed_cases = sorted(set(str(case) for case in comparison.get("regressed_cases", [])))
    target_improved_cases = sorted(set(target_cases) & set(improved_cases))
    unrelated_improved_cases = sorted(set(improved_cases) - set(target_cases))
    classification = classify_outcome(
        target_improved_cases=target_improved_cases,
        regressed_cases=regressed_cases,
    )
    scope = str(record["scope"])
    candidate_versions = sorted(set(str(value) for value in record["candidate_versions"]))
    claim_scope = "singleton-version" if scope == "singleton" else "exact-tested-bundle-only"
    return {
        "id": str(record["id"]),
        "title": str(record.get("title") or record["id"]),
        "scope": scope,
        "claim_scope": claim_scope,
        "comparison_json": normalize_path(comparison_path),
        "case_count": int(comparison.get("case_count", 0)),
        "target_cases": target_cases,
        "candidate_versions": candidate_versions,
        "improved_cases": improved_cases,
        "target_improved_cases": target_improved_cases,
        "unrelated_improved_cases": unrelated_improved_cases,
        "regressed_cases": regressed_cases,
        "classification": classification,
        "promotion_decision": promotion_decision(classification, scope),
        "candidate_labels": [
            {
                "candidate_version": candidate,
                "classification": classification,
                "claim_scope": claim_scope,
            }
            for candidate in candidate_versions
        ],
    }


def classify_outcome(
    *,
    target_improved_cases: list[str],
    regressed_cases: list[str],
) -> str:
    if target_improved_cases and not regressed_cases:
        return "safe"
    if target_improved_cases and regressed_cases:
        return "app-specific"
    if regressed_cases:
        return "regression-risk"
    return "no-change"


def promotion_decision(classification: str, scope: str) -> str:
    if classification == "safe" and scope == "singleton":
        return "Eligible for shared-DB promotion after canonical regeneration."
    if classification == "safe":
        return "Exact bundle is clean; split into singleton runs before per-version promotion claims."
    if classification == "app-specific":
        return "Keep isolated as app-specific evidence; do not promote globally."
    if classification == "regression-risk":
        return "Reject global promotion; controls regress without a demonstrated target benefit."
    return "Do not promote; no target benefit was demonstrated."


def build_gates(experiments: list[dict[str, Any]]) -> list[dict[str, Any]]:
    safe_with_regressions = [
        row for row in experiments if row["classification"] == "safe" and row["regressed_cases"]
    ]
    app_specific_without_regressions = [
        row
        for row in experiments
        if row["classification"] == "app-specific" and not row["regressed_cases"]
    ]
    malformed_bundle_claims = [
        row
        for row in experiments
        if row["scope"] == "tested-bundle" and row["claim_scope"] != "exact-tested-bundle-only"
    ]
    return [
        gate(
            "experiments-present",
            fail_count=0 if experiments else 1,
            evidence=f"{len(experiments)} experiment comparisons classified.",
        ),
        gate(
            "classifications-complete",
            fail_count=sum(
                1 for row in experiments if row["classification"] not in CLASSIFICATIONS
            ),
            evidence="Every experiment has a stable promotion-policy classification.",
        ),
        gate(
            "safe-outcomes-have-no-regressions",
            fail_count=len(safe_with_regressions),
            evidence=f"{len(safe_with_regressions)} safe rows contain control regressions.",
        ),
        gate(
            "app-specific-outcomes-preserve-regressions",
            fail_count=len(app_specific_without_regressions),
            evidence=(
                f"{len(app_specific_without_regressions)} app-specific rows lack "
                "recorded control regressions."
            ),
        ),
        gate(
            "tested-bundles-remain-bundle-scoped",
            fail_count=len(malformed_bundle_claims),
            evidence=(
                f"{len(malformed_bundle_claims)} tested bundles overclaim "
                "per-version evidence."
            ),
        ),
    ]


def validate_record(record: Any) -> None:
    if not isinstance(record, dict):
        raise ValueError("each manifest experiment must be an object")
    missing = [
        key
        for key in ("id", "scope", "comparison_json", "target_cases", "candidate_versions")
        if not record.get(key)
    ]
    if missing:
        raise ValueError(f"manifest experiment is missing required values: {', '.join(missing)}")
    if record["scope"] not in VALID_SCOPES:
        raise ValueError(f"invalid experiment scope: {record['scope']!r}")
    if not isinstance(record["target_cases"], list):
        raise ValueError("target_cases must be a list")
    if not isinstance(record["candidate_versions"], list):
        raise ValueError("candidate_versions must be a list")


def gate(gate_id: str, *, fail_count: int, evidence: str) -> dict[str, Any]:
    return {
        "gate": gate_id,
        "status": "pass" if fail_count == 0 else "fail",
        "fail_count": fail_count,
        "evidence": evidence,
    }


def write_outputs(
    payload: dict[str, Any],
    *,
    output_json: Path,
    output_doc: Path,
) -> dict[str, Any]:
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    output_doc.parent.mkdir(parents=True, exist_ok=True)
    output_doc.write_text(build_markdown(payload), encoding="utf-8")
    return {
        "doc": normalize_path(output_doc),
        "json": normalize_path(output_json),
        "verdict": payload["verdict"],
        **payload["summary"],
    }


def build_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Guarded Reference-DB Promotion Workflow",
        "",
        "Generated by `scripts/build_guarded_reference_db_promotion_workflow.py`.",
        "",
        f"Verdict: `{payload['verdict']}`.",
        "",
        payload["scope"],
        "",
        "## Policy",
        "",
    ]
    lines.extend(f"- {line}" for line in payload["policy"])
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- Experiments classified: `{summary['experiments_classified']}`",
            f"- Candidate-version slots recorded: `{summary['candidate_version_slots']}`",
            f"- Safe singleton experiments: `{summary['safe_singletons']}`",
            f"- Safe exact tested bundles: `{summary['safe_tested_bundles']}`",
            f"- App-specific experiments: `{summary['classification_counts']['app-specific']}`",
            f"- Regression-risk experiments: `{summary['classification_counts']['regression-risk']}`",
            f"- No-change experiments: `{summary['classification_counts']['no-change']}`",
            f"- Failed gates: `{summary['failed_gates']}`",
            "",
            "Safe singleton candidates eligible for guarded shared-DB promotion:",
            "",
        ]
    )
    if payload["safe_singleton_candidates"]:
        lines.extend(f"- `{candidate}`" for candidate in payload["safe_singleton_candidates"])
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "## Experiment Decisions",
            "",
            "| Experiment | Scope | Candidates | Target improvements | Regressed controls | Label | Decision |",
            "|---|---|---:|---|---|---|---|",
        ]
    )
    for row in payload["experiments"]:
        lines.append(
            "| "
            f"`{md(row['id'])}` | "
            f"`{md(row['scope'])}` | "
            f"{len(row['candidate_versions'])} | "
            f"{md(', '.join(row['target_improved_cases']) or 'none')} | "
            f"{md(', '.join(row['regressed_cases']) or 'none')} | "
            f"`{md(row['classification'])}` | "
            f"{md(row['promotion_decision'])} |"
        )
    lines.extend(
        [
            "",
            "## Candidate Labels",
            "",
            "| Experiment | Candidate version | Label | Claim scope |",
            "|---|---|---|---|",
        ]
    )
    for row in payload["experiments"]:
        for candidate in row["candidate_labels"]:
            lines.append(
                "| "
                f"`{md(row['id'])}` | "
                f"`{md(candidate['candidate_version'])}` | "
                f"`{md(candidate['classification'])}` | "
                f"`{md(candidate['claim_scope'])}` |"
            )
    lines.extend(["", "## Gates", "", "| Gate | Status | Evidence |", "|---|---|---|"])
    for item in payload["gates"]:
        lines.append(
            "| "
            f"`{md(item['gate'])}` | "
            f"`{md(item['status'])}` | "
            f"{md(item['evidence'])} |"
        )
    lines.extend(
        [
            "",
            "## Next Use",
            "",
            "For the next queued source version, build an isolated experiment DB, "
            "run the current-control matrix, write a comparison JSON with "
            "`scripts/compare_experiment_summaries.py`, add one manifest row, and "
            "regenerate this artifact before changing the shared calibrated DB.",
            "",
        ]
    )
    return "\n".join(lines)


def resolve_input_path(manifest_json: Path, value: str) -> Path:
    path = Path(value)
    if path.is_absolute() or path.exists():
        return path
    return manifest_json.parent / path


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_path(path: Any) -> str:
    return str(path).replace("\\", "/")


def md(value: Any) -> str:
    return str(value or "").replace("|", "\\|").replace("\n", " ")


if __name__ == "__main__":
    raise SystemExit(main())
