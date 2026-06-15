from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "collect_fdroid_real_apk_batch.py"


def load_module():
    spec = importlib.util.spec_from_file_location("collect_fdroid_real_apk_batch", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_latest_version_uses_highest_manifest_version_code() -> None:
    module = load_module()
    package = {
        "versions": {
            "old": {"manifest": {"versionCode": 1}, "file": {"name": "/old.apk"}},
            "new": {"manifest": {"versionCode": 3}, "file": {"name": "/new.apk"}},
            "middle": {"manifest": {"versionCode": 2}, "file": {"name": "/middle.apk"}},
        }
    }

    assert module.latest_version(package)["file"]["name"] == "/new.apk"


def test_collect_batch_reuses_existing_apk_and_writes_metadata(tmp_path: Path) -> None:
    module = load_module()
    apk_bytes = b"fake apk bytes"
    sha256 = hashlib.sha256(apk_bytes).hexdigest()
    apk_root = tmp_path / "apks"
    apk_path = apk_root / "demo" / "demo.apk"
    apk_path.parent.mkdir(parents=True)
    apk_path.write_bytes(apk_bytes)

    index = {
        "packages": {
            "org.example.demo": {
                "metadata": {
                    "categories": ["Demo"],
                    "license": "Apache-2.0",
                    "sourceCode": "https://example.invalid/demo",
                },
                "versions": {
                    "v1": {
                        "manifest": {
                            "versionCode": 10,
                            "versionName": "1.0",
                            "nativecode": ["arm64-v8a"],
                        },
                        "file": {
                            "name": "/org.example.demo_10.apk",
                            "sha256": sha256,
                            "size": len(apk_bytes),
                        },
                        "src": {
                            "name": "/org.example.demo_10_src.tar.gz",
                            "sha256": "abc",
                            "size": 123,
                        },
                    }
                },
            }
        }
    }
    selection = {
        "package_name": "org.example.demo",
        "slug": "demo",
        "app": "Demo",
        "target_layer": "smoke-real",
        "validation_level": "L3-report-with-source-link",
        "classifications": ["no-native", "test"],
        "reason": "unit test",
    }

    payload = module.collect_batch(
        index=index,
        selections=[selection],
        apk_root=apk_root,
        report_root=tmp_path / "reports",
        db_path=tmp_path / "missing.sqlite",
        skip_download=True,
        skip_report=True,
        reuse_reports=False,
        skip_osv=True,
        include_uncertain=False,
        continue_on_error=False,
    )

    assert payload["summary"]["succeeded"] == 1
    assert payload["apks"][0]["apk"]["sha256"] == sha256
    assert payload["apks"][0]["source_tarball"]["url"].endswith("/org.example.demo_10_src.tar.gz")
    metadata = json.loads((apk_path.parent / "metadata.json").read_text(encoding="utf-8"))
    assert metadata["metric_eligibility"] == "excluded-from-source-validated-metrics"


def test_load_selection_json_accepts_batch_apks(tmp_path: Path) -> None:
    module = load_module()
    path = tmp_path / "selection.json"
    path.write_text(
        json.dumps(
            {
                "apks": [
                    {
                        "package_name": "org.example.demo",
                        "slug": "demo",
                        "app": "Demo",
                        "classifications": ["no-native"],
                    }
                ]
            }
        )
        + "\n",
        encoding="utf-8",
    )

    selections = module.load_selection_json(path)

    assert selections == [
        {
            "package_name": "org.example.demo",
            "slug": "demo",
            "app": "Demo",
            "target_layer": "smoke-real",
            "validation_level": "L3-report-with-source-link",
            "classifications": ["no-native"],
            "reason": "Custom F-Droid real APK selection.",
        }
    ]


def test_write_outputs_documents_metric_exclusion(tmp_path: Path) -> None:
    module = load_module()
    payload = {
        "summary": {
            "selected": 1,
            "succeeded": 1,
            "failed": 0,
            "apk_root": "data/test_apks/real",
            "report_root": "data/results/evaluation/real-apk-growth-batch-v2",
            "classes_covered": ["flutter"],
        },
        "apks": [
            {
                "app": "LocalSend",
                "package_name": "org.localsend.localsend_app",
                "version_name": "1.0",
                "version_code": 1,
                "target_layer": "smoke-real",
                "classifications": ["flutter"],
                "report": {"status": "skipped", "json": "report.json"},
                "reason": "framework-boundary case",
            }
        ],
    }

    module.write_outputs(payload, tmp_path / "summary.json", tmp_path / "summary.md")

    doc = (tmp_path / "summary.md").read_text(encoding="utf-8")
    assert "excluded from source-validated metrics" in doc
    assert "LocalSend" in doc
