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
- Sandbox purchase/restore checks remain required before release; mocked purchase
  boundary checks passed, but no store sandbox transaction was performed.
- Website PR 21 was merged with Eyal's explicit approval: https://github.com/Eyal8/beno-studio-site/pull/21 . Verified the analytics section, date and request-ID instructions in the public HTML at https://beno74.com/privacy/landscraper .
- Review and submit App Store Connect App Privacy and Play Data safety using
  `store/LISTING.md`, reconciled with final native SDK behavior.
  Apple App Privacy was published on November 16: added Purchase History for Analytics, linked to the installation, not used for tracking. Existing device, location and interaction Analytics disclosures were already present. The optional User Privacy Choices URL was left blank after automatic approval review rejected an unverified choice-mechanism link; the existing policy URL remains correct. Google Play: added optional, non-ephemeral Purchase history for Analytics (collected, not shared under the service-provider exception) and the verified deletion-request instructions URL. One Data safety-only change was saved and quick checks passed. Two confirmed send attempts did not persist: after reload, Publishing overview still shows "Changes not yet submitted for review" without an error. Stopped per the two-attempt policy; owner should complete "Submit 1 change for review" from Publishing overview. No binary changes are included.
- Store privacy metadata updates were authorized; no app binary upload or public app release is authorized.

## AdMob and other settings

Owner approved account-wide combined AdMob consent on November 16, 2026.
Required account settings: Privacy & messaging → European regulations → Settings
→ enable Consent Mode for advertising purposes, then analytics purposes → Save.
These settings affect all configured European messages, not just Landscraper.
**Activation reported by owner, November 16, 2026:** both advertising and
analytics Consent Mode toggles were checked and saved. Earlier attempts by the
agent had encountered a loading settings page; that is no longer an owner task.
The saved settings and effective SDK/message values still require device proof.
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
