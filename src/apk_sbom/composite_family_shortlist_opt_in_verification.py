from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Sequence

from apk_sbom.composite_family_shortlist_live_validation import (
    DEFAULT_OUTPUT_JSON as DEFAULT_LIVE_VALIDATION_JSON,
    DEFAULT_REFERENCE_DB,
)
from apk_sbom.matcher import MatchSummary, match_apk_to_reference_db, reportable_version_decisions


DEFAULT_OUTPUT_JSON = Path(
    "data/results/experiments/composite-family-shortlist-opt-in-matcher-experiment.json"
)
DEFAULT_OUTPUT_DOC = Path(
    "docs/evaluation/COMPOSITE_FAMILY_SHORTLIST_OPT_IN_MATCHER_EXPERIMENT.md"
)
DEFAULT_CACHE_DIR = Path(
    "data/results/experiments/composite-family-shortlist-opt-in-matcher-experiment-cases"
)
DEFAULT_SMOKE_CASE_IDS = ("generated-gson-2-8-6-clear", "aegis")
DEFAULT_BROAD_REAL_CASE_IDS = ("aegis", "antennapod", "termux", "vlc-android")
CACHE_SCHEMA_VERSION = 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run default-vs-opt-in matcher controls for the balanced "
            "composite family shortlist."
        )
    )
    parser.add_argument("--live-validation-json", default=str(DEFAULT_LIVE_VALIDATION_JSON))
    parser.add_argument("--reference-db", default=str(DEFAULT_REFERENCE_DB))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--output-doc", default=str(DEFAULT_OUTPUT_DOC))
    parser.add_argument("--cache-dir", default=str(DEFAULT_CACHE_DIR))
    parser.add_argument("--no-cache", action="store_true")
    parser.add_argument(
        "--case-set",
        default="smoke",
        choices=["smoke", "broad", "all"],
        help=(
            "Control slice to evaluate. 'broad' means all controlled-generated "
            "cases plus representative real APK cases."
        ),
    )
    parser.add_argument("--case-id", action="append", default=[])
    return parser


