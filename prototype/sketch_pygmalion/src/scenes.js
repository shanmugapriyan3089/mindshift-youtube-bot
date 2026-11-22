// =====================================================================
//  SCENES — The Pygmalion Effect (Rosenthal & Jacobson, 1968), sketchbook. Every time comes from the narration: when('word', n).
//  Shared helpers (person, say, speech, iconPeople, stamp, ...) live in ../sketch_kit/people.js.
//  Cast: YOU (a pupil, terracotta t-shirt) · your teacher (smock, glasses) · a researcher (lab coat).
// =====================================================================

const GY = 1235;
const HITS = [when('bloom'), when('lie'), when('twice'), when('catch')];

const teacher = (x, r, o = {}) => person(x, onGround(GY, r), r, { key: o.key ?? 'tch', outfit: 'smock', shirt: '#c9b27c', hair: 'mop', hairCol: '#a0703c', glasses: true,
                                                               mood: o.mood ?? 'calm', look: o.look ?? [1, 0], arms: o.arms ?? [-1.2, -1.2] });
// a little school desk in front of a pupil
function desk(x, key, part = 1) {
  const D = sketchBox(x - 110, 1110, 220, 24, 4, 0.02);
  gfill(D, '#ecc995', { key: key + 'f', off: [3, 3], a: clamp(part * 2) }); gline(D, { closed: true, key, w: 5, part });
  for (const s of [-1, 1]) gline([[x + s * 95, 1134], [x + s * 95, GY]], { key: key + 'l' + s, w: 5, second: false, part });
}
// a growing flower: k 0..1
function flower(x, gy, h, k, key) {
  if (k <= 0) return;
  const top = gy - h * EZ.io(clamp(k));
  gline([[x, gy], [x + 6, (gy + top) / 2], [x, top]], { key: key + 's', w: 5, col: SK.green, second: false });
  gline(loopPts(x + 26, (gy + top) / 2 + 10, 24, 12, 0.05), { key: key + 'lf', w: 4, col: SK.green, second: false, part: clamp(k * 2 - 0.5) });
  if (k >= 0.6) { const p = clamp((k - 0.6) / 0.4);
    for (let i = 0; i < 6; i++) { const a = i * TAU / 6; const P = loopPts(x + Math.cos(a) * 26, top + Math.sin(a) * 26, 18, 18, 0.04);
      gfill(P, '#f1bf2c', { key: key + 'pf' + i, off: [0, 0], a: p }); gline(P, { key: key + 'p' + i, w: 3, second: false, part: p }); }
    gfill(loopPts(x, top, 16, 16, 0.04), '#a0703c', { key: key + 'c', off: [0, 0], a: p }); }
}
// a sheet of paper with ruled lines
function sheet(x, y, w, h, key, part = 1, n = 4) {
  const P = sketchBox(x, y, w, h, 6, 0.02);
  gfill(P, '#fffdf6', { key: key + 'f', off: [5, 5], a: clamp(part * 2) }); gline(P, { closed: true, key, w: 5, part });
  for (let i = 0; i < n; i++) gpencil([[x + 30, y + 90 + i * (h - 120) / n], [x + w - 30 - (i % 2) * 60, y + 90 + i * (h - 120) / n]], { key: key + 'r' + i, w: 3, a: 0.5, part: clamp(part * 2 - 1) });
}

