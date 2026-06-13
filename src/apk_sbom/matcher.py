from __future__ import annotations

import json
import math
import sqlite3
from collections import Counter
from dataclasses import asdict, dataclass, field, replace
from pathlib import Path

import networkx as nx
from packaging.version import InvalidVersion, Version

from apk_sbom.composite_family_shortlist_simulation import (
    PROFILES,
    RECOMMENDED_PROFILE_ID,
    RECOMMENDED_RESCUE_POLICY,
    composite_score,
    should_rescue,
)
from apk_sbom.dex_analyzer import ApkDexAnalysis, analyze_apk_dex
from apk_sbom.maven_downloader import MavenPomDependency
from apk_sbom.models import ComponentEvidence, DetectedLibrary
from apk_sbom.reference_features import DEFAULT_FEATURE_DB_PATH


DEFAULT_PACKAGE_WEIGHT = 0.15
DEFAULT_CLASS_WEIGHT = 0.45
DEFAULT_METHOD_WEIGHT = 0.25
DEFAULT_OPCODE_WEIGHT = 0.15
DEFAULT_DEPENDENCY_WEIGHT = 0.10
DEFAULT_LITERAL_WEIGHT = 0.08
DEFAULT_UNIQUE_VERSION_WEIGHT = 0.12
DEFAULT_API_REFERENCE_WEIGHT = 0.0
DEFAULT_OPCODE_NGRAM_WEIGHT = 0.0
ARTIFACT_FAMILY_CLOSE_SCORE_MARGIN = 0.05
ARTIFACT_FAMILY_VERSION_HINT_SCORE_MARGIN = 0.15
VERSION_DISTINCTIVE_SCORE_MARGIN = 0.06
VERSION_DISTINCTIVE_UNIQUE_ADVANTAGE = 0.04
VERSION_DISTINCTIVE_MAX_RAW_SCORE = 0.75
VERSION_DISAMBIGUATION_IDENTITY_TOLERANCE = 0.13
VERSION_UNIQUE_LITERAL_CONTEXT_SCORE_MARGIN = 0.02
VERSION_UNIQUE_LITERAL_CONTEXT_MIN_RAW_SCORE = 0.35
VERSION_UNIQUE_LITERAL_CONTEXT_MIN_SCORE = 0.10
VERSION_UNIQUE_LITERAL_CONTEXT_MIN_ADVANTAGE = 0.05
VERSION_UNIQUE_LITERAL_CONTEXT_MIN_MATCHES = 2
COMPOSITE_FAMILY_SHORTLIST_MARGIN = 0.10
FEATURE_EQUIVALENT_VERSION_SCORE_MARGIN = 0.001
FEATURE_EQUIVALENT_VERSION_SIGNAL_TOLERANCE = 0.001
VERSION_NEAR_TIE_SCORE_MARGIN = 0.006
VERSION_NEAR_TIE_MIN_SCORE = 0.35
POM_COHERENCE_SCORE_MARGIN = 0.06
POM_COHERENCE_MAX_RAW_SCORE = 0.75
POM_COHERENCE_MIN_RAW_SCORE = 0.35
APP_ERA_COHERENCE_SCORE_MARGIN = 0.12
APP_ERA_COHERENCE_MIN_RAW_SCORE = 0.30
APP_ERA_COHERENCE_IDENTITY_TOLERANCE = 0.18
APP_ERA_COHERENCE_UNSUPPORTED_MAX_SCORE = 0.65
LIFECYCLE_RUNTIME_ARTIFACTS = {"lifecycle-runtime", "lifecycle-runtime-android"}
LIFECYCLE_VIEWMODEL_ARTIFACTS = {"lifecycle-viewmodel", "lifecycle-viewmodel-android"}


@dataclass(frozen=True)
class ArtifactFamilyRule:
    family_id: str
    preference_rank: int
    reason: str


@dataclass(frozen=True)
class AppEraCoherenceRule:
    family_id: str
    coordinates: frozenset[str]
    minimum_support: int = 2
    score_margin: float = APP_ERA_COHERENCE_SCORE_MARGIN
    unsupported_max_score: float = APP_ERA_COHERENCE_UNSUPPORTED_MAX_SCORE
    requires_support_for_candidate: bool = False


ARTIFACT_FAMILY_RULES: dict[tuple[str, str], ArtifactFamilyRule] = {
    (
        "com.squareup.okio",
        "okio",
    ): ArtifactFamilyRule(
        family_id="com.squareup.okio:okio-family",
        preference_rank=0,
        reason="Okio metadata/legacy artifacts can share bytecode evidence with JVM artifacts.",
    ),
    (
        "com.squareup.okio",
        "okio-jvm",
    ): ArtifactFamilyRule(
        family_id="com.squareup.okio:okio-family",
        preference_rank=10,
        reason="APK DEX bytecode should prefer the JVM artifact when Okio family scores are close.",
    ),
    (
        "com.squareup.okhttp3",
        "okhttp",
    ): ArtifactFamilyRule(
        family_id="com.squareup.okhttp3:okhttp-family",
        preference_rank=0,
        reason="OkHttp public and Android target artifacts can overlap for KMP-era releases.",
    ),
    (
        "com.squareup.okhttp3",
        "okhttp-android",
    ): ArtifactFamilyRule(
        family_id="com.squareup.okhttp3:okhttp-family",
        preference_rank=10,
        reason="APK DEX bytecode should prefer the Android target artifact when OkHttp family scores are close.",
    ),
    (
        "androidx.lifecycle",
        "lifecycle-runtime",
    ): ArtifactFamilyRule(
        family_id="androidx.lifecycle:lifecycle-runtime-family",
        preference_rank=10,
        reason=(
            "Gradle source trees usually report the public Lifecycle runtime coordinate; "
            "Android target variants are overlapping bytecode artifacts."
        ),
    ),
    (
        "androidx.lifecycle",
        "lifecycle-runtime-android",
    ): ArtifactFamilyRule(
        family_id="androidx.lifecycle:lifecycle-runtime-family",
        preference_rank=0,
        reason=(
            "Android target variants can share bytecode evidence with the public "
            "Lifecycle runtime coordinate."
        ),
    ),
    (
        "androidx.lifecycle",
        "lifecycle-viewmodel",
    ): ArtifactFamilyRule(
        family_id="androidx.lifecycle:lifecycle-viewmodel-family",
        preference_rank=10,
        reason=(
            "Gradle source trees usually report the public Lifecycle ViewModel coordinate; "
            "Android target variants are overlapping bytecode artifacts."
        ),
    ),
    (
        "androidx.lifecycle",
        "lifecycle-viewmodel-android",
    ): ArtifactFamilyRule(
        family_id="androidx.lifecycle:lifecycle-viewmodel-family",
        preference_rank=0,
        reason=(
            "Android target variants can share bytecode evidence with the public "
            "Lifecycle ViewModel coordinate."
        ),
    ),
}

COMPOSE_VERSION_COHERENCE_COORDINATES = frozenset(
    {
        "androidx.compose.foundation:foundation-android",
        "androidx.compose.runtime:runtime-android",
        "androidx.compose.ui:ui-android",
        "androidx.compose.ui:ui-tooling-preview-android",
    }
)

APP_ERA_COHERENCE_RULES: dict[str, AppEraCoherenceRule] = {
    coordinate: AppEraCoherenceRule(
        family_id="androidx.compose",
        coordinates=COMPOSE_VERSION_COHERENCE_COORDINATES,
        requires_support_for_candidate=(
            coordinate == "androidx.compose.runtime:runtime-android"
        ),
    )
    for coordinate in COMPOSE_VERSION_COHERENCE_COORDINATES
}


@dataclass(frozen=True)
class FeatureSet:
    packages: set[str]
    classes: set[str]
    methods: set[str]
    opcode_histogram: dict[str, int] = field(default_factory=dict)
    opcode_ngrams: dict[str, int] = field(default_factory=dict)
    class_dependencies: set[tuple[str, str, str]] = field(default_factory=set)
    dependency_shape: dict[str, int] = field(default_factory=dict)
    string_literals: set[str] = field(default_factory=set)
    api_references: set[str] = field(default_factory=set)
    basic_block_opcode_fingerprints: dict[str, int] = field(default_factory=dict)
    call_chain_opcode_fingerprints: dict[str, int] = field(default_factory=dict)
    class_neighbor_summaries: dict[str, int] = field(default_factory=dict)
    field_operation_sequences: dict[str, int] = field(default_factory=dict)
    literal_context_features: set[str] = field(default_factory=set)

    @property
    def packages_count(self) -> int:
        return len(self.packages)

    @property
    def classes_count(self) -> int:
        return len(self.classes)

    @property
    def methods_count(self) -> int:
        return len(self.methods)

    @property
    def distinct_opcodes_count(self) -> int:
        return len(self.opcode_histogram)

    @property
    def opcode_total(self) -> int:
        return sum(self.opcode_histogram.values())

    @property
    def distinct_opcode_ngrams_count(self) -> int:
        return len(self.opcode_ngrams)

    @property
    def opcode_ngram_total(self) -> int:
        return sum(self.opcode_ngrams.values())

    @property
    def dependency_edges_count(self) -> int:
        return len(self.class_dependencies)

    @property
    def dependency_shape_bins_count(self) -> int:
        return len(self.dependency_shape)

    @property
    def string_literals_count(self) -> int:
        return len(self.string_literals)

    @property
    def api_references_count(self) -> int:
        return len(self.api_references)

    @property
    def basic_block_fingerprints_count(self) -> int:
        return len(self.basic_block_opcode_fingerprints)

    @property
    def basic_block_fingerprints_total(self) -> int:
        return sum(self.basic_block_opcode_fingerprints.values())

    @property
    def call_chain_fingerprints_count(self) -> int:
        return len(self.call_chain_opcode_fingerprints)

    @property
    def call_chain_fingerprints_total(self) -> int:
        return sum(self.call_chain_opcode_fingerprints.values())

    @property
    def class_neighbor_summaries_count(self) -> int:
        return len(self.class_neighbor_summaries)

    @property
    def class_neighbor_summaries_total(self) -> int:
        return sum(self.class_neighbor_summaries.values())

    @property
    def field_operation_sequences_count(self) -> int:
        return len(self.field_operation_sequences)

    @property
    def field_operation_sequences_total(self) -> int:
        return sum(self.field_operation_sequences.values())

    @property
    def literal_context_features_count(self) -> int:
        return len(self.literal_context_features)


@dataclass(frozen=True)
class ReferenceComponentFeatures:
    component_id: int
    coordinate: str
    group_id: str
    artifact_id: str
    version: str
    purl: str
    features: FeatureSet
    maven_dependencies: list[MavenPomDependency] = field(default_factory=list)


