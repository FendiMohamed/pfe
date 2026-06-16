from __future__ import annotations

import json
from pathlib import Path
from typing import Any


DEFAULT_SOURCE_KNOWN_JSON = Path(
    "data/results/experiments/version-band-rerank-experiment.json"
)
DEFAULT_APK_ONLY_JSON = Path(
    "data/results/experiments/version-band-apk-reranker-v2.json"
)
DEFAULT_OUTPUT_JSON = Path(
    "data/results/experiments/version-band-candidate-expansion-v3.json"
)
DEFAULT_OUTPUT_DOC = Path(
    "docs/evaluation/VERSION_BAND_CANDIDATE_EXPANSION_V3.md"
)


RECORDED_DEEP_PROBES: list[dict[str, Any]] = [
    {
        "case_id": "cryptomator-lite",
        "coordinate": "androidx.activity:activity",
        "baseline_selected_version": "1.8.0",
        "source_version_for_evaluation_only": "1.8.1",
        "reference_db": "data/reference_db/reference_features_demo_final_large_v2.sqlite",
        "references_scored": 134,
        "apk_analysis_seconds": 72.98,
        "reference_load_seconds": 5.07,
        "expanded_scoring_seconds": 104.95,
        "scoring_profile": "full-default-weights-with-version-unique-siblings",
        "expanded_selected_version": "1.2.0-alpha01",
        "expanded_selected_score": 0.886915,
        "top_candidates": [
            {"version": "1.2.0-alpha01", "score": 0.886915},
            {"version": "1.1.0", "score": 0.884645},
            {"version": "1.1.0-alpha02", "score": 0.884645},
            {"version": "1.1.0-alpha03", "score": 0.884645},
        ],
        "evaluation_classification": "expanded-candidate-scoring-wrong-to-wrong",
        "lesson": (
            "Making more same-coordinate versions visible is not enough: generic "
            "bytecode similarity favored older feature-equivalent Activity versions."
        ),
    },
    {
        "case_id": "cryptomator-lite",
        "coordinate": "androidx.activity:activity",
        "baseline_selected_version": "1.8.0",
        "source_version_for_evaluation_only": "1.8.1",
        "reference_db": "data/reference_db/reference_features_demo_final_large_v2.sqlite",
        "references_scored": 134,
        "scoring_profile": "default-weights-no-sibling-unique-features",
        "expanded_selected_version": "1.2.0-alpha01",
        "expanded_selected_score": 0.886915,
        "source_version_rank": 40,
        "evaluation_classification": "expanded-candidate-scoring-wrong-to-wrong",
        "lesson": (
            "Removing sibling unique-feature cost did not change the selected "
            "version; the source version remained far below the top candidates."
        ),
    },
]


