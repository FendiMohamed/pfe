from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


DEFAULT_APK_TYPE_JSON = Path("data/results/evaluation/apk-type-evaluation.json")
DEFAULT_GENERATED_BATCH_JSON = Path("data/results/evaluation/generated-apk-category-batch.json")
DEFAULT_HIDDEN_DEX_JSON = Path("data/results/evaluation/hidden-dex-diagnostics.json")
DEFAULT_OPCODE_API_JSON = Path("data/results/experiments/opcode-api-signal-diagnostics.json")
DEFAULT_OUTPUT_JSON = Path("data/results/evaluation/r8-obfuscation-method-selection.json")
DEFAULT_OUTPUT_DOC = Path("docs/research/R8_OBFUSCATION_METHOD_SELECTION.md")


SOURCE_NOTES: list[dict[str, str]] = [
    {
        "source": "Android R8 official guide",
        "url": "https://developer.android.com/topic/performance/app-optimization/enable-app-optimization",
        "evidence": "R8 removes unreachable code, rewrites code, inlines methods, merges classes, obfuscates names, and can optimize resources.",
        "design_impact": "The MVP must not model R8 as name minification only; classifier and fixtures must cover shrink, optimize, inlining, class merging, and repackaging symptoms.",
    },
    {
        "source": "LibHunter / ASE 2024",
        "url": "https://xzf1234.github.io/pdfs/ASE24_LibHunter.pdf",
        "evidence": "The paper finds R8 is common and that inlining plus call-site optimization are among the strongest causes of detector failure; LibHunter adds optimization-resilient semantic matching.",
        "design_impact": "Adopt inlining-aware and call-site-aware scoring only as a scoped experiment after controlled R8 evaluation expands beyond rename and shrink.",
    },
    {
        "source": "SAD / EASE 2025",
        "url": "https://arxiv.org/abs/2504.13547",
        "evidence": "SAD matches class dependency graph summaries and reports strong library-level and version-level F1 on obfuscated apps, while version identification remains a separate structural-similarity problem.",
        "design_impact": "Adopt class-neighbor summaries, stateful/stateless handling, field-operation features, and literal tie-breakers for version disambiguation.",
    },
    {
        "source": "ATVHunter / arXiv 2021",
        "url": "https://arxiv.org/abs/2102.08172",
        "evidence": "ATVHunter combines CDG module decoupling, CFG/opcode matching, and vulnerable-version mapping, and reports strong precision/recall on its evaluation.",
        "design_impact": "Use two-stage matching and basic-block/opcode evidence for version and CVE-oriented detection, but do not assume it solves modern R8 inlining by itself.",
    },
    {
        "source": "LibAttention / SANER 2025",
        "url": "https://aoa0.github.io/pubs/saner25.pdf",
        "evidence": "LibAttention learns Smali/code representations and reports a large F1 improvement on R8-obfuscated datasets, but it is mainly a library-presence classifier rather than an explainable exact-version SBOM pipeline.",
        "design_impact": "Keep ML as a later optional identity/risk classifier, not the first MVP integration path for exact Maven versions.",
    },
    {
        "source": "LibMD / Information Fusion 2025",
        "url": "https://www.sciencedirect.com/science/article/abs/pii/S1566253524006869",
        "evidence": "LibMD describes multi-scale dependency fusion, basic-block context, metadata dependency graphs, and Bayesian posterior scoring to handle obfuscation and adjacent versions.",
        "design_impact": "Use LibMD as the north-star architecture: multi-scale evidence plus probability/confidence, implemented incrementally and explainably.",
    },
    {
        "source": "ObfDetector robustness study / ICSE 2026",
        "url": "https://aoa0.github.io/pubs/icse26.pdf",
        "evidence": "The study reports advanced obfuscation causes large drops for state-of-the-art tools, with library-level F1 below 50 percent and version-level F1 below 10 percent in hard settings.",
        "design_impact": "Do not claim R8-proof recovery; add obfuscation-method classification and keep low-confidence/ambiguous outputs under hard evidence loss.",
    },
    {
        "source": "Revisiting TPL Detection / arXiv 2025",
        "url": "https://arxiv.org/abs/2509.04091",
        "evidence": "The benchmark exposes R8-era fragility, weak version discrimination, threshold generalization issues, and runtime costs across tools.",
        "design_impact": "Evaluate every R8 feature against a realistic cross-app/control matrix, not a single improved example.",
    },
    {
        "source": "Systematic Assessment / arXiv 2021",
        "url": "https://arxiv.org/abs/2108.01964",
        "evidence": "The assessment evaluates public tools across accuracy, version identification, obfuscation resilience, efficiency, scalability, and usability.",
        "design_impact": "Keep the con diagnostic and evaluation-first, then promote only changes that preserve clean and partial controls.",
    },
]


