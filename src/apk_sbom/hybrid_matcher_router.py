from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


DEFAULT_MATCHER_RECALL_JSON = Path(
    "data/results/evaluation/demo-final-v2-matcher-recall-diagnostics.json"
)
DEFAULT_TRANSPARENCY_JSON = Path(
    "data/results/evaluation/demo-final-transparency-export.json"
)
DEFAULT_SOURCE_GAP_JSON = Path(
    "data/results/evaluation/demo-final-large-v2-source-gap-triage.json"
)
DEFAULT_WRONG_VERSION_JSON = Path(
    "data/results/evaluation/wrong-version-optimization-dashboard.json"
)
DEFAULT_AI_SUGGESTIONS_JSON = Path(
    "data/results/experiments/ai-r8-assistant/suggestions.json"
)
DEFAULT_OUTPUT_JSON = Path("data/results/evaluation/hybrid-matcher-router-v1.json")
DEFAULT_OUTPUT_DOC = Path("docs/evaluation/HYBRID_MATCHER_ROUTER_V1.md")


ALLOWED_EFFECTS = [
    "matcher experiment prioritization",
    "report-only strategy explanation",
    "future control-matrix planning",
]
FORBIDDEN_EFFECTS = [
    "selected version change",
    "CycloneDX SBOM component change",
    "vulnerability label change",
    "source-validation metric change",
    "default matcher scoring change",
]


STRATEGY_CATALOG: dict[str, dict[str, Any]] = {
    "baseline-weighted-evidence": {
        "label": "Current weighted multi-evidence matcher",
        "research_basis": "LibScout-style profile matching plus local SBOM confidence design",
        "when_to_use": "Clean or high-evidence rows where package/class/method/literal evidence is coherent.",
        "pros": "Fast, explainable, already regression-tested, produces SBOM-ready confidence labels.",
        "cons": "Global weights struggle with R8 shrink/inline and adjacent version-band ties.",
        "promotion_gate": "Already default; keep as control baseline for every experiment.",
    },
    "coarse-to-fine-recall": {
        "label": "Coarse-to-fine matcher recall",
        "research_basis": "LibHunter/LibScan coarse-to-fine filtering",
        "when_to_use": "Source coordinate exists in the DB but was not emitted, or matcher score is below threshold.",
        "pros": "Can increase recall without comparing every component against every reference row.",
        "cons": "A bad coarse filter can hide true libraries; must preserve full-family rescue checks.",
        "promotion_gate": "Must improve matcher-recall rows without new clean/partial/boundary regressions.",
    },
    "r8-structural-recall": {
        "label": "R8 structural recall profile",
        "research_basis": "LibAttention, LibHunter, LibMD multi-scale and learned-code evidence",
        "when_to_use": "Opcode/dependency evidence is strong while package/class/method evidence is weak.",
        "pros": "Targets rename, shrink, inlining, and class-merging symptoms.",
        "cons": "Global structural weights already caused regressions; use only scoped controls.",
        "promotion_gate": "Controlled R8, clean-real, partial-real, boundary, and no-Maven controls must all stay clean.",
    },
    "version-band-rerank": {
        "label": "Version-band rerank profile",
        "research_basis": "SAD/LibPecker class-structural similarity and local version-unique evidence",
        "when_to_use": "AndroidX/Kotlin/nearby-version rows with tiny score gaps or source-known version drift.",
        "pros": "Directly targets wrong-version and near-tie rows.",
        "cons": "Generic newer/older tie rules already regressed controls; must stay per-coordinate or per-family.",
        "promotion_gate": "Target fixes plus zero selected-version/source-validation regressions in current controls.",
    },
    "metadata-coherence-rerank": {
        "label": "Metadata/POM coherence rerank profile",
        "research_basis": "LibMD-style probabilistic SBOM evidence plus Maven dependency coherence",
        "when_to_use": "Candidate versions differ mainly by dependency-era/POM support.",
        "pros": "Useful for AndroidX/Kotlin/Compose families where bytecode is nearly equivalent.",
        "cons": "Unsafe if POM metadata is used alone; requires independently detected supporting coordinates.",
        "promotion_gate": "Only activate when independent APK-side support confirms the candidate family/era.",
    },
    "reference-growth-first": {
        "label": "Reference DB growth first",
        "research_basis": "LibScout/LibD reference-profile completeness requirement",
        "when_to_use": "The source coordinate/version is not represented by bytecode-bearing reference features.",
        "pros": "Fixes denominator honesty before tuning the matcher.",
        "cons": "Does not solve matcher recall by itself and can enlarge the candidate search space.",
        "promotion_gate": "Recovered artifacts must be bytecode-bearing and evaluated before shared DB promotion.",
    },
    "alias-boundary-map": {
        "label": "Alias/family boundary mapping",
        "research_basis": "LibMD-style SBOM normalization and artifact-family handling",
        "when_to_use": "Public/source coordinates map to Android target, KMP, sibling, or relocated bytecode artifacts.",
        "pros": "Improves transparency without pretending source-only aliases are direct APK bytecode.",
        "cons": "Can become misleading if aliases are counted as exact emitted components.",
        "promotion_gate": "Report mapping only until alias pairs are validated as bytecode-equivalent.",
    },
    "boundary-hash-only": {
        "label": "Boundary/hash-only reporting",
        "research_basis": "SBOM honesty for native/framework/protected/source-only payloads",
        "when_to_use": "No APK bytecode is expected or static Maven versioning is not supported.",
        "pros": "Prevents false precision and keeps limitations visible.",
        "cons": "Does not increase Maven recall or exact-version accuracy.",
        "promotion_gate": "Never promote to exact Maven version without bytecode evidence.",
    },
    "vulnerability-focused-review": {
        "label": "Vulnerability-focused review",
        "research_basis": "ATVHunter-style vulnerability-oriented prioritization",
        "when_to_use": "Rows involve CVE-sensitive ecosystems such as JSON, networking, crypto, XML, or logging.",
        "pros": "Helps prioritize security-relevant uncertain rows.",
        "cons": "Not a complete SBOM strategy and must not inflate CVE counts.",
        "promotion_gate": "Can affect review priority only; CVE labels still require SBOM/source-validation evidence.",
    },
    "ai-report-only-triage": {
        "label": "AI-assisted report-only triage",
        "research_basis": "Phase 6A RandomForest and Phase 6B Transformer prototype",
        "when_to_use": "Hard R8/matcher-recall rows need prioritization or wording decisions.",
        "pros": "Uses learned patterns from current evidence while preserving SBOM honesty.",
        "cons": "Trained on project diagnostics, not independent ground truth for all APKs.",
        "promotion_gate": "AI can recommend triage/wording only; it cannot emit confirmed versions.",
    },
}