def build_payload(
    *,
    source_known_json: str | Path = DEFAULT_SOURCE_KNOWN_JSON,
    apk_only_json: str | Path = DEFAULT_APK_ONLY_JSON,
) -> dict[str, Any]:
    source_known = _load_json(source_known_json)
    apk_only = _load_json(apk_only_json)
    source_summary = source_known.get("summary", {})
    apk_summary = apk_only.get("summary", {})

    promotion_gate = evaluate_promotion_gate(source_summary, apk_summary)
    return {
        "schema_version": "version-band-candidate-expansion-v3",
        "report_only": True,
        "default_matcher_unchanged": True,
        "verdict": promotion_gate["verdict"],
        "scope": (
            "Promotion-gate diagnostic for version-band candidate expansion. "
            "It combines the source-known upper-bound result, the APK-only "
            "source-free reranker result, and a bounded deep same-coordinate "
            "candidate expansion pilot. It does not change matcher scoring, "
            "selected versions, SBOM output, CVE labels, or metrics."
        ),
        "sources": {
            "source_known_json": normalize_path(source_known_json),
            "apk_only_json": normalize_path(apk_only_json),
        },
        "source_known_upper_bound": {
            "baseline_wrong_version_rows_in_scope": source_summary.get(
                "baseline_wrong_version_rows_in_scope",
                0,
            ),
            "source_known_fixable_wrong_version_rows": source_summary.get(
                "source_known_fixable_wrong_version_rows",
                0,
            ),
            "exact_control_rows_in_scope": source_summary.get(
                "exact_control_rows_in_scope",
                0,
            ),
            "false_positive_extra_control_rows_in_scope": source_summary.get(
                "false_positive_extra_control_rows_in_scope",
                0,
            ),
        },
        "apk_only_reranker": {
            "rows_evaluated": apk_summary.get("rows_evaluated", 0),
            "wrong_version_rows_in_scope": apk_summary.get(
                "wrong_version_rows_in_scope",
                0,
            ),
            "apk_only_reranker_changes": apk_summary.get(
                "apk_only_reranker_changes",
                0,
            ),
            "apk_only_wrong_version_fixes": apk_summary.get(
                "apk_only_wrong_version_fixes",
                0,
            ),
            "apk_only_exact_control_regressions": apk_summary.get(
                "apk_only_exact_control_regressions",
                0,
            ),
            "wrong_version_rows_with_source_in_baseline_alternatives": apk_summary.get(
                "wrong_version_rows_with_source_in_baseline_alternatives",
                0,
            ),
            "wrong_version_source_candidate_availability_percent": apk_summary.get(
                "wrong_version_source_candidate_availability_percent",
                0.0,
            ),
        },
        "deep_candidate_expansion_pilot": RECORDED_DEEP_PROBES,
        "promotion_gate": promotion_gate,
        "next_actions": [
            "Do not promote version-band reranking today.",
            "Improve source-free candidate generation before reranking: keep more same-coordinate versions visible in APK-only reports.",
            "Add stronger version-specific independent features before retrying: version-unique literals/context, dependency-era coherence, and structural similarity.",
            "Run deep rescoring in small batches because one APK+coordinate pilot took about three minutes on this machine.",
            "The follow-up router r8-structural-recall lane is evaluated separately as report-only matcher-recall transparency, not SBOM emission.",
        ],
    }


def evaluate_promotion_gate(
    source_summary: dict[str, Any],
    apk_summary: dict[str, Any],
) -> dict[str, Any]:
    source_known_fixes = int(
        source_summary.get("source_known_fixable_wrong_version_rows") or 0
    )
    apk_fixes = int(apk_summary.get("apk_only_wrong_version_fixes") or 0)
    exact_regressions = int(
        apk_summary.get("apk_only_exact_control_regressions") or 0
    )
    false_positive_changes = int(
        apk_summary.get("apk_only_false_positive_control_changes") or 0
    )
    visible = int(
        apk_summary.get("wrong_version_rows_with_source_in_baseline_alternatives")
        or 0
    )
    wrong_scope = int(apk_summary.get("wrong_version_rows_in_scope") or 0)

    blockers: list[str] = []
    if source_known_fixes:
        blockers.append(
            "source-known opportunity exists, but source-known fixes are not APK-only evidence"
        )
    if apk_fixes <= 0:
        blockers.append("APK-only reranker produced zero wrong-version fixes")
    if exact_regressions:
        blockers.append("APK-only reranker regressed exact controls")
    if false_positive_changes:
        blockers.append("APK-only reranker changed false-positive controls")
    if wrong_scope and visible / wrong_scope < 0.25:
        blockers.append(
            "source version is visible in too few baseline alternatives for promotion"
        )
    blockers.append(
        "deep same-coordinate expansion pilot selected a wrong old version"
    )

    promotable = (
        apk_fixes >= 50
        and exact_regressions == 0
        and false_positive_changes == 0
        and wrong_scope > 0
        and visible / wrong_scope >= 0.25
    )
    return {
        "promotable": promotable,
        "verdict": (
            "promote-version-band-reranker"
            if promotable
            else "do-not-promote-candidate-expansion-v3"
        ),
        "minimum_fix_target_for_promotion": 50,
        "required_exact_control_regressions": 0,
        "required_false_positive_control_changes": 0,
        "minimum_source_candidate_visibility_percent": 25.0,
        "blockers": blockers,
    }


