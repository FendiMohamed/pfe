from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from apk_sbom.ai_r8_assistant import (  # noqa: E402
    DEFAULT_TRAINING_DATASET_JSON,
    FEATURE_COLUMNS,
    LABELS,
    deterministic_group_split,
)


DEFAULT_OUTPUT_JSON = Path(
    "data/results/experiments/ai-r8-dl-prototype/token-corpus.json"
)
MAX_SEQUENCE_LENGTH = 64
SPECIAL_TOKENS = ["<pad>", "<unk>"]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Build an isolated structured-token corpus for the Phase 6B tiny "
            "Transformer prototype. Reports may surface prototype status only; "
            "production decision wiring remains disabled."
        ),
    )
    parser.add_argument(
        "--dataset-json",
        default=str(DEFAULT_TRAINING_DATASET_JSON),
        help="AI R8 training dataset JSON.",
    )
    parser.add_argument(
        "--output-json",
        default=str(DEFAULT_OUTPUT_JSON),
        help="Output token-corpus JSON.",
    )
    parser.add_argument(
        "--max-sequence-length",
        type=int,
        default=MAX_SEQUENCE_LENGTH,
        help="Maximum token IDs stored per row.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    dataset = json.loads(Path(args.dataset_json).read_text(encoding="utf-8"))
    payload = build_corpus(dataset, max_sequence_length=args.max_sequence_length)
    output = Path(args.output_json)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "output_json": str(output),
                "rows": payload["summary"]["rows"],
                "vocab_size": payload["summary"]["vocab_size"],
                "max_sequence_length": payload["max_sequence_length"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def build_corpus(dataset: dict, *, max_sequence_length: int) -> dict:
    rows = dataset.get("rows", [])
    split = deterministic_group_split(rows)
    split_by_index = {}
    for name, indices in (
        ("train", split["train_indices"]),
        ("validation", split["validation_indices"]),
        ("test", split["test_indices"]),
    ):
        for index in indices:
            split_by_index[index] = name

    tokenized = []
    token_counts: Counter[str] = Counter()
    for index, row in enumerate(rows):
        tokens = row_to_tokens(row)
        token_counts.update(tokens)
        tokenized.append(
            {
                "row_id": row.get("row_id"),
                "case_id": row.get("case_id"),
                "coordinate": row.get("coordinate"),
                "label": row.get("label"),
                "split": split_by_index.get(index, "train"),
                "tokens": tokens,
            }
        )

    vocabulary = {
        token: token_id
        for token_id, token in enumerate(
            SPECIAL_TOKENS + sorted(token_counts.keys()),
        )
    }
    for row in tokenized:
        token_ids = [vocabulary.get(token, vocabulary["<unk>"]) for token in row["tokens"]]
        token_ids = token_ids[:max_sequence_length]
        row["token_ids"] = token_ids + [vocabulary["<pad>"]] * (
            max_sequence_length - len(token_ids)
        )
        row["length"] = min(len(token_ids), max_sequence_length)
        row.pop("tokens")

    label_counts = Counter(row["label"] for row in tokenized)
    split_counts = Counter(row["split"] for row in tokenized)
    return {
        "schema_version": "ai-r8-dl-token-corpus-v2",
        "source_dataset": dataset.get("sources", {}),
        "report_only": True,
        "production_wiring": "disabled",
        "task": "multiclass identity-risk classification from structured R8/matcher evidence tokens",
        "label_set": LABELS,
        "max_sequence_length": max_sequence_length,
        "vocabulary": vocabulary,
        "summary": {
            "rows": len(tokenized),
            "vocab_size": len(vocabulary),
            "labels": dict(sorted(label_counts.items())),
            "splits": dict(sorted(split_counts.items())),
            "case_ids": len({row["case_id"] for row in tokenized if row.get("case_id")}),
        },
        "limitations": [
            "This is a structured-token prototype over project evidence rows, not a large smali pretraining corpus.",
            "It demonstrates DL workflow and identity-risk triage only.",
            "It is not exact-version authority; reports may surface status only.",
        ],
        "rows": tokenized,
    }


def row_to_tokens(row: dict) -> list[str]:
    tokens = [
        "src:" + str(row.get("row_source") or "unknown"),
        "label-space:report-only-triage",
    ]
    tokens.extend(_coordinate_tokens(str(row.get("coordinate") or "")))
    tokens.extend(_version_tokens("source-version", str(row.get("source_version") or "")))
    tokens.extend(_version_tokens("candidate-version", str(row.get("candidate_version") or "")))
    features = row.get("features", {})
    for feature in FEATURE_COLUMNS:
        value = features.get(feature)
        tokens.append(f"feature:{feature}:{_feature_bucket(value)}")
    context = row.get("context", {})
    for key in (
        "recall_status",
        "next_action",
        "result_class",
        "coverage_class",
        "gap_class",
        "reason_label",
        "triage_bucket",
        "trigger_outcome",
        "role",
        "row_type",
    ):
        if context.get(key):
            tokens.extend(_text_tokens(f"context:{key}", str(context[key])))
    return tokens


def _coordinate_tokens(coordinate: str) -> list[str]:
    if not coordinate:
        return ["coordinate:missing"]
    group, _, artifact = coordinate.partition(":")
    tokens = ["coordinate:" + coordinate.lower()]
    tokens.extend("group:" + part for part in _split_words(group))
    tokens.extend("artifact:" + part for part in _split_words(artifact))
    return tokens


def _version_tokens(prefix: str, version: str) -> list[str]:
    if not version:
        return [f"{prefix}:missing"]
    parts = _split_words(version)
    tokens = [f"{prefix}:raw:{version.lower()}"]
    tokens.extend(f"{prefix}:part:{part}" for part in parts)
    return tokens


def _text_tokens(prefix: str, value: str) -> list[str]:
    return [f"{prefix}:{part}" for part in _split_words(value)]


def _split_words(value: str) -> list[str]:
    return [part.lower() for part in re.split(r"[^A-Za-z0-9]+", value) if part]


def _feature_bucket(value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "missing"
    if number == 0:
        return "zero"
    if number < 0.25:
        return "very-low"
    if number < 0.5:
        return "low"
    if number < 0.75:
        return "medium"
    if number < 1.0:
        return "high"
    return "one-or-more"


if __name__ == "__main__":
    raise SystemExit(main())