TOOL_COMPARISON: list[dict[str, str]] = [
    {
        "tool_family": "LibScout-style",
        "method": "Library profiles and structural hashes",
        "pros": "Precise and explainable on clean known libraries.",
        "cons": "Brittle under shrink, method inlining, and removed code.",
        "router_adoption": "Keep as baseline-weighted evidence and reference-profile completeness gate.",
    },
    {
        "tool_family": "LibRadar/LibD-style",
        "method": "Package-independent clustering and opcode/graph-like similarity",
        "pros": "More robust to simple obfuscation and scalable for identity.",
        "cons": "Weak exact-version authority; nearby versions can collapse.",
        "router_adoption": "Use for coarse-to-fine recall, not final exact-version claims.",
    },
    {
        "tool_family": "LibPecker/SAD-style",
        "method": "Class structural similarity and version-level comparison",
        "pros": "Better aligned with exact-version recovery than package names alone.",
        "cons": "Adjacent AndroidX/Kotlin versions and R8 shrink remain risky.",
        "router_adoption": "Use for scoped version-band rerank experiments.",
    },
    {
        "tool_family": "ORLIS-style",
        "method": "CFG/fuzzy hashing and control-flow similarity",
        "pros": "Survives renaming and some structural edits.",
        "cons": "Heavier and can false-match similar code.",
        "router_adoption": "Candidate for future R8 structural profile controls.",
    },
    {
        "tool_family": "LibHunter/LibScan-style",
        "method": "Coarse-to-fine detection pipeline",
        "pros": "Controls runtime and avoids broad expensive search.",
        "cons": "First-stage filter mistakes can hide true positives.",
        "router_adoption": "Use for matcher-recall and large-DB pruning profiles.",
    },
    {
        "tool_family": "ATVHunter-style",
        "method": "Vulnerability-oriented matching",
        "pros": "Good for prioritizing security-relevant uncertain rows.",
        "cons": "Not a complete SBOM or dependency recall method.",
        "router_adoption": "Use for review priority only, not vulnerability labels.",
    },
    {
        "tool_family": "LibAttention-style",
        "method": "Learned code representations for obfuscation robustness",
        "pros": "Promising for R8 identity-risk classification.",
        "cons": "Needs larger independent corpus and is not exact Maven version authority.",
        "router_adoption": "Use as AI report-only triage and future raw-code DL research.",
    },
    {
        "tool_family": "LibMD-style",
        "method": "Multi-scale SBOM/CVE fusion with confidence",
        "pros": "Closest to the project goal: SBOM plus vulnerability-aware evidence.",
        "cons": "Complex calibration and strict regression gates are required.",
        "router_adoption": "Use as the long-term hybrid fusion direction.",
    },
]