METHOD_OPTIONS: list[dict[str, str]] = [
    {
        "option": "Reference profile matching only",
        "papers": "LibScout",
        "verdict": "reject as the R8 solution",
        "reason": "Good exact-version baseline when code is preserved, but package and method structure are unstable under shrink, optimize, and inlining.",
        "reuse": "Keep reference DB and exact-version evidence as the backbone, but cap confidence under evidence loss.",
    },
    {
        "option": "Global opcode/API weight",
        "papers": "ATVHunter, LibScan, LibID",
        "verdict": "reject globally for now",
        "reason": "The current project experiment already shows opcode tri-gram weight 0.02 regresses controls, while API-reference weight 0.05 changes no metrics.",
        "reuse": "Keep opcode/API signals as stored diagnostics and later use them only in scoped per-coordinate or high-obfuscation rerankers.",
    },
    {
        "option": "ML-first classifier",
        "papers": "LibAttention",
        "verdict": "defer",
        "reason": "It is promising for R8 library presence, but it adds training data, runtime, explainability, and exact-version/SBOM gaps.",
        "reuse": "Use later as an optional identity or obfuscation-risk classifier, not as the first exact-version path.",
    },
    {
        "option": "Single CDG structural matcher",
        "papers": "SAD, LibPecker",
        "verdict": "partial",
        "reason": "CDG/class summaries are strong under renaming and package changes, but heavy inlining still changes boundaries and reduces version certainty.",
        "reuse": "Add class-neighbor summaries and stateful/stateless features as one layer of a multi-scale scorer.",
    },
    {
        "option": "Explainable multi-scale R8-aware evidence layer",
        "papers": "LibHunter, SAD, ATVHunter, LibMD, LibID, LibScan",
        "verdict": "selected",
        "reason": "It keeps the MVP explainable, builds on current static features, and can be evaluated incrementally before scoring promotion.",
        "reuse": "Classifier, controlled matrix, inert feature extraction, Phase 4 global-blend rejection, a Phase 5 scoped trigger diagnostic, and current-control trigger validation are now in place; default scoring stays unchanged.",
    },
]


INTEGRATION_PHASES: list[dict[str, str]] = [
    {
        "phase": "0",
        "name": "Research and method selection",
        "action": "Record the paper-backed method choice and rejected options.",
        "promotion_rule": "No matcher behavior change.",
    },
    {
        "phase": "1",
        "name": "R8/obfuscation classifier upgrade",
        "action": "Implemented as report-only indicators for short-name density, package flattening/repackaging, class/method loss, low structural coverage, low-confidence component ratio, nonstandard DEX/protector hints, resource shrinking symptoms, and method-inlining/class-merging indicators.",
        "promotion_rule": "Complete for Phase 1; selected components, selected versions, matcher scoring, source-validation metrics, and vulnerability labels stay unchanged.",
    },
    {
        "phase": "2",
        "name": "Controlled R8 evaluation matrix",
        "action": "Implemented as an expanded generated matrix covering clear, rename, shrink, optimize, shrink+optimize, package flattening/repackage, inline-like call-site stress, and multidex/multi-library controls.",
        "promotion_rule": "Complete for Phase 2; matcher scoring and selected component/version behavior stay unchanged.",
    },
    {
        "phase": "3",
        "name": "Inert multi-scale feature extraction",
        "action": "Implemented storage for call-chain opcode fingerprints, basic-block opcode rolling hashes, class-neighbor summaries, field-operation sequences, and version-unique literal/context features.",
        "promotion_rule": "Complete for Phase 3; weights stay disabled.",
    },
    {
        "phase": "4",
        "name": "Scoped multi-scale diagnostic",
        "action": "Run offline controlled and layered real APK diagnostics with the Phase 3 features before any scorer promotion.",
        "promotion_rule": "Expanded pass complete: 4 real source-validated improvement candidates exist, but controlled and real regression blockers reject global multi-scale scoring.",
    },
    {
        "phase": "5",
        "name": "Scoped R8-aware trigger diagnostic",
        "action": "Implemented an experiment-only hard-case trigger around the four Phase 4 improvement profiles, exposed it through the explicit r8-phase5-experiment command and optional generate-report report-only evidence, and validated it against current controls: 4 target improvements kept and 0 triggered regressions/conflicts. The generated report-evidence summary checks 4 target APK reports with 4 separate suggestions and 0 default selection changes.",
        "promotion_rule": "The opt-in experiment command is available, but default scoring stays unchanged; any production scorer must remain narrower than the rejected Phase 4 global blend and needs its own regression tests.",
    },
]


