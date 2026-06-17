from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from apk_sbom.apk_extractor import DEX_PATTERN, normalized_zip_names  # noqa: E402
from apk_sbom.dex_analyzer import analyze_apk_dex, silence_androguard_logging  # noqa: E402


DEFAULT_OUTPUT_JSON = Path(
    "data/results/experiments/ai-r8-raw-opcode-prototype/raw-opcode-corpus.json"
)
DEFAULT_OUTPUT_DOC = Path("docs/evaluation/AI_R8_RAW_OPCODE_CORPUS.md")
DEFAULT_APK_ROOT = Path("data/test_apks")
DEFAULT_MAX_APKS = 14
DEFAULT_MAX_METHODS_PER_APK = 120
DEFAULT_MAX_SEQUENCE_LENGTH = 128
SPECIAL_TOKENS = ["<pad>", "<unk>", "<cls>", "<sep>"]


@dataclass(frozen=True)
class MethodOpcodeRow:
    row_id: str
    apk_path: str
    case_id: str
    source_role: str
    obfuscation_profile: str
    label: str
    dex_file: str
    class_name: str
    method_name: str
    tokens: list[str]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Build an isolated raw DEX/opcode token corpus for a future R8 "
            "Transformer prototype. The artifact is report-only research evidence "
            "and is not production matcher wiring."
        )
    )
    parser.add_argument(
        "--apk",
        action="append",
        default=[],
        help="APK path to include. Can be supplied multiple times. Defaults to a bounded generated-R8 plus smoke sample.",
    )
    parser.add_argument(
        "--apk-root",
        default=str(DEFAULT_APK_ROOT),
        help="APK root used when --apk is not supplied.",
    )
    parser.add_argument(
        "--max-apks",
        type=int,
        default=DEFAULT_MAX_APKS,
        help="Maximum APKs to analyze from the default discovery set.",
    )
    parser.add_argument(
        "--max-methods-per-apk",
        type=int,
        default=DEFAULT_MAX_METHODS_PER_APK,
        help="Maximum method opcode sequences stored per APK.",
    )
    parser.add_argument(
        "--max-sequence-length",
        type=int,
        default=DEFAULT_MAX_SEQUENCE_LENGTH,
        help="Maximum opcode tokens per method sequence.",
    )
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--output-doc", default=str(DEFAULT_OUTPUT_DOC))
    return parser


def main() -> int:
    args = build_parser().parse_args()
    apk_paths = [Path(path) for path in args.apk] or discover_default_apks(
        Path(args.apk_root),
        max_apks=args.max_apks,
    )
    payload = build_payload(
        apk_paths,
        max_methods_per_apk=args.max_methods_per_apk,
        max_sequence_length=args.max_sequence_length,
    )
    result = write_outputs(payload, output_json=args.output_json, output_doc=args.output_doc)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


def discover_default_apks(apk_root: Path, *, max_apks: int) -> list[Path]:
    generated = sorted(apk_root.glob("generated-*-r8-*.apk"))
    controlled = sorted(apk_root.glob("controlled-*-r8-*.apk"))
    smoke = [
        apk_root / "real" / "F-Droid.apk",
        apk_root / "real" / "aegis-authenticator" / "aegis-authenticator.apk",
    ]
    smoke_existing = [path for path in smoke if path.exists()]
    remaining_slots = max(0, max_apks - len(smoke_existing))
    generated_existing = [path for path in generated if path.exists()]
    controlled_existing = [path for path in controlled if path.exists()]
    return (generated_existing + controlled_existing)[:remaining_slots] + smoke_existing


