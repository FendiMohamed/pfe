from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict, dataclass
from pathlib import Path

from apk_sbom.dex_analyzer import DexFileFeatures, analyze_dex_bytes
from apk_sbom.maven_downloader import MavenPomDependency
from apk_sbom.reference_converter import (
    DEFAULT_DEX_ROOT,
    DexFileRecord,
    ReferenceConversionResult,
)


DEFAULT_FEATURE_DB_PATH = Path("data/reference_db/reference_features.sqlite")


@dataclass(frozen=True)
class FeatureExtractionResult:
    coordinate: str
    version: str
    purl: str
    status: str
    dex_files_analyzed: int
    classes_count: int
    methods_count: int
    packages_count: int
    opcodes_count: int
    opcode_ngrams_count: int
    dependency_edges_count: int
    dependency_shapes_count: int
    string_literals_count: int
    api_references_count: int
    basic_block_fingerprints_count: int
    call_chain_fingerprints_count: int
    class_neighbor_summaries_count: int
    field_operation_sequences_count: int
    literal_context_features_count: int
    error: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class FeatureDatabaseSummary:
    db_path: str
    components: int
    dex_files: int
    packages: int
    classes: int
    methods: int
    opcodes: int
    opcode_ngrams: int
    class_dependencies: int
    dependency_shapes: int
    string_literals: int
    api_references: int
    basic_block_opcode_fingerprints: int
    call_chain_opcode_fingerprints: int
    class_neighbor_summaries: int
    field_operation_sequences: int
    literal_context_features: int
    results: list[FeatureExtractionResult]

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True)


def load_conversion_result(metadata_path: str | Path) -> ReferenceConversionResult:
    path = Path(metadata_path)
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    dex_files = [DexFileRecord(**item) for item in payload.get("dex_files", [])]
    dependencies = [
        item
        if isinstance(item, MavenPomDependency)
        else MavenPomDependency(
            group=str(item["group"]),
            artifact=str(item["artifact"]),
            version=item.get("version"),
            scope=item.get("scope"),
            optional=bool(item.get("optional", False)),
            type=item.get("type"),
            classifier=item.get("classifier"),
        )
        for item in payload.get("maven_dependencies", [])
    ]
    payload = {**payload, "dex_files": dex_files, "maven_dependencies": dependencies}
    return ReferenceConversionResult(**payload)


def discover_conversion_results(
    dex_root: str | Path = DEFAULT_DEX_ROOT,
    *,
    coordinate: str | None = None,
    limit: int | None = None,
    offset: int = 0,
    include_skipped: bool = False,
) -> list[ReferenceConversionResult]:
    if offset < 0:
        raise ValueError("offset must be >= 0")

    root = Path(dex_root)
    results: list[ReferenceConversionResult] = []
    seen = 0

    for metadata_path in sorted(root.rglob("conversion.json")):
        result = load_conversion_result(metadata_path)
        if coordinate and result.coordinate != coordinate:
            continue
        if result.status == "skipped" and not include_skipped:
            continue
        if seen < offset:
            seen += 1
            continue
        seen += 1
        results.append(result)
        if limit is not None and len(results) >= limit:
            return results

    return results


