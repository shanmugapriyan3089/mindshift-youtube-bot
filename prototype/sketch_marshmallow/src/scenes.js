// =====================================================================
//  SCENES — The Marshmallow Test (Mischel; Kidd et al., 2013), sketchbook. Times come from the narration: when('word', n).
//  Shared helpers (person, say, speech, iconPeople, stamp, ...) live in ../sketch_kit/people.js.
//  Cast: YOU = the four-year-old (terracotta t-shirt) · the RESEARCHER (lab coat) · other kids (blue/green/khaki).
// =====================================================================

const GY = 1235;
const HITS = [when('marshmallow'), when('smaller'), when('never'), when('trust')];
const SHIRTS = ['#8fa7c2', '#7fa77a', '#c9b27c', '#9aa3ad', '#b48ead'];
const HAIRS = ['#2f2620', '#7a5a3c', '#555', '#a0703c', '#222'];

// one marshmallow standing on (x, y = its bottom); s = width; dashed = only an outline (not here yet)
function mallow(x, y, s, key, part = 1, dashed = false) {
  if (part <= 0) return;
  const h = s * 0.8, P = sketchBox(x - s / 2, y - h, s, h, s * 0.28, 0.02);
  if (dashed) { ctx.save(); ctx.setLineDash([10, 10]); gpencil(P, { closed: true, key: key + 'd', w: 3, a: 0.8, part }); ctx.restore(); return; }
  gfill(P, '#fffdf6', { key: key + 'f', off: [3, 3], a: clamp(part) });
  gline(P, { closed: true, key: key + 'o', w: 4, part });
  gline(arcPts(x, y - h + s * 0.2, s * 0.42, Math.PI * 0.15, Math.PI * 0.85, 8), { key: key + 't', w: 2.5, col: SK.graph, second: false, part });
}
// a plate (ellipse) centred at (x, y)
function plate(x, y, rx, key, part = 1) {
  const P = loopPts(x, y, rx, rx * 0.2, 0.04);
  gfill(P, '#fffdf6', { key: key + 'f', off: [3, 3], a: clamp(part) });
  gline(P, { key: key + 'o', w: 4, part });
}
// a table top from x0 to x1 at y (people drawn before it are hidden behind it)
function table(x0, x1, y, key, part = 1) {
  const T = [[x0, y], [x1, y], [x1 - 15, y + 70], [x0 + 15, y + 70]];
  gfill(T, '#ecc995', { key: key + 'f', off: [4, 4], a: clamp(part) });
  gline(T, { closed: true, key: key + 'o', w: 5, part });
  for (const x of [x0 + 40, x1 - 40]) gline([[x, y + 70], [x, GY]], { key: key + 'l' + x, w: 5, second: false, part });
}
// a kid standing behind a table whose top is at ty
function kidAt(x, ty, r, o = {}) { person(x, ty - 3.6 * r + r * 1.9, r, o); }
// a clock face; `hand` 0..1 is one turn of the minute hand; `wedge` 0..1 shades that much of the dial
function clockDial(cx, cy, r, hand, key, part = 1, wedge = 0, wcol = SK.hilite) {
  const C = loopPts(cx, cy, r, r, 0.06);
  gfill(C, '#fffdf6', { key: key + 'f', off: [4, 4], a: clamp(part) });
  if (wedge > 0) { const W = [[cx, cy]]; for (let i = 0; i <= 24; i++) { const a = -Math.PI / 2 + wedge * TAU * i / 24; W.push([cx + Math.cos(a) * r * 0.9, cy + Math.sin(a) * r * 0.9]); } scribbleFill(W, wcol, { key: key + 'w', gap: 10, w: 4, part: 1, base: 0.25 }); }
  gline(C, { key: key + 'o', w: 5, part });
  for (let i = 0; i < 12; i++) { const a = i * TAU / 12; gline([[cx + Math.cos(a) * r * 0.8, cy + Math.sin(a) * r * 0.8], [cx + Math.cos(a) * r * 0.92, cy + Math.sin(a) * r * 0.92]], { key: key + 't' + i, w: 3, second: false, a: clamp(part) }); }
  const a = -Math.PI / 2 + hand * TAU;
  gline([[cx, cy], [cx + Math.cos(a) * r * 0.75, cy + Math.sin(a) * r * 0.75]], { key: key + 'm', w: 5, second: false, a: clamp(part) });
}
// a box of crayons
function crayons(x, y, s, key, part = 1) {
  const cols = ['#e0483a', '#f1bf2c', '#4f9d5d', '#5b7fc2', '#b48ead'];
  cols.forEach((c, i) => {
    const cx = x - s * 0.4 + i * s * 0.2, P = [[cx - s * 0.07, y - s * 0.3], [cx, y - s * 0.55], [cx + s * 0.07, y - s * 0.3], [cx + s * 0.07, y], [cx - s * 0.07, y]];
    gfill(P, c, { key: key + 'cf' + i, off: [0, 0], a: clamp(part) }); gline(P, { closed: true, key: key + 'c' + i, w: 2.5, second: false, part });
  });
  const Bx = sketchBox(x - s * 0.55, y - s * 0.15, s * 1.1, s * 0.5, 6);
  gfill(Bx, '#f1bf2c', { key: key + 'bf', off: [3, 3], a: clamp(part) }); gline(Bx, { closed: true, key: key + 'b', w: 4, part });
}

