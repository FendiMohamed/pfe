from __future__ import annotations

import json
import re
import zipfile
from collections import Counter
from dataclasses import asdict, dataclass, field
from hashlib import sha256
from pathlib import Path

from apk_sbom.apk_extractor import DEX_PATTERN, normalized_zip_names


DESCRIPTOR_PATTERN = re.compile(r"L[^;]+;")
API_REFERENCE_PATTERN = re.compile(r"L[^;]+;->[^\s,]+")
STRING_LITERAL_MAX_LENGTH = 512
OPCODE_NGRAM_SIZE = 3
BASIC_BLOCK_BOUNDARY_PREFIXES = ("return", "throw", "goto", "if-", "packed-switch", "sparse-switch")
FIELD_OPERATION_PREFIXES = ("iget", "iput", "sget", "sput")
INVOKE_OPCODE_PREFIX = "invoke-"


@dataclass(frozen=True)
class DexParseError:
    dex_file: str
    error: str


@dataclass(frozen=True)
class ClassDependency:
    source: str
    target: str
    kind: str


@dataclass(frozen=True)
class DexFileFeatures:
    dex_file: str
    classes_count: int
    methods_count: int
    packages: list[str]
    class_descriptors: list[str]
    method_signatures: list[str]
    opcode_histogram: dict[str, int]
    field_signatures: list[str] = field(default_factory=list)
    opcode_ngrams: dict[str, int] = field(default_factory=dict)
    class_dependencies: list[ClassDependency] = field(default_factory=list)
    dependency_shape: dict[str, int] = field(default_factory=dict)
    string_literals: list[str] = field(default_factory=list)
    api_references: list[str] = field(default_factory=list)
    basic_block_opcode_fingerprints: dict[str, int] = field(default_factory=dict)
    call_chain_opcode_fingerprints: dict[str, int] = field(default_factory=dict)
    class_neighbor_summaries: dict[str, int] = field(default_factory=dict)
    field_operation_sequences: dict[str, int] = field(default_factory=dict)
    literal_context_features: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ApkDexAnalysis:
    apk_path: str
    dex_files_analyzed: int
    dex_files_failed: int
    classes_count: int
    methods_count: int
    packages: list[str]
    opcode_histogram: dict[str, int]
    opcode_ngrams: dict[str, int]
    dex_files: list[DexFileFeatures]
    parse_errors: list[DexParseError]
    basic_block_opcode_fingerprints: dict[str, int] = field(default_factory=dict)
    call_chain_opcode_fingerprints: dict[str, int] = field(default_factory=dict)
    class_neighbor_summaries: dict[str, int] = field(default_factory=dict)
    field_operation_sequences: dict[str, int] = field(default_factory=dict)
    literal_context_features: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True)


def class_descriptor_to_package(descriptor: str) -> str | None:
    if not descriptor.startswith("L") or "/" not in descriptor:
        return None

    package_path = descriptor[1:].rsplit("/", maxsplit=1)[0]
    if not package_path:
        return None

    return package_path.replace("/", ".")