@dataclass(frozen=True)
class OverlapEvidence:
    matched_packages: int
    reference_packages: int
    apk_packages: int
    package_score: float
    matched_classes: int
    reference_classes: int
    apk_classes: int
    class_score: float
    matched_methods: int
    reference_methods: int
    apk_methods: int
    method_score: float
    shared_opcodes: int
    reference_distinct_opcodes: int
    reference_opcode_total: int
    apk_distinct_opcodes: int
    apk_opcode_total: int
    opcode_score: float
    shared_opcode_ngrams: int
    reference_distinct_opcode_ngrams: int
    reference_opcode_ngram_total: int
    apk_distinct_opcode_ngrams: int
    apk_opcode_ngram_total: int
    opcode_ngram_score: float
    matched_dependency_edges: int
    reference_dependency_edges: int
    apk_dependency_edges: int
    dependency_edge_score: float
    reference_dependency_shape_bins: int
    apk_dependency_shape_bins: int
    dependency_shape_score: float
    dependency_score: float
    matched_string_literals: int
    reference_string_literals: int
    apk_string_literals: int
    literal_score: float
    matched_api_references: int
    reference_api_references: int
    apk_api_references: int
    api_reference_score: float
    matched_unique_classes: int
    reference_unique_classes: int
    unique_class_score: float
    matched_unique_methods: int
    reference_unique_methods: int
    unique_method_score: float
    matched_unique_literals: int
    reference_unique_literals: int
    unique_literal_score: float
    unique_version_score: float
    matched_unique_literal_context_features: int = 0
    reference_unique_literal_context_features: int = 0
    unique_literal_context_score: float = 0.0


@dataclass(frozen=True)
class MatchCandidate:
    coordinate: str
    group_id: str
    artifact_id: str
    version: str
    purl: str
    score: float
    evidence: OverlapEvidence
    maven_dependencies: list[MavenPomDependency] = field(default_factory=list)


@dataclass(frozen=True)
class VersionAlternative:
    version: str
    purl: str
    score: float


@dataclass(frozen=True)
class VersionDecision:
    coordinate: str
    group_id: str
    artifact_id: str
    selected_version: str
    purl: str
    score: float
    confidence: float
    confidence_label: str
    version_decision: str
    gap_to_next: float
    reference_versions_considered: int
    evidence: OverlapEvidence
    alternatives: list[VersionAlternative]
    identity_confidence: float | None = None
    identity_confidence_label: str | None = None
    identity_status: str | None = None
    version_confidence: float | None = None
    version_confidence_label: str | None = None
    version_status: str | None = None
    version_selection_reason: str | None = None
    version_ambiguity_reason: str | None = None
    ambiguous_versions: list[VersionAlternative] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.identity_confidence is None:
            object.__setattr__(self, "identity_confidence", self.confidence)
        if self.version_confidence is None:
            object.__setattr__(self, "version_confidence", self.confidence)
        if self.identity_status is None:
            object.__setattr__(self, "identity_status", self.version_decision)
        if self.identity_confidence_label is None:
            object.__setattr__(self, "identity_confidence_label", self.confidence_label)
        if self.version_status is None:
            object.__setattr__(self, "version_status", self.version_decision)
        if self.version_confidence_label is None:
            object.__setattr__(self, "version_confidence_label", self.confidence_label)


@dataclass(frozen=True)
class MatchSummary:
    apk_path: str
    db_path: str
    dex_files_analyzed: int
    dex_files_failed: int
    apk_packages: int
    apk_classes: int
    apk_methods: int
    apk_distinct_opcodes: int
    apk_opcode_total: int
    apk_distinct_opcode_ngrams: int
    apk_opcode_ngram_total: int
    apk_dependency_edges: int
    apk_dependency_shape_bins: int
    apk_string_literals: int
    apk_api_references: int
    package_weight: float
    class_weight: float
    method_weight: float
    opcode_weight: float
    dependency_weight: float
    literal_weight: float
    unique_version_weight: float
    api_reference_weight: float
    opcode_ngram_weight: float
    min_score: float
    candidates: list[MatchCandidate]
    decisions: list[VersionDecision]
    inert_multiscale_features: dict[str, object] = field(default_factory=dict)
    version_unique_literal_context_reranker_enabled: bool = True
    composite_family_shortlist_enabled: bool = True
    composite_family_shortlist_summary: dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True)


def match_apk_to_reference_db(
    apk_path: str | Path,
    *,
    db_path: str | Path = DEFAULT_FEATURE_DB_PATH,
    coordinate: str | None = None,
    top: int | None = 10,
    min_score: float = 0.05,
    package_weight: float = DEFAULT_PACKAGE_WEIGHT,
    class_weight: float = DEFAULT_CLASS_WEIGHT,
    method_weight: float = DEFAULT_METHOD_WEIGHT,
    opcode_weight: float = DEFAULT_OPCODE_WEIGHT,
    dependency_weight: float = DEFAULT_DEPENDENCY_WEIGHT,
    literal_weight: float = DEFAULT_LITERAL_WEIGHT,
    unique_version_weight: float = DEFAULT_UNIQUE_VERSION_WEIGHT,
    api_reference_weight: float = DEFAULT_API_REFERENCE_WEIGHT,
    opcode_ngram_weight: float = DEFAULT_OPCODE_NGRAM_WEIGHT,
    enable_version_unique_literal_context_reranker: bool = True,
    enable_composite_family_shortlist: bool = True,
    composite_family_shortlist_margin: float = COMPOSITE_FAMILY_SHORTLIST_MARGIN,
    enable_reference_package_prefilter: bool = False,
    reference_package_prefilter_min_overlap: int = 1,
    reference_package_prefilter_limit: int | None = None,
) -> MatchSummary:
    db = Path(db_path)
    if not db.exists():
        raise FileNotFoundError(f"Reference feature DB not found: {db}")

    analysis = analyze_apk_dex(apk_path, include_members=True)
    apk_features = feature_set_from_apk_analysis(analysis)

    with sqlite3.connect(db) as connection:
        component_ids = None
        if enable_reference_package_prefilter:
            component_ids = prefilter_component_ids_by_package_overlap(
                connection,
                apk_features.packages,
                coordinate=coordinate,
                min_overlap=reference_package_prefilter_min_overlap,
                limit=reference_package_prefilter_limit,
            )
        references = load_reference_components(
            connection,
            coordinate=coordinate,
            component_ids=component_ids,
        )
    shortlist_summary = build_disabled_composite_family_shortlist_summary(references)
    if enable_composite_family_shortlist:
        references, shortlist_summary = shortlist_reference_families(
            apk_features,
            references,
            margin=composite_family_shortlist_margin,
        )

    references_by_coordinate: dict[str, list[ReferenceComponentFeatures]] = {}
    for reference in references:
        references_by_coordinate.setdefault(reference.coordinate, []).append(reference)

    candidates = []
    for reference in references:
        siblings = [
            item.features
            for item in references_by_coordinate.get(reference.coordinate, [])
            if item.component_id != reference.component_id
        ]
        candidates.append(
            score_reference_component(
                apk_features,
                reference,
                sibling_features=siblings,
                package_weight=package_weight,
                class_weight=class_weight,
                method_weight=method_weight,
                opcode_weight=opcode_weight,
                dependency_weight=dependency_weight,
                literal_weight=literal_weight,
                unique_version_weight=unique_version_weight,
                api_reference_weight=api_reference_weight,
                opcode_ngram_weight=opcode_ngram_weight,
            )
        )
    candidates = [candidate for candidate in candidates if candidate.score >= min_score]
    candidates.sort(
        key=lambda item: (
            item.score,
            item.evidence.class_score,
            item.evidence.method_score,
            item.evidence.dependency_score,
            item.evidence.unique_version_score,
            item.evidence.literal_score,
            item.evidence.opcode_score,
            item.evidence.package_score,
            item.coordinate,
            item.version,
        ),
        reverse=True,
    )
    decisions = build_version_decisions(
        candidates,
        enable_version_unique_literal_context_reranker=(
            enable_version_unique_literal_context_reranker
        ),
    )
    if top is not None:
        candidates = candidates[:top]

    return MatchSummary(
        apk_path=str(apk_path),
        db_path=str(db),
        dex_files_analyzed=analysis.dex_files_analyzed,
        dex_files_failed=analysis.dex_files_failed,
        apk_packages=apk_features.packages_count,
        apk_classes=apk_features.classes_count,
        apk_methods=apk_features.methods_count,
        apk_distinct_opcodes=apk_features.distinct_opcodes_count,
        apk_opcode_total=apk_features.opcode_total,
        apk_distinct_opcode_ngrams=apk_features.distinct_opcode_ngrams_count,
        apk_opcode_ngram_total=apk_features.opcode_ngram_total,
        apk_dependency_edges=apk_features.dependency_edges_count,
        apk_dependency_shape_bins=apk_features.dependency_shape_bins_count,
        apk_string_literals=apk_features.string_literals_count,
        apk_api_references=apk_features.api_references_count,
        package_weight=package_weight,
        class_weight=class_weight,
        method_weight=method_weight,
        opcode_weight=opcode_weight,
        dependency_weight=dependency_weight,
        literal_weight=literal_weight,
        unique_version_weight=unique_version_weight,
        api_reference_weight=api_reference_weight,
        opcode_ngram_weight=opcode_ngram_weight,
        min_score=min_score,
        candidates=candidates,
        decisions=decisions,
        inert_multiscale_features=build_inert_multiscale_feature_summary(
            apk_features,
            references,
        ),
        version_unique_literal_context_reranker_enabled=(
            enable_version_unique_literal_context_reranker
        ),
        composite_family_shortlist_enabled=enable_composite_family_shortlist,
        composite_family_shortlist_summary=shortlist_summary,
    )


