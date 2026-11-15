// =====================================================================
//  SCENES — Patient H.M. (1953), sketchbook. Every time comes from the narration: when('word', n).
//  Shared helpers (person, say, speech, iconPeople, stamp, ...) live in ../sketch_kit/people.js.
//  Cast: YOU (Henry, terracotta t-shirt) · the surgeon (coat) · the psychologist (green cardigan, glasses) · a visitor (blue).
// =====================================================================

const GY = 1235;
const HITS = [when('forever'), when('gone', 2), when('remembered'), when('perfect')];

// a doodle brain (side view): bumpy outline and a fold line
function brainDoodle(cx, cy, rx, ry, key, part = 1) {
  const P = []; for (let i = 0; i <= 48; i++) { const a = i / 48 * TAU, k = 1 + 0.07 * Math.sin(a * 9); P.push([cx + Math.cos(a) * rx * k, cy + Math.sin(a) * ry * k * (Math.sin(a) > 0 ? 0.8 : 1)]); }
  gfill(P, '#f3c6c0', { key: key + 'f', off: [5, 5], a: clamp(part) });
  gline(P, { closed: true, key: key + 'o', w: 5, part });
  gline([[cx - rx * 0.6, cy - ry * 0.1], [cx - rx * 0.2, cy - ry * 0.3], [cx + rx * 0.2, cy], [cx + rx * 0.6, cy - ry * 0.2]], { key: key + 'fold', w: 4, second: false, part });
}
// a five-point star outline (cx, cy, radius); `wob` adds a shaky traced copy on top
function starOutline(cx, cy, r) {
  const P = []; for (let i = 0; i <= 10; i++) { const a = -Math.PI / 2 + i * Math.PI / 5, rr = i % 2 ? r * 0.45 : r; P.push([cx + Math.cos(a) * rr, cy + Math.sin(a) * rr]); }
  return P;
}
function tracedStar(cx, cy, r, wob, part, key, col = SK.terra) {
  gline(starOutline(cx, cy, r), { key: key + 's', w: 4, col: SK.ink, second: false });
  if (part <= 0) return;
  const S0 = starOutline(cx, cy, r), T = [];
  for (let i = 0; i < S0.length - 1; i++) for (let k = 0; k < 6; k++) {
    const u = k / 6, x = lerp(S0[i][0], S0[i + 1][0], u), y = lerp(S0[i][1], S0[i + 1][1], u), h = (hash(key, i, k) % 1000) / 1000;
    T.push([x + (h - 0.5) * wob, y + ((hash(key, 'y', i, k) % 1000) / 1000 - 0.5) * wob]);
  }
  T.push(S0[S0.length - 1]);
  gline(T, { key: key + 't', w: 4, col, second: false, part, amp: 0.4 });
  return T;
}

