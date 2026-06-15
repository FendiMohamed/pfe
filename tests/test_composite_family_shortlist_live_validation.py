from __future__ import annotations

from apk_sbom.composite_family_shortlist_live_validation import (
    build_family_shortlist,
    compare_selected_versions,
)
from apk_sbom.matcher import FeatureSet, ReferenceComponentFeatures


def test_live_shortlist_preserves_complete_retained_version_band() -> None:
    apk_features = FeatureSet(
        packages={"target"},
        classes={"Ltarget/Api;"},
        methods={"Ltarget/Api;->run()V"},
    )
    references = [
        reference(1, "example:target", "1.0.0", classes={"Ltarget/Api;"}),
        reference(2, "example:target", "2.0.0", classes={"Ltarget/Api;"}),
        reference(3, "example:noise", "1.0.0", classes={"Lnoise/Api;"}),
    ]

    shortlist = build_family_shortlist(apk_features, references)

    assert shortlist["retained_coordinates"] == {"example:target"}
    assert shortlist["removed_coordinates"] == {"example:noise"}
    assert shortlist["reference_rows_retained"] == 2


def test_live_shortlist_rescues_family_with_independent_dependency_support() -> None:
    dependency = ("Lsource/A;", "Lsource/B;", "invoke")
    apk_features = FeatureSet(
        packages={"best"},
        classes={"Lbest/Api;"},
        methods={"Lbest/Api;->run()V"},
        class_dependencies={dependency},
    )
    references = [
        reference(
            1,
            "example:best",
            "1.0.0",
            packages={"best"},
            classes={"Lbest/Api;"},
            methods={"Lbest/Api;->run()V"},
        ),
        reference(
            2,
            "example:rescued",
            "1.0.0",
            dependencies={dependency},
        ),
        reference(3, "example:noise", "1.0.0", classes={"Lnoise/Api;"}),
    ]

    shortlist = build_family_shortlist(apk_features, references, margin=0.0)

    assert shortlist["retained_coordinates"] == {"example:best", "example:rescued"}
    assert shortlist["rescued_coordinates"] == {"example:best", "example:rescued"}
    assert shortlist["removed_coordinates"] == {"example:noise"}


def test_selected_version_comparison_flags_source_regression_and_improvement() -> None:
    comparison = compare_selected_versions(
        {
            "example:lost": "1.0.0",
            "example:regressed": "1.0.0",
            "example:improved": "0.9.0",
        },
        {
            "example:regressed": "2.0.0",
            "example:improved": "1.0.0",
        },
        source_versions_by_coordinate={
            "example:lost": ["1.0.0"],
            "example:regressed": ["1.0.0"],
            "example:improved": ["1.0.0"],
        },
    )

    assert comparison["source_family_loss_count"] == 1
    assert comparison["source_selection_regression_count"] == 2
    assert comparison["source_selection_improvement_count"] == 1
    assert comparison["selected_version_change_count"] == 3


def reference(
    component_id: int,
    coordinate: str,
    version: str,
    *,
    packages: set[str] | None = None,
    classes: set[str] | None = None,
    methods: set[str] | None = None,
    dependencies: set[tuple[str, str, str]] | None = None,
) -> ReferenceComponentFeatures:
    group_id, artifact_id = coordinate.split(":")
    return ReferenceComponentFeatures(
        component_id=component_id,
        coordinate=coordinate,
        group_id=group_id,
        artifact_id=artifact_id,
        version=version,
        purl=f"pkg:maven/{group_id}/{artifact_id}@{version}",
        features=FeatureSet(
            packages=packages or set(),
            classes=classes or set(),
            methods=methods or set(),
            class_dependencies=dependencies or set(),
        ),
    )
