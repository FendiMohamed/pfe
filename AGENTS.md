# Agent Instructions

This project is a PFE/master MVP for recovering SBOMs from compiled Android APKs.

## Read First

Before making changes, read:

1. `docs/codex/CODEX_CONTEXT.md`
2. `TASKS.md`
3. `docs/planning/IMPLEMENTATION_PLAN.md`
4. `docs/tooling/TOOLCHAIN.md`
5. `docs/architecture/DECISIONS_LOG.md`

## Approved MVP Scope

The MVP scope is approved/frozen. Do not reopen architecture discussions unless the user or supervisor explicitly changes the scope.

The MVP is:

```text
APK
-> extract DEX, manifest, resources, strings, native files
-> parse all classes*.dex files
-> detect known Java/Kotlin Maven libraries
-> estimate versions with confidence
-> generate CycloneDX SBOM
-> query vulnerabilities, OSV first
-> produce final report
```

The first MVP handles:

- standard single APK files
- multidex APKs
- Java/Kotlin Maven libraries
- selected known libraries in the reference DB
- light obfuscation and partial shrinking with lower confidence
- native `.so` extraction and hashing only

The first MVP does not handle:

- packed/encrypted APKs
- dynamic code loading
- commercial protectors
- full native `.so` version identification
- all Maven libraries
- perfect heavy R8 recovery

## Working Rules

- Keep changes small and verifiable.
- Update `TASKS.md` after completing or starting a task.
- Update `docs/tooling/TOOLCHAIN.md` when tool availability or tool choices change.
- Update `docs/architecture/DECISIONS_LOG.md` only for major approved decisions.
- Do not delete or rewrite research PDFs.
- Do not install dependencies without asking the user first.
- Prefer implementation work under `src/`.
- Put generated results under `data/results/`.
- Put reference DB artifacts under `data/reference_db/`.
- Put test APKs under `data/test_apks/`.

## Current Next Task

The toolchain audit, Docker setup files, Python scaffold, first APK extraction module, and initial Docker build are done.

Current status:

- Docker works from this environment with elevated access.
- Container tests pass.
- Apktool, D8, Trivy/Grype, and cyclonedx-cli are still optional/missing in the container.

Useful commands:

```powershell
docker compose build
docker compose run --rm apk-sbom python scripts/check_toolchain.py
docker compose run --rm apk-sbom pytest -q
```

Current implementation task:

- Generate the first minimal CycloneDX SBOM from mocked detection results.
