# APK, DEX, and Android Bytecode Basics

## APK

An APK is a ZIP-compatible application package. It commonly contains:

- `AndroidManifest.xml`: binary Android manifest;
- `classes.dex`, `classes2.dex`, ...: Dalvik/ART bytecode;
- `lib/<abi>/*.so`: native libraries;
- resources and assets;
- signing metadata.

The project reads the APK without installing or executing it.

## DEX

DEX is the bytecode format executed by Android Runtime. A DEX file contains
classes, fields, methods, instructions, string constants, and references to
other types and APIs.

Java or Kotlin dependencies are usually compiled into the application's DEX
files. Their original JAR/AAR boundary is not preserved. Detection therefore
tries to find a known library's surviving evidence inside a larger merged DEX
universe.

## Multidex

Large APKs contain several DEX files. The extractor collects standard
`classes*.dex` entries and also records suspicious nonstandard DEX locations.
All discovered DEX evidence contributes to the app-level feature set.

## Manifest decoding

APK manifests use Android's binary XML format. The extractor uses Androguard
to decode package name, version, SDK information, components, and permissions.
Manifest information provides context; it is not enough to identify embedded
Maven versions.

## Native libraries

Native `.so` files are hashed and emitted as file components. A hash proves the
exact bytes observed, but without a trusted native reference catalog it does
not prove a package name or version. The project keeps this as an explicit
boundary instead of inventing Maven coordinates.

## Static-analysis boundaries

Static APK inspection may miss:

- code downloaded at runtime;
- encrypted or packed secondary payloads;
- reflection targets not visible in simple references;
- server-side behavior;
- source dependencies removed completely by shrinking.

## Code to read

- [apk_extractor.py](../../../src/apk_sbom/apk_extractor.py)
- [dex_analyzer.py](../../../src/apk_sbom/dex_analyzer.py)
- [models.py](../../../src/apk_sbom/models.py)

Use `inspect-apk` to see archive-level evidence and `analyze-dex` to see
bytecode feature counts.
