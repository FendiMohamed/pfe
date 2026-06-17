from __future__ import annotations

import importlib.util
import io
from pathlib import Path
import tarfile


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "advance_real_apk_batch_proofs.py"


def load_module():
    spec = importlib.util.spec_from_file_location("advance_real_apk_batch_proofs", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_safe_extract_rejects_path_traversal(tmp_path: Path) -> None:
    module = load_module()
    tar_path = tmp_path / "bad.tar.gz"
    with tarfile.open(tar_path, "w:gz") as archive:
        data = b"bad"
        info = tarfile.TarInfo("../escape.txt")
        info.size = len(data)
        archive.addfile(info, io.BytesIO(data))

    try:
        module.safe_extract_tar(tar_path, tmp_path / "out")
    except ValueError as exc:
        assert "unsafe tar member" in str(exc)
    else:
        raise AssertionError("unsafe tar path was accepted")


def test_find_gradle_roots_prefers_settings_file(tmp_path: Path) -> None:
    module = load_module()
    root = tmp_path / "source" / "project"
    root.mkdir(parents=True)
    (root / "settings.gradle").write_text("", encoding="utf-8")
    nested = root / "app"
    nested.mkdir()
    (nested / "build.gradle").write_text("", encoding="utf-8")

    assert module.find_gradle_roots(tmp_path / "source") == [root]


def test_build_markdown_records_batch_gate_status() -> None:
    module = load_module()
    payload = {
        "summary": {
            "selected": 1,
            "source_available": 1,
            "dependency_tree_ok": 0,
            "source_validation_ok": 0,
            "failed": 0,
            "source_root": "data/source/real-apk-growth-batch-v2",
            "validation_root": "data/results/source-validation/real-apk-growth-batch-v2",
        },
        "proofs": [
            {
                "app": "Shelter",
                "version_name": "1.9.1",
                "version_code": 445,
                "proof_status": "source-downloaded",
                "source": {"status": "ok", "tarball_path": "source.tar.gz"},
                "dependency_tree": {"status": "not-attempted", "reason": "run with --attempt-gradle"},
                "source_validation": {"status": "blocked-until-dependency-tree", "reason": "wait for tree"},
            }
        ],
    }

    doc = module.build_markdown(payload)

    assert "Real APK Batch Proof Status" in doc
    assert "Shelter" in doc
    assert "not-attempted: run with --attempt-gradle" in doc
    assert "blocked-until-dependency-tree: wait for tree" in doc
    assert "Attempt Gradle runtime dependency tree" in doc


def test_missing_gradle_command_is_blocker_not_script_failure(tmp_path: Path) -> None:
    module = load_module()
    root = tmp_path / "source"
    root.mkdir()
    module.gradle_command = lambda _root, _slug=None: [
        "definitely-not-a-gradle-command-codex-test"
    ]

    result = module.attempt_dependency_tree(
        slug="shelter",
        gradle_roots=[root],
        validation_dir=tmp_path / "validation",
        timeout=1,
    )

    assert result["status"] == "blocked"
    assert result["reason"] == "Gradle command unavailable"
    assert result["attempts"][0]["status"] == "tool-unavailable"
    assert result["attempts"][0]["task"] == ":app:dependencies"


def test_unknown_slug_tries_app_dependency_task_first(tmp_path: Path) -> None:
    module = load_module()
    root = tmp_path / "source"
    root.mkdir()
    module.gradle_command = lambda _root, _slug=None: [
        "definitely-not-a-gradle-command-codex-test"
    ]

    result = module.attempt_dependency_tree(
        slug="new-low-risk-app",
        gradle_roots=[root],
        validation_dir=tmp_path / "validation",
        timeout=1,
    )

    assert result["attempts"][0]["task"] == ":app:dependencies"
    assert result["attempts"][0]["configuration"] == "releaseRuntimeClasspath"


def test_attempt_label_keeps_root_and_project_task_logs_distinct() -> None:
    module = load_module()

    assert (
        module.attempt_label(2, ":app-ose:dependencies", "oseReleaseRuntimeClasspath")
        == "root2-app-ose-dependencies-oseReleaseRuntimeClasspath"
    )


def test_source_validation_result_classifies_partial() -> None:
    module = load_module()

    status = module.classify_status(
        "ok",
        "ok",
        {"status": "ok", "version_mismatches": 2, "missing": 0},
    )

    assert status == "source-validated-partial"


def test_validation_copy_result_never_classifies_clean() -> None:
    module = load_module()

    status = module.classify_status(
        "ok",
        "ok",
        {"status": "ok", "version_mismatches": 0, "missing": 0},
        {"validation_copy": True},
    )

    assert status == "source-validated-partial"


def test_zero_component_source_validation_is_no_maven_signal() -> None:
    module = load_module()

    status = module.classify_status(
        "ok",
        "ok",
        {"status": "ok", "sbom_components": 0, "version_mismatches": 0, "missing": 0},
    )

    assert status == "source-validated-no-maven-signal"


def test_derive_fdroid_source_tarball_url_handles_signed_suffix() -> None:
    module = load_module()

    url = module.derive_fdroid_source_tarball_url(
        {
            "package_name": "nodomain.freeyourgadget.gadgetbridge",
            "version_code": 248,
            "apk": {
                "url": "https://f-droid.org/repo/nodomain.freeyourgadget.gadgetbridge_248_01cce93.apk"
            },
        }
    )

    assert url == "https://f-droid.org/repo/nodomain.freeyourgadget.gadgetbridge_248_src.tar.gz"


def test_prepare_shelter_validation_copy_adds_settings_and_removes_incomplete_project(tmp_path: Path) -> None:
    module = load_module()
    source_root = tmp_path / "source"
    app_dir = source_root / "app"
    app_dir.mkdir(parents=True)
    (source_root / "build.gradle").write_text("", encoding="utf-8")
    app_build = app_dir / "build.gradle"
    app_build.write_text(
        "dependencies {\n"
        "    debugImplementation project(path: ':setup-wizard-lib', configuration: 'gingerbreadCompatDebugRuntimeElements')\n"
        "    releaseImplementation project(path: ':setup-wizard-lib', configuration: 'gingerbreadCompatReleaseRuntimeElements')\n"
        "}\n",
        encoding="utf-8",
    )

    result = module.prepare_shelter_validation_copy(source_root, tmp_path / "validation")

    copied_root = result["root"]
    assert (copied_root / "settings.gradle").read_text(encoding="utf-8") == (
        "rootProject.name = 'shelter-validation'\ninclude ':app'\n"
    )
    copied_build = (copied_root / "app" / "build.gradle").read_text(encoding="utf-8")
    assert "setup-wizard-lib" in copied_build
    assert "project(path:" not in copied_build


def test_reuse_existing_proofs_rebuilds_summary(tmp_path: Path) -> None:
    module = load_module()
    validation_root = tmp_path / "validation"
    proof_dir = validation_root / "shelter"
    proof_dir.mkdir(parents=True)
    (proof_dir / "proof-status.json").write_text(
        """
{
  "slug": "shelter",
  "app": "Shelter",
  "package_name": "net.typeblog.shelter",
  "target_layer": "smoke-real",
  "validation_level": "L3-report-with-source-link",
  "source": {"status": "ok"},
  "dependency_tree": {"status": "ok"},
  "source_validation": {"status": "ok"}
}
""".strip()
        + "\n",
        encoding="utf-8",
    )

    result = module.reuse_existing_proofs(
        rows=[
            {
                "slug": "shelter",
                "app": "Shelter",
                "package_name": "net.typeblog.shelter",
                "target_layer": "smoke-real",
                "validation_level": "L3-report-with-source-link",
            }
        ],
        source_root=tmp_path / "source",
        validation_root=validation_root,
        continue_on_error=False,
    )

    assert result["summary"]["selected"] == 1
    assert result["summary"]["dependency_tree_ok"] == 1
    assert result["summary"]["source_validation_ok"] == 1
