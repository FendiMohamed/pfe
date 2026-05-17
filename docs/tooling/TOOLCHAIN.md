# Toolchain

## Tool Choices

| Tool | Role | Why chosen | Main limitation |
|---|---|---|---|
| Python | Main implementation language. | Fast prototyping, good libraries, easy JSON/API/SQLite integration. | Slower than lower-level languages for huge analysis. |
| Python `zipfile` | Raw APK extraction. | APK is a ZIP archive. Simple and reliable for extracting DEX/native files. | Does not decode binary XML/resources. |
| Apktool | Manifest/resources decoding. | Decodes binary XML and resources. | Can be slower and may fail on protected APKs. |
| Androguard | APK/DEX parsing. | Python Android analysis library for classes, methods, opcodes, references. | May be slow or imperfect on unusual APKs. |
| JADX | Manual inspection. | Helps verify decompiled code during debugging. | Not the automated core. |
| Maven Central | Reference library source. | Main ecosystem for Java/Kotlin/Android libraries. | Only covers libraries we download. |
| Android D8 | Convert JAR/AAR to DEX. | Official Android dexer; makes references comparable to APK DEX. | Requires Android build tools setup. |
| SQLite | Local feature DB. | Reproducible, simple, no server needed. | Not ideal for very large-scale indexing. |
| NetworkX | Class dependency graphs. | Easy graph construction and experiments in Python. | Not optimized for massive graphs. |
| scikit-learn | Optional similarity utilities. | Useful for cosine similarity or nearest-neighbor experiments. | Heavy ML is not required for first MVP. |
| CycloneDX JSON | SBOM output. | Standard, scanner-compatible, supports PURL and metadata. | We must generate reliable component evidence. |
| cyclonedx-cli | SBOM validation. | Validates generated BOMs. | Extra dependency. |
| OSV API | Primary vulnerability lookup. | Package/version-oriented, good for Maven/PURL. | Coverage may differ from NVD/GitHub/Sonatype. |
| NVD API | Optional CVE enrichment. | Official CVE/CVSS data source. | Maven-to-CPE mapping is hard. |
| Trivy | Optional SBOM scanner. | Common scanner that can scan SBOMs. | Depends on correct SBOM identity/version. |
| Grype | Optional SBOM scanner. | Good second scanner for comparison. | Depends on correct SBOM identity/version. |
| R8 / ProGuard | Obfuscation evaluation. | Realistic Android obfuscation/shrinking tools. | Heavy R8 remains hard to handle perfectly. |
| Obfuscapk | Optional obfuscation tests. | Black-box APK obfuscation. | Extra setup; not essential for first evaluation. |

## Install/Check Commands To Use Later

These commands are examples; verify paths on the actual machine before using.

```powershell
python --version
java -version
apktool --version
jadx --version
trivy --version
grype version
cyclonedx --version
```

For Python dependencies, the first likely set is:

```text
androguard
networkx
requests
packaging
pydantic
rich
pytest
```

Optional later:

```text
scikit-learn
rapidfuzz
cyclonedx-python-lib
```

## Reuse vs Build

Reuse:

- APK archive extraction
- DEX parsing
- graph utilities
- SBOM validation
- vulnerability APIs
- external scanners

Build ourselves:

- feature schema
- candidate generation
- segmentation strategy
- matching and version scoring
- confidence and evidence reporting
- final APK-to-SBOM workflow

## Current Toolchain Audit

Audit date: 2026-05-18.

No tools were installed during this audit.

### Host Tools

