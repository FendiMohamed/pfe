# Next Real APK Growth Queue

This queue keeps real APK growth category-driven. Do not admit a real APK into source-validated metrics until the APK hash, source tag/commit, resolved dependency tree, generated report, and source-validation output are present. Smoke and limitation APKs may be useful without full ground truth, but they must stay out of precision/recall/version-accuracy metrics.

Post-100 optimization is now governed by `docs/planning/RESEARCH_BACKED_REAL_APK_OPTIMIZATION_PLAN.md`: rescue the two current source-linked blockers first, then audit no-Maven-signal rows, boundary rows, wrong-version rows, missing-source rows, guarded reference DB growth, and dashboard history in that order.

## Current Position

| Area | Current evidence | Gap |
|---|---|---|
| Clean source-validated real APKs | F-Droid, OpenTracks, Tusky, Daily Dozen, QuickDic | Need more non-sparse clean APKs; Tusky, Daily Dozen, and QuickDic are clean but sparse. |
| Partial source-validated real APKs | 95 partial rows, including NewPipe, AntennaPod, KDE Connect, Wikipedia, Conversations, Aegis, Markor, Nextcloud, FairEmail, VLC, OsmAnd, Material Files, Jitsi Meet, K-9 / Thunderbird Android, the low-risk/no-native rows, clean-candidate sweeps, v12 Password Generator/Todo Agenda/Keep it up/c3nav, v13 OpenTopoMap Viewer/Railway station photos/LinkDroid/Quasseldroid, v14 Bimba/wX/Egyptian Writer/Smouldering Durtles/DNS Hero/Baby Books/Odysee/RadarWeather, v15 Clock/Poet Assistant/Ultrasonic/FTPClient/RunnerUp/Json List/ImapNotes3/Forecastie, v16 OceanNex/Praktika Vortaro/MsgGo/AF Weather Widget/Study Tracker/Calliope mini/F-Droid Build Status/Password Master/Todo List (PFA), and blocker rescues. | Good diversity and the source-validated real APK set has now reached 100 total real APKs. The clean non-sparse bucket is still open, so future rows should improve quality/diversity or unblock current source-linked rows rather than only increasing count. |
| Source-linked blocked APKs | Flying Carpet and FitoTrack. | Both have APK/source/report evidence from v16 but no resolved runtime dependency tree yet, so they stay out of source-validated metrics. Try targeted Gradle/toolchain rescue before admission. |
| Native / `.so` boundary | Organic Maps, Termux, VLC, OsmAnd, Material Files, Jitsi | Strong boundary evidence; still no native package/version recovery claim. |
| Heavy obfuscation / protected | Hidden-DEX fixture, Termux-style limitation evidence, Simplify obfuscated sample | Commercial protected/packed APKs remain future work, but one legal public obfuscated APK sample now covers normal-layout obfuscation as limitation evidence. |
| Modern framework boundary | Jitsi Meet for React Native is now source-validated partial; native React Native/WebRTC/Hermes files remain hash-only boundary evidence. | Need Flutter and Unity-style cases, likely limitation/smoke first. |
| Category-balanced smoke/report batch | LocalSend, OpenVPN for Android, KeePassDX, Gadgetbridge, DAVx5, Shelter, TheXTech, Fennec F-Droid | Collected with SHA-256 verification and calibrated no-OSV reports in `docs/evaluation/REAL_APK_GROWTH_BATCH_V2.md`; still excluded from source-validated metrics. |
| Low-risk/no-native preflight and clean-candidate batches | Stopwatch, Bubble, Audio Source, Blue Square Speedometer, Gotify, BetterCounter, Coffee, MedTimer, Doodle, Simple Time Tracker, KeePassVault, Daily Dozen, Privacy Browser, Cryptomator Lite, Easy Xkcd, MoneyWallet, Foxy Droid, QuickDic, Cirrus, AFWall+, Loop Habit Tracker, yetCalc, Broccoli, LibreTube, Retro Music, microMathematics Plus, Diaguard, Fulguris Web Browser, Working Time Account, AndStatus, I2P, Mastodon, Drift // Audio, JaMuz, monocles browser, DoliDroid, ownCloud, Your local weather, OpenKeychain, HomeFeed - RSS Widget, Etar - OpenSource Calendar, RadioDroid, SimpleLogin, Omni Notes, Primitive FTPd, floccus bookmark sync, Waistline, OpenCloud, NightDream, SambaLite, Password Generator, Todo Agenda, Keep it up, c3nav, OpenTopoMap Viewer, Railway station photos, LinkDroid for Linkwarden, Quasseldroid, Bimba, wX, Egyptian Writer, Smouldering Durtles, DNS Hero, Baby Books, Odysee, RadarWeather, Clock, Poet Assistant, FTPClient, Json List, Forecastie, Ultrasonic, RunnerUp, ImapNotes3, OceanNex, Praktika Vortaro, MsgGo, AF Weather Widget, Study Tracker, Calliope mini, F-Droid Build Status, Password Master, Todo List (PFA), Flying Carpet, FitoTrack, ProseReader | Chosen by source/build preflight or clean-candidate sweeps to avoid native/framework blockers. Counted rows pass APK report, dependency-tree, and source-validation gates; Blue Square, Privacy Browser, Mastodon, monocles browser, and ProseReader are no-Maven-signal/report-only controls. Daily Dozen and QuickDic are clean but sparse at 2/2. Coffee is near-clean at 10/11 confirmed; v14 added eight useful partial rows after rescuing three Gradle/Cordova/AGP blockers; v15 added eight useful partial rows after strict module/flavor rescue closed Ultrasonic, RunnerUp, and ImapNotes3; v16 added nine useful partial rows and left Flying Carpet/FitoTrack blocked pending dependency-tree rescue. The clean non-sparse bucket remains open. |

