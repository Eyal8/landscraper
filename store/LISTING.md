# Landscraper: store listing and submission kit

Developer: BENO74 Studios
- Privacy policy: https://beno74.com/privacy/landscraper
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

**App Store Connect verified and updated November 16, 2026.** Purchase History was published for Analytics, linked to the installation, not used for tracking. Existing Analytics declarations for device IDs, interactions, advertising data and coarse location were already present and were preserved. No app version was submitted or released by this update.

"Do you or your third-party partners collect data?" **Yes** (Google AdMob and optional Google Analytics for Firebase).

| Data type | Collected for | Linked to user | Used for tracking |
|---|---|---|---|
| Identifiers › Device ID | Analytics, Developer’s Advertising or Marketing, Third-Party Advertising | Yes | Yes (existing AdMob disclosure) |
| Usage Data › Advertising Data | Analytics, Developer’s Advertising or Marketing, Third-Party Advertising | Yes | No |
| Usage Data › Product Interaction | Analytics, Developer’s Advertising or Marketing, Third-Party Advertising | Yes | No |
| Location › Coarse Location | Analytics, Developer’s Advertising or Marketing, Third-Party Advertising | Yes | No |
| Diagnostics › Crash Data | Analytics | No | No |
| Diagnostics › Performance Data, Other Diagnostic Data | Analytics, Developer’s Advertising or Marketing, Third-Party Advertising | No | No |
| Purchases › Purchase History | Analytics | Yes | No |

- Apply the combined purposes/linkage/tracking of all SDKs for each type in the form. "No name/account" does not make an installation ID anonymous. Conservatively disclose Firebase events as linked to a device through the app-instance ID.
- The ATT prompt alone does not determine whether data is used for tracking. Keep the existing AdMob tracking disclosures based on its actual behavior; Firebase does not add cross-app tracking in this configuration.
- Firebase Analytics: collection off until explicit opt-in; advertising consent denied, IDFA/AD_ID collection disabled for analytics, iOS IDFV disabled, no account User-ID or Google Signals. App lifecycle, purchase and general-location collection must still be disclosed. AdMob can independently use advertising IDs according to its consent.
- Privacy policy URL is https://beno74.com/privacy/landscraper . The optional Apple User Privacy Choices URL remains blank: automatic approval review rejected using an unverified policy anchor as a choice mechanism. No workaround was used for that optional field. In-app controls: Settings → Gameplay analytics, and Ad privacy choices when UMP requires it.
- Game Center information managed by Apple is separate from Firebase; do not add account credentials or leaderboard names to analytics.
- Check the final archive's SDK privacy manifests and privacy report for all linked Firebase dependencies. No screen recording, Crashlytics, cloud saves, Auth or Firestore is added.

Official references: [Apple privacy details](https://developer.apple.com/app-store/app-privacy-details/), [Google Analytics Apple disclosures](https://support.google.com/analytics/answer/10285841), [Firebase dependency disclosures](https://firebase.google.com/docs/ios/app-store-data-collection).

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

**Play Console edited November 16, 2026; final submission blocked.** Added optional, non-ephemeral Purchase history collection for Analytics and the data-deletion request URL. Existing AdMob collection/sharing and Analytics purposes for location, device IDs and app interactions were verified and preserved. Saved as one Data safety change; quick checks passed. Two confirmed send attempts did not persist, and a reload still shows "Changes not yet submitted for review" without an error. Stopped per the two-attempt policy. Owner action: Publishing overview → Submit 1 change for review. The only pending change is Data safety, with no app binary included.

| Question | Answer |
|---|---|
| Collects or shares data | Yes: existing AdMob plus optional Firebase Analytics collection |
| Encrypted in transit | Yes |
| Users can request deletion | Yes: https://beno74.com/privacy/landscraper#analytics ; email privacy@beno74.com with the Analytics ID shown in app settings |
| Account creation / account deletion | No BENO74 account creation; the account-deletion requirement is separate from analytics deletion requests |

Declare the union of all integrations:
- **Device or other IDs:** existing AdMob advertising/device identifiers plus Firebase app-instance ID, for Analytics. Gameplay analytics is optional and installation-linked.
- **App activity › App interactions:** sessions, level starts/results, lives lost, run abandonment and ad interactions, for Analytics; retain Advertising purposes for AdMob where applicable.
- **Financial info › Purchase history:** product IDs, names and purchase values/events measured by Analytics; Analytics purpose, optional analytics collection. No card/bank details collected by BENO74.
- **Location › Approximate location:** AdMob's existing collection plus Analytics general location from masked IP, adding Analytics as a purpose. No GPS permission is introduced.
- **App info and performance:** retain and verify the existing AdMob diagnostic disclosures; no Crashlytics or new crash-reporting integration is included.
- Firebase analytics records are **not processed ephemerally**. Do not mark stored events ephemeral merely because an IP address is masked or not stored.
- New purchase-history collection is not marked shared under the service-provider exception. Verified the Beno Studio Analytics account has Google products & services sharing OFF and existing data processing terms accepted; modeling uses aggregated/de-identified data, with technical support enabled. Existing AdMob sharing declarations remain unchanged.
- Privacy policy: https://beno74.com/privacy/landscraper . The policy explains optional collection, automatic SDK data, consent withdrawal, retention and deletion requests.

Official references: [Play Data safety requirements](https://support.google.com/googleplay/android-developer/answer/10787469), [Google Analytics Play disclosures](https://support.google.com/analytics/answer/11582702).

### Content rating (IARC questionnaire)
Category: Game. No violence beyond cartoon creatures being trapped (answer "No" to violence), no sexual content, no gambling, no user interaction. The game has ads and in-app purchases. Expected result: Everyone / PEGI 3.

### Ads declaration
Contains ads: **Yes**.
