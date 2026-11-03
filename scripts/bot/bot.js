window.runBot = function (levelIdx, maxSec) {
  const G = window.__game, SEA = 0, LAND = 1;
  const D = { up: [0, -1], down: [0, 1], left: [-1, 0], right: [1, 0] };
  const dirOf = (dx, dy) => (dx > 0 ? 'right' : dx < 0 ? 'left' : dy > 0 ? 'down' : 'up');
  window.__halt = true; window.__botHold = false;
  G.startLevel(levelIdx); G.skipIntro();
  let plan = null, t = 0, idle = 0, lastLives = null, deaths = 0, plans = 0;
  window.__botNext = (x, y) => {
    if (!plan) return 'stop';
    const k = plan.findIndex((c) => c[0] === x && c[1] === y);
    if (k < 0 || k === plan.length - 1) { plan = null; window.__botHold = false; return 'stop'; }
    return dirOf(plan[k + 1][0] - x, plan[k + 1][1] - y);
  };
  function choose(s) {
    const W = s.W, H = s.Hh, cell = (x, y) => (x < 0 || y < 0 || x >= W || y >= H ? -1 : s.cells[y * W + x]);
    // land distances from the player
    const dist = new Int32Array(W * H).fill(-1), prev = new Int32Array(W * H).fill(-1), q = [s.py * W + s.px]; dist[q[0]] = 0;
    for (let h = 0; h < q.length; h++) { const i = q[h], x = i % W, y = (i / W) | 0; for (const [dx, dy] of Object.values(D)) { const nx = x + dx, ny = y + dy; if (cell(nx, ny) !== LAND) continue; const j = ny * W + nx; if (dist[j] < 0) { dist[j] = dist[i] + 1; prev[j] = i; q.push(j); } } }
    const seaMons = s.monsters.filter((m) => !m.land);
    const coast = []; for (let i = 0; i < W * H; i++) if (dist[i] >= 0) { const x = i % W, y = (i / W) | 0; for (const [d, [dx, dy]] of Object.entries(D)) if (cell(x + dx, y + dy) === SEA) coast.push([x, y, d]); }
    if (!coast.length) return null;
    let best = null, bestScore = -1;
    const tries = 700;
    for (let n = 0; n < tries; n++) {
      const [ax, ay, d1] = coast[(Math.random() * coast.length) | 0], [dx, dy] = D[d1];
      const path = [[ax, ay]], seen = new Set([ay * W + ax]); let x = ax, y = ay, ok = true;
      const add = (nx, ny) => { const k = ny * W + nx; if (seen.has(k)) return false; seen.add(k); path.push([nx, ny]); return true; };
      const kind = Math.random();
      if (kind < 0.3) { // straight across
        for (let k = 0; k < 30; k++) { x += dx; y += dy; const c = cell(x, y); if (c === -1) { ok = false; break; } if (!add(x, y)) { ok = false; break; } if (c === LAND) break; if (c !== SEA) { ok = false; break; } }
        if (!ok || cell(x, y) !== LAND) continue;
      } else { // a U: out a, along b, back
        const a = 1 + ((Math.random() * 7) | 0), b = 1 + ((Math.random() * 12) | 0), side = Math.random() < 0.5 ? 1 : -1, ex = -dy * side, ey = dx * side;
        for (let k = 0; k < a && ok; k++) { x += dx; y += dy; if (cell(x, y) !== SEA || !add(x, y)) ok = false; }
        for (let k = 0; k < b && ok; k++) { x += ex; y += ey; const c = cell(x, y); if (c === LAND) { add(x, y); break; } if (c !== SEA || !add(x, y)) ok = false; }
        if (!ok) continue;
        if (cell(x, y) !== LAND) { for (let k = 0; k < a + 4; k++) { x -= dx; y -= dy; const c = cell(x, y); if (c === -1 || !add(x, y)) { ok = false; break; } if (c === LAND) break; if (c !== SEA) { ok = false; break; } } }
        if (!ok || cell(x, y) !== LAND) continue;
      }
      const sea = path.slice(1, -1); if (!sea.length) continue;
      // claim simulation
      const grid = s.cells.slice(); for (const [px2, py2] of sea) grid[py2 * W + px2] = LAND;
      const reach = new Uint8Array(W * H), st = [];
      for (const m of seaMons) { const i = Math.floor(m.y) * W + Math.floor(m.x); if (grid[i] === SEA && !reach[i]) { reach[i] = 1; st.push(i); } }
      while (st.length) { const i = st.pop(), x2 = i % W, y2 = (i / W) | 0; for (const [ddx, ddy] of Object.values(D)) { const nx = x2 + ddx, ny = y2 + ddy; if (nx < 0 || ny < 0 || nx >= W || ny >= H) continue; const j = ny * W + nx; if (!reach[j] && grid[j] === SEA) { reach[j] = 1; st.push(j); } } }
      let gain = sea.length; for (let i = 0; i < W * H; i++) if (grid[i] === SEA && !reach[i]) gain++;
      if (s.boss) { const bm = seaMons.find((m) => m.boss); if (bm) { const i = Math.floor(bm.y) * W + Math.floor(bm.x); let sz = 0; if (grid[i] === SEA) { const r2 = new Uint8Array(W * H), st2 = [i]; r2[i] = 1; while (st2.length && sz < 90) { const k = st2.pop(); sz++; const x3 = k % W, y3 = (k / W) | 0; for (const [ddx, ddy] of Object.values(D)) { const nx = x3 + ddx, ny = y3 + ddy; if (nx < 0 || ny < 0 || nx >= W || ny >= H) continue; const j = ny * W + nx; if (!r2[j] && grid[j] === SEA) { r2[j] = 1; st2.push(j); } } } if (sz < 80) gain += 400; } } }
      // risk: can a monster reach the line while we draw it?
      const walk = dist[ay * W + ax], tSea = sea.length / 9;
      let safe = true;
      for (const m of seaMons) { if (m.under) continue; let md = 99; for (const [px2, py2] of sea) md = Math.min(md, Math.hypot(px2 + 0.5 - m.x, py2 + 0.5 - m.y)); if (md < 2.2 + m.sp * (tSea + walk / 9) * 1.0) { safe = false; break; } }
      if (!safe) continue;
      const score = gain / (sea.length + walk * 0.25 + 2);
      if (score > bestScore) { bestScore = score; best = { path, walkTo: ay * W + ax }; }
    }
    if (!best) return null;
    const walkPath = []; for (let i = best.walkTo; i >= 0; i = prev[i]) walkPath.unshift([i % W, (i / W) | 0]);
    return walkPath.concat(best.path.slice(1));
  }
  const step = 1 / 15;
  while (t < maxSec) {
    const s = G.snap();
    if (s.state === 'clear') return { win: true, t, deaths, plans, why: (window.__why || []).splice(0) };
    if (s.state === 'over') return { win: false, t, deaths, plans, pct: s.pct, why: window.__why.splice(0) };
    if (lastLives !== null && s.lives < lastLives) { deaths++; (window.__why = window.__why || []).push(window.__lastWhy); plan = null; window.__botHold = false; }
    lastLives = s.lives;
    if (s.state === 'play' && !s.entering && !s.dir && !plan) {
      const p = choose(s);
      if (p && p.length > 1) { plan = p; plans++; window.__botHold = true; G.steer(dirOf(p[1][0] - p[0][0], p[1][1] - p[0][1])); }
    }
    G.sim(step); t += step;
  }
  return { win: false, t, deaths, plans, timeout: true, pct: G.snap().pct };
};
