from __future__ import annotations

import json
from pathlib import Path

from apk_sbom.class_correspondence_pruning_diagnostics import build_payload


def test_class_correspondence_stays_diagnostic_when_it_underperforms_composite(
    tmp_path: Path,
) -> None:
    paths = write_inputs(tmp_path, promoted_removed=20)

    payload = build_payload(
        **paths,
        margins=(0.0, 1.0),
    )

    assert payload["verdict"] == "class-correspondence-pruning-no-new-promotion"
    assert (
        payload["recommendation"]
        == "keep-class-correspondence-diagnostic-only-and-move-to-optimization-aware-logic"
    )
    assert payload["summary"]["strict_clean_reducing_configurations"] == 0
    assert payload["summary"]["best_safe_candidate_version_slots_removed"] < 20


def test_class_correspondence_candidate_when_it_beats_composite(tmp_path: Path) -> None:
    paths = write_inputs(tmp_path, promoted_removed=2)

    payload = build_payload(
        **paths,
        margins=(0.0, 1.0),
    )

    assert (
        payload["verdict"]
        == "class-correspondence-pruning-candidate-needs-live-validation"
    )
    assert payload["summary"]["best_safe_outperforms_promoted_composite"] is True


def write_inputs(tmp_path: Path, *, promoted_removed: int) -> dict[str, Path]:
    diagnostic_json = tmp_path / "diagnostic.json"
    composite_json = tmp_path / "composite.json"
    write_json(
        diagnostic_json,
        {
            "rows": [
                row(
                    "controlled",
                    "source:library",
                    slots=3,
                    source=["1.0.0"],
                    class_score=0.1,
                    matched_dependency_edges=1,
                ),
                row(
                    "controlled",
                    "noise:library",
                    slots=4,
                    class_score=0.95,
                    method_score=0.95,
                ),
                row(
                    "real",
                    "real:library",
                    slots=2,
                    source=["2.0.0"],
                    class_score=0.9,
                    method_score=0.9,
                ),
                row("real", "other:library", slots=5, class_score=0.2),
            ]
        },
    )
    write_json(
        composite_json,
        {
            "recommended_configuration": {
                "profile_id": "balanced-context",
                "rescue_policy": "independent-support-rescue",
                "margin": 0.1,
                "candidate_version_slots_removed": promoted_removed,
                "family_rows_removed": 10,
                "tracked_source_family_losses": 0,
            }
        },
    )
    return {
        "diagnostic_json": diagnostic_json,
        "composite_json": composite_json,
    }


def row(
    report: str,
    coordinate: str,
    *,
    slots: int,
    source: list[str] | None = None,
    package_score: float = 0.0,
    class_score: float = 0.0,
    method_score: float = 0.0,
    matched_classes: int = 0,
    matched_methods: int = 0,
    matched_dependency_edges: int = 0,
    matched_string_literals: int = 0,
) -> dict:
    return {
        "report_path": f"{report}.json",
        "dataset_layer": "controlled-generated" if report == "controlled" else "real-apk",
        "case_id": report,
        "coordinate": coordinate,
        "reference_versions_considered": slots,
        "source_versions": source or [],
        "package_score": package_score,
        "class_score": class_score,
        "method_score": method_score,
        "matched_classes": matched_classes,
        "matched_methods": matched_methods,
        "matched_dependency_edges": matched_dependency_edges,
        "matched_string_literals": matched_string_literals,
    }


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")
