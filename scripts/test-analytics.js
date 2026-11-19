// Consent is a release-critical boundary: exercise it without a network or device.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const { test } = require('node:test');
const html = fs.readFileSync(require('node:path').join(__dirname, '../src/game.html'), 'utf8');
const source = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].find(x => x[1].includes('window.GameAnalytics ='))[1];

function boot({ modes = '', paused = false, native = true, storeBuild = true, storageFails = false, nativeFails = false, oldConsent, onEnable } = {}) {
  const calls = [], values = new Map([['ls_analytics_paused', paused ? '1' : '0'], ['ls_analytics_consent_v1', oldConsent]]);
  const state = { modes };
  const plugin = Object.fromEntries(['setEnabled', 'setConsent', 'logEvent', 'getAppInstanceId'].map(method =>
    [method, async options => {
      calls.push({ method, options });
      if (nativeFails) throw Error('native unavailable');
      if (method === 'setEnabled' && options.enabled === true && onEnable) await onEnable();
      return { appInstanceId: 'installation-123' };
    }]));
  const consentPlugin = { async getConsentModes() { if (nativeFails) throw Error('bridge'); return { values: state.modes }; } };
  const context = { AgeAssurance: { analyticsAllowed: () => true }, Promise, Event, document: { dispatchEvent() {} },
    localStorage: { getItem: key => values.get(key) || null, setItem(key, value) { if (storageFails) throw Error('storage'); values.set(key, value); } },
    Capacitor: { isNativePlatform: () => native }, capacitorExports: { registerPlugin: name => name === 'AnalyticsConsent' ? consentPlugin : plugin } };
  context.window = context;
  vm.runInNewContext(storeBuild ? source.replace('const ANALYTICS_ALLOWED = false;', 'const ANALYTICS_ALLOWED = true;') : source, context);
  return { analytics: context.GameAnalytics, calls, values, state, context };
}
const settle = () => new Promise(setImmediate);
const events = s => s.calls.filter(x => x.method === 'logEvent');

test('missing, denied, unconfigured and malformed signals fail closed', async () => {
  for (const modes of ['', '2220', '1112', '1114', '1', '11111', 'xxx1']) {
    const s = boot({ modes, oldConsent: 'granted' });
    await s.analytics.reconcile('OBTAINED');
    s.analytics.track('level_start', { level_name: 'no-consent' });
    await settle();
    assert.equal(events(s).length, 0, modes);
    assert.ok(!s.calls.some(x => x.options?.enabled === true || x.options?.status === 'GRANTED'), modes);
  }
});
test('a cached UMP grant does not enable collection before a successful current UMP update', async () => {
  const s = boot({ modes: '2221' });
  await settle();
  assert.equal(s.analytics.enabled(), false);
  await s.analytics.reconcile(false);
  assert.equal(s.analytics.enabled(), false);
});
test('explicit analytics grant precedes collection without granting advertising; fields are allowlisted', async () => {
  const s = boot({ modes: '1111' });
  await s.analytics.reconcile('OBTAINED');
  s.analytics.track('level_start', { level_name: 'meadow-01', mode: 'campaign', email: 'private@example.test', receipt: 'secret' });
  s.analytics.track('unknown_event', { secret: 'value' });
  await settle();
  assert.equal(events(s).length, 1);
  assert.deepEqual(JSON.parse(JSON.stringify(events(s)[0].options)), { name: 'level_start', params: { mode: 'campaign', level_name: 'meadow-01' } });
  assert.ok(s.calls.findIndex(x => x.options?.type === 'ANALYTICS_STORAGE' && x.options?.status === 'GRANTED') < s.calls.findIndex(x => x.options?.enabled === true));
  assert.ok(!s.calls.some(x => x.options?.type?.startsWith('AD_') && x.options.status !== 'DENIED'));
  assert.equal(s.analytics.requestId(), 'installation-123');
});
test('privacy form entry blocks queued events; denial remains off and retains the request ID', async () => {
  const s = boot({ modes: '2221' });
  await s.analytics.reconcile('OBTAINED');
  s.analytics.track('level_start', { level_name: 'queued' });
  await s.analytics.reconcile(false);
  s.state.modes = '2222';
  await s.analytics.reconcile('OBTAINED');
  assert.equal(events(s).length, 0);
  assert.equal(s.analytics.enabled(), false);
  assert.equal(s.analytics.requestId(), 'installation-123');
});
test('device pause survives reconciliation/relaunch and resume never substitutes for UMP consent', async () => {
  const s = boot({ modes: '2221' });
  await s.analytics.reconcile('OBTAINED');
  await s.analytics.setPaused(true);
  await s.analytics.reconcile('OBTAINED');
  assert.equal(s.analytics.enabled(), false);
  const restarted = boot({ modes: '2221', paused: s.values.get('ls_analytics_paused') === '1' });
  await restarted.analytics.reconcile('OBTAINED');
  assert.equal(restarted.analytics.enabled(), false);
  s.state.modes = '2222';
  await s.analytics.setPaused(false);
  assert.equal(s.analytics.enabled(), false);
});
test('preview, default tester builds, unavailable storage and native failures fail closed', async () => {
  for (const options of [{ native: false }, { storeBuild: false }, { storageFails: true }, { nativeFails: true }]) {
    const s = boot({ modes: '2221', ...options });
    await s.analytics.reconcile('OBTAINED');
    await s.analytics.setPaused(false);
    s.analytics.track('purchase_completed', { item_id: 'landscraper_no_ads' });
    await settle();
    assert.equal(events(s).length, 0);
    assert.equal(s.analytics.enabled(), false);
  }
});
test('an obsolete in-flight consent read cannot enable collection after suspension', async () => {
  const s = boot({ modes: '2221' });
  const grant = s.analytics.reconcile('OBTAINED');
  const suspend = s.analytics.reconcile(false);
  await Promise.all([grant, suspend]);
  assert.equal(s.analytics.enabled(), false);
  assert.ok(!s.calls.some(x => x.options?.enabled === true));
});