## Next Admission Targets

| Priority | Target class | Preferred layer | Why it matters | Admission rule |
|---:|---|---|---|---|
| 1 | Clean non-sparse modern AndroidX/Kotlin app | source-validated-real | We need more clean real accuracy evidence beyond F-Droid/OpenTracks and sparse Tusky. | Must have matching source release and Gradle runtime dependency tree. |
| 2 | Older dependency profile app | source-validated-real | Markor shows older dependency drift; add another old/minSdk or older-library case before changing reference coverage. | Must preserve old/new label and source version mismatches separately. |
| 3 | R8/minified source-validated app | source-validated-real | Phase 5 remains experimental; real R8/minified controls should grow before scorer promotion. | Must record source minify/shrink evidence or report indicators. |
| 4 | Heavy obfuscation / protected APK | limitation or smoke-real | The MVP should warn and avoid false Maven claims under packed/protected/dynamic code. | Full source validation is optional, but risk indicators and report behavior must be documented. |
| 5 | Flutter app | limitation or smoke-real | Flutter moves major logic to Dart/native artifacts and can reduce Java/Kotlin Maven evidence. | Classify as framework boundary; do not count as Maven-version failure without ground truth. |
| 6 | Unity or game-engine app | limitation or smoke-real | Game engines are often native-heavy and outside normal Android library detection. | Native hash-only behavior and missing Java/Kotlin evidence are the expected result. |
| 7 | Large multidex modern app | source-validated-real or smoke-real | Tests runtime, DEX scaling, and large dependency trees. | Source-validated if dependency tree is feasible; otherwise smoke-only. |
| 8 | Native-heavy app with source tree | source-validated-real or limitation | More `.so` cases help defend the native boundary claim. | Maven dependency validation and native file reporting must remain separate. |
| 9 | Vulnerable dependency expected | controlled or source-validated-real | CVE conclusions depend on exact version confidence. | Use only when the vulnerable version is source-confirmed or controlled. |
| 10 | No-native simple app | source-validated-real | Balances native-heavy cases and tests clean Java/Kotlin behavior. | Prefer small, maintained F-Droid/GitHub app with a simple Gradle tree. |

## Working Rule

For the next real APK batch, choose at least one APK from each of these buckets before revisiting ML:

1. clean non-sparse source-validated;
2. older dependency profile;
3. real R8/minified;
4. heavy obfuscation/protected limitation;
5. Flutter or Unity/framework boundary;
6. native-heavy source-linked or source-validated.

If an APK cannot produce a resolved dependency tree, keep it as `source-linked-blocked`, `smoke-real`, or `limitation`; do not promote it into source-validated metrics.

## Batch V2 Result

The first category-balanced smoke/report batch is complete: 8/8 APKs downloaded from F-Droid, SHA-256 verified against index-v2, and reported with the calibrated matcher DB. It adds Flutter, game/native, older long-lived, modern sync, security, large multidex/browser, VPN/native-heavy, and no-native simple coverage. The protected/obfuscation gap is now partially covered by the public Simplify obfuscated sample, but a fully commercial protected/packed APK remains future limitation work because F-Droid is useful for reproducible source-linked apps and usually does not supply commercial-protected samples.