def write_outputs(
    payload: dict[str, Any],
    *,
    output_json: str | Path = DEFAULT_OUTPUT_JSON,
    output_doc: str | Path = DEFAULT_OUTPUT_DOC,
) -> dict[str, Any]:
    json_path = Path(output_json)
    doc_path = Path(output_doc)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    doc_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    doc_path.write_text(build_markdown(payload), encoding="utf-8")
    return {
        "json": normalize_path(json_path),
        "doc": normalize_path(doc_path),
        "verdict": payload["verdict"],
        "promotable": payload["promotion_gate"]["promotable"],
    }


def build_markdown(payload: dict[str, Any]) -> str:
    source = payload["source_known_upper_bound"]
    apk = payload["apk_only_reranker"]
    gate = payload["promotion_gate"]
    lines = [
        "# Version-Band Candidate Expansion V3",
        "",
        "Generated by `apk-sbom version-band-candidate-expansion` or `scripts/build_version_band_candidate_expansion_v3.py`.",
        "",
        f"Verdict: `{payload['verdict']}`.",
        "",
        payload["scope"],
        "",
        "## Source-Known Upper Bound",
        "",
        f"- Scoped wrong-version rows: `{source['baseline_wrong_version_rows_in_scope']}`",
        f"- Source-known fixable rows: `{source['source_known_fixable_wrong_version_rows']}`",
        f"- Exact controls: `{source['exact_control_rows_in_scope']}`",
        f"- False-positive controls: `{source['false_positive_extra_control_rows_in_scope']}`",
        "",
        "## APK-Only Reranker Result",
        "",
        f"- Rows evaluated: `{apk['rows_evaluated']}`",
        f"- Wrong-version rows in scope: `{apk['wrong_version_rows_in_scope']}`",
        f"- APK-only changes: `{apk['apk_only_reranker_changes']}`",
        f"- APK-only wrong-version fixes: `{apk['apk_only_wrong_version_fixes']}`",
        f"- Exact-control regressions: `{apk['apk_only_exact_control_regressions']}`",
        f"- Source version visible in baseline alternatives: `{apk['wrong_version_rows_with_source_in_baseline_alternatives']}` (`{apk['wrong_version_source_candidate_availability_percent']}%`)",
        "",
        "## Deep Candidate Expansion Pilot",
        "",
            "| Case | Coordinate | Scoring profile | Baseline | Source eval only | Refs | Expanded selected | Result |",
            "|---|---|---|---|---|---:|---|---|",
    ]
    for probe in payload["deep_candidate_expansion_pilot"]:
        lines.append(
            "| "
            f"{probe['case_id']} | "
            f"`{probe['coordinate']}` | "
            f"{probe['scoring_profile']} | "
            f"{probe['baseline_selected_version']} | "
            f"{probe['source_version_for_evaluation_only']} | "
            f"{probe['references_scored']} | "
            f"{probe['expanded_selected_version']} | "
            f"{probe['evaluation_classification']} |"
        )
    lines.extend(
        [
            "",
            "## Promotion Gate",
            "",
            f"- Promotable: `{str(gate['promotable']).lower()}`",
            f"- Minimum fix target: `{gate['minimum_fix_target_for_promotion']}`",
            f"- Required exact-control regressions: `{gate['required_exact_control_regressions']}`",
            f"- Required false-positive control changes: `{gate['required_false_positive_control_changes']}`",
            f"- Minimum source-candidate visibility: `{gate['minimum_source_candidate_visibility_percent']}%`",
            "",
            "### Blockers",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in gate["blockers"])
    lines.extend(
        [
            "",
            "## Next Actions",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in payload["next_actions"])
    lines.extend(["", "## Source Artifacts", ""])
    for key, value in sorted(payload["sources"].items()):
        lines.append(f"- `{key}`: `{value}`")
    lines.append("")
    return "\n".join(lines)


def _load_json(path: str | Path) -> dict[str, Any]:
    source = Path(path)
    if not source.exists():
        return {}
    return json.loads(source.read_text(encoding="utf-8"))


def normalize_path(path: str | Path) -> str:
    return str(path).replace("\\", "/")
