from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping, Sequence


MIN_TARGET_SCORE = 0.35
MIN_FAMILY_ANCHOR_SCORE = 0.30
MIN_FAMILY_ANCHORS = 2
PATCH_NEAR_TIE_MARGIN = 0.001
PUBLIC_TO_TARGET = {
    "androidx.lifecycle:lifecycle-runtime": "androidx.lifecycle:lifecycle-runtime-android",
    "androidx.lifecycle:lifecycle-viewmodel": "androidx.lifecycle:lifecycle-viewmodel-android",
}


@dataclass(frozen=True)
class LifecycleFamilyDecision:
    classification: str
    downgrade_public_claim: bool
    public_coordinate: str
    public_version: str
    source_versions: tuple[str, ...]
    target_coordinate: str | None
    target_version: str | None
    target_score: float
    target_source_alternative_gap: float | None
    family_anchors: tuple[str, ...]
    reason_codes: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def classify_lifecycle_public_overlap(
    *,
    coordinate: str,
    selected_version: str,
    source_versions: Sequence[str],
    sibling_decisions: Sequence[Mapping[str, Any]],
) -> LifecycleFamilyDecision:
    target_coordinate = PUBLIC_TO_TARGET.get(coordinate)
    if target_coordinate is None:
        return make_decision(
            classification="outside-lifecycle-public-scope",
            downgrade=False,
            coordinate=coordinate,
            selected_version=selected_version,
            source_versions=source_versions,
        )

    target = find_decision(sibling_decisions, target_coordinate)
    if target is None:
        return make_decision(
            classification="no-android-target-variant",
            downgrade=False,
            coordinate=coordinate,
            selected_version=selected_version,
            source_versions=source_versions,
            target_coordinate=target_coordinate,
        )

    target_version = str(target.get("selected_version") or "")
    target_score = float(target.get("score") or 0.0)
    anchors = family_anchors(
        sibling_decisions,
        excluded={coordinate, target_coordinate},
        version=target_version,
    )
    source_set = {str(version) for version in source_versions}
    source_gap = source_alternative_gap(target, source_set)

    if target_version in source_set and target_score >= MIN_TARGET_SCORE:
        return make_decision(
            classification="source-version-backed-target-family-evidence",
            downgrade=True,
            coordinate=coordinate,
            selected_version=selected_version,
            source_versions=source_versions,
            target_coordinate=target_coordinate,
            target_version=target_version,
            target_score=target_score,
            source_gap=source_gap,
            anchors=anchors,
            reason_codes=(
                "android-target-variant-matches-source-version",
                "downgrade-public-coordinate-claim-only",
            ),
        )

    if len(anchors) >= MIN_FAMILY_ANCHORS and target_score >= MIN_TARGET_SCORE:
        return make_decision(
            classification="coherent-target-family-band-evidence",
            downgrade=True,
            coordinate=coordinate,
            selected_version=selected_version,
            source_versions=source_versions,
            target_coordinate=target_coordinate,
            target_version=target_version,
            target_score=target_score,
            source_gap=source_gap,
            anchors=anchors,
            reason_codes=(
                "android-target-family-band-supported",
                "multiple-lifecycle-family-anchors",
                "downgrade-public-coordinate-claim-only",
            ),
        )

    if source_gap is not None and source_gap <= PATCH_NEAR_TIE_MARGIN:
        return make_decision(
            classification="target-patch-near-tie-keep-ambiguous",
            downgrade=False,
            coordinate=coordinate,
            selected_version=selected_version,
            source_versions=source_versions,
            target_coordinate=target_coordinate,
            target_version=target_version,
            target_score=target_score,
            source_gap=source_gap,
            anchors=anchors,
            reason_codes=("source-target-patch-near-tie", "do-not-force-patch-version"),
        )

    return make_decision(
        classification="insufficient-family-evidence",
        downgrade=False,
        coordinate=coordinate,
        selected_version=selected_version,
        source_versions=source_versions,
        target_coordinate=target_coordinate,
        target_version=target_version,
        target_score=target_score,
        source_gap=source_gap,
        anchors=anchors,
        reason_codes=("keep-visible-mismatch-or-ambiguity",),
    )


def family_anchors(
    decisions: Sequence[Mapping[str, Any]],
    *,
    excluded: set[str],
    version: str,
) -> tuple[str, ...]:
    anchors = [
        f"{decision.get('coordinate')}@{decision.get('selected_version')}"
        for decision in decisions
        if str(decision.get("coordinate") or "").startswith("androidx.lifecycle:")
        and str(decision.get("coordinate") or "") not in excluded
        and str(decision.get("selected_version") or "") == version
        and float(decision.get("score") or 0.0) >= MIN_FAMILY_ANCHOR_SCORE
    ]
    return tuple(sorted(anchors))


def source_alternative_gap(
    target: Mapping[str, Any],
    source_versions: set[str],
) -> float | None:
    target_score = float(target.get("score") or 0.0)
    for alternative in target.get("alternatives") or []:
        if str(alternative.get("version") or "") in source_versions:
            return round(abs(target_score - float(alternative.get("score") or 0.0)), 6)
    return None


def find_decision(
    decisions: Sequence[Mapping[str, Any]],
    coordinate: str,
) -> Mapping[str, Any] | None:
    for decision in decisions:
        if decision.get("coordinate") == coordinate:
            return decision
    return None


def make_decision(
    *,
    classification: str,
    downgrade: bool,
    coordinate: str,
    selected_version: str,
    source_versions: Sequence[str],
    target_coordinate: str | None = None,
    target_version: str | None = None,
    target_score: float = 0.0,
    source_gap: float | None = None,
    anchors: Sequence[str] = (),
    reason_codes: Sequence[str] = (),
) -> LifecycleFamilyDecision:
    return LifecycleFamilyDecision(
        classification=classification,
        downgrade_public_claim=downgrade,
        public_coordinate=coordinate,
        public_version=selected_version,
        source_versions=tuple(str(version) for version in source_versions),
        target_coordinate=target_coordinate,
        target_version=target_version,
        target_score=round(target_score, 6),
        target_source_alternative_gap=source_gap,
        family_anchors=tuple(anchors),
        reason_codes=tuple(reason_codes),
    )
