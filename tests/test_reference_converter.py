from __future__ import annotations

import json
import sys
import zipfile

from apk_sbom.maven_downloader import ArtifactRecord
from apk_sbom.reference_converter import (
    convert_artifact_to_dex,
    dex_output_dir,
    discover_artifact_records,
    planned_conversion,
    resolve_artifact_path,
)


def make_record(tmp_path, *, coordinate: str = "com.google.code.gson:gson") -> ArtifactRecord:
    group, artifact = coordinate.split(":", maxsplit=1)
    jar_path = tmp_path / f"{artifact}-1.0.0.jar"
    jar_path.write_bytes(b"fake jar")
    return ArtifactRecord(
        group=group,
        artifact=artifact,
        version="1.0.0",
        coordinate=coordinate,
        purl=f"pkg:maven/{group}/{artifact}@1.0.0",
        packaging="jar",
        url=f"https://repo1.maven.org/maven2/{artifact}-1.0.0.jar",
        path=str(jar_path),
        sha256="0" * 64,
        size=jar_path.stat().st_size,
    )


def test_discover_artifact_records_filter_and_limit(tmp_path):
    first = make_record(tmp_path, coordinate="com.google.code.gson:gson")
    second = make_record(tmp_path, coordinate="commons-codec:commons-codec")
    first_dir = tmp_path / "first"
    second_dir = tmp_path / "second"
    first_dir.mkdir()
    second_dir.mkdir()
    (first_dir / "metadata.json").write_text(json.dumps(first.__dict__), encoding="utf-8")
    (second_dir / "metadata.json").write_text(json.dumps(second.__dict__), encoding="utf-8")

    records = discover_artifact_records(tmp_path, coordinate="commons-codec:commons-codec", limit=1)

    assert len(records) == 1
    assert records[0].coordinate == "commons-codec:commons-codec"


def test_discover_artifact_records_supports_offset(tmp_path):
    first = make_record(tmp_path, coordinate="androidx.activity:activity")
    second = make_record(tmp_path, coordinate="androidx.appcompat:appcompat")
    third = make_record(tmp_path, coordinate="androidx.core:core")
    for index, record in enumerate((first, second, third), start=1):
        record_dir = tmp_path / f"record-{index}"
        record_dir.mkdir()
        (record_dir / "metadata.json").write_text(json.dumps(record.__dict__), encoding="utf-8")

    records = discover_artifact_records(tmp_path, offset=1, limit=1)

    assert len(records) == 1
    assert records[0].coordinate == "androidx.appcompat:appcompat"


def test_planned_conversion_uses_group_artifact_version_path(tmp_path):
    record = make_record(tmp_path)
    planned = planned_conversion(record, tmp_path / "dex")

    assert planned["coordinate"] == "com.google.code.gson:gson"
    assert planned["output_dir"].endswith("com/google/code/gson/gson/1.0.0")
    assert planned["metadata_path"].endswith("com/google/code/gson/gson/1.0.0/conversion.json")


def test_convert_artifact_to_dex_with_fake_d8(tmp_path):
    fake_d8 = tmp_path / "fake_d8.py"
    fake_d8.write_text(
        "\n".join(
            [
                "from pathlib import Path",
                "import sys",
                "output = Path(sys.argv[sys.argv.index('--output') + 1])",
                "output.mkdir(parents=True, exist_ok=True)",
                "(output / 'classes.dex').write_bytes(b'dex\\n035\\0')",
            ]
        ),
        encoding="utf-8",
    )
    record = make_record(tmp_path)

    result = convert_artifact_to_dex(
        record,
        output_root=tmp_path / "dex",
        d8_command=[sys.executable, str(fake_d8)],
    )

    assert result.status == "converted"
    assert len(result.dex_files) == 1
    assert result.dex_files[0].path.endswith("classes.dex")
    assert (dex_output_dir(record, tmp_path / "dex") / "conversion.json").exists()


def test_convert_artifact_to_dex_reports_missing_d8(tmp_path):
    record = make_record(tmp_path)

    result = convert_artifact_to_dex(
        record,
        output_root=tmp_path / "dex",
        d8_command="definitely-missing-d8",
    )

    assert result.status == "failed"
    assert "D8 command not found" in (result.error or "")


def test_convert_artifact_to_dex_skips_when_d8_outputs_no_dex(tmp_path):
    fake_d8 = tmp_path / "fake_d8_no_output.py"
    fake_d8.write_text("import sys\nraise SystemExit(0)\n", encoding="utf-8")
    record = make_record(tmp_path)

    result = convert_artifact_to_dex(
        record,
        output_root=tmp_path / "dex",
        d8_command=[sys.executable, str(fake_d8)],
    )

    assert result.status == "skipped"
    assert "no classes*.dex" in (result.error or "")
    assert (dex_output_dir(record, tmp_path / "dex") / "conversion.json").exists()


def test_convert_artifact_to_dex_skips_aar_without_classes_jar(tmp_path):
    aar_path = tmp_path / "empty.aar"
    with zipfile.ZipFile(aar_path, "w") as archive:
        archive.writestr("AndroidManifest.xml", "<manifest />")
    record = ArtifactRecord(
        group="androidx.compose.ui",
        artifact="ui",
        version="1.0.0",
        coordinate="androidx.compose.ui:ui",
        purl="pkg:maven/androidx.compose.ui/ui@1.0.0",
        packaging="aar",
        url="https://dl.google.com/dl/android/maven2/androidx/compose/ui/ui/1.0.0/ui-1.0.0.aar",
        path=str(aar_path),
        sha256="0" * 64,
        size=aar_path.stat().st_size,
    )

    result = convert_artifact_to_dex(record, output_root=tmp_path / "dex", d8_command="unused-d8")

    assert result.status == "skipped"
    assert "no classes.jar" in (result.error or "")
    assert (dex_output_dir(record, tmp_path / "dex") / "conversion.json").exists()


def test_resolve_artifact_path_accepts_windows_style_paths(tmp_path, monkeypatch):
    artifact_dir = tmp_path / "data" / "reference_db" / "artifacts"
    artifact_dir.mkdir(parents=True)
    artifact_path = artifact_dir / "library.jar"
    artifact_path.write_bytes(b"fake jar")
    monkeypatch.chdir(tmp_path)

    resolved = resolve_artifact_path("data\\reference_db\\artifacts\\library.jar")

    assert resolved == artifact_path.relative_to(tmp_path)
    assert resolved.exists()
