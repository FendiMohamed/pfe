# Evaluation Plan

## Evaluation Questions

| Question | Why it matters |
|---|---|
| Can the MVP detect known libraries in compiled APKs? | Basic library-level usefulness. |
| Can it identify versions? | SBOM and CVE lookup require versions. |
| How does obfuscation affect results? | Obfuscation is central in Android TPL detection papers. |
| Does confidence prevent false exact-version claims? | Important for honest security reporting. |
| Is the generated SBOM scanner-compatible? | Shows practical value beyond academic detection. |

## Dataset Strategy

Start with controlled APKs:

- Build small Android apps with known dependencies.
- Include several versions of selected libraries.
- Build clear and obfuscated variants.

Suggested variants:

```text
clear debug/release build
ProGuard/R8 rename only
R8 shrink
R8 shrink + optimize
```

Optional later:

- F-Droid/open-source APKs with known Gradle dependencies.
- Real APKs from a public dataset if available and legally allowed.

## Baselines

Use simple baselines first:

| Baseline | Purpose |
|---|---|
| Package-name matching | Shows why names are fragile. |
| Class-name overlap | Simple structural baseline. |
| File/hash matching | Shows why exact hashes fail after shrinking/rebuilds. |
| LibScout if easy to run | Useful research baseline, but not required for first MVP. |

## Metrics

Library-level:

- precision
- recall
- F1

Version-level:

- exact-version accuracy
- version-level precision/recall/F1
- top-k accuracy
- uncertain/range rate

SBOM:

- component completeness
- PURL correctness
- valid CycloneDX output
- vulnerability lookup success

Runtime:

- analysis time per APK
- reference DB size

## Expected Limitations

- Heavy R8 method inlining may reduce method/opcode matching.
- Adjacent versions may be indistinguishable when code differences are tiny.
- Libraries absent from the reference DB cannot be identified confidently.
- Native `.so` versions are not fully solved in the first MVP.
- Packed/encrypted APKs and dynamic loading are out of scope.