const SCENES = [
// ---- 1. one now, or two later ----------------------------------------------------------------
() => {
  sketchPage({ grid: 'dots' });
  const ty = 1060;
  kidAt(300, ty, 70, { key: 'hero', mood: TT >= when('marshmallow') ? 'wow' : 'calm', look: TT >= when('marshmallow') ? [1, 0.5] : [0, 0], arms: [-1.2, -1.2] });
  table(110, 920, ty, 'tb1', ev(when('table') - 0.3, 0.4));
  plate(640, ty - 8, 110, 'pl1', ev(when('marshmallow') - 0.3, 0.3));
  mallow(640, ty - 12, 100, 'm1', ev(when('marshmallow'), 0.3));
  // the choice: NOW = one, WAIT = two
  const c1 = sketchBox(120, 440, 360, 320, 10, 0.03), c2 = sketchBox(570, 440, 360, 320, 10, 0.03);
  if (TT >= when('eat')) { gfill(c1, '#fffdf6', { key: 'c1f', off: [5, 5] }); gline(c1, { closed: true, key: 'c1', w: 5, part: ev(when('eat'), 0.3) });
    handLetter('NOW', 300, 530, 64, { face: 'marker', col: SK.ink, key: 'now', reveal: ev(when('now'), 0.3) }); mallow(300, 700, 90, 'mn', ev(when('now') + 0.2, 0.3)); }
  if (TT >= when('wait')) { gfill(c2, '#fffdf6', { key: 'c2f', off: [5, 5] }); gline(c2, { closed: true, key: 'c2', w: 5, part: ev(when('wait'), 0.3) });
    handLetter('WAIT', 750, 530, 64, { face: 'marker', col: SK.ink, key: 'wt', reveal: ev(when('wait'), 0.3) });
    mallow(690, 700, 90, 'mw1', ev(when('two') - 0.1, 0.3)); mallow(810, 700, 90, 'mw2', ev(when('two'), 0.3)); }
  pageTag('age four');
  say([[S[0], ["you're four."], [[0, 'four.']]], [when('marshmallow') - 0.4, ['a marshmallow', 'on the table.'], [[0, 'marshmallow']]],
       [when('eat'), ['eat it now,', 'or wait and get two.'], [[1, 'two.']]]], S[0]);
},
// ---- 2. alone with it --------------------------------------------------------------------------
() => {
  sketchPage({ grid: 'ruled' }); ground('g2', GY);
  // the door on the right; open until "closes"
  const closed = TT >= when('closes') + 0.3, D = sketchBox(700, 700, 210, 535, 6, 0.02);
  if (!closed) gfill(D, '#3b3530', { key: 'dop', off: [0, 0], a: 0.55 });
  // "the researcher walks out"
  if (!closed && TT >= when('researcher') - 0.3) {
    const k = EZ.io(ev(when('walks'), 1.2));
    person(lerp(560, 805, k), onGround(GY, 62), 62, { key: 'res', outfit: 'coat', hair: 'short', hairCol: '#6b6b6b', glasses: true, mood: 'calm', look: [1, 0], arms: [-1.2, -1.2] });
  }
  if (closed) gfill(D, '#d9b88a', { key: 'dcl', off: [3, 3] });
  gline(D, { closed: true, key: 'door', w: 5 });
  if (closed) { gline(loopPts(730, 980, 10, 10, 0.05), { key: 'knob', w: 3, second: false }); handLetter('slam', 805, 660, 44, { col: SK.graph, key: 'slam', reveal: ev(when('closes') + 0.3, 0.2) }); }
  const ty = 1060;
  kidAt(260, ty, 64, { key: 'hero', mood: TT >= when('idea') ? 'puzzled' : 'calm', look: [1, 0], arms: [-1.2, -1.2] });
  table(90, 560, ty, 'tb2');
  plate(420, ty - 8, 90, 'pl2'); mallow(420, ty - 12, 84, 'm2');
  if (TT >= when('idea')) { clockDial(300, 600, 110, 0, 'clk2', ev(when('idea'), 0.3)); handLetter('?', 300, 640, 100, { face: 'marker', col: SK.red, key: 'q2', reveal: ev(when('idea') + 0.3, 0.2) }); }
  pageTag('stanford, 1960s');
  say([[S[1], ['stanford, 1960s.'], [[0, 'stanford,']]], [when('researcher'), ['the researcher', 'walks out.'], [[1, 'walks out.']]],
       [when('you', 2), ['no idea when', "he'll come back."], [[0, 'no idea']]]], S[1]);
},
// ---- 3. how kids waited (or didn't) ------------------------------------------------------------
() => {
  sketchPage({ grid: 'dots' });
  const ty = 1100;
  clockDial(540, 560, 110, (TT - S[2]) * 0.15, 'clk3', ev(S[2], 0.3));
  const xs = [180, 400, 640, 860];
  const tEat = when('seconds') - 0.3, tCover = when('cover'), tSing = when('sing'), tTurn = when('turn');
  kidAt(xs[0], ty, 44, { key: 'k0', shirt: SHIRTS[0], hairCol: HAIRS[0], mood: TT >= tEat ? 'happy' : 'calm', arms: TT >= tEat && TT < tEat + 0.6 ? [-1.2, 0.9] : [-1.2, -1.2] });
  kidAt(xs[1], ty, 44, { key: 'k1', shirt: SK.terra, hairCol: HAIRS[1], mood: 'calm', arms: TT >= tCover ? [1.4, 1.4] : [-1.2, -1.2], look: [0, 0] });
  kidAt(xs[2], ty, 44, { key: 'k2', shirt: SHIRTS[1], hairCol: HAIRS[2], hair: 'short', mood: TT >= tSing ? 'happy' : 'calm', look: [0, -1] });
  kidAt(xs[3], ty, 44, { key: 'k3', shirt: SHIRTS[2], hairCol: HAIRS[3], mood: 'calm', look: TT >= tTurn ? [1, -1] : [0, 0], rot: TT >= tTurn ? 0.12 : 0 });
  table(90, 950, ty, 'tb3');
  xs.forEach((x, i) => { plate(x, ty - 6, 60, 'p3' + i); if (i > 0 || TT < tEat + 0.4) mallow(x, ty - 10, 56, 'm3' + i); });
  // labels above each kid
  if (TT >= tEat) handLetter('gulp!', xs[0], 900, 44, { face: 'marker', col: SK.red, key: 'l0', reveal: ev(tEat + 0.3, 0.3) });
  if (TT >= tCover) handLetter('eyes shut', xs[1], 900, 36, { col: SK.ink, key: 'l1', reveal: ev(tCover, 0.3) });
  if (TT >= tSing) { handLetter('la la', xs[2], 900, 40, { col: SK.ink, key: 'l2', reveal: ev(tSing, 0.3) });
    for (let i = 0; i < 2; i++) { const nx = xs[2] + 60 + i * 34, ny = 820 - i * 20 + 6 * Math.sin(B + i); gline([[nx, ny], [nx, ny - 40], [nx + 18, ny - 46]], { key: 'nt' + i, w: 3, second: false }); ctx.fillStyle = SK.ink; ctx.beginPath(); ctx.ellipse(nx - 6, ny, 8, 6, -0.4, 0, TAU); ctx.fill(); } }
  if (TT >= tTurn) handLetter('looks away', xs[3], 900, 36, { col: SK.ink, key: 'l3', reveal: ev(tTurn, 0.3) });
  pageTag('waiting');
  say([[S[2], ['some kids eat it', 'in seconds.'], [[1, 'in seconds.']]], [when('others'), ['others cover their', 'eyes, or sing...'], [[1, 'sing...']]],
       [when('turn'), ['or turn their', 'backs on it.'], [[1, 'backs']]]], S[2]);
},
// ---- 4. willpower predicts your future? ------------------------------------------------------
() => {
  sketchPage({ grid: 'dots' }); ground('g4', GY);
  person(270, onGround(GY, 66), 66, { key: 'hero', mood: TT >= when('better') ? 'happy' : 'calm', look: [1, -0.3], arms: TT >= when('tests') ? [-1.2, 0.8] : [-1.2, -1.2] });
  // "even on school tests": a test paper with a top grade
  const T = sketchBox(560, 600, 340, 400, 8, 0.03);
  if (TT >= when('school') - 0.3) {
    gfill(T, '#fffdf6', { key: 'tpf', off: [5, 5], a: clamp(ev(when('school') - 0.3, 0.3)) });
    gline(T, { closed: true, key: 'tp', w: 5, part: ev(when('school') - 0.3, 0.4) });
    handLetter('TEST', 730, 670, 50, { face: 'marker', col: SK.ink, key: 'tt', reveal: ev(when('school'), 0.3) });
    for (let i = 0; i < 4; i++) gpencil([[600, 730 + i * 50], [760, 730 + i * 50]], { key: 'tl' + i, w: 3, a: 0.6, part: ev(when('school') + 0.2 + i * 0.08, 0.2) });
    if (TT >= when('tests')) { handLetter('A+', 820, 940, 90, { face: 'marker', col: SK.green, key: 'ap', reveal: ev(when('tests'), 0.3) }); gline(loopPts(820, 910, 75, 60, 0.12), { key: 'apl', w: 5, col: SK.green, part: ev(when('tests') + 0.3, 0.3) }); }
  }
  // "willpower ... could predict your future"
  if (TT >= when('willpower')) {
    handLetter('WILLPOWER', 300, 480, 56, { face: 'marker', col: SK.ink, key: 'wp', reveal: ev(when('willpower'), 0.3) });
    arrowPencil([[490, 465], [580, 465]], ev(when('predict'), 0.3), { key: 'ar4', w: 4, col: SK.ink });
    handLetter('FUTURE?', 760, 480, 56, { face: 'marker', col: SK.ink, key: 'fu', reveal: ev(when('future'), 0.3) });
  }
  pageTag('years later');
  say([[S[3], ['kids who waited', 'did better...'], [[1, 'better...']]], [when('even'), ['even on', 'school tests.'], [[1, 'school tests.']]],
       [when('willpower'), ['willpower could', 'predict your future?'], [[0, 'willpower']]]], S[3]);
},
// ---- 5. 2018: a bigger study ---------------------------------------------------------------------
() => {
  sketchPage({ grid: 'dots' });
  iconPeople(180, 440, 10, 3, 80, 30, ev(when('bigger'), 1.2), 'ip5', SK.graph);
  if (TT >= when('about')) handLetter('about 900 kids', 540, 790, 60, { face: 'marker', col: SK.ink, key: 'k900', reveal: ev(when('about'), 0.4) });
  // the link: old result vs the retest
  if (TT >= when('link') - 0.2) {
    gpencil([[150, 1220], [930, 1220]], { key: 'ax5', w: 3, a: 0.8, part: ev(when('link') - 0.2, 0.3) });
    const b1 = sketchBox(240, 880, 200, 340, 6);
    gfill(b1, '#c9c2b4', { key: 'b1f', off: [3, 3], a: clamp(ev(when('link'), 0.3)) }); gline(b1, { closed: true, key: 'b1', w: 5, part: ev(when('link'), 0.3) });
    handLetter('before', 340, 1060, 44, { col: SK.ink, key: 'bf', reveal: ev(when('link') + 0.2, 0.3) });
  }
  if (TT >= when('smaller') - 0.2) {
    const k = clamp(ev(when('smaller') - 0.2, 0.4)), b2 = sketchBox(640, 1220 - 110 * k, 200, Math.max(4, 110 * k), 6);
    gfill(b2, SK.green, { key: 'b2f', off: [3, 3], a: 0.8 * k }); gline(b2, { closed: true, key: 'b2', w: 5 });
    handLetter('2018', 740, 1080, 50, { face: 'marker', col: SK.green, key: 'n18', reveal: ev(when('smaller'), 0.3) });
  }
  pageTag('2018');
  say([[S[4], ['in 2018, a much', 'bigger study,'], [[1, 'bigger']]], [when('about'), ['about 900 kids.'], [[0, '900']]],
       [when('link'), ['the link was', 'far smaller.'], [[1, 'far smaller.']]]], S[4]);
},
// ---- 6. what it really tracked -----------------------------------------------------------------
() => {
  sketchPage({ grid: 'ruled' });
  const t1 = when('family'), t2 = when('money'), t3 = when('early');
  // family background: a house
  if (TT >= t1 - 0.2) {
    const k = ev(t1 - 0.2, 0.4), H = [[140, 700], [140, 580], [220, 500], [300, 580], [300, 700]];
    gfill(H, '#fffdf6', { key: 'hf', off: [3, 3], a: clamp(k) }); gline(H, { closed: true, key: 'h', w: 5, part: k });
    gline(sketchBox(200, 630, 40, 70, 4), { closed: true, key: 'hd', w: 4, part: k });
    handLetter('family', 220, 790, 46, { col: SK.ink, key: 'lf', reveal: ev(t1, 0.3) });
  }
  // money: a stack of coins
  if (TT >= t2 - 0.2) for (let i = 0; i < 4; i++) {
    const C = loopPts(540, 690 - i * 34, 70, 22, 0.04);
    gfill(C, '#f1bf2c', { key: 'cf' + i, off: [2, 2], a: clamp(ev(t2 - 0.2 + i * 0.08, 0.2)) }); gline(C, { closed: true, key: 'c' + i, w: 4, part: ev(t2 - 0.2 + i * 0.08, 0.2) });
  }
  if (TT >= t2) handLetter('money', 540, 790, 46, { col: SK.ink, key: 'lm', reveal: ev(t2, 0.3) });
  // early skills: ABC blocks
  if (TT >= t3 - 0.2) ['A', 'B', 'C'].forEach((L, i) => {
    const x = 780 + (i === 2 ? 40 : i * 80), y = i === 2 ? 540 : 620, Bx = sketchBox(x, y, 76, 76, 6);
    gfill(Bx, ['#8fa7c2', '#7fa77a', '#c9b27c'][i], { key: 'bkf' + i, off: [3, 3], a: clamp(ev(t3 - 0.2 + i * 0.1, 0.2)) });
    gline(Bx, { closed: true, key: 'bk' + i, w: 4, part: ev(t3 - 0.2 + i * 0.1, 0.2) });
    handLetter(L, x + 38, y + 58, 50, { face: 'marker', col: SK.ink, key: 'bl' + i, reveal: ev(t3 + i * 0.1, 0.2) });
  });
  if (TT >= t3) handLetter('early skills', 840, 790, 46, { col: SK.ink, key: 'le', reveal: ev(t3, 0.3) });
  if (TT >= when('not')) {
    handLetter('not just', 540, 960, 54, { col: SK.ink, key: 'nj', reveal: ev(when('not'), 0.3) });
    handLetter('WILLPOWER', 540, 1100, 90, { face: 'marker', col: SK.ink, key: 'wp6', reveal: ev(when('not') + 0.4, 0.3) });
  }
  pageTag('the real story');
  say([[S[5], ['family background,', 'money,'], [[0, 'family']]], [when('early'), ['and early skills,'], [[0, 'early skills,']]],
       [when('not'), ['not just', 'willpower.'], [[1, 'willpower.']]]], S[5]);
},
// ---- 7. the broken promise (2013) -----------------------------------------------------------------
() => {
  sketchPage({ grid: 'dots' }); ground('g7', GY);
  const broken = TT >= when('never');
  person(290, onGround(GY, 58), 58, { key: 'hero', mood: broken ? 'angry' : TT >= when('crayons') ? 'happy' : 'calm', look: [1, -0.5], arms: [-1.2, -1.2] });
  person(720, onGround(GY, 74), 74, { key: 'adult', shirt: SHIRTS[1], hair: 'short', hairCol: HAIRS[4], mood: broken ? 'calm' : 'happy', look: [-1, 0.3], arms: broken ? [-0.4, -0.4] : [-1.2, 0.4] });
  if (!broken) {
    speech(110, 400, 740, 320, ['"I\'ll bring you', 'better crayons!"'], [640, 900], ev(when('promised') - 0.2, 0.5), 'b7a', { size: 50 });
    if (TT >= when('crayons')) crayons(855, 880, 140, 'cr7', ev(when('crayons'), 0.4));
  } else {
    speech(110, 400, 740, 200, ['"...sorry, no crayons."'], [640, 900], ev(when('never'), 0.4), 'b7b', { size: 50 });
    stamp('BROKEN', 300, 790, when('brought'), -0.08, 'sbp');
  }
  if (TT >= when('sneaky') - 0.2 && TT < when('promised') - 0.2) handLetter('2013', 540, 600, 120, { face: 'marker', col: SK.ink, key: 'y13', reveal: ev(when('sneaky') - 0.2, 0.3) });
  pageTag('2013');
  say([[S[6], ['then a study did', 'something sneaky.'], [[1, 'sneaky.']]], [when('promised'), ['an adult promised', 'better crayons...'], [[1, 'crayons...']]],
       [when('never'), ['and never', 'brought them.'], [[0, 'never']]]], S[6]);
},
// ---- 8. three minutes vs twelve -----------------------------------------------------------------
() => {
  sketchPage({ grid: 'dots' });
  const tL = when('those'), tK = when('kept'), t12 = when('waited', 3);
  handLetter('let down', 290, 480, 56, { face: 'marker', col: SK.ink, key: 'ld', reveal: ev(tL, 0.3) });
  clockDial(290, 680, 140, 3 / 20 * clamp(ev(when('waited', 2), 0.8)), 'ck1', ev(tL, 0.3), 3 / 20 * clamp(ev(when('waited', 2), 0.8)), '#e8a99f');
  if (TT >= when('minutes')) handLetter('~3 min', 290, 910, 64, { face: 'marker', col: SK.red, key: 'm3', reveal: ev(when('minutes'), 0.3) });
  if (TT >= tK - 0.3) {
    handLetter('promise kept', 770, 480, 50, { face: 'marker', col: SK.ink, key: 'pk', reveal: ev(tK - 0.3, 0.3) });
    clockDial(770, 680, 140, 12 / 20 * clamp(ev(t12, 1.0)), 'ck2', ev(tK - 0.3, 0.3), 12 / 20 * clamp(ev(t12, 1.0)), SK.hilite);
    if (TT >= t12 + 0.4) handLetter('~12 min', 770, 910, 64, { face: 'marker', col: SK.green, key: 'm12', reveal: ev(t12 + 0.4, 0.3) });
  }
  stamp('4x LONGER', 540, 1120, when('times'), -0.06, 's4x');
  pageTag('the result');
  say([[S[7], ['let down kids waited', 'about 3 minutes.'], [[1, '3 minutes.']]], [when('kids', 6), ['promise kept:', 'about 12.'], [[1, '12.']]],
       [when('times'), ['four times longer.'], [[0, 'four times']]]], S[7]);
},
// ---- 9. maybe it's trust ---------------------------------------------------------------------
() => {
  sketchPage({ grid: 'dots' }); ground('g9', GY);
  handLetter('WILLPOWER', 540, 500, 80, { face: 'marker', col: SK.graph, key: 'wp9', reveal: ev(when('willpower', 3) - 0.3, 0.3) });
  if (TT >= when('trust')) {
    gline([[300, 475], [780, 485]], { key: 'wx', w: 8, col: SK.red, second: false, part: ev(when('trust'), 0.2) });
    handLetter('TRUST', 540, 650, 110, { face: 'marker', col: SK.ink, key: 'tr', reveal: ev(when('trust'), 0.3) });
    const [a, b] = [400, 680]; highlight(a, b, 620, 70, ev(when('trust') + 0.3, 0.3));
  }
  const ty = 1080;
  kidAt(300, ty, 66, { key: 'hero', mood: TT >= when('second') ? 'puzzled' : 'calm', look: [1, 0.4], arms: [-1.2, -1.2] });
  table(110, 900, ty, 'tb9');
  plate(640, ty - 6, 160, 'pl9');
  mallow(570, ty - 10, 90, 'm9a');
  if (TT >= when('second')) { mallow(710, ty - 10, 90, 'm9b', ev(when('second'), 0.3), true); handLetter('?', 710, 950, 90, { face: 'marker', col: SK.red, key: 'q9', reveal: ev(when('second') + 0.3, 0.2) }); }
  pageTag('your turn');
  say([[S[8], ['maybe it was never', 'just willpower.'], [[1, 'willpower.']]], [when('maybe', 2), ['maybe it was trust.'], [[0, 'trust.']]],
       [when('would'), ['would YOU wait, if', 'it might not come?'], [[0, 'YOU']]]], S[8]);
},
];
