from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_VERSION_TIES_JSON = Path("data/results/experiments/version-band-tie-evidence.json")
DEFAULT_OPCODE_SUMMARY_JSON = Path(
    "data/results/experiments/opcode-ngram-weight/opcode-ngram-weight-summary.json"
)
DEFAULT_OUTPUT_JSON = Path("data/results/experiments/version-tie-reranker-diagnostics.json")
DEFAULT_OUTPUT_DOC = Path("docs/evaluation/VERSION_TIE_RERANKER_DIAGNOSTICS.md")

SCORE_SIGNALS = [
    "class_score",
    "method_score",
    "dependency_score",
    "literal_score",
    "api_reference_score",
    "unique_version_score",
]
SIGNAL_THRESHOLD = 0.005


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate diagnostic-only reranker evidence for version-band ties.",
    )
    parser.add_argument("--version-ties-json", default=str(DEFAULT_VERSION_TIES_JSON))
    parser.add_argument("--opcode-summary-json", default=str(DEFAULT_OPCODE_SUMMARY_JSON))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--output-doc", default=str(DEFAULT_OUTPUT_DOC))
    return parser


def main() -> int:
    args = build_parser().parse_args()
    ties_path = Path(args.version_ties_json)
    opcode_path = Path(args.opcode_summary_json)
    payload = build_payload(
        read_json(ties_path),
        read_json(opcode_path),
        ties_path=ties_path,
        opcode_path=opcode_path,
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
                "rows": len(payload["rows"]),
                "verdict_counts": payload["verdict_counts"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def build_payload(
    version_ties: dict[str, Any],
    opcode_summary: dict[str, Any],
    *,
    ties_path: Path,
    opcode_path: Path,
) -> dict[str, Any]:
    rows = [diagnose_row(row) for row in version_ties.get("rows", [])]
    verdict_counts: dict[str, int] = {}
    for row in rows:
        verdict_counts[row["diagnostic_verdict"]] = verdict_counts.get(row["diagnostic_verdict"], 0) + 1
    return {
        "schema_version": 1,
        "sources": {
            "version_ties": normalize_path(ties_path),
            "opcode_summary": normalize_path(opcode_path),
        },
        "scope": "Diagnostic only; this artifact does not change matcher output or promote versions.",
        "signal_threshold": SIGNAL_THRESHOLD,
        "opcode_ngram_global_experiment": summarize_opcode_experiment(opcode_summary),
        "verdict_counts": verdict_counts,
        "rows": rows,
    }


def diagnose_row(row: dict[str, Any]) -> dict[str, Any]:
    candidates = row.get("top_candidates") or []
    selected = find_candidate(candidates, row.get("selected_version")) or (candidates[0] if candidates else {})
    source = find_source_candidate(candidates, row.get("source_versions", []))
    signal_deltas = build_signal_deltas(source, selected) if source else {}
    source_signals = [
        signal
        for signal, delta in signal_deltas.items()
        if signal != "matched_unique_features" and delta >= SIGNAL_THRESHOLD
    ]
    selected_signals = [
        signal
        for signal, delta in signal_deltas.items()
        if signal != "matched_unique_features" and delta <= -SIGNAL_THRESHOLD
    ]
    matched_unique_delta = signal_deltas.get("matched_unique_features")
    if matched_unique_delta is not None and matched_unique_delta > 0:
        source_signals.append("matched_unique_features")
    elif matched_unique_delta is not None and matched_unique_delta < 0:
        selected_signals.append("matched_unique_features")

    verdict = classify_verdict(row, source, source_signals, selected_signals)
    return {
        "case_id": row.get("case_id"),
        "coordinate": row.get("coordinate"),
        "classification": row.get("classification"),
        "selected_version": row.get("selected_version"),
        "source_versions": row.get("source_versions", []),
        "gap_to_next": row.get("gap_to_next"),
        "status": row.get("status"),
        "version_status": row.get("version_status"),
        "source_candidate_present": bool(source),
        "selected_candidate": compact_candidate(selected),
        "source_candidate": compact_candidate(source) if source else None,
        "signal_deltas_source_minus_selected": signal_deltas,
        "signals_supporting_source": source_signals,
        "signals_supporting_selected": selected_signals,
        "diagnostic_verdict": verdict,
        "safe_action": safe_action(verdict),
    }


def classify_verdict(
    row: dict[str, Any],
    source: dict[str, Any] | None,
    source_signals: list[str],
    selected_signals: list[str],
) -> str:
    classification = row.get("classification")
    next_action = str(row.get("next_action") or "")
    if "do not promote globally" in next_action:
        return "known-regression-risk-do-not-promote"
    if classification == "artifact-family-or-source-coordinate-nuance":
        return "artifact-family-review"
    if classification == "missing-reference-coverage-helped-in-experiment":
        return "known-regression-risk-do-not-promote"
    if classification == "source-version-not-in-reference-db":
        return "coverage-gap-reference-needed"
    if classification == "missing-reference-coverage-but-bytecode-prefers-other-version":
        return "do-not-rerank-bytecode-prefers-selected"
    if not source:
        return "no-source-candidate-in-top-list"
    if classification in {
        "bytecode-evidence-prefers-selected-version",
    }:
        return "do-not-rerank-bytecode-prefers-selected"
    if selected_signals:
        return "conflicting-signals-keep-ambiguous"
    if source_signals:
        return "diagnostic-candidate-needs-control-matrix"
    return "ambiguity-only-no-independent-signal"


def safe_action(verdict: str) -> str:
    actions = {
        "artifact-family-review": "Review coordinate-family mapping before version scoring.",
        "coverage-gap-reference-needed": "Treat as reference coverage gap; add source version only in a guarded experiment.",
        "no-source-candidate-in-top-list": "Regenerate evidence with the source version available before considering a reranker.",
        "known-regression-risk-do-not-promote": "Do not promote globally; existing isolated experiment already regressed controls.",
        "do-not-rerank-bytecode-prefers-selected": "Keep selected version and report limitation unless a new independent signal appears.",
        "conflicting-signals-keep-ambiguous": "Keep ambiguity visible; do not force a scorer while signals conflict.",
        "diagnostic-candidate-needs-control-matrix": "Candidate for scoped experiment only; run current-control matrix before any output change.",
        "ambiguity-only-no-independent-signal": "Keep ambiguity reporting; no scoring change is justified.",
    }
    return actions[verdict]


def find_candidate(candidates: list[dict[str, Any]], version: Any) -> dict[str, Any] | None:
    for candidate in candidates:
        if str(candidate.get("version")) == str(version):
            return candidate
    return None


def find_source_candidate(
    candidates: list[dict[str, Any]], source_versions: list[Any]
) -> dict[str, Any] | None:
    source_version_set = {str(version) for version in source_versions}
    for candidate in candidates:
        if candidate.get("is_source_version") or str(candidate.get("version")) in source_version_set:
            return candidate
    return None


def build_signal_deltas(source: dict[str, Any], selected: dict[str, Any]) -> dict[str, float]:
    deltas: dict[str, float] = {}
    for signal in SCORE_SIGNALS:
        if source.get(signal) is not None and selected.get(signal) is not None:
            deltas[signal] = round(float(source[signal]) - float(selected[signal]), 6)
    if source.get("matched_unique_features") is not None and selected.get("matched_unique_features") is not None:
        deltas["matched_unique_features"] = int(source["matched_unique_features"]) - int(
            selected["matched_unique_features"]
        )
    if source.get("score") is not None and selected.get("score") is not None:
        deltas["total_score"] = round(float(source["score"]) - float(selected["score"]), 6)
    return deltas


def compact_candidate(candidate: dict[str, Any]) -> dict[str, Any]:
    keys = ["version", "score", *SCORE_SIGNALS, "matched_unique_features"]
    return {key: candidate.get(key) for key in keys if key in candidate}


def summarize_opcode_experiment(opcode_summary: dict[str, Any]) -> dict[str, Any]:
    rows = opcode_summary.get("rows", [])
    weighted_rows = [row for row in rows if float(row.get("opcode_ngram_weight", 0.0)) > 0.0]
    regressed_cases = [
        row.get("case_id")
        for row in weighted_rows
        if int(row.get("confirmed", 0)) < confirmed_at_weight_zero(rows, row.get("case_id"))
    ]
    return {
        "db_path": opcode_summary.get("db_path"),
        "weighted_cases": len(weighted_rows),
        "regressed_cases": sorted(case for case in regressed_cases if case),
        "policy": "Keep opcode n-gram weighting disabled globally; use only as diagnostic evidence.",
    }


def confirmed_at_weight_zero(rows: list[dict[str, Any]], case_id: Any) -> int:
    for row in rows:
        if row.get("case_id") == case_id and float(row.get("opcode_ngram_weight", 0.0)) == 0.0:
            return int(row.get("confirmed", 0))
    return 0


def build_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Version-Tie Reranker Diagnostics",
        "",
        "Generated by `scripts/build_version_tie_reranker_diagnostics.py`.",
        "",
        "This is a diagnostic-only artifact. It does not change matcher output, does not promote reference versions, and does not enable API-reference or opcode tri-gram weights globally.",
        "",
        "## Summary",
        "",
        f"- Rows inspected: {len(payload['rows'])}",
        f"- Signal threshold for source-vs-selected deltas: {payload['signal_threshold']}",
        f"- Opcode n-gram policy: {payload['opcode_ngram_global_experiment']['policy']}",
        "",
        "## Verdict Counts",
        "",
        "| Verdict | Count |",
        "|---|---:|",
    ]
    for verdict, count in sorted(payload["verdict_counts"].items()):
        lines.append(f"| `{verdict}` | {count} |")

    lines.extend(
        [
            "",
            "## Diagnostic Table",
            "",
            "| Case | Coordinate | Selected | Source | Classification | Source-supporting signals | Selected-supporting signals | Verdict | Safe action |",
            "|---|---|---|---|---|---|---|---|---|",
        ]
    )
    for row in payload["rows"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    md(row["case_id"]),
                    f"`{row['coordinate']}`",
                    md(row["selected_version"]),
                    md(", ".join(str(v) for v in row["source_versions"]) or "n/a"),
                    f"`{row['classification']}`",
                    md(", ".join(row["signals_supporting_source"]) or "none"),
                    md(", ".join(row["signals_supporting_selected"]) or "none"),
                    f"`{row['diagnostic_verdict']}`",
                    md(row["safe_action"]),
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Candidate Details",
            "",
        ]
    )
    for row in payload["rows"]:
        lines.extend(
            [
                f"### {row['case_id']} - `{row['coordinate']}`",
                "",
                f"- Selected version: `{row['selected_version']}`",
                f"- Source version(s): `{', '.join(str(v) for v in row['source_versions']) or 'n/a'}`",
                f"- Diagnostic verdict: `{row['diagnostic_verdict']}`",
                f"- Safe action: {row['safe_action']}",
                f"- Source candidate present in top list: `{row['source_candidate_present']}`",
                f"- Signal deltas, source minus selected: `{json.dumps(row['signal_deltas_source_minus_selected'], sort_keys=True)}`",
                "",
            ]
        )
    return "\n".join(lines)


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