def initialize_feature_db(db_path: str | Path) -> None:
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as connection:
        connection.executescript(
            """
            PRAGMA foreign_keys = ON;

            CREATE TABLE IF NOT EXISTS components (
                id INTEGER PRIMARY KEY,
                coordinate TEXT NOT NULL,
                group_id TEXT NOT NULL,
                artifact_id TEXT NOT NULL,
                version TEXT NOT NULL,
                purl TEXT NOT NULL,
                packaging TEXT NOT NULL,
                conversion_status TEXT NOT NULL,
                artifact_path TEXT NOT NULL,
                dex_output_dir TEXT NOT NULL,
                conversion_metadata_path TEXT NOT NULL,
                classes_count INTEGER NOT NULL DEFAULT 0,
                methods_count INTEGER NOT NULL DEFAULT 0,
                UNIQUE(coordinate, version)
            );

            CREATE TABLE IF NOT EXISTS dex_files (
                id INTEGER PRIMARY KEY,
                component_id INTEGER NOT NULL,
                path TEXT NOT NULL,
                sha256 TEXT NOT NULL,
                size INTEGER NOT NULL,
                classes_count INTEGER NOT NULL,
                methods_count INTEGER NOT NULL,
                FOREIGN KEY(component_id) REFERENCES components(id) ON DELETE CASCADE,
                UNIQUE(component_id, path)
            );

            CREATE TABLE IF NOT EXISTS packages (
                component_id INTEGER NOT NULL,
                package TEXT NOT NULL,
                FOREIGN KEY(component_id) REFERENCES components(id) ON DELETE CASCADE,
                PRIMARY KEY(component_id, package)
            );

            CREATE TABLE IF NOT EXISTS classes (
                component_id INTEGER NOT NULL,
                class_descriptor TEXT NOT NULL,
                FOREIGN KEY(component_id) REFERENCES components(id) ON DELETE CASCADE,
                PRIMARY KEY(component_id, class_descriptor)
            );

            CREATE TABLE IF NOT EXISTS methods (
                component_id INTEGER NOT NULL,
                method_signature TEXT NOT NULL,
                FOREIGN KEY(component_id) REFERENCES components(id) ON DELETE CASCADE,
                PRIMARY KEY(component_id, method_signature)
            );

            CREATE TABLE IF NOT EXISTS opcodes (
                component_id INTEGER NOT NULL,
                opcode TEXT NOT NULL,
                count INTEGER NOT NULL,
                FOREIGN KEY(component_id) REFERENCES components(id) ON DELETE CASCADE,
                PRIMARY KEY(component_id, opcode)
            );

            CREATE TABLE IF NOT EXISTS opcode_ngrams (
                component_id INTEGER NOT NULL,
                ngram TEXT NOT NULL,
                count INTEGER NOT NULL,
                FOREIGN KEY(component_id) REFERENCES components(id) ON DELETE CASCADE,
                PRIMARY KEY(component_id, ngram)
            );

            CREATE TABLE IF NOT EXISTS class_dependencies (
                component_id INTEGER NOT NULL,
                source_class TEXT NOT NULL,
                target_class TEXT NOT NULL,
                kind TEXT NOT NULL,
                FOREIGN KEY(component_id) REFERENCES components(id) ON DELETE CASCADE,
                PRIMARY KEY(component_id, source_class, target_class, kind)
            );

            CREATE TABLE IF NOT EXISTS dependency_shapes (
                component_id INTEGER NOT NULL,
                feature TEXT NOT NULL,
                count INTEGER NOT NULL,
                FOREIGN KEY(component_id) REFERENCES components(id) ON DELETE CASCADE,
                PRIMARY KEY(component_id, feature)
            );

            CREATE TABLE IF NOT EXISTS string_literals (
                component_id INTEGER NOT NULL,
                literal TEXT NOT NULL,
                FOREIGN KEY(component_id) REFERENCES components(id) ON DELETE CASCADE,
                PRIMARY KEY(component_id, literal)
            );

            CREATE TABLE IF NOT EXISTS api_references (
                component_id INTEGER NOT NULL,
                reference TEXT NOT NULL,
                FOREIGN KEY(component_id) REFERENCES components(id) ON DELETE CASCADE,
                PRIMARY KEY(component_id, reference)
            );

            CREATE TABLE IF NOT EXISTS basic_block_opcode_fingerprints (
                component_id INTEGER NOT NULL,
                fingerprint TEXT NOT NULL,
                count INTEGER NOT NULL,
                FOREIGN KEY(component_id) REFERENCES components(id) ON DELETE CASCADE,
                PRIMARY KEY(component_id, fingerprint)
            );

            CREATE TABLE IF NOT EXISTS call_chain_opcode_fingerprints (
                component_id INTEGER NOT NULL,
                fingerprint TEXT NOT NULL,
                count INTEGER NOT NULL,
                FOREIGN KEY(component_id) REFERENCES components(id) ON DELETE CASCADE,
                PRIMARY KEY(component_id, fingerprint)
            );

            CREATE TABLE IF NOT EXISTS class_neighbor_summaries (
                component_id INTEGER NOT NULL,
                summary TEXT NOT NULL,
                count INTEGER NOT NULL,
                FOREIGN KEY(component_id) REFERENCES components(id) ON DELETE CASCADE,
                PRIMARY KEY(component_id, summary)
            );

            CREATE TABLE IF NOT EXISTS field_operation_sequences (
                component_id INTEGER NOT NULL,
                fingerprint TEXT NOT NULL,
                count INTEGER NOT NULL,
                FOREIGN KEY(component_id) REFERENCES components(id) ON DELETE CASCADE,
                PRIMARY KEY(component_id, fingerprint)
            );

            CREATE TABLE IF NOT EXISTS literal_context_features (
                component_id INTEGER NOT NULL,
                feature TEXT NOT NULL,
                FOREIGN KEY(component_id) REFERENCES components(id) ON DELETE CASCADE,
                PRIMARY KEY(component_id, feature)
            );

            CREATE TABLE IF NOT EXISTS maven_dependencies (
                component_id INTEGER NOT NULL,
                group_id TEXT NOT NULL,
                artifact_id TEXT NOT NULL,
                coordinate TEXT NOT NULL,
                version TEXT,
                scope TEXT,
                optional INTEGER NOT NULL DEFAULT 0,
                type TEXT,
                classifier TEXT,
                FOREIGN KEY(component_id) REFERENCES components(id) ON DELETE CASCADE
            );
            """
        )


