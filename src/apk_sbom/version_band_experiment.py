from __future__ import annotations

from dataclasses import asdict, dataclass
import re
from typing import Any, Mapping, Sequence


MIN_ANCHOR_SCORE = 0.30
MIN_HIGHER_BAND_ANCHORS = 2


@dataclass(frozen=True)
class VersionBandTriggerDecision:
    apply: bool
    coordinate: str
    selected_version: str
    selected_band: str | None
    reason_codes: tuple[str, ...]
    blocked_by: tuple[str, ...]
    higher_band_anchors: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def should_downgrade_old_version_steal(
    *,
    coordinate: str,
    selected_version: str,
    sibling_decisions: Sequence[Mapping[str, Any]],
) -> VersionBandTriggerDecision:
    selected_band = version_band(coordinate, selected_version)
    blocked_by: list[str] = []
    reason_codes: list[str] = []
    anchors: list[str] = []

    if coordinate not in {"androidx.appcompat:appcompat", "androidx.core:core"}:
        blocked_by.append("coordinate-not-in-scoped-profile")
    if selected_band is None:
        blocked_by.append("selected-version-band-unknown")
    elif selected_band == "modern":
        blocked_by.append("selected-version-not-old-band")

    if not blocked_by:
        selected_rank = band_rank(selected_band)
        for sibling in sibling_decisions:
            sibling_coordinate = str(sibling.get("coordinate") or "")
            sibling_version = str(sibling.get("selected_version") or "")
            if sibling_coordinate == coordinate:
                continue
            sibling_band = version_band(sibling_coordinate, sibling_version)
            if sibling_band is None or band_rank(sibling_band) <= selected_rank:
                continue
            if float(sibling.get("score") or 0.0) < MIN_ANCHOR_SCORE:
                continue
            anchors.append(
                f"{sibling_coordinate}@{sibling_version}:{sibling_band}"
            )

        if len(anchors) < MIN_HIGHER_BAND_ANCHORS:
            blocked_by.append("insufficient-higher-band-apk-anchors")

    if not blocked_by:
        reason_codes.extend(
            [
                "scoped-old-version-steal-profile",
                "multiple-higher-band-apk-anchors",
                "diagnostic-downgrade-only",
            ]
        )

    return VersionBandTriggerDecision(
        apply=not blocked_by,
        coordinate=coordinate,
        selected_version=selected_version,
        selected_band=selected_band,
        reason_codes=tuple(reason_codes),
        blocked_by=tuple(blocked_by),
        higher_band_anchors=tuple(sorted(anchors)),
    )


def version_band(coordinate: str, version: str) -> str | None:
    artifact = coordinate.split(":", 1)[-1]
    major, minor = major_minor(version)
    if artifact == "appcompat":
        return threshold_band((major, minor), middle=(1, 6), modern=(1, 7))
    if artifact == "core":
        return threshold_band((major, minor), middle=(1, 9), modern=(1, 15))
    if artifact == "fragment":
        return threshold_band((major, minor), middle=(1, 5), modern=(1, 8))
    if artifact.startswith("lifecycle-"):
        return threshold_band((major, minor), middle=(2, 5), modern=(2, 8))
    if artifact == "recyclerview":
        return threshold_band((major, minor), middle=(1, 2), modern=(1, 4))
    return None


def major_minor(version: str) -> tuple[int, int]:
    numbers = [int(value) for value in re.findall(r"\d+", version)[:2]]
    return tuple((numbers + [0, 0])[:2])  # type: ignore[return-value]


def threshold_band(
    version: tuple[int, int],
    *,
    middle: tuple[int, int],
    modern: tuple[int, int],
) -> str:
    if version < middle:
        return "legacy"
    if version < modern:
        return "middle"
    return "modern"


def band_rank(band: str | None) -> int:
    return {"legacy": 0, "middle": 1, "modern": 2}.get(str(band), -1)