def analyze_dex_bytes(dex_file: str, data: bytes, *, include_members: bool = False) -> DexFileFeatures:
    silence_androguard_logging()
    from androguard.core.dex import DEX

    dex = DEX(data)
    packages: set[str] = set()
    class_descriptors: set[str] = set()
    method_signatures: set[str] = set()
    field_signatures: set[str] = set()
    string_literals: set[str] = set()
    api_references: set[str] = set()
    opcode_counter: Counter[str] = Counter()
    opcode_ngram_counter: Counter[str] = Counter()
    basic_block_counter: Counter[str] = Counter()
    call_chain_counter: Counter[str] = Counter()
    field_operation_counter: Counter[str] = Counter()
    literal_context_features: set[str] = set()
    classes_count = 0
    methods_count = 0

    dex_classes = list(dex.get_classes())
    internal_classes = {dex_class.get_name() for dex_class in dex_classes}
    dependency_edges: set[tuple[str, str, str]] = set()

    for dex_class in dex_classes:
        classes_count += 1
        class_name = dex_class.get_name()
        if include_members:
            class_descriptors.add(class_name)
            dependency_edges.update(_class_dependency_edges(dex_class, class_name, internal_classes))
            for field_item in _safe_iter(_safe_call(dex_class, "get_fields")):
                field_name = _safe_call(field_item, "get_name")
                descriptor = _safe_call(field_item, "get_descriptor")
                if field_name:
                    field_signatures.add(f"{class_name}->{field_name}:{descriptor or ''}")

        package_name = class_descriptor_to_package(class_name)
        if package_name:
            packages.add(package_name)

        class_methods = list(dex_class.get_methods())
        methods_count += len(class_methods)

        for method in class_methods:
            method_name = method.get_name()
            method_descriptor = method.get_descriptor()
            method_signature = f"{class_name}->{method_name}{method_descriptor}"
            if include_members:
                method_signatures.add(method_signature)

            try:
                instructions = method.get_instructions()
            except Exception:
                continue

            method_opcodes: list[str] = []
            for instruction in instructions:
                instruction_name = instruction.get_name()
                method_opcodes.append(instruction_name)
                opcode_counter[instruction_name] += 1
                if include_members:
                    instruction_output = _safe_call(instruction, "get_output")
                    literal = extract_string_literal_from_instruction(
                        instruction_name,
                        instruction_output,
                    )
                    if literal is not None:
                        string_literals.add(literal)
                        literal_context_features.add(
                            literal_context_feature(class_name, method_signature, literal)
                        )
                    api_references.update(extract_api_references_from_instruction(instruction_output))
            opcode_ngram_counter.update(opcode_ngrams_from_sequence(method_opcodes))
            basic_block_counter.update(basic_block_fingerprints_from_sequence(method_opcodes))
            call_chain_counter.update(call_chain_fingerprints_from_sequence(method_opcodes))
            if include_members:
                field_operation_counter.update(
                    field_operation_fingerprints_from_sequence(method_opcodes)
                )

    return DexFileFeatures(
        dex_file=dex_file,
        classes_count=classes_count,
        methods_count=methods_count,
        packages=sorted(packages),
        class_descriptors=sorted(class_descriptors),
        method_signatures=sorted(method_signatures),
        opcode_histogram=dict(sorted(opcode_counter.items())),
        field_signatures=sorted(field_signatures),
        opcode_ngrams=dict(sorted(opcode_ngram_counter.items())),
        class_dependencies=[
            ClassDependency(source=source, target=target, kind=kind)
            for source, target, kind in sorted(dependency_edges)
        ],
        dependency_shape=build_dependency_shape(internal_classes, dependency_edges)
        if include_members
        else {},
        string_literals=sorted(string_literals),
        api_references=sorted(api_references),
        basic_block_opcode_fingerprints=dict(sorted(basic_block_counter.items())),
        call_chain_opcode_fingerprints=dict(sorted(call_chain_counter.items())),
        class_neighbor_summaries=build_class_neighbor_summaries(
            internal_classes,
            dependency_edges,
        )
        if include_members
        else {},
        field_operation_sequences=dict(sorted(field_operation_counter.items())),
        literal_context_features=sorted(literal_context_features),
    )


def silence_androguard_logging() -> None:
    try:
        from loguru import logger
    except Exception:
        return
    logger.disable("androguard")


def extract_class_descriptors(value: object) -> set[str]:
    if value is None:
        return set()
    if isinstance(value, bytes):
        text = value.decode("utf-8", errors="ignore")
    else:
        text = str(value)
    return set(DESCRIPTOR_PATTERN.findall(text))


def extract_string_literal_from_instruction(
    instruction_name: str,
    instruction_output: object,
) -> str | None:
    if not instruction_name.startswith("const-string"):
        return None
    if instruction_output is None:
        return None

    output = str(instruction_output)
    quote_index = min(
        (index for index in (output.find('"'), output.find("'")) if index >= 0),
        default=-1,
    )
    if quote_index < 0:
        return None

    quote = output[quote_index]
    end_index = output.rfind(quote)
    if end_index <= quote_index:
        return None

    literal = output[quote_index + 1 : end_index]
    literal = literal.encode("utf-8", errors="ignore").decode("unicode_escape", errors="ignore")
    if not is_useful_string_literal(literal):
        return None
    return literal


def extract_api_references_from_instruction(instruction_output: object) -> set[str]:
    if instruction_output is None:
        return set()
    if isinstance(instruction_output, bytes):
        text = instruction_output.decode("utf-8", errors="ignore")
    else:
        text = str(instruction_output)
    return set(API_REFERENCE_PATTERN.findall(text))


def opcode_ngrams_from_sequence(
    opcodes: list[str],
    *,
    n: int = OPCODE_NGRAM_SIZE,
) -> Counter[str]:
    if n <= 0:
        raise ValueError("opcode n-gram size must be positive")
    if len(opcodes) < n:
        return Counter()
    return Counter("|".join(opcodes[index : index + n]) for index in range(len(opcodes) - n + 1))