NEXT_IMPLEMENTATION_TASKS: list[dict[str, str]] = [
    {
        "task": "Preserve inert multi-scale R8 feature extraction as diagnostic evidence.",
        "result": "Call-chain opcode fingerprints, basic-block opcode fingerprints, class-neighbor summaries, field-operation sequences, and literal/context features stay stored with weights disabled.",
    },
    {
        "task": "Keep the expanded Phase 4 multi-scale diagnostic as no-promotion evidence.",
        "result": "The blend has useful improvement candidates, but controlled and real regression-risk rows keep matcher scoring and SBOM selection unchanged.",
    },
    {
        "task": "Keep the Phase 5 scoped trigger experiment-only.",
        "result": "The opt-in r8-phase5-experiment command and report-only generate-report evidence keep the four target improvements visible with zero triggered regressions/conflicts. The generated report-evidence summary confirms 4 separate target suggestions and 0 default selection changes, so default matcher and SBOM behavior stay unchanged.",
    },
    {
        "task": "Keep the explicit experiment command separate from production scoring.",
        "result": "Any future scorer wiring must stay off by default until it proves the scoped trigger still improves targets without reintroducing controlled, clean-real, or partial-real regressions.",
    },
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate the R8/obfuscation method selection artifact.",
    )
    parser.add_argument("--apk-type-json", default=str(DEFAULT_APK_TYPE_JSON))
    parser.add_argument("--generated-batch-json", default=str(DEFAULT_GENERATED_BATCH_JSON))
    parser.add_argument("--hidden-dex-json", default=str(DEFAULT_HIDDEN_DEX_JSON))
    parser.add_argument("--opcode-api-json", default=str(DEFAULT_OPCODE_API_JSON))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--output-doc", default=str(DEFAULT_OUTPUT_DOC))
    return parser


