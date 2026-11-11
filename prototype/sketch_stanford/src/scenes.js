// =====================================================================
//  SCENES — Prisoner 8612 (sketchbook). World 1080x1920; TT on 2s; times are absolute (S[], word times).
//  Shared helpers (person, say, stamp, cellBars, ...) live in ../sketch_kit/people.js.
// =====================================================================

// ---- 1. the ad (0 – 9.64) -------------------------------------------------------------------
function sceneAd() {
  sketchPage({ grid: 'dots' });
  const t = S[0];
  ground('g1', 1225);
  const wow = TT >= 4.96;
  person(270, onGround(1225, 72), 72, { key: 'hero', mood: wow ? 'wow' : 'calm', look: [1, -0.4], arms: wow ? [0.9, 0.2] : [0.2, 0.2] });
  // "newspaper ad" (3.42)
  const NP = sketchBox(470, 560, 470, 520, 10, 0.04);
  gfill(NP, '#fffaf0', { key: 'npf', a: clamp(ev(3.2, 0.3)) });
  gpencil(NP, { closed: true, key: 'npc', w: 2.6, a: 0.7, part: ev(2.9, 0.6) });
  gline(NP, { closed: true, key: 'np', w: 5, part: ev(3.4, 0.4) });
  drawPencil(closeP(NP), 2.9, 0.6);
  for (let i = 0; i < 4; i++) gpencil([[500, 610 + i * 26], [500 + [400, 360, 380, 240][i], 610 + i * 26]], { key: 'npl' + i, w: 2.4, a: 0.6, part: ev(3.6 + i * 0.08, 0.15) });
  gline(sketchBox(510, 730, 390, 320, 8, 0.03), { key: 'adbox', w: 4, part: ev(3.8, 0.3) });
  handLetter('WANTED', 705, 790, 44, { face: 'marker', col: SK.ink, key: 'adw', reveal: ev(3.9, 0.4) });
  // "$15 a day" (4.96)
  handLetter('$15 a day', 705, 870, 62, { face: 'marker', col: SK.ink, key: 'ad15', reveal: ev(4.96, 0.5) });
  gline(loopPts(705, 850, 175, 52, 0.12), { key: 'adloop', w: 5, col: SK.red, part: ev(5.6, 0.35) });
  // "fake prison" (6.98): a little barred window doodled in the ad
  gline(sketchBox(560, 905, 110, 110, 6, 0.03), { key: 'pw', w: 3.5, part: ev(6.8, 0.25) });
  for (let i = 0; i < 3; i++) gline([[587 + i * 28, 908], [587 + i * 28, 1012]], { key: 'pb' + i, w: 3.5, second: false, part: ev(7.0 + i * 0.06, 0.12) });
  // "two weeks" (7.92)
  handLetter('2 weeks', 810, 975, 46, { face: 'marker', col: SK.ink, key: 'ad2w', reveal: ev(7.92, 0.4) });
  if (wow) handLetter('!', 380, 830, 90, { face: 'marker', col: SK.ink, key: 'bang1', reveal: ev(4.96, 0.1) });
  pageTag('august 1971');
  say([[0, ['august, 1971.']], [2.9, ['you answer', 'a newspaper ad.'], [[1, 'ad.']]],
       [4.96, ['$15 a day to live', 'in a fake prison'], [[1, 'prison']]], [7.6, ['for two weeks.'], [[0, 'two weeks.']]]], t);
}

