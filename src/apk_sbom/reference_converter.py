from __future__ import annotations

import json
import shlex
import subprocess
import tempfile
import zipfile
from dataclasses import asdict, dataclass
from pathlib import Path

from apk_sbom.apk_extractor import sha256_file
from apk_sbom.maven_downloader import ArtifactRecord, MavenPomDependency


DEFAULT_ARTIFACT_ROOT = Path("data/reference_db/artifacts")
DEFAULT_DEX_ROOT = Path("data/reference_db/dex")


@dataclass(frozen=True)
class DexFileRecord:
    path: str
    sha256: str
    size: int


@dataclass(frozen=True)
class ReferenceConversionResult:
    coordinate: str
    version: str
    purl: str
    packaging: str
    status: str
    artifact_path: str
    output_dir: str
    metadata_path: str
    dex_files: list[DexFileRecord]
    command: list[str]
    error: str | None = None
    stdout: str = ""
    stderr: str = ""
    artifact_metadata_path: str | None = None
    maven_dependencies: list[MavenPomDependency] | None = None

    def to_dict(self) -> dict:
        return asdict(self)

    def __post_init__(self) -> None:
        if self.maven_dependencies is None:
            object.__setattr__(self, "maven_dependencies", [])


def parse_d8_command(command: str | list[str] | tuple[str, ...]) -> list[str]:
    if isinstance(command, str):
        return shlex.split(command)
    return list(command)


def load_artifact_record(metadata_path: str | Path) -> ArtifactRecord:
    path = Path(metadata_path)
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return ArtifactRecord.from_dict(payload)


def discover_artifact_records(
    artifact_root: str | Path = DEFAULT_ARTIFACT_ROOT,
    *,
    coordinate: str | None = None,
    limit: int | None = None,
    offset: int = 0,
) -> list[ArtifactRecord]:
    if offset < 0:
        raise ValueError("offset must be >= 0")

    root = Path(artifact_root)
    records: list[ArtifactRecord] = []
    seen = 0

    for metadata_path in sorted(root.rglob("metadata.json")):
        record = load_artifact_record(metadata_path)
        if coordinate and record.coordinate != coordinate:
            continue
        if seen < offset:
            seen += 1
            continue
        seen += 1
        records.append(record)
        if limit is not None and len(records) >= limit:
            return records

    return records


def dex_output_dir(record: ArtifactRecord, output_root: str | Path = DEFAULT_DEX_ROOT) -> Path:
    return Path(output_root) / Path(*record.group.split(".")) / record.artifact / record.version


def dex_metadata_path(record: ArtifactRecord, output_root: str | Path = DEFAULT_DEX_ROOT) -> Path:
    return dex_output_dir(record, output_root) / "conversion.json"


def planned_conversion(record: ArtifactRecord, output_root: str | Path = DEFAULT_DEX_ROOT) -> dict:
    output_dir = dex_output_dir(record, output_root)
    return {
        "coordinate": record.coordinate,
        "version": record.version,
        "purl": record.purl,
        "packaging": record.packaging,
        "artifact_path": record.path,
        "output_dir": str(output_dir),
        "metadata_path": str(output_dir / "conversion.json"),
    }


def convert_artifact_to_dex(
    record: ArtifactRecord,
    *,
    output_root: str | Path = DEFAULT_DEX_ROOT,
    d8_command: str | list[str] | tuple[str, ...] = "d8",
    min_api: int = 21,
    timeout: int = 120,
    force: bool = False,
) -> ReferenceConversionResult:
    output_dir = dex_output_dir(record, output_root)
    metadata_path = dex_metadata_path(record, output_root)
    command_prefix = parse_d8_command(d8_command)

    if not command_prefix:
        return _failed_result(record, output_dir, metadata_path, [], "D8 command is empty")

    artifact_path = resolve_artifact_path(record.path)
    if not artifact_path.exists():
        return _failed_result(
            record,
            output_dir,
            metadata_path,
            command_prefix,
            f"Artifact file does not exist: {artifact_path}",
        )

    if metadata_path.exists() and _dex_files(output_dir) and not force:
        result = ReferenceConversionResult(
            coordinate=record.coordinate,
            version=record.version,
            purl=record.purl,
            packaging=record.packaging,
            status="existing",
            artifact_path=str(artifact_path),
            output_dir=str(output_dir),
            metadata_path=str(metadata_path),
            dex_files=_dex_file_records(output_dir),
            command=[],
            maven_dependencies=record.dependencies,
        )
        write_conversion_metadata(result)
        return result

    output_dir.mkdir(parents=True, exist_ok=True)

    if record.packaging == "jar":
        return _run_d8(
            record,
            artifact_path,
            output_dir,
            metadata_path,
            command_prefix,
            min_api=min_api,
            timeout=timeout,
        )

    if record.packaging == "aar":
        return _convert_aar(
            record,
            artifact_path,
            output_dir,
            metadata_path,
            command_prefix,
            min_api=min_api,
            timeout=timeout,
        )

    return _failed_result(
        record,
        output_dir,
        metadata_path,
        command_prefix,
        f"Unsupported artifact packaging: {record.packaging}",
    )


