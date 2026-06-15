from __future__ import annotations

import json
from pathlib import Path

import pytest

from apk_sbom.guarded_reference_db_promotion import build_payload


def test_guarded_workflow_classifies_safe_app_specific_and_regression_risk(tmp_path) -> None:
    write_comparison(tmp_path / "safe.json", improved=["target"], regressed=[])
    write_comparison(
        tmp_path / "app-specific.json",
        improved=["target"],
        regressed=["control-a"],
    )
    write_comparison(
        tmp_path / "regression-risk.json",
        improved=[],
        regressed=["control-b"],
    )
    manifest = tmp_path / "manifest.json"
    write_json(
        manifest,
        {
            "experiments": [
                experiment("safe", "safe.json", scope="singleton"),
                experiment("app-specific", "app-specific.json", scope="tested-bundle"),
                experiment("regression-risk", "regression-risk.json", scope="singleton"),
            ]
        },
    )

    payload = build_payload(manifest_json=manifest)

    assert payload["verdict"] == "guarded-reference-db-promotion-workflow-ready"
    assert payload["summary"]["classification_counts"] == {
        "safe": 1,
        "app-specific": 1,
        "regression-risk": 1,
        "no-change": 0,
    }
    assert payload["safe_singleton_candidates"] == ["example:library@1.0.0"]
    by_id = {row["id"]: row for row in payload["experiments"]}
    assert by_id["app-specific"]["claim_scope"] == "exact-tested-bundle-only"
    assert by_id["regression-risk"]["promotion_decision"].startswith("Reject global")


def test_guarded_workflow_keeps_clean_bundle_claim_scoped_to_bundle(tmp_path) -> None:
    write_comparison(tmp_path / "safe-bundle.json", improved=["target"], regressed=[])
    manifest = tmp_path / "manifest.json"
    write_json(
        manifest,
        {
            "experiments": [
                {
                    **experiment("safe-bundle", "safe-bundle.json", scope="tested-bundle"),
                    "candidate_versions": [
                        "example:first@1.0.0",
                        "example:second@2.0.0",
                    ],
                }
            ]
        },
    )

    payload = build_payload(manifest_json=manifest)

    row = payload["experiments"][0]
    assert row["classification"] == "safe"
    assert row["claim_scope"] == "exact-tested-bundle-only"
    assert payload["summary"]["safe_tested_bundles"] == 1
    assert payload["safe_singleton_candidates"] == []


def test_guarded_workflow_rejects_invalid_scope(tmp_path) -> None:
    write_comparison(tmp_path / "comparison.json", improved=["target"], regressed=[])
    manifest = tmp_path / "manifest.json"
    write_json(
        manifest,
        {"experiments": [experiment("invalid", "comparison.json", scope="global")]},
    )

    with pytest.raises(ValueError, match="invalid experiment scope"):
        build_payload(manifest_json=manifest)


def experiment(experiment_id: str, comparison_json: str, *, scope: str) -> dict:
    return {
        "id": experiment_id,
        "scope": scope,
        "comparison_json": comparison_json,
        "target_cases": ["target"],
        "candidate_versions": ["example:library@1.0.0"],
    }


def write_comparison(path: Path, *, improved: list[str], regressed: list[str]) -> None:
    write_json(
        path,
        {
            "case_count": 3,
            "improved_cases": improved,
            "regressed_cases": regressed,
        },
    )


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")