// ---- 2. the arrest (9.64 – 15.79) -----------------------------------------------------------
function sceneArrest() {
  sketchPage({ grid: 'dots' });
  const t = S[1];
  ground('g2', 1225);
  // "Sunday morning" (10.1): a house and a sun
  const H = [[100, 1225], [100, 1000], [230, 900], [360, 1000], [360, 1225]];
  gfill(H, '#fffaf0', { key: 'hsf', a: clamp(ev(10.2, 0.3)) });
  gline(H, { key: 'hs', w: 5, part: ev(10.0, 0.6) });
  drawPencil(H, 10.0, 0.6);
  gline(sketchBox(200, 1120, 60, 105, 4), { key: 'hd', w: 4, part: ev(10.5, 0.2) });
  gline(sketchBox(150, 1020, 150, 70, 4), { key: 'hwin', w: 3.5, part: ev(10.6, 0.2) });
  const SUNP = loopPts(880, 470, 55, 55, 0.08);
  scribbleFill(SUNP, SK.hilite, { key: 'sunf', gap: 10, w: 4, part: ev(10.2, 0.4) });
  gline(SUNP, { key: 'sun', w: 4, part: ev(10.1, 0.3) });
  // "a real police car pulls up" (11.04–12.2): it drives in from the right
  const dx = lerp(800, 0, EZ.io(ev(11.0, 1.1)));
  ctx.save(); ctx.translate(dx, 0);
  const body = [[420, 1185], [420, 1070], [520, 1062], [580, 990], [800, 990], [860, 1062], [960, 1075], [960, 1185]];
  gfill(body, '#fffaf0', { key: 'carf', off: [0, 0] });
  gline(body, { closed: true, key: 'car', w: 6 });
  for (const [i, x] of [[0, 520], [1, 860]]) { const wp = loopPts(x, 1190, 50, 50, 0.08); gfill(wp, SK.ink, { key: 'whf' + i, a: 0.9, off: [0, 0] }); gline(wp, { key: 'wh' + i, w: 5 }); }
  handLetter('POLICE', 690, 1150, 50, { face: 'marker', col: SK.ink, key: 'pol' });
  const siren = loopPts(690, 968, 30, 20, 0.1);
  gline(siren, { key: 'sir', w: 4 });
  if (TT > 11.4 && (B % 4) < 2) scribbleFill(siren, SK.red, { key: 'sirf', gap: 8, w: 4 });
  ctx.restore();
  // "you're arrested" (13.08)
  const arr = TT >= 13.08;
  person(385, 1225 - 3.6 * 44, 44, { key: 'hero', mood: arr ? 'scared' : 'calm', look: [0.6, 0], arms: arr ? [1.2, 1.2] : [-1.2, -1.2] });
  if (arr) handLetter('!', 470, 960, 90, { face: 'marker', col: SK.ink, key: 'b2', reveal: ev(13.08, 0.1) });
  // "in front of your neighbours" (14.16): heads pop up at the window
  for (let i = 0; i < 2; i++) { const k = ev(14.2 + i * 0.15, 0.2); if (k > 0) { gline(loopPts(195 + i * 60, 1060 - 18 * k, 20, 20, 0.08), { key: 'nb' + i, w: 3.5, col: SK.graph }); handLetter('!', 195 + i * 60, 1015 - 18 * k, 34, { col: SK.graph, key: 'nbx' + i }); } }
  pageTag('sunday');
  say([[9.64, ['sunday morning.']], [10.94, ['a real police car', 'pulls up.'], [[0, 'police car']]],
       [12.94, ["you're arrested"], [[0, 'arrested']]], [14.16, ['in front of', 'your neighbours.'], [[1, 'neighbours.']]]], t);
}

