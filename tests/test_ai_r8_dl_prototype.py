from __future__ import annotations

from scripts.build_ai_r8_token_corpus import build_corpus, row_to_tokens


def make_dataset() -> dict:
    labels = [
        "suggest_report_only",
        "suppress_uncertain",
        "risk_only",
        "confirmed_exact",
        "mismatch_or_extra",
        "boundary_do_not_suggest",
    ]
    rows = []
    for index in range(12):
        rows.append(
            {
                "row_id": f"row-{index}",
                "case_id": f"case-{index}",
                "coordinate": "com.google.code.gson:gson",
                "source_version": "2.8.9",
                "candidate_version": "2.8.9",
                "row_source": "matcher-recall",
                "label": labels[index % len(labels)],
                "features": {
                    "best_score": 0.91,
                    "score_gap_to_best": 0.1,
                    "source_rank": 1,
                    "identity_confidence": 0.9,
                    "package_score": 0.8,
                    "class_score": 0.7,
                    "method_score": 0.6,
                    "opcode_score": 0.5,
                    "literal_score": 0.4,
                    "dependency_score": 0.3,
                    "matched_packages": 4,
                    "matched_classes": 5,
                    "matched_methods": 6,
                    "is_r8_or_minified": True,
                    "is_boundary_or_limitation": index % 6 == 5,
                    "is_clean_real": False,
                    "is_partial_real": True,
                },
                "context": {
                    "recall_status": "report-only-source-context-suggestion",
                    "next_action": "surface-as-source-context-report-only-suggestion",
                },
            }
        )
    return {
        "sources": {"unit": "test"},
        "rows": rows,
    }


def test_row_to_tokens_uses_structured_evidence_not_label_leakage():
    row = make_dataset()["rows"][0]
    tokens = row_to_tokens(row)

    assert "src:matcher-recall" in tokens
    assert "coordinate:com.google.code.gson:gson" in tokens
    assert "label-space:report-only-triage" in tokens
    assert "label:suggest_report_only" not in tokens


def test_build_corpus_creates_padded_grouped_token_rows():
    payload = build_corpus(make_dataset(), max_sequence_length=16)

    assert payload["schema_version"] == "ai-r8-dl-token-corpus-v2"
    assert payload["report_only"] is True
    assert payload["production_wiring"] == "disabled"
    assert payload["summary"]["rows"] == 12
    assert payload["summary"]["vocab_size"] > 2
    assert set(payload["summary"]["splits"]) == {"test", "train", "validation"}
    assert len(payload["rows"][0]["token_ids"]) == 16
    assert payload["rows"][0]["length"] <= 16
