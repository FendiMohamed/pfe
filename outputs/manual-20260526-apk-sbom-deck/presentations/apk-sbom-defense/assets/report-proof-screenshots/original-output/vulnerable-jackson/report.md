# APK SBOM Recovery Report

## APK

- Path: `data/test_apks/controlled-com-fasterxml-jackson-core-jackson-databind-2.9.10.8-clear.apk`
- SHA-256: `604a9833ccd276362c2dd3685ad66b70a6c6cf9bb59b4fe55377639c4dc12e58`
- Package name: `com.example.fixture`
- Version: `unknown` / code `unknown`
- SDK range: min `unknown` / target `unknown`
- Manifest parse status: parsed
- DEX files: 1
- Multidex: false
- Native libraries: 0
- Extraction risk: low
- Obfuscation risk: low (0.20)

## Detection Summary

- DEX files analyzed: 1
- DEX files failed: 0
- Detected Maven components: 1
- Native file components: 0
- Vulnerability findings: 3 (3 confirmed, 0 potential)

## APK Forensic Summary

- ZIP entries: 3
- Standard DEX files: `classes.dex`
- Nonstandard DEX files: none
- Native ABIs: none
- Permissions: none

No extraction indicators were raised.

## Obfuscation Risk

- Level: low
- Score: 0.20
- Reason: Structural evidence is stronger than package-name evidence.

## Detected Components

| Component | Version | Candidate reasons | Identity confidence | Version confidence | Match type | Vulnerabilities |
|---|---:|---|---|---|---|---|
| `com.fasterxml.jackson.core:jackson-databind` | 2.9.10.8 | package, class, method, opcode, graph, literals, version-unique | confirmed/high (1.000) | exact/high (1.000) | hybrid-exact | 3 confirmed |

## Native Libraries

No native `.so` files were found in the APK.

## Version Decisions

| Component | Selected version | Identity | Version | Score | Gap | Alternatives |
|---|---:|---|---|---:|---:|---|
| `com.fasterxml.jackson.core:jackson-databind` | 2.9.10.8 | confirmed/high (1.000) | exact/high (1.000) | 1.000 | 0.183 | 2.12.7.1 (0.817), 2.13.5 (0.802), 2.15.2 (0.755) |
| `com.google.code.gson:gson` | 2.8.5 | uncertain/uncertain (0.146) | uncertain/uncertain (0.161) | 0.161 | 0.015 | 2.8.6 (0.146), 2.8.9 (0.146) |
| `com.squareup.retrofit2:retrofit` | 2.8.1 | uncertain/uncertain (0.133) | uncertain/uncertain (0.137) | 0.137 | 0.000 | 2.9.0 (0.137) |
| `com.squareup.okhttp3:okhttp` | 4.8.0 | uncertain/uncertain (0.125) | uncertain/uncertain (0.130) | 0.130 | 0.000 | 4.9.0 (0.130), 4.9.1 (0.130), 4.12.0 (0.130) |
| `com.squareup.okio:okio-jvm` | 3.7.0 | uncertain/uncertain (0.124) | uncertain/uncertain (0.127) | 0.127 | 0.000 | 3.6.0 (0.127), 3.0.0 (0.125) |
| `commons-codec:commons-codec` | 1.15 | uncertain/uncertain (0.119) | uncertain/uncertain (0.125) | 0.125 | 0.001 | 1.16.1 (0.124), 1.16.0 (0.124) |
| `io.ktor:ktor-client-core-jvm` | 2.3.12 | uncertain/uncertain (0.119) | uncertain/uncertain (0.124) | 0.124 | 0.124 | none |
| `com.squareup.okio:okio` | 2.9.0 | uncertain/uncertain (0.119) | uncertain/uncertain (0.123) | 0.123 | 0.000 | 2.8.0 (0.122) |
| `io.ktor:ktor-http-jvm` | 2.3.12 | uncertain/uncertain (0.115) | uncertain/uncertain (0.119) | 0.119 | 0.119 | none |
| `io.ktor:ktor-utils-jvm` | 2.3.12 | uncertain/uncertain (0.114) | uncertain/uncertain (0.119) | 0.119 | 0.119 | none |
| `io.ktor:ktor-io-jvm` | 2.3.12 | uncertain/uncertain (0.112) | uncertain/uncertain (0.117) | 0.117 | 0.117 | none |
| `io.ktor:ktor-client-okhttp-jvm` | 2.3.12 | uncertain/uncertain (0.098) | uncertain/uncertain (0.107) | 0.107 | 0.107 | none |

## Vulnerabilities

| Component | Version | Finding confidence | Severity | Advisory | Aliases | Summary |
|---|---:|---|---|---|---|---|
| `com.fasterxml.jackson.core:jackson-databind` | 2.9.10.8 | confirmed | HIGH | `GHSA-57j2-w4cx-62h2` | CVE-2020-36518 | Deeply nested json in jackson-databind |
| `com.fasterxml.jackson.core:jackson-databind` | 2.9.10.8 | confirmed | HIGH | `GHSA-jjjh-jjxp-wpff` | CVE-2022-42003 | Uncontrolled Resource Consumption in Jackson-databind |
| `com.fasterxml.jackson.core:jackson-databind` | 2.9.10.8 | confirmed | HIGH | `GHSA-rgv9-q543-rqg4` | CVE-2022-42004 | Uncontrolled Resource Consumption in FasterXML jackson-databind |

## Artifacts

- Match details: `data/results/demo-osv-vulnerable-jackson-databind/matches.json`
- CycloneDX SBOM: `data/results/demo-osv-vulnerable-jackson-databind/sbom.cdx.json`
- JSON report: `data/results/demo-osv-vulnerable-jackson-databind/report.json`
- Markdown report: `data/results/demo-osv-vulnerable-jackson-databind/report.md`
- HTML report: `data/results/demo-osv-vulnerable-jackson-databind/report.html`
- OSV results: `data/results/demo-osv-vulnerable-jackson-databind/osv-vulnerabilities.json`

## Limitations

- This MVP only detects libraries present in the local Maven reference DB.
- Heavy R8 optimization, reflection, packed APKs, encrypted DEX, and dynamic loading remain limited or unsupported.
- Native `.so` files are hashed, but native component version identification is not implemented in the first MVP.
