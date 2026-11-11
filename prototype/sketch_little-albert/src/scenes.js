// =====================================================================
//  SCENES — Little Albert (Watson & Rayner, 1920), sketchbook. Times come from the narration: when('word', n).
//  Shared helpers (person, say, speech, iconPeople, stamp, ...) live in ../sketch_kit/people.js.
//  Cast: YOU = baby Albert (terracotta romper) · JOHN WATSON (lab coat) · the white rat, rabbit, dog, mask, cotton wool.
// =====================================================================

const GY = 1235;
const HITS = [when('hammer'), when('bang'), when('scream'), when('week')];

// a sitting baby; r = head radius; mood: happy | calm | wow | cry | scream
function baby(x, gy, r, o = {}) {
  const key = o.key ?? 'bb', mood = o.mood ?? 'happy', lw = Math.max(3, r * 0.08);
  ctx.save(); ctx.translate(x + (o.shake ? o.shake * Math.sin(B * 2.7) : 0), gy - (o.lift ?? 0));
  for (const s of [-1, 1]) {   // legs forward + feet
    const L = loopPts(s * r * 0.6, -r * 0.3, r * 0.55, r * 0.3, 0.05);
    gfill(L, SK.terra, { key: key + 'lgf' + s, off: [2, 2] }); gline(L, { closed: true, key: key + 'lg' + s, w: lw });
    const F = loopPts(s * r * 1.12, -r * 0.32, r * 0.2, r * 0.24, 0.05);
    gfill(F, SKIN, { key: key + 'ftf' + s, off: [0, 0] }); gline(F, { closed: true, key: key + 'ft' + s, w: lw * 0.8, second: false });
  }
  const Bd = loopPts(0, -r * 1.05, r * 0.85, r * 0.9, 0.05);
  gfill(Bd, SK.terra, { key: key + 'bdf', off: [3, 3] }); gline(Bd, { closed: true, key: key + 'bd', w: lw });
  for (const [i, s] of [[0, -1], [1, 1]]) {   // arms (0 = out, + up, - down)
    const ang = o.arms?.[i] ?? -0.9, sh = [s * r * 0.6, -r * 1.5], L = r * 1.0;
    const hd = [sh[0] + s * L * Math.cos(ang), sh[1] - L * Math.sin(ang)];
    gline([sh, [(sh[0] + hd[0]) / 2, (sh[1] + hd[1]) / 2 + r * 0.06], hd], { key: key + 'ar' + s, w: lw * 1.2, second: false });
    const H = loopPts(hd[0], hd[1], r * 0.17, r * 0.17, 0.05);
    gfill(H, SKIN, { key: key + 'hf' + s, off: [0, 0] }); gline(H, { closed: true, key: key + 'h' + s, w: lw * 0.8, second: false });
  }
  const hy = -r * 2.6, Fc = loopPts(0, hy, r, r * 0.96, 0, 0, 40);
  gfill(Fc, SKIN, { key: key + 'ff', off: [r * 0.04, r * 0.04] }); gline(loopPts(0, hy, r, r * 0.96, 0.06), { key: key + 'fo', w: lw });
  gline([[-r * 0.1, hy - r * 0.95], [0, hy - r * 1.2], [r * 0.18, hy - r * 1.08], [r * 0.1, hy - r * 0.95]], { key: key + 'curl', w: lw * 0.9, second: false });
  for (const s of [-1, 1]) {   // ears
    gline(arcPts(s * r * 0.98, hy + r * 0.1, r * 0.16, s > 0 ? -1.4 : 1.7, s > 0 ? 1.4 : 4.6, 8), { key: key + 'ear' + s, w: lw * 0.8, second: false });
  }
  const [lx, ly] = o.look ?? [0, 0];
  for (const s of [-1, 1]) {
    const ex = s * r * 0.36 + lx * r * 0.08, ey = hy + r * 0.12 + ly * r * 0.07;
    if (mood === 'happy') gline([[ex - r * 0.1, ey + r * 0.03], [ex, ey - r * 0.07], [ex + r * 0.1, ey + r * 0.03]], { key: key + 'e' + s, w: lw * 0.9, second: false, step: 6 });
    else if (mood === 'cry' || mood === 'scream') gline([[ex - r * 0.12, ey - r * 0.05], [ex + r * 0.12, ey + r * 0.02 * s]], { key: key + 'e' + s, w: lw * 0.9, second: false, step: 6 });
    else { ctx.fillStyle = SK.ink; ctx.beginPath(); ctx.ellipse(ex, ey, r * 0.09, r * (mood === 'wow' ? 0.15 : 0.11), 0, 0, TAU); ctx.fill(); }
    if (mood === 'cry' || mood === 'scream') {   // tears
      const k = (TT * 1.5 + (s > 0 ? 0.5 : 0)) % 1;
      gline([[ex, ey + r * 0.1], [ex + s * r * 0.05, ey + r * (0.25 + k * 0.4)]], { key: key + 'tr' + s, w: lw * 0.8, col: '#7fb4d6', second: false });
    }
  }
  const my = hy + r * 0.55; ctx.fillStyle = SK.ink;
  if (mood === 'happy') { ctx.beginPath(); ctx.moveTo(-r * 0.25, my - r * 0.06); ctx.quadraticCurveTo(0, my + r * 0.3, r * 0.25, my - r * 0.06); ctx.closePath(); ctx.fill(); }
  else if (mood === 'cry') { ctx.beginPath(); ctx.ellipse(0, my + r * 0.04, r * 0.18, r * 0.14, 0, 0, TAU); ctx.fill(); }
  else if (mood === 'scream') { ctx.beginPath(); ctx.ellipse(0, my + r * 0.06, r * 0.22, r * 0.26, 0, 0, TAU); ctx.fill(); }
  else if (mood === 'wow') { ctx.beginPath(); ctx.ellipse(0, my, r * 0.09, r * 0.12, 0, 0, TAU); ctx.fill(); }
  else gline(arcPts(0, my - r * 0.12, r * 0.16, Math.PI * 0.2, Math.PI * 0.8, 8), { key: key + 'm', w: lw * 0.8, second: false });
  ctx.restore();
}
// the white rat, sitting on the ground at (x, gy), facing left (dir -1) or right (dir 1)
function rat(x, gy, s, key, part = 1, dir = -1) {
  if (part <= 0) return;
  ctx.save(); ctx.translate(x, gy); ctx.scale(dir * -1, 1);
  const Bd = loopPts(0, -s * 0.38, s * 0.62, s * 0.38, 0.05);
  gline(arcPts(s * 0.9, -s * 0.05, s * 0.32, -Math.PI * 0.95, Math.PI * 0.3, 12), { key: key + 'tl', w: 4, col: '#d98a8a', second: false, part });
  gfill(Bd, '#fffdf6', { key: key + 'bf', off: [3, 3], a: clamp(part) });
  gline(Bd, { closed: true, key: key + 'b', w: 4, part });
  const Hd = [[-s * 0.5, -s * 0.62], [-s * 1.0, -s * 0.38], [-s * 0.5, -s * 0.2]];
  gfill(Hd, '#fffdf6', { key: key + 'hf', off: [0, 0], a: clamp(part) });
  gline(Hd, { key: key + 'h', w: 4, second: false, part });
  const E = loopPts(-s * 0.48, -s * 0.72, s * 0.14, s * 0.14, 0.05);
  gfill(E, '#f2b5b5', { key: key + 'ef', off: [0, 0], a: clamp(part) }); gline(E, { closed: true, key: key + 'e', w: 3, second: false, part });
  if (part >= 1) { ctx.fillStyle = SK.ink; ctx.beginPath(); ctx.arc(-s * 0.7, -s * 0.44, s * 0.05, 0, TAU); ctx.fill(); ctx.fillStyle = '#e0889a'; ctx.beginPath(); ctx.arc(-s * 1.0, -s * 0.38, s * 0.05, 0, TAU); ctx.fill(); }
  for (let i = 0; i < 2; i++) gline([[-s * 0.95, -s * 0.36], [-s * 1.25, -s * (0.44 - i * 0.14)]], { key: key + 'wh' + i, w: 2, col: SK.graph, second: false, part });
  ctx.restore();
}
// small doodles: rabbit, dog, mask, cotton wool, fur coat, santa mask — centred at (x, y)
function rabbitD(x, y, k, key) {
  const Bd = loopPts(x, y + 30, 55, 42, 0.05), Hd = loopPts(x - 45, y - 10, 30, 28, 0.05);
  for (const P of [Bd, Hd]) gfill(P, '#fffdf6', { key: key + 'f' + P.length, off: [3, 3], a: clamp(k) });
  gline(Bd, { closed: true, key: key + 'b', w: 4, part: k }); gline(Hd, { closed: true, key: key + 'h', w: 4, part: k });
  for (const s of [0, 1]) gline(loopPts(x - 55 + s * 22, y - 70, 10, 32, 0.05), { closed: true, key: key + 'e' + s, w: 4, second: false, part: k });
  gline(loopPts(x + 58, y + 25, 12, 12, 0.05), { key: key + 't', w: 3, second: false, part: k });
}
function dogD(x, y, k, key) {
  const Bd = sketchBox(x - 50, y + 5, 100, 50, 20), Hd = loopPts(x - 55, y - 10, 30, 27, 0.05);
  gfill(Bd, '#c9a27c', { key: key + 'bf', off: [3, 3], a: clamp(k) }); gfill(Hd, '#c9a27c', { key: key + 'hf', off: [3, 3], a: clamp(k) });
  gline(Bd, { closed: true, key: key + 'b', w: 4, part: k }); gline(Hd, { closed: true, key: key + 'h', w: 4, part: k });
  gline(loopPts(x - 72, y - 5, 10, 22, 0.05), { closed: true, key: key + 'ear', w: 4, second: false, part: k });
  for (const lx of [-35, -10, 20, 40]) gline([[x + lx, y + 55], [x + lx, y + 80]], { key: key + 'lg' + lx, w: 4, second: false, part: k });
  gline([[x + 50, y + 10], [x + 75, y - 20]], { key: key + 'tl', w: 4, second: false, part: k });
}
function maskD(x, y, k, key, santa = false) {
  const F = loopPts(x, y + 5, 52, 62, 0.05);
  gfill(F, santa ? SKIN : '#fffdf6', { key: key + 'f', off: [3, 3], a: clamp(k) }); gline(F, { closed: true, key: key + 'o', w: 4, part: k });
  for (const s of [-1, 1]) gline(loopPts(x + s * 20, y - 5, 10, 7, 0.05), { closed: true, key: key + 'e' + s, w: 4, second: false, part: k });
  if (santa) {
    const Hat = [[x - 58, y - 35], [x + 10, y - 115], [x + 58, y - 35]];
    gfill(Hat, '#d98a8a', { key: key + 'hat', off: [2, 2], a: clamp(k) }); gline(Hat, { key: key + 'ho', w: 4, second: false, part: k });
    const Bd = [[x - 52, y + 15], [x - 40, y + 85], [x, y + 105], [x + 40, y + 85], [x + 52, y + 15], [x, y + 35]];
    gfill(Bd, '#fffdf6', { key: key + 'bd', off: [2, 2], a: clamp(k) }); gline(Bd, { closed: true, key: key + 'bo', w: 4, second: false, part: k });
  } else gline(arcPts(x, y + 22, 18, 0.3, Math.PI - 0.3, 8), { key: key + 'm', w: 4, second: false, part: k });
}
function cottonD(x, y, k, key) {
  [[-30, 10], [0, -10], [30, 10], [0, 25], [-15, 0], [18, -2]].forEach(([dx, dy], i) => {
    const C = loopPts(x + dx, y + dy, 30, 26, 0.05);
    gfill(C, '#fffdf6', { key: key + 'f' + i, off: [2, 2], a: clamp(k) }); gline(C, { closed: true, key: key + 'c' + i, w: 3, second: false, part: k });
  });
}
function coatD(x, y, k, key) {
  const C = [[x - 30, y - 60], [x + 30, y - 60], [x + 62, y - 30], [x + 50, y + 75], [x - 50, y + 75], [x - 62, y - 30]];
  gfill(C, '#9a7454', { key: key + 'f', off: [3, 3], a: clamp(k) });
  ctx.save(); gclip(C); ghatch(x - 70, y - 70, x + 70, y + 80, { ang: -0.6, gap: 9, col: SK.ink, w: 1.5, a: 0.35 * clamp(k), key: key + 'h' }); ctx.restore();
  gline(C, { closed: true, key: key + 'o', w: 4, part: k });
  gline([[x, y - 60], [x, y + 75]], { key: key + 'mid', w: 3, second: false, part: k });
}
// a row of items, each drawn on its word; items = [[drawFn, label, t]]
function itemRow(items, y, keyp) {
  items.forEach(([fn, label, t], i) => {
    const x = 180 + i * 240;
    if (TT < t - 0.1) return;
    fn(x, y, ev(t - 0.1, 0.4), keyp + i);
    handLetter(label, x, y + 150, 40, { col: SK.ink, key: keyp + 'l' + i, reveal: ev(t, 0.3) });
  });
}

