from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ComponentEvidence:
    source: str
    detail: str
    weight: float


@dataclass(frozen=True)
class DetectedLibrary:
    group: str
    artifact: str
    version: str
    confidence: float
    match_type: str
    evidence: list[ComponentEvidence]
    identity_confidence: float | None = None
    identity_confidence_label: str | None = None
    identity_status: str | None = None
    version_confidence: float | None = None
    version_confidence_label: str | None = None
    version_status: str | None = None
    ambiguous_versions: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.identity_confidence is None:
            object.__setattr__(self, "identity_confidence", self.confidence)
        if self.version_confidence is None:
            object.__setattr__(self, "version_confidence", self.confidence)
        if self.identity_status is None:
            object.__setattr__(self, "identity_status", _status_from_match_type(self.match_type))
        if self.version_status is None:
            object.__setattr__(self, "version_status", _status_from_match_type(self.match_type))
        if self.identity_confidence_label is None:
            object.__setattr__(
                self,
                "identity_confidence_label",
                _label_from_status(str(self.identity_status)),
            )
        if self.version_confidence_label is None:
            object.__setattr__(
                self,
                "version_confidence_label",
                _label_from_status(str(self.version_status)),
            )

    @property
    def coordinate(self) -> str:
        return f"{self.group}:{self.artifact}"

    @property
    def purl(self) -> str:
        return f"pkg:maven/{self.group}/{self.artifact}@{self.version}"

    @property
    def bom_ref(self) -> str:
        return self.purl


def _status_from_match_type(value: str) -> str:
    lowered = value.lower()
    if "exact" in lowered:
        return "exact"
    if "likely" in lowered:
        return "likely"
    if "candidate" in lowered:
        return "candidate"
    if "uncertain" in lowered:
        return "uncertain"
    return value


def _label_from_status(value: str) -> str:
    lowered = value.lower()
    if lowered == "exact":
        return "high"
    if lowered == "likely":
        return "medium"
    if lowered == "candidate":
        return "low"
    return "uncertain"
