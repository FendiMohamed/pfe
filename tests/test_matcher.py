from __future__ import annotations

import sqlite3
from dataclasses import replace

from apk_sbom.dex_analyzer import ApkDexAnalysis, DexFileFeatures
from apk_sbom.maven_downloader import MavenPomDependency
from apk_sbom.matcher import (
    FeatureSet,
    MatchCandidate,
    OverlapEvidence,
    ReferenceComponentFeatures,
    VersionDecision,
    build_version_decisions,
    classify_identity_candidate,
    classify_version_candidate,
    detected_libraries_from_match_summary,
    feature_set_from_apk_analysis,
    identity_confidence_score,
    match_apk_to_reference_db,
    reportable_version_decisions,
    score_reference_component,
)
from apk_sbom.reference_features import initialize_feature_db


def test_score_reference_component_uses_reference_coverage():
    apk_features = FeatureSet(
        packages={"com.google.gson", "com.example.app"},
        classes={
            "Lcom/google/gson/Gson;",
            "Lcom/google/gson/JsonElement;",
            "Lcom/example/app/MainActivity;",
        },
        methods={
            "Lcom/google/gson/Gson;-><init>()V",
            "Lcom/google/gson/Gson;->toJson(Ljava/lang/Object;)Ljava/lang/String;",
        },
    )
    reference = ReferenceComponentFeatures(
        component_id=1,
        coordinate="com.google.code.gson:gson",
        group_id="com.google.code.gson",
        artifact_id="gson",
        version="2.8.9",
        purl="pkg:maven/com.google.code.gson/gson@2.8.9",
        features=FeatureSet(
            packages={"com.google.gson"},
            classes={
                "Lcom/google/gson/Gson;",
                "Lcom/google/gson/JsonElement;",
                "Lcom/google/gson/MissingClass;",
            },
            methods={
                "Lcom/google/gson/Gson;-><init>()V",
                "Lcom/google/gson/JsonElement;->isJsonObject()Z",
            },
        ),
    )

    candidate = score_reference_component(
        apk_features,
        reference,
        opcode_weight=0.0,
        dependency_weight=0.0,
        literal_weight=0.0,
        unique_version_weight=0.0,
    )

    assert candidate.score == 0.676471
    assert candidate.evidence.package_score == 1.0
    assert candidate.evidence.class_score == 0.666667
    assert candidate.evidence.method_score == 0.5
    assert candidate.evidence.opcode_score == 0.0


def test_score_reference_component_can_use_opcode_similarity():
    apk_features = FeatureSet(
        packages=set(),
        classes=set(),
        methods=set(),
        opcode_histogram={"invoke-virtual": 3, "return-void": 4},
    )
    reference = ReferenceComponentFeatures(
        component_id=1,
        coordinate="com.google.code.gson:gson",
        group_id="com.google.code.gson",
        artifact_id="gson",
        version="2.8.9",
        purl="pkg:maven/com.google.code.gson/gson@2.8.9",
        features=FeatureSet(
            packages=set(),
            classes=set(),
            methods=set(),
            opcode_histogram={"invoke-virtual": 3, "return-void": 4},
        ),
    )

    candidate = score_reference_component(
        apk_features,
        reference,
        package_weight=0.0,
        class_weight=0.0,
        method_weight=0.0,
        opcode_weight=1.0,
        dependency_weight=0.0,
        literal_weight=0.0,
        unique_version_weight=0.0,
    )

    assert candidate.score == 1.0
    assert candidate.evidence.shared_opcodes == 2
    assert candidate.evidence.opcode_score == 1.0


def test_score_reference_component_can_use_opcode_ngram_similarity():
    apk_features = FeatureSet(
        packages=set(),
        classes=set(),
        methods=set(),
        opcode_ngrams={
            "const/4|invoke-virtual|move-result-object": 2,
            "invoke-virtual|move-result-object|return-object": 1,
        },
    )
    reference = ReferenceComponentFeatures(
        component_id=1,
        coordinate="com.google.code.gson:gson",
        group_id="com.google.code.gson",
        artifact_id="gson",
        version="2.8.9",
        purl="pkg:maven/com.google.code.gson/gson@2.8.9",
        features=FeatureSet(
            packages=set(),
            classes=set(),
            methods=set(),
            opcode_ngrams={
                "const/4|invoke-virtual|move-result-object": 2,
                "invoke-virtual|move-result-object|return-object": 1,
            },
        ),
    )

    candidate = score_reference_component(
        apk_features,
        reference,
        package_weight=0.0,
        class_weight=0.0,
        method_weight=0.0,
        opcode_weight=0.0,
        dependency_weight=0.0,
        literal_weight=0.0,
        unique_version_weight=0.0,
        opcode_ngram_weight=1.0,
    )

    assert candidate.score == 1.0
    assert candidate.evidence.shared_opcode_ngrams == 2
    assert candidate.evidence.opcode_ngram_score == 1.0


def test_score_reference_component_can_use_api_reference_overlap():
    apk_features = FeatureSet(
        packages=set(),
        classes=set(),
        methods=set(),
        api_references={
            "Landroid/content/Context;->getPackageName()Ljava/lang/String;",
        },
    )
    reference = ReferenceComponentFeatures(
        component_id=1,
        coordinate="com.google.code.gson:gson",
        group_id="com.google.code.gson",
        artifact_id="gson",
        version="2.8.9",
        purl="pkg:maven/com.google.code.gson/gson@2.8.9",
        features=FeatureSet(
            packages=set(),
            classes=set(),
            methods=set(),
            api_references={
                "Landroid/content/Context;->getPackageName()Ljava/lang/String;",
                "Ljava/lang/String;->valueOf(Ljava/lang/Object;)Ljava/lang/String;",
            },
        ),
    )

    candidate = score_reference_component(
        apk_features,
        reference,
        package_weight=0.0,
        class_weight=0.0,
        method_weight=0.0,
        opcode_weight=0.0,
        dependency_weight=0.0,
        literal_weight=0.0,
        unique_version_weight=0.0,
        api_reference_weight=1.0,
    )

    assert candidate.score == 0.5
    assert candidate.evidence.matched_api_references == 1
    assert candidate.evidence.reference_api_references == 2
    assert candidate.evidence.api_reference_score == 0.5