// ---- 3. 8612 (15.79 – 27.31) ----------------------------------------------------------------
function sceneNumber() {
  sketchPage({ grid: 'ruled' });
  const t = S[2];
  // "a basement at Stanford" (16.26): pipes and a bare bulb
  gline([[90, 420], [990, 420]], { key: 'pipe1', w: 6, part: ev(16.0, 0.5) });
  gline([[90, 446], [990, 446]], { key: 'pipe2', w: 3, col: SK.graph, part: ev(16.2, 0.5) });
  gline([[540, 446], [540, 520]], { key: 'cord', w: 3, part: ev(16.6, 0.2), second: false });
  const bulb = loopPts(540, 545, 26, 30, 0.08);
  scribbleFill(bulb, SK.hilite, { key: 'blb', gap: 8, w: 3.5, part: ev(16.8, 0.3) });
  gline(bulb, { key: 'bl', w: 4, part: ev(16.7, 0.2) });
  ground('g3', 1235);
  // "they take your clothes" (18.16) -> "smock" (19.68)
  const smock = TT >= 19.5, poof = TT >= 18.9 && TT < 19.6;
  person(540, onGround(1235, 74), 74, { key: 'hero', outfit: smock ? 'smock' : 'tee', mood: TT >= 23.26 ? 'scared' : (TT >= 18.16 ? 'puzzled' : 'calm'),
                         num: smock ? ev(22.22, 0.8) : 0, look: [0, 0.2], arms: [-1.2, -1.2] });
  if (poof) graphiteScribble(540, 1120, 300, 260, 'poof' + (B % 3));
  if (TT >= 18.16 && TT < 19.6) { const k = ev(18.16, 0.8); ctx.save(); ctx.translate(lerp(560, 900, k), lerp(1100, 760, k)); ctx.rotate(k * 2.2);
    const tee = [[-60, -50], [60, -50], [55, 60], [-55, 60]]; gfill(tee, SK.terra, { key: 'teef', off: [0, 0] }); gline(tee, { closed: true, key: 'tee', w: 4 }); ctx.restore(); }
  // "a chain on your ankle" (20.52)
  for (let i = 0; i < 6; i++) gline(loopPts(500 - i * 32, 1240 + (i % 2) * 6, 17, 10, 0.1), { key: 'ch' + i, w: 3.5, col: SK.graph, part: ev(20.52 + i * 0.08, 0.12) });
  const ball = loopPts(290, 1236, 38, 38, 0.08);
  if (TT > 21.0) { gfill(ball, SK.ink, { key: 'ballf', a: 0.85, off: [0, 0] }); gline(ball, { key: 'ball', w: 4 }); }
  // "you're not you anymore" (23.26): bars close in front
  cellBars(330, 750, 640, 1250, 7, 23.3, 0.18, 'bar');
  // "you're 8612" (25.42)
  stamp('8612', 540, 600, 25.42, -0.08, 'st8612');
  pageTag('stanford basement');
  say([[15.79, ['a basement', 'at stanford.'], [[1, 'stanford.']]], [17.56, ['they take', 'your clothes.'], [[1, 'clothes.']]],
       [19.18, ['you get a smock,', 'a chain,'], [[1, 'chain,']]], [21.48, ['and a number.'], [[0, 'number.']]],
       [23.26, ["you're not you", 'anymore.']], [25.18, ["you're 8612."], [[0, '8612.']]]], t);
}

// ---- 4. the guards (27.31 – 35.91) ---------------------------------------------------------
function sceneGuard() {
  sketchPage({ grid: 'dots' });
  const t = S[3];
  ground('g4', 1235);
  // two equal students side by side; then the guard changes: khaki (31.02), sunglasses (32.5), baton (34.5)
  const khaki = clamp(ev(30.9, 0.4)), shades = clamp(ev(32.4, 0.3)), baton = ev(34.4, 0.4);
  const gx = 720, gy = onGround(1235, 82);
  person(gx, gy, 82, { key: 'guard', hair: khaki > 0.5 ? 'short' : 'mop', hairCol: '#3e3128', shirt: khaki > 0 ? KHAKI : '#8fa7c2',
                       mood: khaki > 0 ? 'angry' : 'calm', shades, baton, look: [-1, 0.2], arms: [-1.2, -1.0] });
  if (khaki > 0 && khaki < 1) graphiteScribble(gx, gy + 130, 180, 160, 'kh' + (B % 2));
  person(330, onGround(1235, 62), 62, { key: 'hero', outfit: 'smock', num: 1, mood: shades > 0 ? 'scared' : 'calm', look: [1, -0.4], arms: [-1.2, -1.2] });
  handLetter('student', 720, 800, 46, { col: SK.graph, key: 'lbl1', reveal: ev(28.28, 0.4) });
  handLetter('student', 330, 880, 40, { col: SK.graph, key: 'lbl2', reveal: ev(29.3, 0.4) });
  if (TT >= 31.0) gline([[620, 788], [820, 780]], { key: 'strike', w: 5, col: SK.red, second: false, part: ev(31.0, 0.25) });
  handLetter('GUARD', 720, 730, 56, { face: 'marker', col: SK.red, key: 'lblg', reveal: ev(31.3, 0.3) });
  pageTag('the guards');
  say([[27.06, ['the guards', 'are students,'], [[1, 'students,']]], [29.24, ['just like you.'], [[0, 'just like you.']]],
       [30.7, ['khaki uniforms.'], [[0, 'khaki']]], [32.26, ['mirrored', 'sunglasses.'], [[1, 'sunglasses.']]], [34.24, ['wooden batons.'], [[0, 'batons.']]]], t);
}

