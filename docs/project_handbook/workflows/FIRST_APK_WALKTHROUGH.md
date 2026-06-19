# First APK Walkthrough

This walkthrough lets you observe each pipeline layer. Replace `APP.apk` with a
real path.

```powershell
$apk = "data/test_apks/sample.apk"
$db = "data/reference_db/reference_features_calibrated_combined.sqlite"
$out = "data/results/handbook-first-run"
```

## 1. Check the environment

```powershell
docker compose run --rm apk-sbom python scripts/check_toolchain.py
```

Expected: Python and core packages are available; D8/Android tools are present
inside Docker. Optional scanners may be reported separately.

## 2. Inspect the APK container

```powershell
docker compose run --rm apk-sbom python -m apk_sbom.cli inspect-apk $apk
```

Look for:

- APK SHA-256;
- `classes*.dex` list and multidex status;
- manifest package/version/SDK;
- native `.so` files and ABIs;
- suspicious nonstandard DEX or extraction-risk indicators.

This step does not claim any Maven component.

## 3. Analyze DEX evidence

```powershell
docker compose run --rm apk-sbom python -m apk_sbom.cli analyze-dex $apk
```

Look for nonzero package/class/method counts and any DEX parse errors. Compare
the number of DEX files with the inspection output.

## 4. Rank candidates

```powershell
docker compose run --rm apk-sbom python -m apk_sbom.cli match-apk $apk `
  --db-path $db --top 10 --min-score 0.05
```

For each candidate, inspect:

- coordinate and version;
- total score;
- class/method/package evidence;
- structural, literal, and version-unique signals;
- identity versus version confidence;
- ambiguous alternatives.

Do not read “rank 1” as automatically confirmed.

## 5. Run a focused diagnostic

If a coordinate is already known for learning purposes:

```powershell
docker compose run --rm apk-sbom python -m apk_sbom.cli match-apk $apk `
  --db-path $db --coordinate com.google.code.gson:gson --top 10
```

This answers “which stored Gson version best matches?” It does not prove that an
unconstrained detector independently discovered Gson.

## 6. Generate the full offline report

```powershell
docker compose run --rm apk-sbom python -m apk_sbom.cli generate-report $apk `
  --output-dir $out --db-path $db --top 30 --skip-osv
```

Open:

- `$out/report.html` for the visual result;
- `$out/report.md` for readable evidence;
- `$out/report.json` and `$out/matches.json` for details;
- `$out/sbom.cdx.json` for the standard SBOM.

## 7. Add OSV when needed

Either rerun without `--skip-osv`, or scan the existing SBOM:

```powershell
docker compose run --rm apk-sbom python -m apk_sbom.cli scan-sbom-osv `
  "$out/sbom.cdx.json" --output "$out/osv-vulnerabilities.json"
```

OSV requires network access. A vulnerability result is only as certain as its
component and exact-version evidence.

## 8. Validate against source, if available

```powershell
docker compose run --rm apk-sbom python -m apk_sbom.cli validate-source-deps `
  --sbom "$out/sbom.cdx.json" `
  --dependency-tree "path/to/runtimeClasspath.txt" `
  --output-dir "$out/source-validation"
```

Remember: this validates emitted rows. It does not measure all-source
dependency recall by itself.

## Questions to answer after the exercise

1. Was the APK multidex or native-heavy?
2. Which feature family dominated the top candidate?
3. Was identity stronger than exact-version confidence?
4. Did the SBOM omit uncertain candidates?
5. Would a weak version claim change the CVE conclusion?
