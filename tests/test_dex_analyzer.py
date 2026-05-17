from __future__ import annotations

import zipfile

from apk_sbom.dex_analyzer import analyze_apk_dex, class_descriptor_to_package


def test_class_descriptor_to_package():
    assert class_descriptor_to_package("Lcom/google/gson/Gson;") == "com.google.gson"
    assert class_descriptor_to_package("Lokhttp3/OkHttpClient;") == "okhttp3"
    assert class_descriptor_to_package("Ljava/lang/String;") == "java.lang"
    assert class_descriptor_to_package("NotADescriptor") is None


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
