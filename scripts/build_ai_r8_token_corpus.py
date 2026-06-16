from __future__ import annotations

import argparse
import json
from pathlib import Path


DEFAULT_OUTPUT_JSON = Path(
    "data/results/experiments/ai-r8-dl-prototype/token-corpus.json"
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Build an isolated DL-prototype token corpus manifest. This script is "
            "not wired into production reports."
        ),
    )
    parser.add_argument(
        "--output-json",
        default=str(DEFAULT_OUTPUT_JSON),
        help="Output token-corpus manifest JSON.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    output = Path(args.output_json)
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": "ai-r8-dl-token-corpus-v1",
        "status": "prototype-manifest",
        "report_only": True,
        "production_wiring": "disabled",
        "task": "identity-risk classification over DEX/opcode token sequences",
        "inputs": [
            "controlled R8 fixtures",
            "known source-validated rows",
            "future opcode/DEX token extraction outputs",
        ],
        "limits": [
            "This corpus builder is a Phase 6B scaffold.",
            "It does not train a model and does not change reports or SBOMs.",
        ],
    }
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output_json": str(output), "status": payload["status"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