ANDROIDX_OR_KOTLIN_PREFIXES = (
    "androidx.",
    "androidx:",
    "org.jetbrains.kotlin",
    "org.jetbrains.kotlinx",
    "com.google.android.material",
)
VULNERABILITY_SENSITIVE_HINTS = (
    "gson",
    "jackson",
    "okhttp",
    "retrofit",
    "bouncycastle",
    "commons-codec",
    "xml",
    "log4j",
    "netty",
    "crypto",
)


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
        "json": str(json_path),
        "doc": str(doc_path),
        "router_rows": payload["summary"]["router_rows"],
        "top_profile": payload["summary"]["top_recommended_profiles"][0]
        if payload["summary"]["top_recommended_profiles"]
        else None,
    }


def build_payload(
    *,
    matcher_recall_json: str | Path = DEFAULT_MATCHER_RECALL_JSON,
    transparency_json: str | Path = DEFAULT_TRANSPARENCY_JSON,
    source_gap_json: str | Path = DEFAULT_SOURCE_GAP_JSON,
    wrong_version_json: str | Path = DEFAULT_WRONG_VERSION_JSON,
    ai_suggestions_json: str | Path = DEFAULT_AI_SUGGESTIONS_JSON,
) -> dict[str, Any]:
    matcher_recall = _load_json(matcher_recall_json)
    transparency = _load_json(transparency_json)
    source_gap = _load_json(source_gap_json)
    wrong_version = _load_json(wrong_version_json)
    ai_suggestions = _load_json(ai_suggestions_json)
    case_index = {
        str(row.get("case_id") or ""): row
        for row in transparency.get("dataset_cases", [])
        if row.get("case_id")
    }
    ai_index = _build_ai_index(ai_suggestions.get("suggestions", []))

    router_rows: list[dict[str, Any]] = []
    for index, row in enumerate(matcher_recall.get("rows", [])):
        router_rows.append(
            route_matcher_recall_row(
                row,
                index=index,
                case_meta=case_index.get(str(row.get("case_id") or ""), {}),
                ai_suggestion=ai_index.get(_row_key(row)),
            )
        )
    for index, row in enumerate(source_gap.get("rows", [])):
        router_rows.append(
            route_source_gap_row(
                row,
                index=index,
                case_meta=case_index.get(str(row.get("case_id") or ""), {}),
            )
        )
    for index, row in enumerate(wrong_version.get("top_selected_to_source_pairs", [])):
        router_rows.append(route_wrong_version_pair(row, index=index))
    for index, row in enumerate(wrong_version.get("top_coordinates", [])):
        router_rows.append(route_wrong_version_coordinate(row, index=index))

    summary = summarize_rows(router_rows, ai_suggestions)
    return {
        "schema_version": "hybrid-matcher-router-v1",
        "report_only": True,
        "default_matcher_unchanged": True,
        "policy": [
            "This router is an experiment planner, not matcher scoring.",
            "No router recommendation changes selected versions, SBOM components, vulnerability labels, or source-validation metrics.",
            "Any future promotion must pass controlled, clean-real, partial-real, no-Maven, boundary, and CVE-sensitive controls.",
            "AI recommendations may influence triage priority and wording only.",
        ],
        "sources": {
            "matcher_recall_json": str(matcher_recall_json),
            "transparency_json": str(transparency_json),
            "source_gap_json": str(source_gap_json),
            "wrong_version_json": str(wrong_version_json),
            "ai_suggestions_json": str(ai_suggestions_json),
        },
        "current_matcher": {
            "summary": "Weighted explainable matcher using package, class, method, opcode, dependency, literal, version-unique, optional API, and optional opcode-ngram evidence.",
            "default_safe_boundary": "Current matcher remains the SBOM authority until a scoped strategy passes controls.",
            "known_gap": "Fixed global weights are less effective for mixed APK conditions such as R8 shrink/inline, version-band ties, alias boundaries, and missing reference rows.",
        },
        "tool_strategy_comparison": TOOL_COMPARISON,
        "strategy_catalog": STRATEGY_CATALOG,
        "summary": summary,
        "rows": router_rows,
    }


