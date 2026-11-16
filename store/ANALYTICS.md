# Landscraper Firebase Analytics — implementation and release status

Approved by Eyal on November 16, 2026. Firebase is the studio analytics standard;
other games migrate in their own chats and repositories.

## Created and verified

- Firebase project: `beno74-landscraper`, Spark (no billing upgrade).
- Android app: `1:273290471243:android:eaae0610eaf96a7e05eace`.
- iOS app: `1:273290471243:ios:1aa4c753d3df100905eace`.
- Both use `com.beno74.landscraper`; App Store ID `6828032990`.
- Google Analytics account: Beno Studio (`407422411`).
- Property: `beno74-landscraper` (`564475302`).
- Streams: Android `16350564423`, iOS `16350577384`.
- Console showed event retention **2 months**, user retention **14 months** with
  reset on new activity enabled. These settings were read, not changed.

## Collection contract

Collection is off until the player explicitly allows it. The menu offers a
review of the choice; Settings → Gameplay analytics allows withdrawal and shows
an installation ID for access/deletion requests. Keep this ID available after
withdrawal. Turning collection off does not delete previously uploaded records.

Native Firebase only; browser previews and default tester builds do not collect.
Store builds enable the consent UI, not collection itself. To test analytics
with test ads, build with `ANALYTICS_TEST=true npm run build`, then sync.
Use Firebase DebugView on a test device; do not test with real ads.

No account User-ID, analytics advertising identifiers, replay or Crashlytics.
iOS uses the plugin's AnalyticsWithoutAdIdSupport SPM trait and disables IDFV;
Android disables Analytics AD_ID collection. Analytics ad storage, ad user data
and ad personalization remain denied by the app. Reapply these choices after UMP
returns. Do not enable UMP Consent Mode account-wide as part of this change.
AdMob's existing independent advertising behavior is unchanged.

| Event | Meaning |
|---|---|
| `level_start` | Campaign/Daily attempt or Rush run starts; a rewarded continuation after failure starts another segment |
| `level_end` | Clear, out-of-lives failure, or final Rush result; mode, level, success, score and active play seconds |
| `life_lost` | An actual lost life, or a Rush hit; tutorial protection and shields do not count |
| `run_abandoned` | Active attempt left through menus or replaced; OS termination is not reliably measurable |
| `rewarded_ad_completed` | Native SDK confirms reward; ad-free grants and browser simulation excluded |
| `interstitial_ad_shown` | Native SDK confirms interstitial display |
| `purchase_completed` | Purchase call returns a valid matching transaction; cancellation, failure, pending and restore excluded |

Firebase also measures lifecycle/session and purchase events automatically.
Use custom purchase/ad events for behavior counts, not as an additional revenue
total on top of automatic `in_app_purchase`/`ad_impression` events.
Reports represent opted-in installations, not all players.

## Before the first analytics release

- Native sync stopped twice before producing output locally. Do not keep retrying
  the same local command; use a fresh CI checkout or an owner-run sync as the next
  approach. Generated native plugin lists/SPM package still need synchronization.
- Verify native dependency resolution and final merged Android manifest/iOS
  archive, including disabled collection defaults and no analytics ad identifiers.
- On iOS and Android, verify DebugView: no collection before consent/after
  withdrawal; opt-in persists; UMP choices never grant gameplay analytics or
  analytics advertising purposes implicitly. Exercise a level start, loss,
  completion, abandonment and real test ad reward. Check actual installation ID.
- Sandbox purchase/restore checks remain required before release; mocked purchase
  boundary checks passed, but no store sandbox transaction was performed.
- Publish the reviewed policy at `https://beno74.com/privacy/landscraper`.
  Website draft: https://github.com/Eyal8/beno-studio-site/pull/21 .
  Website repo requires Eyal's approval before merging to main.
- Review and submit App Store Connect App Privacy and Play Data safety using
  `store/LISTING.md`, reconciled with final native SDK behavior.
  Live forms were not updated: the browser connection stopped responding.
- No public app release or store submission is authorized by this implementation.

## AdMob and other settings

EU/US/IDFA messages are not replaced by analytics. An independent opt-in is used,
so enabling AdMob's global Consent Mode analytics purpose is not required.
If switching to UMP-managed analytics later, review both consent-mode toggles,
SDK versions and initialization order first: the settings affect all apps.
Check the existing message's Landscraper policy URL points to the game-specific
page; do not change unrelated apps' messages here.

Linking AdMob to Firebase is optional for richer revenue reports, not required
for the custom behavior events above. It has not been enabled. Google Ads links,
Google Signals, BigQuery, Auth, Firestore, Remote Config and Crashlytics have not
been enabled by this task. Review Google Analytics account sharing and consent
settings before the first release; they were not changed here.

The shared game terms already defer to each game's privacy notice and do not
grant tracking consent; no terms-of-use change is needed for this integration.
The marketing description, screenshots and store age rating do not change
solely because gameplay analytics is added.

References: [collection controls](https://firebase.google.com/docs/analytics/configure-data-collection),
[Apple disclosures](https://support.google.com/analytics/answer/10285841),
[Play disclosures](https://support.google.com/analytics/answer/11582702),
[UMP Consent Mode settings](https://support.google.com/admob/answer/16053245).