// ---- 5. day 2: the rebellion (35.91 – 41.79) -----------------------------------------------
function sceneRebel() {
  sketchPage({ grid: 'dots' });
  const t = S[4];
  const reb = TT >= 37.34;
  for (let i = 0; i < 3; i++) person(430 + i * 185, onGround(1240, 54), 54, { key: 'pr' + i, outfit: 'smock', mood: reb ? 'angry' : 'calm', arms: reb ? [1.1, 1.1] : [-1.2, -1.2], shake: reb ? 5 : 0, hairCol: ['#5a4232', '#2f2620', '#7a5a3c'][i] });
  if (reb) graphiteScribble(610, 1010, 520, 200, 'chaos' + (B % 3));
  cellBars(330, 900, 760, 1250, 8, 36.1, 0.05, 'bar5');
  // "the guards fight back" (38.56)
  if (TT >= 38.4) person(185, onGround(1240, 52), 52, { key: 'g5', hair: 'short', hairCol: '#3e3128', shirt: KHAKI, mood: 'angry', shades: 1, look: [1, 0], arms: [0.1, -1.1] });
  // "with fire extinguishers" (39.84)
  const ex = sketchBox(90, 1010, 80, 190, 18, 0.02);
  scribbleFill(ex, SK.red, { key: 'exf', gap: 10, w: 4, part: ev(39.84, 0.3) });
  gline(ex, { key: 'ex', w: 5, part: ev(39.7, 0.3) });
  gline([[130, 1010], [130, 975], [240, 930]], { key: 'hose', w: 6, part: ev(39.9, 0.2), second: false });
  const sp = ev(40.2, 1.2);
  for (let i = 0; i < 9; i++) { const k = clamp(sp * 1.4 - i * 0.05), r = 30 + 70 * k; if (k > 0) gpencil(loopPts(260 + i * 75, 900 + 40 * Math.sin(i * 1.7), r, r * 0.8, 0.1), { key: 'cl' + i + (B % 2), w: 3, a: 0.75 }); }
  ground('g5', 1240);
  pageTag('day 2');
  say([[35.91, ['day two.']], [36.9, ['the prisoners', 'rebel.'], [[1, 'rebel.']]], [38.4, ['the guards', 'fight back'], [[1, 'fight back']]],
       [39.5, ['with fire', 'extinguishers.'], [[0, 'fire']]]], t);
}

