const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const { execFileSync } = require('node:child_process');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const read = (p) => fs.readFileSync(path.join(root, p), 'utf8');
const source = read('src/game.html');
const boardSource = source.match(/window.Board = \(function \(\) \{[\s\S]*?\n\}\)\(\);/)[0];
const settle = () => new Promise(setImmediate);

// Use the actual Capacitor runtime with a controlled native transport.
function app(platform = 'ios', behavior = {}) {
  const calls = [], events = [], warnings = [], timers = [], listeners = {};
  const context = vm.createContext({
    console: { warn: (s) => warnings.push(s) },
    document: { dispatchEvent: (e) => events.push(e.type) },
    Event: class { constructor(type) { this.type = type; } },
    setTimeout: (fn, ms) => { timers.push({ fn, ms }); }
  });
  context.window = context;
  if (platform === 'ios') context.webkit = { messageHandlers: { bridge: {} } };
  if (platform === 'android') context.androidBridge = {};
  context.Capacitor = {
    PluginHeaders: behavior.missingPlugin ? [] : [{ name: 'Games', methods: [{ name: 'addListener' }, { name: 'removeListener' }, ...['signIn', 'submitScore', 'showLeaderboard'].map(name => ({ name, rtype: 'promise' }))] }],
    nativeCallback: (_plugin, method, options, callback) => {
      if (method === 'addListener') listeners[options.eventName] = callback;
      return 'test-listener';
    },
    nativePromise: async (plugin, method, args) => {
      calls.push({ plugin, method, args });
      if (behavior[method]) return behavior[method](args);
      return method === 'signIn' ? { authenticated: true } : {};
    }
  };
  vm.runInContext(read('node_modules/@capacitor/core/dist/capacitor.js'), context);
  vm.runInContext(boardSource, context);
  return { board: context.Board, calls, events, warnings, timers, listeners };
}

test('both tester and store output load Capacitor before every native consumer', () => {
  for (const adsTest of ['true', 'false']) {
    execFileSync(process.execPath, ['scripts/build-web.js'], { cwd: root, env: { ...process.env, ADS_TEST: adsTest } });
    const html = read('www/index.html');
    const runtime = html.indexOf('<script src="capacitor.js"></script>');
    assert.equal(html.match(/<script src="capacitor.js"><\/script>/g).length, 1);
    for (const consumer of ['window.Store =', 'window.Ads =', 'window.Board =']) {
      assert.ok(runtime < html.indexOf(consumer), consumer + ' must have the runtime at initialization');
    }
    for (const [, inline] of html.matchAll(/<script>([\s\S]*?)<\/script>/g)) new vm.Script(inline);
    assert.ok(html.includes('const DEV_ALLOWED = ' + (adsTest === 'false' ? 'false' : 'true')));
  }
});

test('iOS initializes without a delay and uses native authentication state', async () => {
  const a = app();
  await settle();
  assert.equal(a.board.available, true);
  assert.equal(a.board.status(), 'signed in');
  assert.equal(a.calls.filter(c => c.method === 'signIn').length, 1);
  assert.equal(a.timers.length, 0);
  a.listeners.authenticationChanged({ authenticated: false });
  assert.equal(a.board.status(), 'not signed in');
});

test('overlapping startup, sign-in and leaderboard requests wait for authentication', async () => {
  let finish;
  const a = app('ios', { signIn: () => new Promise(resolve => { finish = resolve; }) });
  const signIn = a.board.signIn(true), showing = a.board.show('daily');
  await settle();
  assert.equal(a.calls.filter(c => c.method === 'signIn').length, 1);
  assert.equal(a.calls.filter(c => c.method === 'showLeaderboard').length, 0);
  finish({ authenticated: true });
  await Promise.all([signIn, showing]);
  assert.equal(a.calls.find(c => c.method === 'showLeaderboard').args.id, 'com.beno74.landscraper.daily');
});

