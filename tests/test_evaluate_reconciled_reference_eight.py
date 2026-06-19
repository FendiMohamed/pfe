import importlib.util
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "scripts" / "evaluate_reconciled_reference_eight.py"
SPEC = importlib.util.spec_from_file_location(
    "evaluate_reconciled_reference_eight",
    MODULE_PATH,
)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
build_markdown = MODULE.build_markdown
build_payload = MODULE.build_payload


def test_build_payload_separates_exact_ambiguous_and_uncertain_rows() -> None:
    rows = [
        {
            "exact_selected": True,
            "newly_selectable": True,
            "changed_selection": True,
            "classification": "exact-selected",
        },
        {
            "exact_selected": False,
            "newly_selectable": True,
            "changed_selection": True,
            "classification": "identity-supported-version-ambiguous",
        },
        {
            "exact_selected": False,
            "newly_selectable": False,
            "changed_selection": False,
            "classification": "weak-or-uncertain",
        },
    ]

    payload = build_payload(
        rows,
        baseline_db=Path("baseline.sqlite"),
        experiment_db=Path("experiment.sqlite"),
    )

    assert payload["verdict"] == "reconciled-eight-partial-version-impact"
    assert payload["summary"] == {
        "rows": 3,
        "exact_selected": 1,
        "newly_selectable_rows": 2,
        "changed_selections": 2,
        "not_exact_selected": 2,
        "identity_supported_version_ambiguous": 1,
        "weak_or_uncertain": 1,
    }


def test_build_markdown_includes_scoped_policy() -> None:
    payload = {
        "verdict": "reconciled-eight-no-exact-selection-impact",
        "scope": "Coordinate-only test.",
        "summary": {
            "rows": 0,
            "exact_selected": 0,
            "newly_selectable_rows": 0,
            "identity_supported_version_ambiguous": 0,
            "weak_or_uncertain": 0,
            "changed_selections": 0,
            "not_exact_selected": 0,
        },
        "rows": [],
        "policy": ["Keep the shared calibrated DB unchanged."],
    }

    markdown = build_markdown(payload)

    assert "Coordinate-only test." in markdown
    assert "Keep the shared calibrated DB unchanged." in markdown