const SCENES = [
// ---- 1. you're about to bloom -------------------------------------------------------------------
() => {
  sketchPage({ grid: 'dots' }); ground('g1', GY);
  teacher(230, 64, { mood: TT >= when('bloom') ? 'wow' : 'calm', look: [1, 0], arms: [-1.2, 0.3] });
  sheet(250, 900, 150, 110, 'note1', ev(when('told'), 0.4), 1);
  desk(690, 'dk1', ev(S[0], 0.4));
  person(690, onGround(GY, 46), 46, { key: 'hero', mood: TT >= when('idea') ? 'puzzled' : 'calm', look: [0, 0.8], arms: [-0.5, -0.5] });
  flower(870, GY, 240, ev(when('bloom'), 1.2), 'fl1');
  speech(120, 470, 440, 150, ['"about to bloom!"'], [240, 820], ev(when('bloom') - 0.2, 0.4), 'b1', { size: 46 });
  if (TT >= when('idea')) handLetter('?', 760, 900, 80, { face: 'marker', col: SK.graph, key: 'q1', reveal: ev(when('idea'), 0.2) });
  pageTag('you');
  say([[S[0], ['your teacher is told', 'something about you.'], [[0, 'teacher']]], [when('bloom') - 0.7, ["you're about", 'to bloom.'], [[1, 'bloom.']]],
       [when('and', 1), ['and you have', 'no idea.'], [[1, 'no idea.']]]], S[0]);
},
// ---- 2. 1964, California: the test ---------------------------------------------------------------
() => {
  sketchPage({ grid: 'ruled' }); ground('g2', GY);
  // the school
  const sp = ev(when('school') - 0.2, 0.5), SH = [[120, 760], [120, 560], [270, 450], [420, 560], [420, 760]];
  gfill(SH, '#fffdf6', { key: 'shf', off: [5, 5], a: clamp(sp) }); gline(SH, { closed: true, key: 'sh', w: 5, part: sp });
  const DR = sketchBox(240, 660, 60, 100, 4, 0.02); gfill(DR, '#c9b27c', { key: 'drf', off: [0, 0], a: clamp(sp) }); gline(DR, { closed: true, key: 'dr', w: 4, part: sp });
  gline(loopPts(270, 545, 22, 22, 0.05), { key: 'bell', w: 4, part: sp });
  handLetter('CALIFORNIA, 1964', 540, 860, 54, { face: 'marker', col: SK.ink, key: 'ca', reveal: ev(when('california') - 0.2, 0.5) });
  // the test paper with its fancy name
  sheet(540, 420, 380, 360, 'tp', ev(when('test') - 0.2, 0.4), 3);
  if (TT >= when('harvard')) { handLetter('HARVARD', 730, 490, 46, { face: 'marker', col: SK.red, key: 'hv', reveal: ev(when('harvard'), 0.3) });
                              handLetter('TEST OF...', 730, 545, 34, { col: SK.ink, key: 'hv2', reveal: ev(when('harvard') + 0.2, 0.3) }); }
  [[300, 0], [540, 1], [780, 2]].forEach(([x, i]) => { if (TT < when('every') + i * 0.15) return;
    desk(x, 'dk2' + i); person(x, onGround(GY, 36), 36, { key: i === 1 ? 'hero' : 'kid' + i, shirt: i === 1 ? undefined : ['#7fa77a', '', '#8fa7c2'][i], hair: i === 2 ? 'short' : 'mop', mood: 'calm', look: [0, 1], arms: [-0.4, -0.4] }); });
  pageTag('1964');
  say([[S[1], ['1964, a school', 'in California.'], [[1, 'California.']]], [when('every'), ['every child', 'takes a test...'], [[1, 'test...']]],
       [when('fancy'), ['...with a fancy', 'Harvard name.'], [[1, 'Harvard']]]], S[1]);
},
// ---- 3. the list: about 1 in 5 will bloom ----------------------------------------------------------
() => {
  sketchPage({ grid: 'dots' }); ground('g3', GY);
  person(260, onGround(GY, 60), 60, { key: 'res', outfit: 'coat', hair: 'short', hairCol: '#555', mood: 'calm', look: [1, 0], arms: [-1.2, 0.2] });
  teacher(800, 60, { look: [-1, 0], arms: [0.2, -1.2], mood: TT >= when('bloom', 2) ? 'wow' : 'calm' });
  const lp = ev(when('list') - 0.2, 0.4), LX = 420 + 140 * EZ.io(ev(when('list') + 0.4, 0.6));
  sheet(LX, 860, 120, 150, 'lst', lp, 2);
  if (TT >= when('list')) handLetter('LIST', LX + 60, 905, 30, { face: 'marker', col: SK.ink, key: 'lstl', reveal: ev(when('list'), 0.3) });
  if (TT >= when('children')) {
    iconPeople(180, 440, 5, 1, 160, 1, ev(when('soon'), 0.4), 'ic3', SK.green);
    handLetter('about 1 in 5', 540, 700, 56, { face: 'marker', col: SK.ink, key: 'p15', reveal: ev(when('children') - 0.3, 0.4) });
  }
  pageTag('the list');
  say([[S[2], ['your teacher', 'gets a list.'], [[1, 'list.']]], [when('about', 2), ['about 1 in 5 kids', 'will soon bloom.'], [[1, 'bloom.']]]], S[2]);
},
// ---- 4. your name is on it, and it's random --------------------------------------------------------
() => {
  sketchPage({ grid: 'ruled' });
  sheet(140, 420, 440, 560, 'big', ev(S[3], 0.4), 0);
  handLetter('will bloom:', 360, 500, 48, { face: 'marker', col: SK.ink, key: 'wb', reveal: ev(S[3] + 0.2, 0.4) });
  ['Ann', 'YOU', 'Leo', 'Maya'].forEach((n, i) => {
    const y = 600 + i * 95;
    if (i === 1) { const [x0, x1] = handLetter(n, 360, y, 60, { face: 'marker', col: SK.terra, key: 'nm' + i, reveal: ev(when('name', 2), 0.3) }); if (TT >= when('name', 2) + 0.3) highlight(x0, x1, y - 20, 50, ev(when('name', 2) + 0.3, 0.3)); }
    else handLetter(n, 360, y, 48, { col: SK.ink, key: 'nm' + i, reveal: ev(S[3] + 0.4 + i * 0.1, 0.3) });
  });
  stamp('FAKE', 760, 600, when('lie'), -0.14, 'sfk');
  // "picked at random": a pair of dice
  if (TT >= when('picked') - 0.2) [[680, 1020, 0.2, 5], [820, 1060, -0.25, 3]].forEach(([x, y, rot, n], i) => {
    const p = ev(when('picked') - 0.2 + i * 0.15, 0.3);
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot);
    const D = sketchBox(-60, -60, 120, 120, 14, 0.02); gfill(D, '#fffdf6', { key: 'dcf' + i, off: [4, 4], a: clamp(p * 2) }); gline(D, { closed: true, key: 'dc' + i, w: 5, part: p });
    if (p >= 1) { const pips = n === 5 ? [[-30, -30], [30, -30], [0, 0], [-30, 30], [30, 30]] : [[-30, -30], [0, 0], [30, 30]];
      ctx.fillStyle = SK.ink; for (const [px, py] of pips) { ctx.beginPath(); ctx.arc(px, py, 10, 0, TAU); ctx.fill(); } }
    ctx.restore();
  });
  if (TT >= when('random')) handLetter('at random', 750, 900, 56, { face: 'marker', col: SK.red, key: 'rnd', reveal: ev(when('random'), 0.3) });
  pageTag('the truth');
  say([[S[3], ['your name is', 'on the list.'], [[0, 'your name']]], [when('but'), ['but the list', 'is a lie.'], [[1, 'lie.']]],
       [when('names'), ['the names were', 'picked at random.'], [[1, 'random.']]]], S[3]);
},
// ---- 5. only the expectation changed ---------------------------------------------------------------
() => {
  sketchPage({ grid: 'dots' }); ground('g5', GY);
  const warm = TT >= when('maybe');
  teacher(270, 64, { mood: warm ? 'happy' : 'calm', look: [1, 0.3], arms: [-1.2, warm ? 0.1 : -1.2] });
  desk(720, 'dk5');
  person(720, onGround(GY, 46), 46, { key: 'hero', mood: TT >= when('smiles') ? 'happy' : 'calm', look: [-1, 0], arms: [-0.5, TT >= when('answer') ? 1.2 : -0.5] });
  if (TT < when('only')) handLetter('nothing changed', 720, 860, 46, { col: SK.graph, key: 'nc', reveal: ev(when('nothing'), 0.4) });
  else handLetter('expects', 270, 520, 60, { face: 'marker', col: SK.ink, key: 'exp', reveal: ev(when('expects') - 0.3, 0.4) });
  [['more smiles', 'smiles'], ['more patience', 'patience'], ['more time', 'time']].forEach(([s, wd], i) => {
    if (TT < when(wd) - 0.2) return;
    handLetter(s, 690, 500 + i * 80, 48, { face: 'marker', col: SK.green, key: 'm' + i, reveal: ev(when(wd) - 0.2, 0.4) });
  });
  if (TT >= when('maybe') && TT < when('smiles') + 4) handLetter('(maybe)', 690, 760, 36, { col: SK.graph, key: 'mb', reveal: ev(when('maybe'), 0.3) });
  pageTag('expectations');
  say([[S[4], ['nothing about you', 'has changed.'], [[0, 'nothing']]], [when('only'), ['only what your', 'teacher expects.'], [[1, 'expects.']]],
       [when('maybe'), ['maybe more smiles,', 'more patience...'], [[0, 'smiles,']]]], S[4]);
},
// ---- 6. first grade: about twice the IQ gain --------------------------------------------------------
() => {
  sketchPage({ grid: 'dots' });
  handLetter('IQ gain, first grade', 540, 480, 54, { face: 'marker', col: SK.ink, key: 'ttl', reveal: ev(when('first') - 0.3, 0.5) });
  const base = 1140;
  gline([[140, base], [940, base]], { key: 'ax', w: 5, part: ev(S[5], 0.4) });
  [[360, 0.42, 'others', '#8fa7c2', when('tested') + 0.3], [720, 0.95, 'bloomers', SK.terra, when('twice') - 0.2]].forEach(([x, h, lab, col, t], i) => {
    if (TT < t) return;
    const k = EZ.io(ev(t, 0.7)), top = base - 520 * h * k, P = [[x - 100, base], [x - 100, top], [x + 100, top], [x + 100, base]];
    scribbleFill(P, col, { key: 'bar' + i, gap: 14, w: 4, base: 0.25 });
    gline(P, { key: 'baro' + i, w: 5 });
    handLetter(lab, x, base + 60, 44, { col: SK.ink, key: 'bl' + i, reveal: ev(t, 0.3) });
  });
  if (TT >= when('twice') + 0.6) handLetter('about 2x', 400, 680, 64, { face: 'marker', col: SK.green, key: 'x2', reveal: ev(when('twice') + 0.6, 0.4) });
  pageTag('the result');
  say([[S[5], ['a year later,', 'a new test.'], [[1, 'new test.']]], [when('first'), ['in first grade, about', 'twice the IQ gain.'], [[1, 'twice']]]], S[5]);
},
// ---- 7. the catch: flawed test, older grades ~nothing ------------------------------------------------
() => {
  sketchPage({ grid: 'ruled' });
  sheet(150, 420, 360, 420, 'tp7', ev(S[6], 0.4), 4);
  if (TT >= when('flaws')) for (let i = 0; i < 3; i++) gline(loopPts(260 + i * 80, 560 + i * 90, 46, 30, 0.1), { key: 'fl' + i, w: 4, col: SK.red, second: false, part: ev(when('flaws') + i * 0.15, 0.3) });
  stamp('FLAWED', 330, 900, when('flaws') + 0.4, -0.1, 'sfl');
  if (TT >= when('critics')) { const g = 700, m = 720, rr = 80;
    gline(loopPts(g, m, rr, rr, 0.05), { key: 'mg', w: 7, part: ev(when('critics'), 0.4) });
    gline([[g + rr * 0.7, m + rr * 0.7], [g + rr * 1.6, m + rr * 1.6]], { key: 'mgh', w: 14, second: false, part: ev(when('critics') + 0.3, 0.3) }); }
  if (TT >= when('older')) {
    handLetter('older grades', 540, 1040, 50, { face: 'marker', col: SK.ink, key: 'og', reveal: ev(when('older'), 0.4) });
    [[440, 0.42], [640, 0.45]].forEach(([x, h], i) => { const P = [[x - 70, 1240], [x - 70, 1240 - 120 * h * EZ.io(ev(when('older') + 0.4, 0.5))], [x + 70, 1240 - 120 * h * EZ.io(ev(when('older') + 0.4, 0.5))], [x + 70, 1240]];
      scribbleFill(P, i ? SK.terra : '#8fa7c2', { key: 'ob' + i, gap: 12, w: 3, base: 0.25 }); gline(P, { key: 'obo' + i, w: 4 }); });
    if (TT >= when('almost')) handLetter('= almost no effect', 760, 1120, 40, { col: SK.red, key: 'ane', reveal: ev(when('almost'), 0.4) });
  }
  pageTag('the catch');
  say([[S[6], ["but here's", 'the catch.'], [[1, 'catch.']]], [when('critics'), ['critics found big', 'flaws in the test.'], [[1, 'flaws']]],
       [when('and', 2), ['older grades:', 'almost no effect.'], [[1, 'no effect.']]]], S[6]);
},
// ---- 8. real, but smaller ---------------------------------------------------------------------------
() => {
  sketchPage({ grid: 'dots' });
  // a gauge: the needle drops from "huge" to "small"
  const cx = 540, cy = 900, R = 300;
  gline(arcPts(cx, cy, R, Math.PI, TAU, 30), { key: 'gauge', w: 6, part: ev(S[7], 0.5) });
  for (let i = 0; i <= 4; i++) { const a = Math.PI + i * Math.PI / 4; gline([[cx + Math.cos(a) * (R - 30), cy + Math.sin(a) * (R - 30)], [cx + Math.cos(a) * R, cy + Math.sin(a) * R]], { key: 'tk' + i, w: 4, second: false, part: ev(S[7] + 0.3, 0.3) }); }
  handLetter('small', cx - R + 10, cy + 60, 40, { col: SK.ink, key: 'gs', reveal: ev(S[7] + 0.4, 0.3) });
  handLetter('huge', cx + R - 10, cy + 60, 40, { col: SK.ink, key: 'gh', reveal: ev(S[7] + 0.4, 0.3) });
  const na = Math.PI + lerp(Math.PI * 0.85, Math.PI * 0.3, EZ.io(ev(when('smaller') - 0.2, 0.8)));
  gline([[cx, cy], [cx + Math.cos(na) * (R - 50), cy + Math.sin(na) * (R - 50)]], { key: 'needle', w: 8, col: SK.red, second: false });
  gfill(loopPts(cx, cy, 18, 18, 0.04), SK.ink, { key: 'hub', off: [0, 0] });
  if (TT >= when('real')) handLetter('real', 540, 480, 64, { face: 'marker', col: SK.green, key: 'real', reveal: ev(when('real'), 0.3) });
  if (TT >= when('strongest')) {
    handLetter('strongest for:', 540, 1020, 46, { face: 'marker', col: SK.ink, key: 'sf', reveal: ev(when('strongest'), 0.3) });
    handLetter('young kids', 300, 1110, 44, { col: SK.terra, key: 'yk', reveal: ev(when('young'), 0.3) });
    if (TT >= when('others')) handLetter('the written off', 720, 1110, 44, { col: SK.terra, key: 'wo', reveal: ev(when('others'), 0.4) });
  }
  pageTag('later studies');
  say([[S[7], ['the effect is real...'], [[0, 'real...']]], [when('just'), ['...just usually', 'smaller.'], [[1, 'smaller.']]],
       [when('strongest'), ['strongest for kids', 'others wrote off.'], [[1, 'wrote off.']]]], S[7]);
},
// ---- 9. living up, or down ---------------------------------------------------------------------------
() => {
  sketchPage({ grid: 'dots' }); ground('g9', GY);
  person(380, onGround(GY, 76), 76, { key: 'hero', mood: TT >= when('whose') ? 'puzzled' : 'happy', look: [1, -0.3], arms: [-1.2, -1.2] });
  flower(560, GY, 260, ev(when('belief'), 1.2), 'fl9');
  if (TT >= when('belief')) handLetter('belief', 560, 850, 44, { face: 'marker', col: SK.green, key: 'bel', reveal: ev(when('belief'), 0.3) });
  if (TT >= when('up')) { arrowPencil([[780, 1160], [780, 860]], ev(when('up'), 0.4), { key: 'au', col: SK.green, w: 7 }); handLetter('up', 860, 900, 46, { face: 'marker', col: SK.green, key: 'upl', reveal: ev(when('up'), 0.3) }); }
  if (TT >= when('down')) { arrowPencil([[700, 860], [700, 1160]], ev(when('down'), 0.4), { key: 'ad', col: SK.graph, w: 7 }); handLetter('down', 620, 1180, 40, { face: 'marker', col: SK.graph, key: 'dnl', reveal: ev(when('down'), 0.3) }); }
  speech(150, 420, 780, 240, ['whose expectations', 'are you living up to?'], [400, 880], ev(when('whose'), 0.5), 'q9', { face: 'marker', size: 54 });
  pageTag('your turn');
  say([[S[8], ["your teacher didn't", 'change you.'], [[1, 'change you.']]], [when('their'), ['their belief in you', 'did, a little.'], [[0, 'belief']]],
       [when('whose'), ['whose expectations', 'are you living up to?'], [[0, 'whose']]]], S[8]);
},
];