def route_matcher_recall_row(
    row: dict[str, Any],
    *,
    index: int,
    case_meta: dict[str, Any],
    ai_suggestion: dict[str, Any] | None,
) -> dict[str, Any]:
    coordinate = str(row.get("coordinate") or "")
    reasons: list[str] = ["source-coordinate-exists-but-not-emitted"]
    secondary: list[str] = []
    profile = "coarse-to-fine-recall"
    priority = "P2"
    next_action = str(row.get("next_action") or "")
    recall_status = str(row.get("recall_status") or "")
    opcode_score = _float(row.get("opcode_score"))
    class_score = _float(row.get("class_score"))
    method_score = _float(row.get("method_score"))
    has_score_gap = row.get("score_gap_to_best") not in (None, "")
    score_gap = _float(row.get("score_gap_to_best"))
    identity = _float(row.get("identity_confidence"))
    r8_profile = str(case_meta.get("r8_obfuscation_profile") or "").lower()
    is_r8 = "r8" in r8_profile or "minified" in r8_profile
    is_boundary = False

    if recall_status == "no-bytecode-signal":
        profile = "boundary-hash-only"
        priority = "P3"
        is_boundary = True
        reasons.append("no-bytecode-signal")
    elif next_action == "surface-as-source-context-report-only-suggestion":
        profile = "coarse-to-fine-recall"
        priority = "P1"
        reasons.append("source-context-report-only-suggestion")
    elif recall_status == "below-threshold":
        profile = "coarse-to-fine-recall"
        reasons.append("below-current-threshold")
    elif "suppressed" in recall_status:
        profile = "ai-report-only-triage"
        reasons.append("suppressed-uncertain")

    if (
        not is_boundary
        and has_score_gap
        and _is_version_band_coordinate(coordinate)
        and score_gap <= 0.006
    ):
        profile = "version-band-rerank"
        reasons.append("version-band-or-adjacent-version-family")
        secondary.append("metadata-coherence-rerank")
        priority = "P1" if priority == "P2" else priority
    if not is_boundary and opcode_score >= 0.75 and max(class_score, method_score) < 0.30:
        profile = "r8-structural-recall"
        reasons.append("strong-opcode-weak-class-method-signal")
        if is_r8:
            reasons.append("case-has-r8-or-minified-profile")
        secondary.append("ai-report-only-triage")
    if _is_vulnerability_sensitive(coordinate):
        secondary.append("vulnerability-focused-review")
    if ai_suggestion:
        reasons.append(f"ai-{ai_suggestion.get('recommendation')}")
        if ai_suggestion.get("recommendation") == "risk_only":
            secondary.append("ai-report-only-triage")
    if identity and identity < 0.35:
        reasons.append("low-identity-confidence")

    return _router_row(
        row_id=f"matcher-recall:{index}:{row.get('case_id')}:{coordinate}:{row.get('source_version')}",
        row_source="matcher-recall",
        case_id=row.get("case_id"),
        app=row.get("app") or case_meta.get("name"),
        coordinate=coordinate,
        source_version=row.get("source_version"),
        candidate_version=row.get("best_version"),
        recommended_profile=profile,
        secondary_profiles=secondary,
        priority=priority,
        reason_codes=reasons,
        evidence={
            "best_score": row.get("best_score"),
            "source_score": row.get("source_score"),
            "score_gap_to_best": row.get("score_gap_to_best"),
            "identity_confidence": row.get("identity_confidence"),
            "package_score": row.get("package_score"),
            "class_score": row.get("class_score"),
            "method_score": row.get("method_score"),
            "opcode_score": row.get("opcode_score"),
            "literal_score": row.get("literal_score"),
            "dependency_score": row.get("dependency_score"),
            "recall_status": recall_status,
            "next_action": next_action,
            "r8_obfuscation_profile": case_meta.get("r8_obfuscation_profile"),
            "ai_recommendation": ai_suggestion.get("recommendation")
            if ai_suggestion
            else None,
        },
    )


