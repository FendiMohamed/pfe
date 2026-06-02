from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

from apk_sbom.models import DetectedLibrary
from apk_sbom.vulnerability import load_detected_libraries_from_cyclonedx


DEFAULT_SOURCE_VALIDATION_DIR = Path("data/results/source-validation")
GRADLE_MODULE_RE = re.compile(
    r"(?P<group>[A-Za-z0-9_.-]+):"
    r"(?P<artifact>[A-Za-z0-9_.-]+):"
    r"(?P<requested>[^\s()]+)"
    r"(?:\s+->\s+(?P<resolved>[^\s()]+))?"
)


@dataclass(frozen=True)
class GradleDependencyOccurrence:
    coordinate: str
    requested_version: str
    resolved_version: str
    line: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class SourceDependencyEntry:
    coordinate: str
    resolved_versions: list[str]
    requested_versions: list[str]
    occurrences: list[GradleDependencyOccurrence]

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class SourceValidationResult:
    kind: str
    coordinate: str
    version: str
    purl: str
    confidence: float
    match_type: str
    status: str
    source_versions: list[str]
    source_requested_versions: list[str]
    evidence_line: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class SourceValidationSummary:
    sbom_path: str
    dependency_tree_path: str
    source_components: int
    sbom_components: int
    extra_candidates: int
    confirmed: int
    version_mismatches: int
    missing: int
    candidate_confirmed: int
    candidate_version_mismatches: int
    candidate_missing: int
    results: list[SourceValidationResult]

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True)

    def write_json(self, output_path: str | Path) -> Path:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.to_json() + "\n", encoding="utf-8")
        return path

    def write_markdown(self, output_path: str | Path) -> Path:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(build_source_validation_markdown(self), encoding="utf-8")
        return path


@dataclass(frozen=True)
class SourceValidationArtifacts:
    output_dir: str
    validation_json: str
    validation_markdown: str

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True)


def parse_gradle_dependency_tree(text: str) -> dict[str, SourceDependencyEntry]:
    occurrences_by_coordinate: dict[str, list[GradleDependencyOccurrence]] = {}
    for raw_line in text.splitlines():
        match = GRADLE_MODULE_RE.search(raw_line)
        if not match:
            continue

        coordinate = f"{match.group('group')}:{match.group('artifact')}"
        requested_version = match.group("requested").strip()
        resolved_version = (match.group("resolved") or requested_version).strip()
        occurrence = GradleDependencyOccurrence(
            coordinate=coordinate,
            requested_version=requested_version,
            resolved_version=resolved_version,
            line=raw_line.strip(),
        )
        occurrences_by_coordinate.setdefault(coordinate, []).append(occurrence)

    return {
        coordinate: SourceDependencyEntry(
            coordinate=coordinate,
            resolved_versions=sorted(
                {occurrence.resolved_version for occurrence in occurrences},
                key=_version_sort_key,
            ),
            requested_versions=sorted(
                {occurrence.requested_version for occurrence in occurrences},
                key=_version_sort_key,
            ),
            occurrences=occurrences,
        )
        for coordinate, occurrences in sorted(occurrences_by_coordinate.items())
    }


def validate_cyclonedx_against_gradle_tree(
    sbom_path: str | Path,
    dependency_tree_path: str | Path,
    *,
    extra_candidates: list[DetectedLibrary] | None = None,
) -> SourceValidationSummary:
    sbom = Path(sbom_path)
    tree = Path(dependency_tree_path)
    sbom_libraries = load_detected_libraries_from_cyclonedx(sbom)
    source_dependencies = parse_gradle_dependency_tree(tree.read_text(encoding="utf-8"))
    candidates = extra_candidates or []
    results = [
        _validate_library("sbom-component", library, source_dependencies)
        for library in sbom_libraries
    ] + [
        _validate_library("candidate", library, source_dependencies)
        for library in candidates
    ]

    sbom_results = [result for result in results if result.kind == "sbom-component"]
    candidate_results = [result for result in results if result.kind == "candidate"]

    return SourceValidationSummary(
        sbom_path=str(sbom),
        dependency_tree_path=str(tree),
        source_components=len(source_dependencies),
        sbom_components=len(sbom_libraries),
        extra_candidates=len(candidates),
        confirmed=_count_status(sbom_results, "confirmed"),
        version_mismatches=_count_status(sbom_results, "version-mismatch"),
        missing=_count_status(sbom_results, "missing"),
        candidate_confirmed=_count_status(candidate_results, "confirmed"),
        candidate_version_mismatches=_count_status(candidate_results, "version-mismatch"),
        candidate_missing=_count_status(candidate_results, "missing"),
        results=results,
    )


def write_source_validation_report(
    sbom_path: str | Path,
    dependency_tree_path: str | Path,
    *,
    output_dir: str | Path = DEFAULT_SOURCE_VALIDATION_DIR,
    extra_candidates: list[DetectedLibrary] | None = None,
) -> SourceValidationArtifacts:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    summary = validate_cyclonedx_against_gradle_tree(
        sbom_path,
        dependency_tree_path,
        extra_candidates=extra_candidates,
    )
    json_path = summary.write_json(output / "source-validation.json")
    markdown_path = summary.write_markdown(output / "source-validation.md")
    return SourceValidationArtifacts(
        output_dir=str(output),
        validation_json=str(json_path),
        validation_markdown=str(markdown_path),
    )