def build_payload(
    apk_paths: list[Path],
    *,
    max_methods_per_apk: int = DEFAULT_MAX_METHODS_PER_APK,
    max_sequence_length: int = DEFAULT_MAX_SEQUENCE_LENGTH,
) -> dict[str, Any]:
    rows: list[MethodOpcodeRow] = []
    apk_summaries: list[dict[str, Any]] = []
    skipped: list[dict[str, str]] = []
    for apk_path in apk_paths:
        try:
            analysis = analyze_apk_dex(apk_path, include_members=False)
            method_rows = extract_method_opcode_rows(
                apk_path,
                max_methods=max_methods_per_apk,
            )
        except Exception as exc:
            skipped.append({"apk_path": normalize_path(apk_path), "reason": str(exc)})
            continue
        rows.extend(method_rows)
        apk_summaries.append(
            {
                "apk_path": normalize_path(apk_path),
                "case_id": case_id_from_path(apk_path),
                "source_role": source_role(apk_path),
                "obfuscation_profile": obfuscation_profile(apk_path),
                "label": corpus_label(apk_path),
                "dex_files_analyzed": analysis.dex_files_analyzed,
                "dex_files_failed": analysis.dex_files_failed,
                "classes": analysis.classes_count,
                "methods": analysis.methods_count,
                "stored_method_sequences": len(method_rows),
                "distinct_opcodes": len(analysis.opcode_histogram),
                "distinct_opcode_ngrams": len(analysis.opcode_ngrams),
                "distinct_basic_block_fingerprints": len(
                    analysis.basic_block_opcode_fingerprints
                ),
                "parse_errors": [error.__dict__ for error in analysis.parse_errors[:10]],
            }
        )

    token_counts = Counter(token for row in rows for token in row.tokens)
    vocabulary = {
        token: token_id
        for token_id, token in enumerate(SPECIAL_TOKENS + sorted(token_counts))
    }
    tokenized_rows = [
        tokenized_row(row, vocabulary, max_sequence_length=max_sequence_length)
        for row in rows
    ]
    label_counts = Counter(row["label"] for row in tokenized_rows)
    source_role_counts = Counter(row["source_role"] for row in tokenized_rows)
    obfuscation_counts = Counter(row["obfuscation_profile"] for row in tokenized_rows)
    return {
        "schema_version": "ai-r8-raw-opcode-corpus-v1",
        "report_only": True,
        "production_wiring": "disabled",
        "task": "method-level R8/obfuscation identity-risk research from raw DEX opcode sequences",
        "sequence_unit": "method opcode sequence",
        "max_sequence_length": max_sequence_length,
        "max_methods_per_apk": max_methods_per_apk,
        "sources": {
            "apk_paths": [normalize_path(path) for path in apk_paths],
        },
        "summary": {
            "apks_requested": len(apk_paths),
            "apks_analyzed": len(apk_summaries),
            "apks_skipped": len(skipped),
            "method_sequence_rows": len(tokenized_rows),
            "vocab_size": len(vocabulary),
            "labels": dict(sorted(label_counts.items())),
            "source_roles": dict(sorted(source_role_counts.items())),
            "obfuscation_profiles": dict(sorted(obfuscation_counts.items())),
            "production_effect": "none",
        },
        "limitations": [
            "This is a bounded raw DEX/opcode corpus prototype, not a large external pretraining corpus.",
            "Rows are method-level opcode sequences capped for reproducible local execution.",
            "Labels describe APK role/obfuscation profile for research triage; they are not exact SBOM version authority.",
            "The corpus is not wired into generate-report, matcher scoring, SBOM output, or CVE labeling.",
        ],
        "apk_summaries": apk_summaries,
        "skipped_apks": skipped,
        "vocabulary": vocabulary,
        "rows": tokenized_rows,
    }


def extract_method_opcode_rows(apk_path: Path, *, max_methods: int) -> list[MethodOpcodeRow]:
    silence_androguard_logging()
    try:
        from androguard.core.dex import DEX
    except Exception as exc:
        raise RuntimeError("androguard is required for raw opcode extraction") from exc

    rows: list[MethodOpcodeRow] = []
    case_id = case_id_from_path(apk_path)
    role = source_role(apk_path)
    obfuscation = obfuscation_profile(apk_path)
    label = corpus_label(apk_path)
    with zipfile.ZipFile(apk_path) as apk_zip:
        names = normalized_zip_names(apk_zip.namelist())
        dex_files = [name for name in names if DEX_PATTERN.match(Path(name).name)]
        for dex_file in dex_files:
            dex = DEX(apk_zip.read(dex_file))
            for dex_class in dex.get_classes():
                class_name = str(dex_class.get_name())
                for method in dex_class.get_methods():
                    if len(rows) >= max_methods:
                        return rows
                    tokens = method_opcode_tokens(method)
                    if not tokens:
                        continue
                    method_name = str(method.get_name())
                    rows.append(
                        MethodOpcodeRow(
                            row_id=(
                                f"{case_id}:{dex_file}:{len(rows)}:"
                                f"{short_token(class_name)}:{short_token(method_name)}"
                            ),
                            apk_path=normalize_path(apk_path),
                            case_id=case_id,
                            source_role=role,
                            obfuscation_profile=obfuscation,
                            label=label,
                            dex_file=dex_file,
                            class_name=class_name,
                            method_name=method_name,
                            tokens=tokens,
                        )
                    )
    return rows


def method_opcode_tokens(method: object) -> list[str]:
    try:
        instructions = method.get_instructions()
    except Exception:
        return []
    tokens: list[str] = []
    for instruction in instructions:
        try:
            name = str(instruction.get_name())
        except Exception:
            continue
        if name:
            tokens.append("op:" + name)
    return tokens


def tokenized_row(
    row: MethodOpcodeRow,
    vocabulary: dict[str, int],
    *,
    max_sequence_length: int,
) -> dict[str, Any]:
    tokens = ["<cls>"] + row.tokens[: max_sequence_length - 2] + ["<sep>"]
    token_ids = [vocabulary.get(token, vocabulary["<unk>"]) for token in tokens]
    token_ids += [vocabulary["<pad>"]] * (max_sequence_length - len(token_ids))
    return {
        "row_id": row.row_id,
        "apk_path": row.apk_path,
        "case_id": row.case_id,
        "source_role": row.source_role,
        "obfuscation_profile": row.obfuscation_profile,
        "label": row.label,
        "dex_file": row.dex_file,
        "class_name": row.class_name,
        "method_name": row.method_name,
        "token_ids": token_ids,
        "length": min(len(tokens), max_sequence_length),
        "report_only": True,
    }


