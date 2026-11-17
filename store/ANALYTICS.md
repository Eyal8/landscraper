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

Analytics consent is integrated with the existing Google UMP privacy message;
there is no home-screen analytics offer or separate Allow analytics permission.
Firebase initializes with collection off before UMP. After a successful current
UMP update/form, the native AnalyticsConsent bridge reads `UMP_consentModeValues`
from Android default shared preferences or iOS standard UserDefaults. A well-formed four-digit signal permits Analytics storage when its fourth digit
is `1` (granted) or `3` (not applicable), after a successful current UMP update
with status OBTAINED or NOT_REQUIRED. iPhone build 196 device QA showed
OBTAINED + 3333; requiring the broader NOT_REQUIRED status was too restrictive. No additional consent request is shown for NOT_REQUIRED.
`0` (unknown), `2` (denied), `4` (not configured), missing or malformed values,
failed updates and unresolved REQUIRED forms stay off. Cached value `3` without a successful resolved update, or NOT_REQUIRED with a
missing/unconfigured/denied analytics value, never enables.
US ad-sale/sharing opt-outs and ATT remain distinct from service-provider
gameplay measurement. Existing GA products/services sharing is off, applicable
data processing terms are accepted and Analytics advertising consent is denied.
Regional/minor requirements outside UMP coverage remain a pre-release check;
NOT_REQUIRED is not a universal legal clearance.

Settings → Privacy choices reopens UMP where required. Collection stops before
opening the form and is reconciled afterwards. Settings → Gameplay analytics
shows status and an installation ID for access/deletion requests, plus a device
pause. Removing that pause never overrides the UMP result or an explicit denial. The old separate
`ls_analytics_consent_v1` choice is ignored. Historical request IDs are retained;
stopping collection does not delete previously uploaded records.

Native Firebase only; browser previews and default tester builds do not collect.
To test analytics with test ads: `ANALYTICS_TEST=true npm run build`, then sync.
Use Firebase DebugView on a test device; do not test with real ads.

No account User-ID, analytics advertising identifiers, replay or Crashlytics.
iOS uses AnalyticsWithoutAdIdSupport and disables IDFV; Android disables
Analytics AD_ID collection. Analytics ad storage, ad user data and ad
personalization remain denied by the app even when UMP grants them. Reapply
these restrictions before enabling collection and after privacy changes.

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
Reports represent permitted measured installations (consented or not-required), not all players.

## Native CI validation — November 16, 2026 (earlier separate-consent revision)

Eyal authorized the CI pivot and website merge on November 16.
- Android sync, targeted tests and APK build passed: https://github.com/Eyal8/landscraper/actions/runs/43850587369 .
- Unsigned iOS Simulator build, targeted tests and packaged configuration checks passed: https://github.com/Eyal8/landscraper/actions/runs/43850587807 . This job does not sign, upload to TestFlight or submit an app version.
- Inspected the actual Android APK: FirebaseAnalyticsPlugin is packaged, default tester analytics is disabled, and all seven Analytics privacy defaults in the merged manifest are false.
- iOS compiled with the AnalyticsWithoutAdIdSupport trait. The CI artifact resolved Firebase Apple SDK 12.19.3 and GoogleAppMeasurement 12.19.2; packaged project ID, disabled collection, denied advertising consent and disabled IDFV checks passed.
- Local Capacitor sync had stalled twice; a fresh CI checkout resolved the integration successfully. No repeated local retries were needed.

## Combined UMP migration validation — November 16, 2026

- Ten consent-boundary tests passed, including explicit grants, not-applicable
  measurement without a prompt, stale grants, malformed/missing signals, errors,
  device pause, revocation and queued events. NOT_REQUIRED never overrides denial
  or an unconfigured purpose. The region-handling correction changes JS only;
  native code remains at the already-validated 48d0506 revision.
- Native startup/monetization boundary tests passed for Android and iOS, including
  successful UMP initialization, NOT_REQUIRED collection, unresolved forms, UMP
  failures and withdrawal.