// ---- 6. hour 36 (41.79 – 48.14) -------------------------------------------------------------
function sceneOut() {
  sketchPage({ grid: 'ruled' });
  const t = S[5];
  ctx.save(); gclip(sketchBox(140, 520, 800, 740, 10)); ghatch(140, 520, 940, 1260, { ang: -0.7, gap: 10, col: SK.graph, w: 2, a: 0.4, key: 'cellh' }); ctx.restore();
  gline(sketchBox(140, 520, 800, 740, 10, 0.03), { key: 'cell', w: 6 });
  // "36 hours" (42.06): tally marks on the wall
  for (let i = 0; i < 6; i++) gline([[190 + i * 18, 580], [190 + i * 18, 640]], { key: 'tally' + i, w: 4, second: false, part: ev(42.1 + i * 0.1, 0.1) });
  gline([[180, 625], [310, 590]], { key: 'tallyx', w: 4, second: false, part: ev(42.8, 0.1) });
  handLetter('36 HOURS', 540, 470, 64, { face: 'marker', col: SK.ink, key: 'h36', reveal: ev(42.06, 0.5) });
  // the door opens at "let you go" (46.76)
  const open = EZ.io(ev(46.76, 0.6));
  const door = [[760, 640], [760 + 140 * (1 - open), 640 + 30 * open], [760 + 140 * (1 - open), 1230 - 30 * open], [760, 1230]];
  if (open > 0) scribbleFill(sketchBox(760, 640, 140, 590, 4), SK.hilite, { key: 'light', gap: 10, w: 4, part: open });
  gfill(door, '#e6dcc2', { key: 'doorf', a: 1, off: [0, 0] });
  gline(door, { closed: true, key: 'door', w: 5 });
  // "you start screaming" (44.0)
  const scream = TT >= 44.0 && TT < 46.76;
  person(420, onGround(1255, 66), 66, { key: 'hero', outfit: 'smock', num: 1, mood: TT >= 46.76 ? 'wow' : (scream ? 'scream' : 'scared'),
                         shake: scream ? 7 : 0, look: open > 0 ? [1, 0] : [0, 0.3], arms: scream ? [1.3, 1.3] : [-1.3, -1.3] });
  if (scream) for (let i = 0; i < 3; i++) gline([[330 - i * 26, 950 - i * 30], [290 - i * 30, 930 - i * 34]], { key: 'scr' + i, w: 4, second: false });
  handLetter('LET ME OUT', 470, 760, 70, { face: 'marker', col: SK.ink, key: 'lmo', reveal: ev(45.0, 0.6), rot: -0.05, jit: 2 + (B % 2) });
  pageTag('hour 36');
  say([[41.79, ['36 hours in,']], [43.54, ['you start', 'screaming'], [[1, 'screaming']]], [44.84, ['you want out.'], [[0, 'out.']]],
       [46.12, ['and they', 'let you go.'], [[1, 'go.']]]], t);
}

// ---- 7. day 6: shut down (48.14 – 54.34) ----------------------------------------------------
function sceneShut() {
  sketchPage({ grid: 'dots' });
  const t = S[6];
  // "supposed to last two weeks" (49.68–50.32): 14 days drawn
  for (let i = 0; i < 14; i++) {
    const r = Math.floor(i / 7), c = i % 7, x = 150 + c * 112, y = 600 + r * 140;
    gline(sketchBox(x, y, 96, 120, 6, 0.04), { key: 'd' + i, w: 3.5, part: ev(49.3 + i * 0.07, 0.15) });
    handLetter(String(i + 1), x + 48, y + 46, 34, { col: SK.graph, key: 'dn' + i, reveal: ev(49.5 + i * 0.06, 0.15) });
    if (i < 6) { const k = ev(50.5 + i * 0.12, 0.1);
      gline([[x + 14, y + 20], [x + 82, y + 104]], { key: 'x1' + i, w: 5, part: k, second: false });
      gline([[x + 82, y + 20], [x + 14, y + 104]], { key: 'x2' + i, w: 5, part: seg(k, 0.5, 1) * 2, second: false }); }
  }
  handLetter('2 WEEKS', 540, 540, 54, { face: 'marker', col: SK.graph, key: 'cal', reveal: ev(49.9, 0.4) });
  // "shut down" (51.56) ... "after six days" (52.66)
  stamp('SHUT DOWN', 540, 1050, 51.56, -0.1, 'shut');
  if (TT >= 52.66) gline(loopPts(430, 680, 330, 80, 0.12), { key: 'six', w: 5, col: SK.red, part: ev(52.66, 0.4) });
  pageTag('day 6');
  say([[48.14, ['it was supposed', 'to last two weeks.'], [[1, 'two weeks.']]], [51.22, ['it was shut down', 'after six days.'], [[1, 'six days.']]]], t);
}

