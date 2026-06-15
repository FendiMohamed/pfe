# Final Demo Checklist

Use this as the fast day-of-defense checklist. It points to already-generated artifacts; do not rerun the long 106-APK evaluation live.

## Open First

| Order | Artifact | Purpose |
|---:|---|---|
| 1 | `outputs/manual-20260526-apk-sbom-deck/presentations/apk-sbom-defense/output/apk-sbom-defense-deck.pptx` | Current editable defense deck with the final v2 story. |
| 2 | `docs/evaluation/FINAL_DEMO_RUNBOOK_V2.md` | Exact opening wording, file order, and hard-question answers. |
| 3 | `docs/evaluation/DEMO_FINAL_V2_PACKAGE.md` | Current v2 package index and headline numbers. |
| 4 | `docs/thesis/FINAL_V2_RESULTS_SECTION.md` | Thesis-ready wording that separates normal metrics from the v2 upper-bound lane. |
| 5 | `docs/evaluation/DEMO_FINAL_TRANSPARENCY_REPORT.md` | Row-level dataset/source/emitted/vulnerability classification summary. |

## Live Demo Artifacts

| Demo moment | Open |
|---|---|
| Clean APK-to-SBOM report | `data/results/report-real-f-droid-final-demo-osv/report.html` |
| Clean CycloneDX SBOM | `data/results/report-real-f-droid-final-demo-osv/sbom.cdx.json` |
| Clean source validation | `data/results/source-validation/fdroid-final-demo-osv/source-validation.md` |
| Positive CVE report | `data/results/demo-osv-vulnerable-jackson-databind/report.html` |
| Positive CVE OSV JSON | `data/results/demo-osv-vulnerable-jackson-databind/osv-vulnerabilities.json` |
| Real APK CVE triage policy | `docs/evaluation/OSV_SOURCE_VALIDATION_TRIAGE.md` |
| Graduation rehearsal pack | `docs/evaluation/GRADUATION_DEMO_REHEARSAL.md` |

## Numbers To Say

| Claim | Number |
|---|---:|
| Controlled fixtures | 84 / 84 expected Maven versions |
| Normal source-validated emitted-version metric | 927 / 1837 exact emitted Maven versions |
| Clean source-validated real APKs | 47 / 47 emitted Maven versions across 5 APKs |
| Partial source-validated real APKs | 880 / 1790 emitted Maven versions across 97 APKs |
| V2 source-version constrained emitted rows | 6772 / 6772 exact confirmations |
| V2 wrong-version emitted rows | 0 |
| V2 missing emitted rows | 0 |
| V2 source-gap rows | 5238 |
| Explained/boundary source-gap rows | 2515 |
| Actionable source-gap rows | 2723 |
| Missing-reference candidate rows | 442 |
| Matcher-recall candidate rows | 2281 |
| Matcher report-only suggestions | 1425 |

## Exact Phrases

Use:

```text
The normal real-APK metric is emitted Maven version confirmation, not full dependency recall.
```

Use:

```text
The v2 result is a source-version constrained upper-bound lane. It proves exact recognition when the correct source versions are known, not unconstrained APK-only production accuracy.
```

Use:

```text
The remaining denominator is exported row by row: boundary/source-only rows, missing-reference rows, and matcher-recall rows are not hidden.
```

Avoid:

```text
The tool has 100% real-world APK accuracy.
```

## Verified Before Defense

| Check | Status |
|---|---|
| Transparency export regenerated | passed |
| Thesis artifact index regenerated | passed |
| Graduation demo rehearsal regenerated | passed |
| V2 dashboard JSON count check | 106 cases, 6772 checked, 0 mismatches, 0 missing |
| Transparency JSON count check | 110 cases, 12082 source rows, 6772 emitted rows, 232 vulnerability rows |
| Deck package validation | passed earlier: 12 slides, 12 notes slides |

## Do Not Run Live

- Do not rerun the full 106-APK v2 source-version evaluation during the defense.
- Do not rebuild the large DB during the defense.
- Do not query OSV live unless the network is known to work; the clean and vulnerable demo artifacts already exist.

## Safe Optional Commands

```powershell
python scripts\build_demo_final_transparency_export.py
python scripts\build_thesis_artifact_index.py
python scripts\build_graduation_demo_rehearsal.py
```