test('pause during native enable never reopens collection or emits stale events', async () => {
  let release, started;
  const enabling = new Promise(resolve => { started = resolve; });
  const held = new Promise(resolve => { release = resolve; });
  const s = boot({ modes: '2221', onEnable: () => { started(); return held; } });
  const grant = s.analytics.reconcile('OBTAINED');
  await enabling;
  const pause = s.analytics.setPaused(true);
  release();
  await Promise.all([grant, pause]);
  s.analytics.track('level_start', { mode: 'campaign', level_name: 'meadow-01' });
  await settle();
  assert.equal(s.analytics.enabled(), false);
  assert.equal(events(s).length, 0);
  assert.equal(s.calls.filter(c => c.method === 'getAppInstanceId').length, 0);
  assert.equal(s.calls.filter(c => c.method === 'setEnabled').at(-1).options.enabled, false);
});

test('Settings directly exposes policy and required UMP choices; denial stops analytics', async () => {
  const s = boot({ modes: '1111' });
  await s.analytics.reconcile('OBTAINED');
  let rendered, required = true, forms = 0;
  Object.assign(s.context, { BACK_X: '', dev: false, toMenu() {}, showHome() {}, settingsButtons: () => ({ html: '', acts: {} }),
    $: () => ({ addEventListener() {}, classList: { add() {} } }),
    panel(content, actions) { rendered = { content, actions }; },
    Ads: { privacyRequired: () => required, async showPrivacyOptions() {
      forms++; await s.analytics.reconcile(false); s.state.modes = '1112';
      await s.analytics.reconcile('OBTAINED');
    } } });
  const privacy = html.slice(html.indexOf('  function showSettings()'), html.indexOf('  async function showUMPTestSettings('));
  vm.runInNewContext(privacy + '; window.openPrivacyForTest = showSettings;', s.context);
  await s.context.openPrivacyForTest();
  assert.match(rendered.content, /Privacy policy/);
  assert.match(rendered.content, /Privacy choices/);
  assert.doesNotMatch(rendered.content, /Analytics:|Pause|Resume|mailto:|privacy request/i);
  await rendered.actions.privacyChoices();
  assert.equal(forms, 1); assert.equal(s.analytics.enabled(), false);
  s.analytics.track('level_start', { mode: 'campaign', level_name: 'meadow-01' });
  await settle(); assert.equal(events(s).length, 0);
  assert.equal(s.calls.filter(c => c.method === 'setEnabled').at(-1).options.enabled, false);
  required = false; await s.context.openPrivacyForTest();
  assert.match(rendered.content, /data-act="privacyChoices" hidden/);
  assert.doesNotMatch(html, /async function showPrivacy\(/);
});

test('not-applicable analytics works after a resolved UMP update with either completed status', async () => {
  const s = boot({ modes: '3333' });
  await settle();
  assert.equal(s.analytics.enabled(), false, 'cached values do not enable startup');
  for (const status of ['REQUIRED', 'UNKNOWN', false]) {
    await s.analytics.reconcile(status);
    assert.equal(s.analytics.enabled(), false, status);
  }
  await s.analytics.reconcile('NOT_REQUIRED');
  s.analytics.track('level_start', { level_name: 'meadow-01' });
  await settle();
  assert.equal(events(s).length, 1);
  assert.equal(s.analytics.enabled(), true);
  await s.analytics.setPaused(true);
  await s.analytics.reconcile('NOT_REQUIRED');
  assert.equal(s.analytics.enabled(), false, 'device opt-out overrides not-required');
});
test('NOT_REQUIRED never overrides an explicit denial or missing/unconfigured analytics signal', async () => {
  for (const modes of ['', '3330', '3332', '3334']) {
    const s = boot({ modes });
    await s.analytics.reconcile('NOT_REQUIRED');
    assert.equal(s.analytics.enabled(), false, modes);
  }
});

test('iPhone build 196 regression: OBTAINED with 3333 permits analytics and pause still wins', async () => {
  const s = boot({ modes: '3333' });
  await s.analytics.reconcile('OBTAINED');
  assert.equal(s.analytics.enabled(), true);
  s.analytics.track('level_start', { level_name: 'meadow-01' });
  await settle();
  assert.equal(events(s).length, 1);
  assert.ok(!s.calls.some(x => x.options?.type?.startsWith('AD_') && x.options.status !== 'DENIED'));
  await s.analytics.setPaused(true);
  await s.analytics.reconcile('OBTAINED');
  assert.equal(s.analytics.enabled(), false);
});
