from __future__ import annotations

from scripts.train_ai_r8_raw_opcode_transformer import (
    build_baseline_comparison,
    build_markdown,
    case_heldout_split,
    row_token_counts,
)


def make_row(label: str, case_id: str, index: int) -> dict:
    return {
        "row_id": f"{label}:{case_id}:{index}",
        "case_id": case_id,
        "label": label,
        "token_ids": [2, 10 + index, 11, 3, 0, 0],
    }


def test_case_heldout_split_keeps_each_label_in_train_validation_and_test():
    rows = []
    for label in ("r8-rename", "real-apk-smoke"):
        for case_id in (f"{label}-a", f"{label}-b"):
            rows.extend(make_row(label, case_id, index) for index in range(12))

    split = case_heldout_split(rows)

    assert {row["label"] for row in split["train"]} == {"r8-rename", "real-apk-smoke"}
    assert {row["label"] for row in split["validation"]} == {
        "r8-rename",
        "real-apk-smoke",
    }
    assert {row["label"] for row in split["test"]} == {"r8-rename", "real-apk-smoke"}
    assert {row["case_id"] for row in split["test"]} == {
        "r8-rename-b",
        "real-apk-smoke-b",
    }


def test_row_token_counts_drops_special_tokens():
    counts = row_token_counts({"token_ids": [2, 9, 9, 3, 0, 10, 1]})

    assert counts == {"tok:9": 2, "tok:10": 1}


def test_baseline_comparison_marks_underperforming_transformer_not_promotable():
    comparison = build_baseline_comparison(
        {
            "majority": {"test": {"macro_f1": 0.1}},
            "opcode_count": {"test": {"macro_f1": 0.3}},
        },
        {"macro_f1": 0.2},
    )

    assert comparison["best_baseline"] == "opcode_count"
    assert comparison["beats_best_baseline"] is False
    assert comparison["verdict"] == "raw-opcode-transformer-research-only-not-promotable"


def test_markdown_records_raw_opcode_guardrails():
    markdown = build_markdown(
        {
            "status": "trained",
            "model_type": "torch.nn.TransformerEncoder",
            "dataset": {
                "method_sequence_rows": 4,
                "apks_analyzed": 2,
                "vocab_size": 12,
                "split_strategy": "case-heldout",
                "splits": {"train": {"rows": 2, "case_ids": 1, "labels": {"a": 2}}},
            },
            "baselines": {
                "opcode_count": {
                    "validation": {"macro_f1": 0.1},
                    "test": {"macro_f1": 0.2, "accuracy": 0.3},
                }
            },
            "baseline_comparison": {
                "best_baseline": "opcode_count",
                "delta_vs_best_baseline": -0.1,
                "verdict": "raw-opcode-transformer-research-only-not-promotable",
            },
            "validation": {"macro_f1": 0.1, "accuracy": 0.2},
            "test": {
                "macro_f1": 0.1,
                "accuracy": 0.2,
                "per_class": {
                    "a": {"precision": 0.1, "recall": 0.2, "f1": 0.13, "support": 2}
                },
            },
            "history": [],
            "limits": ["report-only"],
        }
    )

    assert "Raw Opcode Transformer" in markdown
    assert "raw-opcode-transformer-research-only-not-promotable" in markdown
    assert "not exact SBOM versioning" in markdown
