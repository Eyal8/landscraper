// Exercise the packaged startup order and monetization flows at the native plugin boundary.
// An optional directory allows the same checks to run against files extracted from an AAB.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const webDir = path.resolve(process.argv[2] || path.join(__dirname, '../www'));
const html = fs.readFileSync(path.join(webDir, 'index.html'), 'utf8');
const scripts = [...html.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script>/g)];
const testing = process.env.ADS_TEST !== 'false';
assert.equal(html.includes('    testing: true,'), testing, 'wrong ads build mode');
if (!testing) assert.ok(html.includes('const DEV_ALLOWED = false;'), 'developer mode must be disabled');
for (const [, attributes, code] of scripts) {
  if (!attributes.includes('src=')) new vm.Script(code); // Check every inline script, including gameplay.
}

const settle = () => new Promise(setImmediate);

async function boot(platform, missingRuntime = false, consentOptions = {}) {
  const calls = [];
  const listeners = new Map();
  const storage = new Map([['ls_pack_sea', '1']]); // Old simulated ownership must be reconciled.
  const elements = { adSim: { hidden: true }, adCount: {}, adClose: { focus() {} } };
  const state = { purchases: [], purchase: null, purchaseError: null, offline: false, reward: false, adFailure: false, modes: '2221', consentStatus: 'OBTAINED', consentFailure: false, ...consentOptions };
  let now = 100000;
  const record = (plugin, method, options) => calls.push({ plugin, method, options });
  const emit = (name) => { for (const callback of listeners.get(name) || []) callback({}); };
  const plugins = {
    NativePurchases: {
      async getPurchases(options) {
        record('NativePurchases', 'getPurchases', options);
        if (state.offline) throw new Error('offline');
        return { purchases: state.purchases };
      },
      async getProducts(options) {
        record('NativePurchases', 'getProducts', options);
        return { products: [{ identifier: 'landscraper_pack_sea', priceString: '₪10.90' }] };
      },
      async purchaseProduct(options) {
        record('NativePurchases', 'purchaseProduct', options);
        if (state.purchaseError) throw new Error(state.purchaseError);
        return state.purchase;
      },
      async restorePurchases() { record('NativePurchases', 'restorePurchases'); },
      async acknowledgePurchase(options) { record('NativePurchases', 'acknowledgePurchase', options); },
      addListener() { return Promise.resolve({ remove() {} }); }
    },
    AdMob: {
      async initialize(options) { record('AdMob', 'initialize', options); },
      async resetConsentInfo() {
        assert.equal(context.GameAnalytics.enabled(), false, 'test reset must stop collection first');
        record('AdMob', 'resetConsentInfo');
      },
      async requestConsentInfo(options) {
        record('AdMob', 'requestConsentInfo', options);
        if (state.consentFailure) throw Error('UMP unavailable');
        return { status: state.consentStatus, privacyOptionsRequirementStatus: 'REQUIRED' };
      },
      async showPrivacyOptionsForm() {
        assert.equal(context.GameAnalytics.enabled(), false, 'collection stops before opening privacy choices');
        state.modes = '2222';
      },
      async trackingAuthorizationStatus() { return { status: 'authorized' }; },
      async prepareRewardVideoAd(options) {
        record('AdMob', 'prepareRewardVideoAd', options);
        if (state.adFailure) throw new Error('no fill');
      },
      async prepareInterstitial(options) { record('AdMob', 'prepareInterstitial', options); },
      async showRewardVideoAd() {
        record('AdMob', 'showRewardVideoAd');
        if (state.reward) emit('onRewardedVideoAdReward');
        emit('onRewardedVideoAdDismissed');
        return {};
      },
      async showInterstitial() { record('AdMob', 'showInterstitial'); emit('interstitialAdDismissed'); },
      addListener(name, callback) {
        if (!listeners.has(name)) listeners.set(name, new Set());
        listeners.get(name).add(callback);
        return Promise.resolve({ remove() { listeners.get(name).delete(callback); } });
      }
    },
    AnalyticsConsent: { async getConsentModes() { return { values: state.modes }; } },
    FirebaseAnalytics: {
      async setEnabled(options) { record('FirebaseAnalytics', 'setEnabled', options); },
      async setConsent(options) { record('FirebaseAnalytics', 'setConsent', options); },
      async getAppInstanceId() { return { appInstanceId: 'test-installation' }; },
      async logEvent(options) { record('FirebaseAnalytics', 'logEvent', options); }
    },
    Games: {}
  };
  const context = {
    console, Event: class {},
    Date: class extends Date { static now() { return now; } },
    setTimeout(callback, ms) { if (ms === 250) queueMicrotask(callback); return 1; },
    clearTimeout() {}, setInterval() { return 1; }, clearInterval() {},
    localStorage: { getItem: (key) => storage.get(key), setItem: (key, value) => storage.set(key, value) },
    document: { getElementById: (id) => elements[id], dispatchEvent() {}, addEventListener() {} },
    Capacitor: { getPlatform: () => platform }
  };
  context.window = context;
  if (platform === 'android') context.androidBridge = {};
  if (platform === 'ios') context.webkit = { messageHandlers: { bridge: {} } };
  vm.createContext(context);
  for (const [, attributes, code] of scripts) {
    if (/src="capacitor\.js"/.test(attributes)) {
      if (!missingRuntime) {
        vm.runInContext(fs.readFileSync(path.join(webDir, 'capacitor.js'), 'utf8'), context);
        // Keep the real runtime's platform detection; replace only the native plugin boundary.
        context.capacitorExports.registerPlugin = (name) => {
          record(name, 'register');
          return plugins[name];
        };
      }
    } else if (code.includes('window.UMPTest =') || code.includes('window.GameAnalytics =') || code.includes('window.Store =') || code.includes('window.Ads =')) {
      vm.runInContext(code, context);
    }
  }
  await settle();
  return { context, calls, state, elements, advance() { now += 200000; } };
}