def main() -> int:
    args = build_parser().parse_args()
    payload = build_payload(
        live_validation_json=Path(args.live_validation_json),
        reference_db=Path(args.reference_db),
        case_set=args.case_set,
        explicit_case_ids=args.case_id,
        cache_dir=Path(args.cache_dir) if args.cache_dir else None,
        use_cache=not args.no_cache,
    )
    result = write_outputs(
        payload,
        output_json=Path(args.output_json),
        output_doc=Path(args.output_doc),
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


def build_payload(
    *,
    live_validation_json: Path = DEFAULT_LIVE_VALIDATION_JSON,
    reference_db: Path = DEFAULT_REFERENCE_DB,
    case_set: str = "smoke",
    explicit_case_ids: Sequence[str] = (),
    cache_dir: Path | None = DEFAULT_CACHE_DIR,
    use_cache: bool = True,
) -> dict[str, Any]:
    live_validation = read_json(live_validation_json)
    cases_by_id = {
        str(row.get("case_id")): row
        for row in live_validation.get("cases", [])
        if isinstance(row, dict)
    }
    case_ids = select_case_ids(live_validation, case_set, explicit_case_ids)
    case_rows = []
    total = len(case_ids)
    for index, case_id in enumerate(case_ids, start=1):
        if case_id not in cases_by_id:
            continue
        case_rows.append(
            evaluate_case_cached(
                cases_by_id[case_id],
                reference_db=reference_db,
                case_set=case_set,
                cache_dir=cache_dir,
                use_cache=use_cache,
                index=index,
                total=total,
            )
        )
    missing_case_ids = [case_id for case_id in case_ids if case_id not in cases_by_id]
    summary = summarize(live_validation, case_rows, missing_case_ids)
    gates = build_gates(summary)
    failed_gates = [gate for gate in gates if gate["status"] != "pass"]
    summary["failed_gates"] = len(failed_gates)
    return {
        "schema_version": 1,
        "verdict": (
            "composite-family-shortlist-opt-in-matcher-experiment-ready"
            if not failed_gates
            else "composite-family-shortlist-opt-in-matcher-experiment-blocked"
        ),
        "recommendation": recommendation(case_set, failed_gates),
        "scope": (
            "Implementation control gate only. It runs current matcher defaults and "
            "the explicit composite-family-shortlist opt-in flag on the selected "
            "case set from the clean live-validation inventory. It does not change "
            "default matcher behavior, SBOM output, vulnerability labels, or "
            "source-validation metrics."
        ),
        "sources": {
            "live_validation_json": normalize_path(live_validation_json),
            "reference_db": normalize_path(reference_db),
            "case_cache_dir": normalize_path(cache_dir) if cache_dir else None,
        },
        "case_set": case_set,
        "policy": [
            "The composite family shortlist remains disabled unless the explicit opt-in flag is passed.",
            "The opt-in filter must retain complete coordinate version bands.",
            "Reportable selected versions must stay unchanged in the selected control gate.",
            "A future default promotion still requires a fresh full-control run, not only this opt-in artifact.",
        ],
        "summary": summary,
        "gates": gates,
        "cases": case_rows,
        "missing_case_ids": missing_case_ids,
    }


def select_case_ids(
    live_validation: dict[str, Any],
    case_set: str,
    explicit_case_ids: Sequence[str],
) -> list[str]:
    if explicit_case_ids:
        return list(dict.fromkeys(str(case_id) for case_id in explicit_case_ids))
    cases = [
        row for row in live_validation.get("cases", [])
        if isinstance(row, dict) and row.get("status") == "evaluated"
    ]
    if case_set == "smoke":
        return list(DEFAULT_SMOKE_CASE_IDS)
    if case_set == "broad":
        controlled = [
            str(row["case_id"])
            for row in cases
            if row.get("dataset_layer") == "controlled-generated"
        ]
        return controlled + [
            case_id
            for case_id in DEFAULT_BROAD_REAL_CASE_IDS
            if any(str(row.get("case_id")) == case_id for row in cases)
        ]
    if case_set == "all":
        return [str(row["case_id"]) for row in cases]
    raise ValueError(f"unknown case set: {case_set}")


def evaluate_case(case: dict[str, Any], *, reference_db: Path) -> dict[str, Any]:
    apk_path = Path(str(case.get("apk_path") or ""))
    if not apk_path.exists():
        return {
            "case_id": case.get("case_id"),
            "dataset_layer": case.get("dataset_layer"),
            "apk_path": normalize_path(apk_path),
            "status": "missing-apk",
            "default_shortlist_status": "not-run",
            "opt_in_shortlist_status": "not-run",
            "opt_in_enabled": False,
            "reference_rows_before": 0,
            "reference_rows_retained": 0,
            "reference_rows_removed": 0,
            "coordinate_families_removed": 0,
            "baseline_reportable_components": 0,
            "opt_in_reportable_components": 0,
            "reportable_selected_version_changes": [],
            "reportable_selected_version_change_count": 0,
            "selected_version_change_count": 0,
        }
    baseline = run_match(apk_path, reference_db=reference_db, enable_shortlist=False)
    opt_in = run_match(apk_path, reference_db=reference_db, enable_shortlist=True)
    reportable_changes = changed_selected_versions(
        reportable_selected_versions(baseline),
        reportable_selected_versions(opt_in),
    )
    selected_changes = changed_selected_versions(
        selected_versions(baseline),
        selected_versions(opt_in),
    )
    shortlist = opt_in.composite_family_shortlist_summary
    return {
        "case_id": case.get("case_id"),
        "dataset_layer": case.get("dataset_layer"),
        "apk_path": normalize_path(apk_path),
        "status": "evaluated",
        "default_shortlist_status": baseline.composite_family_shortlist_summary.get(
            "scoring_status"
        ),
        "opt_in_shortlist_status": shortlist.get("scoring_status"),
        "opt_in_enabled": opt_in.composite_family_shortlist_enabled,
        "reference_rows_before": shortlist.get("reference_rows_before", 0),
        "reference_rows_retained": shortlist.get("reference_rows_retained", 0),
        "reference_rows_removed": shortlist.get("reference_rows_removed", 0),
        "coordinate_families_removed": shortlist.get("coordinate_families_removed", 0),
        "baseline_reportable_components": len(reportable_selected_versions(baseline)),
        "opt_in_reportable_components": len(reportable_selected_versions(opt_in)),
        "reportable_selected_version_changes": reportable_changes,
        "reportable_selected_version_change_count": len(reportable_changes),
        "selected_version_change_count": len(selected_changes),
    }


def evaluate_case_cached(
    case: dict[str, Any],
    *,
    reference_db: Path,
    case_set: str,
    cache_dir: Path | None,
    use_cache: bool,
    index: int,
    total: int,
) -> dict[str, Any]:
    signature = case_cache_signature(case, reference_db=reference_db)
    cache_path = case_cache_path(cache_dir, case) if cache_dir else None
    if use_cache and cache_path and cache_path.exists():
        cached = read_cached_case(cache_path, signature)
        if cached is not None:
            print(f"[{index}/{total}] cache hit {case['case_id']}", flush=True)
            return {**cached, "cache_status": "hit", "case_set": case_set}
    print(f"[{index}/{total}] validating {case['case_id']}", flush=True)
    row = evaluate_case(case, reference_db=reference_db)
    row = {
        **row,
        "case_set": case_set,
        "cache_status": "miss",
        "cache_signature": signature,
    }
    if use_cache and cache_path:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(json.dumps(row, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return row


def case_cache_signature(
    case: dict[str, Any],
    *,
    reference_db: Path,
) -> dict[str, Any]:
    return {
        "schema_version": CACHE_SCHEMA_VERSION,
        "case_id": case.get("case_id"),
        "apk_path": normalize_path(case.get("apk_path") or ""),
        "reference_db": normalize_path(reference_db),
        "matcher_path": "default-vs-composite-family-shortlist-opt-in",
    }


def case_cache_path(cache_dir: Path | None, case: dict[str, Any]) -> Path:
    if cache_dir is None:
        raise ValueError("cache_dir is required")
    raw = f"{case.get('dataset_layer')}-{case.get('case_id')}"
    slug = re.sub(r"[^A-Za-z0-9_.-]+", "-", raw).strip("-").lower()[:90]
    digest = hashlib.sha1(str(case.get("apk_path") or "").encode("utf-8")).hexdigest()[:10]
    return cache_dir / f"{slug}-{digest}.json"


def read_cached_case(path: Path, signature: dict[str, Any]) -> dict[str, Any] | None:
    try:
        cached = read_json(path)
    except (OSError, json.JSONDecodeError):
        return None
    if cached.get("cache_signature") != signature:
        return None
    if cached.get("status") == "missing-apk" and Path(str(cached.get("apk_path") or "")).exists():
        return None
    return cached


def run_match(
    apk_path: Path,
    *,
    reference_db: Path,
    enable_shortlist: bool,
) -> MatchSummary:
    return match_apk_to_reference_db(
        apk_path,
        db_path=reference_db,
        top=10,
        min_score=0.05,
        enable_composite_family_shortlist=enable_shortlist,
    )


def summarize(
    live_validation: dict[str, Any],
    cases: Sequence[dict[str, Any]],
    missing_case_ids: Sequence[str],
) -> dict[str, Any]:
    evaluated = [row for row in cases if row.get("status") == "evaluated"]
    return {
        "live_validation_verdict": live_validation.get("verdict"),
        "live_validation_failed_gates": live_validation.get("summary", {}).get(
            "failed_gates",
            1,
        ),
        "requested_control_cases": len(cases) + len(missing_case_ids),
        "control_cases_evaluated": len(evaluated),
        "controlled_cases_evaluated": sum(
            row.get("dataset_layer") == "controlled-generated" for row in evaluated
        ),
        "real_cases_evaluated": sum(row.get("dataset_layer") == "real-apk" for row in evaluated),
        "missing_control_cases": len(missing_case_ids)
        + sum(row.get("status") != "evaluated" for row in cases),
        "reference_rows_removed": sum(int(row["reference_rows_removed"]) for row in evaluated),
        "reportable_selected_version_changes": sum(
            int(row["reportable_selected_version_change_count"]) for row in evaluated
        ),
        "default_disabled_cases": sum(
            row["default_shortlist_status"] == "disabled" for row in evaluated
        ),
        "opt_in_enabled_cases": sum(
            row["opt_in_shortlist_status"] in {"enabled", "enabled-experiment"}
            and row["opt_in_enabled"]
            for row in evaluated
        ),
        "case_cache_hits": sum(row.get("cache_status") == "hit" for row in cases),
        "case_cache_misses": sum(row.get("cache_status") == "miss" for row in cases),
    }


def build_gates(summary: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        gate(
            "live-validation-clean",
            0
            if summary["live_validation_verdict"]
            == "composite-family-shortlist-live-validation-clean-opt-in-candidate"
            and int(summary["live_validation_failed_gates"]) == 0
            else 1,
            f"Live validation verdict: {summary['live_validation_verdict']}.",
        ),
        gate(
            "control-cases-present",
            summary["missing_control_cases"],
            f"{summary['control_cases_evaluated']}/{summary['requested_control_cases']} control cases evaluated.",
        ),
        gate(
            "default-path-keeps-shortlist-disabled",
            summary["control_cases_evaluated"] - summary["default_disabled_cases"],
            f"{summary['default_disabled_cases']} default cases kept the shortlist disabled.",
        ),
        gate(
            "opt-in-path-enables-shortlist",
            summary["control_cases_evaluated"] - summary["opt_in_enabled_cases"],
            f"{summary['opt_in_enabled_cases']} opt-in cases enabled the shortlist.",
        ),
        gate(
            "opt-in-removes-reference-rows",
            0 if summary["reference_rows_removed"] else 1,
            f"{summary['reference_rows_removed']} reference rows removed in control cases.",
        ),
        gate(
            "no-reportable-selected-version-changes",
            summary["reportable_selected_version_changes"],
            f"{summary['reportable_selected_version_changes']} reportable selected-version changes.",
        ),
    ]


def gate(gate_id: str, fail_count: int, evidence: str) -> dict[str, Any]:
    return {
        "gate": gate_id,
        "status": "pass" if fail_count == 0 else "fail",
        "fail_count": fail_count,
        "evidence": evidence,
    }


def recommendation(case_set: str, failed_gates: Sequence[dict[str, Any]]) -> str:
    if failed_gates:
        return "keep-live-validation-only-and-fix-opt-in-control-gates"
    if case_set == "smoke":
        return "keep-opt-in-flag-and-run-broader-controls-before-default-promotion"
    if case_set == "broad":
        return "keep-opt-in-flag-and-run-full-controls-before-default-promotion"
    return "evaluate-default-promotion-readiness-with-fresh-doc-sync"


def selected_versions(summary: MatchSummary) -> dict[str, str]:
    return {
        decision.coordinate: decision.selected_version
        for decision in summary.decisions
    }


def reportable_selected_versions(summary: MatchSummary) -> dict[str, str]:
    return {
        decision.coordinate: decision.selected_version
        for decision, _ in reportable_version_decisions(summary.decisions)
    }


def changed_selected_versions(
    baseline: dict[str, str],
    opt_in: dict[str, str],
) -> list[dict[str, Any]]:
    return [
        {
            "coordinate": coordinate,
            "baseline_selected_version": baseline.get(coordinate),
            "opt_in_selected_version": opt_in.get(coordinate),
        }
        for coordinate in sorted(set(baseline) | set(opt_in))
        if baseline.get(coordinate) != opt_in.get(coordinate)
    ]


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
        "recommendation": payload["recommendation"],
        **payload["summary"],
    }


def build_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Composite Family-Shortlist Opt-In Matcher Experiment",
        "",
        "Generated by `scripts/build_composite_family_shortlist_opt_in_verification.py`.",
        "",
        f"Verdict: `{payload['verdict']}`.",
        "",
        f"Recommendation: `{payload['recommendation']}`.",
        "",
        payload["scope"],
        "",
        "## Summary",
        "",
        f"- Case set: `{payload['case_set']}`",
        f"- Control cases evaluated: `{summary['control_cases_evaluated']}/{summary['requested_control_cases']}`",
        f"- Controlled / real cases: `{summary['controlled_cases_evaluated']}` / `{summary['real_cases_evaluated']}`",
        f"- Reference rows removed in control cases: `{summary['reference_rows_removed']}`",
        f"- Reportable selected-version changes: `{summary['reportable_selected_version_changes']}`",
        f"- Failed gates: `{summary['failed_gates']}`",
        f"- Case cache hits / misses: `{summary['case_cache_hits']}` / `{summary['case_cache_misses']}`",
        "",
        "## Guardrails",
        "",
    ]
    lines.extend(f"- {item}" for item in payload["policy"])
    lines.extend(
        [
            "",
            "## Gates",
            "",
            "| Gate | Status | Evidence |",
            "|---|---|---|",
        ]
    )
    for item in payload["gates"]:
        lines.append(
            f"| `{md(item['gate'])}` | `{md(item['status'])}` | {md(item['evidence'])} |"
        )
    lines.extend(
        [
            "",
            "## Control Cases",
            "",
            "| Layer | Case | Status | Ref rows removed | Default status | Opt-in status | Reportable changes |",
            "|---|---|---|---:|---|---|---:|",
        ]
    )
    for row in payload["cases"]:
        lines.append(
            "| "
            f"`{md(row['dataset_layer'])}` | "
            f"`{md(row['case_id'])}` | "
            f"`{md(row.get('status', 'unknown'))}` | "
            f"{row.get('reference_rows_removed', 0)} | "
            f"`{md(row.get('default_shortlist_status'))}` | "
            f"`{md(row.get('opt_in_shortlist_status'))}` | "
            f"{row.get('reportable_selected_version_change_count', 0)} |"
        )
    lines.extend(["", "## Conclusion", "", conclusion(payload), ""])
    return "\n".join(lines)


def conclusion(payload: dict[str, Any]) -> str:
    if payload["summary"]["failed_gates"]:
        return (
            "Keep the composite family shortlist in live-validation only until the "
            "opt-in control gate is fixed."
        )
    return (
        "The explicit opt-in matcher path is wired and control-clean while the default "
        "path keeps the shortlist disabled. This is not a default-promotion result; "
        "run a full fresh control pass before changing production defaults."
    )


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_path(path: Any) -> str:
    return str(path).replace("\\", "/")


def md(value: Any) -> str:
    return str(value or "").replace("|", "\\|").replace("\n", " ")


if __name__ == "__main__":
    raise SystemExit(main())