def feature_set_from_apk_analysis(analysis: ApkDexAnalysis) -> FeatureSet:
    opcode_counter: Counter[str] = Counter()
    opcode_ngram_counter: Counter[str] = Counter()
    dependency_shape_counter: Counter[str] = Counter()
    basic_block_counter: Counter[str] = Counter()
    call_chain_counter: Counter[str] = Counter()
    class_neighbor_counter: Counter[str] = Counter()
    field_operation_counter: Counter[str] = Counter()
    for dex_file in analysis.dex_files:
        opcode_counter.update(dex_file.opcode_histogram)
        opcode_ngram_counter.update(dex_file.opcode_ngrams)
        dependency_shape_counter.update(dex_file.dependency_shape)
        basic_block_counter.update(dex_file.basic_block_opcode_fingerprints)
        call_chain_counter.update(dex_file.call_chain_opcode_fingerprints)
        class_neighbor_counter.update(dex_file.class_neighbor_summaries)
        field_operation_counter.update(dex_file.field_operation_sequences)

    return FeatureSet(
        packages=set(analysis.packages),
        classes={
            class_descriptor
            for dex_file in analysis.dex_files
            for class_descriptor in dex_file.class_descriptors
        },
        methods={
            method_signature
            for dex_file in analysis.dex_files
            for method_signature in dex_file.method_signatures
        },
        opcode_histogram=dict(opcode_counter),
        opcode_ngrams=dict(opcode_ngram_counter),
        class_dependencies={
            (edge.source, edge.target, edge.kind)
            for dex_file in analysis.dex_files
            for edge in dex_file.class_dependencies
        },
        dependency_shape=dict(dependency_shape_counter),
        string_literals={
            literal
            for dex_file in analysis.dex_files
            for literal in dex_file.string_literals
        },
        api_references={
            reference
            for dex_file in analysis.dex_files
            for reference in dex_file.api_references
        },
        basic_block_opcode_fingerprints=dict(basic_block_counter),
        call_chain_opcode_fingerprints=dict(call_chain_counter),
        class_neighbor_summaries=dict(class_neighbor_counter),
        field_operation_sequences=dict(field_operation_counter),
        literal_context_features={
            feature
            for dex_file in analysis.dex_files
            for feature in dex_file.literal_context_features
        },
    )


def build_inert_multiscale_feature_summary(
    apk_features: FeatureSet,
    references: list[ReferenceComponentFeatures],
) -> dict[str, object]:
    return {
        "scoring_status": "disabled",
        "scoring_note": (
            "Phase 3 features are extracted for diagnostics and controlled experiments only; "
            "matcher scoring, selected versions, vulnerability classification, and SBOM "
            "component selection do not consume them."
        ),
        "apk": {
            "basic_block_opcode_fingerprints": {
                "distinct": apk_features.basic_block_fingerprints_count,
                "total": apk_features.basic_block_fingerprints_total,
            },
            "call_chain_opcode_fingerprints": {
                "distinct": apk_features.call_chain_fingerprints_count,
                "total": apk_features.call_chain_fingerprints_total,
            },
            "class_neighbor_summaries": {
                "distinct": apk_features.class_neighbor_summaries_count,
                "total": apk_features.class_neighbor_summaries_total,
            },
            "field_operation_sequences": {
                "distinct": apk_features.field_operation_sequences_count,
                "total": apk_features.field_operation_sequences_total,
            },
            "literal_context_features": {
                "distinct": apk_features.literal_context_features_count,
                "total": apk_features.literal_context_features_count,
            },
        },
        "reference": _reference_multiscale_feature_availability(references),
    }


def build_disabled_composite_family_shortlist_summary(
    references: list[ReferenceComponentFeatures],
) -> dict[str, object]:
    coordinate_count = len({reference.coordinate for reference in references})
    return {
        "scoring_status": "disabled",
        "profile_id": RECOMMENDED_PROFILE_ID,
        "rescue_policy": RECOMMENDED_RESCUE_POLICY,
        "margin": COMPOSITE_FAMILY_SHORTLIST_MARGIN,
        "reference_rows_before": len(references),
        "reference_rows_retained": len(references),
        "reference_rows_removed": 0,
        "coordinate_families_before": coordinate_count,
        "coordinate_families_retained": coordinate_count,
        "coordinate_families_removed": 0,
        "coordinate_families_rescued": 0,
    }


def shortlist_reference_families(
    apk_features: FeatureSet,
    references: list[ReferenceComponentFeatures],
    *,
    margin: float = COMPOSITE_FAMILY_SHORTLIST_MARGIN,
) -> tuple[list[ReferenceComponentFeatures], dict[str, object]]:
    if not references:
        return [], {
            **build_disabled_composite_family_shortlist_summary([]),
            "scoring_status": "enabled",
            "margin": margin,
        }

    by_coordinate: dict[str, list[ReferenceComponentFeatures]] = {}
    for reference in references:
        by_coordinate.setdefault(reference.coordinate, []).append(reference)

    family_rows = []
    for coordinate, family_references in by_coordinate.items():
        evidence_rows = [
            _composite_family_reference_evidence(apk_features, reference)
            for reference in family_references
        ]
        family_rows.append(
            {
                "coordinate": coordinate,
                "reference_versions": len(family_references),
                "composite_score": max(
                    (float(row["composite_score"]) for row in evidence_rows),
                    default=0.0,
                ),
                "rescued": any(bool(row["rescued"]) for row in evidence_rows),
            }
        )

    best_score = max((float(row["composite_score"]) for row in family_rows), default=0.0)
    retained_coordinates = {
        str(row["coordinate"])
        for row in family_rows
        if float(row["composite_score"]) + margin >= best_score or bool(row["rescued"])
    }
    retained_references = [
        reference for reference in references if reference.coordinate in retained_coordinates
    ]
    removed_family_rows = [
        row for row in family_rows if row["coordinate"] not in retained_coordinates
    ]
    rescued_coordinates = {
        str(row["coordinate"])
        for row in family_rows
        if row["coordinate"] in retained_coordinates and bool(row["rescued"])
    }
    return retained_references, {
        "scoring_status": "enabled",
        "profile_id": RECOMMENDED_PROFILE_ID,
        "rescue_policy": RECOMMENDED_RESCUE_POLICY,
        "margin": margin,
        "best_composite_score": round(best_score, 6),
        "reference_rows_before": len(references),
        "reference_rows_retained": len(retained_references),
        "reference_rows_removed": len(references) - len(retained_references),
        "reference_row_reduction_ratio": round(
            (len(references) - len(retained_references)) / len(references),
            6,
        ),
        "coordinate_families_before": len(by_coordinate),
        "coordinate_families_retained": len(retained_coordinates),
        "coordinate_families_removed": len(removed_family_rows),
        "coordinate_families_rescued": len(rescued_coordinates),
        "top_removed_coordinates": [
            {
                "coordinate": str(row["coordinate"]),
                "reference_versions": int(row["reference_versions"]),
                "composite_score": round(float(row["composite_score"]), 6),
            }
            for row in sorted(
                removed_family_rows,
                key=lambda item: (
                    int(item["reference_versions"]),
                    str(item["coordinate"]),
                ),
                reverse=True,
            )[:15]
        ],
    }


def _composite_family_reference_evidence(
    apk_features: FeatureSet,
    reference: ReferenceComponentFeatures,
) -> dict[str, object]:
    package_matches = apk_features.packages & reference.features.packages
    class_matches = apk_features.classes & reference.features.classes
    method_matches = apk_features.methods & reference.features.methods
    dependency_matches = apk_features.class_dependencies & reference.features.class_dependencies
    literal_matches = apk_features.string_literals & reference.features.string_literals
    dependency_edge_score = _coverage_score(
        dependency_matches,
        reference.features.class_dependencies,
    )
    row = {
        "package_score": _coverage_score(package_matches, reference.features.packages),
        "class_score": _coverage_score(class_matches, reference.features.classes),
        "method_score": _coverage_score(method_matches, reference.features.methods),
        "dependency_score": (
            0.65 * dependency_edge_score
            + 0.35 * _dependency_shape_similarity(apk_features, reference.features)
        ),
        "literal_score": _coverage_score(literal_matches, reference.features.string_literals),
        "matched_classes": len(class_matches),
        "matched_methods": len(method_matches),
        "matched_dependency_edges": len(dependency_matches),
        "matched_string_literals": len(literal_matches),
    }
    return {
        **row,
        "composite_score": composite_score(row, _composite_family_profile_weights()),
        "rescued": should_rescue(row, RECOMMENDED_RESCUE_POLICY),
    }


def _composite_family_profile_weights() -> dict[str, float]:
    return next(
        dict(profile["weights"])
        for profile in PROFILES
        if profile["profile_id"] == RECOMMENDED_PROFILE_ID
    )


def _reference_multiscale_feature_availability(
    references: list[ReferenceComponentFeatures],
) -> dict[str, dict[str, int]]:
    return {
        "basic_block_opcode_fingerprints": _counter_feature_availability(
            [reference.features.basic_block_opcode_fingerprints for reference in references]
        ),
        "call_chain_opcode_fingerprints": _counter_feature_availability(
            [reference.features.call_chain_opcode_fingerprints for reference in references]
        ),
        "class_neighbor_summaries": _counter_feature_availability(
            [reference.features.class_neighbor_summaries for reference in references]
        ),
        "field_operation_sequences": _counter_feature_availability(
            [reference.features.field_operation_sequences for reference in references]
        ),
        "literal_context_features": _set_feature_availability(
            [reference.features.literal_context_features for reference in references]
        ),
    }


def _counter_feature_availability(items: list[dict[str, int]]) -> dict[str, int]:
    distinct_features: set[str] = set()
    total_observations = 0
    components_with_features = 0
    for item in items:
        if item:
            components_with_features += 1
        distinct_features.update(item)
        total_observations += sum(item.values())
    return {
        "components_with_features": components_with_features,
        "distinct": len(distinct_features),
        "total": total_observations,
    }


def _set_feature_availability(items: list[set[str]]) -> dict[str, int]:
    distinct_features: set[str] = set()
    components_with_features = 0
    for item in items:
        if item:
            components_with_features += 1
        distinct_features.update(item)
    return {
        "components_with_features": components_with_features,
        "distinct": len(distinct_features),
        "total": len(distinct_features),
    }


def load_reference_components(
    connection: sqlite3.Connection,
    *,
    coordinate: str | None = None,
    component_ids: set[int] | None = None,
) -> list[ReferenceComponentFeatures]:
    if component_ids is not None and not component_ids:
        rows = []
    elif component_ids is None:
        rows = connection.execute(
            """
            SELECT id, coordinate, group_id, artifact_id, version, purl
            FROM components
            WHERE (? IS NULL OR coordinate = ?)
            ORDER BY coordinate, version
            """,
            (coordinate, coordinate),
        ).fetchall()
    else:
        placeholders = ",".join("?" for _ in component_ids)
        rows = connection.execute(
            f"""
            SELECT id, coordinate, group_id, artifact_id, version, purl
            FROM components
            WHERE id IN ({placeholders})
              AND (? IS NULL OR coordinate = ?)
            ORDER BY coordinate, version
            """,
            (*sorted(component_ids), coordinate, coordinate),
        ).fetchall()

    return [
        ReferenceComponentFeatures(
            component_id=int(row[0]),
            coordinate=str(row[1]),
            group_id=str(row[2]),
            artifact_id=str(row[3]),
            version=str(row[4]),
            purl=str(row[5]),
            features=_load_component_feature_set(connection, int(row[0])),
            maven_dependencies=_load_maven_dependencies(connection, int(row[0])),
        )
        for row in rows
    ]


