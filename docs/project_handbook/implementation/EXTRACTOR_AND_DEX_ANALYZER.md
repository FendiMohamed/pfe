# APK Extractor and DEX Analyzer

## APK extractor

Primary file: [apk_extractor.py](../../../src/apk_sbom/apk_extractor.py)

`inspect_apk()` performs archive-level inspection:

1. validates and opens the APK as a ZIP archive;
2. computes the APK SHA-256;
3. discovers standard and nonstandard DEX entries;
4. records native `.so` files with ABI, size, and hash;
5. decodes binary manifest metadata;
6. builds forensic indicators.

Important output models include `ApkInspection`, `ManifestMetadata`,
`NativeLibrary`, and `ApkForensicSummary`.

### Forensic indicators

Indicators are observations, not malware verdicts. Examples include:

- DEX outside normal `classes*.dex` paths;
- unusually small primary DEX;
- names associated with packers or protectors;
- large opaque assets;
- an APK dominated by native code.

They help explain why ordinary static matching may be incomplete.

## DEX analyzer

Primary file: [dex_analyzer.py](../../../src/apk_sbom/dex_analyzer.py)

`analyze_dex_bytes()` parses one DEX. `analyze_apk_dex()` aggregates all DEX
files in an APK.

### Extracted features

- package names;
- class descriptors;
- method and field signatures;
- opcode histograms;
- opcode tri-grams;
- string literals;
- invoked API/member references;
- extends, implements, field-type, and method-signature dependency edges;
- dependency-shape summaries;
- basic-block, call-chain, class-neighbor, field-operation, and literal-context
  diagnostics.

### Why `include_members` exists

Member-level extraction is more expensive and creates larger artifacts. Some
commands only need summary counts; reference construction and detailed matching
need richer members.

### Error handling

One malformed DEX should be reported as parse evidence rather than silently
inventing an empty APK. Check parse errors in the JSON output before trusting a
zero-feature result.

## How to inspect the layers

```powershell
docker compose run --rm apk-sbom python -m apk_sbom.cli inspect-apk path/to/app.apk
docker compose run --rm apk-sbom python -m apk_sbom.cli analyze-dex path/to/app.apk
```

`inspect-apk` answers “what files and metadata are present?” `analyze-dex`
answers “what comparable bytecode evidence was recovered?”

## Common misunderstandings

- A class count is not a library count.
- A package name is not necessarily a Maven coordinate.
- Missing source code after shrinking is not an analyzer parsing failure.
- Native hashes are useful evidence but do not automatically provide versions.
