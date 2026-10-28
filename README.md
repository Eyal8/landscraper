# Landscraper: Draw & Conquer

A 3D territory game for iOS and Android by BENO74 Studios. Leave your land, draw a trail across the open field, and get back to land to claim every area with no monster in it. Claim 75% to clear the level.

Built with Three.js (r128) and Capacitor 8. Sister game of [Shapescraper](https://github.com/Eyal8/shapescraper).

## Run it
```
npm install
npm run build      # src/game.html -> www/ (offline fonts, local three.js)
npm run android    # build, sync, open Android Studio
npm run ios        # build, sync, open Xcode (Mac only)
```
For a quick look, open `src/game.html` in a browser (it loads three.js and fonts from CDNs). Arrow keys or WASD steer on desktop.

## Cloud builds (no Mac needed)
- **Build Android APK**: runs on every push, gives an installable debug APK.
- **Android release (Play Store bundle)**: signed `.aab`. Secrets: `ANDROID_KEYSTORE_BASE64`, `ANDROID_KEYSTORE_PASSWORD`, `ANDROID_KEY_ALIAS`, `ANDROID_KEY_PASSWORD`.
- **iOS release (TestFlight)**: builds on a cloud Mac and uploads to TestFlight. Secrets: `ASC_KEY_ID`, `ASC_ISSUER_ID`, `ASC_KEY_P8`, `APPLE_TEAM_ID`.

The version code / build number is the workflow run number.

## Ads
Tester builds always use Google's test ads. Only store builds run with `real_ads=true` (`ADS_TEST=false`). Never tap your own real ads.

The AdMob app IDs in the Android manifest and iOS `Info.plist` are Google's sample IDs until the Landscraper AdMob app is created.

## Status
- [x] Prototype ported to `src/game.html`
- [x] Capacitor projects for `com.beno74.landscraper`
- [ ] App icon and splash (currently placeholders carried over from Shapescraper)
- [x] Controls: two-turn swipe queue, corner forgiveness, reverse on land, native haptics
- [x] Claimed land grows a world (trees, houses, lamps); slow orbit at level clear
- [x] Trap monsters: enclose one in 40 cells or less to catch it
- [ ] More monsters, board shapes, themed worlds, power-ups
- [ ] Ads, Remove Ads purchase, tutorial, Daily
