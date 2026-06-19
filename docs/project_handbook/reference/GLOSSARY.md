# Glossary

**AAR**
Android Archive. May contain `classes.jar`, resources, manifest fragments, and
native files.

**ABI**
Native CPU architecture such as `arm64-v8a` or `x86_64`.

**Ambiguous version**
An alternative release whose evidence is too close to the selected version for
a safe exact claim.

**APK**
Installable Android application package.

**API reference**
A DEX reference to a type, method, or field used by code.

**Basic block**
A straight-line instruction region with one entry and one exit; used in
structural diagnostics.

**BOM**
Bill of Materials. In Maven/Gradle, a dependency version platform; in security,
SBOM means Software Bill of Materials.

**Candidate**
A reference coordinate/version being compared with APK evidence.

**CDG / dependency graph**
Class dependency graph or related structural representation.

**Confirmed emitted version**
An emitted Maven coordinate/version that matches supplied source evidence.

**Coordinate**
Maven `group:artifact`, for example `com.google.code.gson:gson`.

**CVE**
Common Vulnerabilities and Exposures identifier.

**CycloneDX**
The SBOM standard emitted by the project.

**D8**
Android tool that converts Java bytecode into DEX.

**DEX**
Dalvik Executable bytecode used by Android Runtime.

**Emitted-version confirmation rate**
Confirmed emitted Maven rows divided by all emitted Maven rows checked against
source. It is not full dependency recall.

**EPSS**
Exploit Prediction Scoring System.

**Exact source recall**
Source dependencies emitted with the exact source version divided by all
source dependency rows.

**Feature family**
A kind of comparable evidence: classes, methods, opcodes, literals, dependency
edges, APIs, and so on.

**Ground truth**
External expected evidence, such as a controlled fixture configuration or a
resolved source dependency tree.

**Identity confidence**
Confidence that a library coordinate/family is present, independent of exact
version certainty.

**JAR**
Java Archive containing JVM class files and resources.

**KEV**
CISA Known Exploited Vulnerabilities catalog.

**Literal context**
A string constant together with surrounding method/class evidence.

**Matcher**
The component that ranks reference releases against APK features.

**Maven PURL**
Normalized package URL such as
`pkg:maven/com.google.code.gson/gson@2.10.1`.

**Multidex**
An APK containing more than one DEX file.

**No-Maven signal**
A source-backed APK for which the matcher emits no ordinary Maven component;
used as a false-positive control.

**Opcode**
A bytecode instruction operation. Histograms and n-grams summarize behavior.

**OSV**
Open Source Vulnerabilities API used for ecosystem-aware advisory lookup.

**Partial APK**
A source-validated real APK with useful confirmations plus explicit mismatch or
missing evidence.

**POM**
Maven Project Object Model metadata.

**Promotion gate**
Target/control criteria that an experiment must pass before changing defaults.

**Reference coverage**
How many source coordinates or exact coordinate/version rows exist in the
reference DB.

**R8**
Android shrinker, optimizer, obfuscator, and bytecode rewriter.

**Report-only**
Evidence shown to a user but forbidden from changing selected versions, SBOM
components, CVE labels, or official metrics.

**SBOM**
Software Bill of Materials.

**Source-known lane**
Evaluation in which source coordinate/version knowledge constrains candidates;
an upper-bound diagnostic, not unconstrained APK-only accuracy.

**TPL**
Third-party library.

**Version confidence**
Confidence in the exact selected release after identity is considered.

**Version-unique evidence**
Features present in one stored version but not its siblings.