async function testNative(platform) {
  const { context: c, calls, state, elements, advance } = await boot(platform);
  for (const name of ['NativePurchases', 'AdMob', 'Games']) {
    assert.ok(calls.some((x) => x.plugin === name && x.method === 'register'), `${platform}: ${name} must register at startup`);
  }
  assert.equal(c.Store.isNative, true);
  if (c.GameAnalytics.available) {
    assert.equal(c.GameAnalytics.enabled(), true, 'startup consumes the current UMP grant');
    assert.ok(calls.findIndex(x => x.plugin === 'FirebaseAnalytics' && x.method === 'setEnabled') < calls.findIndex(x => x.plugin === 'AdMob' && x.method === 'initialize'), 'Firebase initializes before UMP');
  }
  const analyticsEvents = (name) => calls.filter(x => x.method === 'logEvent' && x.options.name === name);
  assert.equal(c.Store.owns('sea'), false, 'unpaid cached ownership must be cleared after store refresh');
  assert.equal(c.Store.price('sea'), '₪10.90', 'use the native store price');
  assert.equal(calls.find((x) => x.method === 'initialize').options.initializeForTesting, testing);
  for (const call of calls.filter((x) => x.method.startsWith('prepare'))) {
    assert.equal(call.options.isTesting, testing);
    assert.ok(call.options.adId.startsWith('ca-app-pub-5535097818156227/'), 'must use our ad units');
  }

  state.purchase = { productIdentifier: 'landscraper_pack_sea', purchaseState: '1' };
  assert.equal(await c.Store.buy('sea'), 'bought');
  assert.ok(calls.some((x) => x.method === 'purchaseProduct' && x.options.autoAcknowledgePurchases));
  assert.equal(c.Store.owns('sea'), true);
  await settle();
  if (c.GameAnalytics.available) assert.equal(analyticsEvents('purchase_completed').length, 1);
  state.purchaseError = 'user cancelled';
  assert.equal(await c.Store.buy('space'), 'cancelled');
  assert.equal(c.Store.owns('space'), false);
  state.purchaseError = 'billing unavailable';
  assert.equal(await c.Store.buy('space'), 'error');
  assert.equal(c.Store.owns('space'), false);
  state.purchaseError = null;
  state.purchase = { productIdentifier: 'landscraper_pack_space', purchaseState: '2' };
  if (platform === 'android') {
    assert.equal(await c.Store.buy('space'), 'error', 'pending purchase must not unlock');
    assert.equal(c.Store.owns('space'), false);
  }

  state.purchases = [{ productIdentifier: 'landscraper_pack_pool', purchaseState: '1', isAcknowledged: false, purchaseToken: 'test-token' }];
  assert.ok((await c.Store.restore()).includes('pool'));
  assert.equal(c.Store.owns('sea'), false, 'store owns the entitlement record');
  if (platform === 'android') assert.ok(calls.some((x) => x.method === 'acknowledgePurchase'));
  state.offline = true;
  await c.Store.refresh();
  assert.equal(c.Store.owns('pool'), true, 'offline refresh preserves verified ownership');
  state.offline = false;
  state.purchases[0].revocationDate = '2026-11-15';
  await c.Store.refresh();
  assert.equal(c.Store.owns('pool'), false, 'revoked purchase must not stay unlocked');
  await settle();
  if (c.GameAnalytics.available) assert.equal(analyticsEvents('purchase_completed').length, 1, 'cancelled, failed, pending and restored purchases must not count as new purchases');

  assert.equal(await c.Ads.showRewarded('continue'), false, 'closing an ad without reward gives no reward');
  state.reward = true;
  assert.equal(await c.Ads.showRewarded('dailyRetry'), true);
  advance();
  await c.Ads.maybeInterstitial(2);
  assert.ok(calls.some((x) => x.method === 'showInterstitial'));
  state.adFailure = true;
  assert.equal(await c.Ads.showRewarded('rushTime'), false, 'no fill gives no reward');
  assert.equal(elements.adSim.hidden, true, 'native ads must never open the browser simulator');
  await settle();
  if (c.GameAnalytics.available) assert.equal(analyticsEvents('rewarded_ad_completed').length, 1, 'only earned real ad rewards count as completed videos');
  console.log(`PASS ${platform}: startup, prices, purchases, cancellation/failure, restore/revocation, rewarded/interstitial ads`);
}