- Android native sync/build/tests passed at commit 48d0506:
  https://github.com/Eyal8/landscraper/actions/runs/43864150725 .
- Unsigned iOS Simulator sync/build/tests and packaged Firebase privacy checks
  passed at commit 48d0506: https://github.com/Eyal8/landscraper/actions/runs/43864150992 .
- A subsequent menu-only callback refreshes the visible Analytics status after
  returning from privacy choices; its packaged startup checks passed locally.
- Website TypeScript, targeted ESLint, production build and legal-route checks
  passed. No website tracker was added. Policy/standard update is draft PR 23.
- Account activation is owner-reported; physical-device/sandbox checks remain pending; successful
  builds are not proof that the live UMP message supplies an analytics grant.

## Before the first analytics release
- On iOS and Android, verify DebugView: no collection before consent/after
  withdrawal; a UMP grant or successful resolved update + analytics value 3 enables
  collection, while denial, missing/unconfigured values and failed updates do not. Device pause persists.
  UMP/ATT never implicitly grant Analytics advertising purposes. Exercise a level start, loss,
  completion, abandonment and real test ad reward. Check actual installation ID.
- Sandbox cancellation, purchase, relaunch and restore smoke checks passed on
  iPhone TestFlight 197 and the dedicated Android AVD; see the device records below.
- Website PR 21 was merged with Eyal's explicit approval: https://github.com/Eyal8/beno-studio-site/pull/21 . Verified the analytics section, date and request-ID instructions in the public HTML at https://beno74.com/privacy/landscraper .
- Review and submit App Store Connect App Privacy and Play Data safety using
  `store/LISTING.md`, reconciled with final native SDK behavior.
  Apple App Privacy was published on November 16: added Purchase History for Analytics, linked to the installation, not used for tracking. Existing device, location and interaction Analytics disclosures were already present. The optional User Privacy Choices URL was left blank after automatic approval review rejected an unverified choice-mechanism link; the existing policy URL remains correct. Google Play: added optional, non-ephemeral Purchase history for Analytics (collected, not shared under the service-provider exception) and the verified deletion-request instructions URL. On November 17, the live Play Console confirmed Submission 17 (Data safety only) was Published on November 16 and no changes remained unsubmitted. No binary release was part of that submission.
- Store privacy metadata updates and internal-only TestFlight uploads were authorized;
  no public app release or app main merge has been authorized or performed.

## AdMob and other settings

Owner approved account-wide combined AdMob consent on November 16, 2026.
Required account settings: Privacy & messaging → European regulations → Settings
→ enable Consent Mode for advertising purposes, then analytics purposes → Save.
These settings affect all configured European messages, not just Landscraper.
**Activation reported by owner, November 16, 2026:** both advertising and
analytics Consent Mode toggles were checked and saved. Earlier attempts by the
agent had encountered a loading settings page; that is no longer an owner task.
The effective SDK/message values were subsequently verified on iPhone; see the
November 17 device results below. Android emulator results are recorded below;
Android physical-device verification remains pending.
Existing EU/US/IDFA message definitions and ad units were not replaced. Verify
analytics choices for returning users; an old ads-only consent is insufficient.

Current wrapper 8.2.1 declares Android UMP 4.0.0 and iOS UMP 3.1.x, above Google's
required versions. Shapescraper and other games must implement their own native
initialization, consent read, collection gate and disclosure migration before
shipping Analytics. Shared settings alone do not implement those safeguards.
Website policy and standard v1.8 were merged with explicit owner approval:
https://github.com/Eyal8/beno-studio-site/pull/23 (74e2c072). Verified the updated
public policy includes not-required collection, the device pause and Firebase. No public app release is authorized.