const SCENES = [
// ---- 1. the white rat --------------------------------------------------------------------
() => {
  sketchPage({ grid: 'dots' }); ground('g1', GY);
  const reach = TT >= when('reach');
  baby(330, GY, 72, { key: 'albert', mood: TT >= when('rat') ? 'happy' : 'calm', look: TT >= when('rat') ? [1, 0.3] : [0, 0], arms: reach ? [-0.9, 0.3] : [-0.9, -0.9] });
  rat(720, GY, 120, 'rat1', ev(when('rat') - 0.2, 0.5), -1);
  handLetter('white rat', 720, 1000, 54, { face: 'marker', col: SK.ink, key: 'wr', reveal: ev(when('white'), 0.4) });
  if (TT >= when('love')) {   // a doodled heart
    const hp = []; for (let i = 0; i <= 30; i++) { const a = i / 30 * TAU; hp.push([330 + 40 * 16 * Math.pow(Math.sin(a), 3) / 16, 560 - 40 * (13 * Math.cos(a) - 5 * Math.cos(2 * a) - 2 * Math.cos(3 * a) - Math.cos(4 * a)) / 16]); }
    gfill(hp, '#e88a7a', { key: 'hrtf', off: [3, 3], a: clamp(ev(when('love') + 0.2, 0.3)) });
    gline(hp, { key: 'hrt', w: 5, part: ev(when('love'), 0.4) });
  }
  pageTag('nine months old');
  say([[S[0], ["you're nine", 'months old.'], [[1, 'months old.']]], [when('soft'), ['a soft white rat.'], [[0, 'white rat.']]],
       [when('love'), ['you love it.'], [[0, 'love']]], [when('reach'), ['you reach out', 'to touch it.'], [[1, 'touch it.']]]], S[0]);
},
// ---- 2. afraid of nothing ------------------------------------------------------------------
() => {
  sketchPage({ grid: 'ruled' }); ground('g2', GY);
  itemRow([[rabbitD, 'rabbit', when('rabbit')], [dogD, 'dog', when('dog')], [(x, y, k, kk) => maskD(x, y, k, kk), 'mask', when('mask')], [cottonD, 'cotton wool', when('cotton')]], 560, 'it2');
  if (TT >= when('afraid')) for (let i = 0; i < 4; i++) checkMark(180 + i * 240, 800, 0.8, ev(when('afraid') + i * 0.12, 0.25), SK.green, 'ck2' + i);
  baby(300, GY, 60, { key: 'albert', mood: TT >= when('rabbit') ? 'happy' : 'calm', look: [1, -0.6], arms: [-0.9, -0.9] });
  if (TT >= when('psychologist') - 0.2) person(760, onGround(GY, 64), 64, { key: 'watson', outfit: 'coat', hair: 'short', hairCol: '#4a3a30', mood: 'calm', look: [-1, 0], arms: [-1.2, 0.2], tag: 'WATSON', tagReveal: ev(when('watson'), 0.4) });
  pageTag('1920, johns hopkins');
  say([[S[1], ['1920,', 'johns hopkins.'], [[1, 'johns hopkins.']]], [when('psychologist'), ['john watson', 'shows you things.'], [[0, 'john watson']]],
       [when('afraid') - 0.6, ["you're not afraid", 'of anything.'], [[0, 'not afraid']]]], S[1]);
},
// ---- 3. the hammer and the steel bar ---------------------------------------------------------
() => {
  sketchPage({ grid: 'dots' }); ground('g3', GY);
  // the steel bar, hung from a frame behind the baby
  const t0 = when('steel') - 0.3;
  gline([[110, 760], [480, 760]], { key: 'beam', w: 6, part: ev(t0, 0.3) });
  gline([[480, 760], [480, GY]], { key: 'post', w: 6, part: ev(t0 + 0.1, 0.3) });
  for (const x of [170, 420]) gline([[x, 760], [x, 860]], { key: 'str' + x, w: 2.5, col: SK.graph, second: false, part: ev(t0 + 0.3, 0.2) });
  const BAR = sketchBox(150, 860, 290, 26, 8);
  gfill(BAR, '#9aa3ad', { key: 'barf', off: [2, 2], a: clamp(ev(t0 + 0.4, 0.3)) });
  gline(BAR, { closed: true, key: 'bar', w: 5, part: ev(t0 + 0.4, 0.3) });
  handLetter('STEEL BAR', 295, 720, 44, { face: 'marker', col: SK.ink, key: 'sb', reveal: ev(when('steel'), 0.3) });
  // "a man hits ... with a hammer"
  const hit = TT >= when('hammer') && (TT - when('hammer')) % 1.2 < 0.25;
  if (TT >= when('man')) {
    person(250, onGround(GY, 50), 50, { key: 'watson', outfit: 'coat', hair: 'short', hairCol: '#4a3a30', mood: 'calm', look: [0, -1], arms: [-1.2, hit ? 0.5 : 1.3] });
    if (TT >= when('hammer')) {
      const hx = 250 + 50 * 0.62 + 50 * 1.45 * Math.cos(hit ? 0.5 : 1.3), hyy = onGround(GY, 50) + 65 - 72 * Math.sin(hit ? 0.5 : 1.3);
      gline([[hx, hyy], [hx + 30, hyy - 70]], { key: 'hmh' + hit, w: 7, col: '#8b6a45', second: false });
      gfill(sketchBox(hx + 5, hyy - 100, 60, 36, 6), '#6f6a63', { key: 'hmf' + hit, off: [0, 0] });
      gline(sketchBox(hx + 5, hyy - 100, 60, 36, 6), { closed: true, key: 'hmo' + hit, w: 4 });
    }
    if (hit) for (let i = 0; i < 5; i++) { const a = -2.6 + i * 0.5; gline([[295 + Math.cos(a) * 170, 873 + Math.sin(a) * 60], [295 + Math.cos(a) * 230, 873 + Math.sin(a) * 85]], { key: 'bl' + i, w: 4, second: false }); }
  }
  baby(650, GY, 58, { key: 'albert', mood: hit ? 'wow' : 'happy', look: [1, 0.3], arms: TT >= when('touch', 2) ? [-0.9, 0.2] : [-0.9, -0.9] });
  rat(870, GY, 80, 'rat3', ev(when('rat', 2) - 0.2, 0.4), -1);
  if (TT >= when('behind')) arrowPencil([[560, 1000], [470, 960], [430, 900]], ev(when('behind'), 0.4), { key: 'arw3', col: SK.red, w: 4 });
  pageTag('the noise');
  say([[S[2], ['every time you', 'touch the rat,'], [[1, 'touch the rat,']]], [when('man'), ['a man hits a', 'steel bar'], [[1, 'steel bar']]],
       [when('right'), ['right behind', 'your head.'], [[1, 'your head.']]]], S[2]);
},
// ---- 4. bang, you cry ----------------------------------------------------------------------
() => {
  sketchPage({ grid: 'dots' }); ground('g4', GY);
  if (TT >= when('bang')) {
    handLetter('BANG!', 540, 600, 130, { face: 'marker', col: SK.red, key: 'bang', reveal: ev(when('bang'), 0.15) });
    for (let i = 0; i < 8; i++) { const a = i * TAU / 8; gline([[540 + Math.cos(a) * 250, 560 + Math.sin(a) * 120], [540 + Math.cos(a) * 310, 560 + Math.sin(a) * 150]], { key: 'bst' + i, w: 5, second: false, part: ev(when('bang'), 0.2) }); }
  }
  const jump = TT >= when('jump') && TT < when('jump') + 0.4 ? 40 : 0;
  const fall = TT >= when('fall');
  const mood = TT >= when('cry') ? 'cry' : TT >= when('jump') ? 'wow' : 'calm';
  ctx.save(); if (fall && TT < when('start')) { ctx.translate(540, GY); ctx.rotate(0.25); ctx.translate(-540, -GY); }
  baby(540, GY, 78, { key: 'albert', mood, look: [0, 0], arms: TT >= when('jump') ? [0.6, 0.6] : [-0.9, -0.9], lift: jump, shake: mood === 'cry' ? 3 : 0 });
  ctx.restore();
  // tally of the bangs
  const n = (TT >= when('bang') ? 1 : 0) + (TT >= when('do') ? 1 : 0) + (TT >= when('again') ? 1 : 0) + (TT >= when('again', 2) ? 1 : 0);
  for (let i = 0; i < n; i++) gline([[760 + i * 30, 790], [765 + i * 30, 880]], { key: 'tal' + i, w: 6, second: false, part: ev([when('bang'), when('do'), when('again'), when('again', 2)][i], 0.15) });
  pageTag('bang');
  say([[S[3], ['bang.'], [[0, 'bang.']]], [when('jump'), ['you jump.', 'you fall forward.'], [[0, 'jump.']]], [when('start'), ['you start to cry.'], [[0, 'cry.']]],
       [when('do'), ['again,', 'and again.'], [[1, 'again.']]]], S[3]);
},
// ---- 5. seven bangs: the rat alone ---------------------------------------------------------------
() => {
  sketchPage({ grid: 'dots' }); ground('g5', GY);
  for (let i = 0; i < 7; i++) gline([[150 + i * 34 + (i === 4 ? 0 : 0), 430], [155 + i * 34, 520]], { key: 'tl7' + i, w: 6, second: false, part: ev(S[4] + 0.2 + i * 0.1, 0.12) });
  gline([[140, 500], [300, 440]], { key: 'tl7x', w: 5, second: false, part: ev(S[4] + 0.9, 0.15) });
  handLetter('7 bangs', 220, 600, 50, { face: 'marker', col: SK.ink, key: 'b7', reveal: ev(when('bangs'), 0.3) });
  // "no noise at all": the hammer, crossed out
  if (TT >= when('noise') - 0.3) {
    const k = ev(when('noise') - 0.3, 0.3);
    gline([[690, 560], [730, 460]], { key: 'nh', w: 7, col: '#8b6a45', second: false, part: k });
    gline(sketchBox(700, 430, 70, 40, 6), { closed: true, key: 'nhh', w: 4, part: k });
    gline(loopPts(730, 500, 100, 100, 0.1), { key: 'nc', w: 6, col: SK.red, part: ev(when('noise'), 0.3) });
    gline([[660, 430], [800, 570]], { key: 'ns', w: 6, col: SK.red, second: false, part: ev(when('noise') + 0.2, 0.2) });
    handLetter('no noise', 730, 660, 46, { col: SK.ink, key: 'nn', reveal: ev(when('noise'), 0.3) });
  }
  rat(780, GY, 110, 'rat5', ev(when('rat', 3) - 0.2, 0.4), -1);
  const crawl = EZ.io(ev(when('crawl'), 1.2)), scream = TT >= when('scream');
  baby(lerp(420, 200, crawl), GY, 64, { key: 'albert', mood: scream ? 'scream' : TT >= when('rat', 3) ? 'wow' : 'calm', look: [1, 0], arms: scream ? [0.4, 0.8] : [-0.9, -0.9], shake: scream ? 4 : 0 });
  if (crawl > 0) for (let i = 0; i < 3; i++) gpencil([[lerp(420, 200, crawl) + 110 + i * 30, 1120 + i * 25], [lerp(420, 200, crawl) + 160 + i * 30, 1120 + i * 25]], { key: 'mv' + i, w: 3, a: 0.7 });
  pageTag('the rat alone');
  say([[S[4], ['after just seven bangs:', 'the rat alone.'], [[1, 'the rat alone.']]], [when('no'), ['no noise at all.'], [[0, 'no noise']]],
       [when('scream'), ['you scream', 'and crawl away.'], [[0, 'scream']]]], S[4]);
},
// ---- 6. the fear spreads ---------------------------------------------------------------------
() => {
  sketchPage({ grid: 'dots' }); ground('g6', GY);
  handLetter('the fear spreads', 540, 470, 60, { face: 'marker', col: SK.red, key: 'fs', reveal: ev(when('spread') - 0.3, 0.4) });
  itemRow([[rabbitD, 'rabbit', when('rabbit', 2)], [dogD, 'dog', when('dog', 2)], [coatD, 'fur coat', when('fur')], [(x, y, k, kk) => maskD(x, y, k, kk, true), 'santa mask', when('santa')]], 640, 'it6');
  for (let i = 0; i < 4; i++) { const t = [when('rabbit', 2), when('dog', 2), when('fur'), when('santa')][i]; if (TT >= t + 0.2) handLetter('!', 250 + i * 240, 560, 60, { face: 'marker', col: SK.ink, key: 'ex6' + i, reveal: ev(t + 0.2, 0.1) }); }
  baby(540, GY, 58, { key: 'albert', mood: TT >= when('cry', 2) ? 'cry' : 'wow', look: [0, -0.6], arms: [0.5, 0.5], shake: TT >= when('cry', 2) ? 3 : 0 });
  pageTag('days later');
  say([[S[5], ['days later,', 'the fear spreads.'], [[1, 'spreads.']]], [when('rabbit', 2), ['a rabbit, a dog,', 'a fur coat...'], [[1, 'fur coat...']]],
       [when('even'), ['even a santa mask', 'makes you cry.'], [[1, 'cry.']]]], S[5]);
},
// ---- 7. never undone --------------------------------------------------------------------------
() => {
  sketchPage({ grid: 'ruled' }); ground('g7', GY);
  // the case file
  const F = sketchBox(160, 430, 760, 380, 10, 0.03);
  gfill(F, '#efe2b4', { key: 'ff', off: [5, 5], a: clamp(ev(S[6], 0.3)) });
  gline(F, { closed: true, key: 'fo', w: 5, part: ev(S[6], 0.4) });
  handLetter('CASE: ALBERT B.', 540, 510, 54, { face: 'marker', col: SK.ink, key: 'cf1', reveal: ev(S[6] + 0.2, 0.4) });
  handLetter('fear: learned', 540, 620, 50, { col: SK.ink, key: 'cf2', reveal: ev(S[6] + 0.6, 0.4) });
  handLetter('undone: NEVER', 540, 730, 54, { face: 'marker', col: SK.red, key: 'cf3', reveal: ev(when('undo'), 0.4) });
  // "you leave the study": a door, open, an empty mat
  const D = sketchBox(130, 880, 190, 350, 6, 0.02);
  gfill(D, '#3b3530', { key: 'dop', off: [0, 0], a: 0.6 * clamp(ev(when('leave'), 0.3)) });
  gline(D, { closed: true, key: 'door', w: 5, part: ev(when('leave') - 0.2, 0.3) });
  handLetter('EXIT', 225, 860, 36, { face: 'marker', col: SK.graph, key: 'exit', reveal: ev(when('leave'), 0.3) });
  // "who you grew up to be is still debated": a grown man, outlined in graphite, with a question mark
  if (TT >= when('grew')) {
    person(680, onGround(GY, 52), 52, { key: 'grown', shirt: '#d8d2c4', hair: 'short', hairCol: '#9a948b', mood: 'puzzled', look: [0, -0.4], arms: [-1.2, -1.2] });
    handLetter('?', 840, 1000, 110, { face: 'marker', col: SK.ink, key: 'q7', reveal: ev(when('grew') + 0.3, 0.2) });
  }
  pageTag('afterwards');
  say([[S[6], ['then you', 'leave the study.'], [[1, 'leave']]], [when('nobody'), ['nobody tries to', 'undo the fear.'], [[1, 'undo']]],
       [when('who'), ['who you became', 'is still debated.'], [[1, 'debated.']]]], S[6]);
},
// ---- 8. learned in about a week ---------------------------------------------------------------
() => {
  sketchPage({ grid: 'dots' });
  const BB = sketchBox(140, 430, 800, 380, 10, 0.03);
  gfill(BB, '#4f5b52', { key: 'bbf', off: [5, 5], a: clamp(ev(S[7], 0.3)) });
  gline(BB, { closed: true, key: 'bbo', w: 6, part: ev(S[7], 0.4) });
  handLetter('ETHICS', 540, 600, 100, { face: 'marker', col: '#fffdf6', key: 'eth', reveal: ev(when('ethics'), 0.4) });
  handLetter('what not to do', 540, 720, 52, { col: '#e8e2d0', key: 'wnd', reveal: ev(when('ethics') + 0.5, 0.5) });
  // "a fear can be learned in about a week": seven days, crossed off
  if (TT >= when('fear', 3) - 0.2) for (let i = 0; i < 7; i++) {
    const x = 140 + i * 114, C = sketchBox(x, 930, 100, 100, 8);
    gfill(C, '#fffdf6', { key: 'dyf' + i, off: [3, 3], a: clamp(ev(when('fear', 3) - 0.2 + i * 0.05, 0.2)) });
    gline(C, { closed: true, key: 'dy' + i, w: 4, part: ev(when('fear', 3) - 0.2 + i * 0.05, 0.2) });
    if (TT >= when('learned') + i * 0.12) gline([[x + 15, 945], [x + 85, 1015]], { key: 'dx' + i, w: 6, col: SK.red, second: false, part: ev(when('learned') + i * 0.12, 0.1) });
  }
  if (TT >= when('week')) handLetter('about one week', 540, 1180, 66, { face: 'marker', col: SK.ink, key: 'wk', reveal: ev(when('week'), 0.4) });
  pageTag('the lesson');
  say([[S[7], ["today it's taught", 'as a lesson in ethics.'], [[1, 'ethics.']]], [when('but'), ['but it showed', 'something unsettling.'], [[1, 'unsettling.']]],
       [when('fear', 3), ['a fear can be learned', 'in about a week.'], [[1, 'a week.']]]], S[7]);
},
// ---- 9. which of your fears were learned? -----------------------------------------------------------
() => {
  sketchPage({ grid: 'dots' }); ground('g9', GY);
  person(250, onGround(GY, 72), 72, { key: 'hero', mood: TT >= when('unlearn') ? 'calm' : 'puzzled', look: [0.6, -0.8], arms: [-1.2, -1.2] });
  speech(110, 400, 820, 330, [], [270, 880], ev(S[8], 0.3), 'th9');
  if (TT >= S[8] + 0.2) { rat(270, 640, 90, 'rat9', ev(S[8] + 0.2, 0.4), -1); dogD(530, 580, ev(S[8] + 0.5, 0.4), 'dg9'); maskD(780, 560, ev(S[8] + 0.8, 0.4), 'mk9', true); }
  stamp('LEARNED', 650, 1000, when('learned', 2), -0.1, 'slearn');
  if (TT >= when('unlearn')) { const k = ev(when('unlearn'), 1.2); eraserTool(lerp(260, 820, k), 600 + 30 * Math.sin(k * 20), -0.3, 0.8); }
  pageTag('your turn');
  say([[S[8], ['some of your fears', 'were never yours.'], [[1, 'never yours.']]], [when('learned', 2) - 0.5, ['they were learned.'], [[0, 'learned.']]],
       [when('so'), ['which of yours could', 'YOU unlearn?'], [[1, 'YOU unlearn?']]]], S[8]);
},
];
