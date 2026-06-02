from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping, Sequence


STRONG_BASELINE_STATUSES = frozenset({"exact", "likely"})
STRONG_BASELINE_LABELS = frozenset({"high", "medium"})


@dataclass(frozen=True)
class R8ScopedRerankProfile:
    profile_id: str
    coordinate: str
    diagnostic_version: str
    min_top_score: float
    min_margin: float
    min_feature_families: int = 3
    required_any_tags: tuple[str, ...] = ()
    required_all_tags: tuple[str, ...] = ()
    blocked_tags: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class R8TriggerDecision:
    apply: bool
    reason_codes: tuple[str, ...]
    blocked_by: tuple[str, ...]
    baseline_version: str | None
    diagnostic_version: str | None
    profile_id: str | None = None
    top_score: float = 0.0
    score_margin: float = 0.0
    supporting_feature_families: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


DEFAULT_R8_SCOPED_PROFILES: tuple[R8ScopedRerankProfile, ...] = (
    R8ScopedRerankProfile(
        profile_id="androidx-core-1.16.0-modern-androidx-low-confidence",
        coordinate="androidx.core:core",
        diagnostic_version="1.16.0",
        min_top_score=0.84,
        min_margin=0.0,
        required_any_tags=("modern-androidx",),
        blocked_tags=("older-dependency-profile", "native-heavy", "maps"),
    ),
    R8ScopedRerankProfile(
        profile_id="androidx-viewpager2-1.1.0-modern-or-security-low-confidence",
        coordinate="androidx.viewpager2:viewpager2",
        diagnostic_version="1.1.0",
        min_top_score=0.62,
        min_margin=0.015,
        required_any_tags=("modern-androidx", "security"),
        blocked_tags=("older-dependency-profile", "native-heavy", "maps"),
    ),
    R8ScopedRerankProfile(
        profile_id="androidx-swiperefreshlayout-1.2.0-large-compose-low-confidence",
        coordinate="androidx.swiperefreshlayout:swiperefreshlayout",
        diagnostic_version="1.2.0",
        min_top_score=0.66,
        min_margin=0.03,
        required_all_tags=("large-modern-tree", "compose"),
    ),
)


def should_apply_scoped_r8_rerank(
    *,
    coordinate: str,
    baseline_version: str | None,
    diagnostic_version: str | None,
    top_diagnostic_versions: Sequence[Mapping[str, Any]] | None,
    role: str | None = None,
    category: str | None = None,
    tags: Sequence[str] | None = None,
    baseline_version_status: str | None = None,
    baseline_version_confidence_label: str | None = None,
    validation_source_versions: Sequence[str] | None = None,
    profiles: Sequence[R8ScopedRerankProfile] = DEFAULT_R8_SCOPED_PROFILES,
) -> R8TriggerDecision:
    top_score, score_margin, supporting_families = multiscale_rank_stats(
        top_diagnostic_versions
    )
    base_decision = {
        "baseline_version": baseline_version,
        "diagnostic_version": diagnostic_version,
        "top_score": top_score,
        "score_margin": score_margin,
        "supporting_feature_families": supporting_families,
    }
    blocked_by: list[str] = []
    reason_codes: list[str] = []

    if not diagnostic_version:
        blocked_by.append("missing-diagnostic-version")
        return R8TriggerDecision(False, tuple(reason_codes), tuple(blocked_by), **base_decision)
    if diagnostic_version == baseline_version:
        blocked_by.append("diagnostic-matches-baseline")
        return R8TriggerDecision(False, tuple(reason_codes), tuple(blocked_by), **base_decision)
    if category:
        blocked_by.append("controlled-generated-row")
        return R8TriggerDecision(False, tuple(reason_codes), tuple(blocked_by), **base_decision)

    profile = _matching_profile(coordinate, diagnostic_version, profiles)
    if profile is None:
        blocked_by.append("not-phase4-improvement-profile")
        return R8TriggerDecision(False, tuple(reason_codes), tuple(blocked_by), **base_decision)

    if role != "source-validated-partial":
        blocked_by.append("not-source-validated-partial-layer")
    if _is_strong_baseline(baseline_version_status, baseline_version_confidence_label):
        blocked_by.append("baseline-decision-too-strong")
    if supporting_families < profile.min_feature_families:
        blocked_by.append("insufficient-feature-family-agreement")
    if top_score < profile.min_top_score:
        blocked_by.append("diagnostic-score-below-profile-threshold")
    if score_margin < profile.min_margin:
        blocked_by.append("diagnostic-margin-below-profile-threshold")

    tag_set = frozenset(tags or ())
    missing_all = sorted(set(profile.required_all_tags) - tag_set)
    if missing_all:
        blocked_by.append("missing-required-context-tags")
    if profile.required_any_tags and not tag_set.intersection(profile.required_any_tags):
        blocked_by.append("missing-required-context-tag-family")
    if tag_set.intersection(profile.blocked_tags):
        blocked_by.append("blocked-context-tag")

    if _has_prerelease_source(validation_source_versions):
        blocked_by.append("source-prerelease-not-in-reference-profile")

    if blocked_by:
        return R8TriggerDecision(
            False,
            tuple(reason_codes),
            tuple(blocked_by),
            profile_id=profile.profile_id,
            **base_decision,
        )

    reason_codes.extend(
        [
            "phase4-improvement-profile",
            "baseline-low-confidence-candidate",
            "multiscale-thresholds-passed",
            "context-tags-passed",
        ]
    )
    return R8TriggerDecision(
        True,
        tuple(reason_codes),
        tuple(blocked_by),
        profile_id=profile.profile_id,
        **base_decision,
    )


def multiscale_rank_stats(
    top_diagnostic_versions: Sequence[Mapping[str, Any]] | None,
) -> tuple[float, float, int]:
    if not top_diagnostic_versions:
        return 0.0, 0.0, 0
    leader = top_diagnostic_versions[0]
    top_score = _float_value(leader.get("diagnostic_score"))
    second_score = (
        _float_value(top_diagnostic_versions[1].get("diagnostic_score"))
        if len(top_diagnostic_versions) > 1
        else 0.0
    )
    feature_scores = leader.get("feature_scores")
    supporting_families = 0
    if isinstance(feature_scores, Mapping):
        supporting_families = sum(
            1 for value in feature_scores.values() if _float_value(value) >= 0.5
        )
    return round(top_score, 6), round(max(0.0, top_score - second_score), 6), supporting_families


def _matching_profile(
    coordinate: str,
    diagnostic_version: str,
    profiles: Sequence[R8ScopedRerankProfile],
) -> R8ScopedRerankProfile | None:
    for profile in profiles:
        if profile.coordinate == coordinate and profile.diagnostic_version == diagnostic_version:
            return profile
    return None


def _is_strong_baseline(
    version_status: str | None,
    version_confidence_label: str | None,
) -> bool:
    return (
        str(version_status or "").lower() in STRONG_BASELINE_STATUSES
        or str(version_confidence_label or "").lower() in STRONG_BASELINE_LABELS
    )


def _has_prerelease_source(source_versions: Sequence[str] | None) -> bool:
    return any("-" in str(version) for version in source_versions or ())


def _float_value(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0