def score_reference_component(
    apk_features: FeatureSet,
    reference: ReferenceComponentFeatures,
    *,
    sibling_features: list[FeatureSet] | None = None,
    package_weight: float = DEFAULT_PACKAGE_WEIGHT,
    class_weight: float = DEFAULT_CLASS_WEIGHT,
    method_weight: float = DEFAULT_METHOD_WEIGHT,
    opcode_weight: float = DEFAULT_OPCODE_WEIGHT,
    dependency_weight: float = DEFAULT_DEPENDENCY_WEIGHT,
    literal_weight: float = DEFAULT_LITERAL_WEIGHT,
    unique_version_weight: float = DEFAULT_UNIQUE_VERSION_WEIGHT,
    api_reference_weight: float = DEFAULT_API_REFERENCE_WEIGHT,
    opcode_ngram_weight: float = DEFAULT_OPCODE_NGRAM_WEIGHT,
) -> MatchCandidate:
    package_matches = apk_features.packages & reference.features.packages
    class_matches = apk_features.classes & reference.features.classes
    method_matches = apk_features.methods & reference.features.methods

    package_score = _coverage_score(package_matches, reference.features.packages)
    class_score = _coverage_score(class_matches, reference.features.classes)
    method_score = _coverage_score(method_matches, reference.features.methods)
    opcode_score = _cosine_similarity(
        apk_features.opcode_histogram,
        reference.features.opcode_histogram,
    )
    opcode_ngram_score = (
        _cosine_similarity(
            apk_features.opcode_ngrams,
            reference.features.opcode_ngrams,
        )
        if opcode_ngram_weight > 0
        else 0.0
    )
    dependency_edge_matches = apk_features.class_dependencies & reference.features.class_dependencies
    dependency_edge_score = _coverage_score(
        dependency_edge_matches,
        reference.features.class_dependencies,
    )
    dependency_shape_score = _dependency_shape_similarity(apk_features, reference.features)
    dependency_score = (0.65 * dependency_edge_score) + (0.35 * dependency_shape_score)
    literal_matches = apk_features.string_literals & reference.features.string_literals
    literal_score = _coverage_score(literal_matches, reference.features.string_literals)
    api_reference_matches = apk_features.api_references & reference.features.api_references
    api_reference_score = _coverage_score(
        api_reference_matches,
        reference.features.api_references,
    )
    unique_features = _version_unique_features(reference.features, sibling_features or [])
    unique_class_matches = apk_features.classes & unique_features.classes
    unique_method_matches = apk_features.methods & unique_features.methods
    unique_literal_matches = apk_features.string_literals & unique_features.string_literals
    unique_literal_context_matches = (
        apk_features.literal_context_features & unique_features.literal_context_features
    )
    unique_class_score = _coverage_score(unique_class_matches, unique_features.classes)
    unique_method_score = _coverage_score(unique_method_matches, unique_features.methods)
    unique_literal_score = _coverage_score(unique_literal_matches, unique_features.string_literals)
    unique_literal_context_score = _coverage_score(
        unique_literal_context_matches,
        unique_features.literal_context_features,
    )
    unique_version_score = _weighted_score(
        [
            (unique_class_score, 0.35, bool(unique_features.classes)),
            (unique_method_score, 0.45, bool(unique_features.methods)),
            (unique_literal_score, 0.20, bool(unique_features.string_literals)),
        ]
    )
    total_weight = (
        package_weight
        + class_weight
        + method_weight
        + opcode_weight
        + dependency_weight
        + literal_weight
        + unique_version_weight
        + api_reference_weight
        + opcode_ngram_weight
    )
    if total_weight <= 0:
        raise ValueError("At least one matcher weight must be positive")

    score = (
        package_weight * package_score
        + class_weight * class_score
        + method_weight * method_score
        + opcode_weight * opcode_score
        + dependency_weight * dependency_score
        + literal_weight * literal_score
        + unique_version_weight * unique_version_score
        + api_reference_weight * api_reference_score
        + opcode_ngram_weight * opcode_ngram_score
    ) / total_weight

    return MatchCandidate(
        coordinate=reference.coordinate,
        group_id=reference.group_id,
        artifact_id=reference.artifact_id,
        version=reference.version,
        purl=reference.purl,
        score=round(score, 6),
        maven_dependencies=reference.maven_dependencies,
        evidence=OverlapEvidence(
            matched_packages=len(package_matches),
            reference_packages=reference.features.packages_count,
            apk_packages=apk_features.packages_count,
            package_score=round(package_score, 6),
            matched_classes=len(class_matches),
            reference_classes=reference.features.classes_count,
            apk_classes=apk_features.classes_count,
            class_score=round(class_score, 6),
            matched_methods=len(method_matches),
            reference_methods=reference.features.methods_count,
            apk_methods=apk_features.methods_count,
            method_score=round(method_score, 6),
            shared_opcodes=_shared_key_count(
                apk_features.opcode_histogram,
                reference.features.opcode_histogram,
            ),
            reference_distinct_opcodes=reference.features.distinct_opcodes_count,
            reference_opcode_total=reference.features.opcode_total,
            apk_distinct_opcodes=apk_features.distinct_opcodes_count,
            apk_opcode_total=apk_features.opcode_total,
            opcode_score=round(opcode_score, 6),
            shared_opcode_ngrams=_shared_key_count(
                apk_features.opcode_ngrams,
                reference.features.opcode_ngrams,
            )
            if opcode_ngram_weight > 0
            else 0,
            reference_distinct_opcode_ngrams=reference.features.distinct_opcode_ngrams_count,
            reference_opcode_ngram_total=reference.features.opcode_ngram_total,
            apk_distinct_opcode_ngrams=apk_features.distinct_opcode_ngrams_count,
            apk_opcode_ngram_total=apk_features.opcode_ngram_total,
            opcode_ngram_score=round(opcode_ngram_score, 6),
            matched_dependency_edges=len(dependency_edge_matches),
            reference_dependency_edges=reference.features.dependency_edges_count,
            apk_dependency_edges=apk_features.dependency_edges_count,
            dependency_edge_score=round(dependency_edge_score, 6),
            reference_dependency_shape_bins=reference.features.dependency_shape_bins_count,
            apk_dependency_shape_bins=apk_features.dependency_shape_bins_count,
            dependency_shape_score=round(dependency_shape_score, 6),
            dependency_score=round(dependency_score, 6),
            matched_string_literals=len(literal_matches),
            reference_string_literals=reference.features.string_literals_count,
            apk_string_literals=apk_features.string_literals_count,
            literal_score=round(literal_score, 6),
            matched_api_references=len(api_reference_matches),
            reference_api_references=reference.features.api_references_count,
            apk_api_references=apk_features.api_references_count,
            api_reference_score=round(api_reference_score, 6),
            matched_unique_classes=len(unique_class_matches),
            reference_unique_classes=unique_features.classes_count,
            unique_class_score=round(unique_class_score, 6),
            matched_unique_methods=len(unique_method_matches),
            reference_unique_methods=unique_features.methods_count,
            unique_method_score=round(unique_method_score, 6),
            matched_unique_literals=len(unique_literal_matches),
            reference_unique_literals=unique_features.string_literals_count,
            unique_literal_score=round(unique_literal_score, 6),
            unique_version_score=round(unique_version_score, 6),
            matched_unique_literal_context_features=len(unique_literal_context_matches),
            reference_unique_literal_context_features=(
                unique_features.literal_context_features_count
            ),
            unique_literal_context_score=round(unique_literal_context_score, 6),
        ),
    )


def build_version_decisions(
    candidates: list[MatchCandidate],
    *,
    enable_version_unique_literal_context_reranker: bool = True,
) -> list[VersionDecision]:
    by_coordinate: dict[str, list[MatchCandidate]] = {}
    for candidate in candidates:
        by_coordinate.setdefault(candidate.coordinate, []).append(candidate)

    ranked_by_coordinate = {
        coordinate: sorted(coordinate_candidates, key=lambda item: item.score, reverse=True)
        for coordinate, coordinate_candidates in by_coordinate.items()
    }
    preliminary_selections = {
        coordinate: _choose_version_candidate(
            ranked,
            enable_version_unique_literal_context_reranker=(
                enable_version_unique_literal_context_reranker
            ),
        )[0]
        for coordinate, ranked in ranked_by_coordinate.items()
    }

    decisions: list[VersionDecision] = []
    for coordinate, ranked in sorted(ranked_by_coordinate.items()):
        best, selection_reason = _choose_version_candidate(
            ranked,
            dependency_context=preliminary_selections,
            enable_version_unique_literal_context_reranker=(
                enable_version_unique_literal_context_reranker
            ),
        )
        non_selected = [candidate for candidate in ranked if candidate is not best]
        second = non_selected[0] if non_selected else None
        gap_to_next = max(0.0, best.score - second.score) if second else best.score
        confidence_label, version_decision = classify_version_candidate(best, gap_to_next)
        if len(ranked) == 1:
            confidence_label, version_decision = _cap_single_reference_version_decision(
                best,
                confidence_label,
                version_decision,
            )
        coherence_downgrade_reason = _unsupported_app_era_coherence_reason(
            best,
            preliminary_selections,
        )
        if coherence_downgrade_reason:
            confidence_label = "uncertain"
            version_decision = "uncertain"
            selection_reason = _append_selection_reason(
                selection_reason,
                coherence_downgrade_reason,
            )
        ambiguity_reason = _version_ambiguity_reason(best, second)
        ambiguous_versions = _ambiguous_version_set(best, ranked)
        identity_confidence = identity_confidence_score(best)
        identity_confidence_label, identity_status = classify_identity_candidate(
            best,
            identity_confidence,
        )
        alternatives = [
            VersionAlternative(
                version=candidate.version,
                purl=candidate.purl,
                score=candidate.score,
            )
            for candidate in non_selected[:3]
        ]
        decisions.append(
            VersionDecision(
                coordinate=coordinate,
                group_id=best.group_id,
                artifact_id=best.artifact_id,
                selected_version=best.version,
                purl=best.purl,
                score=best.score,
                confidence=best.score,
                confidence_label=confidence_label,
                version_decision=version_decision,
                gap_to_next=round(gap_to_next, 6),
                reference_versions_considered=len(ranked),
                evidence=best.evidence,
                alternatives=alternatives,
                identity_confidence=identity_confidence,
                identity_confidence_label=identity_confidence_label,
                identity_status=identity_status,
                version_confidence=best.score,
                version_confidence_label=confidence_label,
                version_status=version_decision,
                version_selection_reason=selection_reason,
                version_ambiguity_reason=ambiguity_reason,
                ambiguous_versions=ambiguous_versions,
            )
        )

    decisions.sort(key=lambda item: item.score, reverse=True)
    return decisions