def extract_reference_features_to_db(
    conversions: list[ReferenceConversionResult],
    *,
    db_path: str | Path = DEFAULT_FEATURE_DB_PATH,
    reset: bool = False,
) -> FeatureDatabaseSummary:
    path = Path(db_path)
    if reset and path.exists():
        path.unlink()
    initialize_feature_db(path)

    results: list[FeatureExtractionResult] = []
    with sqlite3.connect(path) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        for conversion in conversions:
            result = _store_conversion_features(connection, conversion)
            results.append(result)

        summary = _database_summary(connection, path, results)

    return summary


def _store_conversion_features(
    connection: sqlite3.Connection,
    conversion: ReferenceConversionResult,
) -> FeatureExtractionResult:
    if conversion.status not in {"converted", "existing"}:
        return FeatureExtractionResult(
            coordinate=conversion.coordinate,
            version=conversion.version,
            purl=conversion.purl,
            status="skipped",
            dex_files_analyzed=0,
            classes_count=0,
            methods_count=0,
            packages_count=0,
            opcodes_count=0,
            opcode_ngrams_count=0,
            dependency_edges_count=0,
            dependency_shapes_count=0,
            string_literals_count=0,
            api_references_count=0,
            basic_block_fingerprints_count=0,
            call_chain_fingerprints_count=0,
            class_neighbor_summaries_count=0,
            field_operation_sequences_count=0,
            literal_context_features_count=0,
            error=f"conversion status is {conversion.status}",
        )

    group_id, artifact_id = conversion.coordinate.split(":", maxsplit=1)
    component_id = _upsert_component(connection, conversion, group_id, artifact_id)
    _clear_component_features(connection, component_id)

    dex_features: list[DexFileFeatures] = []
    for dex_file in conversion.dex_files:
        dex_path = _resolve_path(dex_file.path)
        if not dex_path.exists():
            return FeatureExtractionResult(
                coordinate=conversion.coordinate,
                version=conversion.version,
                purl=conversion.purl,
                status="failed",
                dex_files_analyzed=len(dex_features),
                classes_count=sum(item.classes_count for item in dex_features),
                methods_count=sum(item.methods_count for item in dex_features),
                packages_count=0,
                opcodes_count=0,
                opcode_ngrams_count=0,
                dependency_edges_count=0,
                dependency_shapes_count=0,
                string_literals_count=0,
                api_references_count=0,
                basic_block_fingerprints_count=0,
                call_chain_fingerprints_count=0,
                class_neighbor_summaries_count=0,
                field_operation_sequences_count=0,
                literal_context_features_count=0,
                error=f"DEX file does not exist: {dex_path}",
            )

        features = analyze_dex_bytes(str(dex_path), dex_path.read_bytes(), include_members=True)
        dex_features.append(features)
        connection.execute(
            """
            INSERT INTO dex_files(component_id, path, sha256, size, classes_count, methods_count)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                component_id,
                str(dex_path),
                dex_file.sha256,
                dex_file.size,
                features.classes_count,
                features.methods_count,
            ),
        )

    packages = sorted({package for item in dex_features for package in item.packages})
    classes = sorted({class_name for item in dex_features for class_name in item.class_descriptors})
    methods = sorted({method for item in dex_features for method in item.method_signatures})
    string_literals = sorted({literal for item in dex_features for literal in item.string_literals})
    api_references = sorted({reference for item in dex_features for reference in item.api_references})
    literal_context_features = sorted(
        {feature for item in dex_features for feature in item.literal_context_features}
    )
    opcodes: dict[str, int] = {}
    opcode_ngrams: dict[str, int] = {}
    basic_block_fingerprints: dict[str, int] = {}
    call_chain_fingerprints: dict[str, int] = {}
    class_neighbor_summaries: dict[str, int] = {}
    field_operation_sequences: dict[str, int] = {}
    dependency_edges = sorted(
        {
            (edge.source, edge.target, edge.kind)
            for item in dex_features
            for edge in item.class_dependencies
        }
    )
    dependency_shapes: dict[str, int] = {}
    for item in dex_features:
        for opcode, count in item.opcode_histogram.items():
            opcodes[opcode] = opcodes.get(opcode, 0) + count
        for ngram, count in item.opcode_ngrams.items():
            opcode_ngrams[ngram] = opcode_ngrams.get(ngram, 0) + count
        for feature, count in item.dependency_shape.items():
            dependency_shapes[feature] = dependency_shapes.get(feature, 0) + count
        for fingerprint, count in item.basic_block_opcode_fingerprints.items():
            basic_block_fingerprints[fingerprint] = (
                basic_block_fingerprints.get(fingerprint, 0) + count
            )
        for fingerprint, count in item.call_chain_opcode_fingerprints.items():
            call_chain_fingerprints[fingerprint] = call_chain_fingerprints.get(fingerprint, 0) + count
        for summary, count in item.class_neighbor_summaries.items():
            class_neighbor_summaries[summary] = class_neighbor_summaries.get(summary, 0) + count
        for fingerprint, count in item.field_operation_sequences.items():
            field_operation_sequences[fingerprint] = (
                field_operation_sequences.get(fingerprint, 0) + count
            )

    connection.executemany(
        "INSERT INTO packages(component_id, package) VALUES (?, ?)",
        [(component_id, package) for package in packages],
    )
    connection.executemany(
        "INSERT INTO classes(component_id, class_descriptor) VALUES (?, ?)",
        [(component_id, class_name) for class_name in classes],
    )
    connection.executemany(
        "INSERT INTO methods(component_id, method_signature) VALUES (?, ?)",
        [(component_id, method) for method in methods],
    )
    connection.executemany(
        "INSERT INTO opcodes(component_id, opcode, count) VALUES (?, ?, ?)",
        [(component_id, opcode, count) for opcode, count in sorted(opcodes.items())],
    )
    connection.executemany(
        "INSERT INTO opcode_ngrams(component_id, ngram, count) VALUES (?, ?, ?)",
        [(component_id, ngram, count) for ngram, count in sorted(opcode_ngrams.items())],
    )
    connection.executemany(
        "INSERT INTO string_literals(component_id, literal) VALUES (?, ?)",
        [(component_id, literal) for literal in string_literals],
    )
    connection.executemany(
        "INSERT INTO api_references(component_id, reference) VALUES (?, ?)",
        [(component_id, reference) for reference in api_references],
    )
    connection.executemany(
        """
        INSERT INTO basic_block_opcode_fingerprints(component_id, fingerprint, count)
        VALUES (?, ?, ?)
        """,
        [
            (component_id, fingerprint, count)
            for fingerprint, count in sorted(basic_block_fingerprints.items())
        ],
    )
    connection.executemany(
        """
        INSERT INTO call_chain_opcode_fingerprints(component_id, fingerprint, count)
        VALUES (?, ?, ?)
        """,
        [
            (component_id, fingerprint, count)
            for fingerprint, count in sorted(call_chain_fingerprints.items())
        ],
    )
    connection.executemany(
        """
        INSERT INTO class_neighbor_summaries(component_id, summary, count)
        VALUES (?, ?, ?)
        """,
        [
            (component_id, summary, count)
            for summary, count in sorted(class_neighbor_summaries.items())
        ],
    )
    connection.executemany(
        """
        INSERT INTO field_operation_sequences(component_id, fingerprint, count)
        VALUES (?, ?, ?)
        """,
        [
            (component_id, fingerprint, count)
            for fingerprint, count in sorted(field_operation_sequences.items())
        ],
    )
    connection.executemany(
        "INSERT INTO literal_context_features(component_id, feature) VALUES (?, ?)",
        [(component_id, feature) for feature in literal_context_features],
    )
    connection.executemany(
        """
        INSERT INTO class_dependencies(component_id, source_class, target_class, kind)
        VALUES (?, ?, ?, ?)
        """,
        [(component_id, source, target, kind) for source, target, kind in dependency_edges],
    )
    connection.executemany(
        "INSERT INTO dependency_shapes(component_id, feature, count) VALUES (?, ?, ?)",
        [(component_id, feature, count) for feature, count in sorted(dependency_shapes.items())],
    )
    connection.executemany(
        """
        INSERT INTO maven_dependencies(
            component_id, group_id, artifact_id, coordinate, version, scope,
            optional, type, classifier
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                component_id,
                dependency.group,
                dependency.artifact,
                dependency.coordinate,
                dependency.version,
                dependency.scope,
                int(dependency.optional),
                dependency.type,
                dependency.classifier,
            )
            for dependency in conversion.maven_dependencies or []
        ],
    )
    connection.execute(
        "UPDATE components SET classes_count = ?, methods_count = ? WHERE id = ?",
        (
            sum(item.classes_count for item in dex_features),
            sum(item.methods_count for item in dex_features),
            component_id,
        ),
    )

    return FeatureExtractionResult(
        coordinate=conversion.coordinate,
        version=conversion.version,
        purl=conversion.purl,
        status="stored",
        dex_files_analyzed=len(dex_features),
        classes_count=sum(item.classes_count for item in dex_features),
        methods_count=sum(item.methods_count for item in dex_features),
        packages_count=len(packages),
        opcodes_count=len(opcodes),
        opcode_ngrams_count=len(opcode_ngrams),
        dependency_edges_count=len(dependency_edges),
        dependency_shapes_count=len(dependency_shapes),
        string_literals_count=len(string_literals),
        api_references_count=len(api_references),
        basic_block_fingerprints_count=len(basic_block_fingerprints),
        call_chain_fingerprints_count=len(call_chain_fingerprints),
        class_neighbor_summaries_count=len(class_neighbor_summaries),
        field_operation_sequences_count=len(field_operation_sequences),
        literal_context_features_count=len(literal_context_features),
    )


