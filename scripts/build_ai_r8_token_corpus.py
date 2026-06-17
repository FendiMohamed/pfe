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
DEFAULT_MVP_SAFE_OUTPUT_JSON = Path(
    "data/results/experiments/ai-r8-dl-prototype/token-corpus-mvp-safe.json"
)
MAX_SEQUENCE_LENGTH = 64
SPECIAL_TOKENS = ["<pad>", "<unk>"]
CORPUS_PROFILES = ["full", "mvp-safe"]
MVP_SAFE_FEATURE_COLUMNS = [
    "best_score",
    "score_gap_to_best",
    "identity_confidence",
    "package_score",
    "class_score",
    "method_score",
    "opcode_score",
    "literal_score",
    "dependency_score",
    "matched_packages",
    "matched_classes",
    "matched_methods",
    "is_r8_or_minified",
]


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
        "--profile",
        choices=CORPUS_PROFILES,
        default="full",
        help=(
            "Corpus profile. 'full' reproduces the original research prototype; "
            "'mvp-safe' strips source-version tokens and source-validation-only "
            "context before training."
        ),
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
    payload = build_corpus(
        dataset,
        max_sequence_length=args.max_sequence_length,
        profile=args.profile,
    )
    output = Path(args.output_json)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "output_json": str(output),
                "profile": payload["profile"],
                "rows": payload["summary"]["rows"],
                "vocab_size": payload["summary"]["vocab_size"],
                "max_sequence_length": payload["max_sequence_length"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def build_corpus(
    dataset: dict,
    *,
    max_sequence_length: int,
    profile: str = "full",
) -> dict:
    if profile not in CORPUS_PROFILES:
        raise ValueError(f"unknown AI R8 token corpus profile: {profile}")
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
        tokens = row_to_tokens(row, profile=profile)
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
        "profile": profile,
        "source_dataset": dataset.get("sources", {}),
        "report_only": True,
        "production_wiring": "disabled",
        "task": _task_for_profile(profile),
        "mvp_safe": profile == "mvp-safe",
        "excluded_from_mvp_safe_profile": _excluded_from_mvp_safe_profile(),
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
            _profile_limitation(profile),
            "It demonstrates DL workflow and identity-risk triage only.",
            "It is not exact-version authority; reports may surface status only.",
        ],
        "rows": tokenized,
    }


def row_to_tokens(row: dict, *, profile: str = "full") -> list[str]:
    if profile not in CORPUS_PROFILES:
        raise ValueError(f"unknown AI R8 token corpus profile: {profile}")
    tokens = [
        "src:" + str(row.get("row_source") or "unknown"),
        "label-space:report-only-triage",
    ]
    tokens.extend(
        _coordinate_tokens(
            str(row.get("coordinate") or ""),
            include_raw=profile == "full",
        )
    )
    if profile == "full":
        tokens.extend(_version_tokens("source-version", str(row.get("source_version") or "")))
        tokens.extend(
            _version_tokens("candidate-version", str(row.get("candidate_version") or ""))
        )
        feature_columns = FEATURE_COLUMNS
    else:
        tokens.extend(
            _safe_version_shape_tokens(
                "candidate-version",
                str(row.get("candidate_version") or ""),
            )
        )
        feature_columns = MVP_SAFE_FEATURE_COLUMNS
    features = row.get("features", {})
    for feature in feature_columns:
        value = features.get(feature)
        tokens.append(f"feature:{feature}:{_feature_bucket(value)}")
    if profile == "full":
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


def _coordinate_tokens(coordinate: str, *, include_raw: bool = True) -> list[str]:
    if not coordinate:
        return ["coordinate:missing"]
    group, _, artifact = coordinate.partition(":")
    tokens = ["coordinate:" + coordinate.lower()] if include_raw else []
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


def _safe_version_shape_tokens(prefix: str, version: str) -> list[str]:
    if not version:
        return [f"{prefix}:missing"]
    parts = _split_words(version)
    numeric_parts = [part for part in parts if part.isdigit()]
    tokens = [
        f"{prefix}:numeric-parts:{min(len(numeric_parts), 4)}",
        f"{prefix}:has-prerelease:{str(_has_prerelease(version)).lower()}",
        f"{prefix}:has-snapshot:{str('snapshot' in version.lower()).lower()}",
    ]
    if numeric_parts:
        major = int(numeric_parts[0])
        tokens.append(f"{prefix}:major-band:{_major_band(major)}")
    return tokens


def _has_prerelease(version: str) -> bool:
    lowered = version.lower()
    return any(token in lowered for token in ("alpha", "beta", "rc", "m", "preview"))


def _major_band(major: int) -> str:
    if major <= 0:
        return "zero"
    if major == 1:
        return "one"
    if major <= 3:
        return "two-three"
    if major <= 9:
        return "four-nine"
    return "ten-plus"


def _task_for_profile(profile: str) -> str:
    if profile == "mvp-safe":
        return (
            "multiclass identity-risk classification from source-free structured "
            "R8/matcher evidence tokens"
        )
    return "multiclass identity-risk classification from structured R8/matcher evidence tokens"


def _profile_limitation(profile: str) -> str:
    if profile == "mvp-safe":
        return (
            "This source-free profile strips source-version tokens, raw candidate "
            "versions, source-rank features, source-validation role flags, and "
            "diagnostic context labels before training."
        )
    return "This is a structured-token prototype over project evidence rows, not a large smali pretraining corpus."


def _excluded_from_mvp_safe_profile() -> list[str]:
    return [
        "source-version tokens",
        "raw candidate-version tokens",
        "raw coordinate token",
        "source_rank feature",
        "is_boundary_or_limitation feature",
        "is_clean_real feature",
        "is_partial_real feature",
        "diagnostic context labels",
    ]


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
