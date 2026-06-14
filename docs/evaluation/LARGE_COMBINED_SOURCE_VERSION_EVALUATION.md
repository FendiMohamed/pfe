# Large Combined Source-Constrained Evaluation

## Policy

This is an evaluation-only oracle/source-version constrained run. Each APK is matched only against exact coordinate+version rows that appear in its resolved source dependency tree. It measures an upper bound for bytecode recognition and reference coverage when the correct source versions are known; it must not be reported as production APK-only version-selection accuracy.

## Summary

| Metric | Value |
|---|---:|
| Completed cases | 106 / 106 |
| Pending cases | 0 |
| Checked emitted rows | 6748 |
| Confirmed exact rows | 6748 |
| Version mismatches | 0 |
| Missing emitted coordinates | 0 |
| Confirmation rate | 100.0% |
| Source gap rows | 5262 |
| Source gaps with coordinate in large DB | 4202 |
| Source gaps missing from large DB | 1060 |

## Outputs

- Dashboard JSON: `data/results/evaluation/real-apk-large-combined-source-version-dashboard.json`
- Row CSV: `data/results/evaluation/real-apk-large-combined-source-version-rows.csv`
- Source gap CSV: `data/results/evaluation/real-apk-large-combined-source-version-gaps.csv`

## Case Progress