def basic_block_fingerprints_from_sequence(opcodes: list[str]) -> Counter[str]:
    blocks: list[list[str]] = []
    current: list[str] = []
    for opcode in opcodes:
        current.append(opcode)
        if is_basic_block_boundary_opcode(opcode):
            blocks.append(current)
            current = []
    if current:
        blocks.append(current)
    return Counter(opcode_sequence_fingerprint("bb", block) for block in blocks if block)


def call_chain_fingerprints_from_sequence(opcodes: list[str]) -> Counter[str]:
    calls = [opcode for opcode in opcodes if opcode.startswith(INVOKE_OPCODE_PREFIX)]
    if not calls:
        return Counter()
    return Counter({opcode_sequence_fingerprint("call", calls): 1})


def field_operation_fingerprints_from_sequence(opcodes: list[str]) -> Counter[str]:
    field_ops = [opcode for opcode in opcodes if opcode.startswith(FIELD_OPERATION_PREFIXES)]
    if not field_ops:
        return Counter()
    return Counter({opcode_sequence_fingerprint("fieldops", field_ops): 1})


def is_basic_block_boundary_opcode(opcode: str) -> bool:
    return opcode.startswith(BASIC_BLOCK_BOUNDARY_PREFIXES)


def opcode_sequence_fingerprint(prefix: str, opcodes: list[str]) -> str:
    joined = "|".join(opcodes)
    digest = sha256(joined.encode("utf-8")).hexdigest()[:16]
    return f"{prefix}:{len(opcodes)}:{digest}"


def is_useful_string_literal(value: str) -> bool:
    if not value:
        return False
    if len(value) > STRING_LITERAL_MAX_LENGTH:
        return False
    if len(value.strip()) == 0:
        return False
    return True


def build_dependency_shape(
    classes: set[str],
    edges: set[tuple[str, str, str]],
) -> dict[str, int]:
    in_degree: Counter[str] = Counter({class_name: 0 for class_name in classes})
    out_degree: Counter[str] = Counter({class_name: 0 for class_name in classes})
    kind_counter: Counter[str] = Counter()

    for source, target, kind in edges:
        if source not in classes or target not in classes:
            continue
        out_degree[source] += 1
        in_degree[target] += 1
        kind_counter[f"kind:{kind}"] += 1

    shape: Counter[str] = Counter()
    for value in out_degree.values():
        shape[f"out:{_degree_bucket(value)}"] += 1
    for value in in_degree.values():
        shape[f"in:{_degree_bucket(value)}"] += 1
    shape.update(kind_counter)
    return dict(sorted(shape.items()))


def build_class_neighbor_summaries(
    classes: set[str],
    edges: set[tuple[str, str, str]],
) -> dict[str, int]:
    summaries: Counter[str] = Counter()
    stats: dict[str, Counter[str]] = {class_name: Counter() for class_name in classes}
    for source, target, kind in edges:
        if source not in classes or target not in classes:
            continue
        stats[source][f"out:{kind}"] += 1
        stats[target][f"in:{kind}"] += 1

    kinds = ("extends", "implements", "field", "method-signature")
    for class_name in sorted(classes):
        row = stats[class_name]
        out_total = sum(row[f"out:{kind}"] for kind in kinds)
        in_total = sum(row[f"in:{kind}"] for kind in kinds)
        parts = [
            f"in:{_degree_bucket(in_total)}",
            f"out:{_degree_bucket(out_total)}",
        ]
        parts.extend(f"in-{kind}:{_degree_bucket(row[f'in:{kind}'])}" for kind in kinds)
        parts.extend(f"out-{kind}:{_degree_bucket(row[f'out:{kind}'])}" for kind in kinds)
        summaries["|".join(parts)] += 1
    return dict(sorted(summaries.items()))


def literal_context_feature(class_name: str, method_signature: str, literal: str) -> str:
    package_name = class_descriptor_to_package(class_name) or "<default>"
    payload = f"{package_name}|{method_signature}|{literal}"
    return f"literal-context:{sha256(payload.encode('utf-8')).hexdigest()[:16]}"