const SCENES = [
// ---- 1. you wake up ------------------------------------------------------------------------------
() => {
  sketchPage({ grid: 'dots' }); ground('g1', GY);
  // a hospital bed, you lying in it
  const BF = sketchBox(130, 1010, 540, 70, 8, 0.02);
  for (const lx of [150, 650]) gline([[lx, 1080], [lx, GY]], { key: 'bl' + lx, w: 6, second: false });
  gline([[140, 880], [140, 1080]], { key: 'bhead', w: 7, second: false });
  gfill(BF, '#fffdf6', { key: 'bff', off: [4, 4] }); gline(BF, { closed: true, key: 'bf', w: 5 });
  const awake = TT >= when('wake');
  person(240, 950, 60, { key: 'hero', rot: -Math.PI / 2, mood: TT >= when('stranger') ? 'scared' : 'calm', look: TT >= when('person') ? [0.6, -1] : [0, 0], arms: [-1.2, -1.2] });
  const BL = [[300, 900], [660, 905], [660, 1012], [300, 1012]];
  gfill(BL, '#cfe0ea', { key: 'blk', off: [3, 3] }); gline(BL, { closed: true, key: 'blko', w: 4 });
  gline([[180, 870], [195, 1030]], { key: 'band1', w: 10, col: '#fffdf6', second: false, a: awake ? 1 : 0.9 });
  if (!awake) handLetter('z z', 330, 820, 50, { col: SK.graph, key: 'zz' });
  // "every new person you meet will be a stranger"
  if (TT >= when('person')) {
    person(820, onGround(GY, 54), 54, { key: 'vis', shirt: '#8fa7c2', hair: 'short', hairCol: '#222', mood: 'happy', look: [-1, 0], arms: [-1.2, 0.5] });
    if (TT >= when('stranger')) handLetter('stranger', 800, 860, 50, { face: 'marker', col: SK.red, key: 'str', reveal: ev(when('stranger'), 0.3) });
  }
  if (TT >= when('forever')) {
    gline([[440, 520], [500, 470], [560, 520], [620, 570], [680, 520], [620, 470], [560, 520], [500, 570], [440, 520]], { key: 'inf', w: 7, col: SK.red, second: false, part: ev(when('forever'), 0.5) });
    handLetter('FOREVER', 560, 660, 72, { face: 'marker', col: SK.ink, key: 'fe', reveal: ev(when('forever'), 0.4) });
  }
  pageTag('waking up');
  say([[S[0], ['you wake up after', 'brain surgery.'], [[1, 'brain surgery.']]], [when('every'), ['every new person', 'is a stranger.'], [[1, 'stranger.']]],
       [when('forever'), ['forever.'], [[0, 'forever.']]]], S[0]);
},
// ---- 2. 1953: the choice --------------------------------------------------------------------------
() => {
  sketchPage({ grid: 'ruled' }); ground('g2', GY);
  const sz = TT >= when('seizures');
  person(290, onGround(GY, 64), 64, { key: 'hero', mood: sz ? 'scared' : 'calm', look: [1, 0], arms: [-1.2, -1.2], shake: sz && TT < when('surgeon') ? 3 : 0 });
  handLetter('age 27', 290, 560, 62, { face: 'marker', col: SK.ink, key: 'age', reveal: ev(S[1] + 1.2, 0.4) });
  if (sz) for (let i = 0; i < 3; i++) { const a = -2.4 + i * 0.6, x0 = 290 + Math.cos(a) * 110, y0 = 1000 + Math.sin(a) * 110;
    gline([[x0, y0], [x0 + Math.cos(a) * 25 + 10, y0 + Math.sin(a) * 25 - 8], [x0 + Math.cos(a) * 50, y0 + Math.sin(a) * 50]], { key: 'zg' + i, w: 4, col: SK.red, second: false, part: ev(when('seizures') + i * 0.1, 0.2) }); }
  if (sz) handLetter('seizures', 290, 690, 50, { col: SK.red, key: 'szl', reveal: ev(when('seizures'), 0.3) });
  // the surgeon and his offer
  if (TT >= when('surgeon') - 0.2) {
    person(770, onGround(GY, 62), 62, { key: 'surg', outfit: 'coat', hair: 'short', hairCol: '#555', glasses: true, mood: 'calm', look: [-1, 0], arms: [-1.2, 0.4] });
    speech(470, 420, 460, 200, ['experimental', 'operation?'], [740, 920], ev(when('offers'), 0.5), 'b2', { face: 'marker', size: 52 });
  }
  pageTag('1953');
  say([[S[1], ['1953. you are 27.'], [[0, '27.']]], [when('and'), ['your seizures', 'are severe.'], [[0, 'seizures']]],
       [when('surgeon'), ['a surgeon offers', 'an operation.'], [[1, 'operation.']]]], S[1]);
},
// ---- 3. the surgery ---------------------------------------------------------------------------------
() => {
  sketchPage({ grid: 'dots' });
  brainDoodle(540, 650, 250, 150, 'br3', ev(S[2] + 0.1, 0.5));
  // "both sides, deep inside": two spots, cut out
  if (TT >= when('sides')) for (const [i, x] of [[0, 430], [1, 650]]) {
    const L = loopPts(x, 700, 46, 30, 0.1);
    gfill(L, SK.paper ?? '#f2ead8', { key: 'cut' + i, off: [0, 0], a: clamp(ev(when('deep'), 0.4)) });
    ctx.save(); ctx.setLineDash([10, 8]); gline(L, { key: 'cutl' + i, w: 4, col: SK.red, second: false, part: ev(when('sides') + i * 0.2, 0.3) }); ctx.restore();
  }
  if (TT >= when('sides')) handLetter('both sides', 540, 870, 54, { face: 'marker', col: SK.red, key: 'bs', reveal: ev(when('sides'), 0.3) });
  // the seizure calendar: many crosses before, few after
  if (TT >= when('afterwards') - 0.2) {
    const cp = ev(when('afterwards') - 0.2, 0.4);
    handLetter('seizures', 140, 990, 44, { align: 'left', col: SK.ink, key: 'scl', reveal: cp });
    for (let i = 0; i < 8; i++) {
      const x = 150 + i * 98; gline(sketchBox(x, 1030, 80, 80, 4), { key: 'cal' + i, w: 3, second: false, part: cp });
      const before = i < 3, mark = before || i === 6;
      if (mark) { const t = before ? when('afterwards') : when('rarer'); gline([[x + 14, 1044], [x + 66, 1096]], { key: 'cx' + i, w: 5, col: SK.red, second: false, part: ev(t + i * 0.08, 0.15) }); gline([[x + 66, 1044], [x + 14, 1096]], { key: 'cy' + i, w: 5, col: SK.red, second: false, part: ev(t + i * 0.08 + 0.05, 0.15) }); }
    }
    gline([[440, 1010], [440, 1130]], { key: 'calsep', w: 4, col: SK.graph, second: false, part: cp });
    if (TT >= when('rarer')) handLetter('much rarer', 690, 1200, 50, { face: 'marker', col: SK.green, key: 'mr', reveal: ev(when('rarer'), 0.3) });
  }
  pageTag('the surgery');
  say([[S[2], ['parts of both sides', 'are removed.'], [[0, 'both sides']]], [when('afterwards'), ['the seizures become', 'much rarer.'], [[1, 'much rarer.']]]], S[2]);
},
// ---- 4. no new memories ----------------------------------------------------------------------------
() => {
  sketchPage({ grid: 'dots' }); ground('g4', GY);
  const away = TT >= when('look');
  person(290, onGround(GY, 64), 64, { key: 'hero', mood: TT >= when('gone', 2) ? 'puzzled' : 'happy', look: away ? [-1, 0] : [1, 0], arms: [-1.2, -1.2] });
  if (TT < when('meet', 2)) {
    handLetter('new memories', 540, 560, 70, { face: 'marker', col: SK.ink, key: 'nm', reveal: ev(when('memories') - 0.3, 0.4) });
    if (TT >= when('memories')) { gline([[300, 500], [780, 600]], { key: 'nmx1', w: 8, col: SK.red, second: false, part: ev(when('memories') + 0.2, 0.2) }); gline([[780, 500], [300, 600]], { key: 'nmx2', w: 8, col: SK.red, second: false, part: ev(when('memories') + 0.3, 0.2) }); }
  } else {
    // someone introduces themselves...
    person(780, onGround(GY, 60), 60, { key: 'vis', shirt: '#8fa7c2', hair: 'short', hairCol: '#222', mood: 'happy', look: [-1, 0], arms: [-1.2, 0.6] });
    speech(530, 430, 400, 150, ['"hi, I\'m Sam!"'], [760, 930], ev(when('meet', 2), 0.3), 'b4', { size: 50 });
    // ...and the name in your head is erased the moment you look away
    speech(110, 640, 360, 170, [], [290, 930], 1, 'th4');
    handLetter('Sam', 290, 750, 64, { face: 'marker', col: SK.terra, key: 'sam', reveal: ev(when('meet', 2) + 0.4, 0.3) });
    if (away) graphiteScribble(290, 730, 150, 60, 'er4', { n: Math.round(lerp(4, 40, ev(when('look'), 1.2))) });
    if (TT >= when('gone', 2)) handLetter('?', 400, 700, 64, { face: 'marker', col: SK.ink, key: 'q4', reveal: ev(when('gone', 2), 0.2) });
  }
  pageTag('gone');
  say([[S[3], ['you cannot make', 'new memories.'], [[1, 'new memories.']]], [when('meet', 2), ['meet someone,', 'look away...'], [[1, 'look away...']]],
       [when('and', 2), ['...and they are', 'gone.'], [[1, 'gone.']]]], S[3]);
},
// ---- 5. meeting her for the first time, again ------------------------------------------------------
() => {
  sketchPage({ grid: 'ruled' }); ground('g5', GY);
  // tally marks on the wall: decades of visits
  const tp = ev(when('decades') - 0.2, 1.2), n = Math.floor(lerp(0, 24, tp));
  for (let i = 0; i < n; i++) { const g = Math.floor(i / 5), k = i % 5, x = 140 + g * 160 + k * 22;
    if (k < 4) gpencil([[x, 420], [x + 3, 500]], { key: 'ty' + i, w: 3, a: 0.85 }); else gpencil([[x - 92, 480], [x - 4, 440]], { key: 'ty' + i, w: 3, a: 0.85 }); }
  if (TT >= when('decades')) handLetter('decades of visits', 140, 560, 44, { align: 'left', col: SK.graph, key: 'dv', reveal: ev(when('decades'), 0.4) });
  // a door, she walks in
  gline([[120, GY], [120, 760], [300, 760], [300, GY]], { key: 'door', w: 5 });
  const walk = EZ.io(ev(when('walks') - 0.3, 1.0));
  if (TT >= when('psychologist')) person(lerp(210, 440, walk), onGround(GY, 58), 58, { key: 'psy', shirt: '#7fa77a', hair: 'mop', hairCol: '#2f2620', glasses: true, mood: 'happy', look: [1, 0], arms: [-1.2, -1.2] });
  person(780, onGround(GY, 64), 64, { key: 'hero', mood: 'happy', look: [-1, 0], arms: [-1.2, TT >= when('first') ? 0.3 : -1.2] });
  speech(470, 620, 460, 170, ['"nice to meet you!"'], [760, 930], ev(when('first'), 0.4), 'b5', { size: 48 });
  pageTag('decades');
  say([[S[4], ['a psychologist', 'studies you.'], [[0, 'psychologist']]], [when('every', 2), ['every visit is', 'the first time.'], [[1, 'first time.']]]], S[4]);
},
// ---- 6. the mirror task ---------------------------------------------------------------------------
() => {
  sketchPage({ grid: 'dots' }); ground('g6', GY);
  // the mirror, top-left: a reversed star in a frame
  const mp = ev(when('mirror') - 0.3, 0.4), MR = sketchBox(120, 420, 380, 260, 10, 0.03);
  if (TT >= when('mirror') - 0.3) {
    gfill(MR, '#e3edf2', { key: 'mrf', off: [4, 4], a: clamp(mp) }); gline(MR, { closed: true, key: 'mr', w: 6, part: mp });
    for (let i = 0; i < 3; i++) gline([[160 + i * 40, 460], [130 + i * 40, 520]], { key: 'gl' + i, w: 3, col: '#ffffff', second: false, a: clamp(mp) });
    gline(starOutline(310, 560, 80).map(([x, y]) => [x, 1120 - y]), { key: 'mst', w: 3, col: SK.graph, second: false, part: mp });
    handLetter('MIRROR', 310, 720, 40, { face: 'marker', col: SK.graph, key: 'mrl', reveal: mp });
  }
  // the star card and the shaky trace
  const cp = ev(when('star') - 0.3, 0.4), CD = sketchBox(160, 820, 440, 340, 8, 0.03);
  gfill(CD, '#fffdf6', { key: 'cdf', off: [5, 5], a: clamp(cp) }); gline(CD, { closed: true, key: 'cd', w: 5, part: cp });
  if (TT >= when('star') - 0.2) {
    const tr = ev(when('hand') - 0.2, 2.6), T = tracedStar(380, 1000, 130, 46, tr, 'ts6');
    if (T && tr > 0 && tr < 1) { const tip = writeEnd(T, tr); pencilTool(tip[0], tip[1], -0.75, 1); }
  }
  person(800, onGround(GY, 58), 58, { key: 'hero', mood: TT >= when('hard') ? 'scared' : 'puzzled', look: [-1, -0.8], arms: [0.1, -1.2] });
  if (TT >= when('very')) { handLetter('very hard', 800, 820, 50, { face: 'marker', col: SK.red, key: 'vh', reveal: ev(when('very'), 0.3) }); for (let i = 0; i < 2; i++) sweat(870 + i * 12, 940 + i * 8, ((TT * 1.3 + i * 0.5) % 1), 'sw6' + i); }
  pageTag('the task');
  say([[S[5], ['trace a star...'], [[0, 'star...']]], [when('but', 2), ['...seeing your hand', 'only in a mirror.'], [[1, 'mirror.']]], [when('hard'), ["it's very hard."], [[0, 'hard.']]]], S[5]);
},
// ---- 7. three days: better and better ----------------------------------------------------------------
() => {
  sketchPage({ grid: 'dots' }); ground('g7', GY);
  [[0, 255, 60], [1, 540, 26], [2, 825, 6]].forEach(([i, cx, wob]) => {
    const t0 = when('days') + i * 0.6, P = sketchBox(cx - 130, 430, 260, 280, 8, 0.03);
    if (TT < t0 - 0.3) return;
    gfill(P, '#fffdf6', { key: 'pf' + i, off: [4, 4], a: clamp(ev(t0 - 0.3, 0.3)) }); gline(P, { closed: true, key: 'pn' + i, w: 4, part: ev(t0 - 0.3, 0.3) });
    tracedStar(cx, 570, 95, wob, ev(t0, 0.6), 'd7' + i);
    handLetter('day ' + (i + 1), cx, 770, 48, { face: 'marker', col: SK.ink, key: 'dl' + i, reveal: ev(t0, 0.3) });
  });
  if (TT >= when('perfect')) checkMark(890, 690, 0.8, ev(when('perfect'), 0.3));
  if (TT >= when('better', 2)) arrowPencil([[180, 820], [900, 820]], ev(when('better', 2), 0.5), { key: 'ar7', col: SK.green, w: 5 });
  person(290, onGround(GY, 58), 58, { key: 'hero', mood: TT >= when('swear') ? 'puzzled' : 'happy', look: [1, -0.3], arms: [-1.2, -1.2] });
  speech(430, 880, 500, 170, ['"I\'ve never', 'done this before."'], [320, 960], ev(when('swear'), 0.5), 'b7', { size: 46 });
  pageTag('three days');
  say([[S[6], ['3 days: better', 'and better.'], [[1, 'better.']]], [when('almost'), ['almost perfect.'], [[0, 'perfect.']]],
       [when('swear'), ['"never done', 'this before."'], [[0, 'never']]]], S[6]);
},
// ---- 8. two kinds of memory -------------------------------------------------------------------------
() => {
  sketchPage({ grid: 'dots' });
  const A = sketchBox(110, 420, 380, 300, 10, 0.03), Bx = sketchBox(570, 420, 370, 300, 10, 0.03);
  gfill(A, '#fffdf6', { key: 'af', off: [5, 5] }); gline(A, { closed: true, key: 'a', w: 5, part: ev(S[7], 0.3) });
  handLetter('MIND', 300, 500, 60, { face: 'marker', col: SK.ink, key: 'mnd', reveal: ev(S[7] + 0.1, 0.3) });
  graphiteScribble(300, 610, 160, 60, 'fog8');
  if (TT >= when('forgot')) handLetter('forgot', 300, 690, 44, { col: SK.red, key: 'fg', reveal: ev(when('forgot'), 0.3) });
  if (TT >= when('hands')) {
    gfill(Bx, '#fffdf6', { key: 'bf', off: [5, 5] }); gline(Bx, { closed: true, key: 'b', w: 5, part: ev(when('hands'), 0.3) });
    handLetter('HANDS', 755, 500, 60, { face: 'marker', col: SK.ink, key: 'hnd', reveal: ev(when('hands'), 0.3) });
    tracedStar(720, 610, 60, 4, ev(when('hands') + 0.2, 0.5), 'st8');
    checkMark(860, 620, 0.8, ev(when('remembered'), 0.3));
    handLetter('remembered', 755, 690, 44, { col: SK.green, key: 'rm', reveal: ev(when('remembered'), 0.3) });
  }
  // "memory isn't one thing"
  if (TT >= when('memory')) {
    handLetter('MEMORY', 540, 880, 70, { face: 'marker', col: SK.ink, key: 'mem', reveal: ev(when('memory'), 0.3) });
    arrowPencil([[470, 910], [300, 1010]], ev(when('memory') + 0.4, 0.3), { key: 'm1' });
    arrowPencil([[610, 910], [780, 1010]], ev(when('memory') + 0.5, 0.3), { key: 'm2' });
    handLetter('events + facts', 290, 1070, 44, { col: SK.ink, key: 'ef', reveal: ev(when('memory') + 0.6, 0.3) });
  }
  if (TT >= when('skill')) handLetter('skills', 790, 1070, 48, { face: 'marker', col: SK.green, key: 'sk', reveal: ev(when('skill'), 0.3) });
  if (TT >= when('system')) handLetter('a different system', 540, 1200, 52, { face: 'marker', col: SK.ink, key: 'ds', reveal: ev(when('system') - 0.4, 0.4) });
  pageTag('the twist');
  say([[S[7], ['your mind forgot.'], [[0, 'forgot.']]], [when('hands'), ['your hands', 'remembered.'], [[1, 'remembered.']]],
       [when('memory'), ["memory isn't", 'one thing.'], [[1, 'one thing.']]]], S[7]);
},
// ---- 9. your hands ------------------------------------------------------------------------------------
() => {
  sketchPage({ grid: 'dots' }); ground('g9', GY);
  const r = 80, hy = onGround(GY, r), q = TT >= when('what');
  person(540, hy, r, { key: 'hero', mood: q ? 'happy' : 'calm', look: [0, q ? 0.6 : 0], arms: q ? [0.3, 0.3] : [-1.2, -1.2] });
  if (!q) {
    handLetter('Henry Molaison', 540, 520, 76, { face: 'marker', col: SK.ink, key: 'hm', reveal: ev(S[8] + 0.2, 0.5) });
    if (TT >= when('science')) handLetter('known as "H.M."', 540, 620, 56, { col: SK.graph, key: 'kn', reveal: ev(when('science'), 0.4) });
  } else {
    speech(170, 420, 740, 230, ['what do your hands', 'remember?'], [540, hy - 100], ev(when('what'), 0.6), 'q9', { face: 'marker', size: 60 });
    for (const s of [-1, 1]) sparkle(540 + s * 160, hy + 70, 46, ((TT - when('what')) * 1.2 + (s > 0 ? 0.5 : 0)) % 1, 'spk' + s, SK.ink);
  }
  pageTag('your turn');
  say([[S[8], ['you were', 'Henry Molaison.'], [[1, 'Henry Molaison.']]], [when('science'), ['known to science', 'as H.M.'], [[1, 'H.M.']]],
       [when('what'), ['what do your hands', 'remember?'], [[1, 'remember?']]]], S[8]);
},
];
