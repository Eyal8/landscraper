// Consent is a release-critical boundary: exercise it without a network or device.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const { test } = require('node:test');
const html = fs.readFileSync(require('node:path').join(__dirname, '../src/game.html'), 'utf8');
const source = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].find(x => x[1].includes('window.GameAnalytics ='))[1];

function boot({ consent, native = true, storeBuild = true, storageFails = false, nativeFails = false } = {}) {
  const calls = [], values = new Map(consent ? [['ls_analytics_consent_v1', consent]] : []);
  const plugin = Object.fromEntries(['setEnabled', 'setConsent', 'logEvent', 'getAppInstanceId'].map(method =>
    [method, async options => {
      calls.push({ method, options });
      if (nativeFails) throw Error('native unavailable');
      return { appInstanceId: 'installation-123' };
    }]));
  const context = { Promise, Event, document: { dispatchEvent() {} },
    localStorage: { getItem: key => values.get(key) || null, setItem(key, value) { if (storageFails) throw Error('storage'); values.set(key, value); } },
    Capacitor: { isNativePlatform: () => native }, capacitorExports: { registerPlugin: () => plugin } };
  context.window = context;
  vm.runInNewContext(storeBuild ? source.replace('const ANALYTICS_ALLOWED = false;', 'const ANALYTICS_ALLOWED = true;') : source, context);
  return { analytics: context.GameAnalytics, calls, values };
}
const settle = () => new Promise(setImmediate);
const events = s => s.calls.filter(x => x.method === 'logEvent');

test('unknown or denied consent never grants storage or logs', async () => {
  for (const consent of [undefined, 'denied']) {
    const s = boot({ consent });
    await settle();
    s.analytics.track('level_start', { level_name: 'meadow-01' });
    await settle();
    assert.equal(events(s).length, 0);
    assert.ok(!s.calls.some(x => x.options?.enabled === true || x.options?.status === 'GRANTED'));
  }
});
test('opt-in precedes collection; only approved event fields leave the app', async () => {
  const s = boot();
  s.analytics.track('level_start', { level_name: 'before-consent' });
  await s.analytics.setChoice(true);
  s.analytics.track('level_start', { level_name: 'meadow-01', mode: 'campaign', email: 'private@example.test', receipt: 'secret' });
  s.analytics.track('unknown_event', { secret: 'value' });
  await settle();
  assert.equal(events(s).length, 1);
  assert.deepEqual(JSON.parse(JSON.stringify(events(s)[0].options)), { name: 'level_start', params: { mode: 'campaign', level_name: 'meadow-01' } });
  assert.ok(s.calls.findIndex(x => x.options?.type === 'ANALYTICS_STORAGE' && x.options?.status === 'GRANTED') < s.calls.findIndex(x => x.options?.enabled === true));
  assert.ok(!s.calls.some(x => x.options?.type?.startsWith('AD_') && x.options.status !== 'DENIED'));
  assert.equal(s.analytics.requestId(), 'installation-123');
});
test('withdrawal drops queued events and survives reconciliation/relaunch', async () => {
  const s = boot({ consent: 'granted' });
  await settle();
  s.analytics.track('level_start', { level_name: 'queued' });
  await s.analytics.setChoice(false);
  s.analytics.track('level_start', { level_name: 'after-withdrawal' });
  await s.analytics.reconcile();
  assert.equal(events(s).length, 0);
  assert.equal(s.analytics.enabled(), false);
  assert.equal(s.analytics.requestId(), 'installation-123', 'retain request ID for historical deletion requests');
  const restarted = boot({ consent: s.values.get('ls_analytics_consent_v1') });
  await settle();
  assert.equal(restarted.analytics.enabled(), false);
});
test('preview, tester builds and unavailable consent storage fail closed', async () => {
  for (const options of [{ native: false }, { storeBuild: false }, { storageFails: true }, { nativeFails: true }]) {
    const s = boot(options);
    await s.analytics.setChoice(true);
    s.analytics.track('purchase_completed', { item_id: 'landscraper_no_ads' });
    await settle();
    assert.equal(events(s).length, 0);
    assert.equal(s.analytics.enabled(), false);
  }
});
