from __future__ import annotations

import argparse
import json
from pathlib import Path

from apk_sbom.r8_phase5_experiment import (
    DEFAULT_OUTPUT_DOC,
    DEFAULT_OUTPUT_JSON,
    DEFAULT_PHASE4_JSON,
    build_markdown,
    build_payload,
    classify_trigger_outcome,
    evaluate_trigger_row,
    normalize_path,
    verdict_from_summary,
    write_outputs,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Evaluate the Phase 5 scoped R8 trigger without changing default scoring."
    )
    parser.add_argument("--phase4-json", default=str(DEFAULT_PHASE4_JSON))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--output-doc", default=str(DEFAULT_OUTPUT_DOC))
    return parser


def main() -> int:
    args = build_parser().parse_args()
    payload = build_payload(Path(args.phase4_json))
    result = write_outputs(
        payload,
        output_json=Path(args.output_json),
        output_doc=Path(args.output_doc),
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


__all__ = [
    "build_markdown",
    "build_payload",
    "classify_trigger_outcome",
    "evaluate_trigger_row",
    "normalize_path",
    "verdict_from_summary",
]


if __name__ == "__main__":
    raise SystemExit(main())
