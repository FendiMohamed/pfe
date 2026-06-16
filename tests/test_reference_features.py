from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from apk_sbom.dex_analyzer import DexFileFeatures
from apk_sbom.maven_downloader import MavenPomDependency
from apk_sbom.reference_converter import DexFileRecord, ReferenceConversionResult
from apk_sbom.reference_features import (
    discover_conversion_results,
    extract_reference_features_to_db,
)


def make_conversion(tmp_path, *, status: str = "converted") -> ReferenceConversionResult:
    tmp_path.mkdir(parents=True, exist_ok=True)
    dex_path = tmp_path / "classes.dex"
    dex_path.write_bytes(b"fake dex")
    metadata_path = tmp_path / "conversion.json"
    conversion = ReferenceConversionResult(
        coordinate="com.google.code.gson:gson",
        version="2.8.9",
        purl="pkg:maven/com.google.code.gson/gson@2.8.9",
        packaging="jar",
        status=status,
        artifact_path=str(tmp_path / "gson-2.8.9.jar"),
        output_dir=str(tmp_path),
        metadata_path=str(metadata_path),
        dex_files=[
            DexFileRecord(
                path=str(dex_path),
                sha256="1" * 64,
                size=dex_path.stat().st_size,
            )
        ]
        if status != "skipped"
        else [],
        command=[],
        maven_dependencies=[
            MavenPomDependency(
                group="com.squareup.okio",
                artifact="okio-jvm",
                version="3.7.0",
            )
        ],
    )
    metadata_path.write_text(json.dumps(conversion.to_dict()), encoding="utf-8")
    return conversion


def test_discover_conversion_results_skips_skipped_by_default(tmp_path):
    make_conversion(tmp_path / "converted")
    make_conversion(tmp_path / "skipped", status="skipped")

    results = discover_conversion_results(tmp_path)
    all_results = discover_conversion_results(tmp_path, include_skipped=True)

    assert len(results) == 1
    assert results[0].status == "converted"
    assert len(all_results) == 2


def test_discover_conversion_results_supports_offset(tmp_path):
    first = make_conversion(tmp_path / "a")
    second = make_conversion(tmp_path / "b")
    third = make_conversion(tmp_path / "c")
    assert first.version == second.version == third.version

    results = discover_conversion_results(tmp_path, offset=1, limit=1)

    assert len(results) == 1
    assert Path(results[0].metadata_path).as_posix().endswith("b/conversion.json")