def detected_libraries_from_match_summary(
    summary: MatchSummary,
    *,
    include_uncertain: bool = False,
) -> list[DetectedLibrary]:
    libraries: list[DetectedLibrary] = []
    for decision, suppressed in reportable_version_decisions(
        summary.decisions,
        include_uncertain=include_uncertain,
    ):
        evidence = _decision_evidence(decision)
        evidence.extend(_artifact_family_evidence(decision, suppressed))
        libraries.append(
            DetectedLibrary(
                group=decision.group_id,
                artifact=decision.artifact_id,
                version=decision.selected_version,
                confidence=decision.confidence,
                match_type=f"hybrid-{decision.version_decision}",
                evidence=evidence,
                identity_confidence=decision.identity_confidence,
                identity_confidence_label=decision.identity_confidence_label,
                identity_status=decision.identity_status,
                version_confidence=decision.version_confidence,
                version_confidence_label=decision.version_confidence_label,
                version_status=decision.version_status,
                ambiguous_versions=[
                    candidate.version for candidate in decision.ambiguous_versions
                ],
            )
        )
    return libraries


def reportable_version_decisions(
    decisions: list[VersionDecision],
    *,
    include_uncertain: bool = False,
) -> list[tuple[VersionDecision, list[VersionDecision]]]:
    eligible = [
        decision
        for decision in decisions
        if include_uncertain or decision.version_decision != "uncertain"
    ]
    if not include_uncertain:
        eligible_family_keys = {_artifact_family_key(decision) for decision in eligible}
        eligible.extend(
            decision
            for decision in decisions
            if decision.version_decision == "uncertain"
            and _artifact_family_rule(decision)
            and _artifact_family_key(decision) in eligible_family_keys
            and decision.identity_status != "uncertain"
            and decision.score >= 0.35
        )
    grouped: dict[str, list[VersionDecision]] = {}
    for decision in eligible:
        grouped.setdefault(_artifact_family_key(decision), []).append(decision)

    version_hints = _artifact_family_version_hints(eligible)
    reportable: list[tuple[VersionDecision, list[VersionDecision]]] = []
    for group_decisions in grouped.values():
        if len(group_decisions) == 1:
            reportable.append((group_decisions[0], []))
            continue
        raw_winner = _choose_artifact_family_winner(
            group_decisions,
            version_hint=version_hints.get(_artifact_family_key(group_decisions[0])),
        )
        winner = _promote_family_selected_uncertain_candidate(raw_winner)
        suppressed = [
            decision
            for decision in sorted(group_decisions, key=_decision_sort_key, reverse=True)
            if decision is not raw_winner
        ]
        reportable.append((winner, suppressed))

    reportable.sort(key=lambda item: _decision_sort_key(item[0]), reverse=True)
    return reportable


def classify_version_candidate(candidate: MatchCandidate, gap_to_next: float) -> tuple[str, str]:
    if (
        candidate.score >= 0.995
        and candidate.evidence.package_score >= 0.995
        and candidate.evidence.class_score >= 0.995
        and candidate.evidence.method_score >= 0.995
        and candidate.evidence.opcode_score >= 0.995
    ):
        return "high", "exact"
    if (
        candidate.score >= 0.92
        and gap_to_next >= 0.08
        and candidate.evidence.class_score >= 0.85
        and candidate.evidence.method_score >= 0.75
    ):
        return "high", "exact"
    if candidate.score >= 0.75 and gap_to_next >= 0.05:
        return "medium", "likely"
    if candidate.score >= 0.45:
        return "low", "candidate"
    if _has_obfuscation_resilient_candidate_evidence(candidate, gap_to_next):
        return "low", "candidate"
    return "uncertain", "uncertain"


def identity_confidence_score(candidate: MatchCandidate) -> float:
    evidence = candidate.evidence
    return round(
        _weighted_score(
            [
                (evidence.package_score, 0.20, evidence.reference_packages > 0),
                (evidence.class_score, 0.30, evidence.reference_classes > 0),
                (evidence.method_score, 0.20, evidence.reference_methods > 0),
                (evidence.opcode_score, 0.10, evidence.reference_distinct_opcodes > 0),
                (evidence.dependency_score, 0.10, evidence.reference_dependency_edges > 0),
                (evidence.literal_score, 0.10, evidence.reference_string_literals > 0),
                (evidence.api_reference_score, 0.10, evidence.reference_api_references > 0),
            ]
        ),
        6,
    )


def classify_identity_candidate(
    candidate: MatchCandidate,
    identity_confidence: float | None = None,
) -> tuple[str, str]:
    score = candidate.score
    evidence = candidate.evidence
    identity_score = (
        identity_confidence if identity_confidence is not None else identity_confidence_score(candidate)
    )
    has_name_evidence = (
        evidence.package_score >= 0.70
        or evidence.class_score >= 0.35
        or evidence.method_score >= 0.35
    )
    has_structural_evidence = (
        evidence.opcode_score >= 0.80
        and (evidence.dependency_score >= 0.35 or evidence.literal_score >= 0.50)
    )
    if identity_score >= 0.90 and score >= 0.75 and has_name_evidence:
        return "high", "confirmed"
    if identity_score >= 0.70 and score >= 0.45 and (has_name_evidence or has_structural_evidence):
        return "medium", "likely"
    if identity_score >= 0.45 or _has_obfuscation_resilient_candidate_evidence(candidate, 0.01):
        return "low", "candidate"
    return "uncertain", "uncertain"


def _cap_single_reference_version_decision(
    candidate: MatchCandidate,
    confidence_label: str,
    version_decision: str,
) -> tuple[str, str]:
    if version_decision not in {"exact", "likely"}:
        return confidence_label, version_decision
    if _has_complete_single_version_match(candidate):
        return confidence_label, version_decision
    return "low", "candidate"


def _has_complete_single_version_match(candidate: MatchCandidate) -> bool:
    evidence = candidate.evidence
    return (
        candidate.score >= 0.995
        and evidence.package_score >= 0.995
        and evidence.class_score >= 0.995
        and evidence.method_score >= 0.995
        and evidence.opcode_score >= 0.995
    )


def _has_obfuscation_resilient_candidate_evidence(
    candidate: MatchCandidate,
    gap_to_next: float,
) -> bool:
    evidence = candidate.evidence
    has_version_literal_evidence = (
        evidence.literal_score >= 0.65
        and evidence.unique_literal_score >= 0.60
        and evidence.opcode_score >= 0.85
        and gap_to_next >= 0.01
    )
    has_package_literal_evidence = (
        evidence.package_score >= 0.70
        and evidence.literal_score >= 0.65
        and evidence.opcode_score >= 0.85
        and gap_to_next >= 0.01
    )
    has_low_gap_package_literal_evidence = (
        candidate.score >= 0.35
        and evidence.package_score >= 0.90
        and evidence.literal_score >= 0.75
        and evidence.opcode_score >= 0.85
        and gap_to_next >= 0.001
    )
    return (
        has_version_literal_evidence
        or has_package_literal_evidence
        or has_low_gap_package_literal_evidence
    )


def _choose_version_candidate(
    ranked: list[MatchCandidate],
    *,
    dependency_context: dict[str, MatchCandidate] | None = None,
    enable_version_unique_literal_context_reranker: bool = True,
) -> tuple[MatchCandidate, str | None]:
    raw_best = ranked[0]
    distinctive = _choose_distinctive_version_candidate(ranked)
    if distinctive is not None:
        reason = (
            f"Selected {distinctive.version} over raw-score leader {raw_best.version} "
            f"because it has stronger version-distinctive evidence "
            f"(unique_score={distinctive.evidence.unique_version_score:.3f} vs "
            f"{raw_best.evidence.unique_version_score:.3f}) while staying within "
            f"{VERSION_DISTINCTIVE_SCORE_MARGIN:.3f} score."
        )
        return distinctive, reason

    if enable_version_unique_literal_context_reranker:
        literal_context = _choose_version_unique_literal_context_candidate(ranked)
        if literal_context is not None:
            evidence = literal_context.evidence
            advantage = _version_unique_literal_context_advantage(
                literal_context,
                ranked,
            )
            reason = (
                f"Selected {literal_context.version} over raw-score leader "
                f"{raw_best.version} because it has stronger version-unique "
                "literal/context evidence "
                f"({evidence.matched_unique_literal_context_features}/"
                f"{evidence.reference_unique_literal_context_features} matches; "
                f"score={evidence.unique_literal_context_score:.3f}; "
                f"advantage={advantage:.3f}) while staying within "
                f"{VERSION_UNIQUE_LITERAL_CONTEXT_SCORE_MARGIN:.3f} raw score."
            )
            return literal_context, reason

    dependency_coherent = _choose_dependency_coherent_version_candidate(
        ranked,
        dependency_context or {},
    )
    if dependency_coherent is not None:
        supported = _pom_dependency_support(dependency_coherent, dependency_context or {})
        raw_supported = _pom_dependency_support(raw_best, dependency_context or {})
        reason = (
            f"Selected {dependency_coherent.version} over raw-score leader {raw_best.version} "
            "because its Maven POM dependencies are supported by independently detected "
            f"components ({_format_dependency_support(supported)} vs "
            f"{_format_dependency_support(raw_supported)})."
        )
        return dependency_coherent, reason

    app_era_coherent = _choose_app_era_coherent_version_candidate(
        ranked,
        dependency_context or {},
    )
    if app_era_coherent is not None:
        supported = _app_era_coherence_support(app_era_coherent, dependency_context or {})
        raw_supported = _app_era_coherence_support(raw_best, dependency_context or {})
        reason = (
            f"Selected {app_era_coherent.version} over raw-score leader {raw_best.version} "
            "because app-era/dependency coherence supports its version band "
            f"({_format_app_era_support(supported)} vs "
            f"{_format_app_era_support(raw_supported)})."
        )
        return app_era_coherent, reason

    return raw_best, None


def _choose_distinctive_version_candidate(
    ranked: list[MatchCandidate],
) -> MatchCandidate | None:
    raw_best = ranked[0]
    if raw_best.score >= VERSION_DISTINCTIVE_MAX_RAW_SCORE:
        return None

    best_identity = identity_confidence_score(raw_best)
    eligible = [
        candidate
        for candidate in ranked[1:]
        if raw_best.score - candidate.score <= VERSION_DISTINCTIVE_SCORE_MARGIN
        and _has_matched_unique_version_features(candidate)
        and candidate.evidence.unique_version_score
        >= raw_best.evidence.unique_version_score + VERSION_DISTINCTIVE_UNIQUE_ADVANTAGE
        and identity_confidence_score(candidate)
        >= best_identity - VERSION_DISAMBIGUATION_IDENTITY_TOLERANCE
    ]
    if not eligible:
        return None

    return max(
        eligible,
        key=lambda candidate: (
            candidate.evidence.unique_version_score,
            _matched_unique_feature_count(candidate),
            candidate.score,
            _version_rank(candidate.version),
        ),
    )