def convert_reference_artifacts(
    records: list[ArtifactRecord],
    *,
    output_root: str | Path = DEFAULT_DEX_ROOT,
    d8_command: str | list[str] | tuple[str, ...] = "d8",
    min_api: int = 21,
    timeout: int = 120,
    force: bool = False,
) -> list[ReferenceConversionResult]:
    return [
        convert_artifact_to_dex(
            record,
            output_root=output_root,
            d8_command=d8_command,
            min_api=min_api,
            timeout=timeout,
            force=force,
        )
        for record in records
    ]


def resolve_artifact_path(path: str | Path) -> Path:
    candidate = Path(path)
    if candidate.exists():
        return candidate

    raw_path = str(path)
    if "\\" in raw_path:
        normalized = Path(raw_path.replace("\\", "/"))
        if normalized.exists():
            return normalized

    return candidate


def write_conversion_metadata(result: ReferenceConversionResult) -> Path:
    path = Path(result.metadata_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def _convert_aar(
    record: ArtifactRecord,
    aar_path: Path,
    output_dir: Path,
    metadata_path: Path,
    command_prefix: list[str],
    *,
    min_api: int,
    timeout: int,
) -> ReferenceConversionResult:
    with tempfile.TemporaryDirectory(prefix="apk-sbom-aar-") as temp_dir:
        classes_jar = Path(temp_dir) / "classes.jar"
        try:
            with zipfile.ZipFile(aar_path) as archive:
                with archive.open("classes.jar") as source, classes_jar.open("wb") as target:
                    target.write(source.read())
        except KeyError:
            return _skipped_result(
                record,
                output_dir,
                metadata_path,
                command_prefix,
                "AAR contains no classes.jar; no JVM bytecode to dex",
            )
        except (OSError, zipfile.BadZipFile) as exc:
            return _failed_result(
                record,
                output_dir,
                metadata_path,
                command_prefix,
                f"Could not extract classes.jar from AAR: {exc}",
            )

        return _run_d8(
            record,
            classes_jar,
            output_dir,
            metadata_path,
            command_prefix,
            min_api=min_api,
            timeout=timeout,
        )


def _run_d8(
    record: ArtifactRecord,
    input_path: Path,
    output_dir: Path,
    metadata_path: Path,
    command_prefix: list[str],
    *,
    min_api: int,
    timeout: int,
) -> ReferenceConversionResult:
    command = [*command_prefix, "--min-api", str(min_api), "--output", str(output_dir), str(input_path)]

    try:
        completed = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except FileNotFoundError:
        return _failed_result(
            record,
            output_dir,
            metadata_path,
            command,
            f"D8 command not found: {command_prefix[0]}",
        )
    except subprocess.TimeoutExpired as exc:
        return _failed_result(
            record,
            output_dir,
            metadata_path,
            command,
            f"D8 conversion timed out after {timeout} seconds",
            stdout=exc.stdout or "",
            stderr=exc.stderr or "",
        )

    dex_files = _dex_file_records(output_dir)
    if completed.returncode != 0:
        return _failed_result(
            record,
            output_dir,
            metadata_path,
            command,
            f"D8 exited with code {completed.returncode}",
            stdout=completed.stdout,
            stderr=completed.stderr,
        )

    if not dex_files:
        return _skipped_result(
            record,
            output_dir,
            metadata_path,
            command,
            "D8 completed but no classes*.dex files were produced",
            stdout=completed.stdout,
            stderr=completed.stderr,
        )

    result = ReferenceConversionResult(
        coordinate=record.coordinate,
        version=record.version,
        purl=record.purl,
        packaging=record.packaging,
        status="converted",
        artifact_path=record.path,
        output_dir=str(output_dir),
        metadata_path=str(metadata_path),
        dex_files=dex_files,
        command=command,
        stdout=completed.stdout,
        stderr=completed.stderr,
        maven_dependencies=record.dependencies,
    )
    write_conversion_metadata(result)
    return result


def _skipped_result(
    record: ArtifactRecord,
    output_dir: Path,
    metadata_path: Path,
    command: list[str],
    error: str,
    *,
    stdout: str = "",
    stderr: str = "",
) -> ReferenceConversionResult:
    result = ReferenceConversionResult(
        coordinate=record.coordinate,
        version=record.version,
        purl=record.purl,
        packaging=record.packaging,
        status="skipped",
        artifact_path=record.path,
        output_dir=str(output_dir),
        metadata_path=str(metadata_path),
        dex_files=[],
        command=command,
        error=error,
        stdout=stdout,
        stderr=stderr,
        maven_dependencies=record.dependencies,
    )
    write_conversion_metadata(result)
    return result


def _failed_result(
    record: ArtifactRecord,
    output_dir: Path,
    metadata_path: Path,
    command: list[str],
    error: str,
    *,
    stdout: str = "",
    stderr: str = "",
) -> ReferenceConversionResult:
    return ReferenceConversionResult(
        coordinate=record.coordinate,
        version=record.version,
        purl=record.purl,
        packaging=record.packaging,
        status="failed",
        artifact_path=record.path,
        output_dir=str(output_dir),
        metadata_path=str(metadata_path),
        dex_files=[],
        command=command,
        error=error,
        stdout=stdout,
        stderr=stderr,
        maven_dependencies=record.dependencies,
    )


def _dex_files(output_dir: Path) -> list[Path]:
    return sorted(output_dir.glob("classes*.dex"))


def _dex_file_records(output_dir: Path) -> list[DexFileRecord]:
    return [
        DexFileRecord(path=str(path), sha256=sha256_file(path), size=path.stat().st_size)
        for path in _dex_files(output_dir)
    ]