def route_source_gap_row(
    row: dict[str, Any],
    *,
    index: int,
    case_meta: dict[str, Any],
) -> dict[str, Any]:
    coordinate = str(row.get("coordinate") or "")
    next_action = str(row.get("next_action") or "")
    triage_bucket = str(row.get("triage_bucket") or "")
    reasons = [next_action or triage_bucket or "source-gap-row"]
    priority = "P2"
    secondary: list[str] = []
    if next_action == "add-or-retry-reference-version-if-bytecode-bearing":
        profile = "reference-growth-first"
        priority = "P1"
    elif next_action == "investigate-matcher-threshold-or-feature-recall":
        profile = "version-band-rerank" if _is_version_band_coordinate(coordinate) else "coarse-to-fine-recall"
        priority = "P1"
        if profile == "version-band-rerank":
            secondary.append("metadata-coherence-rerank")
    elif next_action.startswith("map-"):
        profile = "alias-boundary-map"
    elif next_action.startswith("document-"):
        profile = "boundary-hash-only"
        priority = "P3"
    else:
        profile = "coarse-to-fine-recall"
    if _is_vulnerability_sensitive(coordinate):
        secondary.append("vulnerability-focused-review")

    return _router_row(
        row_id=f"source-gap:{index}:{row.get('case_id')}:{coordinate}:{row.get('source_version')}",
        row_source="source-gap",
        case_id=row.get("case_id"),
        app=row.get("app") or case_meta.get("name"),
        coordinate=coordinate,
        source_version=row.get("source_version"),
        candidate_version=row.get("matcher_best_version"),
        recommended_profile=profile,
        secondary_profiles=secondary,
        priority=priority,
        reason_codes=reasons,
        evidence={
            "classification": row.get("classification"),
            "triage_bucket": row.get("triage_bucket"),
            "exact_source_version_in_large_db": row.get("exact_source_version_in_large_db"),
            "reference_versions": row.get("reference_versions"),
            "matcher_best_score": row.get("matcher_best_score"),
            "matcher_source_score": row.get("matcher_source_score"),
            "r8_obfuscation_profile": case_meta.get("r8_obfuscation_profile"),
        },
    )


def route_wrong_version_pair(row: dict[str, Any], *, index: int) -> dict[str, Any]:
    coordinate = str(row.get("coordinate") or "")
    profile = "version-band-rerank"
    secondary = ["metadata-coherence-rerank"]
    if _is_vulnerability_sensitive(coordinate):
        secondary.append("vulnerability-focused-review")
    return _router_row(
        row_id=f"wrong-version-pair:{index}:{coordinate}:{row.get('tool_selected_version')}:{row.get('source_version')}",
        row_source="wrong-version-pair",
        case_id=None,
        app=None,
        coordinate=coordinate,
        source_version=row.get("source_version"),
        candidate_version=row.get("tool_selected_version"),
        recommended_profile=profile,
        secondary_profiles=secondary,
        priority="P1" if _is_version_band_coordinate(coordinate) else "P2",
        reason_codes=[
            str(row.get("relation") or "wrong-version-drift"),
            "source-present-identity-row",
        ],
        evidence={
            "rows": row.get("rows"),
            "unique_cases": row.get("unique_cases"),
            "safe_next_action": row.get("safe_next_action"),
        },
    )


