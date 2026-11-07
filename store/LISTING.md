# Landscraper: store listing and submission kit

Developer: BENO74 Studios
- Privacy policy: https://beno74.com/privacy (the Landscraper page)
- Support: https://beno74.com

## Graphics (all in `store/`)

| What | File | Size |
|---|---|---|
| iPhone screenshots (6.9" slot) | `ios/screenshots/final/iphone-large-store-1..6.png` | 1290 × 2796 |
| Android phone screenshots | `android/screenshots/final/android-store-1..6.png` | 1080 × 1920 |
| Play feature graphic | `android/feature-graphic.png` | 1024 × 500 |
| Play icon | `android/play-icon-512.png` | 512 × 512 |
| IAP review screenshots (Apple) | `iap/*.png` | 1290 × 2796 |
| IAP promo icons (optional) | `iap-icons/*.png` | |
| Game Center leaderboard art | `leaderboards/daily-512.png`, `leaderboards/rush-512.png` | |

- iPhone only (TARGETED_DEVICE_FAMILY = 1), so no iPad screenshots are needed.
- Apple scales the 6.9" set down for smaller iPhones.

---

## App Store (English, U.S.)

**Name** (30 chars max)
`Landscraper: Draw & Conquer`

**Subtitle** (30 chars max)
`Draw lines. Trap sea monsters.`

**Promotional text** (170 chars max, can change any time)
`Five worlds, five giant bosses, and a new Daily board every day. Draw your line, close it off, and take the sea back one island at a time.`

**Description**
```
Draw a line across the sea, reach land, and everything you closed off becomes yours. Trap the monsters inside and they're gone. Get caught on your line and you lose a life.

Landscraper is a fresh 3D take on the classic territory game, built for one thumb and short sessions.

• 100 levels across 5 worlds: Meadow, Dunes, Glacier, Coral Reef and Volcano
• A giant boss at the end of every world, three rounds each
• 13 kinds of sea monsters, from bouncing puffers to land-eating chompers and fast darts
• 8 boosters: Shield, Speed, Freeze, Slow, Island, Iron Line, +1 Life and extra time
• Daily: a new board every day, with streaks and a monthly calendar
• Rush: clear as many boards as you can before the clock runs out
• Trophies for every world, every month of Daily, and your best Rush runs
• Collect boats and skins: a raft, a duck, a turtle, a submarine, a UFO, a swan and more
• Game Center leaderboards for Daily and Rush
• Plays offline

Free to play with ads. Remove ads, or unlock skin packs, with a one-time purchase.
```

**Keywords** (100 chars max, comma separated, no spaces)
`xonix,qix,territory,claim,area,island,boat,arcade,trap,line,draw,offline,casual,boss,daily,sea,ocean`

**What's New** (first version)
`Welcome to Landscraper!`

**Category:** Games › Arcade (secondary: Puzzle)

**Copyright:** `2026 BENO74 Studios`

### App Review notes (paste into "Notes")
```
Landscraper is a single-player arcade game. No login is required.

In-app purchases (all non-consumable): tap the cart icon at the top left of the home screen to open the Shop (Everything, Remove Ads, All Skins). Skin packs are also sold on the Skins screen (home > Skins > tap a locked pack skin). "Restore purchases" is at the bottom of the Shop.

Ads: rewarded ads are optional and marked with a ▶ AD badge (continue after losing, try a skin, skip a level). Interstitials appear between levels unless Remove Ads is owned. Ad privacy choices can be reopened from Settings (gear icon) > Ad privacy.

Game Center is used for the Daily and Rush leaderboards only.
```

### In-app purchases (non-consumable)

| Product ID | Reference name | Price | Display name | Description (55 chars max) |
|---|---|---|---|---|
| landscraper_bundle | Everything | $9.99 | Everything | No ads, plus every skin pack, now and later. |
| landscraper_no_ads | Remove Ads | $4.99 | Remove Ads | No ads between levels. Free continues. |
| landscraper_all_skins | All Skins | $5.99 | All Skins | All 12 pack skins, plus future packs. |
| landscraper_pack_sea | Sea Pack | $2.99 | Sea Pack | Submarine, Pirate Ship, Yacht and Jet Ski. |
| landscraper_pack_space | Space Pack | $2.99 | Space Pack | UFO, Rocket, Astronaut and Saturn. |
| landscraper_pack_pool | Pool Party | $2.99 | Pool Party | Swan, Donut, Crocodile and Unicorn. |

Review screenshots:
- Everything, Remove Ads and All Skins: `iap/shop-no-ads-everything.png` (All Skins can also use `iap/all-skins.png`).
- Each pack uses its own `iap/pack-*.png`.

### App Privacy (App Store Connect › App Privacy)
"Do you or your third-party partners collect data?" **Yes.** The collection comes from Google AdMob (with UMP consent) and, on Apple's side, Game Center.

| Data type | Collected for | Linked to user | Used for tracking |
|---|---|---|---|
| Identifiers › Device ID | Third-Party Advertising, Analytics | No | Yes |
| Usage Data › Advertising Data | Third-Party Advertising, Analytics | No | Yes |
| Usage Data › Product Interaction | Analytics | No | No |
| Location › Coarse Location | Third-Party Advertising | No | Yes |
| Diagnostics › Crash Data, Performance Data | App Functionality, Analytics | No | No |
| Purchases › Purchase History | App Functionality | No | No |

- "Used for tracking = Yes" fits because the app shows the App Tracking Transparency prompt (NSUserTrackingUsageDescription).
- Game Center data is collected by Apple, not by you, so it isn't declared.

### Age rating
- Cartoon or fantasy violence: **None**. Monsters are trapped, nothing is shown being hurt.
- Everything else: **None / No**.
- Unrestricted web access: No. Gambling: No. Contests: No.
- Expected result: **4+**.

---

## Google Play

**App name** (30 chars max): `Landscraper: Draw & Conquer`

**Short description** (80 chars max)
`Draw lines across the sea, claim the land and trap the monsters. 100 levels.`

**Full description:** the App Store description above, with "Game Center leaderboards" changed to "Google Play Games leaderboards".

**Category:** Arcade. **Tags:** Arcade, Casual, Puzzle, Offline.

### Data safety
| Question | Answer |
|---|---|
| Collects or shares data | Yes (AdMob) |
| Encrypted in transit | Yes |
| Users can request deletion | No account; data isn't linked to a user |

Declare:
- Device or other IDs (Advertising ID): collected and shared, for Advertising and Analytics.
- App info and performance (crash logs, diagnostics): collected, for Analytics.
- App activity (app interactions): collected, for Analytics and Advertising.
- Approximate location: collected and shared, for Advertising.
- All of it is processed ephemerally where AdMob says so. None of it is required for the app to work, except as part of ads.

### Content rating (IARC questionnaire)
Category: Game. No violence beyond cartoon creatures being trapped (answer "No" to violence), no sexual content, no gambling, no user interaction. The game has ads and in-app purchases. Expected result: Everyone / PEGI 3.

### Ads declaration
Contains ads: **Yes**.
