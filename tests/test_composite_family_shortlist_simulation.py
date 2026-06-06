from __future__ import annotations

import json
from pathlib import Path

from apk_sbom.composite_family_shortlist_simulation import build_payload, should_rescue


def test_composite_shortlist_recommends_balanced_rescue_lane(tmp_path) -> None:
    diagnostic = tmp_path / "diagnostic.json"
    write_json(
        diagnostic,
        {
            "rows": [
                row("controlled", "expected:library", slots=3, source=["1.0.0"], class_score=0.9),
                row("controlled", "noise:library", slots=4),
                row("real", "best:library", slots=2, class_score=0.9),
                row(
                    "real",
                    "source:library",
                    slots=2,
                    source=["2.0.0"],
                    dependency_score=0.1,
                    matched_dependency_edges=1,
                ),
                row("real", "noise:library", slots=5),
            ]
        },
    )

    payload = build_payload(diagnostic_json=diagnostic, margins=(0.0, 0.1, 1.0))

    assert (
        payload["verdict"]
        == "composite-family-shortlist-report-backed-candidate-needs-live-offline-validation"
    )
    recommended = payload["recommended_configuration"]
    assert recommended["profile_id"] == "balanced-context"
    assert recommended["rescue_policy"] == "independent-support-rescue"
    assert recommended["margin"] == 0.1
    assert recommended["candidate_version_slots_removed"] == 9
    assert recommended["tracked_source_family_losses"] == 0


def test_composite_shortlist_rejects_when_source_family_has_no_support(tmp_path) -> None:
    diagnostic = tmp_path / "diagnostic.json"
    write_json(
        diagnostic,
        {
            "rows": [
                row("controlled", "noise:library", slots=4, class_score=0.9),
                row("controlled", "source:library", slots=3, source=["1.0.0"]),
                row("real", "real:library", slots=2, source=["2.0.0"], class_score=0.8),
            ]
        },
    )

    payload = build_payload(diagnostic_json=diagnostic, margins=(0.0, 1.0))

    assert payload["verdict"] == "composite-family-shortlist-no-safe-report-backed-candidate"
    assert payload["recommended_configuration"] is None


def test_independent_support_rescue_requires_concrete_evidence() -> None:
    assert should_rescue({"matched_dependency_edges": 1}, "independent-support-rescue")
    assert should_rescue({"matched_string_literals": 2}, "independent-support-rescue")
    assert should_rescue(
        {"matched_classes": 1, "matched_methods": 1},
        "independent-support-rescue",
    )
    assert not should_rescue({"matched_classes": 1}, "independent-support-rescue")
    assert not should_rescue({"matched_string_literals": 1}, "independent-support-rescue")


def row(
    report: str,
    coordinate: str,
    *,
    slots: int,
    source: list[str] | None = None,
    package_score: float = 0.0,
    class_score: float = 0.0,
    method_score: float = 0.0,
    dependency_score: float = 0.0,
    literal_score: float = 0.0,
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
        "dependency_score": dependency_score,
        "literal_score": literal_score,
        "matched_classes": matched_classes,
        "matched_methods": matched_methods,
        "matched_dependency_edges": matched_dependency_edges,
        "matched_string_literals": matched_string_literals,
    }


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")
