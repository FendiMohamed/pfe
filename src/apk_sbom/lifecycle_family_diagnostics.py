from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
from typing import Any

from apk_sbom.lifecycle_family_experiment import classify_lifecycle_public_overlap
from apk_sbom.version_band_trigger_diagnostics import load_reports, normalize_path


DEFAULT_INPUT_JSON = Path("data/results/experiments/low-risk-version-band-diagnostics.json")
DEFAULT_OUTPUT_JSON = Path("data/results/experiments/lifecycle-family-separation-diagnostics.json")
DEFAULT_OUTPUT_DOC = Path("docs/evaluation/LIFECYCLE_FAMILY_SEPARATION_DIAGNOSTICS.md")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Evaluate Lifecycle public-vs-Android family separation without changing matcher output.",
    )
    parser.add_argument("--input-json", default=str(DEFAULT_INPUT_JSON))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--output-doc", default=str(DEFAULT_OUTPUT_DOC))
    return parser


def main() -> int:
    args = build_parser().parse_args()
    payload = build_payload(Path(args.input_json))
    result = write_outputs(
        payload,
        output_json=Path(args.output_json),
        output_doc=Path(args.output_doc),
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


def build_payload(input_json: Path) -> dict[str, Any]:
    source = json.loads(input_json.read_text(encoding="utf-8"))
    reports = load_reports()
    full = source["full_experiment"]
    introduced = evaluate_rows(full["introduced_mismatches"], reports=reports)
    resolved = evaluate_rows(full["resolved_target_mismatches"], reports=reports)
    counts = Counter(row["lifecycle_decision"]["classification"] for row in introduced)
    summary = {
        "introduced_lifecycle_rows": len(introduced),
        "public_claim_downgrade_candidates": count_downgrades(introduced),
        "resolved_target_lifecycle_rows": len(resolved),
        "resolved_target_rows_blocked": count_downgrades(resolved),
        "classification_counts": dict(sorted(counts.items())),
    }
    return {
        "schema_version": 1,
        "verdict": verdict(summary),
        "scope": (
            "Experiment only. This artifact separates Lifecycle public-coordinate drift from "
            "Android-target family overlap without changing matcher scoring, selected versions, "
            "SBOM components, vulnerability labels, or the shared DB."
        ),
        "policy": [
            "Downgrade only the public-coordinate claim; never force an Android-target replacement version.",
            "Accept source-version-backed target evidence or at least two same-version Lifecycle family anchors.",
            "Keep patch-level Android-target near-ties ambiguous.",
            "Keep insufficient family evidence visible as mismatch or ambiguity.",
            "Require a fresh report/control matrix before any production integration.",
        ],
        "source": normalize_path(input_json),
        "summary": summary,
        "introduced_rows": introduced,
        "resolved_target_rows": resolved,
    }


def evaluate_rows(rows: list[dict[str, Any]], *, reports: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    evaluated = []
    for row in rows:
        if not str(row["coordinate"]).startswith("androidx.lifecycle:"):
            continue
        report = reports[str(row["case_id"])]
        decisions = report.get("match_summary", {}).get("decisions", [])
        decision = classify_lifecycle_public_overlap(
            coordinate=str(row["coordinate"]),
            selected_version=str(row["selected_version"]),
            source_versions=[str(row["source_versions"])],
            sibling_decisions=decisions,
        )
        evaluated.append({**row, "lifecycle_decision": decision.to_dict()})
    return evaluated


def count_downgrades(rows: list[dict[str, Any]]) -> int:
    return sum(1 for row in rows if row["lifecycle_decision"]["downgrade_public_claim"])


def verdict(summary: dict[str, Any]) -> str:
    if summary["resolved_target_rows_blocked"]:
        return "reject-lifecycle-family-trigger-blocks-target-benefits"
    if summary["public_claim_downgrade_candidates"]:
        return "lifecycle-family-separation-promising-not-promoted"
    return "no-safe-lifecycle-family-applications"


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
        "# Lifecycle Family Separation Diagnostics",
        "",
        "Generated by `apk-sbom lifecycle-family-experiment`.",
        "",
        f"Verdict: `{payload['verdict']}`.",
        "",
        payload["scope"],
        "",
        "## Summary",
        "",
        f"- Introduced Lifecycle mismatch rows inspected: `{summary['introduced_lifecycle_rows']}`",
        f"- Public claims eligible for diagnostic downgrade: `{summary['public_claim_downgrade_candidates']}`",
        f"- Resolved target Lifecycle rows inspected: `{summary['resolved_target_lifecycle_rows']}`",
        f"- Resolved target rows blocked: `{summary['resolved_target_rows_blocked']}`",
        "",
        "## Introduced Lifecycle Rows",
        "",
        "| Case | Public coordinate | Selected | Source | Android target evidence | Classification | Downgrade public claim |",
        "|---|---|---|---|---|---|---|",
    ]
    for row in payload["introduced_rows"]:
        decision = row["lifecycle_decision"]
        target = (
            f"{decision['target_coordinate']}@{decision['target_version']}:{decision['target_score']}"
            if decision["target_coordinate"]
            else "none"
        )
        lines.append(
            "| "
            f"{md(row['case_id'])} | "
            f"`{row['coordinate']}` | "
            f"{md(row['selected_version'])} | "
            f"{md(row['source_versions'])} | "
            f"{md(target)} | "
            f"`{decision['classification']}` | "
            f"`{decision['downgrade_public_claim']}` |"
        )

    lines.extend(["", "## Policy", ""])
    lines.extend(f"- {item}" for item in payload["policy"])
    lines.extend(
        [
            "",
            "## Conclusion",
            "",
            "Lifecycle evidence must remain family-aware. This diagnostic identifies public-coordinate claims that can be downgraded because Android-target family evidence is stronger, while preserving patch-level near-ties and weak family rows as visible ambiguity. It does not justify forcing replacement versions or changing default matcher behavior.",
            "",
        ]
    )
    return "\n".join(lines)


def md(value: Any) -> str:
    return str(value or "").replace("|", "\\|").replace("\n", " ")


if __name__ == "__main__":
    raise SystemExit(main())