def _has_matched_unique_version_features(candidate: MatchCandidate) -> bool:
    return _matched_unique_feature_count(candidate) > 0


def _choose_version_unique_literal_context_candidate(
    ranked: list[MatchCandidate],
) -> MatchCandidate | None:
    raw_best = ranked[0]
    if raw_best.score < VERSION_UNIQUE_LITERAL_CONTEXT_MIN_RAW_SCORE:
        return None

    best_identity = identity_confidence_score(raw_best)
    eligible = [
        candidate
        for candidate in ranked[1:]
        if raw_best.score - candidate.score <= VERSION_UNIQUE_LITERAL_CONTEXT_SCORE_MARGIN
        and _has_supported_version_unique_literal_context(candidate)
        and _version_unique_literal_context_advantage(candidate, ranked)
        >= VERSION_UNIQUE_LITERAL_CONTEXT_MIN_ADVANTAGE
        and identity_confidence_score(candidate)
        >= best_identity - VERSION_DISAMBIGUATION_IDENTITY_TOLERANCE
    ]


def prefilter_component_ids_by_package_overlap(
    connection: sqlite3.Connection,
    apk_packages: set[str],
    *,
    coordinate: str | None = None,
    min_overlap: int = 1,
    limit: int | None = None,
) -> set[int]:
    if not apk_packages:
        return set()

    placeholders = ", ".join("?" for _ in apk_packages)
    params: list[object] = list(apk_packages)
    coordinate_clause = ""
    if coordinate:
        coordinate_clause = "AND c.coordinate = ?"
        params.append(coordinate)
    having_clause = "HAVING shared_packages >= ?"
    params.append(max(1, min_overlap))
    limit_clause = ""
    if limit is not None:
        limit_clause = "LIMIT ?"
        params.append(max(0, limit))

    rows = connection.execute(
        f"""
        SELECT p.component_id, COUNT(DISTINCT p.package) AS shared_packages
        FROM packages p
        JOIN components c ON c.id = p.component_id
        WHERE p.package IN ({placeholders})
        {coordinate_clause}
        GROUP BY p.component_id
        {having_clause}
        ORDER BY shared_packages DESC, c.coordinate ASC, c.version DESC
        {limit_clause}
        """,
        params,
    )
    return {int(component_id) for component_id, _shared_packages in rows}
    if not eligible:
        return None

    return max(
        eligible,
        key=lambda candidate: (
            candidate.evidence.unique_literal_context_score,
            candidate.evidence.matched_unique_literal_context_features,
            candidate.score,
            _version_rank(candidate.version),
        ),
    )


def _has_supported_version_unique_literal_context(candidate: MatchCandidate) -> bool:
    evidence = candidate.evidence
    return (
        evidence.matched_unique_literal_context_features
        >= VERSION_UNIQUE_LITERAL_CONTEXT_MIN_MATCHES
        and evidence.unique_literal_context_score
        >= VERSION_UNIQUE_LITERAL_CONTEXT_MIN_SCORE
    )


def _version_unique_literal_context_advantage(
    candidate: MatchCandidate,
    ranked: list[MatchCandidate],
) -> float:
    competing_scores = [
        item.evidence.unique_literal_context_score
        for item in ranked
        if item is not candidate
    ]
    next_score = max(competing_scores, default=0.0)
    return candidate.evidence.unique_literal_context_score - next_score


def _version_ambiguity_reason(
    selected: MatchCandidate,
    alternative: MatchCandidate | None,
) -> str | None:
    feature_equivalent_reason = _feature_equivalent_version_ambiguity_reason(
        selected,
        alternative,
    )
    if feature_equivalent_reason:
        return feature_equivalent_reason
    return _near_tie_version_ambiguity_reason(selected, alternative)


def _feature_equivalent_version_ambiguity_reason(
    selected: MatchCandidate,
    alternative: MatchCandidate | None,
) -> str | None:
    if alternative is None:
        return None
    if selected.score - alternative.score > FEATURE_EQUIVALENT_VERSION_SCORE_MARGIN:
        return None
    if not _feature_signals_are_equivalent(selected, alternative):
        return None
    return (
        f"Version ambiguity: {selected.version} and {alternative.version} have "
        "feature-equivalent APK evidence within "
        f"{FEATURE_EQUIVALENT_VERSION_SCORE_MARGIN:.3f} score. Treat this as a "
        "version-band limitation unless independent dependency or app-era evidence "
        "breaks the tie."
    )


def _near_tie_version_ambiguity_reason(
    selected: MatchCandidate,
    alternative: MatchCandidate | None,
) -> str | None:
    if alternative is None:
        return None
    if (
        selected.score < VERSION_NEAR_TIE_MIN_SCORE
        or alternative.score < VERSION_NEAR_TIE_MIN_SCORE
    ):
        return None
    gap = selected.score - alternative.score
    if gap < 0 or gap > VERSION_NEAR_TIE_SCORE_MARGIN:
        return None
    if _matched_unique_feature_count(selected) or _matched_unique_feature_count(alternative):
        return None
    return (
        f"Version near-tie: {selected.version} and {alternative.version} are within "
        f"{VERSION_NEAR_TIE_SCORE_MARGIN:.3f} score, and neither candidate has matched "
        "version-unique APK evidence. Treat the selected version as a nearby version-band "
        "candidate unless independent dependency, source, or app-era evidence confirms it."
    )


def _ambiguous_version_set(
    selected: MatchCandidate,
    ranked: list[MatchCandidate],
) -> list[VersionAlternative]:
    ambiguous_candidates = [selected]
    for candidate in ranked:
        if candidate is selected:
            continue
        if _version_ambiguity_reason(selected, candidate):
            ambiguous_candidates.append(candidate)

    if len(ambiguous_candidates) < 2:
        return []

    return [
        VersionAlternative(
            version=candidate.version,
            purl=candidate.purl,
            score=candidate.score,
        )
        for candidate in ambiguous_candidates[:4]
    ]


def _feature_signals_are_equivalent(
    left: MatchCandidate,
    right: MatchCandidate,
) -> bool:
    left_evidence = left.evidence
    right_evidence = right.evidence
    if _matched_unique_feature_count(left) or _matched_unique_feature_count(right):
        return False
    signal_pairs = [
        (left_evidence.package_score, right_evidence.package_score),
        (left_evidence.class_score, right_evidence.class_score),
        (left_evidence.method_score, right_evidence.method_score),
        (left_evidence.dependency_score, right_evidence.dependency_score),
        (left_evidence.literal_score, right_evidence.literal_score),
        (left_evidence.api_reference_score, right_evidence.api_reference_score),
        (left_evidence.unique_version_score, right_evidence.unique_version_score),
    ]
    return all(
        abs(left_score - right_score) <= FEATURE_EQUIVALENT_VERSION_SIGNAL_TOLERANCE
        for left_score, right_score in signal_pairs
    )


def _matched_unique_feature_count(candidate: MatchCandidate) -> int:
    evidence = candidate.evidence
    return (
        evidence.matched_unique_classes
        + evidence.matched_unique_methods
        + evidence.matched_unique_literals
    )


def _version_rank(version: str) -> tuple[int, Version | str]:
    try:
        return (1, Version(version))
    except InvalidVersion:
        return (0, version)


def _choose_dependency_coherent_version_candidate(
    ranked: list[MatchCandidate],
    dependency_context: dict[str, MatchCandidate],
) -> MatchCandidate | None:
    if not dependency_context:
        return None

    raw_best = ranked[0]
    if raw_best.score < POM_COHERENCE_MIN_RAW_SCORE:
        return None
    if raw_best.score >= POM_COHERENCE_MAX_RAW_SCORE:
        return None

    raw_support = _pom_dependency_support(raw_best, dependency_context)
    best_identity = identity_confidence_score(raw_best)
    eligible = [
        candidate
        for candidate in ranked[1:]
        if raw_best.score - candidate.score <= POM_COHERENCE_SCORE_MARGIN
        and candidate.score >= POM_COHERENCE_MIN_RAW_SCORE
        and identity_confidence_score(candidate)
        >= best_identity - VERSION_DISAMBIGUATION_IDENTITY_TOLERANCE
        and len(_pom_dependency_support(candidate, dependency_context)) > len(raw_support)
    ]
    if not eligible:
        return None

    return max(
        eligible,
        key=lambda candidate: (
            len(_pom_dependency_support(candidate, dependency_context)),
            candidate.score,
            _version_rank(candidate.version),
        ),
    )


def _pom_dependency_support(
    candidate: MatchCandidate,
    dependency_context: dict[str, MatchCandidate],
) -> list[MavenPomDependency]:
    supported: list[MavenPomDependency] = []
    for dependency in candidate.maven_dependencies:
        if not _is_runtime_dependency_hint(dependency):
            continue
        selected = dependency_context.get(dependency.coordinate)
        if selected is None or selected.coordinate == candidate.coordinate:
            continue
        if selected.version == dependency.version and _is_independent_dependency_support(selected):
            supported.append(dependency)
    return supported


def _is_runtime_dependency_hint(dependency: MavenPomDependency) -> bool:
    if not dependency.version or dependency.version.startswith("${"):
        return False
    if dependency.optional:
        return False
    return dependency.scope not in {"test", "provided"}


def _is_independent_dependency_support(candidate: MatchCandidate) -> bool:
    confidence_label, version_decision = classify_version_candidate(candidate, candidate.score)
    identity_label, identity_status = classify_identity_candidate(candidate)
    return (
        version_decision != "uncertain"
        and identity_status != "uncertain"
        and identity_label in {"high", "medium", "low"}
        and confidence_label in {"high", "medium", "low"}
    )


def _format_dependency_support(dependencies: list[MavenPomDependency]) -> str:
    if not dependencies:
        return "no supported POM dependencies"
    return ", ".join(
        f"{dependency.coordinate}@{dependency.version}"
        for dependency in dependencies[:3]
    )


