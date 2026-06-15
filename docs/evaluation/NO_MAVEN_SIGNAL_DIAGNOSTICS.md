# No-Maven-Signal Diagnostics

Generated from `data/results/evaluation/real-apk-source-validation-dashboard.json`.

## Summary

| Metric | Count |
|---|---:|
| No-Maven-signal cases | 4 |
| True no-signal controls | 0 |
| Identity-coverage miss controls | 3 |
| Forked-library boundary cases | 1 |

## Cases

| APK | Classification | Source coords | Candidate coords | Overlap | Top candidate | Top overlap | Lane |
|---|---|---:|---:|---:|---|---|---|
| Privacy Browser 3.20.1 | identity-coverage-miss | 87 | 5 | 5/5 | `androidx.swiperefreshlayout:swiperefreshlayout:1.0.0` (`0.371413`) | `androidx.swiperefreshlayout:swiperefreshlayout:1.0.0` (`0.371413`) | Browser/WebView AndroidX diagnostic |
| Mastodon 2.12.3 | forked-library-boundary | 20 | 3 | 1/3 | `androidx.recyclerview:recyclerview:1.2.1` (`0.288090`) | `com.google.code.gson:gson:2.8.9` (`0.266870`) | me.grishka.litex fork-family/reference audit plus weak Gson check |
| monocles browser 1.9.3 | identity-coverage-miss | 84 | 5 | 5/5 | `androidx.swiperefreshlayout:swiperefreshlayout:1.0.0` (`0.369899`) | `androidx.swiperefreshlayout:swiperefreshlayout:1.0.0` (`0.369899`) | Browser/WebView AndroidX diagnostic |
| Blue Square Speedometer 1.1.0 | identity-coverage-miss | 54 | 5 | 4/5 | `androidx.startup:startup-runtime:1.1.1` (`0.359615`) | `androidx.startup:startup-runtime:1.1.1` (`0.359615`) | Small-app AndroidX diagnostic |

## Notes

- Rows remain outside emitted-version accuracy metrics until a controlled experiment emits source-confirmed components.
- Candidate overlap means the source runtime tree and APK report candidate list share a Maven coordinate family.
- Mastodon is kept separate because source uses `me.grishka.litex:*` forked UI-library coordinates.