def main() -> int:
    args = build_parser().parse_args()
    payload = build_payload(
        apk_type=read_json(Path(args.apk_type_json)),
        generated_batch=read_json(Path(args.generated_batch_json)),
        hidden_dex=read_json(Path(args.hidden_dex_json)),
        opcode_api=read_json(Path(args.opcode_api_json)),
        source_paths={
            "apk_type": args.apk_type_json,
            "generated_batch": args.generated_batch_json,
            "hidden_dex": args.hidden_dex_json,
            "opcode_api": args.opcode_api_json,
        },
    )

    output_json = Path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    output_doc = Path(args.output_doc)
    output_doc.parent.mkdir(parents=True, exist_ok=True)
    output_doc.write_text(build_markdown(payload), encoding="utf-8")

    print(
        json.dumps(
            {
                "doc": normalize_path(output_doc),
                "json": normalize_path(output_json),
                "selected_method": payload["decision"]["selected_method"],
                "next_tasks": len(payload["next_implementation_tasks"]),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def build_payload(
    *,
    apk_type: dict[str, Any],
    generated_batch: dict[str, Any],
    hidden_dex: dict[str, Any],
    opcode_api: dict[str, Any],
    source_paths: dict[str, str],
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "sources": {key: normalize_path(value) for key, value in source_paths.items()},
        "research_sources": SOURCE_NOTES,
        "current_project_evidence": {
            "generated_r8_batch": summarize_generated_batch(generated_batch),
            "apk_type_groups": summarize_apk_type_groups(apk_type),
            "hidden_dex_boundary": summarize_hidden_dex(hidden_dex),
            "opcode_api_policy": summarize_opcode_api(opcode_api),
        },
        "method_options": METHOD_OPTIONS,
        "decision": {
            "selected_method": "explainable multi-scale R8-aware evidence layer",
            "claim_policy": "R8-aware, not R8-proof. Exact version claims require strong surviving evidence; otherwise emit low confidence, ambiguity, or risk warnings.",
            "why": [
                "R8 changes names, reachability, class boundaries, call sites, and method bodies, so one feature family is not enough.",
                "The current project already has negative evidence for global opcode/API weighting.",
                "The strongest reusable ideas are explainable and incremental: LibHunter for inlining/call-site awareness, SAD for class summaries and field/literal features, ATVHunter and LibID/LibScan for opcode/basic-block/call-chain features, and LibMD for Bayesian multi-scale fusion.",
                "LibAttention is valuable evidence that learned representations help R8, but it is not the first integration choice for exact, auditable SBOM version claims.",
            ],
        },
        "integration_phases": INTEGRATION_PHASES,
        "next_implementation_tasks": NEXT_IMPLEMENTATION_TASKS,
    }


def summarize_generated_batch(payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = payload.get("evaluation_rows", [])
    counters: dict[str, Counter[str]] = {}
    totals: Counter[str] = Counter()
    for row in rows:
        category = str(row.get("category") or "unknown")
        if not category.startswith("r8"):
            continue
        counters.setdefault(category, Counter())
        counters[category]["expected"] += 1
        totals["expected"] += 1
        if row.get("component_detected"):
            counters[category]["component_detected"] += 1
            totals["component_detected"] += 1
        if row.get("version_detected"):
            counters[category]["version_detected"] += 1
            totals["version_detected"] += 1
        if row.get("candidate_version_correct"):
            counters[category]["candidate_version_correct"] += 1
            totals["candidate_version_correct"] += 1
        decision = str(row.get("candidate_decision") or "unknown")
        confidence = str(row.get("candidate_confidence") or "unknown")
        risk = str(row.get("obfuscation_risk_level") or "unknown")
        counters[category][f"decision:{decision}"] += 1
        counters[category][f"confidence:{confidence}"] += 1
        counters[category][f"risk:{risk}"] += 1
        totals[f"decision:{decision}"] += 1
        totals[f"confidence:{confidence}"] += 1
        totals[f"risk:{risk}"] += 1

    summary = []
    for category in sorted(counters):
        counter = counters[category]
        expected = counter["expected"]
        summary.append(
            {
                "category": category,
                "expected": expected,
                "component_detected": counter["component_detected"],
                "version_detected": counter["version_detected"],
                "candidate_version_correct": counter["candidate_version_correct"],
                "dominant_decision": most_common_prefixed_label(
                    counter, "decision", {"candidate", "exact", "likely"}
                ),
                "dominant_confidence": most_common_prefixed_label(
                    counter, "confidence", {"low", "medium", "high"}
                ),
                "dominant_risk": most_common_prefixed_label(
                    counter, "risk", {"low", "medium", "high"}
                ),
            }
        )
    if totals["expected"]:
        summary.append(
            {
                "category": "r8-total",
                "expected": totals["expected"],
                "component_detected": totals["component_detected"],
                "version_detected": totals["version_detected"],
                "candidate_version_correct": totals["candidate_version_correct"],
                "dominant_decision": most_common_prefixed_label(
                    totals, "decision", {"candidate", "exact", "likely"}
                ),
                "dominant_confidence": most_common_prefixed_label(
                    totals, "confidence", {"low", "medium", "high"}
                ),
                "dominant_risk": most_common_prefixed_label(
                    totals, "risk", {"low", "medium", "high"}
                ),
            }
        )
    return summary


def summarize_apk_type_groups(payload: dict[str, Any]) -> list[dict[str, str]]:
    wanted = {
        "controlled-r8-rename",
        "controlled-r8-shrink",
        "r8-minified-messaging-security",
        "native-heavy-hidden-code-limitations",
        "source-linked-blocked",
    }
    rows = []
    for group in payload.get("groups", []):
        group_id = str(group.get("group_id") or "")
        name = str(group.get("name") or "")
        if group_id in wanted or "R8" in name or "hidden" in name.lower():
            rows.append(
                {
                    "group_id": group_id,
                    "name": name,
                    "case_count": str(group.get("case_count") or ""),
                    "result_summary": str(group.get("result_summary") or ""),
                    "interpretation": str(group.get("interpretation") or ""),
                    "next_improvement": str(group.get("next_improvement") or ""),
                }
            )
    return rows


def summarize_hidden_dex(payload: dict[str, Any]) -> dict[str, Any]:
    summary = payload.get("summary", {})
    return {
        "verdict": payload.get("verdict", ""),
        "extraction_risk": summary.get("extraction_risk", ""),
        "obfuscation_risk": summary.get("obfuscation_risk", ""),
        "risk_indicator_codes": summary.get("risk_indicator_codes", []),
        "detected_maven_components": summary.get("detected_maven_components", 0),
        "native_file_components": summary.get("native_file_components", 0),
        "conclusion": payload.get("conclusion", ""),
    }


def summarize_opcode_api(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "conclusion": payload.get("conclusion", ""),
        "signals": [
            {
                "signal": signal.get("signal", ""),
                "decision": signal.get("decision", ""),
                "case_count": signal.get("case_count", 0),
                "improved_cases": signal.get("improved_cases", []),
                "regressed_cases": signal.get("regressed_cases", []),
            }
            for signal in payload.get("signals", [])
        ],
    }


def build_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# R8 Obfuscation Method Selection",
        "",
        "Generated by `scripts/build_r8_obfuscation_method_selection.py`.",
        "",
        "This artifact is the research gate for the final P4 R8/obfuscation con. It selects a method to integrate later, but it intentionally does not change matcher scoring. The policy is R8-aware, not R8-proof: exact version claims require strong surviving evidence; otherwise the tool should emit low confidence, ambiguity, or risk warnings.",
        "",
        "## Current Project Evidence",
        "",
        "### Generated R8 Category Batch",
        "",
        "| Category | Expected | Components detected | Versions detected | Candidate version correct | Decision | Confidence | Risk |",
        "|---|---:|---:|---:|---:|---|---|---|",
    ]
    for row in payload["current_project_evidence"]["generated_r8_batch"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    md(row["category"]),
                    str(row["expected"]),
                    str(row["component_detected"]),
                    str(row["version_detected"]),
                    str(row["candidate_version_correct"]),
                    md(row["dominant_decision"]),
                    md(row["dominant_confidence"]),
                    md(row.get("dominant_risk", "")),
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "### Relevant Evaluation Groups",
            "",
            "| Group | Cases | Result | Interpretation | Next improvement |",
            "|---|---:|---|---|---|",
        ]
    )
    for row in payload["current_project_evidence"]["apk_type_groups"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    md(row["name"] or row["group_id"]),
                    md(row["case_count"]),
                    md(row["result_summary"]),
                    md(row["interpretation"]),
                    md(row["next_improvement"]),
                ]
            )
            + " |"
        )

    hidden = payload["current_project_evidence"]["hidden_dex_boundary"]
    lines.extend(
        [
            "",
            "### Hidden/Protected Boundary",
            "",
            f"- Verdict: `{hidden['verdict']}`",
            f"- Extraction risk: `{hidden['extraction_risk']}`",
            f"- Obfuscation risk: `{hidden['obfuscation_risk']}`",
            "- Risk indicators: "
            + ", ".join(f"`{item}`" for item in hidden.get("risk_indicator_codes", [])),
            f"- Maven components emitted: `{hidden['detected_maven_components']}`",
            f"- Native file components emitted: `{hidden['native_file_components']}`",
            f"- Conclusion: {hidden['conclusion']}",
            "",
            "### Existing Signal Guardrail",
            "",
            payload["current_project_evidence"]["opcode_api_policy"].get("conclusion", ""),
            "",
            "| Signal | Decision | Cases | Improved | Regressed |",
            "|---|---|---:|---|---|",
        ]
    )
    for row in payload["current_project_evidence"]["opcode_api_policy"].get("signals", []):
        lines.append(
            "| "
            + " | ".join(
                [
                    md(row["signal"]),
                    md(row["decision"]),
                    str(row["case_count"]),
                    md(", ".join(row.get("improved_cases") or []) or "none"),
                    md(", ".join(row.get("regressed_cases") or []) or "none"),
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Paper And Tool Evidence",
            "",
            "| Source | Evidence | Design impact |",
            "|---|---|---|",
        ]
    )
    for row in payload["research_sources"]:
        lines.append(
            f"| [{md(row['source'])}]({row['url']}) | {md(row['evidence'])} | {md(row['design_impact'])} |"
        )

    lines.extend(
        [
            "",
            "## Method Options",
            "",
            "| Option | Papers/tools | Verdict | Reason | Reuse in this project |",
            "|---|---|---|---|---|",
        ]
    )
    for row in payload["method_options"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    md(row["option"]),
                    md(row["papers"]),
                    f"`{md(row['verdict'])}`",
                    md(row["reason"]),
                    md(row["reuse"]),
                ]
            )
            + " |"
        )

    decision = payload["decision"]
    lines.extend(
        [
            "",
            "## Selected Method",
            "",
            f"Selected method: `{decision['selected_method']}`.",
            "",
            f"Claim policy: {decision['claim_policy']}",
            "",
            "Why this is the safest integration path:",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in decision["why"])

    lines.extend(
        [
            "",
            "## Integration Phases",
            "",
            "| Phase | Name | Action | Promotion rule |",
            "|---:|---|---|---|",
        ]
    )
    for row in payload["integration_phases"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    md(row["phase"]),
                    md(row["name"]),
                    md(row["action"]),
                    md(row["promotion_rule"]),
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Next Implementation Tasks",
            "",
            "| Step | Task | Expected result |",
            "|---:|---|---|",
        ]
    )
    for index, row in enumerate(payload["next_implementation_tasks"], start=1):
        lines.append(f"| {index} | {md(row['task'])} | {md(row['result'])} |")

    lines.extend(
        [
            "",
            "## Decision Summary",
            "",
            "- Complete now: research method selection, scoring-unchanged diagnostics, Phase 1 report-only classifier fields, Phase 2 controlled R8 matrix expansion, Phase 3 inert feature extraction, the expanded Phase 4 layered multi-scale diagnostic, the Phase 5 scoped trigger diagnostic, and Phase 5 current-control validation.",
            "- Do next: keep the Phase 4 global blend rejected and the opt-in Phase 5 command experiment-only unless a production scorer is separately justified and verified.",
            "- Do not do yet: global opcode/API weighting, global multi-scale scoring, exact-version claims under heavy R8, or ML-first implementation.",
            "- Con status: Phases 1-5 have diagnostic artifacts; default matcher scoring and SBOM selection remain unchanged.",
            "",
        ]
    )
    return "\n".join(lines)


def most_common_label(counter: Counter[str], labels: set[str]) -> str:
    candidates = [(label, counter[label]) for label in labels if counter[label]]
    if not candidates:
        return "unknown"
    return max(candidates, key=lambda item: item[1])[0]


def most_common_prefixed_label(counter: Counter[str], prefix: str, labels: set[str]) -> str:
    candidates = [
        (label, counter[f"{prefix}:{label}"])
        for label in labels
        if counter[f"{prefix}:{label}"]
    ]
    if not candidates:
        return "unknown"
    return max(candidates, key=lambda item: item[1])[0]


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_path(path: Any) -> str:
    return str(path).replace("\\", "/") if path else ""


def md(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


if __name__ == "__main__":
    raise SystemExit(main())
