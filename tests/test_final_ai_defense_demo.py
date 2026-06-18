from __future__ import annotations

from scripts.run_final_ai_defense_demo import build_markdown, build_payload


def test_final_ai_defense_demo_requires_all_guardrails():
    payload = build_payload(
        smoke={
            "summary": {
                "all_outputs_unchanged": True,
                "all_hybrid_sections_visible": True,
            },
            "targets": [
                _target("fdroid", 23),
                _target("aegis-authenticator", 7),
            ],
        },
        gate={
            "mvp_integration": {
                "report_only_ready": True,
                "matcher_authority_ready": False,
                "current_integration_level": "production-report-only-ai-assistance",
            },
            "model_decisions": {
                "matcher_or_sbom_authority": {
                    "decision": "blocked-keep-deterministic-matcher-authority"
                }
            },
            "model_evidence": {},
        },
        vulnerable_report={
            "apk": {"apk_path": "fixture.apk"},
            "detected_components": [{"coordinate": "jackson-databind"}],
            "osv": {
                "confirmed_vulnerabilities": 3,
                "severity_counts": {"HIGH": 3},
                "results": [
                    {
                        "vulnerabilities": [
                            {"aliases": ["CVE-2020-36518"]},
                            {"aliases": ["CVE-2022-42003"]},
                            {"aliases": ["CVE-2022-42004"]},
                        ]
                    }
                ],
            },
        },
    )

    assert payload["verdict"]["defense_demo_ready"] is True
    assert payload["verdict"]["checks_passed"] == 10
    assert payload["checks"]["matcher_authority_blocked"] is True
    assert "Defense demo ready: `true`" in build_markdown(payload)


def test_final_ai_defense_demo_fails_when_ai_changes_outputs():
    fdroid = _target("fdroid", 23)
    fdroid["comparison"]["unchanged"] = False
    payload = build_payload(
        smoke={
            "summary": {
                "all_outputs_unchanged": False,
                "all_hybrid_sections_visible": True,
            },
            "targets": [fdroid, _target("aegis-authenticator", 7)],
        },
        gate={
            "mvp_integration": {
                "report_only_ready": True,
                "matcher_authority_ready": False,
            },
            "model_decisions": {
                "matcher_or_sbom_authority": {
                    "decision": "blocked-keep-deterministic-matcher-authority"
                }
            },
        },
        vulnerable_report={
            "detected_components": [{}],
            "osv": {
                "confirmed_vulnerabilities": 3,
                "results": [
                    {
                        "vulnerabilities": [
                            {"aliases": ["CVE-1", "CVE-2", "CVE-3"]}
                        ]
                    }
                ],
            },
        },
    )

    assert payload["verdict"]["defense_demo_ready"] is False
    assert payload["checks"]["default_vs_ai_outputs_unchanged"] is False


def _target(case_id: str, components: int) -> dict:
    return {
        "case_id": case_id,
        "label": case_id,
        "apk_path": f"{case_id}.apk",
        "hybrid_section_visible": True,
        "hybrid_section_report_only": True,
        "hybrid_section_summary": {
            "router_matching_rows": 4,
            "ml_matching_rows": 3,
            "structural_gate_promotion_candidates": 0,
        },
        "comparison": {
            "default_component_count": components,
            "unchanged": True,
        },
    }