def route_wrong_version_coordinate(row: dict[str, Any], *, index: int) -> dict[str, Any]:
    coordinate = str(row.get("coordinate") or "")
    profile = "version-band-rerank" if _is_version_band_coordinate(coordinate) else "metadata-coherence-rerank"
    secondary = ["coarse-to-fine-recall"]
    if _is_vulnerability_sensitive(coordinate):
        secondary.append("vulnerability-focused-review")
    return _router_row(
        row_id=f"wrong-version-coordinate:{index}:{coordinate}",
        row_source="wrong-version-coordinate",
        case_id=None,
        app=None,
        coordinate=coordinate,
        source_version=None,
        candidate_version=None,
        recommended_profile=profile,
        secondary_profiles=secondary,
        priority=str(row.get("priority") or "P2"),
        reason_codes=[
            str(row.get("dominant_relation") or "wrong-version-family"),
            str(row.get("family") or "unknown-family"),
        ],
        evidence={
            "rows": row.get("rows"),
            "unique_cases": row.get("unique_cases"),
            "safe_next_action": row.get("safe_next_action"),
        },
    )


def summarize_rows(
    rows: list[dict[str, Any]],
    ai_suggestions: dict[str, Any],
) -> dict[str, Any]:
    profile_counts = Counter(row["recommended_profile"] for row in rows)
    row_source_counts = Counter(row["row_source"] for row in rows)
    priority_counts = Counter(row["priority"] for row in rows)
    case_counts = Counter(row["case_id"] for row in rows if row.get("case_id"))
    coordinate_counts = Counter(row["coordinate"] for row in rows if row.get("coordinate"))
    return {
        "router_rows": len(rows),
        "unique_cases": len(case_counts),
        "unique_coordinates": len(coordinate_counts),
        "profile_counts": dict(sorted(profile_counts.items())),
        "row_source_counts": dict(sorted(row_source_counts.items())),
        "priority_counts": dict(sorted(priority_counts.items())),
        "ai_recommendation_counts": ai_suggestions.get("summary", {}).get(
            "recommendation_counts", {}
        ),
        "top_recommended_profiles": _top_counts(profile_counts, limit=10),
        "top_cases": _top_counts(case_counts, limit=10),
        "top_coordinates": _top_counts(coordinate_counts, limit=15),
    }