def test_extract_reference_features_to_db(monkeypatch, tmp_path):
    conversion = make_conversion(tmp_path / "converted")

    def fake_analyze_dex_bytes(dex_file: str, data: bytes, *, include_members: bool = False):
        assert include_members is True
        return DexFileFeatures(
            dex_file=dex_file,
            classes_count=2,
            methods_count=3,
            packages=["com.google.gson"],
            class_descriptors=[
                "Lcom/google/gson/Gson;",
                "Lcom/google/gson/JsonElement;",
            ],
            method_signatures=[
                "Lcom/google/gson/Gson;-><init>()V",
                "Lcom/google/gson/Gson;->toJson(Ljava/lang/Object;)Ljava/lang/String;",
                "Lcom/google/gson/JsonElement;->isJsonObject()Z",
            ],
            opcode_histogram={"invoke-virtual": 4, "return-void": 1},
            opcode_ngrams={"invoke-virtual|move-result-object|return-object": 1},
            dependency_shape={"out:0": 1, "out:1": 1},
            string_literals=["2.8.9", "gson"],
            api_references=["Ljava/lang/String;->valueOf(Ljava/lang/Object;)Ljava/lang/String;"],
            basic_block_opcode_fingerprints={"bb:3:abc": 2},
            call_chain_opcode_fingerprints={"call:2:def": 1},
            class_neighbor_summaries={"in:0|out:1|out-field:1": 1},
            field_operation_sequences={"fieldops:2:fed": 1},
            literal_context_features=["literal-context:1234567890abcdef"],
        )

    monkeypatch.setattr("apk_sbom.reference_features.analyze_dex_bytes", fake_analyze_dex_bytes)

    db_path = tmp_path / "features.sqlite"
    summary = extract_reference_features_to_db([conversion], db_path=db_path, reset=True)

    assert summary.components == 1
    assert summary.dex_files == 1
    assert summary.packages == 1
    assert summary.classes == 2
    assert summary.methods == 3
    assert summary.opcodes == 2
    assert summary.opcode_ngrams == 1
    assert summary.class_dependencies == 0
    assert summary.dependency_shapes == 2
    assert summary.string_literals == 2
    assert summary.api_references == 1
    assert summary.basic_block_opcode_fingerprints == 1
    assert summary.call_chain_opcode_fingerprints == 1
    assert summary.class_neighbor_summaries == 1
    assert summary.field_operation_sequences == 1
    assert summary.literal_context_features == 1
    assert summary.results[0].status == "stored"
    assert summary.results[0].basic_block_fingerprints_count == 1
    assert summary.results[0].call_chain_fingerprints_count == 1
    assert summary.results[0].class_neighbor_summaries_count == 1
    assert summary.results[0].field_operation_sequences_count == 1
    assert summary.results[0].literal_context_features_count == 1

    with sqlite3.connect(db_path) as connection:
        row = connection.execute(
            "SELECT coordinate, version, classes_count, methods_count FROM components"
        ).fetchone()
        dependency_row = connection.execute(
            """
            SELECT coordinate, version, optional
            FROM maven_dependencies
            WHERE component_id = (SELECT id FROM components WHERE coordinate = ?)
            """,
            ("com.google.code.gson:gson",),
        ).fetchone()
        api_reference_row = connection.execute(
            """
            SELECT reference
            FROM api_references
            WHERE component_id = (SELECT id FROM components WHERE coordinate = ?)
            """,
            ("com.google.code.gson:gson",),
        ).fetchone()
        opcode_ngram_row = connection.execute(
            """
            SELECT ngram, count
            FROM opcode_ngrams
            WHERE component_id = (SELECT id FROM components WHERE coordinate = ?)
            """,
            ("com.google.code.gson:gson",),
        ).fetchone()
        basic_block_row = connection.execute(
            """
            SELECT fingerprint, count
            FROM basic_block_opcode_fingerprints
            WHERE component_id = (SELECT id FROM components WHERE coordinate = ?)
            """,
            ("com.google.code.gson:gson",),
        ).fetchone()
        call_chain_row = connection.execute(
            """
            SELECT fingerprint, count
            FROM call_chain_opcode_fingerprints
            WHERE component_id = (SELECT id FROM components WHERE coordinate = ?)
            """,
            ("com.google.code.gson:gson",),
        ).fetchone()
        class_neighbor_row = connection.execute(
            """
            SELECT summary, count
            FROM class_neighbor_summaries
            WHERE component_id = (SELECT id FROM components WHERE coordinate = ?)
            """,
            ("com.google.code.gson:gson",),
        ).fetchone()
        field_operation_row = connection.execute(
            """
            SELECT fingerprint, count
            FROM field_operation_sequences
            WHERE component_id = (SELECT id FROM components WHERE coordinate = ?)
            """,
            ("com.google.code.gson:gson",),
        ).fetchone()
        literal_context_row = connection.execute(
            """
            SELECT feature
            FROM literal_context_features
            WHERE component_id = (SELECT id FROM components WHERE coordinate = ?)
            """,
            ("com.google.code.gson:gson",),
        ).fetchone()

    assert row == ("com.google.code.gson:gson", "2.8.9", 2, 3)
    assert dependency_row == ("com.squareup.okio:okio-jvm", "3.7.0", 0)
    assert opcode_ngram_row == ("invoke-virtual|move-result-object|return-object", 1)
    assert api_reference_row == (
        "Ljava/lang/String;->valueOf(Ljava/lang/Object;)Ljava/lang/String;",
    )
    assert basic_block_row == ("bb:3:abc", 2)
    assert call_chain_row == ("call:2:def", 1)
    assert class_neighbor_row == ("in:0|out:1|out-field:1", 1)
    assert field_operation_row == ("fieldops:2:fed", 1)
    assert literal_context_row == ("literal-context:1234567890abcdef",)
