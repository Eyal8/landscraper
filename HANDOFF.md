# Landscraper — handoff notes for an AI coding agent

Landscraper: Draw & Conquer, by BENO74 Studios. Repo Eyal8/landscraper, bundle id `com.beno74.landscraper`. A 3D Xonix-style game for iOS and Android built with Capacitor 8, Three.js r128 and AdMob. The owner is Eyal. Keep replies short. Use no emoji in the app.

## Where the code lives
- **The whole game** is in one file: `src/game.html` (HTML, CSS and JS, Three.js r128). Edit only this file for gameplay and UI.
- **Build:** `npm run build` (scripts/build-web.js) turns it into `www/index.html`. Never edit `www/` by hand.
- **Native code:**
  - iOS: `ios/App/App/GamesPlugin.swift` (Game Center, screenshot hook, edge gestures).
  - Android: `android/app/src/main/java/.../MainActivity.java` (gesture exclusion, screenshot callback).
- **Store assets:** design scripts are in `design/*.py`, outputs in `store/`.
- **Privacy pages:** in the separate repo Eyal8/beno-studio-site. Ask Eyal before merging to its `main`, because that deploys the live site.

## Main concepts in game.html
- **Data tables:**
  - `WORLDS`: Meadow, Dunes, Glacier, Reef, Volcano, 20 levels each. Level 20 of each world is the boss.
  - `lineups`: one letter per monster, `B` = boss.
  - `BOARDS`, `BOSS_BOARD`, `BOOSTERS` (pool and intro level per world), `POWERS` (booster label, colour, duration), `MONSTER_INFO`.
- **Modes:** campaign, daily (`DAILY_START`, streaks), rush.
- **Lives:** carry over in the campaign (3 to 5). A 3-star clear gives +1 life. Running out of lives resets to 3.
- **Ads:** `window.Ads.showRewarded(tag)`. The `adTag()` label is the "▶ AD" badge.
- **Dev mode:** must never ship in production builds. The build strips it when `ADS_TEST=false`.
- **Test hooks:** `window.__game`, including `startLevel(i)` (0-based), `skipIntro`, `freeze`, `clearMonsters`, `addMonster(kind,x,y,vx,vy)`, `power(kind,x,y)`, `trail(cells, close)`, `sim(sec)`, `steer`, `hold`, `setLives`, `setClock`, `snap()`, `powers`, `rings`, `monsters`, `fuse`, `state`, `lives`.

## How to test
Use headless Playwright with Chromium (`--use-gl=swiftshader`) at a 390×844 viewport:
1. Load `file://…/www/index.html` and wait for `window.__game`.
2. Call `startLevel(n)`, then `skipIntro()`, then wait until `!__game.snap().entering`.
3. Script the scenario you need.
4. Screenshot and look at the image, and check that there are no `pageerror` events.

Before building, check the JS syntax:

```
node -e "const s=require('fs').readFileSync('src/game.html','utf8');for(const x of s.matchAll(/<script>([\s\S]*?)<\/script>/g)){try{new Function(x[1])}catch(e){console.log(e.message)}}"
```

## Ship a change (end to end)
1. Edit `src/game.html`, run `npm run build`, run the syntax check, then test headless.
2. Commit to `main`, ending the message with the attribution lines, then run `git push origin HEAD:main`.
3. Start the test builds. These are the tester builds, which use test ads:
   ```
   gh api -X POST repos/Eyal8/landscraper/actions/workflows/android-release.yml/dispatches -f ref=main -F 'inputs[real_ads]=false'
   gh api -X POST repos/Eyal8/landscraper/actions/workflows/ios-testflight.yml/dispatches -f ref=main -F 'inputs[real_ads]=false'
   ```
   - Android `versionCode` = the run number. The AAB is attached to the Actions run as an artifact.
   - iOS uploads to TestFlight.
4. **The store submission build** uses `inputs[real_ads]=true`. Only run it when Eyal says to.

## State as of 2026-11-07
Recent work:
- Boss rounds: eaten obstacles grow back each round.
- Giant Starfish drops 3 babies per trap.
- Boss levels have no small copies of the boss, more boosters (every 9 s), and one shark at most. Glacier's boss board has 5 islands.
- Life boosters: rarer, none at 4+ lives, and about 1 in 3 when nearly out.
- Iron Line replaced Lure.
- The booster HUD shows icon chips with a draining ring.
- The trap hint is a gold glow.
- Whirlpool: visible pull zone and a stronger pull.
- Boosters: vivid colours, they rise from the water, and they fade after 25 s.
- When the Continue offer expires, the card shrinks from the bottom and its top stays fixed.

Still to do:
- Run a bot on all boss levels to check they can be passed.
- Regenerate the store screenshots and IAP review shots, because the UI changed. The review notes should say "cart icon".
- Store listing texts, App Privacy and Data safety.
- App Store Connect submission. The build must use `real_ads=true`.
- Open idea: free 360° movement instead of 4 directions. Not recommended (see the chat).
