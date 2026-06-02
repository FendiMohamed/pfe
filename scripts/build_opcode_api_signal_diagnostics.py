from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_API_JSON = Path("data/results/experiments/api-reference-weight/api-reference-weight-summary.json")
DEFAULT_OPCODE_JSON = Path("data/results/experiments/opcode-ngram-weight/opcode-ngram-weight-summary.json")
DEFAULT_OUTPUT_JSON = Path("data/results/experiments/opcode-api-signal-diagnostics.json")
DEFAULT_OUTPUT_DOC = Path("docs/evaluation/OPCODE_API_SIGNAL_DIAGNOSTICS.md")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Summarize guarded API-reference and opcode tri-gram signal experiments.",
    )
    parser.add_argument("--api-json", default=str(DEFAULT_API_JSON))
    parser.add_argument("--opcode-json", default=str(DEFAULT_OPCODE_JSON))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--output-doc", default=str(DEFAULT_OUTPUT_DOC))
    return parser


def main() -> int:
    args = build_parser().parse_args()
    api_path = Path(args.api_json)
    opcode_path = Path(args.opcode_json)
    payload = build_payload(
        read_json(api_path),
        read_json(opcode_path),
        api_path=api_path,
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
                "signals": len(payload["signals"]),
                "verdict": payload["verdict"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def build_payload(
    api_summary: dict[str, Any],
    opcode_summary: dict[str, Any],
    *,
    api_path: Path,
    opcode_path: Path,
) -> dict[str, Any]:
    signals = [
        summarize_signal(
            "api-reference-weight",
            api_summary,
            weight_key="api_reference_weight",
            evidence_key="total_matched_api_references",
        ),
        summarize_signal(
            "opcode-ngram-weight",
            opcode_summary,
            weight_key="opcode_ngram_weight",
            evidence_key="total_matched_opcode_ngrams",
        ),
    ]
    has_improvement = any(signal["improved_cases"] for signal in signals)
    has_regression = any(signal["regressed_cases"] for signal in signals)
    verdict = (
        "keep-disabled"
        if has_regression or not has_improvement
        else "requires-scoped-control-matrix"
    )
    return {
        "schema_version": 1,
        "sources": {
            "api_reference_weight": normalize_path(api_path),
            "opcode_ngram_weight": normalize_path(opcode_path),
        },
        "policy": [
            "API/member-reference and opcode tri-gram features are useful diagnostic evidence.",
            "Global weights stay at 0.0 unless a scoped scorer improves target APKs without current-control regressions.",
            "A feature being extractable is not enough to promote it into official scoring.",
        ],
        "signals": signals,
        "verdict": verdict,
        "conclusion": (
            "Complete for the current MVP: keep API-reference and opcode tri-gram weights disabled by default. "
            "API-reference weight 0.05 changed no source-validation metrics in its guarded slice; opcode "
            "tri-gram weight 0.02 regressed controls and produced no confirmed-version improvement."
        ),
    }


def summarize_signal(
    name: str,
    summary: dict[str, Any],
    *,
    weight_key: str,
    evidence_key: str,
) -> dict[str, Any]:
    rows = summary.get("rows", [])
    baseline_by_case = {
        str(row.get("case_id")): row
        for row in rows
        if float(row.get(weight_key, 0.0)) == 0.0
    }
    trial_rows = [
        summarize_trial_row(row, baseline_by_case.get(str(row.get("case_id"))), weight_key, evidence_key)
        for row in rows
        if float(row.get(weight_key, 0.0)) != 0.0
    ]
    improved_cases = [
        row["case_id"]
        for row in trial_rows
        if row["delta_confirmed"] > 0 or row["delta_mismatches"] < 0 or row["delta_missing"] < 0
    ]
    regressed_cases = [
        row["case_id"]
        for row in trial_rows
        if row["delta_confirmed"] < 0 or row["delta_mismatches"] > 0 or row["delta_missing"] > 0
    ]
    return {
        "signal": name,
        "case_count": summary.get("case_count", len(baseline_by_case)),
        "weights": summary.get("weights", sorted({row.get(weight_key) for row in rows})),
        "trial_rows": trial_rows,
        "improved_cases": improved_cases,
        "regressed_cases": regressed_cases,
        "decision": "keep-disabled" if regressed_cases or not improved_cases else "needs-scoped-review",
    }


def summarize_trial_row(
    row: dict[str, Any],
    baseline: dict[str, Any] | None,
    weight_key: str,
    evidence_key: str,
) -> dict[str, Any]:
    baseline = baseline or {}
    return {
        "case_id": row.get("case_id"),
        "weight": row.get(weight_key),
        "confirmed": row.get("confirmed", 0),
        "mismatches": row.get("version_mismatches", 0),
        "missing": row.get("missing", 0),
        "delta_confirmed": row.get("confirmed", 0) - baseline.get("confirmed", 0),
        "delta_mismatches": row.get("version_mismatches", 0) - baseline.get("version_mismatches", 0),
        "delta_missing": row.get("missing", 0) - baseline.get("missing", 0),
        "matched_signal_count": row.get(evidence_key, 0),
    }


def build_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Opcode/API Signal Diagnostics",
        "",
        "Generated by `scripts/build_opcode_api_signal_diagnostics.py`.",
        "",
        "This diagnostic consolidates the guarded API/member-reference and opcode tri-gram weight experiments. It does not change matcher output.",
        "",
        "## Policy",
        "",
    ]
    lines.extend(f"- {item}" for item in payload["policy"])
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- Verdict: `{payload['verdict']}`",
            f"- Conclusion: {payload['conclusion']}",
            "",
            "## Signal Decisions",
            "",
            "| Signal | Cases | Weights | Improved cases | Regressed cases | Decision |",
            "|---|---:|---|---|---|---|",
        ]
    )
    for signal in payload["signals"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{signal['signal']}`",
                    str(signal["case_count"]),
                    md(", ".join(str(weight) for weight in signal["weights"])),
                    md(", ".join(signal["improved_cases"]) or "none"),
                    md(", ".join(signal["regressed_cases"]) or "none"),
                    f"`{signal['decision']}`",
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Trial Rows",
            "",
            "| Signal | Case | Weight | Confirmed delta | Mismatch delta | Missing delta | Matched signal count |",
            "|---|---|---:|---:|---:|---:|---:|",
        ]
    )
    for signal in payload["signals"]:
        for row in signal["trial_rows"]:
            lines.append(
                "| "
                + " | ".join(
                    [
                        f"`{signal['signal']}`",
                        md(row["case_id"]),
                        f"{float(row['weight']):.3f}",
                        str(row["delta_confirmed"]),
                        str(row["delta_mismatches"]),
                        str(row["delta_missing"]),
                        str(row["matched_signal_count"]),
                    ]
                )
                + " |"
            )

    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- Do not enable API-reference or opcode tri-gram weights globally.",
            "- Keep both signals available for diagnostics and future per-coordinate experiments.",
            "- Require a fresh current-control matrix before any scoped scorer uses either signal.",
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
