from __future__ import annotations

import argparse
import json
from pathlib import Path


DEFAULT_GROUND_TRUTH_DIR = Path("data/test_apks")
DEFAULT_REPORTS_DIR = Path("data/results")
DEFAULT_OUTPUT_DIR = Path("data/results/evaluation")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Evaluate controlled APK reports against ground-truth metadata.",
    )
    parser.add_argument("--ground-truth-dir", default=str(DEFAULT_GROUND_TRUTH_DIR))
    parser.add_argument("--reports-dir", default=str(DEFAULT_REPORTS_DIR))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    return parser


def main() -> int:
    args = build_parser().parse_args()
    ground_truths = load_ground_truths(args.ground_truth_dir)
    reports = load_reports(args.reports_dir)
    evaluation = evaluate_reports(ground_truths, reports)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "controlled-evaluation.json"
    markdown_path = output_dir / "controlled-evaluation.md"
    json_path.write_text(json.dumps(evaluation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(build_markdown(evaluation), encoding="utf-8")

    print(
        json.dumps(
            {
                "evaluation_json": str(json_path),
                "evaluation_markdown": str(markdown_path),
                "fixtures": evaluation["fixtures"],
                "expected_components": evaluation["expected_components"],
                "component_recall": evaluation["metrics"]["component_recall"],
                "version_recall": evaluation["metrics"]["version_recall"],
                "candidate_version_recall": evaluation["metrics"]["candidate_version_recall"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def load_ground_truths(root: str | Path) -> list[dict]:
    return [
        read_json(path)
        for path in sorted(Path(root).glob("*.ground-truth.json"))
    ]


def load_reports(root: str | Path) -> dict[str, dict]:
    reports: dict[str, dict] = {}
    for path in sorted(Path(root).glob("report-*/report.json")):
        payload = read_json(path)
        apk_path = payload.get("apk", {}).get("apk_path")
        if apk_path:
            reports[normalize_path(apk_path)] = {**payload, "_report_path": str(path)}
    return reports


def evaluate_reports(ground_truths: list[dict], reports_by_apk: dict[str, dict]) -> dict:
    rows: list[dict] = []
    detected_total = 0
    for truth in ground_truths:
        apk_path = normalize_path(truth["apk_path"])
        report = reports_by_apk.get(apk_path)
        if report:
            detected_total += len(report.get("detected_components", []))
        rows.extend(evaluate_fixture(truth, report))

    correct_component_total = sum(1 for row in rows if row["component_detected"])
    correct_version_total = sum(1 for row in rows if row["version_detected"])
    candidate_correct_total = sum(1 for row in rows if row["candidate_version_correct"])
    expected_components = len(rows)

    return {
        "fixtures": len(ground_truths),
        "expected_components": expected_components,
        "rows": rows,
        "metrics": {
            "component_precision": safe_divide(correct_component_total, detected_total),
            "component_recall": safe_divide(correct_component_total, expected_components),
            "version_precision": safe_divide(correct_version_total, detected_total),
            "version_recall": safe_divide(correct_version_total, expected_components),
            "candidate_version_recall": safe_divide(candidate_correct_total, expected_components),
        },
    }


def evaluate_fixture(truth: dict, report: dict | None) -> list[dict]:
    expected_components = expected_components_from_truth(truth)
    if report is None:
        return [
            {
                "apk_path": truth["apk_path"],
                "variant": truth.get("variant", "unknown"),
                "coordinate": component["coordinate"],
                "version": component["version"],
                "report_found": False,
                "detected_components": 0,
                "component_detected": False,
                "version_detected": False,
                "candidate_version_correct": False,
                "candidate_decision": "missing",
                "candidate_confidence": "missing",
                "candidate_selected_version": None,
                "candidate_score": 0.0,
            }
            for component in expected_components
        ]

    components = report.get("detected_components", [])
    rows = []
    for expected in expected_components:
        truth_components = [
            component
            for component in components
            if component.get("group") and component.get("artifact")
            and f"{component['group']}:{component['artifact']}" == expected["coordinate"]
        ]
        component_detected = bool(truth_components)
        version_detected = any(
            component.get("version") == expected["version"]
            for component in truth_components
        )

        decision = find_truth_decision(report, expected["coordinate"])
        candidate_version_correct = bool(
            decision and decision.get("selected_version") == expected["version"]
        )

        rows.append(
            {
                "apk_path": truth["apk_path"],
                "variant": truth.get("variant", "unknown"),
                "coordinate": expected["coordinate"],
                "version": expected["version"],
                "report_found": True,
                "report_path": report.get("_report_path"),
                "detected_components": len(components),
                "component_detected": component_detected,
                "version_detected": version_detected,
                "candidate_version_correct": candidate_version_correct,
                "candidate_decision": decision.get("version_decision") if decision else "missing",
                "candidate_confidence": decision.get("confidence_label") if decision else "missing",
                "candidate_selected_version": decision.get("selected_version") if decision else None,
                "candidate_score": decision.get("score") if decision else 0.0,
            }
        )
    return rows


def expected_components_from_truth(truth: dict) -> list[dict]:
    components = truth.get("expected_components")
    if components:
        return [
            {
                "coordinate": component["coordinate"],
                "version": component["version"],
            }
            for component in components
        ]
    return [{"coordinate": truth["coordinate"], "version": truth["version"]}]


def find_truth_decision(report: dict, coordinate: str) -> dict | None:
    decisions = report.get("match_summary", {}).get("decisions", [])
    for decision in decisions:
        if decision.get("coordinate") == coordinate:
            return decision
    return None


def build_markdown(evaluation: dict) -> str:
    metrics = evaluation["metrics"]
    lines = [
        "# Controlled APK Evaluation",
        "",
        f"- Fixtures: {evaluation['fixtures']}",
        f"- Expected components: {evaluation['expected_components']}",
        "",
        "## Metrics",
        "",
        f"- Component precision: {metrics['component_precision']:.3f}",
        f"- Component recall: {metrics['component_recall']:.3f}",
        f"- Version precision: {metrics['version_precision']:.3f}",
        f"- Version recall: {metrics['version_recall']:.3f}",
        f"- Candidate version recall: {metrics['candidate_version_recall']:.3f}",
        "",
        "## Fixtures",
        "",
        "| Variant | Ground truth | Detected component | Detected version | Candidate version | Decision | Score |",
        "|---|---|---:|---:|---:|---|---:|",
    ]
    for row in evaluation["rows"]:
        lines.append(
            "| "
            f"{row['variant']} | "
            f"`{row['coordinate']}@{row['version']}` | "
            f"{str(row['component_detected']).lower()} | "
            f"{str(row['version_detected']).lower()} | "
            f"{str(row['candidate_version_correct']).lower()} | "
            f"{row['candidate_decision']}/{row['candidate_confidence']} | "
            f"{float(row['candidate_score']):.3f} |"
        )
    lines.append("")
    return "\n".join(lines)


def read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def normalize_path(path: str) -> str:
    return path.replace("\\", "/")


def safe_divide(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return round(numerator / denominator, 6)


if __name__ == "__main__":
    raise SystemExit(main())