def test_inert_multiscale_features_do_not_change_default_score():
    apk_features = FeatureSet(
        packages={"com.google.gson"},
        classes={"Lcom/google/gson/Gson;"},
        methods={"Lcom/google/gson/Gson;-><init>()V"},
    )
    reference = ReferenceComponentFeatures(
        component_id=1,
        coordinate="com.google.code.gson:gson",
        group_id="com.google.code.gson",
        artifact_id="gson",
        version="2.8.9",
        purl="pkg:maven/com.google.code.gson/gson@2.8.9",
        features=FeatureSet(
            packages={"com.google.gson"},
            classes={"Lcom/google/gson/Gson;"},
            methods={"Lcom/google/gson/Gson;-><init>()V"},
        ),
    )
    baseline = score_reference_component(
        apk_features,
        reference,
        opcode_weight=0.0,
        dependency_weight=0.0,
        literal_weight=0.0,
        unique_version_weight=0.0,
    )

    candidate = score_reference_component(
        replace(
            apk_features,
            basic_block_opcode_fingerprints={"bb:1:apk-only": 2},
            call_chain_opcode_fingerprints={"call:1:apk-only": 1},
            class_neighbor_summaries={"in:0|out:0": 1},
            field_operation_sequences={"fieldops:1:apk-only": 1},
            literal_context_features={"literal-context:apkonly"},
        ),
        replace(
            reference,
            features=replace(
                reference.features,
                basic_block_opcode_fingerprints={"bb:1:ref-only": 4},
                call_chain_opcode_fingerprints={"call:1:ref-only": 1},
                class_neighbor_summaries={"in:1|out:0": 1},
                field_operation_sequences={"fieldops:1:ref-only": 1},
                literal_context_features={"literal-context:refonly"},
            ),
        ),
        opcode_weight=0.0,
        dependency_weight=0.0,
        literal_weight=0.0,
        unique_version_weight=0.0,
    )

    assert candidate.score == baseline.score
    assert candidate.evidence == baseline.evidence


def test_feature_set_from_apk_analysis_aggregates_inert_multiscale_features():
    analysis = ApkDexAnalysis(
        apk_path="sample.apk",
        dex_files_analyzed=1,
        dex_files_failed=0,
        classes_count=1,
        methods_count=1,
        packages=["com.google.gson"],
        opcode_histogram={},
        opcode_ngrams={},
        dex_files=[
            DexFileFeatures(
                dex_file="classes.dex",
                classes_count=1,
                methods_count=1,
                packages=["com.google.gson"],
                class_descriptors=["Lcom/google/gson/Gson;"],
                method_signatures=["Lcom/google/gson/Gson;-><init>()V"],
                opcode_histogram={},
                basic_block_opcode_fingerprints={"bb:2:abc": 2},
                call_chain_opcode_fingerprints={"call:1:def": 1},
                class_neighbor_summaries={"in:0|out:0": 1},
                field_operation_sequences={"fieldops:1:fed": 1},
                literal_context_features=["literal-context:1234567890abcdef"],
            )
        ],
        parse_errors=[],
    )

    features = feature_set_from_apk_analysis(analysis)

    assert features.basic_block_opcode_fingerprints == {"bb:2:abc": 2}
    assert features.call_chain_opcode_fingerprints == {"call:1:def": 1}
    assert features.class_neighbor_summaries == {"in:0|out:0": 1}
    assert features.field_operation_sequences == {"fieldops:1:fed": 1}
    assert features.literal_context_features == {"literal-context:1234567890abcdef"}


