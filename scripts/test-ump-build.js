// Verify the real packaging boundary: UMP QA may never ship with production ads.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const { spawnSync } = require('node:child_process');
const path = require('node:path');
const root = path.join(__dirname, '..');
const htmlPath = path.join(root, 'www/index.html');
const originalHTML = fs.readFileSync(htmlPath);
function build(env) {
  return spawnSync(process.execPath, ['scripts/build-web.js'], { cwd: root, env: { ...process.env, ...env }, encoding: 'utf8' });
}
try {
  for (const env of [
    { ADS_TEST: 'true', ANALYTICS_TEST: 'false', UMP_TEST: 'false' },
    { ADS_TEST: 'false', ANALYTICS_TEST: 'false', UMP_TEST: 'false' },
    { ADS_TEST: 'true', ANALYTICS_TEST: 'true', UMP_TEST: 'true' }
  ]) {
    const result = build(env);
    assert.equal(result.status, 0, result.stderr);
    const html = fs.readFileSync(path.join(root, 'www/index.html'), 'utf8');
    assert.equal(html.includes('window.UMPTest ='), env.UMP_TEST === 'true');
    assert.equal(html.includes('const ANALYTICS_ALLOWED = true;'), env.ADS_TEST === 'false' || env.ANALYTICS_TEST === 'true');
  }
  for (const env of [
    { ADS_TEST: 'false', ANALYTICS_TEST: 'true', UMP_TEST: 'true' },
    { ADS_TEST: 'true', ANALYTICS_TEST: 'false', UMP_TEST: 'true' }
  ]) assert.notEqual(build(env).status, 0, 'unsafe QA build must fail');
  console.log('PASS UMP test configuration is removed from normal/store builds; unsafe combinations are rejected');
} finally {
  fs.writeFileSync(htmlPath, originalHTML);
}