test('signed-out iOS does not submit or present; explicit taps report unavailability', async () => {
  const a = app('ios', { signIn: async () => ({ authenticated: false }) });
  await a.board.show('rush');
  await a.board.submit('daily', 12.34);
  assert.ok(a.calls.every(c => c.method === 'signIn'));
  assert.deepEqual(a.events, ['leaderboard:unavailable']);
});

test('offline/authentication errors settle safely and log only error codes', async () => {
  const a = app('ios', { signIn: async () => { throw { code: 'GKErrorDomain:3', message: 'private player detail' }; } });
  assert.equal(await a.board.signIn(false), false);
  await a.board.show('daily');
  a.listeners.authenticationChanged({ authenticated: false });
  assert.match(a.board.status(), /GKErrorDomain:3/);
  assert.ok(a.warnings.every(s => !s.includes('private player detail')));
  assert.deepEqual(a.events, ['leaderboard:unavailable']);
});

test('Daily/Rush IDs and existing score conversion are preserved', async () => {
  for (const platform of ['ios', 'android']) {
    const a = app(platform);
    await a.board.submit('daily', 12.34);
    await a.board.submit('rush', 4321);
    await a.board.show('rush');
    const submitted = a.calls.filter(c => c.method === 'submitScore');
    assert.equal(submitted[0].args.id, platform === 'ios' ? 'com.beno74.landscraper.daily' : 'CgkIqb3wx_MBEAIQAQ');
    assert.equal(submitted[0].args.score, platform === 'ios' ? 1234 : 12340);
    assert.equal(submitted[1].args.id, platform === 'ios' ? 'com.beno74.landscraper.rush' : 'CgkIqb3wx_MBEAIQAg');
    assert.equal(submitted[1].args.score, 4321);
    assert.equal(a.calls.find(c => c.method === 'showLeaderboard').args.id, submitted[1].args.id);
  }
});

test('iOS refreshes a stale signed-in state before submission', async () => {
  let authenticated = true;
  const a = app('ios', { signIn: async () => ({ authenticated }) });
  await settle();
  authenticated = false;
  await a.board.submit('rush', 300);
  assert.equal(a.calls.filter(c => c.method === 'submitScore').length, 0);
  assert.equal(a.board.status(), 'not signed in');
});

test('failed presentation is reported without rejecting into gameplay', async () => {
  const a = app('ios', { showLeaderboard: async () => { throw { code: 'PRESENTATION_UNAVAILABLE' }; } });
  await a.board.show('rush');
  assert.match(a.board.status(), /PRESENTATION_UNAVAILABLE/);
  assert.deepEqual(a.events, ['leaderboard:unavailable']);
});

test('web remains offline-capable and Android retains its startup timing', async () => {
  const web = app('web');
  assert.equal(web.board.available, false);
  assert.equal(await web.board.signIn(false), false);
  await web.board.submit('daily', 12);
  await web.board.show('rush');
  assert.equal(web.calls.length, 0);
  const android = app('android');
  assert.equal(android.calls.length, 0);
  assert.equal(android.timers[0].ms, 1500);
  android.timers[0].fn();
  await settle();
  assert.equal(android.board.status(), 'signed in');
});

test('a missing iOS native plugin is diagnosed without an unhandled listener rejection', async () => {
  const a = app('ios', { missingPlugin: true });
  await settle();
  assert.equal(a.board.available, false);
  assert.equal(a.board.status(), 'Game Center bridge unavailable');
  assert.deepEqual(a.warnings, ['[GameCenter] bridge unavailable']);
  assert.equal(a.calls.length, 0);
});

test('the scene startup and storyboard both select the plugin-registering controller', () => {
  assert.match(read('ios/App/App/SceneDelegate.swift'), /rootViewController = MainViewController\(\)/);
  assert.match(read('ios/App/App/Base.lproj/Main.storyboard'), /customClass="MainViewController"/);
  assert.match(read('ios/App/App/GamesPlugin.swift'), /registerPluginInstance\(games\)/);
});