Linking AdMob to Firebase is optional for richer revenue reports, not required
for the custom behavior events above. It has not been enabled. Google Ads links,
Google Signals, BigQuery, Auth, Firestore, Remote Config and Crashlytics have not
been enabled by this task. Verified the Beno Studio Analytics account: Google products & services sharing is OFF; modeling contributions use aggregated/de-identified data, technical support and business recommendations are enabled; data processing terms were already accepted on September 24, 2026. These account-wide settings were not changed. Native consent behavior still needs on-device verification before release.

The shared game terms already defer to each game's privacy notice and do not
grant tracking consent; no terms-of-use change is needed for this integration.
The marketing description, screenshots and store age rating do not change
solely because gameplay analytics is added.

References: [collection controls](https://firebase.google.com/docs/analytics/configure-data-collection),
[Apple disclosures](https://support.google.com/analytics/answer/10285841),
[Play disclosures](https://support.google.com/analytics/answer/11582702),
[UMP Consent Mode settings](https://support.google.com/admob/answer/16053245).

Official regional handling references: [UMP signal values and basic mode](https://developers.google.com/funding-choices/fc-sdks),
[non-EU defaults](https://developers.google.com/admob/ios/privacy/consent-mode),
[Analytics US service-provider terms](https://support.google.com/analytics/answer/6004245?hl=en).

## Private UMP QA builds

Explicit test builds use `ANALYTICS_TEST=true UMP_TEST=true npm run build`.
The UMP QA module is removed from ordinary/store HTML and cannot be built with
real ads. Settings → UMP test controls accepts native-log UMP device IDs and
Actual/EEA/US/Other geography; reset stops collection before resetting UMP and
fetching fresh consent. Diagnostics show UMP status, four mode values, collection
and device pause. Changing QA settings does not fabricate a consent grant.

Owner separately authorized internal TestFlight upload only. The workflow uses
`testFlightInternalTestingOnly=true`, which prevents external TestFlight/App
Store distribution, and skips certificate cleanup. No public app release or
app main merge is authorized. See the device guide in the workspace artifacts.

Private QA artifacts (November 16, 2026):
- Android QA build succeeded, downloaded APK was inspected: analytics enabled,
  UMP QA module present and test ads enabled. Run 43909869733:
  https://github.com/Eyal8/landscraper/actions/runs/43909869733 .
- iOS signed archive and internal-only TestFlight upload succeeded: version 1.0
  build 196, run 43910265817. Export explicitly used
  testFlightInternalTestingOnly=true and no certificate cleanup. Apple processing
  completed; the internal group Me tester row showed Installed 1.0 (196).
  No external group or public App Store version was changed.
  https://github.com/Eyal8/landscraper/actions/runs/43910265817 .
- Additional unsigned Simulator/device validation passed: run 43909876177.
- No device behavior or sandbox purchase result is claimed from these builds.

## iPhone 196 device finding and correction

Owner screenshots reproduced OBTAINED + modes 3333 + collection false + paused
false. The extra NOT_REQUIRED condition incorrectly blocked this documented
not-applicable purpose signal. The correction accepts analytics value 1 or 3
after either resolved status, while still blocking unresolved/error states,
denials, missing/unconfigured values and device pause. A regression test uses
this exact device observation on both platform startup paths. Also wrapped the
UMP test-menu callback so the clicked button is not rendered as a message.
Native SDK code and live privacy-page wording are unchanged. Studio standard
v1.9 is proposed separately; no new website main merge is authorized.

Replacement private artifacts: iOS 1.0 (197) signed and uploaded successfully to
internal-only TestFlight in run 43965868560. Owner subsequently installed build
197 and continued the consent/DebugView checks using a local Xcode development
run of the corrected code. Matching
Android QA build 43965875677 passed; downloaded APK was inspected for the new
purpose-3 condition, fixed callback, analytics/UMP test flags and test ads.

## iPhone manual consent/Analytics results — November 17, 2026

Owner-reported device results and screenshots verified:
- Actual-location update: NOT_REQUIRED, modes 3333, collection true, paused false.
- Manual Pause: collection false, paused true.
- Forced EEA on the registered UMP test device displayed the consent message.
- Do not consent: OBTAINED, modes 2222, collection false, paused false.
- Consent after test reset: OBTAINED, modes 1111, collection true, paused false.
  Firebase DebugView received level_start, life_lost and level_end events.
- A subsequent test reset and refusal followed by a complete played level
  produced no new gameplay events in the observed DebugView interval. Earlier
  accepted-session events remained visible.

These observations complete this iPhone grant/refusal gameplay test, including
server-side event visibility after grant. They do not establish every startup
or withdrawal path: the refusal transition used the QA reset, not the ordinary
privacy-options entry point. Android physical-device checks and sandbox
purchase/restore checks remain pending. No public release was performed.

## Android emulator attempt — November 17, 2026

Installed the corrected private APK on the existing Pixel_8_Pro API 37.1 AVD.
Native logs showed collection disabled at startup, a successful UMP update
writing modes 3333 / gdprApplies 0, and subsequent Analytics uploads returning
HTTP 204 for this Android Firebase app. This establishes transport in that
resolved not-applicable case, not EEA consent or gameplay acceptance.

The preview emulator rendered the gameplay area incorrectly and UI automation
was unreliable. Pivoted to the existing Medium_Phone_API_36.1 Play Store AVD;
installation failed because its data partition had only about 23 MB available.
A single cache-only trim did not resolve the second install attempt. Stopped
per the owner's two-attempt rule; no third installation retry or deletion of
app data/accounts was performed. Both started emulators were shut down and the
remaining emulator's Firebase debug property was disabled before shutdown.

Recommended next step: a fresh, dedicated test AVD rather than changing or
deleting existing emulator app data. EEA grant/refusal, Pause and gameplay event
verification on Android are still pending. No store distribution occurred.

## Dedicated Android emulator results — November 17, 2026

Created Landscraper_Analytics_API36_1 using the already installed Google Play
API 36.1 ARM64 system image, with a separate 8 GB data partition under workspace
artifacts/android-avd. No existing AVD configuration, app data or accounts were
modified. Installed the existing corrected private APK from run 43965875677;
no new app build or store distribution was needed.

Verified with the real UMP SDK, Firebase native preferences and Google Analytics
DebugView (device sdk_gphone64_arm64):
- Actual location: NOT_REQUIRED / 3333 / collection true / paused false.
- Forced EEA before choosing: UMP values 0000 and native measurement disabled.
- Consent: OBTAINED / 1111 / collection true / paused false. A subsequent
  level_start at 01:27:02 reached DebugView, as did run_abandoned at 01:31:20.
- Pause: native measurement disabled, and after force-stop/relaunch the UI
  retained 1111 / collection false / paused true. Removing Pause restored On
  according to the existing UMP grant.
- Withdrawal through the ordinary Gameplay analytics → Privacy choices entry
  point, without QA reset: Do not consent produced OBTAINED / 2222 / collection
  false / paused false. Native measurement was disabled.
- A new level attempt and force-stop/relaunch after refusal retained the
  disabled state. No gameplay logEvent bridge calls occurred after the refusal
  at 01:33:47, and DebugView observed through 01:35 still showed 01:31:20 as the
  last gameplay event. This negative result follows positive event verification
  on the same emulator.

Evidence: workspace artifacts/android-emulator-analytics contains the consent,
Pause and relaunch screenshots, targeted logs and results.json. The reusable
start-emulator.command launches this isolated AVD. At completion the Firebase
debug property was disabled and this emulator was shut down; its saved QA
region is EEA with consent denied. No Firebase consent/storage preferences were
edited to simulate a result. The emulator test ID was derived from the installed
UMP SDK's emulator hash algorithm; emulators are also SDK test devices by default.

The Android consent/collection smoke test is complete on this emulator. This
does not claim physical-device coverage, a full completed-level gameplay test,
US-specific messaging, offline startup or purchase/restore sandbox validation.
No public release or app main merge was performed.

## Production preparation — November 17, 2026

- Updated iOS Info.plist from one to all 50 SKAdNetwork identifiers in Google's
  current iOS AdMob quick-start example (49 added). Validated plist syntax,
  uniqueness and exact agreement with the fetched official list. This configures
  ad attribution; it does not change the IDFA explainer or ATT permission dialog.
- CI run 44074021859 passed unsigned iOS Simulator and iPhone device builds.
  The downloaded iPhone package contains all 50 unique identifiers, identical
  to the validated source list, and preserves disabled Firebase collection,
  Analytics storage, advertising-purpose and IDFV defaults. No signed archive
  or new TestFlight upload was created for this configuration-only change.
- Built store-mode web assets and ran the Android/iOS native-boundary suite
  against them: Analytics enabled, developer mode disabled, UMP QA module absent.
  Restored the existing local private-test HTML afterward. No real-ad build was
  installed or run. Ten Analytics tests passed.
- Android offline cold start after previously enabled collection: enabled
  airplane mode on the isolated AVD, force-stopped and launched the game.
  Bundled gameplay/fonts loaded, UMP returned a network error, and diagnostics
  showed UNKNOWN / cached 3333 / collection false / paused false. Native
  measurement remained disabled after the failed update; no custom gameplay
  logEvent call appeared for that offline launch. This verifies the observed
  startup/error path, not an exhaustive audit of every native automatic event.
  Restoring connectivity and cold-launching again successfully updated UMP
  and re-enabled permitted collection. Airplane mode and the Firebase debug
  property were disabled afterward, and the isolated emulator was shut down.
- US regulated-state debug update on the installed Android private build
  returned NOT_REQUIRED / 3333 / collection true, with privacy options
  NOT_REQUIRED and no GPP fields. AdMob overview showed two active US messages,
  but the message-details iframe did not load. App assignments and the actual
  US opt-out flow therefore still need confirmation; no US message was edited.
  Consent Mode's European settings do not themselves wire US advertising
  opt-out choices to the gameplay Analytics switch.

Evidence is under workspace artifacts/android-emulator-analytics, including
skadnetwork-google-2026-11-17.txt, store-build-check.txt, us-region.log and
45-offline-diagnostics.png. iPhone offline and both stores' purchase/restore
sandbox checks still need the owner session described in the device guide.

### iPhone Sandbox follow-up — November 17, 2026

Owner tested internal TestFlight build 197: cancelling retained the price and
allowed a retry; a successful Remove Ads purchase changed the card to Owned
and DebugView showed one purchase_completed event. Ownership persisted after
relaunch, and Restore purchases completed without an error. Duplicate-event
absence after restore has not yet been confirmed by the owner.

The owner observed missing restore feedback and a shop flicker. Restore now
shows inline progress and persistent restored/empty/error feedback, updates
ownership cards in place, and blocks repeat taps while pending. Native restore
or entitlement-query errors no longer report cached ownership as a successful
restore. Targeted Android/iOS purchase-boundary checks and an inline UI smoke
check passed; all 10 Analytics tests passed. This UI correction is for the next
build and is not present in installed build 197. No public release was made.

### iPhone offline/recovery follow-up — November 17, 2026

Owner confirmed on build 197: cold launch without connectivity loaded playable
gameplay, with collection false / paused false. After restoring connectivity
and cold-launching again, the owner reported the recovery check worked.
This completes the owner offline/recovery smoke check on iPhone; exact online
status/mode values were not separately supplied in the final confirmation.

At that checkpoint, remaining before public distribution were confirmation of Landscraper's
US-message assignments/opt-out flow, final
Google Play Data Safety submission status, and final distribution builds
containing the SKAdNetwork and restore-feedback changes. Existing targeted
checks passed; installed TestFlight 197 does not contain those latest changes.
See the final preparation section below for the subsequent results.
No app main merge or public release has been performed.

### Android Play Billing Sandbox — November 17, 2026

On the existing isolated Landscraper_Analytics_API36_1 AVD, the owner signed
into Google Play. The Remove Ads dialog showed "Test card, always approves"
and explicitly stated the order would not be charged. No new APK was uploaded
or installed, and no emulator/app data was cleared.

- Cancellation returned USER_CANCELED, retained the price and allowed retry;
  no custom purchase_completed was sent.
- A successful test purchase showed Owned and sent exactly one custom
  purchase_completed call with item_id landscraper_no_ads. The owner handled
  Google's device purchase-authentication preference prompt personally.
- Force-stop and cold launch re-queried entitlements and retained Owned.
- Explicit Restore purchases called restorePurchases and then getPurchases,
  returned without a native purchase error, and retained Owned. Neither
  relaunch nor restore sent another custom purchase_completed call.

Evidence: workspace artifacts/android-emulator-analytics/billing-results.json,
billing-evidence.log and screenshots 56-65. This session verified the custom
event at the native Firebase bridge; server DebugView purchase delivery was
not separately checked. Firebase debug mode was disabled afterward and the
game was stopped. The emulator's Google login and test ownership were retained.
The installed APK predates the inline restore-feedback correction, which still
needs the final build smoke check. No public app release or main merge occurred.

### Final production preparation — November 17, 2026

- Google Play Publishing overview has no unpublished changes. Submission 17
  contains exactly one Data safety questionnaire change and is Published
  (November 16). Verified in the live submission details, without resubmitting
  anything or touching a binary release.
- Live https://beno74.com/privacy/landscraper returned HTTP 200 and includes
  Firebase, UMP, device Pause and Analytics-ID deletion-request instructions.
- The owner added Landscraper Android and iOS to published US messages. After
  that change, the existing Android US-regulated-state QA configuration exposed
  the ordinary Privacy choices entry and the Google US form. Selecting Don't
  sell or share my data changed native GPP from DBABL~BAAAAAAAAg to
  DBABL~BVQVAAAAAg (section 7), and reopening the form retained the opt-out.
  Analytics returned to On after reconciliation with modes 3333, as designed;
  its advertising-purpose consents stayed denied. This verifies the Android
  form/signals; iPhone US UI and downstream ad requests were not separately
  exercised (Remove Ads is owned on the emulator). Debug was disabled and
  Landscraper was stopped afterward; login, purchase and consent data retained.
- Signed Android AAB versionCode 195 built successfully in run 44106718008.
  Its actual packaged web assets passed the native-boundary suite and checks
  for Analytics enabled, developer mode disabled, UMP QA module absent and
  inline restore feedback present. The JAR signature verified. The AAB was
  downloaded to workspace artifacts/production-prep-2026-11-17/android-195;
  it was not uploaded to Google Play or run with real ads on a device.
- iOS attempt 198 (44106718661) never received a hosted ARM runner and was
  cancelled by GitHub for capacity constraints. The TestFlight workflow now
  uses standard macos-26-intel capacity. Build 199, run 44110532426, passed
  private-build checks, archive/signing and upload to App Store Connect.
  The log confirms testFlightInternalTestingOnly=true, Upload succeeded and
  EXPORT SUCCEEDED. It includes the 50 SKAdNetwork IDs and restore-feedback
  correction. Apple processing/group availability was not re-verified because
  the TestFlight UI timed out; do not claim it is already installable.
  This is a private test-ad/UMP-QA build, not a public-store candidate.
- The existing App Store submission still selects build 195, is Waiting for
  Review and has Manually release this version selected. These settings were
  only read, not changed. A future public iOS release needs a separately
  approved normal store build; internal-only build 199 cannot be used for it.

Evidence: workspace artifacts/production-prep-2026-11-17/status.json and
artifacts/android-emulator-analytics/us-final-result.json, native GPP snapshots
and screenshots 69, 72 and 74. App Store Connect app ID is 6828032990;
Google Play app ID is 4973120307842578235. The app PR remains unmerged.