def source_role(apk_path: Path) -> str:
    parts = {part.lower() for part in apk_path.parts}
    stem = apk_path.stem.lower()
    if "real" in parts:
        return "real-apk-smoke"
    if stem.startswith("generated-"):
        return "generated-controlled"
    if stem.startswith("controlled-"):
        return "controlled-fixture"
    if "limitation" in parts:
        return "limitation-fixture"
    return "unknown"


def obfuscation_profile(apk_path: Path) -> str:
    stem = apk_path.stem.lower()
    profiles = [
        "r8-inline-stress",
        "r8-shrink-optimize",
        "r8-optimize",
        "r8-repackage",
        "r8-rename",
        "r8-shrink",
        "clear",
    ]
    for profile in profiles:
        if profile in stem:
            return profile
    if source_role(apk_path) == "real-apk-smoke":
        return "real-world-unknown"
    return "unknown"


def corpus_label(apk_path: Path) -> str:
    role = source_role(apk_path)
    profile = obfuscation_profile(apk_path)
    if role in {"generated-controlled", "controlled-fixture"}:
        return profile
    return role


def case_id_from_path(apk_path: Path) -> str:
    stem = apk_path.stem.lower()
    stem = re.sub(r"[^a-z0-9]+", "-", stem).strip("-")
    return stem or "apk"


def short_token(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9]+", "-", value).strip("-")
    return cleaned[-32:] or "x"


def write_outputs(
    payload: dict[str, Any],
    *,
    output_json: str | Path = DEFAULT_OUTPUT_JSON,
    output_doc: str | Path = DEFAULT_OUTPUT_DOC,
) -> dict[str, Any]:
    output_json = Path(output_json)
    output_doc = Path(output_doc)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_doc.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    output_doc.write_text(build_markdown(payload), encoding="utf-8")
    summary = payload["summary"]
    return {
        "json": normalize_path(output_json),
        "doc": normalize_path(output_doc),
        "apks_analyzed": summary["apks_analyzed"],
        "apks_skipped": summary["apks_skipped"],
        "method_sequence_rows": summary["method_sequence_rows"],
        "vocab_size": summary["vocab_size"],
    }


def build_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# AI R8 Raw Opcode Corpus",
        "",
        "Generated by `scripts/build_ai_r8_raw_opcode_corpus.py`.",
        "",
        "This artifact turns the raw DEX/opcode Transformer future-work point into a concrete corpus prototype. It stores bounded method-level opcode token sequences for research training/evaluation only.",
        "",
        "## Summary",
        "",
        f"- APKs requested: `{summary['apks_requested']}`",
        f"- APKs analyzed: `{summary['apks_analyzed']}`",
        f"- APKs skipped: `{summary['apks_skipped']}`",
        f"- Method opcode sequence rows: `{summary['method_sequence_rows']}`",
        f"- Vocabulary size: `{summary['vocab_size']}`",
        f"- Max sequence length: `{payload['max_sequence_length']}`",
        f"- Max methods per APK: `{payload['max_methods_per_apk']}`",
        f"- Production effect: `{summary['production_effect']}`",
        "",
        "## Labels",
        "",
        "| Label | Rows |",
        "|---|---:|",
    ]
    append_counts(lines, summary["labels"])
    lines.extend(
        [
            "",
            "## Obfuscation Profiles",
            "",
            "| Profile | Rows |",
            "|---|---:|",
        ]
    )
    append_counts(lines, summary["obfuscation_profiles"])
    lines.extend(
        [
            "",
            "## APK Summaries",
            "",
            "| APK | Role | Profile | DEX analyzed | Classes | Methods | Stored sequences | Distinct opcodes |",
            "|---|---|---|---:|---:|---:|---:|---:|",
        ]
    )
    for row in payload["apk_summaries"]:
        lines.append(
            "| "
            f"`{row['apk_path']}` | "
            f"`{row['source_role']}` | "
            f"`{row['obfuscation_profile']}` | "
            f"{row['dex_files_analyzed']} | "
            f"{row['classes']} | "
            f"{row['methods']} | "
            f"{row['stored_method_sequences']} | "
            f"{row['distinct_opcodes']} |"
        )
    if not payload["apk_summaries"]:
        lines.append("| none | none | none | 0 | 0 | 0 | 0 | 0 |")
    if payload["skipped_apks"]:
        lines.extend(
            [
                "",
                "## Skipped APKs",
                "",
                "| APK | Reason |",
                "|---|---|",
            ]
        )
        for row in payload["skipped_apks"]:
            lines.append(f"| `{row['apk_path']}` | `{row['reason']}` |")
    lines.extend(
        [
            "",
            "## Limitations",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in payload["limitations"])
    lines.append("")
    return "\n".join(lines)


def append_counts(lines: list[str], counts: dict[str, int]) -> None:
    if not counts:
        lines.append("| none | 0 |")
        return
    for key, value in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
        lines.append(f"| `{key}` | {value} |")


def normalize_path(path: str | Path) -> str:
    return Path(path).as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
