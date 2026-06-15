from __future__ import annotations

from apk_sbom.cli import build_parser
from apk_sbom.matcher import COMPOSITE_FAMILY_SHORTLIST_MARGIN


def test_version_unique_literal_context_reranker_cli_defaults_enabled() -> None:
    parser = build_parser()

    for command in ("match-apk", "generate-sbom", "generate-report"):
        args = parser.parse_args([command, "sample.apk"])

        assert args.enable_version_unique_literal_context_reranker is True


def test_version_unique_literal_context_reranker_cli_can_be_disabled() -> None:
    parser = build_parser()

    for command in ("match-apk", "generate-sbom", "generate-report"):
        args = parser.parse_args(
            [
                command,
                "sample.apk",
                "--disable-version-unique-literal-context-reranker",
            ]
        )

        assert args.enable_version_unique_literal_context_reranker is False


def test_composite_family_shortlist_cli_defaults_enabled() -> None:
    parser = build_parser()

    for command in ("match-apk", "generate-sbom", "generate-report"):
        args = parser.parse_args([command, "sample.apk"])

        assert args.enable_composite_family_shortlist is True
        assert args.composite_family_shortlist_margin == COMPOSITE_FAMILY_SHORTLIST_MARGIN


def test_composite_family_shortlist_cli_can_be_disabled() -> None:
    parser = build_parser()

    for command in ("match-apk", "generate-sbom", "generate-report"):
        args = parser.parse_args(
            [
                command,
                "sample.apk",
                "--disable-composite-family-shortlist",
            ]
        )

        assert args.enable_composite_family_shortlist is False


def test_composite_family_shortlist_cli_enable_alias_sets_margin() -> None:
    parser = build_parser()

    for command in ("match-apk", "generate-sbom", "generate-report"):
        args = parser.parse_args(
            [
                command,
                "sample.apk",
                "--enable-composite-family-shortlist-experiment",
                "--composite-family-shortlist-margin",
                "0.2",
            ]
        )

        assert args.enable_composite_family_shortlist is True
        assert args.composite_family_shortlist_margin == 0.2
