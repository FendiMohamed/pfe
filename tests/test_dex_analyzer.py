from __future__ import annotations

import zipfile

from apk_sbom.dex_analyzer import (
    analyze_apk_dex,
    basic_block_fingerprints_from_sequence,
    build_dependency_shape,
    build_class_neighbor_summaries,
    call_chain_fingerprints_from_sequence,
    class_descriptor_to_package,
    extract_api_references_from_instruction,
    extract_class_descriptors,
    extract_string_literal_from_instruction,
    field_operation_fingerprints_from_sequence,
    literal_context_feature,
    opcode_ngrams_from_sequence,
)


def test_class_descriptor_to_package():
    assert class_descriptor_to_package("Lcom/google/gson/Gson;") == "com.google.gson"
    assert class_descriptor_to_package("Lokhttp3/OkHttpClient;") == "okhttp3"
    assert class_descriptor_to_package("Ljava/lang/String;") == "java.lang"
    assert class_descriptor_to_package("NotADescriptor") is None


def test_extract_class_descriptors_from_method_descriptor():
    assert extract_class_descriptors(
        "(Lcom/google/gson/Gson;[Lcom/google/gson/JsonElement;)Ljava/lang/String;"
    ) == {
        "Lcom/google/gson/Gson;",
        "Lcom/google/gson/JsonElement;",
        "Ljava/lang/String;",
    }


def test_build_dependency_shape_counts_degree_buckets():
    shape = build_dependency_shape(
        {"LA;", "LB;", "LC;"},
        {
            ("LA;", "LB;", "field"),
            ("LA;", "LC;", "method-signature"),
        },
    )

    assert shape["out:2-3"] == 1
    assert shape["out:0"] == 2
    assert shape["in:1"] == 2
    assert shape["kind:field"] == 1
    assert shape["kind:method-signature"] == 1


def test_extract_string_literal_from_instruction():
    assert extract_string_literal_from_instruction(
        "const-string",
        'v0, "gson.version=2.8.9"',
    ) == "gson.version=2.8.9"
    assert extract_string_literal_from_instruction("invoke-virtual", 'v0, "ignored"') is None


def test_extract_api_references_from_instruction():
    assert extract_api_references_from_instruction(
        "v0, Landroid/content/Context;->getPackageName()Ljava/lang/String;"
    ) == {"Landroid/content/Context;->getPackageName()Ljava/lang/String;"}
    assert extract_api_references_from_instruction("v0, v1") == set()


def test_opcode_ngrams_from_sequence_keeps_ordered_windows():
    assert opcode_ngrams_from_sequence(
        ["const/4", "invoke-virtual", "move-result-object", "return-object"]
    ) == {
        "const/4|invoke-virtual|move-result-object": 1,
        "invoke-virtual|move-result-object|return-object": 1,
    }


def test_basic_block_fingerprints_split_at_branch_boundaries():
    fingerprints = basic_block_fingerprints_from_sequence(
        ["const/4", "if-eqz", "invoke-virtual", "return-void"]
    )

    assert sum(fingerprints.values()) == 2
    assert all(fingerprint.startswith("bb:") for fingerprint in fingerprints)


def test_call_chain_fingerprints_use_invoke_order_only():
    fingerprints = call_chain_fingerprints_from_sequence(
        ["const/4", "invoke-static", "move-result-object", "invoke-virtual", "return-object"]
    )

    assert sum(fingerprints.values()) == 1
    assert next(iter(fingerprints)).startswith("call:2:")


def test_field_operation_fingerprints_use_field_opcode_order_only():
    fingerprints = field_operation_fingerprints_from_sequence(
        ["iget-object", "invoke-virtual", "sput-object", "return-void"]
    )

    assert sum(fingerprints.values()) == 1
    assert next(iter(fingerprints)).startswith("fieldops:2:")


def test_build_class_neighbor_summaries_buckets_in_and_out_edges():
    summaries = build_class_neighbor_summaries(
        {"LA;", "LB;"},
        {("LA;", "LB;", "field")},
    )

    assert sum(summaries.values()) == 2
    assert any("out-field:1" in summary for summary in summaries)
    assert any("in-field:1" in summary for summary in summaries)


def test_literal_context_feature_is_stable_and_context_sensitive():
    feature = literal_context_feature(
        "Lcom/example/A;",
        "Lcom/example/A;->version()Ljava/lang/String;",
        "2.8.9",
    )

    assert feature == literal_context_feature(
        "Lcom/example/A;",
        "Lcom/example/A;->version()Ljava/lang/String;",
        "2.8.9",
    )
    assert feature != literal_context_feature(
        "Lcom/example/A;",
        "Lcom/example/A;->name()Ljava/lang/String;",
        "2.8.9",
    )
    assert feature.startswith("literal-context:")


def test_analyze_apk_dex_records_parse_error_for_invalid_dex(tmp_path):
    apk_path = tmp_path / "invalid.apk"
    with zipfile.ZipFile(apk_path, "w") as archive:
        archive.writestr("classes.dex", b"not a real dex")

    analysis = analyze_apk_dex(apk_path)

    assert analysis.dex_files_analyzed == 0
    assert analysis.dex_files_failed == 1
    assert analysis.classes_count == 0
    assert analysis.methods_count == 0
    assert analysis.packages == []
    assert analysis.parse_errors[0].dex_file == "classes.dex"
