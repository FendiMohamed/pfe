from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import zipfile
from pathlib import Path


DEFAULT_GROUND_TRUTH_DIR = Path("data/test_apks")
DEFAULT_REPORTS_DIR = Path("data/results")
DEFAULT_FEATURE_DB = Path("data/reference_db/reference_features.sqlite")
DEFAULT_OUTPUT_DIR = Path("data/results/evaluation")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compare simple baselines against controlled APK reports.",
    )
    parser.add_argument("--ground-truth-dir", default=str(DEFAULT_GROUND_TRUTH_DIR))
    parser.add_argument("--reports-dir", default=str(DEFAULT_REPORTS_DIR))
    parser.add_argument("--db-path", default=str(DEFAULT_FEATURE_DB))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    return parser


def main() -> int:
    args = build_parser().parse_args()
    ground_truths = load_ground_truths(args.ground_truth_dir)
    reports = load_reports(args.reports_dir)
    hash_index = load_reference_hash_index(args.db_path)
    evaluation = evaluate_baselines(ground_truths, reports, hash_index)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "baseline-evaluation.json"
    markdown_path = output_dir / "baseline-evaluation.md"
    json_path.write_text(json.dumps(evaluation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(build_markdown(evaluation), encoding="utf-8")

    print(
        json.dumps(
            {
                "baseline_json": str(json_path),
                "baseline_markdown": str(markdown_path),
                "baselines": evaluation["metrics"],
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
            reports[normalize_path(apk_path)] = payload
    return reports


def load_reference_hash_index(db_path: str | Path) -> dict[str, dict]:
    path = Path(db_path)
    if not path.exists():
        return {}
    with sqlite3.connect(path) as connection:
        rows = connection.execute(
            """
            SELECT dex_files.sha256, components.coordinate, components.version, components.purl
            FROM dex_files
            JOIN components ON components.id = dex_files.component_id
            """
        ).fetchall()
    return {
        str(row[0]): {
            "coordinate": str(row[1]),
            "version": str(row[2]),
            "purl": str(row[3]),
        }
        for row in rows
    }


def evaluate_baselines(
    ground_truths: list[dict],
    reports_by_apk: dict[str, dict],
    hash_index: dict[str, dict],
) -> dict:
    rows: list[dict] = []
    for truth in ground_truths:
        report = reports_by_apk.get(normalize_path(truth["apk_path"]))
        rows.extend(evaluate_fixture_baselines(truth, report, hash_index))

    expected_components = sum(len(expected_components_from_truth(truth)) for truth in ground_truths)
    metrics = {
        baseline: metric_for_baseline(rows, baseline, expected_components)
        for baseline in ["package", "class", "hash"]
    }
    return {
        "fixtures": len(ground_truths),
        "expected_components": expected_components,
        "rows": rows,
        "metrics": metrics,
    }


def evaluate_fixture_baselines(
    truth: dict,
    report: dict | None,
    hash_index: dict[str, dict],
) -> list[dict]:
    candidates = report.get("match_summary", {}).get("candidates", []) if report else []
    rows = []
    for expected in expected_components_from_truth(truth):
        rows.extend(
            [
                evaluate_prediction(
                    truth,
                    expected,
                    "package",
                    candidate_baseline_prediction(candidates, "package_score"),
                ),
                evaluate_prediction(
                    truth,
                    expected,
                    "class",
                    candidate_baseline_prediction(candidates, "class_score"),
                ),
                evaluate_prediction(
                    truth,
                    expected,
                    "hash",
                    hash_baseline_prediction(truth["apk_path"], hash_index),
                ),
            ]
        )
    return rows


def candidate_baseline_prediction(candidates: list[dict], evidence_field: str) -> dict | None:
    scored = [
        candidate
        for candidate in candidates
        if candidate.get("evidence", {}).get(evidence_field, 0) > 0
    ]
    if not scored:
        return None
    best = sorted(
        scored,
        key=lambda candidate: (
            candidate.get("evidence", {}).get(evidence_field, 0),
            candidate.get("score", 0),
        ),
        reverse=True,
    )[0]
    return {
        "coordinate": best.get("coordinate"),
        "version": best.get("version"),
        "score": best.get("evidence", {}).get(evidence_field, 0),
    }


def hash_baseline_prediction(apk_path: str, hash_index: dict[str, dict]) -> dict | None:
    for digest in apk_dex_hashes(apk_path):
        if digest in hash_index:
            return {**hash_index[digest], "score": 1.0}
    return None


def apk_dex_hashes(apk_path: str | Path) -> list[str]:
    hashes: list[str] = []
    with zipfile.ZipFile(apk_path) as archive:
        for name in sorted(archive.namelist()):
            if Path(name).name.startswith("classes") and Path(name).suffix == ".dex":
                hashes.append(hashlib.sha256(archive.read(name)).hexdigest())
    return hashes


def evaluate_prediction(
    truth: dict,
    expected: dict,
    baseline: str,
    prediction: dict | None,
) -> dict:
    predicted_coordinate = prediction.get("coordinate") if prediction else None
    predicted_version = prediction.get("version") if prediction else None
    return {
        "variant": truth.get("variant", "unknown"),
        "baseline": baseline,
        "truth_coordinate": expected["coordinate"],
        "truth_version": expected["version"],
        "predicted_coordinate": predicted_coordinate,
        "predicted_version": predicted_version,
        "score": prediction.get("score", 0.0) if prediction else 0.0,
        "component_correct": predicted_coordinate == expected["coordinate"],
        "version_correct": (
            predicted_coordinate == expected["coordinate"]
            and predicted_version == expected["version"]
        ),
        "predicted": prediction is not None,
    }


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


def metric_for_baseline(rows: list[dict], baseline: str, fixtures: int) -> dict:
    baseline_rows = [row for row in rows if row["baseline"] == baseline]
    predicted = sum(1 for row in baseline_rows if row["predicted"])
    component_correct = sum(1 for row in baseline_rows if row["component_correct"])
    version_correct = sum(1 for row in baseline_rows if row["version_correct"])
    return {
        "component_precision": safe_divide(component_correct, predicted),
        "component_recall": safe_divide(component_correct, fixtures),
        "version_precision": safe_divide(version_correct, predicted),
        "version_recall": safe_divide(version_correct, fixtures),
    }


def build_markdown(evaluation: dict) -> str:
    lines = [
        "# Baseline Evaluation",
        "",
        "## Metrics",
        "",
        "| Baseline | Component precision | Component recall | Version precision | Version recall |",
        "|---|---:|---:|---:|---:|",
    ]
    for baseline, metrics in evaluation["metrics"].items():
        lines.append(
            "| "
            f"{baseline} | "
            f"{metrics['component_precision']:.3f} | "
            f"{metrics['component_recall']:.3f} | "
            f"{metrics['version_precision']:.3f} | "
            f"{metrics['version_recall']:.3f} |"
        )

    lines.extend(
        [
            "",
            "## Rows",
            "",
            "| Variant | Baseline | Prediction | Score | Component correct | Version correct |",
            "|---|---|---|---:|---:|---:|",
        ]
    )
    for row in evaluation["rows"]:
        prediction = "none"
        if row["predicted"]:
            prediction = f"`{row['predicted_coordinate']}@{row['predicted_version']}`"
        lines.append(
            "| "
            f"{row['variant']} | "
            f"{row['baseline']} | "
            f"{prediction} | "
            f"{float(row['score']):.3f} | "
            f"{str(row['component_correct']).lower()} | "
            f"{str(row['version_correct']).lower()} |"
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