def _upsert_component(
    connection: sqlite3.Connection,
    conversion: ReferenceConversionResult,
    group_id: str,
    artifact_id: str,
) -> int:
    connection.execute(
        """
        INSERT INTO components(
            coordinate, group_id, artifact_id, version, purl, packaging,
            conversion_status, artifact_path, dex_output_dir, conversion_metadata_path
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(coordinate, version) DO UPDATE SET
            purl = excluded.purl,
            packaging = excluded.packaging,
            conversion_status = excluded.conversion_status,
            artifact_path = excluded.artifact_path,
            dex_output_dir = excluded.dex_output_dir,
            conversion_metadata_path = excluded.conversion_metadata_path
        """,
        (
            conversion.coordinate,
            group_id,
            artifact_id,
            conversion.version,
            conversion.purl,
            conversion.packaging,
            conversion.status,
            conversion.artifact_path,
            conversion.output_dir,
            conversion.metadata_path,
        ),
    )
    row = connection.execute(
        "SELECT id FROM components WHERE coordinate = ? AND version = ?",
        (conversion.coordinate, conversion.version),
    ).fetchone()
    return int(row[0])


def _clear_component_features(connection: sqlite3.Connection, component_id: int) -> None:
    for table in (
        "dex_files",
        "packages",
        "classes",
        "methods",
        "opcodes",
        "opcode_ngrams",
        "string_literals",
        "api_references",
        "basic_block_opcode_fingerprints",
        "call_chain_opcode_fingerprints",
        "class_neighbor_summaries",
        "field_operation_sequences",
        "literal_context_features",
        "class_dependencies",
        "dependency_shapes",
        "maven_dependencies",
    ):
        connection.execute(f"DELETE FROM {table} WHERE component_id = ?", (component_id,))