| Tool | Status | Details |
|---|---|---|
| Python | Available | `Python 3.12.0` at `C:\Python312\python.exe`. |
| pip | Available | `pip 23.2.1`. |
| Git | Available | Git 2.42.0.windows.2. Repository initialized on branch `main`; workspace added as a safe directory because of Windows owner SID mismatch. |
| Java | Available | Java 17.0.12 LTS at `C:\Program Files\Java\jdk-17\bin\java.exe`. |
| Docker CLI | Available | Docker CLI 27.5.1. |
| Docker Compose | Available | Docker Compose v2.32.4-desktop.1. |
| Docker daemon | Not reachable | `docker info` cannot connect to Docker engine; likely Docker Desktop is not running or access/elevation is needed. |
| Android SDK / D8 | Missing from PATH | `d8` not found; common Android SDK build-tools folders were not found in the checked locations. |
| Apktool | Missing from PATH | Needed later for decoded manifest/resources. |
| JADX | Missing from PATH | Useful later for manual inspection, not required for first extraction module. |
| Trivy | Missing from PATH | Optional later SBOM scanner. |
| Grype | Missing from PATH | Optional later SBOM scanner. |
| cyclonedx-cli | Missing from PATH | Useful later for SBOM validation. |

### Python Packages On Host Python

| Package | Status |
|---|---|
| androguard | Missing |
| networkx | Missing |
| requests | Missing |
| packaging | Missing |
| pydantic | Missing |
| rich | Missing |
| pytest | Missing |
| scikit-learn | Missing |
| rapidfuzz | Missing |
| cyclonedx-python-lib / `cyclonedx` module | Missing |

### Audit Conclusion

The Windows host has enough base tooling to start the Docker-based route. Docker Desktop/daemon access required elevated execution from this environment, but the container build now works. The first Docker environment installs the Python packages and CLI dependencies instead of polluting the Windows host.

Immediate next setup tasks:

1. Keep Apktool, D8, Trivy/Grype, and cyclonedx-cli optional at first if they slow down the initial extractor milestone.
2. Use Docker for Androguard-based DEX extraction.
3. Add D8 later when implementing the Maven reference DB converter.

## Docker Runtime Setup

Created files:

- `Dockerfile`
- `docker-compose.yml`
- `requirements.txt`
- `.dockerignore`
- `scripts/check_toolchain.py`

Host-verified commands:

```powershell
docker compose config
$env:PYTHONPATH='src'; python -m apk_sbom.cli --help
python scripts/check_toolchain.py
python -m compileall src scripts tests
```

The Compose file is syntactically valid, but Docker emits warnings because `C:\Users\PC CABA DZ\.docker\config.json` is not accessible. The Docker daemon was also not reachable during `docker info`.

Docker runtime was built successfully with:

```powershell
docker compose build --progress=plain
docker compose run --rm apk-sbom python scripts/check_toolchain.py
```

Container toolchain status:

| Tool/package | Container status |
|---|---|
| Python | Available, 3.12.13 |
| Java | Available, OpenJDK 21 |
| androguard | Available |
| networkx | Available |
| requests | Available |
| packaging | Available |
| pydantic | Available |
| rich | Available |
| pytest | Available |
| Apktool | Missing, optional for now |
| JADX | Missing, optional/manual host tool later |
| D8 | Missing, needed later for reference DB conversion |
| Trivy/Grype | Missing, optional later |
| cyclonedx-cli | Missing, optional later |

Container tests:

```powershell
docker compose run --rm apk-sbom pytest -q
```

Result: `3 passed`.

## First CLI Slice

Implemented command:

```powershell
$env:PYTHONPATH='src'
python -m apk_sbom.cli inspect-apk path\to\sample.apk
```

Current output includes:

- APK path, size, and SHA-256
- list of all `classes*.dex`
- `has_multidex`
- manifest presence
- `resources.arsc` presence
- native libraries under `lib/<abi>/*.so` with ABI, filename, size, and SHA-256

The archive inspection command uses only Python's standard library.

## Minimal DEX Feature Slice

Implemented command:

```powershell
$env:PYTHONPATH='src'
python -m apk_sbom.cli analyze-dex path\to\sample.apk
```

Current output includes:

- number of DEX files analyzed
- number of DEX files that failed parsing
- total class count
- total method count
- recovered package names
- aggregate opcode histogram
- per-DEX feature summaries
- parse errors for invalid or unsupported DEX files

This slice uses Androguard inside the Docker runtime. The command records DEX parse failures explicitly instead of silently dropping them.