def build_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Hybrid Matcher Router V1",
        "",
        "Generated by `apk-sbom hybrid-matcher-router` or `scripts/build_hybrid_matcher_router.py`.",
        "",
        "This is a report-only matcher-improvement planner. It compares the current matcher with tool-family strategies from the literature, routes current hard rows to scoped experimental profiles, and keeps default matcher/SBOM/CVE behavior unchanged.",
        "",
        "## Guardrails",
        "",
    ]
    for item in payload["policy"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## Current Matcher",
            "",
            f"- {payload['current_matcher']['summary']}",
            f"- Safe boundary: {payload['current_matcher']['default_safe_boundary']}",
            f"- Known gap: {payload['current_matcher']['known_gap']}",
            "",
            "## Tool Strategy Comparison",
            "",
            "| Tool family | Method | Pros | Cons | Router adoption |",
            "|---|---|---|---|---|",
        ]
    )
    for row in payload["tool_strategy_comparison"]:
        lines.append(
            f"| {row['tool_family']} | {row['method']} | {row['pros']} | {row['cons']} | {row['router_adoption']} |"
        )
    lines.extend(
        [
            "",
            "## Router Summary",
            "",
            f"- Router rows: `{summary['router_rows']}`",
            f"- Unique cases: `{summary['unique_cases']}`",
            f"- Unique coordinates: `{summary['unique_coordinates']}`",
            f"- Priority counts: `{json.dumps(summary['priority_counts'], sort_keys=True)}`",
            "",
            "### Recommended Profiles",
            "",
            "| Profile | Rows |",
            "|---|---:|",
        ]
    )
    for row in summary["top_recommended_profiles"]:
        lines.append(f"| `{row['key']}` | {row['rows']} |")
    lines.extend(
        [
            "",
            "### Row Sources",
            "",
            "| Source | Rows |",
            "|---|---:|",
        ]
    )
    for source, count in sorted(summary["row_source_counts"].items()):
        lines.append(f"| `{source}` | {count} |")
    lines.extend(
        [
            "",
            "### Top Cases",
            "",
            "| Case | Rows |",
            "|---|---:|",
        ]
    )
    for row in summary["top_cases"]:
        lines.append(f"| `{row['key']}` | {row['rows']} |")
    lines.extend(
        [
            "",
            "### Top Coordinates",
            "",
            "| Coordinate | Rows |",
            "|---|---:|",
        ]
    )
    for row in summary["top_coordinates"]:
        lines.append(f"| `{row['key']}` | {row['rows']} |")
    lines.extend(
        [
            "",
            "## Strategy Catalog",
            "",
            "| Profile | Best use | Research basis | Main risk | Promotion gate |",
            "|---|---|---|---|---|",
        ]
    )
    for key, row in payload["strategy_catalog"].items():
        lines.append(
            f"| `{key}` | {row['when_to_use']} | {row['research_basis']} | {row['cons']} | {row['promotion_gate']} |"
        )
    lines.extend(
        [
            "",
            "## Recommended Hybrid Path",
            "",
            "1. Keep the current weighted matcher as the control baseline.",
            "2. Use this router to select a scoped experiment profile per hard row family.",
            "3. Let AI recommend triage/priority, but keep deterministic promotion gates.",
            "4. Promote only a narrow profile that improves target rows and passes controlled, clean-real, partial-real, no-Maven, boundary, and CVE-sensitive controls.",
            "",
            "## Source Artifacts",
            "",
        ]
    )
    for key, value in sorted(payload["sources"].items()):
        lines.append(f"- `{key}`: `{value}`")
    lines.append("")
    return "\n".join(lines)


def _router_row(
    *,
    row_id: str,
    row_source: str,
    case_id: Any,
    app: Any,
    coordinate: str,
    source_version: Any,
    candidate_version: Any,
    recommended_profile: str,
    secondary_profiles: list[str],
    priority: str,
    reason_codes: list[str],
    evidence: dict[str, Any],
) -> dict[str, Any]:
    return {
        "row_id": row_id,
        "row_source": row_source,
        "case_id": case_id,
        "app": app,
        "coordinate": coordinate,
        "source_version": source_version,
        "candidate_version": candidate_version,
        "recommended_profile": recommended_profile,
        "secondary_profiles": sorted(set(secondary_profiles)),
        "priority": priority,
        "reason_codes": sorted(set(reason_codes)),
        "evidence": evidence,
        "allowed_effects": ALLOWED_EFFECTS,
        "forbidden_effects": FORBIDDEN_EFFECTS,
        "promotion_gate": STRATEGY_CATALOG[recommended_profile]["promotion_gate"],
        "report_only": True,
    }


def _build_ai_index(rows: list[dict[str, Any]]) -> dict[tuple[str, str, str], dict[str, Any]]:
    index = {}
    for row in rows:
        index[_row_key(row)] = row
    return index


def _row_key(row: dict[str, Any]) -> tuple[str, str, str]:
    return (
        str(row.get("case_id") or ""),
        str(row.get("coordinate") or ""),
        str(row.get("source_version") or ""),
    )


def _top_counts(counter: Counter, *, limit: int) -> list[dict[str, Any]]:
    return [
        {"key": str(key), "rows": count}
        for key, count in counter.most_common(limit)
    ]


def _is_version_band_coordinate(coordinate: str) -> bool:
    return coordinate.startswith(ANDROIDX_OR_KOTLIN_PREFIXES)


def _is_vulnerability_sensitive(coordinate: str) -> bool:
    lowered = coordinate.lower()
    return any(hint in lowered for hint in VULNERABILITY_SENSITIVE_HINTS)


def _float(value: Any) -> float:
    try:
        if value in (None, ""):
            return 0.0
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _load_json(path: str | Path) -> dict[str, Any]:
    source = Path(path)
    if not source.exists():
        return {}
    return json.loads(source.read_text(encoding="utf-8"))
