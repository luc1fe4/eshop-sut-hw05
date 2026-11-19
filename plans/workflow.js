import http from 'k6/http';
import { check, sleep } from 'k6';
import { SharedArray } from 'k6/data';
import exec from 'k6/execution';
import { Counter, Rate, Trend } from 'k6/metrics';

const base = (__ENV.BASE_URL || 'http://127.0.0.1:3000').replace(/\/$/, '');
if (!/^http:\/\/(localhost|127\.0\.0\.1):\d+$/.test(base)) {
  throw new Error('This plan permits only local HTTP targets. Review authorized target explicitly before adapting.');
}
if (!__ENV.CSV_PATH || !__ENV.RUN_ID) throw new Error('CSV_PATH and RUN_ID required');
const rows = new SharedArray('m5-csv', () => {
  // Generator deliberately produces plain fields without quotes, commas or newlines.
  const lines = open(__ENV.CSV_PATH).trim().split(/\r?\n/);
  if (lines.shift() !== 'name,email,password,newPassword') throw new Error('Wrong CSV header');
  const seen = new Set();
  return lines.map(line => {
    const fields = line.split(',');
    if (fields.length !== 4 || fields.some(x => !x || /["\r\n]/.test(x))) throw new Error('Invalid generated CSV');
    const [name, email, password, newPassword] = fields;
    if (!email.startsWith(`m5-${__ENV.RUN_ID}-`) || !email.endsWith('@example.invalid') || seen.has(email)) throw new Error('Wrong namespace or duplicate');
    const strong = x => /[A-Z]/.test(x) && /[a-z]/.test(x) && /\d/.test(x) && /[@$!%*?&]/.test(x) && x.length >= 8;
    if (!strong(password) || !strong(newPassword) || password === newPassword) throw new Error('Invalid password schema');
    seen.add(email);
    return {name,email,password,newPassword};
  });
});
const started = new Counter('m5_started');
const finished = new Counter('m5_finished');
const passed = new Counter('m5_passed');
const e2e = new Rate('m5_e2e_success');
const durationAll = new Trend('m5_e2e_all_ms', true);
const durationOK = new Trend('m5_e2e_success_ms', true);
const failedStep = new Counter('m5_failed_step');
const exhausted = new Counter('m5_csv_exhausted');

export function workflow() {
  const t = Date.now();
  started.add(1);
  let ok = false;
  let step = 'csv';
  try {
    const row = rows[exec.scenario.iterationInTest];
    if (!row) {
      exhausted.add(1);
      exec.test.abort('CSV exhausted: generate more unique rows; never wrap');
      return;
    }
    const send = (key, path, body, assertion, jwt) => {
      step = key;
      const params = {headers:{'Content-Type':'application/json'},
        tags:{endpoint:key, name:path}, timeout:'10s', redirects:0};
      if (jwt) params.headers.Authorization = `Bearer ${jwt}`;
      const res = body === null ? http.get(base + path, params) : http.post(base + path, JSON.stringify(body), params);
      let data;
      try { data = res.json(); } catch (_) { data = null; }
      const valid = check(res, {
        [`${key}: status 200`]: r => r.status === 200,
        [`${key}: business contract`]: () => data !== null && assertion(data),
      }, {endpoint:key});
      return valid ? data : null;
    };
    const registered = send('register', '/api/register', {name:row.name,email:row.email,password:row.password},
      d => d.message === 'User registered successfully' && Number.isInteger(d.id) && d.id > 0);
    if (!registered) return;
    const forgot = send('forgot', '/api/forgot-password', {email:row.email},
      d => typeof d.resetToken === 'string' && /^\d+$/.test(d.resetToken));
    if (!forgot) return;
    const reset = send('reset', '/api/reset-password', {email:row.email,resetToken:forgot.resetToken,newPassword:row.newPassword},
      d => d.message === 'Password reset successfully');
    if (!reset) return;
    const login = send('login', '/api/login', {email:row.email,password:row.newPassword},
      d => typeof d.token === 'string' && d.token.split('.').length === 3 && d.user && d.user.id === registered.id && d.user.email === row.email);
    if (!login) return;
    const cart = send('cart', '/api/cart', null, d => Array.isArray(d) && d.length === 0, login.token);
    if (!cart) return;
    ok = true;
  } catch (_) {
    // Never log exception contents: they could contain requests or credentials.
  } finally {
    finished.add(1);
    e2e.add(ok);
    durationAll.add(Date.now() - t);
    if (ok) { passed.add(1); durationOK.add(Date.now() - t); }
    else failedStep.add(1, {step});
    // finally also runs on early return; pace failed iterations as well.
    sleep(Number(__ENV.THINK_SECONDS || 1));
  }
  // Pacing is outside measured E2E; also pace failures to avoid retry storms.
}

export function optionsFor(profile) {
  let scenario;
  if (__ENV.MODE === 'smoke') {
    scenario = {executor:'shared-iterations',vus:1,iterations:Number(__ENV.ITERATIONS || 5),maxDuration:'2m'};
  } else if (__ENV.MODE === 'soak') {
    scenario = {executor:'constant-vus',vus:Number(__ENV.VUS || 2),duration:__ENV.DURATION || '10m'};
  } else {
    const drafts = {
      Load:[{duration:'30s',target:2},{duration:'2m',target:2},{duration:'15s',target:0}],
      Stress:[{duration:'15s',target:2},{duration:'45s',target:2},{duration:'15s',target:5},{duration:'45s',target:5},{duration:'15s',target:10},{duration:'45s',target:10},{duration:'15s',target:0}],
      Spike:[{duration:'15s',target:2},{duration:'45s',target:2},{duration:'2s',target:15},{duration:'30s',target:15},{duration:'2s',target:2},{duration:'60s',target:2},{duration:'10s',target:0}],
    };
    scenario = {executor:'ramping-vus',startVUs:0,stages:__ENV.STAGES_JSON ? JSON.parse(__ENV.STAGES_JSON) : drafts[profile]};
    scenario.gracefulRampDown = '15s';
  }
  scenario.gracefulStop = '15s';
  return {scenarios:{m5:scenario},tags:{run_id:__ENV.RUN_ID,profile},
    systemTags:['status','method','name','scenario','expected_response'],
    thresholds:{http_req_failed:['rate<0.01'],m5_e2e_success:['rate>0.99'],m5_csv_exhausted:['count==0'],
      ...Object.fromEntries(['register','forgot','reset','login','cart'].map(x => [`http_req_duration{endpoint:${x}}`,['p(95)<500']])),
      m5_e2e_success_ms:['p(95)<2000']},
    summaryTrendStats:['avg','min','med','max','p(90)','p(95)','p(99)']};
}

export function summary(data) {
  return { [__ENV.SUMMARY_PATH || 'summary.json']:JSON.stringify(data,null,2),
    stdout: JSON.stringify({note:'See separate summary JSON; raw output contains metrics only',metrics:data.metrics},null,2)+'\n'};
}