def _class_dependency_edges(
    dex_class: object,
    class_name: str,
    internal_classes: set[str],
) -> set[tuple[str, str, str]]:
    edges: set[tuple[str, str, str]] = set()

    superclass = _safe_call(dex_class, "get_superclassname")
    edges.update(_edges_for_descriptors(class_name, superclass, internal_classes, "extends"))

    interfaces = _safe_call(dex_class, "get_interfaces")
    if interfaces:
        for interface in interfaces:
            edges.update(_edges_for_descriptors(class_name, interface, internal_classes, "implements"))

    for field in _safe_iter(_safe_call(dex_class, "get_fields")):
        descriptor = _safe_call(field, "get_descriptor")
        edges.update(_edges_for_descriptors(class_name, descriptor, internal_classes, "field"))

    for method in _safe_iter(_safe_call(dex_class, "get_methods")):
        descriptor = _safe_call(method, "get_descriptor")
        edges.update(
            _edges_for_descriptors(class_name, descriptor, internal_classes, "method-signature")
        )

    return edges


def _edges_for_descriptors(
    source: str,
    value: object,
    internal_classes: set[str],
    kind: str,
) -> set[tuple[str, str, str]]:
    return {
        (source, target, kind)
        for target in extract_class_descriptors(value)
        if target in internal_classes and target != source
    }


def _safe_call(target: object, method_name: str) -> object | None:
    method = getattr(target, method_name, None)
    if method is None:
        return None
    try:
        return method()
    except Exception:
        return None


def _safe_iter(value: object | None) -> list:
    if value is None:
        return []
    if isinstance(value, (str, bytes)):
        return [value]
    try:
        return list(value)
    except TypeError:
        return []


def _degree_bucket(value: int) -> str:
    if value <= 0:
        return "0"
    if value == 1:
        return "1"
    if value <= 3:
        return "2-3"
    if value <= 7:
        return "4-7"
    return "8+"


def analyze_apk_dex(apk_path: str | Path, *, include_members: bool = False) -> ApkDexAnalysis:
    path = Path(apk_path)
    if not path.exists():
        raise FileNotFoundError(f"APK not found: {path}")
    if not path.is_file():
        raise ValueError(f"APK path is not a file: {path}")

    dex_features: list[DexFileFeatures] = []
    parse_errors: list[DexParseError] = []
    package_names: set[str] = set()
    opcode_counter: Counter[str] = Counter()
    opcode_ngram_counter: Counter[str] = Counter()
    basic_block_counter: Counter[str] = Counter()
    call_chain_counter: Counter[str] = Counter()
    class_neighbor_counter: Counter[str] = Counter()
    field_operation_counter: Counter[str] = Counter()
    literal_context_features: set[str] = set()

    with zipfile.ZipFile(path) as apk_zip:
        names = normalized_zip_names(apk_zip.namelist())
        dex_files = [name for name in names if DEX_PATTERN.match(Path(name).name)]

        for dex_file in dex_files:
            try:
                features = analyze_dex_bytes(
                    dex_file,
                    apk_zip.read(dex_file),
                    include_members=include_members,
                )
            except Exception as exc:
                parse_errors.append(DexParseError(dex_file=dex_file, error=str(exc)))
                continue

            dex_features.append(features)
            package_names.update(features.packages)
            opcode_counter.update(features.opcode_histogram)
            opcode_ngram_counter.update(features.opcode_ngrams)
            basic_block_counter.update(features.basic_block_opcode_fingerprints)
            call_chain_counter.update(features.call_chain_opcode_fingerprints)
            class_neighbor_counter.update(features.class_neighbor_summaries)
            field_operation_counter.update(features.field_operation_sequences)
            literal_context_features.update(features.literal_context_features)

    return ApkDexAnalysis(
        apk_path=str(path),
        dex_files_analyzed=len(dex_features),
        dex_files_failed=len(parse_errors),
        classes_count=sum(features.classes_count for features in dex_features),
        methods_count=sum(features.methods_count for features in dex_features),
        packages=sorted(package_names),
        opcode_histogram=dict(sorted(opcode_counter.items())),
        opcode_ngrams=dict(sorted(opcode_ngram_counter.items())),
        dex_files=dex_features,
        parse_errors=parse_errors,
        basic_block_opcode_fingerprints=dict(sorted(basic_block_counter.items())),
        call_chain_opcode_fingerprints=dict(sorted(call_chain_counter.items())),
        class_neighbor_summaries=dict(sorted(class_neighbor_counter.items())),
        field_operation_sequences=dict(sorted(field_operation_counter.items())),
        literal_context_features=sorted(literal_context_features),
    )