(async () => {
  await testNative('android');
  await testNative('ios');
  for (const platform of ['android', 'ios']) {
    for (const consentOptions of [{ modes: '2222' }, { modes: '3334', consentStatus: 'NOT_REQUIRED' }, { consentFailure: true }, { consentStatus: 'REQUIRED' }]) {
      const { context: c } = await boot(platform, false, consentOptions);
      assert.equal(c.GameAnalytics.enabled(), false, 'denial, no regional signal or failed/incomplete UMP keeps collection off');
    }
    for (const consentStatus of ['OBTAINED', 'NOT_REQUIRED']) {
      const { context: noPrompt, calls: noPromptCalls } = await boot(platform, false, { modes: '3333', consentStatus });
      if (noPrompt.GameAnalytics.available) assert.equal(noPrompt.GameAnalytics.enabled(), true, 'purpose-specific not-applicable signal permits measurement');
      assert.ok(!noPromptCalls.some(x => x.method === 'showConsentForm'), 'do not add a consent prompt');
    }
    const { context: c, calls: privacyCalls } = await boot(platform);
    await c.Ads.showPrivacyOptions();
    assert.equal(c.GameAnalytics.enabled(), false, 'revocation in UMP is reflected in Analytics');
    if (c.UMPTest) {
      assert.throws(() => c.UMPTest.save(1, ''), /test device ID/);
      const device = 'A'.repeat(32);
      c.UMPTest.save(1, device);
      await c.Ads.resetConsentForTest();
      const options = (await boot(platform)).calls; // startup remains independent of another device's config
      assert.ok(options.filter(x => x.method === 'requestConsentInfo').every(x => !x.options.debugGeography));
      assert.equal(c.UMPTest.options().debugGeography, 1);
      assert.ok(privacyCalls.some(x => x.method === 'resetConsentInfo'));
      const request = privacyCalls.filter(x => x.method === 'requestConsentInfo').at(-1);
      assert.equal(request.options.debugGeography, 1);
      assert.equal(request.options.testDeviceIdentifiers[0], device);
      assert.equal(c.GameAnalytics.enabled(), false, 'a test reset does not manufacture analytics consent');
    }
  }
  console.log('PASS Android/iOS: UMP startup, not-required measurement, missing signals, errors, incomplete consent and withdrawal');
  for (const platform of ['android', 'ios']) {
    const { context: c, elements, advance } = await boot(platform, true);
    assert.equal(await c.Store.buy('space'), 'error');
    assert.equal(c.Store.owns('space'), false);
    assert.equal(await c.Ads.showRewarded('continue'), false);
    advance();
    await c.Ads.maybeInterstitial(2);
    assert.equal(elements.adSim.hidden, true);
  }
  console.log('PASS missing native runtime: no simulated purchase or ad reward');
  const { context: c, elements } = await boot('web');
  assert.equal(await c.Store.buy('space'), 'bought');
  const ad = c.Ads.showRewarded('continue');
  assert.equal(elements.adSim.hidden, false);
  elements.adClose.onclick();
  assert.equal(await ad, true);
  console.log('PASS browser preview: simulated purchases and ads remain available');
})().catch((error) => { console.error(error); process.exitCode = 1; });
