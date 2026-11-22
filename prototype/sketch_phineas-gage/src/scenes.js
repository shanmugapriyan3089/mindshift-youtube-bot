// =====================================================================
//  SCENES — Phineas Gage (1848), sketchbook. Every time comes from the narration: when('word', n).
//  Shared helpers (person, say, speech, iconPeople, stamp, ...) live in ../sketch_kit/people.js.
//  Cast: YOU (Phineas, terracotta t-shirt) · the crew (khaki/blue) · the doctor (lab coat) · friends (green/blue).
// =====================================================================

const GY = 1235;
const HITS = [when('explodes'), when('survive'), when('longer'), when('monster')];
const ROD = '#5a5048';

// railroad track along the ground
function track(x0, x1, key, part = 1) {
  for (let i = 0; i <= 8; i++) { const x = lerp(x0, x1, i / 8); gline([[x - 10, GY - 6], [x + 14, GY + 30]], { key: key + 'tie' + i, w: 7, col: '#a0703c', second: false, part }); }
  gline([[x0, GY + 2], [x1, GY - 2]], { key: key + 'r1', w: 5, part });
  gline([[x0 + 20, GY + 22], [x1 + 20, GY + 18]], { key: key + 'r2', w: 5, part });
}
// the iron rod as a thick dark bar from p to q
function rod(p, q, key, part = 1) {
  gline([p, q], { key: key, w: 14, col: ROD, second: false, part });
  gline([p, q], { key: key + 'hl', w: 3, col: '#9a948b', second: false, part, a: 0.8 });
}
// a doodle brain: bumpy outline, a fold line; `front` 0..1 shades the front (left) part red
function brain(cx, cy, rx, ry, key, part = 1, front = 0) {
  const P = []; for (let i = 0; i <= 48; i++) { const a = i / 48 * TAU, k = 1 + 0.07 * Math.sin(a * 9); P.push([cx + Math.cos(a) * rx * k, cy + Math.sin(a) * ry * k * (Math.sin(a) > 0 ? 0.8 : 1)]); }
  gfill(P, '#f3c6c0', { key: key + 'f', off: [5, 5], a: clamp(part) });
  if (front > 0) { ctx.save(); gclip(P); scribbleFill([[cx - rx * 1.1, cy - ry * 1.1], [cx - rx * 0.25, cy - ry * 1.1], [cx - rx * 0.35, cy + ry], [cx - rx * 1.1, cy + ry]], SK.red, { key: key + 'fr', gap: 12, w: 4, part: front, base: 0.25 }); ctx.restore(); }
  gline(P, { closed: true, key: key + 'o', w: 5, part });
  gline([[cx - rx * 0.6, cy - ry * 0.1], [cx - rx * 0.2, cy - ry * 0.3], [cx + rx * 0.2, cy], [cx + rx * 0.6, cy - ry * 0.2]], { key: key + 'fold', w: 4, second: false, part });
  gline([[cx - rx * 0.1, cy - ry * 0.8], [cx, cy - ry * 0.45], [cx - rx * 0.15, cy - ry * 0.25]], { key: key + 'f2', w: 3, second: false, part });
}