def _choose_app_era_coherent_version_candidate(
    ranked: list[MatchCandidate],
    dependency_context: dict[str, MatchCandidate],
) -> MatchCandidate | None:
    if not dependency_context:
        return None

    raw_best = ranked[0]
    if raw_best.score < APP_ERA_COHERENCE_MIN_RAW_SCORE:
        return None

    rule = APP_ERA_COHERENCE_RULES.get(raw_best.coordinate)
    if rule is None:
        return None

    raw_support = _app_era_coherence_support(raw_best, dependency_context)
    best_identity = identity_confidence_score(raw_best)
    eligible = [
        candidate
        for candidate in ranked[1:]
        if candidate.coordinate == raw_best.coordinate
        and raw_best.score - candidate.score <= rule.score_margin
        and candidate.score >= APP_ERA_COHERENCE_MIN_RAW_SCORE
        and identity_confidence_score(candidate)
        >= best_identity - APP_ERA_COHERENCE_IDENTITY_TOLERANCE
        and len(_app_era_coherence_support(candidate, dependency_context))
        >= rule.minimum_support
        and len(_app_era_coherence_support(candidate, dependency_context)) > len(raw_support)
    ]
    if not eligible:
        return None

    return max(
        eligible,
        key=lambda candidate: (
            len(_app_era_coherence_support(candidate, dependency_context)),
            candidate.score,
            _version_rank(candidate.version),
        ),
    )


def _unsupported_app_era_coherence_reason(
    candidate: MatchCandidate,
    dependency_context: dict[str, MatchCandidate],
) -> str | None:
    rule = APP_ERA_COHERENCE_RULES.get(candidate.coordinate)
    if rule is None or not rule.requires_support_for_candidate:
        return None
    if candidate.score >= rule.unsupported_max_score:
        return None
    support = _app_era_coherence_support(candidate, dependency_context)
    if len(support) >= rule.minimum_support:
        return None

    family_support = _app_era_family_support(rule, dependency_context, exclude=candidate.coordinate)
    if not family_support:
        return None
    supported_version, supporters = max(
        family_support.items(),
        key=lambda item: (len(item[1]), item[0]),
    )
    if len(supporters) < rule.minimum_support:
        return None
    if supported_version == _app_era_version_key(candidate.version):
        return None

    return (
        f"Downgraded {candidate.version} to uncertain because app-era/dependency "
        f"coherence for {rule.family_id} points to {supported_version} "
        f"({_format_app_era_support(supporters)}) and this candidate has "
        f"{_format_app_era_support(support)}."
    )


def _app_era_coherence_support(
    candidate: MatchCandidate,
    dependency_context: dict[str, MatchCandidate],
) -> list[MatchCandidate]:
    rule = APP_ERA_COHERENCE_RULES.get(candidate.coordinate)
    if rule is None:
        return []
    version_key = _app_era_version_key(candidate.version)
    return [
        selected
        for coordinate, selected in dependency_context.items()
        if coordinate != candidate.coordinate
        and coordinate in rule.coordinates
        and _app_era_version_key(selected.version) == version_key
        and _is_independent_dependency_support(selected)
    ]


def _app_era_family_support(
    rule: AppEraCoherenceRule,
    dependency_context: dict[str, MatchCandidate],
    *,
    exclude: str,
) -> dict[str, list[MatchCandidate]]:
    by_version: dict[str, list[MatchCandidate]] = {}
    for coordinate, selected in dependency_context.items():
        if coordinate == exclude or coordinate not in rule.coordinates:
            continue
        if not _is_independent_dependency_support(selected):
            continue
        by_version.setdefault(_app_era_version_key(selected.version), []).append(selected)
    return by_version


def _app_era_version_key(version: str) -> str:
    return version.strip().lower()


def _format_app_era_support(candidates: list[MatchCandidate]) -> str:
    if not candidates:
        return "no coherent family support"
    return ", ".join(
        f"{candidate.coordinate}@{candidate.version}"
        for candidate in candidates[:3]
    )


def _append_selection_reason(existing: str | None, addition: str) -> str:
    if not existing:
        return addition
    return f"{existing} {addition}"


def _artifact_family_key(decision: VersionDecision) -> str:
    rule = _artifact_family_rule(decision)
    if rule:
        return f"family:{rule.family_id}"
    return f"coordinate:{decision.coordinate}"


def _artifact_family_rule(decision: VersionDecision) -> ArtifactFamilyRule | None:
    return ARTIFACT_FAMILY_RULES.get((decision.group_id, decision.artifact_id))


def _choose_artifact_family_winner(
    decisions: list[VersionDecision],
    *,
    version_hint: str | None = None,
) -> VersionDecision:
    best_by_score = max(decisions, key=_decision_sort_key)
    if version_hint:
        hinted_decisions = [
            decision
            for decision in decisions
            if decision.selected_version == version_hint
            and decision.score
            >= best_by_score.score - ARTIFACT_FAMILY_VERSION_HINT_SCORE_MARGIN
            and _decision_confidence_rank(decision)
            >= _decision_confidence_rank(best_by_score) - 1
        ]
        if hinted_decisions:
            return max(
                hinted_decisions,
                key=lambda decision: (
                    _artifact_family_preference_rank(decision),
                    _decision_confidence_rank(decision),
                    decision.score,
                    decision.gap_to_next,
                    decision.coordinate,
                    decision.selected_version,
                ),
            )

    lifecycle_target = _choose_low_confidence_lifecycle_target_variant(
        decisions,
        best_by_score,
    )
    if lifecycle_target:
        return lifecycle_target

    close_decisions = [
        decision
        for decision in decisions
        if decision.score >= best_by_score.score - ARTIFACT_FAMILY_CLOSE_SCORE_MARGIN
        and _decision_confidence_rank(decision) >= _decision_confidence_rank(best_by_score) - 1
    ]
    return max(
        close_decisions,
        key=lambda decision: (
            _artifact_family_preference_rank(decision),
            _decision_confidence_rank(decision),
            decision.score,
            decision.gap_to_next,
            decision.coordinate,
            decision.selected_version,
        ),
    )


def _decision_sort_key(decision: VersionDecision) -> tuple[float, int, float, str, str]:
    return (
        decision.score,
        _decision_confidence_rank(decision),
        decision.gap_to_next,
        decision.coordinate,
        decision.selected_version,
    )


def _decision_confidence_rank(decision: VersionDecision) -> int:
    return {
        "exact": 3,
        "likely": 2,
        "candidate": 1,
        "uncertain": 0,
    }.get(decision.version_decision, 0)


def _artifact_family_preference_rank(decision: VersionDecision) -> int:
    rule = _artifact_family_rule(decision)
    return rule.preference_rank if rule else 0


def _choose_low_confidence_lifecycle_target_variant(
    decisions: list[VersionDecision],
    best_by_score: VersionDecision,
) -> VersionDecision | None:
    if best_by_score.group_id != "androidx.lifecycle":
        return None
    if best_by_score.artifact_id not in {"lifecycle-runtime", "lifecycle-viewmodel"}:
        return None
    if best_by_score.score >= 0.70:
        return None

    target_artifact = f"{best_by_score.artifact_id}-android"
    target_candidates = [
        decision
        for decision in decisions
        if decision.artifact_id == target_artifact
        and decision.score >= best_by_score.score - ARTIFACT_FAMILY_VERSION_HINT_SCORE_MARGIN
        and decision.identity_status != "uncertain"
    ]
    if not target_candidates:
        return None

    return max(
        target_candidates,
        key=lambda decision: (
            _decision_confidence_rank(decision),
            _version_rank(decision.selected_version),
            decision.score,
        ),
    )


def _promote_family_selected_uncertain_candidate(decision: VersionDecision) -> VersionDecision:
    if decision.version_decision != "uncertain":
        return decision
    rule = _artifact_family_rule(decision)
    if not rule:
        return decision
    return replace(
        decision,
        confidence_label="low",
        version_decision="candidate",
        version_confidence_label="low",
        version_status="candidate",
        version_selection_reason=(
            "Selected as a low-confidence candidate by scoped artifact-family coherence."
        ),
    )


def _artifact_family_version_hints(decisions: list[VersionDecision]) -> dict[str, str]:
    hints: dict[str, str] = {}
    for family_id, excluded_artifacts in {
        "androidx.lifecycle:lifecycle-runtime-family": LIFECYCLE_RUNTIME_ARTIFACTS,
        "androidx.lifecycle:lifecycle-viewmodel-family": LIFECYCLE_VIEWMODEL_ARTIFACTS,
    }.items():
        version_weights: Counter[str] = Counter()
        for decision in decisions:
            if decision.group_id != "androidx.lifecycle":
                continue
            if decision.artifact_id in excluded_artifacts:
                continue
            if decision.version_decision == "uncertain":
                continue
            version_weights[decision.selected_version] += decision.score
        if version_weights:
            hints[f"family:{family_id}"] = max(
                version_weights.items(),
                key=lambda item: (item[1], item[0]),
            )[0]
    return hints


def _artifact_family_evidence(
    selected: VersionDecision,
    suppressed: list[VersionDecision],
) -> list[ComponentEvidence]:
    rule = _artifact_family_rule(selected)
    if not rule or not suppressed:
        return []

    suppressed_detail = ", ".join(
        f"{decision.coordinate}@{decision.selected_version}:{decision.score:.3f}"
        for decision in suppressed
    )
    return [
        ComponentEvidence(
            source="artifact-family-disambiguation",
            detail=(
                f"Selected {selected.coordinate}@{selected.selected_version} for "
                f"{rule.family_id}; suppressed overlapping candidate(s): "
                f"{suppressed_detail}. Reason: {rule.reason}"
            ),
            weight=selected.confidence,
        )
    ]