// ---- 8. the tapes (54.34 – 67.5) -------------------------------------------------------------
function sceneTapes() {
  sketchPage({ grid: 'dots' });
  const t = S[7];
  if (TT < 59.1) {
    // "for 50 years it was proof that good people turn cruel": a textbook; a smiling student turns into a guard
    const book = sketchBox(260, 520, 560, 420, 12, 0.03);
    gfill(book, '#e9dcc0', { key: 'bkf', a: clamp(ev(54.5, 0.3)) });
    gline(book, { closed: true, key: 'bk', w: 6, part: ev(54.4, 0.5) });
    drawPencil(closeP(book), 54.4, 0.5);
    gline([[540, 520], [540, 940]], { key: 'spine', w: 4, part: ev(54.9, 0.2), second: false });
    handLetter('PSYCH 101', 400, 600, 40, { face: 'marker', col: SK.ink, key: 'p101', reveal: ev(55.0, 0.4) });
    handLetter('50 years', 680, 600, 40, { col: SK.graph, key: 'y50', reveal: ev(54.66, 0.4) });
    const cruel = TT >= 57.5;
    person(400, 690, 46, { key: 'good', mood: cruel ? 'angry' : 'happy', shirt: cruel ? KHAKI : '#8fa7c2', shades: cruel ? 1 : 0, hair: cruel ? 'short' : 'mop', look: [0, 0] });
    if (cruel) { const k = ev(57.5, 0.3); gline([[470, 760], [600, 760]], { key: 'arw', w: 5, part: k, second: false }); gline([[580, 740], [605, 760], [580, 780]], { key: 'arh', w: 5, part: k, second: false }); }
    handLetter(cruel ? 'cruel' : 'good', 680, 790, 60, { face: 'marker', col: cruel ? SK.red : SK.green, key: cruel ? 'cr' : 'gd', reveal: ev(cruel ? 57.5 : 57.0, 0.3) });
  } else {
    // "but recordings later showed" (59.18): the tape recorder
    const box = sketchBox(170, 560, 740, 520, 16, 0.03);
    gfill(box, '#e6dcc2', { key: 'tbf', a: clamp(ev(59.3, 0.3)) });
    gline(box, { closed: true, key: 'tb', w: 6, part: ev(59.18, 0.5) });
    drawPencil(closeP(box), 59.18, 0.5);
    const spin = (TT - 59.1) * 2.2;
    for (const [i, x] of [[0, 360], [1, 720]]) {
      const R = loopPts(x, 760, 120, 120, 0.06);
      gfill(R, '#fffaf0', { key: 'rf' + i, a: clamp(ev(59.6, 0.2)) });
      gline(R, { key: 'r' + i, w: 5, part: ev(59.5 + i * 0.1, 0.3) });
      gline(loopPts(x, 760, 26, 26, 0.05), { key: 'hub' + i, w: 4, part: ev(59.8, 0.2) });
      for (let k = 0; k < 3; k++) { const a = spin + k * TAU / 3; gline([[x + Math.cos(a) * 30, 760 + Math.sin(a) * 30], [x + Math.cos(a) * 100, 760 + Math.sin(a) * 100]], { key: 'sp' + i + k, w: 4, second: false, a: clamp(ev(59.9, 0.2)) }); }
    }
    gline([[360, 880], [540, 960], [720, 880]], { key: 'tape', w: 3, col: SK.graph, part: ev(60.0, 0.3), second: false });
    for (let i = 0; i < 3; i++) { const k = ((TT - 59.1) * 0.8 + i / 3) % 1; gpencil(arcPts(910, 820, 40 + 90 * k, -0.6, 0.6, 10), { key: 'wv' + i, w: 3, a: 0.7 * (1 - k) }); }
    // "the guards were coached" (61.78)
    stamp('COACHED', 540, 1180, 61.78, 0.07, 'coach');
    // "and 8612 said he faked part of his breakdown" (63.88 / 65.4)
    if (TT >= 63.88) {
      person(860, 1060, 40, { key: 'hero', outfit: 'smock', num: 1, mood: TT >= 65.4 ? 'happy' : 'calm', look: [-1, 0], arms: [-1.2, 0.9] });
      if (TT >= 65.4) handLetter('?', 780, 1020, 80, { face: 'marker', col: SK.ink, key: 'q8', reveal: ev(65.4, 0.1) });
    }
  }
  pageTag(TT < 59.1 ? 'for 50 years' : 'the tapes');
  say([[54.34, ['for 50 years,']], [55.98, ['it was proof that', 'good people'], [[1, 'good']]], [57.5, ['turn cruel.'], [[0, 'cruel.']]],
       [59.1, ['but the tapes', 'later showed'], [[0, 'tapes']]], [60.9, ['the guards were', 'coached to be tough.'], [[1, 'coached']]],
       [63.8, ['and 8612 said he', 'faked part of it.'], [[1, 'faked']]]], t);
}