const SCENES = [
// ---- 1. a rod is coming ------------------------------------------------------------------------
() => {
  sketchPage({ grid: 'dots' });
  track(110, 920, 'tk1', ev(when('railroad') - 0.3, 0.6));
  const hy = onGround(GY, 74), hit = TT >= when('head');
  person(420, hy, 74, { key: 'hero', mood: TT >= when('survive') ? 'wow' : hit ? 'scared' : 'calm', look: hit ? [1, -0.6] : [0, 0], arms: [-1.2, -1.2] });
  // "an iron rod will shoot straight through your head": the rod and its dotted path
  if (TT >= when('iron')) {
    rod([700, 1180], [790, 620], 'r1', ev(when('iron'), 0.4));
    handLetter('iron rod', 820, 560, 44, { col: SK.ink, key: 'irl', reveal: ev(when('iron') + 0.2, 0.3) });
  }
  if (hit) { ctx.save(); ctx.setLineDash([14, 12]); gline([[380, hy + 60], [445, hy - 140], [470, hy - 230]], { key: 'path1', w: 5, col: SK.red, second: false, part: ev(when('head'), 0.4) }); ctx.restore(); }
  if (TT >= when('survive')) { handLetter('you survive', 420, 520, 72, { face: 'marker', col: SK.green, key: 'srv', reveal: ev(when('survive'), 0.4) }); }
  pageTag('vermont');
  say([[S[0], ['a railroad foreman', 'in Vermont.'], [[0, 'foreman']]], [when('in', 2), ['an iron rod will', 'pierce your head.'], [[1, 'your head.']]],
       [when('and', 1), ["and you'll survive."], [[0, 'survive.']]]], S[0]);
},
// ---- 2. 1848: the job ---------------------------------------------------------------------------
() => {
  sketchPage({ grid: 'ruled' }); ground('g2', GY);
  // "blasts rock": a cliff on the right, two crewmen on top
  const rk = ev(when('rock') - 0.3, 0.5), RK = [[600, GY], [640, 900], [700, 780], [800, 740], [900, 770], [930, GY]];
  gfill(RK, '#d6cfc2', { key: 'rkf', off: [5, 5], a: clamp(rk) });
  ctx.save(); gclip(RK); ghatch(600, 740, 930, GY, { ang: -0.9, gap: 22, col: SK.graph, w: 1.8, a: 0.35 * clamp(rk), key: 'rkh' }); ctx.restore();
  gline(RK, { key: 'rk', w: 5, part: rk });
  if (TT >= when('crew')) [[720, '#c9b27c', 0], [840, '#8fa7c2', 1]].forEach(([x, c, i]) => { if (TT >= when('crew') + i * 0.15) {
    const top = i ? 752 : 770; person(x, onGround(top, 30), 30, { key: 'crew' + i, shirt: c, hair: 'short', hairCol: '#3b3b3b', mood: 'calm', look: [-1, 0], arms: [-1.2, 0.7] }); } });
  // "pack explosive powder": a keg
  if (TT >= when('powder') - 0.2) {
    const kp = ev(when('powder') - 0.2, 0.4), KG = sketchBox(120, 1080, 130, 155, 20, 0.02);
    gfill(KG, '#b98a5a', { key: 'kgf', off: [4, 4], a: clamp(kp) }); gline(KG, { closed: true, key: 'kg', w: 5, part: kp });
    for (const y of [1115, 1200]) gline([[120, y], [250, y]], { key: 'kgb' + y, w: 3, second: false, part: kp });
    handLetter('POWDER', 185, 1060, 40, { face: 'marker', col: SK.red, key: 'pw', reveal: ev(when('powder'), 0.3) });
  }
  // you, tamping with the iron rod into a hole
  const r = 60, hy = onGround(GY, r), tamp = TT >= when('hole') ? 18 * Math.abs(Math.sin(TT * 5)) : 0;
  person(430, hy, r, { key: 'hero', mood: 'calm', look: [1, 0.8], arms: [-1.2, 0.9] });
  gline([[505, GY], [505, GY + 46], [537, GY + 46], [537, GY]], { key: 'hole', w: 4, second: false, part: ev(when('hole') - 0.3, 0.3) });
  if (TT >= when('iron', 2) - 0.6 || TT >= when('job')) rod([521, hy - 110 + tamp], [521, GY + 30 + tamp], 'r2', ev(when('job'), 0.4));
  if (TT >= when('job')) handLetter('YOUR JOB', 400, 520, 70, { face: 'marker', col: SK.ink, key: 'job', reveal: ev(when('job'), 0.3) });
  pageTag('1848');
  say([[S[1], ['1848. your crew', 'blasts rock.'], [[1, 'rock.']]], [when('job'), ['pack powder into', 'a hole with a rod.'], [[0, 'powder']]]], S[1]);
},
// ---- 3. the explosion -----------------------------------------------------------------------------
() => {
  sketchPage({ grid: 'dots' }); ground('g3', GY);
  const r = 100, hx = 540, hy = onGround(GY, r), ex = TT >= when('explodes');
  person(hx, hy, r, { key: 'hero3', mood: ex ? 'scream' : 'calm', look: [0, 0.6], arms: ex ? [0.6, 0.6] : [-1.2, -1.2], shake: ex ? 4 : 0 });
  // "a spark" at the hole, then the blast
  if (TT >= when('spark') && !ex) sparkle(640, GY - 10, 50, ((TT - when('spark')) * 2) % 1, 'spk3', SK.red);
  if (ex) {
    const k = ev(when('explodes'), 0.3), BL = [];
    for (let i = 0; i <= 16; i++) { const a = Math.PI + i / 16 * Math.PI, rr = (i % 2 ? 60 : 120) * k; BL.push([660 + Math.cos(a) * rr * 1.6, GY + Math.sin(a) * rr]); }
    if (TT < when('rod', 3) + 1) { gfill(BL, SK.hilite, { key: 'blf', off: [0, 0], a: 0.9 }); gline(BL, { key: 'bl', w: 4, col: SK.red, second: false }); }
  }
  // the rod: in through the left cheek, out the top of the skull, and gone upward
  const P0 = [hx - 40, hy + 55], dir = [0.33, -1], L = 520;
  if (TT >= when('rod', 3)) {
    ctx.save(); ctx.setLineDash([14, 12]); gline([[P0[0] - dir[0] * 300, P0[1] - dir[1] * 300 * 0.4], [P0[0] + dir[0] * 330, P0[1] + dir[1] * 330]], { key: 'path3', w: 4, col: SK.red, second: false, part: ev(when('rod', 3), 0.4) }); ctx.restore();
    const fly = EZ.io(ev(when('flies'), 0.8)), off = lerp(-60, 330, fly);
    const a = [P0[0] + dir[0] * off, P0[1] + dir[1] * off], b = [a[0] + dir[0] * L * 0.45, a[1] + dir[1] * L * 0.45];
    rod([a[0] - dir[0] * L * 0.55, a[1] - dir[1] * L * 0.55], b, 'r3', ev(when('rod', 3), 0.3));
  }
  if (TT >= when('cheek')) handLetter('cheek', 290, hy + 80, 46, { col: SK.red, key: 'chk3', reveal: ev(when('cheek'), 0.3) });
  if (TT >= when('skull')) handLetter('skull', 790, hy - 110, 46, { col: SK.red, key: 'skl3', reveal: ev(when('skull'), 0.3) });
  if (TT >= when('long')) handLetter('over 1 m long', 300, 470, 46, { face: 'marker', col: SK.ink, key: 'm3', reveal: ev(when('long'), 0.3) });
  pageTag('a spark');
  say([[S[2], ['a spark. the powder', 'explodes.'], [[1, 'explodes.']]], [when('rod', 3), ['the rod flies up', 'through your skull.'], [[1, 'skull.']]]], S[2]);
},
// ---- 4. alive, and talking -----------------------------------------------------------------------
() => {
  sketchPage({ grid: 'dots' }); ground('g4', GY);
  // "it lands far behind you": the rod on the ground with a puff of dust
  rod([620, GY - 8], [920, GY - 18], 'r4', ev(when('lands') - 0.2, 0.3));
  if (TT < when('lands') + 1) for (let i = 0; i < 3; i++) graphiteScribble(660 + i * 110, GY - 30, 50, 20, 'dust' + i, { n: 18 });
  // sitting up in a cart
  const hy = onGround(GY, 56);
  person(290, hy, 56, { key: 'hero', mood: TT >= when('tell') ? 'happy' : 'calm', look: [1, 0], arms: [-1.2, -1.2] });
  gline(loopPts(290, hy - 40, 62, 20, 0.05), { key: 'band', w: 8, col: '#fffdf6', second: false, a: clamp(ev(when('minutes'), 0.3)) });
  const CT = sketchBox(110, 1060, 360, 120, 6, 0.02);
  gfill(CT, '#ecc995', { key: 'ctf', off: [4, 4], a: clamp(ev(when('minutes'), 0.3)) });
  gline(CT, { closed: true, key: 'ct', w: 5, part: ev(when('minutes'), 0.4) });
  for (const wx of [180, 400]) { const R = loopPts(wx, 1190, 38, 38, 0.06); gfill(R, '#b98a5a', { key: 'cw' + wx, off: [0, 0], a: clamp(ev(when('minutes'), 0.3)) }); gline(R, { key: 'cwo' + wx, w: 4, part: ev(when('minutes'), 0.4) }); }
  if (TT >= when('minutes') && TT < when('tell')) handLetter('minutes later...', 290, 560, 52, { col: SK.graph, key: 'ml', reveal: ev(when('minutes'), 0.4) });
  // the doctor arrives
  if (TT >= when('doctor')) person(760, onGround(GY, 58), 58, { key: 'doc', outfit: 'coat', hair: 'short', hairCol: '#555', glasses: true, mood: 'wow', look: [-1, 0], arms: [-1.2, -1.2] });
  speech(110, 420, 560, 200, ['"here is business', 'enough for you!"'], [300, hy - 80], ev(when('business'), 0.5), 'b4', { size: 46 });
  pageTag('alive');
  say([[S[3], ['it lands far', 'behind you.'], [[1, 'behind you.']]], [when('minutes'), ['minutes later,', "you're talking."], [[1, 'talking.']]],
       [when('tell'), ['you joke with', 'the doctor.'], [[1, 'doctor.']]]], S[3]);
},
// ---- 5. no longer Gage --------------------------------------------------------------------------
() => {
  sketchPage({ grid: 'ruled' }); ground('g5', GY);
  const hy = onGround(GY, 66);
  person(240, hy, 66, { key: 'hero', mood: TT >= when('strange') ? 'puzzled' : 'happy', look: [1, 0], arms: [-1.2, -1.2] });
  gline(loopPts(240, hy - 44, 72, 22, 0.05), { key: 'band5', w: 9, col: '#fffdf6', second: false });
  if (TT < when('writes')) checkMark(240, 560, 1.2, ev(when('heals'), 0.4));
  // "your doctor later writes": the case notes
  if (TT >= when('writes') - 0.2) {
    const nt = ev(when('writes') - 0.2, 0.4), NB = sketchBox(440, 420, 480, 380, 8, 0.03);
    gfill(NB, '#fffdf6', { key: 'nbf', off: [5, 5], a: clamp(nt) }); gline(NB, { closed: true, key: 'nb', w: 5, part: nt });
    handLetter('case notes, 1868', 680, 480, 36, { col: SK.graph, key: 'cn', reveal: ev(when('writes'), 0.4) });
    for (let i = 0; i < 3; i++) gpencil([[480, 540 + i * 40], [i === 2 ? 760 : 880, 540 + i * 40]], { key: 'ln' + i, w: 3, a: 0.6, part: ev(when('writes') + 0.3 + i * 0.15, 0.3) });
    if (TT >= when('longer')) { handLetter('"no longer Gage"', 680, 720, 52, { face: 'marker', col: SK.red, key: 'nlg', reveal: ev(when('no') - 0.1, 0.5) }); }
  }
  // "your friends say something strange"
  if (TT >= when('friends')) [[620, '#7fa77a', 0], [820, '#8fa7c2', 1]].forEach(([x, c, i]) => {
    person(x, onGround(GY, 46), 46, { key: 'fr' + i, shirt: c, hair: i ? 'short' : 'mop', hairCol: i ? '#222' : '#7a5a3c', mood: TT >= when('strange') ? 'puzzled' : 'calm', look: [-1, 0], arms: [-1.2, -1.2] });
    if (TT >= when('strange')) handLetter('?', x + 10, 955, 60, { face: 'marker', col: SK.graph, key: 'fq' + i, reveal: ev(when('strange') + i * 0.15, 0.2) });
  });
  pageTag('changed?');
  say([[S[4], ['your body heals.'], [[0, 'heals.']]], [when('but'), ['but your friends say', 'something strange:'], [[1, 'strange:']]],
       [when('no') - 0.3, ['"no longer Gage."'], [[0, 'no longer']]]], S[4]);
},
// ---- 6. about 13 pounds, almost 12 more years ----------------------------------------------------
() => {
  sketchPage({ grid: 'dots' });
  handLetter('about 13 lb of iron', 540, 520, 76, { face: 'marker', col: SK.ink, key: 'lb', reveal: ev(S[5] + 0.3, 0.5) });
  brain(540, 780, 230, 150, 'br', ev(when('front') - 0.4, 0.5), ev(when('front'), 0.5));
  if (TT >= when('front')) { arrowPencil([[180, 640], [330, 740]], ev(when('front') + 0.3, 0.3), { key: 'far' }); handLetter('front', 180, 620, 46, { col: SK.red, key: 'frl', reveal: ev(when('front'), 0.3) }); }
  // "you lived for almost twelve more years": a timeline
  if (TT >= when('lived') - 0.2) {
    const tl = ev(when('lived') - 0.2, 0.6);
    gline([[180, 1040], [lerp(180, 900, tl), 1040]], { key: 'tl', w: 6, second: false });
    for (const [x, s, k] of [[180, '1848', 0], [900, '1860', 1]]) { gline([[x, 1015], [x, 1065]], { key: 'tt' + k, w: 5, second: false, part: ev(when('lived') + k * 0.5, 0.2) }); handLetter(s, x, 1120, 44, { col: SK.ink, key: 'ty' + k, reveal: ev(when('lived') + k * 0.5, 0.3) }); }
    handLetter('almost 12 more years', 540, 1220, 56, { face: 'marker', col: SK.green, key: 'a12', reveal: ev(when('almost'), 0.5) });
  }
  pageTag('the numbers');
  say([[S[5], ['13 pounds of iron', 'through your brain.'], [[0, '13 pounds']]], [when('and', 3), ['you lived almost', '12 more years.'], [[1, '12 more years.']]]], S[5]);
},
// ---- 7. the monster myth -------------------------------------------------------------------------
() => {
  sketchPage({ grid: 'dots' }); ground('g7', GY);
  // an open textbook
  const t0 = when('textbooks') - 0.3, LP = sketchBox(150, 420, 370, 300, 8, 0.03), RP = sketchBox(520, 420, 370, 300, 8, 0.03);
  for (const [P, k] of [[LP, 'lp'], [RP, 'rp']]) { gfill(P, '#fffdf6', { key: k + 'f', off: [4, 4], a: clamp(ev(t0, 0.3)) }); gline(P, { closed: true, key: k, w: 5, part: ev(t0, 0.4) }); }
  handLetter('TEXTBOOK', 335, 490, 44, { face: 'marker', col: SK.graph, key: 'tb', reveal: ev(when('textbooks'), 0.3) });
  for (let i = 0; i < 3; i++) gpencil([[190, 540 + i * 50], [480, 540 + i * 50]], { key: 'tl' + i, w: 3, a: 0.5, part: ev(t0 + 0.3 + i * 0.1, 0.2) });
  if (TT >= when('monster')) handLetter('MONSTER!', 705, 590, 62, { face: 'marker', col: SK.red, key: 'mon', reveal: ev(when('monster'), 0.3) });
  // you, with pencilled-on horns and an angry face that get drawn on by the story
  const mons = TT >= when('monster') && TT < when('added');
  const r = 64, hy = onGround(GY, r);
  person(540, hy, r, { key: 'hero', mood: mons ? 'angry' : 'puzzled', look: [0, -0.5], arms: [-1.2, -1.2] });
  if (TT >= when('monster')) for (const s of [-1, 1]) gpencil([[540 + s * 40, hy - 55], [540 + s * 60, hy - 120], [540 + s * 20, hy - 66]], { key: 'horn' + s, w: 4, a: mons ? 0.9 : 0.25, part: ev(when('monster'), 0.3) });
  if (TT >= when('wild')) for (let i = 0; i < 4; i++) graphiteScribble(180 + (i % 2) * 650, 900 + Math.floor(i / 2) * 140, 70, 40, 'wd' + i, { n: 26 });
  stamp('ADDED LATER', 540, 820, when('added'), -0.06, 'sal');
  pageTag('the myth');
  say([[S[6], ['textbooks turn you', 'into a monster.'], [[1, 'monster.']]], [when('many'), ['most wild details', 'came much later.'], [[1, 'later.']]]], S[6]);
},
// ---- 8. driving a stagecoach in Chile --------------------------------------------------------------
() => {
  sketchPage({ grid: 'dots' }); ground('g8', GY);
  // "mountain roads"
  if (TT >= when('mountain') - 0.2) gline([[110, 760], [250, 590], [350, 690], [480, 540], [620, 700], [740, 600], [920, 760]], { key: 'mtn', w: 4, part: ev(when('mountain') - 0.2, 0.6) });
  // you on the driver's seat
  const bob = 4 * Math.sin(TT * 7);
  person(470, 760 + bob, 40, { key: 'hero', mood: 'happy', look: [1, 0], arms: [-1.2, 0.2] });
  // the coach
  const cp = ev(S[7] + 0.3, 0.5), CO = sketchBox(130, 880 + bob, 380, 230, 14, 0.03);
  gfill(CO, '#b98a5a', { key: 'cof', off: [5, 5], a: clamp(cp) }); gline(CO, { closed: true, key: 'co', w: 5, part: cp });
  drawPencil(closeP(CO), S[7] + 0.3, 0.5);
  const WN = sketchBox(190, 920 + bob, 200, 100, 8, 0.02);
  gfill(WN, '#fffdf6', { key: 'cwf', off: [0, 0], a: clamp(cp) }); gline(WN, { closed: true, key: 'cw', w: 4, part: cp });
  if (TT >= when('passengers')) [[245, '#7fa77a'], [335, '#8fa7c2']].forEach(([x, c], i) => person(x, 960 + bob, 24, { key: 'ps' + i, shirt: c, hair: i ? 'short' : 'mop', mood: 'happy', look: [0, 0], arms: [-1.2, -1.2] }));
  if (TT >= when('passengers')) gfill([[192, 1000 + bob], [388, 1000 + bob], [388, 1018 + bob], [192, 1018 + bob]], '#b98a5a', { key: 'cwc', off: [0, 0] });
  for (const wx of [200, 440]) { const R = loopPts(wx, 1170, 56, 56, 0.06), a = TT * 4; gline(R, { key: 'whl' + wx, w: 5, part: cp }); for (let k = 0; k < 4; k++) gline([[wx, 1170], [wx + Math.cos(a + k * Math.PI / 2) * 50, 1170 + Math.sin(a + k * Math.PI / 2) * 50]], { key: 'sp' + wx + k, w: 3, second: false, a: clamp(cp) }); }
  // "horses"
  if (TT >= when('horses') - 0.2) {
    const hp = ev(when('horses') - 0.2, 0.5), gal = Math.sin(TT * 9) * 14;
    const BD = loopPts(740, 1020, 120, 52, 0.05);
    gfill(BD, '#a0703c', { key: 'hbf', off: [4, 4], a: clamp(hp) }); gline(BD, { key: 'hb', w: 5, part: hp });
    gline([[830, 990], [880, 900], [930, 910], [915, 950], [870, 960], [850, 1010]], { key: 'hn', w: 5, part: hp });
    for (const [lx, s] of [[660, 1], [700, -1], [790, -1], [830, 1]]) gline([[lx, 1060], [lx + s * gal, GY - 4]], { key: 'hl' + lx, w: 5, second: false, part: hp });
    gline([[640, 1000], [600, 1060]], { key: 'htl', w: 5, second: false, part: hp });
    gpencil([[500, 820 + bob], [880, 920]], { key: 'reins', w: 3, a: 0.9, part: hp });
  }
  if (TT >= when('planning')) { handLetter('planning + self-control', 540, 480, 52, { face: 'marker', col: SK.green, key: 'plan', reveal: ev(when('planning'), 0.5) }); }
  pageTag('chile');
  say([[S[7], ['you spent years', 'in Chile...'], [[1, 'Chile...']]], [when('driving'), ['...driving a', 'stagecoach.'], [[1, 'stagecoach.']]],
       [when('takes'), ['that takes planning.'], [[0, 'planning.']]]], S[7]);
},
// ---- 9. who is the real you? -----------------------------------------------------------------------
() => {
  sketchPage({ grid: 'dots' }); ground('g9', GY);
  const real = TT >= when('real') - 0.4 || TT >= when('if');
  person(540, onGround(GY, 80), 80, { key: 'hero', mood: real ? 'puzzled' : 'calm', look: [0, -0.6], arms: [-1.2, -1.2] });
  if (!real) {
    speech(240, 400, 600, 340, [], [540, 860], ev(S[8] + 0.2, 0.3), 'th9');
    if (TT >= S[8] + 0.3) brain(540, 560, 160, 100, 'br9', ev(S[8] + 0.3, 0.4), 0.6);
    if (TT >= when('adapted')) arrowPencil(arcPts(540, 570, 230, -2.6, 2.0, 18).map(([x, y]) => [x, y * 0.6 + 230]), ev(when('adapted'), 0.6), { key: 'adp', col: SK.green, w: 5 });
  } else speech(220, 420, 640, 260, ['who is', 'the real you?'], [540, 860], ev(when('if'), 0.6), 'q9', { face: 'marker', size: 70 });
  pageTag('your turn');
  say([[S[8], ['your brain changed', 'you, then adapted.'], [[1, 'adapted.']]], [when('if'), ['so who is', 'the real YOU?'], [[1, 'YOU?']]]], S[8]);
},
];
