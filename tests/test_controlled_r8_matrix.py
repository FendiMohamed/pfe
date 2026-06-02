from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_script(name: str):
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_controlled_builder_exposes_phase2_r8_variants():
    builder = load_script("build_controlled_apk")

    assert {"r8-optimize", "r8-shrink-optimize", "r8-repackage", "r8-inline-stress"} <= set(
        builder.FIXTURE_VARIANTS
    )
    assert "-dontobfuscate" in builder.r8_rules_for("com.google.code.gson:gson", "r8-optimize")
    assert "-repackageclasses r8flat" in builder.r8_rules_for(
        "com.google.code.gson:gson",
        "r8-repackage",
    )
    assert "allowoptimization" in builder.r8_rules_for(
        "com.google.code.gson:gson",
        "r8-shrink-optimize",
    )


def test_inline_stress_source_uses_known_libraries_where_feasible():
    builder = load_script("build_controlled_apk")

    gson_source = builder.java_source_for("com.google.code.gson:gson", "r8-inline-stress")
    codec_source = builder.java_source_for("commons-codec:commons-codec", "r8-inline-stress")

    assert "private static String first" in gson_source
    assert "new Gson().toJson" in gson_source
    assert "DigestUtils.sha256Hex" in codec_source


def test_generated_batch_contains_phase2_r8_matrix_categories():
    batch = load_script("run_generated_apk_batch")
    categories = {fixture["category"] for fixture in batch.phase2_r8_matrix_fixtures()}
    targets = {fixture["coordinate"] for fixture in batch.phase2_r8_matrix_fixtures()}

    assert categories == {
        "r8-rename",
        "r8-shrink",
        "r8-optimize",
        "r8-shrink-optimize",
        "r8-package-flattening",
        "r8-inline-stress",
    }
    assert {
        "com.google.code.gson:gson",
        "com.fasterxml.jackson.core:jackson-databind",
        "com.squareup.okhttp3:okhttp",
        "com.squareup.retrofit2:retrofit",
        "commons-codec:commons-codec",
    } <= targets
    assert all(
        fixture.get("phase") == "r8-phase-2-matrix"
        for fixture in batch.phase2_r8_matrix_fixtures()
    )


def test_generated_batch_adds_category_driven_dataset_growth_slice():
    batch = load_script("run_generated_apk_batch")
    fixtures = batch.dataset_growth_fixtures()
    categories = {fixture["category"] for fixture in fixtures}
    coordinates = {fixture["coordinate"] for fixture in fixtures}

    assert len(fixtures) == 18
    assert {
        "kotlin-networking-version-band",
        "modern-kotlin-framework",
        "kotlin-networking-r8-shrink-optimize",
        "modern-networking-multidex",
        "modern-framework-multidex",
    } <= categories
    assert {
        "com.squareup.okio:okio-jvm",
        "com.squareup.okhttp3:okhttp",
        "io.ktor:ktor-client-core-jvm",
        "io.ktor:ktor-client-okhttp-jvm",
    } <= coordinates
    assert all(fixture.get("phase") == "dataset-growth-v2" for fixture in fixtures)


def test_dataset_growth_classification_tags_explain_modern_framework_cases():
    batch = load_script("run_generated_apk_batch")
    ktor = next(
        fixture
        for fixture in batch.dataset_growth_fixtures()
        if fixture["name"] == "generated-ktor-client-core-jvm-2-3-12-clear"
    )
    okio = next(
        fixture
        for fixture in batch.dataset_growth_fixtures()
        if fixture["name"] == "generated-okio-jvm-3-7-0-r8-shrink-optimize"
    )

    assert {"framework-ktor", "kotlin-era", "networking"} <= set(
        batch.classification_tags(ktor)
    )
    assert {"artifact-family", "kotlin-era", "networking"} <= set(
        batch.classification_tags(okio)
    )


def test_generated_batch_can_filter_by_phase():
    batch = load_script("run_generated_apk_batch")

    class Args:
        phase = ["dataset-growth-v2"]
        fixture = []

    selected = batch.selected_fixtures(Args())

    assert selected
    assert {fixture.get("phase") for fixture in selected} == {"dataset-growth-v2"}


def test_run_fixture_can_reuse_existing_files(tmp_path, monkeypatch):
    batch = load_script("run_generated_apk_batch")
    fixture = {
        "name": "sample",
        "category": "modern-kotlin-framework",
        "coordinate": "io.ktor:ktor-client-core-jvm",
        "version": "2.3.12",
        "variant": "clear",
        "phase": "dataset-growth-v2",
    }
    (tmp_path / "data" / "test_apks").mkdir(parents=True)
    (tmp_path / "data" / "results" / "report-sample").mkdir(parents=True)
    (tmp_path / "data" / "test_apks" / "sample.apk").write_bytes(b"apk")
    (tmp_path / "data" / "test_apks" / "sample.ground-truth.json").write_text(
        "{}",
        encoding="utf-8",
    )
    (tmp_path / "data" / "results" / "report-sample" / "report.json").write_text(
        "{}",
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)

    result = batch.run_fixture(
        fixture,
        tmp_path / "db.sqlite",
        skip_report=False,
        reuse_existing=True,
    )

    assert result["status"] == "ok"
    assert result["reused_existing"] is True
