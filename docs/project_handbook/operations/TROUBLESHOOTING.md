# Troubleshooting

## Docker engine access denied

Symptom:

```text
open //./pipe/docker_engine: Access is denied
```

Checks:

```powershell
docker version
docker context ls
docker compose config
```

Use a PowerShell/session with Docker Desktop access. Do not interpret this as a
Python or matcher failure.

## A long Docker command prints nothing

Some evaluations buffer output. Verify liveness:

```powershell
docker ps
docker stats --no-stream
docker top CONTAINER_NAME
docker logs --tail 80 CONTAINER_NAME
```

An existing process with CPU activity can be healthy even when logs are empty.
Check the actual command inside the container before restarting a long batch.

## D8 is not found

Use Docker, or ensure Android build tools are on `PATH`.

```powershell
docker compose run --rm apk-sbom d8 --version
docker compose run --rm apk-sbom python scripts/check_toolchain.py
```

## Maven download returns 404

Possible causes:

- wrong `jar` versus `aar` packaging;
- artifact existed only on JCenter or another retired repository;
- alias or source-only version;
- POM/BOM/metadata-only artifact;
- Maven metadata lists a release whose binary is unavailable.

Do not fabricate bytes. Try the correct packaging/repository, classify the row,
or use an isolated exact-tag source build when justified and reproducible.

## Conversion is skipped

Inspect conversion metadata. Common honest skips:

- AAR has no `classes.jar`;
- JAR contains no bytecode;
- BOM/platform/POM-only module;
- artifact download is incomplete.

A skip is not always a failure.

## DEX parse error or zero features

Check:

- APK integrity;
- discovered DEX paths from `inspect-apk`;
- nonstandard or encrypted payloads;
- per-DEX parse errors;
- whether the artifact is native/resource-only.

Do not convert zero features into “no libraries present.”

## Matcher returns no candidates

Check:

- correct DB path;
- DB contains component rows;
- target coordinate/version exists;
- `--min-score` is not too high;
- a coordinate or prefilter did not remove the true candidate;
- the APK has parseable DEX evidence.

Use a coordinate-filtered diagnostic to separate reference absence from
unconstrained retrieval failure.

## Too many candidates or components

This can happen with a large DB and broad package overlap.

Check:

- whether experimental package prefiltering is enabled;
- candidate limits and per-coordinate limits;
- low `--min-score`;
- `--include-uncertain`;
- output change relative to the shared baseline;
- source-missing rows.

The priority I2P preflight is the reference example of a recall gain with a
severe precision regression.

## Wrong adjacent version

Inspect:

- whether the exact source version exists in the DB;
- candidate score margin;
- version-unique and literal-context evidence;
- artifact-family confusion;
- sibling app-era evidence;
- whether R8 removed version-distinguishing code.

Do not solve one row with a global “prefer newer” rule.

## OSV times out

Use:

```powershell
--skip-osv
```

for a fully offline report, or:

```powershell
--no-enrich --timeout 60
```

to reduce calls and allow more time.

## Source dependency task fails

Typical causes:

- project requires another Gradle version;
- Java version mismatch;
- retired JCenter/plugin repository;
- wrong module or configuration name;
- build scripts execute unavailable publishing plugins;
- network timeout.

Use an isolated validation copy and record every compatibility modification.
Do not alter the app evidence or call a failed dependency tree “clean.”

## SQLite is locked or corrupted

Ensure no other extraction process writes the same DB. Copy an experiment DB
before invasive inspection. Never use `--reset` as a casual repair on the
shared calibrated DB.

## Tests fail after documentation-only changes

First run link/Markdown checks if available, then `pytest -q`. Existing dirty
worktree changes may be unrelated; do not reset or overwrite them.

## Where to look next

- [Developer Runbook](../../dev/RUNBOOK.md)
- [Current Codex context](../../codex/CODEX_CONTEXT.md)
- [Safe experiment rules](SAFE_EXPERIMENT_RULES.md)