def test_match_apk_to_reference_db_ranks_matching_version_first(monkeypatch, tmp_path):
    db_path = tmp_path / "reference.sqlite"
    initialize_feature_db(db_path)
    with sqlite3.connect(db_path) as connection:
        first_component_id = insert_component(
            connection,
            coordinate="com.google.code.gson:gson",
            version="2.8.6",
        )
        insert_features(
            connection,
            first_component_id,
            packages={"com.google.gson"},
            classes={
                "Lcom/google/gson/Gson;",
                "Lcom/google/gson/OldOnly;",
            },
            methods={
                "Lcom/google/gson/Gson;-><init>()V",
                "Lcom/google/gson/OldOnly;->legacy()V",
            },
        )
        second_component_id = insert_component(
            connection,
            coordinate="com.google.code.gson:gson",
            version="2.8.9",
        )
        connection.execute(
            """
            INSERT INTO maven_dependencies(
                component_id, group_id, artifact_id, coordinate, version, optional
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                second_component_id,
                "com.squareup.okio",
                "okio-jvm",
                "com.squareup.okio:okio-jvm",
                "3.7.0",
                0,
            ),
        )
        insert_features(
            connection,
            second_component_id,
            packages={"com.google.gson"},
            classes={
                "Lcom/google/gson/Gson;",
                "Lcom/google/gson/JsonElement;",
            },
            methods={
                "Lcom/google/gson/Gson;-><init>()V",
                "Lcom/google/gson/JsonElement;->isJsonObject()Z",
            },
        )

    def fake_analyze_apk_dex(apk_path: str, *, include_members: bool = False):
        assert apk_path == "sample.apk"
        assert include_members is True
        return ApkDexAnalysis(
            apk_path=apk_path,
            dex_files_analyzed=1,
            dex_files_failed=0,
            classes_count=3,
            methods_count=2,
            packages=["com.example.app", "com.google.gson"],
            opcode_histogram={},
            opcode_ngrams={},
            dex_files=[
                DexFileFeatures(
                    dex_file="classes.dex",
                    classes_count=3,
                    methods_count=2,
                    packages=["com.example.app", "com.google.gson"],
                    class_descriptors=[
                        "Lcom/example/app/MainActivity;",
                        "Lcom/google/gson/Gson;",
                        "Lcom/google/gson/JsonElement;",
                    ],
                    method_signatures=[
                        "Lcom/google/gson/Gson;-><init>()V",
                        "Lcom/google/gson/JsonElement;->isJsonObject()Z",
                    ],
                    opcode_histogram={},
                    opcode_ngrams={},
                    basic_block_opcode_fingerprints={"bb:2:abc": 2},
                    call_chain_opcode_fingerprints={"call:1:def": 1},
                    class_neighbor_summaries={"in:0|out:0": 3},
                    field_operation_sequences={"fieldops:1:fed": 1},
                    literal_context_features=["literal-context:1234567890abcdef"],
                )
            ],
            parse_errors=[],
        )

    monkeypatch.setattr("apk_sbom.matcher.analyze_apk_dex", fake_analyze_apk_dex)

    summary = match_apk_to_reference_db(
        "sample.apk",
        db_path=db_path,
        coordinate="com.google.code.gson:gson",
        min_score=0.0,
        top=2,
        opcode_weight=0.0,
        dependency_weight=0.0,
        literal_weight=0.0,
        unique_version_weight=0.0,
    )

    assert summary.dex_files_analyzed == 1
    assert summary.apk_classes == 3
    assert [candidate.version for candidate in summary.candidates] == ["2.8.9", "2.8.6"]
    assert summary.candidates[0].score == 1.0
    assert summary.candidates[0].maven_dependencies[0].coordinate == "com.squareup.okio:okio-jvm"
    assert summary.candidates[1].score == 0.588235
    assert len(summary.decisions) == 1
    assert summary.decisions[0].selected_version == "2.8.9"
    assert summary.decisions[0].confidence_label == "high"
    assert summary.decisions[0].version_decision == "exact"
    assert summary.decisions[0].identity_confidence_label == "high"
    assert summary.decisions[0].identity_status == "confirmed"
    assert summary.decisions[0].version_confidence_label == "high"
    assert summary.decisions[0].version_status == "exact"
    assert summary.decisions[0].reference_versions_considered == 2
    assert summary.decisions[0].alternatives[0].version == "2.8.6"
    assert summary.composite_family_shortlist_enabled is True
    assert summary.composite_family_shortlist_summary["scoring_status"] == "enabled"
    assert summary.inert_multiscale_features["scoring_status"] == "disabled"
    assert (
        summary.inert_multiscale_features["apk"]["basic_block_opcode_fingerprints"]["distinct"]
        == 1
    )
    assert (
        summary.inert_multiscale_features["reference"]["basic_block_opcode_fingerprints"][
            "components_with_features"
        ]
        == 0
    )


def test_match_apk_to_reference_db_opt_in_composite_shortlist_prunes_noise_family(
    monkeypatch,
    tmp_path,
):
    db_path = tmp_path / "reference.sqlite"
    initialize_feature_db(db_path)
    with sqlite3.connect(db_path) as connection:
        first_component_id = insert_component(
            connection,
            coordinate="example:target",
            version="1.0.0",
        )
        insert_features(
            connection,
            first_component_id,
            packages={"target"},
            classes={"Ltarget/Api;"},
            methods={"Ltarget/Api;->run()V"},
        )
        second_component_id = insert_component(
            connection,
            coordinate="example:target",
            version="2.0.0",
        )
        insert_features(
            connection,
            second_component_id,
            packages={"target"},
            classes={"Ltarget/Api;"},
            methods={"Ltarget/Api;->run()V"},
        )
        noise_component_id = insert_component(
            connection,
            coordinate="example:noise",
            version="1.0.0",
        )
        insert_features(
            connection,
            noise_component_id,
            packages={"noise"},
            classes={"Lnoise/Api;"},
            methods={"Lnoise/Api;->run()V"},
        )

    def fake_analyze_apk_dex(apk_path: str, *, include_members: bool = False):
        assert apk_path == "sample.apk"
        assert include_members is True
        return ApkDexAnalysis(
            apk_path=apk_path,
            dex_files_analyzed=1,
            dex_files_failed=0,
            classes_count=1,
            methods_count=1,
            packages=["target"],
            opcode_histogram={},
            opcode_ngrams={},
            dex_files=[
                DexFileFeatures(
                    dex_file="classes.dex",
                    classes_count=1,
                    methods_count=1,
                    packages=["target"],
                    class_descriptors=["Ltarget/Api;"],
                    method_signatures=["Ltarget/Api;->run()V"],
                    opcode_histogram={},
                    opcode_ngrams={},
                )
            ],
            parse_errors=[],
        )

    monkeypatch.setattr("apk_sbom.matcher.analyze_apk_dex", fake_analyze_apk_dex)

    baseline_summary = match_apk_to_reference_db(
        "sample.apk",
        db_path=db_path,
        min_score=0.0,
        top=None,
        opcode_weight=0.0,
        dependency_weight=0.0,
        literal_weight=0.0,
        unique_version_weight=0.0,
        enable_composite_family_shortlist=False,
    )
    default_summary = match_apk_to_reference_db(
        "sample.apk",
        db_path=db_path,
        min_score=0.0,
        top=None,
        opcode_weight=0.0,
        dependency_weight=0.0,
        literal_weight=0.0,
        unique_version_weight=0.0,
    )

    assert {candidate.coordinate for candidate in baseline_summary.candidates} == {
        "example:noise",
        "example:target",
    }
    assert baseline_summary.composite_family_shortlist_enabled is False
    assert baseline_summary.composite_family_shortlist_summary["scoring_status"] == "disabled"
    assert [candidate.coordinate for candidate in default_summary.candidates] == [
        "example:target",
        "example:target",
    ]
    assert default_summary.composite_family_shortlist_enabled is True
    shortlist = default_summary.composite_family_shortlist_summary
    assert shortlist["scoring_status"] == "enabled"
    assert shortlist["reference_rows_before"] == 3
    assert shortlist["reference_rows_retained"] == 2
    assert shortlist["reference_rows_removed"] == 1
    assert shortlist["coordinate_families_removed"] == 1
    assert default_summary.decisions[0].reference_versions_considered == 2


def test_score_reference_component_uses_version_unique_tie_breakers():
    apk_features = FeatureSet(
        packages={"com.google.gson"},
        classes={"Lcom/google/gson/NewIn289;"},
        methods={"Lcom/google/gson/NewIn289;->newMethod()V"},
        string_literals={"new literal"},
    )
    sibling = FeatureSet(
        packages={"com.google.gson"},
        classes={"Lcom/google/gson/Shared;"},
        methods={"Lcom/google/gson/Shared;->shared()V"},
        string_literals={"shared literal"},
    )
    reference = ReferenceComponentFeatures(
        component_id=1,
        coordinate="com.google.code.gson:gson",
        group_id="com.google.code.gson",
        artifact_id="gson",
        version="2.8.9",
        purl="pkg:maven/com.google.code.gson/gson@2.8.9",
        features=FeatureSet(
            packages={"com.google.gson"},
            classes={"Lcom/google/gson/Shared;", "Lcom/google/gson/NewIn289;"},
            methods={
                "Lcom/google/gson/Shared;->shared()V",
                "Lcom/google/gson/NewIn289;->newMethod()V",
            },
            string_literals={"shared literal", "new literal"},
        ),
    )

    candidate = score_reference_component(
        apk_features,
        reference,
        sibling_features=[sibling],
        package_weight=0.0,
        class_weight=0.0,
        method_weight=0.0,
        opcode_weight=0.0,
        dependency_weight=0.0,
        literal_weight=0.0,
        unique_version_weight=1.0,
    )

    assert candidate.score == 1.0
    assert candidate.evidence.reference_unique_classes == 1
    assert candidate.evidence.reference_unique_methods == 1
    assert candidate.evidence.reference_unique_literals == 1
    assert candidate.evidence.unique_version_score == 1.0


def test_score_reference_component_extracts_version_unique_literal_context_evidence():
    apk_features = FeatureSet(
        packages={"com.example"},
        classes=set(),
        methods=set(),
        literal_context_features={"ctx:shared", "ctx:version-1-1"},
    )
    sibling = FeatureSet(
        packages={"com.example"},
        classes=set(),
        methods=set(),
        literal_context_features={"ctx:shared"},
    )
    reference = ReferenceComponentFeatures(
        component_id=1,
        coordinate="com.example:library",
        group_id="com.example",
        artifact_id="library",
        version="1.1.0",
        purl="pkg:maven/com.example/library@1.1.0",
        features=FeatureSet(
            packages={"com.example"},
            classes=set(),
            methods=set(),
            literal_context_features={"ctx:shared", "ctx:version-1-1"},
        ),
    )

    candidate = score_reference_component(
        apk_features,
        reference,
        sibling_features=[sibling],
        package_weight=1.0,
        class_weight=0.0,
        method_weight=0.0,
        opcode_weight=0.0,
        dependency_weight=0.0,
        literal_weight=0.0,
        unique_version_weight=0.0,
    )

    assert candidate.evidence.matched_unique_literal_context_features == 1
    assert candidate.evidence.reference_unique_literal_context_features == 1
    assert candidate.evidence.unique_literal_context_score == 1.0


def test_classify_version_candidate_allows_low_confidence_obfuscation_candidate():
    candidate = MatchCandidate(
        coordinate="com.google.code.gson:gson",
        group_id="com.google.code.gson",
        artifact_id="gson",
        version="2.8.9",
        purl="pkg:maven/com.google.code.gson/gson@2.8.9",
        score=0.20,
        evidence=OverlapEvidence(
            matched_packages=0,
            reference_packages=9,
            apk_packages=9,
            package_score=0.0,
            matched_classes=0,
            reference_classes=195,
            apk_classes=156,
            class_score=0.0,
            matched_methods=0,
            reference_methods=1086,
            apk_methods=544,
            method_score=0.0,
            shared_opcodes=98,
            reference_distinct_opcodes=111,
            reference_opcode_total=14964,
            apk_distinct_opcodes=98,
            apk_opcode_total=9194,
            opcode_score=0.98,
            shared_opcode_ngrams=620,
            reference_distinct_opcode_ngrams=800,
            reference_opcode_ngram_total=14000,
            apk_distinct_opcode_ngrams=640,
            apk_opcode_ngram_total=9000,
            opcode_ngram_score=0.97,
            matched_dependency_edges=0,
            reference_dependency_edges=574,
            apk_dependency_edges=410,
            dependency_edge_score=0.0,
            reference_dependency_shape_bins=14,
            apk_dependency_shape_bins=14,
            dependency_shape_score=0.99,
            dependency_score=0.35,
            matched_string_literals=152,
            reference_string_literals=206,
            apk_string_literals=155,
            literal_score=0.74,
            matched_api_references=0,
            reference_api_references=0,
            apk_api_references=0,
            api_reference_score=0.0,
            matched_unique_classes=0,
            reference_unique_classes=24,
            unique_class_score=0.0,
            matched_unique_methods=0,
            reference_unique_methods=145,
            unique_method_score=0.0,
            matched_unique_literals=9,
            reference_unique_literals=12,
            unique_literal_score=0.75,
            unique_version_score=0.15,
        ),
    )

    assert classify_version_candidate(candidate, gap_to_next=0.01) == ("low", "candidate")
    assert classify_identity_candidate(candidate) == ("low", "candidate")


def test_identity_confidence_is_separate_from_version_confidence():
    candidate = make_candidate(
        coordinate="androidx.core:core",
        version="1.18.0",
        score=0.80,
        evidence=replace(
            make_overlap_evidence(),
            class_score=0.90,
            method_score=0.80,
            opcode_score=0.80,
            reference_unique_classes=0,
            reference_unique_methods=0,
            reference_unique_literals=0,
            unique_version_score=0.0,
        ),
    )

    decision = build_version_decisions([candidate])[0]

    assert identity_confidence_score(candidate) >= 0.80
    assert decision.identity_status == "likely"
    assert decision.identity_confidence_label == "medium"
    assert decision.version_status == "candidate"
    assert decision.version_confidence_label == "low"


def test_build_version_decisions_caps_single_reference_version_likely_claim():
    candidate = make_candidate(
        coordinate="androidx.core:core",
        version="1.18.0",
        score=0.80,
        evidence=replace(
            make_overlap_evidence(),
            class_score=0.90,
            method_score=0.80,
            opcode_score=0.80,
        ),
    )

    decision = build_version_decisions([candidate])[0]

    assert decision.reference_versions_considered == 1
    assert decision.confidence_label == "low"
    assert decision.version_decision == "candidate"


def test_build_version_decisions_keeps_complete_single_reference_version_exact():
    candidate = make_candidate(
        coordinate="com.google.code.gson:gson",
        version="2.8.9",
        score=1.0,
        evidence=make_overlap_evidence(),
    )

    decision = build_version_decisions([candidate])[0]

    assert decision.reference_versions_considered == 1
    assert decision.confidence_label == "high"
    assert decision.version_decision == "exact"


def test_build_version_decisions_prefers_distinctive_version_within_score_margin():
    raw_leader = make_candidate(
        coordinate="androidx.swiperefreshlayout:swiperefreshlayout",
        version="1.0.0",
        score=0.623357,
        evidence=replace(
            make_overlap_evidence(),
            class_score=0.611111,
            method_score=0.447368,
            dependency_score=0.684419,
            unique_version_score=0.0,
            matched_unique_methods=0,
            reference_unique_methods=2,
        ),
    )
    distinctive = make_candidate(
        coordinate="androidx.swiperefreshlayout:swiperefreshlayout",
        version="1.2.0",
        score=0.567867,
        evidence=replace(
            make_overlap_evidence(),
            class_score=0.545455,
            method_score=0.436937,
            dependency_score=0.654781,
            matched_unique_classes=1,
            reference_unique_classes=4,
            matched_unique_methods=12,
            reference_unique_methods=34,
            unique_version_score=0.307904,
        ),
    )

    decision = build_version_decisions([raw_leader, distinctive])[0]

    assert decision.selected_version == "1.2.0"
    assert decision.alternatives[0].version == "1.0.0"
    assert decision.version_selection_reason is not None
    assert "version-distinctive" in decision.version_selection_reason


def test_default_context_reranker_prefers_supported_near_tie_with_disable_escape():
    raw_leader = make_candidate(
        coordinate="androidx.recyclerview:recyclerview",
        version="1.2.1",
        score=0.887249,
        evidence=replace(
            make_overlap_evidence(),
            matched_unique_literal_context_features=0,
            reference_unique_literal_context_features=0,
            unique_literal_context_score=0.0,
        ),
    )
    supported = make_candidate(
        coordinate="androidx.recyclerview:recyclerview",
        version="1.3.2",
        score=0.886286,
        evidence=replace(
            make_overlap_evidence(),
            matched_unique_literal_context_features=7,
            reference_unique_literal_context_features=9,
            unique_literal_context_score=0.777778,
        ),
    )
    newer = make_candidate(
        coordinate="androidx.recyclerview:recyclerview",
        version="1.4.0",
        score=0.879093,
        evidence=replace(
            make_overlap_evidence(),
            matched_unique_literal_context_features=0,
            reference_unique_literal_context_features=27,
            unique_literal_context_score=0.0,
        ),
    )

    default_decision = build_version_decisions([raw_leader, supported, newer])[0]
    disabled_decision = build_version_decisions(
        [raw_leader, supported, newer],
        enable_version_unique_literal_context_reranker=False,
    )[0]
    explicit_enabled_decision = build_version_decisions(
        [raw_leader, supported, newer],
        enable_version_unique_literal_context_reranker=True,
    )[0]

    assert default_decision.selected_version == "1.3.2"
    assert default_decision.version_selection_reason is not None
    assert "version-unique literal/context evidence" in default_decision.version_selection_reason
    assert disabled_decision.selected_version == "1.2.1"
    assert disabled_decision.version_selection_reason is None
    assert explicit_enabled_decision.selected_version == "1.3.2"


def test_opt_in_context_reranker_does_not_flip_single_match():
    raw_leader = make_candidate(
        coordinate="androidx.gridlayout:gridlayout",
        version="1.0.0",
        score=0.70,
        evidence=make_overlap_evidence(),
    )
    single_match = make_candidate(
        coordinate="androidx.gridlayout:gridlayout",
        version="1.1.0",
        score=0.699,
        evidence=replace(
            make_overlap_evidence(),
            matched_unique_literal_context_features=1,
            reference_unique_literal_context_features=1,
            unique_literal_context_score=1.0,
        ),
    )

    decision = build_version_decisions(
        [raw_leader, single_match],
        enable_version_unique_literal_context_reranker=True,
    )[0]

    assert decision.selected_version == "1.0.0"
    assert decision.version_selection_reason is None


def test_build_version_decisions_does_not_flip_near_tie_without_distinctive_evidence():
    source_version = make_candidate(
        coordinate="androidx.concurrent:concurrent-futures",
        version="1.1.0",
        score=0.679934,
        evidence=replace(
            make_overlap_evidence(),
            class_score=0.7,
            method_score=0.514851,
            literal_score=0.975,
            dependency_score=0.717037,
            unique_version_score=0.0,
        ),
    )
    newer = make_candidate(
        coordinate="androidx.concurrent:concurrent-futures",
        version="1.3.0",
        score=0.678989,
        evidence=replace(
            make_overlap_evidence(),
            class_score=0.7,
            method_score=0.509804,
            literal_score=0.975,
            dependency_score=0.717037,
            matched_unique_methods=0,
            reference_unique_methods=1,
            unique_version_score=0.0,
        ),
    )

    decision = build_version_decisions([source_version, newer])[0]

    assert decision.selected_version == "1.1.0"
    assert decision.version_selection_reason is None
    assert decision.version_ambiguity_reason is not None
    assert "Version near-tie" in decision.version_ambiguity_reason
    assert [candidate.version for candidate in decision.ambiguous_versions] == [
        "1.1.0",
        "1.3.0",
    ]


def test_build_version_decisions_does_not_mark_near_tie_with_unique_evidence():
    selected = make_candidate(
        coordinate="androidx.example:example",
        version="1.0.0",
        score=0.610,
        evidence=replace(
            make_overlap_evidence(),
            matched_unique_methods=1,
            reference_unique_methods=2,
            unique_method_score=0.5,
            unique_version_score=0.25,
        ),
    )
    alternative = make_candidate(
        coordinate="androidx.example:example",
        version="1.1.0",
        score=0.606,
        evidence=replace(
            make_overlap_evidence(),
            matched_unique_methods=0,
            reference_unique_methods=2,
            unique_method_score=0.0,
            unique_version_score=0.0,
        ),
    )

    decision = build_version_decisions([selected, alternative])[0]

    assert decision.selected_version == "1.0.0"
    assert decision.version_ambiguity_reason is None
    assert decision.ambiguous_versions == []


def test_build_version_decisions_marks_feature_equivalent_version_tie():
    selected = make_candidate(
        coordinate="androidx.startup:startup-runtime",
        version="1.1.1",
        score=0.548511,
        evidence=replace(
            make_overlap_evidence(),
            class_score=0.6,
            method_score=0.5,
            dependency_score=0.060123,
            literal_score=0.5,
            api_reference_score=0.8,
            matched_unique_classes=0,
            matched_unique_methods=0,
            matched_unique_literals=0,
            unique_version_score=0.0,
        ),
    )
    equivalent = make_candidate(
        coordinate="androidx.startup:startup-runtime",
        version="1.2.0",
        score=0.547856,
        evidence=replace(
            make_overlap_evidence(),
            class_score=0.6,
            method_score=0.5,
            dependency_score=0.060123,
            literal_score=0.5,
            api_reference_score=0.8,
            matched_unique_classes=0,
            matched_unique_methods=0,
            matched_unique_literals=0,
            unique_version_score=0.0,
        ),
    )

    decision = build_version_decisions([selected, equivalent])[0]
    detected = detected_libraries_from_match_summary(make_match_summary_for_decisions([decision]))

    assert decision.selected_version == "1.1.1"
    assert decision.version_ambiguity_reason is not None
    assert "Version ambiguity" in decision.version_ambiguity_reason
    assert [candidate.version for candidate in decision.ambiguous_versions] == [
        "1.1.1",
        "1.2.0",
    ]
    assert any(item.source == "version-ambiguity" for item in detected[0].evidence)
    assert detected[0].ambiguous_versions == ["1.1.1", "1.2.0"]


def test_build_version_decisions_prefers_pom_coherent_candidate_with_independent_support():
    raw_leader = make_candidate(
        coordinate="androidx.example:example-runtime",
        version="1.0.0",
        score=0.602,
        evidence=replace(
            make_overlap_evidence(),
            class_score=0.50,
            method_score=0.45,
        ),
        maven_dependencies=[
            MavenPomDependency(
                group="androidx.annotation",
                artifact="annotation",
                version="1.1.0",
                scope="runtime",
            )
        ],
    )
    pom_coherent = make_candidate(
        coordinate="androidx.example:example-runtime",
        version="1.1.0",
        score=0.575,
        evidence=replace(
            make_overlap_evidence(),
            class_score=0.49,
            method_score=0.44,
        ),
        maven_dependencies=[
            MavenPomDependency(
                group="androidx.annotation",
                artifact="annotation",
                version="1.8.1",
                scope="runtime",
            )
        ],
    )
    annotation = make_candidate(
        coordinate="androidx.annotation:annotation",
        version="1.8.1",
        score=0.91,
        evidence=replace(
            make_overlap_evidence(),
            class_score=0.90,
            method_score=0.88,
        ),
    )

    decisions = build_version_decisions([raw_leader, pom_coherent, annotation])
    by_coordinate = {decision.coordinate: decision for decision in decisions}

    assert by_coordinate["androidx.example:example-runtime"].selected_version == "1.1.0"
    assert by_coordinate["androidx.example:example-runtime"].version_selection_reason is not None
    assert "Maven POM dependencies" in (
        by_coordinate["androidx.example:example-runtime"].version_selection_reason
    )


def test_build_version_decisions_does_not_use_pom_without_independent_support():
    raw_leader = make_candidate(
        coordinate="androidx.example:example-runtime",
        version="1.0.0",
        score=0.602,
        evidence=make_overlap_evidence(),
        maven_dependencies=[
            MavenPomDependency(
                group="androidx.annotation",
                artifact="annotation",
                version="1.1.0",
                scope="runtime",
            )
        ],
    )
    unsupported = make_candidate(
        coordinate="androidx.example:example-runtime",
        version="1.1.0",
        score=0.575,
        evidence=make_overlap_evidence(),
        maven_dependencies=[
            MavenPomDependency(
                group="androidx.annotation",
                artifact="annotation",
                version="1.8.1",
                scope="runtime",
            )
        ],
    )

    decision = build_version_decisions([raw_leader, unsupported])[0]

    assert decision.selected_version == "1.0.0"
    assert decision.version_selection_reason is None


def test_build_version_decisions_prefers_app_era_coherent_compose_runtime():
    raw_leader = make_candidate(
        coordinate="androidx.compose.runtime:runtime-android",
        version="1.11.2",
        score=0.610,
        evidence=make_overlap_evidence(),
    )
    coherent = make_candidate(
        coordinate="androidx.compose.runtime:runtime-android",
        version="1.10.6",
        score=0.535,
        evidence=make_overlap_evidence(),
    )
    compose_ui = make_candidate(
        coordinate="androidx.compose.ui:ui-android",
        version="1.10.6",
        score=0.935,
        evidence=make_overlap_evidence(),
    )
    compose_foundation = make_candidate(
        coordinate="androidx.compose.foundation:foundation-android",
        version="1.10.6",
        score=0.790,
        evidence=make_overlap_evidence(),
    )

    decisions = build_version_decisions(
        [raw_leader, coherent, compose_ui, compose_foundation]
    )
    by_coordinate = {decision.coordinate: decision for decision in decisions}

    runtime = by_coordinate["androidx.compose.runtime:runtime-android"]
    assert runtime.selected_version == "1.10.6"
    assert runtime.version_selection_reason is not None
    assert "app-era/dependency coherence" in runtime.version_selection_reason


def test_build_version_decisions_downgrades_unsupported_compose_runtime_candidate():
    runtime = make_candidate(
        coordinate="androidx.compose.runtime:runtime-android",
        version="1.10.6",
        score=0.530,
        evidence=make_overlap_evidence(),
    )
    compose_ui = make_candidate(
        coordinate="androidx.compose.ui:ui-android",
        version="1.7.8",
        score=0.720,
        evidence=make_overlap_evidence(),
    )
    compose_foundation = make_candidate(
        coordinate="androidx.compose.foundation:foundation-android",
        version="1.7.8",
        score=0.700,
        evidence=make_overlap_evidence(),
    )

    decisions = build_version_decisions([runtime, compose_ui, compose_foundation])
    by_coordinate = {decision.coordinate: decision for decision in decisions}

    runtime_decision = by_coordinate["androidx.compose.runtime:runtime-android"]
    assert runtime_decision.selected_version == "1.10.6"
    assert runtime_decision.version_decision == "uncertain"
    assert runtime_decision.confidence_label == "uncertain"
    assert runtime_decision.version_selection_reason is not None
    assert "Downgraded 1.10.6 to uncertain" in runtime_decision.version_selection_reason


def test_classify_version_candidate_allows_low_gap_package_literal_candidate():
    candidate = make_candidate(
        coordinate="androidx.lifecycle:lifecycle-runtime-android",
        version="2.9.4",
        score=0.400602,
        evidence=replace(
            make_overlap_evidence(),
            class_score=0.193548,
            method_score=0.233766,
            package_score=1.0,
            literal_score=0.818182,
            opcode_score=0.886236,
        ),
    )

    assert classify_version_candidate(candidate, gap_to_next=0.001056) == (
        "low",
        "candidate",
    )


def test_reportable_version_decisions_prefers_low_confidence_lifecycle_target_variant():
    public_runtime = make_decision(
        coordinate="androidx.lifecycle:lifecycle-runtime",
        version="2.6.2",
        score=0.526868,
        gap_to_next=0.526868,
        version_decision="candidate",
        confidence_label="low",
    )
    android_runtime = make_decision(
        coordinate="androidx.lifecycle:lifecycle-runtime-android",
        version="2.9.4",
        score=0.400602,
        gap_to_next=0.001056,
        version_decision="candidate",
        confidence_label="low",
    )

    reportable = reportable_version_decisions([public_runtime, android_runtime])

    assert [decision.coordinate for decision, _ in reportable] == [
        "androidx.lifecycle:lifecycle-runtime-android"
    ]
    assert reportable[0][0].selected_version == "2.9.4"
    assert [decision.coordinate for decision in reportable[0][1]] == [
        "androidx.lifecycle:lifecycle-runtime"
    ]


def test_reportable_version_decisions_prefers_okio_jvm_when_scores_are_close():
    legacy_okio = make_decision(
        coordinate="com.squareup.okio:okio",
        version="2.8.0",
        score=0.557,
        gap_to_next=0.016,
        version_decision="candidate",
        confidence_label="low",
    )
    okio_jvm = make_decision(
        coordinate="com.squareup.okio:okio-jvm",
        version="3.7.0",
        score=0.543,
        gap_to_next=0.004,
        version_decision="candidate",
        confidence_label="low",
    )
    okhttp = make_decision(
        coordinate="com.squareup.okhttp3:okhttp",
        version="4.12.0",
        score=0.807,
        gap_to_next=0.074,
        version_decision="likely",
        confidence_label="medium",
    )

    reportable = reportable_version_decisions([legacy_okio, okio_jvm, okhttp])

    assert [decision.coordinate for decision, _ in reportable] == [
        "com.squareup.okhttp3:okhttp",
        "com.squareup.okio:okio-jvm",
    ]
    assert reportable[1][0].selected_version == "3.7.0"
    assert [decision.coordinate for decision in reportable[1][1]] == [
        "com.squareup.okio:okio"
    ]


def test_reportable_version_decisions_prefers_okhttp_android_when_scores_are_close():
    okhttp = make_decision(
        coordinate="com.squareup.okhttp3:okhttp",
        version="4.10.0",
        score=0.455,
        gap_to_next=0.003,
        version_decision="candidate",
        confidence_label="low",
    )
    okhttp_android = make_decision(
        coordinate="com.squareup.okhttp3:okhttp-android",
        version="5.3.2",
        score=0.457,
        gap_to_next=0.457,
        version_decision="candidate",
        confidence_label="low",
    )

    reportable = reportable_version_decisions([okhttp, okhttp_android])

    assert [decision.coordinate for decision, _ in reportable] == [
        "com.squareup.okhttp3:okhttp-android"
    ]
    assert reportable[0][0].selected_version == "5.3.2"
    assert [decision.coordinate for decision in reportable[0][1]] == [
        "com.squareup.okhttp3:okhttp"
    ]


def test_detected_libraries_include_artifact_family_disambiguation_evidence():
    legacy_okio = make_decision(
        coordinate="com.squareup.okio:okio",
        version="2.8.0",
        score=0.557,
        gap_to_next=0.016,
        version_decision="candidate",
        confidence_label="low",
    )
    okio_jvm = make_decision(
        coordinate="com.squareup.okio:okio-jvm",
        version="3.7.0",
        score=0.543,
        gap_to_next=0.004,
        version_decision="candidate",
        confidence_label="low",
    )
    summary = make_match_summary_for_decisions([legacy_okio, okio_jvm])

    detected = detected_libraries_from_match_summary(summary)

    assert [component.coordinate for component in detected] == ["com.squareup.okio:okio-jvm"]
    assert any(
        item.source == "artifact-family-disambiguation"
        and "suppressed overlapping candidate" in item.detail
        and "com.squareup.okio:okio@2.8.0" in item.detail
        for item in detected[0].evidence
    )


def test_reportable_version_decisions_prefers_lifecycle_public_coordinate_when_close():
    runtime_android = make_decision(
        coordinate="androidx.lifecycle:lifecycle-runtime-android",
        version="2.8.7",
        score=0.882,
        gap_to_next=0.007,
        version_decision="candidate",
        confidence_label="low",
    )
    runtime = make_decision(
        coordinate="androidx.lifecycle:lifecycle-runtime",
        version="2.6.2",
        score=0.858,
        gap_to_next=0.858,
        version_decision="candidate",
        confidence_label="low",
    )
    viewmodel_android = make_decision(
        coordinate="androidx.lifecycle:lifecycle-viewmodel-android",
        version="2.8.7",
        score=0.618,
        gap_to_next=0.112,
        version_decision="candidate",
        confidence_label="low",
    )
    viewmodel = make_decision(
        coordinate="androidx.lifecycle:lifecycle-viewmodel",
        version="2.6.2",
        score=0.853,
        gap_to_next=0.853,
        version_decision="candidate",
        confidence_label="low",
    )

    reportable = reportable_version_decisions(
        [runtime_android, runtime, viewmodel_android, viewmodel]
    )

    assert [decision.coordinate for decision, _ in reportable] == [
        "androidx.lifecycle:lifecycle-runtime",
        "androidx.lifecycle:lifecycle-viewmodel",
    ]
    assert [decision.coordinate for decision in reportable[0][1]] == [
        "androidx.lifecycle:lifecycle-runtime-android"
    ]
    assert [decision.coordinate for decision in reportable[1][1]] == [
        "androidx.lifecycle:lifecycle-viewmodel-android"
    ]


def test_reportable_version_decisions_uses_lifecycle_version_coherence_hint():
    runtime = make_decision(
        coordinate="androidx.lifecycle:lifecycle-runtime",
        version="2.6.2",
        score=0.766,
        gap_to_next=0.766,
        version_decision="candidate",
        confidence_label="low",
    )
    runtime_android = make_decision(
        coordinate="androidx.lifecycle:lifecycle-runtime-android",
        version="2.8.7",
        score=0.676,
        gap_to_next=0.090,
        version_decision="candidate",
        confidence_label="low",
    )
    livedata = make_decision(
        coordinate="androidx.lifecycle:lifecycle-livedata",
        version="2.8.7",
        score=0.700,
        gap_to_next=0.050,
        version_decision="candidate",
        confidence_label="low",
    )
    viewmodel_android = make_decision(
        coordinate="androidx.lifecycle:lifecycle-viewmodel-android",
        version="2.8.7",
        score=0.808,
        gap_to_next=0.222,
        version_decision="likely",
        confidence_label="medium",
    )

    reportable = reportable_version_decisions(
        [runtime, runtime_android, livedata, viewmodel_android]
    )

    assert [decision.coordinate for decision, _ in reportable] == [
        "androidx.lifecycle:lifecycle-viewmodel-android",
        "androidx.lifecycle:lifecycle-livedata",
        "androidx.lifecycle:lifecycle-runtime-android",
    ]
    runtime_result = reportable[2]
    assert runtime_result[0].selected_version == "2.8.7"
    assert [decision.coordinate for decision in runtime_result[1]] == [
        "androidx.lifecycle:lifecycle-runtime"
    ]


def test_reportable_version_decisions_allows_uncertain_lifecycle_target_when_identity_is_supported():
    runtime = make_decision(
        coordinate="androidx.lifecycle:lifecycle-runtime",
        version="2.6.2",
        score=0.539,
        gap_to_next=0.539,
        version_decision="candidate",
        confidence_label="low",
    )
    runtime_android = make_decision(
        coordinate="androidx.lifecycle:lifecycle-runtime-android",
        version="2.10.0",
        score=0.422,
        gap_to_next=0.024,
        version_decision="uncertain",
        confidence_label="uncertain",
        identity_status="candidate",
        identity_confidence_label="low",
    )

    reportable = reportable_version_decisions([runtime, runtime_android])

    assert [decision.coordinate for decision, _ in reportable] == [
        "androidx.lifecycle:lifecycle-runtime-android"
    ]
    selected = reportable[0][0]
    assert selected.selected_version == "2.10.0"
    assert selected.version_decision == "candidate"
    assert selected.version_confidence_label == "low"
    assert selected.version_selection_reason == (
        "Selected as a low-confidence candidate by scoped artifact-family coherence."
    )
    assert [decision.coordinate for decision in reportable[0][1]] == [
        "androidx.lifecycle:lifecycle-runtime"
    ]


def test_detected_libraries_include_lifecycle_disambiguation_evidence():
    runtime_android = make_decision(
        coordinate="androidx.lifecycle:lifecycle-runtime-android",
        version="2.8.7",
        score=0.882,
        gap_to_next=0.007,
        version_decision="candidate",
        confidence_label="low",
    )
    runtime = make_decision(
        coordinate="androidx.lifecycle:lifecycle-runtime",
        version="2.6.2",
        score=0.858,
        gap_to_next=0.858,
        version_decision="candidate",
        confidence_label="low",
    )
    summary = make_match_summary_for_decisions([runtime_android, runtime])

    detected = detected_libraries_from_match_summary(summary)

    assert [component.coordinate for component in detected] == [
        "androidx.lifecycle:lifecycle-runtime"
    ]
    assert any(
        item.source == "artifact-family-disambiguation"
        and "androidx.lifecycle:lifecycle-runtime-android@2.8.7" in item.detail
        for item in detected[0].evidence
    )


def insert_component(connection: sqlite3.Connection, *, coordinate: str, version: str) -> int:
    group_id, artifact_id = coordinate.split(":", maxsplit=1)
    purl = f"pkg:maven/{group_id}/{artifact_id}@{version}"
    connection.execute(
        """
        INSERT INTO components(
            coordinate, group_id, artifact_id, version, purl, packaging,
            conversion_status, artifact_path, dex_output_dir, conversion_metadata_path
        )
        VALUES (?, ?, ?, ?, ?, 'jar', 'converted', 'artifact.jar', 'dex', 'conversion.json')
        """,
        (coordinate, group_id, artifact_id, version, purl),
    )
    row = connection.execute(
        "SELECT id FROM components WHERE coordinate = ? AND version = ?",
        (coordinate, version),
    ).fetchone()
    return int(row[0])


def insert_features(
    connection: sqlite3.Connection,
    component_id: int,
    *,
    packages: set[str],
    classes: set[str],
    methods: set[str],
) -> None:
    connection.executemany(
        "INSERT INTO packages(component_id, package) VALUES (?, ?)",
        [(component_id, value) for value in packages],
    )
    connection.executemany(
        "INSERT INTO classes(component_id, class_descriptor) VALUES (?, ?)",
        [(component_id, value) for value in classes],
    )
    connection.executemany(
        "INSERT INTO methods(component_id, method_signature) VALUES (?, ?)",
        [(component_id, value) for value in methods],
    )


def make_decision(
    *,
    coordinate: str,
    version: str,
    score: float,
    gap_to_next: float,
    version_decision: str,
    confidence_label: str,
    identity_status: str | None = None,
    identity_confidence_label: str | None = None,
) -> VersionDecision:
    group_id, artifact_id = coordinate.split(":", maxsplit=1)
    return VersionDecision(
        coordinate=coordinate,
        group_id=group_id,
        artifact_id=artifact_id,
        selected_version=version,
        purl=f"pkg:maven/{group_id}/{artifact_id}@{version}",
        score=score,
        confidence=score,
        confidence_label=confidence_label,
        version_decision=version_decision,
        gap_to_next=gap_to_next,
        reference_versions_considered=1,
        evidence=make_overlap_evidence(),
        alternatives=[],
        identity_status=identity_status,
        identity_confidence_label=identity_confidence_label,
    )


def make_candidate(
    *,
    coordinate: str,
    version: str,
    score: float,
    evidence: OverlapEvidence,
    maven_dependencies: list[MavenPomDependency] | None = None,
) -> MatchCandidate:
    group_id, artifact_id = coordinate.split(":", maxsplit=1)
    return MatchCandidate(
        coordinate=coordinate,
        group_id=group_id,
        artifact_id=artifact_id,
        version=version,
        purl=f"pkg:maven/{group_id}/{artifact_id}@{version}",
        score=score,
        evidence=evidence,
        maven_dependencies=maven_dependencies or [],
    )


def make_match_summary_for_decisions(decisions: list[VersionDecision]) -> object:
    from apk_sbom.matcher import MatchSummary

    return MatchSummary(
        apk_path="sample.apk",
        db_path="reference.sqlite",
        dex_files_analyzed=1,
        dex_files_failed=0,
        apk_packages=1,
        apk_classes=1,
        apk_methods=1,
        apk_distinct_opcodes=1,
        apk_opcode_total=1,
        apk_distinct_opcode_ngrams=1,
        apk_opcode_ngram_total=1,
        apk_dependency_edges=0,
        apk_dependency_shape_bins=0,
        apk_string_literals=0,
        apk_api_references=0,
        package_weight=0.15,
        class_weight=0.45,
        method_weight=0.25,
        opcode_weight=0.15,
        dependency_weight=0.10,
        literal_weight=0.08,
        unique_version_weight=0.12,
        api_reference_weight=0.0,
        opcode_ngram_weight=0.0,
        min_score=0.05,
        candidates=[],
        decisions=decisions,
    )


def make_overlap_evidence() -> OverlapEvidence:
    return OverlapEvidence(
        matched_packages=1,
        reference_packages=1,
        apk_packages=1,
        package_score=1.0,
        matched_classes=1,
        reference_classes=1,
        apk_classes=1,
        class_score=1.0,
        matched_methods=1,
        reference_methods=1,
        apk_methods=1,
        method_score=1.0,
        shared_opcodes=1,
        reference_distinct_opcodes=1,
        reference_opcode_total=1,
        apk_distinct_opcodes=1,
        apk_opcode_total=1,
        opcode_score=1.0,
        shared_opcode_ngrams=1,
        reference_distinct_opcode_ngrams=1,
        reference_opcode_ngram_total=1,
        apk_distinct_opcode_ngrams=1,
        apk_opcode_ngram_total=1,
        opcode_ngram_score=1.0,
        matched_dependency_edges=0,
        reference_dependency_edges=0,
        apk_dependency_edges=0,
        dependency_edge_score=0.0,
        reference_dependency_shape_bins=0,
        apk_dependency_shape_bins=0,
        dependency_shape_score=0.0,
        dependency_score=0.0,
        matched_string_literals=0,
        reference_string_literals=0,
        apk_string_literals=0,
        literal_score=0.0,
        matched_api_references=0,
        reference_api_references=0,
        apk_api_references=0,
        api_reference_score=0.0,
        matched_unique_classes=0,
        reference_unique_classes=0,
        unique_class_score=0.0,
        matched_unique_methods=0,
        reference_unique_methods=0,
        unique_method_score=0.0,
        matched_unique_literals=0,
        reference_unique_literals=0,
        unique_literal_score=0.0,
        unique_version_score=0.0,
    )