| Case | App | Status | Checked | Exact | Wrong version | Missing | Confirmation |
|---|---|---|---:|---:|---:|---:|---:|
| fdroid | F-Droid 1.23.2 | complete | 86 | 86 | 0 | 0 | 100.0% |
| opentracks | OpenTracks 4.27.0irreproducible | complete | 83 | 83 | 0 | 0 | 100.0% |
| tusky | Tusky 32.2 | complete | 4 | 4 | 0 | 0 | 100.0% |
| daily-dozen | Daily Dozen 28 | complete | 6 | 6 | 0 | 0 | 100.0% |
| cryptomator-lite | Cryptomator Lite 1.12.3 | complete | 120 | 120 | 0 | 0 | 100.0% |
| easy-xkcd | Easy Xkcd 8.4 | complete | 100 | 100 | 0 | 0 | 100.0% |
| moneywallet | MoneyWallet 4.0.5.10 | complete | 75 | 75 | 0 | 0 | 100.0% |
| privacy-browser | Privacy Browser 3.20.1 | complete | 2 | 2 | 0 | 0 | 100.0% |
| quickdic | QuickDic 5.8.2 | complete | 6 | 6 | 0 | 0 | 100.0% |
| cirrus | Cirrus 4.7 | complete | 81 | 81 | 0 | 0 | 100.0% |
| afwall-plus | AFWall+ 4.0.3 | complete | 80 | 80 | 0 | 0 | 100.0% |
| loop-habit-tracker | Loop Habit Tracker 2.3.1 | complete | 37 | 37 | 0 | 0 | 100.0% |
| yetcalc | yetCalc 2.0.8 | complete | 74 | 74 | 0 | 0 | 100.0% |
| broccoli | Broccoli 1.4.4 | complete | 108 | 108 | 0 | 0 | 100.0% |
| libretube | LibreTube 31.4 | complete | 34 | 34 | 0 | 0 | 100.0% |
| retro-music | Retro Music 6.6.0 | complete | 12 | 12 | 0 | 0 | 100.0% |
| micromathematics-plus | microMathematics Plus 2.23.3 | complete | 67 | 67 | 0 | 0 | 100.0% |
| diaguard | Diaguard 3.15.1 | complete | 23 | 23 | 0 | 0 | 100.0% |
| fulguris-web-browser | Fulguris Web Browser 2.0.10 | complete | 104 | 104 | 0 | 0 | 100.0% |
| working-time-account | Working Time Account 2.11.012 | complete | 60 | 60 | 0 | 0 | 100.0% |
| andstatus | AndStatus 62.03 | complete | 83 | 83 | 0 | 0 | 100.0% |
| i2p | I2P 2.11.0 | complete | 90 | 90 | 0 | 0 | 100.0% |
| mastodon | Mastodon 2.12.3 | complete | 0 | 0 | 0 | 0 | 0.0% |
| drift-audio | Drift // Audio 0.1.0 | complete | 45 | 45 | 0 | 0 | 100.0% |
| jamuz | JaMuz 0.6.14 | complete | 73 | 73 | 0 | 0 | 100.0% |
| monocles-browser | monocles browser 1.9.3 | complete | 3 | 3 | 0 | 0 | 100.0% |
| your-local-weather | Your local weather 6.4.0-FOSS | complete | 70 | 70 | 0 | 0 | 100.0% |
| homefeed-rss-widget | HomeFeed - RSS Widget 1.3.0 | complete | 67 | 67 | 0 | 0 | 100.0% |
| etar | Etar - OpenSource Calendar 1.0.55 | complete | 71 | 71 | 0 | 0 | 100.0% |
| dolidroid | DoliDroid 3.0.69 | complete | 50 | 50 | 0 | 0 | 100.0% |
| owncloud | ownCloud 4.8.0 | complete | 129 | 129 | 0 | 0 | 100.0% |
| openkeychain | OpenKeychain: Easy PGP 6.0.4 | complete | 64 | 64 | 0 | 0 | 100.0% |
| radiodroid | RadioDroid 0.86 | complete | 109 | 109 | 0 | 0 | 100.0% |
| simplelogin | SimpleLogin Anti-spam 1.22.0 | complete | 87 | 87 | 0 | 0 | 100.0% |
| omni-notes | Omni Notes 6.3.1 | complete | 73 | 73 | 0 | 0 | 100.0% |
| primitive-ftpd | Primitive FTPd 8.1 | complete | 77 | 77 | 0 | 0 | 100.0% |
| floccus | floccus bookmark sync 5.9.1 | complete | 51 | 51 | 0 | 0 | 100.0% |
| opencloud | OpenCloud 1.2.3 | complete | 126 | 126 | 0 | 0 | 100.0% |
| sambalite | SambaLite 2.5.1 | complete | 77 | 77 | 0 | 0 | 100.0% |
| nightdream | NightDream 2.11.26 | complete | 106 | 106 | 0 | 0 | 100.0% |
| waistline | Waistline 3.10.1 | complete | 53 | 53 | 0 | 0 | 100.0% |
| password-generator | Password Generator 1.9.0 | complete | 65 | 65 | 0 | 0 | 100.0% |
| todo-agenda | Todo Agenda 4.13.3 | complete | 60 | 60 | 0 | 0 | 100.0% |
| keep-it-up | Keep it up 1.11.1 | complete | 16 | 16 | 0 | 0 | 100.0% |
| c3nav | c3nav 4.7.0 | complete | 52 | 52 | 0 | 0 | 100.0% |
| opentopomap-viewer | OpenTopoMap Viewer 1.29 | complete | 102 | 102 | 0 | 0 | 100.0% |
| railway-station-photos | Railway station photos 16.4.0 | complete | 99 | 99 | 0 | 0 | 100.0% |
| linkdroid | LinkDroid for Linkwarden 2.1.9 | complete | 67 | 67 | 0 | 0 | 100.0% |
| quasseldroid | Quasseldroid 1.8.0 | complete | 59 | 59 | 0 | 0 | 100.0% |
| bimba | Bimba 3.99 | complete | 137 | 137 | 0 | 0 | 100.0% |
| wx | wX 55990 | complete | 64 | 64 | 0 | 0 | 100.0% |
| egyptian-writer | Egyptian Writer 14.05.2026@0.1.0.1 | complete | 68 | 68 | 0 | 0 | 100.0% |
| smouldering-durtles | Smouldering Durtles 1.2.3 | complete | 93 | 93 | 0 | 0 | 100.0% |
| dns-hero | DNS Hero 1.7.0 | complete | 37 | 37 | 0 | 0 | 100.0% |
| baby-books | Baby Books 0.9.2 | complete | 130 | 130 | 0 | 0 | 100.0% |
| odysee | Odysee 0.0.124 | complete | 57 | 57 | 0 | 0 | 100.0% |
| radarweather | RadarWeather 6.7 | complete | 71 | 71 | 0 | 0 | 100.0% |
| clock | Clock 2.29 | complete | 73 | 73 | 0 | 0 | 100.0% |
| poet-assistant | Poet Assistant 1.31.1 | complete | 15 | 15 | 0 | 0 | 100.0% |
| ftpclient | FTPClient 3.0.1 | complete | 75 | 75 | 0 | 0 | 100.0% |
| json-list | Json List 1.10 | complete | 57 | 57 | 0 | 0 | 100.0% |
| forecastie | Forecastie 1.23 | complete | 45 | 45 | 0 | 0 | 100.0% |
| ultrasonic | Ultrasonic 4.9.0 | complete | 37 | 37 | 0 | 0 | 100.0% |
| runnerup | RunnerUp 2.11.0.1 | complete | 81 | 81 | 0 | 0 | 100.0% |
| imapnotes3 | ImapNotes3 v1.4-07 | complete | 68 | 68 | 0 | 0 | 100.0% |
| oceannex | OceanNex for DigitalOcean 1.0.0 | complete | 75 | 75 | 0 | 0 | 100.0% |
| praktika-vortaro | Praktika Vortaro 0.26 | complete | 6 | 6 | 0 | 0 | 100.0% |
| msggo | MsgGo 3.9 | complete | 73 | 73 | 0 | 0 | 100.0% |
| af-weather-widget | AF Weather Widget 3.2 | complete | 68 | 68 | 0 | 0 | 100.0% |
| study-tracker | Study Tracker 1.0.7 | complete | 60 | 60 | 0 | 0 | 100.0% |
| calliope-mini | Calliope mini 2.0.9 | complete | 79 | 79 | 0 | 0 | 100.0% |
| fdroid-build-status | F-Droid Build Status 5.14.0 | complete | 93 | 93 | 0 | 0 | 100.0% |
| password-master | Password Master 1.5.1 | complete | 82 | 82 | 0 | 0 | 100.0% |
| todo-list-pfa | Todo List (PFA) 3.4.0 | complete | 74 | 74 | 0 | 0 | 100.0% |
| flying-carpet | Flying Carpet 9.0.8 | complete | 57 | 57 | 0 | 0 | 100.0% |
| fitotrack | FitoTrack 15.6 | complete | 105 | 105 | 0 | 0 | 100.0% |
| newpipe | NewPipe 0.28.5 | complete | 51 | 51 | 0 | 0 | 100.0% |
| antennapod | AntennaPod 3.11.4 | complete | 79 | 79 | 0 | 0 | 100.0% |
| kde-connect | KDE Connect 1.35.5 | complete | 31 | 31 | 0 | 0 | 100.0% |
| wikipedia | Wikipedia Android r/50586 | complete | 45 | 45 | 0 | 0 | 100.0% |
| conversations | Conversations 2.20.0+free | complete | 35 | 35 | 0 | 0 | 100.0% |
| aegis | Aegis Authenticator 3.4.2 | complete | 33 | 33 | 0 | 0 | 100.0% |
| markor | Markor 2.16.1 | complete | 101 | 101 | 0 | 0 | 100.0% |
| nextcloud | Nextcloud Android 33.1.0 | complete | 186 | 186 | 0 | 0 | 100.0% |
| vlc-android | VLC Android 3.7.1 | complete | 160 | 160 | 0 | 0 | 100.0% |
| osmand | OsmAnd~ 5.3.10 | complete | 113 | 113 | 0 | 0 | 100.0% |
| material-files | Material Files 1.7.4 | complete | 11 | 11 | 0 | 0 | 100.0% |
| davx5 | DAVx5 4.5.12-ose | complete | 26 | 26 | 0 | 0 | 100.0% |
| openvpn-for-android | OpenVPN for Android 0.7.64 | complete | 69 | 69 | 0 | 0 | 100.0% |
| gadgetbridge | Gadgetbridge 0.91.1 | complete | 79 | 79 | 0 | 0 | 100.0% |
| shelter | Shelter 1.9.1 | complete | 5 | 5 | 0 | 0 | 100.0% |
| stopwatch | Stopwatch 1.6 | complete | 15 | 15 | 0 | 0 | 100.0% |
| bubble | Bubble 3.4 | complete | 28 | 28 | 0 | 0 | 100.0% |
| audio-source | Audio Source 1.5 | complete | 24 | 24 | 0 | 0 | 100.0% |
| blue-square-speedometer | Blue Square Speedometer 1.1.0 | complete | 0 | 0 | 0 | 0 | 0.0% |
| gotify | Gotify 2.10.0 | complete | 96 | 96 | 0 | 0 | 100.0% |
| foxy-droid | Foxy Droid 1.3 | complete | 22 | 22 | 0 | 0 | 100.0% |
| bettercounter | BetterCounter 6.0.3 | complete | 18 | 18 | 0 | 0 | 100.0% |
| coffee | Coffee 2.26 | complete | 35 | 35 | 0 | 0 | 100.0% |
| medtimer | MedTimer 1.22.18 | complete | 98 | 98 | 0 | 0 | 100.0% |
| doodle | Doodle 6.0.0 | complete | 14 | 14 | 0 | 0 | 100.0% |
| simple-time-tracker | Simple Time Tracker 1.57 | complete | 46 | 46 | 0 | 0 | 100.0% |
| keepassvault | KeePassVault 1.16.0 | complete | 124 | 124 | 0 | 0 | 100.0% |
| k9 | K-9 / Thunderbird Android 18.0 | complete | 55 | 55 | 0 | 0 | 100.0% |
| jitsi-meet | Jitsi Meet 26.0.0 | complete | 16 | 16 | 0 | 0 | 100.0% |
| fairemail | FairEmail 1.2315 | complete | 67 | 67 | 0 | 0 | 100.0% |
