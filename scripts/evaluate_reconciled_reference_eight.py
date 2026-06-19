from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import sqlite3
from typing import Any

from apk_sbom.matcher import MatchSummary, match_apk_to_reference_db


DEFAULT_SOURCE_DASHBOARD = Path(
    "data/results/evaluation/real-apk-source-validation-dashboard.json"
)
DEFAULT_BASELINE_DB = Path(
    "data/reference_db/reference_features_real_apk_priority_without_reconciled_eight.sqlite"
)
DEFAULT_EXPERIMENT_DB = Path(
    "data/reference_db/reference_features_real_apk_priority_versions.sqlite"
)
DEFAULT_OUTPUT_JSON = Path(
    "data/results/experiments/reconciled-eight-reference-impact/summary.json"
)
DEFAULT_OUTPUT_DOC = Path(
    "docs/evaluation/RECONCILED_EIGHT_REFERENCE_IMPACT.md"
)

TARGETS = (
    ("gotify", "io.coil-kt:coil-base", "2.7.0"),
    ("afwall-plus", "org.jetbrains:annotations", "13.0"),
    ("easy-xkcd", "org.jetbrains:annotations", "16.0.1"),
    ("daily-dozen", "org.jetbrains:annotations", "20.1.0"),
    ("fdroid", "org.jetbrains:annotations", "23.0.0"),
    ("fairemail", "org.jetbrains:annotations", "24.0.1"),
    ("imapnotes3", "org.jetbrains:annotations", "26.0.2-1"),
    ("k9", "org.jetbrains:annotations", "26.1.0"),
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Evaluate only the eight reconciled reference rows on one "
            "source-observed representative APK each."
        )
    )
    parser.add_argument("--source-dashboard", default=str(DEFAULT_SOURCE_DASHBOARD))
    parser.add_argument("--baseline-db", default=str(DEFAULT_BASELINE_DB))
    parser.add_argument("--experiment-db", default=str(DEFAULT_EXPERIMENT_DB))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--output-doc", default=str(DEFAULT_OUTPUT_DOC))
    parser.add_argument("--min-score", type=float, default=0.05)
    parser.add_argument("--case", action="append")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    dashboard = read_json(Path(args.source_dashboard))
    cases_by_id = {
        str(case["case_id"]): case for case in dashboard.get("cases", [])
    }
    selected_ids = set(args.case or ())
    targets = [
        target for target in TARGETS if not selected_ids or target[0] in selected_ids
    ]
    if selected_ids:
        missing = selected_ids - {target[0] for target in targets}
        if missing:
            raise SystemExit(
                "unknown selected case id(s): " + ", ".join(sorted(missing))
            )

    baseline_db = Path(args.baseline_db)
    experiment_db = Path(args.experiment_db)
    rows = []
    for case_id, coordinate, expected_version in targets:
        case = cases_by_id.get(case_id)
        if not case:
            raise SystemExit(f"dashboard case not found: {case_id}")
        apk_path = apk_path_for_case(case)
        print(f"scoring {case_id}: {coordinate}@{expected_version}", flush=True)
        baseline = score_if_coordinate_present(
            apk_path,
            db_path=baseline_db,
            coordinate=coordinate,
            min_score=args.min_score,
        )
        experiment = match_apk_to_reference_db(
            apk_path,
            db_path=experiment_db,
            coordinate=coordinate,
            top=None,
            min_score=args.min_score,
            enable_composite_family_shortlist=False,
        )
        rows.append(
            build_row(
                case=case,
                apk_path=apk_path,
                coordinate=coordinate,
                expected_version=expected_version,
                baseline=baseline,
                experiment=experiment,
            )
        )

    payload = build_payload(
        rows,
        baseline_db=baseline_db,
        experiment_db=experiment_db,
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
                "output_json": normalize_path(output_json),
                "output_doc": normalize_path(output_doc),
                "rows": len(rows),
                "exact_selected": payload["summary"]["exact_selected"],
                "newly_selectable_rows": payload["summary"][
                    "newly_selectable_rows"
                ],
                "verdict": payload["verdict"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def score_if_coordinate_present(
    apk_path: Path,
    *,
    db_path: Path,
    coordinate: str,
    min_score: float,
) -> MatchSummary | None:
    with sqlite3.connect(db_path) as connection:
        present = connection.execute(
            "SELECT 1 FROM components WHERE coordinate = ? LIMIT 1",
            (coordinate,),
        ).fetchone()
    if not present:
        return None
    return match_apk_to_reference_db(
        apk_path,
        db_path=db_path,
        coordinate=coordinate,
        top=None,
        min_score=min_score,
        enable_composite_family_shortlist=False,
    )


def build_row(
    *,
    case: dict[str, Any],
    apk_path: Path,
    coordinate: str,
    expected_version: str,
    baseline: MatchSummary | None,
    experiment: MatchSummary,
) -> dict[str, Any]:
    baseline_decision = decision_dict(baseline)
    experiment_decision = decision_dict(experiment)
    target_candidate = next(
        (
            candidate
            for candidate in experiment.candidates
            if candidate.coordinate == coordinate
            and candidate.version == expected_version
        ),
        None,
    )
    baseline_selected = (
        str(baseline_decision.get("selected_version"))
        if baseline_decision
        else None
    )
    experiment_selected = (
        str(experiment_decision.get("selected_version"))
        if experiment_decision
        else None
    )
    exact_selected = experiment_selected == expected_version
    newly_selectable = baseline_selected is None and experiment_selected is not None
    changed_selection = baseline_selected != experiment_selected
    identity_status = (
        str(experiment_decision.get("identity_status"))
        if experiment_decision
        else None
    )
    if exact_selected:
        classification = "exact-selected"
    elif identity_status in {"confirmed", "likely"}:
        classification = "identity-supported-version-ambiguous"
    else:
        classification = "weak-or-uncertain"
    return {
        "case_id": str(case["case_id"]),
        "case_name": str(case.get("name") or case["case_id"]),
        "case_role": str(case.get("role") or ""),
        "apk_path": normalize_path(apk_path),
        "coordinate": coordinate,
        "expected_version": expected_version,
        "baseline_selected_version": baseline_selected,
        "experiment_selected_version": experiment_selected,
        "exact_selected": exact_selected,
        "newly_selectable": newly_selectable,
        "changed_selection": changed_selection,
        "classification": classification,
        "target_candidate_rank": candidate_rank(
            experiment,
            coordinate=coordinate,
            version=expected_version,
        ),
        "target_candidate_score": (
            round(float(target_candidate.score), 6) if target_candidate else None
        ),
        "target_candidate_evidence": (
            asdict(target_candidate.evidence) if target_candidate else None
        ),
        "baseline_decision": baseline_decision,
        "experiment_decision": experiment_decision,
        "experiment_reference_versions": sorted(
            {
                candidate.version
                for candidate in experiment.candidates
                if candidate.coordinate == coordinate
            }
        ),
    }


def build_payload(
    rows: list[dict[str, Any]],
    *,
    baseline_db: Path,
    experiment_db: Path,
) -> dict[str, Any]:
    summary = {
        "rows": len(rows),
        "exact_selected": sum(1 for row in rows if row["exact_selected"]),
        "newly_selectable_rows": sum(
            1 for row in rows if row["newly_selectable"]
        ),
        "changed_selections": sum(1 for row in rows if row["changed_selection"]),
        "not_exact_selected": sum(1 for row in rows if not row["exact_selected"]),
        "identity_supported_version_ambiguous": sum(
            1
            for row in rows
            if row["classification"] == "identity-supported-version-ambiguous"
        ),
        "weak_or_uncertain": sum(
            1 for row in rows if row["classification"] == "weak-or-uncertain"
        ),
    }
    if summary["exact_selected"] == len(rows):
        verdict = "reconciled-eight-all-exact-on-representative-cases"
    elif summary["exact_selected"]:
        verdict = "reconciled-eight-partial-version-impact"
    else:
        verdict = "reconciled-eight-no-exact-selection-impact"
    return {
        "schema_version": 1,
        "scope": (
            "Coordinate-only evaluation of the eight reconciled reference rows. "
            "One source-observed representative APK is used per row. This is not "
            "a full reference-DB or whole-SBOM rerun."
        ),
        "baseline_db": normalize_path(baseline_db),
        "experiment_db": normalize_path(experiment_db),
        "verdict": verdict,
        "summary": summary,
        "rows": rows,
        "policy": [
            "Treat an exact selected version as scoped evidence that the added row is matchable in its representative APK.",
            "Do not extrapolate this eight-row check to full dependency recall or global matcher accuracy.",
            "Keep the shared calibrated DB unchanged; both databases in this comparison are evaluation-only.",
        ],
    }


def build_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Reconciled Eight Reference Impact",
        "",
        "Generated by `scripts/evaluate_reconciled_reference_eight.py`.",
        "",
        f"Verdict: `{payload['verdict']}`.",
        "",
        payload["scope"],
        "",
        "## Summary",
        "",
        f"- Rows evaluated: `{summary['rows']}`",
        f"- Exact expected version selected: `{summary['exact_selected']}`",
        f"- Newly selectable representative rows: `{summary['newly_selectable_rows']}`",
        "- Identity supported but exact version ambiguous: "
        f"`{summary['identity_supported_version_ambiguous']}`",
        f"- Weak or uncertain identity rows: `{summary['weak_or_uncertain']}`",
        f"- Selection changes: `{summary['changed_selections']}`",
        f"- Expected version not selected: `{summary['not_exact_selected']}`",
        "",
        "## Results",
        "",
        "| Case | Added reference | Baseline | With row | Rank | Score | Result |",
        "|---|---|---:|---:|---:|---:|---|",
    ]
    for row in payload["rows"]:
        baseline = row["baseline_selected_version"] or "not available"
        experiment = row["experiment_selected_version"] or "not selected"
        rank = row["target_candidate_rank"] or "-"
        score = row["target_candidate_score"]
        lines.append(
            "| "
            f"{row['case_name']} | "
            f"`{row['coordinate']}@{row['expected_version']}` | "
            f"`{baseline}` | "
            f"`{experiment}` | "
            f"{rank} | "
            f"{score if score is not None else '-'} | "
            f"`{row['classification']}` |"
        )
    lines.extend(["", "## Policy", ""])
    lines.extend(f"- {item}" for item in payload["policy"])
    lines.append("")
    return "\n".join(lines)


def decision_dict(summary: MatchSummary | None) -> dict[str, Any] | None:
    if summary is None or not summary.decisions:
        return None
    return asdict(summary.decisions[0])


def candidate_rank(
    summary: MatchSummary,
    *,
    coordinate: str,
    version: str,
) -> int | None:
    relevant = [
        candidate
        for candidate in summary.candidates
        if candidate.coordinate == coordinate
    ]
    for index, candidate in enumerate(relevant, start=1):
        if candidate.version == version:
            return index
    return None


def apk_path_for_case(case: dict[str, Any]) -> Path:
    report_path = Path(str((case.get("paths") or {}).get("report") or ""))
    report = read_json(report_path)
    apk_path = Path(str(((report.get("apk") or {}).get("apk_path")) or ""))
    if not apk_path.exists():
        raise FileNotFoundError(f"APK not found for {case['case_id']}: {apk_path}")
    return apk_path


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_path(path: str | Path) -> str:
    return Path(path).as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
