from __future__ import annotations

from pathlib import Path

from scripts.build_ai_r8_independent_corpus import build_payload as build_independent
from scripts.build_ai_r8_raw_opcode_corpus import (
    MethodOpcodeRow,
    discover_default_apks,
    tokenized_row,
)
from scripts.build_r8_strict_apk_promotion_gate_matrix import strict_blockers


def write_json(path: Path, payload: str) -> Path:
    path.write_text(payload, encoding="utf-8")
    return path


def test_independent_corpus_separates_training_and_heldout_rows(tmp_path):
    training = write_json(
        tmp_path / "training.json",
        """
        {
          "rows": [
            {
              "row_id": "train:1",
              "case_id": "case-a",
              "coordinate": "com.example:lib",
              "label": "confirmed_exact",
              "candidate_version": "1.0.0",
              "source_version": "1.0.0",
              "row_source": "emitted-result",
              "features": {"best_score": 0.9},
              "context": {"role": "clean"}
            }
          ]
        }
        """,
    )
    router = write_json(
        tmp_path / "router.json",
        """
        {
          "rows": [
            {
              "row_id": "router:1",
              "case_id": "case-b",
              "coordinate": "com.example:other",
              "recommended_profile": "r8-structural-recall",
              "candidate_version": "2.0.0",
              "source_version": "2.0.0",
              "evidence": {"opcode_score": 0.95}
            }
          ]
        }
        """,
    )
    structural = write_json(
        tmp_path / "gate.json",
        """
        {
          "rows": [
            {
              "row_id": "gate:1",
              "case_id": "case-c",
              "coordinate": "com.example:gate",
              "classification": "blocked-no-representative-exact-control",
              "candidate_version": "3.0.0",
              "source_version": "3.0.0",
              "apk_only_gate": {"passes": true, "decision": "pass"},
              "source_evaluation": {"classification": "posthoc-source-exact"},
              "control_context": {"control_risk_rows": 0, "exact_controls": 0},
              "features": {"literal_score": 1.0}
            }
          ]
        }
        """,
    )
    analysis = write_json(
        tmp_path / "analysis.json",
        """
        {
          "version_rows": [
            {
              "case_id": "case-d",
              "case_role": "partial-source-validated",
              "coordinate": "com.example:control",
              "analysis_class": "wrong-version",
              "tool_selected_version": "4.0.0",
              "correct_source_versions": "4.1.0",
              "confidence": 0.7
            }
          ]
        }
        """,
    )
    smoke = write_json(
        tmp_path / "smoke.json",
        """
        {
          "targets": [
            {
              "case_id": "case-e",
              "role": "smoke",
              "comparison": {"unchanged": true},
              "hybrid_section_visible": true,
              "hybrid_section_report_only": true,
              "hybrid_section_summary": {"router_matching_rows": 5}
            }
          ]
        }
        """,
    )

    payload = build_independent(
        training_dataset_json=training,
        router_json=router,
        structural_gate_json=structural,
        large_analysis_json=analysis,
        final_smoke_json=smoke,
    )

    assert payload["summary"]["rows"] == 5
    assert payload["summary"]["training_eligible_rows"] == 1
    assert payload["summary"]["heldout_or_report_only_rows"] == 4
    assert payload["summary"]["external_corpus"] is False
    assert payload["summary"]["partitions"]["phase6a_training_dataset"] == 1
    assert payload["summary"]["partitions"]["heldout_hybrid_router"] == 1


def test_raw_opcode_discovery_reserves_default_slots_for_real_smoke(tmp_path):
    generated = tmp_path / "generated-gson-2-8-9-r8-rename.apk"
    generated.write_bytes(b"")
    controlled = tmp_path / "controlled-com-google-code-gson-gson-2.8.9-r8-rename.apk"
    controlled.write_bytes(b"")
    real = tmp_path / "real"
    real.mkdir()
    fdroid = real / "F-Droid.apk"
    fdroid.write_bytes(b"")
    aegis_dir = real / "aegis-authenticator"
    aegis_dir.mkdir()
    aegis = aegis_dir / "aegis-authenticator.apk"
    aegis.write_bytes(b"")

    discovered = discover_default_apks(tmp_path, max_apks=3)

    assert fdroid in discovered
    assert aegis in discovered
    assert len(discovered) == 3


def test_raw_opcode_tokenized_row_pads_and_preserves_metadata():
    row = MethodOpcodeRow(
        row_id="row",
        apk_path="apk.apk",
        case_id="case",
        source_role="generated-controlled",
        obfuscation_profile="r8-rename",
        label="r8-rename",
        dex_file="classes.dex",
        class_name="Lx;",
        method_name="m",
        tokens=["op:const/4", "op:return-void"],
    )
    vocabulary = {"<pad>": 0, "<unk>": 1, "<cls>": 2, "<sep>": 3, "op:const/4": 4}

    tokenized = tokenized_row(row, vocabulary, max_sequence_length=5)

    assert tokenized["label"] == "r8-rename"
    assert tokenized["token_ids"] == [2, 4, 1, 3, 0]
    assert tokenized["length"] == 4


def test_strict_gate_blocks_risky_or_undercontrolled_rows():
    profile = {
        "require_posthoc_source_exact": True,
        "max_control_risk_rows": 0,
        "min_exact_controls": 2,
        "min_control_cases": 2,
    }
    row = {
        "source_evaluation": {"candidate_matches_source": True},
        "control_context": {
            "control_risk_rows": 1,
            "exact_controls": 1,
            "case_ids": ["case-a"],
        },
        "ai_summary": {},
    }

    blockers = strict_blockers(row, profile)

    assert blockers == [
        "same-coordinate-control-risk",
        "insufficient-exact-controls",
        "insufficient-control-case-support",
    ]