// ---- 9. you (67.5 – 77) ---------------------------------------------------------------------
function sceneYou() {
  sketchPage({ grid: 'dots' });
  const t = S[8];
  ground('g9', 1235);
  if (TT < 71.9) {
    // "what a uniform does to you" (69.26): a khaki shirt on a hanger
    const hk = ev(69.0, 0.6);
    gline([[540, 520], [540, 560]], { key: 'hk', w: 4, part: hk, second: false });
    gline([[420, 610], [540, 560], [660, 610]], { key: 'hg', w: 5, part: hk, second: false });
    const shirtP = [[430, 610], [650, 610], [700, 700], [650, 720], [640, 900], [440, 900], [430, 720], [380, 700]];
    if (hk > 0.5) { gfill(shirtP, KHAKI, { key: 'shf', off: [4, 4] }); gline(shirtP, { closed: true, key: 'sh', w: 5 }); }
  } else {
    // "someone in charge tells you to" (72.4): a huge hand points down at you
    const reach = EZ.io(ev(72.0, 0.9)), dy = lerp(-600, 0, reach);
    const fist = [...arcPts(470, 420 + dy, 110, Math.PI * 0.95, Math.PI * 2.05, 14), [580, 560 + dy], [500, 580 + dy], [400, 540 + dy]];
    const finger = [[500, 560 + dy], [492, 860 + dy], ...arcPts(530, 870 + dy, 38, Math.PI, 0, 8), [568, 860 + dy], [578, 560 + dy]];
    const thumb = [[400, 470 + dy], [330, 520 + dy], [340, 560 + dy], [420, 540 + dy]];
    const sleeve = [[380, dy - 40], [370, 340 + dy], [600, 340 + dy], [610, dy - 40]];
    gfill(sleeve, KHAKI, { key: 'slf', off: [0, 0] });
    gline(sleeve, { key: 'sl', w: 6 });
    for (const [P, k] of [[fist, 'fist'], [finger, 'finger'], [thumb, 'thumb']]) { gfill(P, SKIN, { key: k + 'f', off: [0, 0] }); gline(P, { closed: k !== 'finger', key: k, w: 6 }); }
    gline(sketchBox(510, 820 + dy, 46, 44, 12), { key: 'nail', w: 3, col: SK.graph, second: false });
    for (let i = 0; i < 3; i++) gline([[422 + i * 46, 500 + dy], [436 + i * 46, 556 + dy]], { key: 'kn' + i, w: 3.5, second: false });
  }
  const pointed = TT >= 72.4;
  person(540, onGround(1235, 62), 62, { key: 'hero', mood: pointed ? 'scared' : 'puzzled', look: [0, -1], arms: [-1.2, -1.2] });
  if (pointed) handLetter('?', 650, 960, 80, { face: 'marker', col: SK.ink, key: 'q9', reveal: ev(72.6, 0.1) });
  pageTag('your turn');
  say([[67.5, ['so the real question', "isn't what a uniform"], [[1, 'uniform']]], [69.58, ['does to you.']],
       [70.76, ["it's what you'll do"], [[0, 'you']]], [72.0, ['when someone', 'in charge tells you.'], [[1, 'in charge']]],
       [74.0, ['what would', 'YOU do?'], [[1, 'YOU']]]], t);
}