def parse_maven_component_spec(value: str) -> DetectedLibrary:
    if value.startswith("pkg:maven/"):
        return _parse_purl_component_spec(value)

    if "@" not in value:
        raise ValueError(
            f"expected Maven component as group:artifact@version or pkg:maven/...@version: {value}"
        )
    coordinate, version = value.rsplit("@", maxsplit=1)
    if coordinate.count(":") != 1 or not version:
        raise ValueError(
            f"expected Maven component as group:artifact@version or pkg:maven/...@version: {value}"
        )
    group, artifact = coordinate.split(":", maxsplit=1)
    if not group or not artifact:
        raise ValueError(
            f"expected Maven component as group:artifact@version or pkg:maven/...@version: {value}"
        )
    return DetectedLibrary(
        group=group,
        artifact=artifact,
        version=version,
        confidence=0.0,
        match_type="manual-candidate",
        evidence=[],
    )


def build_source_validation_markdown(summary: SourceValidationSummary) -> str:
    lines = [
        "# Source Dependency Validation",
        "",
        "## Inputs",
        "",
        "| Item | Value |",
        "|---|---|",
        f"| CycloneDX SBOM | `{_escape_markdown_cell(summary.sbom_path)}` |",
        f"| Gradle dependency tree | `{_escape_markdown_cell(summary.dependency_tree_path)}` |",
        f"| Source components parsed | {summary.source_components} |",
        "",
        "## Summary",
        "",
        "| Group | Components | Confirmed | Version mismatch | Missing |",
        "|---|---:|---:|---:|---:|",
        (
            f"| SBOM components | {summary.sbom_components} | {summary.confirmed} | "
            f"{summary.version_mismatches} | {summary.missing} |"
        ),
        (
            f"| Extra candidates | {summary.extra_candidates} | {summary.candidate_confirmed} | "
            f"{summary.candidate_version_mismatches} | {summary.candidate_missing} |"
        ),
        "",
        "## SBOM Component Comparison",
        "",
    ]

    sbom_results = [result for result in summary.results if result.kind == "sbom-component"]
    lines.extend(_result_table(sbom_results, empty_message="No Maven library components were found in the SBOM."))

    candidate_results = [result for result in summary.results if result.kind == "candidate"]
    if candidate_results:
        lines.extend(
            [
                "",
                "## Extra Candidate Comparison",
                "",
            ]
        )
        lines.extend(_result_table(candidate_results, empty_message="No extra candidates were provided."))

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- `confirmed` means the Maven coordinate and selected version are present in the resolved source dependency tree.",
            "- `version-mismatch` means the coordinate is present, but the resolved source version differs from the SBOM version.",
            "- `missing` means the coordinate was not found in the provided dependency tree.",
            "- This validates SBOM identity/version against source dependencies when source is available; it does not prove APK bytecode completeness by itself.",
            "",
        ]
    )
    return "\n".join(lines)


def _validate_library(
    kind: str,
    library: DetectedLibrary,
    source_dependencies: dict[str, SourceDependencyEntry],
) -> SourceValidationResult:
    entry = source_dependencies.get(library.coordinate)
    if not entry:
        return SourceValidationResult(
            kind=kind,
            coordinate=library.coordinate,
            version=library.version,
            purl=library.purl,
            confidence=library.confidence,
            match_type=library.match_type,
            status="missing",
            source_versions=[],
            source_requested_versions=[],
        )

    status = "confirmed" if library.version in entry.resolved_versions else "version-mismatch"
    evidence_line = _first_matching_line(entry, library.version) or entry.occurrences[0].line
    return SourceValidationResult(
        kind=kind,
        coordinate=library.coordinate,
        version=library.version,
        purl=library.purl,
        confidence=library.confidence,
        match_type=library.match_type,
        status=status,
        source_versions=entry.resolved_versions,
        source_requested_versions=entry.requested_versions,
        evidence_line=evidence_line,
    )


def _first_matching_line(entry: SourceDependencyEntry, version: str) -> str | None:
    for occurrence in entry.occurrences:
        if occurrence.resolved_version == version:
            return occurrence.line
    return None


def _count_status(results: list[SourceValidationResult], status: str) -> int:
    return sum(1 for result in results if result.status == status)


def _result_table(results: list[SourceValidationResult], *, empty_message: str) -> list[str]:
    if not results:
        return [empty_message]

    lines = [
        "| Component | SBOM version | Source resolved versions | Result | Match type | Evidence |",
        "|---|---:|---|---|---|---|",
    ]
    for result in results:
        source_versions = ", ".join(result.source_versions) if result.source_versions else "not found"
        evidence = result.evidence_line or "none"
        lines.append(
            "| "
            f"`{_escape_markdown_cell(result.coordinate)}` | "
            f"{_escape_markdown_cell(result.version)} | "
            f"{_escape_markdown_cell(source_versions)} | "
            f"{result.status} | "
            f"{_escape_markdown_cell(result.match_type)} | "
            f"`{_escape_markdown_cell(evidence)}` |"
        )
    return lines


def _parse_purl_component_spec(value: str) -> DetectedLibrary:
    if "@" not in value:
        raise ValueError(f"expected Maven PURL with version: {value}")
    identity, version = value.removeprefix("pkg:maven/").rsplit("@", maxsplit=1)
    if "/" not in identity:
        raise ValueError(f"expected Maven PURL as pkg:maven/group/artifact@version: {value}")
    group, artifact = identity.rsplit("/", maxsplit=1)
    if not group or not artifact or not version:
        raise ValueError(f"expected Maven PURL as pkg:maven/group/artifact@version: {value}")
    return DetectedLibrary(
        group=group,
        artifact=artifact,
        version=version,
        confidence=0.0,
        match_type="manual-candidate",
        evidence=[],
    )


def _version_sort_key(version: str) -> tuple:
    return tuple(int(part) if part.isdigit() else part for part in re.split(r"([0-9]+)", version))


def _escape_markdown_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")
