# R8, Obfuscation, and Uncertainty

## What R8 does

R8 combines shrinking, optimization, obfuscation, and bytecode rewriting:

- removes unreachable classes and methods;
- renames classes, methods, and fields;
- inlines methods;
- merges or rewrites classes;
- changes instruction sequences;
- can flatten or repackage namespaces.

Each transformation attacks a different detector assumption. Renaming damages
name signatures; shrinking damages completeness; inlining damages method
boundaries; optimization damages opcode sequences.

## Why exact versions are harder than identity

Large portions of a library may remain unchanged between adjacent releases.
After R8 removes the few changed or unused methods, two versions can become
observationally identical inside the APK.

The correct output may therefore be:

```text
identity: androidx.fragment:fragment
identity confidence: high
exact version: ambiguous between 1.6.1 and 1.6.2
```

This is more truthful than forcing a precise version.

## Project uncertainty model

The project separates:

- identity confidence;
- version confidence;
- decision status;
- alternative or ambiguous versions;
- vulnerability certainty.

Uncertain components are excluded by default from final SBOM emission unless
`--include-uncertain` is requested.

## R8 research phases

The project progressed from inert diagnostics to scoped experiments, report
wording, structural gates, and AI triage. The rule throughout was: do not alter
production matching until a candidate improves targets without regressing
controls.

Several promising techniques remained report-only because they used source
information, failed APK-only promotion, or did not beat a simple baseline.

## Practical interpretation

- High class/method overlap can indicate a clear unmodified library.
- Low name overlap with strong opcode/literal/dependency evidence can indicate
  an R8-affected identity candidate.
- A narrow score margin between adjacent versions indicates version ambiguity.
- A reference absence is not proof that the library is absent from the APK.

## Evidence

- [R8 method selection](../../research/R8_OBFUSCATION_METHOD_SELECTION.md)
- [AI/R8 method selection](../../research/AI_R8_ASSISTED_METHOD_SELECTION.md)
- [AI/R8 integration gate](../../evaluation/AI_R8_MVP_INTEGRATION_GATE.md)
- [R8 APK structural gate](../../evaluation/R8_APK_STRUCTURAL_PROMOTION_GATE.md)
- [Failed experiments](../evaluation/FAILED_EXPERIMENTS.md)