def _decision_evidence(decision: VersionDecision) -> list[ComponentEvidence]:
    evidence = decision.evidence
    alternatives = ", ".join(
        f"{alternative.version}:{alternative.score:.3f}" for alternative in decision.alternatives
    )
    if not alternatives:
        alternatives = "none"
    items = [
        ComponentEvidence(
            source="package-overlap",
            detail=(
                f"{evidence.matched_packages}/{evidence.reference_packages} reference packages "
                f"matched; score={evidence.package_score:.3f}"
            ),
            weight=evidence.package_score,
        ),
        ComponentEvidence(
            source="class-overlap",
            detail=(
                f"{evidence.matched_classes}/{evidence.reference_classes} reference classes "
                f"matched; score={evidence.class_score:.3f}"
            ),
            weight=evidence.class_score,
        ),
        ComponentEvidence(
            source="method-overlap",
            detail=(
                f"{evidence.matched_methods}/{evidence.reference_methods} reference methods "
                f"matched; score={evidence.method_score:.3f}"
            ),
            weight=evidence.method_score,
        ),
        ComponentEvidence(
            source="opcode-cosine",
            detail=(
                f"{evidence.shared_opcodes} shared opcode kinds; "
                f"score={evidence.opcode_score:.3f}"
            ),
            weight=evidence.opcode_score,
        ),
        ComponentEvidence(
            source="opcode-ngrams",
            detail=(
                f"{evidence.shared_opcode_ngrams} shared opcode tri-grams; "
                f"score={evidence.opcode_ngram_score:.3f}"
            ),
            weight=evidence.opcode_ngram_score,
        ),
        ComponentEvidence(
            source="class-dependency-graph",
            detail=(
                f"{evidence.matched_dependency_edges}/{evidence.reference_dependency_edges} "
                f"reference dependency edges matched; "
                f"edge_score={evidence.dependency_edge_score:.3f}; "
                f"shape_score={evidence.dependency_shape_score:.3f}; "
                f"score={evidence.dependency_score:.3f}"
            ),
            weight=evidence.dependency_score,
        ),
        ComponentEvidence(
            source="string-literals",
            detail=(
                f"{evidence.matched_string_literals}/{evidence.reference_string_literals} "
                f"reference string literals matched; score={evidence.literal_score:.3f}"
            ),
            weight=evidence.literal_score,
        ),
        ComponentEvidence(
            source="api-references",
            detail=(
                f"{evidence.matched_api_references}/{evidence.reference_api_references} "
                f"reference API/member references matched; score={evidence.api_reference_score:.3f}"
            ),
            weight=evidence.api_reference_score,
        ),
        ComponentEvidence(
            source="version-unique-features",
            detail=(
                f"unique classes {evidence.matched_unique_classes}/"
                f"{evidence.reference_unique_classes}; "
                f"unique methods {evidence.matched_unique_methods}/"
                f"{evidence.reference_unique_methods}; "
                f"unique literals {evidence.matched_unique_literals}/"
                f"{evidence.reference_unique_literals}; "
                "unique literal/context "
                f"{evidence.matched_unique_literal_context_features}/"
                f"{evidence.reference_unique_literal_context_features}; "
                f"context_score={evidence.unique_literal_context_score:.3f}; "
                f"score={evidence.unique_version_score:.3f}"
            ),
            weight=evidence.unique_version_score,
        ),
        ComponentEvidence(
            source="identity-decision",
            detail=(
                f"{decision.identity_status} identity with "
                f"{decision.identity_confidence_label} confidence; "
                f"identity_score={decision.identity_confidence:.3f}"
            ),
            weight=decision.identity_confidence,
        ),
        ComponentEvidence(
            source="version-decision",
            detail=(
                f"{decision.version_status} version decision with "
                f"{decision.version_confidence_label} confidence; "
                f"gap_to_next={decision.gap_to_next:.3f}; alternatives={alternatives}"
            ),
            weight=decision.version_confidence,
        ),
    ]
    if decision.version_selection_reason:
        items.append(
            ComponentEvidence(
                source="version-disambiguation",
                detail=decision.version_selection_reason,
                weight=decision.version_confidence,
            )
        )
    if decision.version_ambiguity_reason:
        items.append(
            ComponentEvidence(
                source="version-ambiguity",
                detail=decision.version_ambiguity_reason,
                weight=decision.version_confidence,
            )
        )
    return items


def _load_component_feature_set(connection: sqlite3.Connection, component_id: int) -> FeatureSet:
    return FeatureSet(
        packages=_load_values(connection, "packages", "package", component_id),
        classes=_load_values(connection, "classes", "class_descriptor", component_id),
        methods=_load_values(connection, "methods", "method_signature", component_id),
        opcode_histogram=_load_opcode_histogram(connection, component_id),
        opcode_ngrams=_load_count_table_if_exists(
            connection,
            "opcode_ngrams",
            "ngram",
            component_id,
        ),
        class_dependencies=_load_dependency_edges(connection, component_id),
        dependency_shape=_load_dependency_shape(connection, component_id),
        string_literals=_load_values_if_table_exists(
            connection,
            "string_literals",
            "literal",
            component_id,
        ),
        api_references=_load_values_if_table_exists(
            connection,
            "api_references",
            "reference",
            component_id,
        ),
        basic_block_opcode_fingerprints=_load_count_table_if_exists(
            connection,
            "basic_block_opcode_fingerprints",
            "fingerprint",
            component_id,
        ),
        call_chain_opcode_fingerprints=_load_count_table_if_exists(
            connection,
            "call_chain_opcode_fingerprints",
            "fingerprint",
            component_id,
        ),
        class_neighbor_summaries=_load_count_table_if_exists(
            connection,
            "class_neighbor_summaries",
            "summary",
            component_id,
        ),
        field_operation_sequences=_load_count_table_if_exists(
            connection,
            "field_operation_sequences",
            "fingerprint",
            component_id,
        ),
        literal_context_features=_load_values_if_table_exists(
            connection,
            "literal_context_features",
            "feature",
            component_id,
        ),
    )


def _load_values(
    connection: sqlite3.Connection,
    table: str,
    column: str,
    component_id: int,
) -> set[str]:
    rows = connection.execute(
        f"SELECT {column} FROM {table} WHERE component_id = ?",
        (component_id,),
    ).fetchall()
    return {str(row[0]) for row in rows}


def _load_values_if_table_exists(
    connection: sqlite3.Connection,
    table: str,
    column: str,
    component_id: int,
) -> set[str]:
    if not _table_exists(connection, table):
        return set()
    return _load_values(connection, table, column, component_id)


def _load_maven_dependencies(
    connection: sqlite3.Connection,
    component_id: int,
) -> list[MavenPomDependency]:
    if not _table_exists(connection, "maven_dependencies"):
        return []
    rows = connection.execute(
        """
        SELECT group_id, artifact_id, version, scope, optional, type, classifier
        FROM maven_dependencies
        WHERE component_id = ?
        ORDER BY group_id, artifact_id, version
        """,
        (component_id,),
    ).fetchall()
    return [
        MavenPomDependency(
            group=str(row[0]),
            artifact=str(row[1]),
            version=row[2],
            scope=row[3],
            optional=bool(row[4]),
            type=row[5],
            classifier=row[6],
        )
        for row in rows
    ]


def _coverage_score(matches: set[str], reference_values: set[str]) -> float:
    if not reference_values:
        return 0.0
    return len(matches) / len(reference_values)


def _weighted_score(scores: list[tuple[float, float, bool]]) -> float:
    active = [(score, weight) for score, weight, enabled in scores if enabled]
    total_weight = sum(weight for _, weight in active)
    if total_weight <= 0:
        return 0.0
    return sum(score * weight for score, weight in active) / total_weight


def _version_unique_features(reference: FeatureSet, siblings: list[FeatureSet]) -> FeatureSet:
    if not siblings:
        return FeatureSet(packages=set(), classes=set(), methods=set())

    sibling_classes = set().union(*(item.classes for item in siblings))
    sibling_methods = set().union(*(item.methods for item in siblings))
    sibling_literals = set().union(*(item.string_literals for item in siblings))
    sibling_literal_context = set().union(*(item.literal_context_features for item in siblings))

    return FeatureSet(
        packages=set(),
        classes=reference.classes - sibling_classes,
        methods=reference.methods - sibling_methods,
        string_literals=reference.string_literals - sibling_literals,
        literal_context_features=reference.literal_context_features - sibling_literal_context,
    )


def _load_opcode_histogram(connection: sqlite3.Connection, component_id: int) -> dict[str, int]:
    if not _table_exists(connection, "opcodes"):
        return {}
    rows = connection.execute(
        "SELECT opcode, count FROM opcodes WHERE component_id = ?",
        (component_id,),
    ).fetchall()
    return {str(row[0]): int(row[1]) for row in rows}


def _load_count_table_if_exists(
    connection: sqlite3.Connection,
    table: str,
    key_column: str,
    component_id: int,
) -> dict[str, int]:
    if not _table_exists(connection, table):
        return {}
    rows = connection.execute(
        f"SELECT {key_column}, count FROM {table} WHERE component_id = ?",
        (component_id,),
    ).fetchall()
    return {str(row[0]): int(row[1]) for row in rows}


def _cosine_similarity(left: dict[str, int], right: dict[str, int]) -> float:
    if not left or not right:
        return 0.0

    if len(left) <= len(right):
        numerator = sum(left[key] * right[key] for key in left if key in right)
    else:
        numerator = sum(left[key] * right[key] for key in right if key in left)
    left_norm = math.sqrt(sum(count * count for count in left.values()))
    right_norm = math.sqrt(sum(count * count for count in right.values()))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return numerator / (left_norm * right_norm)


def _shared_key_count(left: dict[str, int], right: dict[str, int]) -> int:
    if not left or not right:
        return 0
    if len(left) <= len(right):
        return sum(1 for key in left if key in right)
    return sum(1 for key in right if key in left)


def _load_dependency_edges(
    connection: sqlite3.Connection,
    component_id: int,
) -> set[tuple[str, str, str]]:
    if not _table_exists(connection, "class_dependencies"):
        return set()
    rows = connection.execute(
        """
        SELECT source_class, target_class, kind
        FROM class_dependencies
        WHERE component_id = ?
        """,
        (component_id,),
    ).fetchall()
    return {(str(row[0]), str(row[1]), str(row[2])) for row in rows}


def _load_dependency_shape(connection: sqlite3.Connection, component_id: int) -> dict[str, int]:
    if not _table_exists(connection, "dependency_shapes"):
        return {}
    rows = connection.execute(
        "SELECT feature, count FROM dependency_shapes WHERE component_id = ?",
        (component_id,),
    ).fetchall()
    return {str(row[0]): int(row[1]) for row in rows}


def _dependency_shape_similarity(left: FeatureSet, right: FeatureSet) -> float:
    left_graph = _dependency_graph(left.class_dependencies)
    right_graph = _dependency_graph(right.class_dependencies)
    if left_graph.number_of_edges() == 0 and right_graph.number_of_edges() == 0:
        return _cosine_similarity(left.dependency_shape, right.dependency_shape)

    left_shape = dict(Counter(left.dependency_shape) + Counter(_graph_shape(left_graph)))
    right_shape = dict(Counter(right.dependency_shape) + Counter(_graph_shape(right_graph)))
    return _cosine_similarity(left_shape, right_shape)


def _dependency_graph(edges: set[tuple[str, str, str]]) -> nx.MultiDiGraph:
    graph = nx.MultiDiGraph()
    for source, target, kind in edges:
        graph.add_edge(source, target, kind=kind)
    return graph


def _graph_shape(graph: nx.MultiDiGraph) -> dict[str, int]:
    if graph.number_of_nodes() == 0:
        return {}
    weak_components = nx.number_weakly_connected_components(graph)
    return {
        "graph:nodes": graph.number_of_nodes(),
        "graph:edges": graph.number_of_edges(),
        "graph:weak-components": weak_components,
    }


def _table_exists(connection: sqlite3.Connection, table: str) -> bool:
    row = connection.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name = ?",
        (table,),
    ).fetchone()
    return row is not None