def _database_summary(
    connection: sqlite3.Connection,
    db_path: Path,
    results: list[FeatureExtractionResult],
) -> FeatureDatabaseSummary:
    return FeatureDatabaseSummary(
        db_path=str(db_path),
        components=_count_rows(connection, "components"),
        dex_files=_count_rows(connection, "dex_files"),
        packages=_count_rows(connection, "packages"),
        classes=_count_rows(connection, "classes"),
        methods=_count_rows(connection, "methods"),
        opcodes=_count_rows(connection, "opcodes"),
        opcode_ngrams=_count_rows(connection, "opcode_ngrams"),
        class_dependencies=_count_rows(connection, "class_dependencies"),
        dependency_shapes=_count_rows(connection, "dependency_shapes"),
        string_literals=_count_rows(connection, "string_literals"),
        api_references=_count_rows(connection, "api_references"),
        basic_block_opcode_fingerprints=_count_rows(
            connection,
            "basic_block_opcode_fingerprints",
        ),
        call_chain_opcode_fingerprints=_count_rows(
            connection,
            "call_chain_opcode_fingerprints",
        ),
        class_neighbor_summaries=_count_rows(connection, "class_neighbor_summaries"),
        field_operation_sequences=_count_rows(connection, "field_operation_sequences"),
        literal_context_features=_count_rows(connection, "literal_context_features"),
        results=results,
    )


def _count_rows(connection: sqlite3.Connection, table: str) -> int:
    row = connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()
    return int(row[0])


def _resolve_path(path: str | Path) -> Path:
    candidate = Path(path)
    if candidate.exists():
        return candidate
    raw_path = str(path)
    if "\\" in raw_path:
        normalized = Path(raw_path.replace("\\", "/"))
        if normalized.exists():
            return normalized
    return candidate
