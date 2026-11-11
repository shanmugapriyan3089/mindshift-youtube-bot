// =====================================================================
//  SCENES — The Shock Machine (Milgram, 1961), sketchbook. Times are absolute word times from timing.json.
//  Shared helpers (person, say, speech, iconPeople, stamp, ...) live in ../sketch_kit/people.js.
//  Cast: YOU = the teacher (terracotta t-shirt) · the EXPERIMENTER (grey lab coat, glasses) · the LEARNER (green shirt).
// =====================================================================

const LEARNER = '#7fa77a', GY = 1235;

// the shock generator: a panel of 30 switches, 15 V – 450 V; `on` = how many are flipped
function shockMachine(x, y, w, h, t0, on, key) {
  const P = sketchBox(x, y, w, h, 14, 0.03);
  gfill(P, '#e6dcc2', { key: key + 'f', a: clamp(ev(t0 + 0.3, 0.3)) });
  gpencil(P, { closed: true, key: key + 'c', w: 2.6, a: 0.7, part: ev(t0, 0.5) });
  gline(P, { closed: true, key: key + 'o', w: 6, part: ev(t0 + 0.4, 0.4) });
  drawPencil(closeP(P), t0, 0.5);
  handLetter('SHOCK GENERATOR', x + w / 2, y + 62, 40, { face: 'marker', col: SK.ink, key: key + 'tt', reveal: ev(t0 + 0.6, 0.4) });
  const n = 30, sw = (w - 80) / 15;
  for (let i = 0; i < n; i++) {
    const r = Math.floor(i / 15), c = i % 15, sx = x + 40 + c * sw + sw / 2, sy = y + 130 + r * 120;
    const k = ev(t0 + 0.7 + i * 0.03, 0.1);
    if (k <= 0) continue;
    const isOn = i < on, col = i >= 26 ? SK.red : SK.ink;
    gline(sketchBox(sx - sw * 0.32, sy, sw * 0.64, 70, 4), { key: key + 's' + i, w: 2.5, second: false, col });
    gline([[sx, sy + (isOn ? 50 : 20)], [sx, sy + (isOn ? 78 : -8)]], { key: key + 'l' + i + (isOn ? 'on' : ''), w: 5, second: false, col: isOn ? SK.red : SK.ink });
  }
  handLetter('15 V', x + 40 + sw / 2, y + 112, 26, { col: SK.graph, key: key + 'v15', reveal: ev(t0 + 1.0, 0.2) });
  handLetter('450 V', x + w - 40 - sw / 2, y + 352, 26, { col: SK.red, key: key + 'v450', reveal: ev(t0 + 1.4, 0.2) });
  handLetter('DANGER  XXX', x + w - 130, y + h - 24, 30, { face: 'marker', col: SK.red, key: key + 'xxx', reveal: ev(t0 + 1.6, 0.3) });
}
// the learner strapped in a chair, wires to his wrist
function learnerChair(x, gy, r, mood, key, o = {}) {
  const seatY = gy - r * 1.6;
  gline([[x - r * 1.1, seatY], [x + r * 1.1, seatY]], { key: key + 'seat', w: 6 });
  gline([[x - r * 1.0, seatY], [x - r * 1.0, gy]], { key: key + 'l1', w: 5, second: false });
  gline([[x + r * 1.0, seatY], [x + r * 1.0, gy]], { key: key + 'l2', w: 5, second: false });
  gline([[x + r * 1.1, seatY], [x + r * 1.2, seatY - r * 2.6]], { key: key + 'back', w: 6 });
  person(x, seatY - r * 2.6, r, { key: key + 'p', shirt: LEARNER, mood, hairCol: '#3b3b3b', hair: 'short', glasses: true, look: o.look ?? [-1, 0], arms: [-0.3, -0.3], shake: o.shake ?? 0 });
  gline([[x - r * 1.2, seatY - r * 0.9], [x - r * 1.9, seatY - r * 0.2], [x - r * 2.6, seatY + r * 0.3]], { key: key + 'wire', w: 3, col: SK.red, second: false });
}

const SCENES = [
// ---- 1. the ad (0 – 10.11) ------------------------------------------------------------------
() => {
  sketchPage({ grid: 'dots' }); ground('g1', GY);
  const wow = TT >= 4.56;
  person(260, onGround(GY, 72), 72, { key: 'hero', mood: wow ? 'wow' : 'calm', look: [1, -0.4], arms: wow ? [0.9, 0.2] : [0.2, 0.2] });
  const NP = sketchBox(450, 520, 500, 600, 10, 0.04);
  gfill(NP, '#fffaf0', { key: 'npf', a: clamp(ev(3.3, 0.3)) });
  gpencil(NP, { closed: true, key: 'npc', w: 2.6, a: 0.7, part: ev(3.1, 0.6) });
  gline(NP, { closed: true, key: 'np', w: 5, part: ev(3.5, 0.4) });
  drawPencil(closeP(NP), 3.1, 0.6);
  handLetter('NEW HAVEN REGISTER', 700, 585, 34, { face: 'marker', col: SK.graph, key: 'mast', reveal: ev(3.6, 0.4) });
  gline([[480, 610], [920, 610]], { key: 'npr', w: 3, second: false, part: ev(3.9, 0.2) });
  handLetter('$4', 700, 740, 110, { face: 'marker', col: SK.ink, key: 'ad4', reveal: ev(4.56, 0.3) });
  gline(loopPts(700, 705, 95, 70, 0.12), { key: 'adloop', w: 5, col: SK.red, part: ev(5.0, 0.35) });
  // "one hour" (5.86): a little clock
  const clk = loopPts(560, 880, 50, 50, 0.08);
  gline(clk, { key: 'clk', w: 4, part: ev(5.86, 0.3) });
  gline([[560, 880], [560, 846], [560, 880], [590, 890]], { key: 'hands', w: 4, second: false, part: ev(6.1, 0.2) });
  handLetter('1 hour', 760, 895, 52, { col: SK.ink, key: 'h1', reveal: ev(6.28, 0.3) });
  // "memory study at Yale" (7.8 / 8.9)
  handLetter('memory study', 700, 990, 48, { col: SK.ink, key: 'mem', reveal: ev(7.8, 0.4) });
  handLetter('YALE', 700, 1075, 66, { face: 'marker', col: SK.ink, key: 'yale', reveal: ev(8.9, 0.3) });
  if (TT >= 9.1) underline(620, 780, 1090, { col: SK.red, part: ev(9.1, 0.25), key: 'yu' });
  if (wow) handLetter('!', 360, 820, 90, { face: 'marker', col: SK.ink, key: 'bang1', reveal: ev(4.56, 0.1) });
  pageTag('new haven, 1961');
  say([[0, ['new haven, 1961.']], [3.22, ['a newspaper ad:', '$4 for one hour'], [[1, '$4']]], [7.28, ['a memory study', 'at yale.'], [[1, 'yale.']]]], S[0]);
},
// ---- 2. the roles (10.11 – 17.94) -----------------------------------------------------------
() => {
  sketchPage({ grid: 'ruled' }); ground('g2', GY);
  const coat = clamp(ev(11.18, 0.5));
  person(205, onGround(GY, 64), 64, { key: 'exp', outfit: coat > 0 ? 'coat' : 'tee', shirt: coat > 0 ? COAT : '#9aa3ad', hair: 'short', hairCol: '#6b6b6b', glasses: true,
                                      mood: 'calm', look: [1, 0], arms: TT >= 12.16 ? [-1.2, 0.0] : [-1.2, -1.2] });
  // "gives you a job" (12.16) -> "you're the teacher" (14.14)
  person(450, onGround(GY, 66), 66, { key: 'hero', mood: TT >= 14.14 ? 'puzzled' : 'calm', look: [-1, 0], arms: [-1.2, -1.2], tag: TT >= 14.0 ? 'TEACHER' : null, tagReveal: ev(14.0, 0.4) });
  // "the man in the next room" (15.44): a wall, a door, and him behind it
  gline([[650, 520], [650, GY]], { key: 'wall', w: 7, part: ev(15.1, 0.4) });
  ctx.save(); gclip([[655, 520], [1000, 520], [1000, GY], [655, GY]]); ghatch(655, 520, 1000, GY, { ang: -0.9, gap: 14, col: SK.graph, w: 2, a: 0.25 * clamp(ev(15.3, 0.3)), key: 'nr' }); ctx.restore();
  if (TT >= 15.6) learnerChair(860, GY, 52, 'calm', 'ln', { look: [0, 0] });
  handLetter('LEARNER', 815, 600, 44, { face: 'marker', col: SK.ink, key: 'lbl', reveal: ev(16.84, 0.3) });
  handLetter('the experimenter', 230, 700, 34, { col: SK.graph, key: 'lbe', reveal: ev(11.6, 0.4) });
  pageTag('the lab');
  say([[10.11, ['a man in a', 'grey lab coat'], [[1, 'grey lab coat']]], [12.16, ['gives you a job.']], [13.7, ["you're the teacher."], [[0, 'teacher.']]],
       [15.08, ['the man next door', 'is the learner.'], [[1, 'learner.']]]], S[1]);
},
// ---- 3. the machine (17.94 – 26.69) ---------------------------------------------------------
() => {
  sketchPage({ grid: 'dots' });
  // "15 volts" (21.58) -> "then 30" (22.66) -> "all the way up to 450" (23.52 – 24.54)
  let on = 0;
  if (TT >= 21.58) on = 1;
  if (TT >= 22.66) on = 2;
  if (TT >= 23.52) on = 2 + Math.floor(28 * clamp(ev(23.52, 1.1)));
  shockMachine(100, 560, 820, 470, 18.2, on, 'mach');
  const volts = on * 15;
  if (on > 0) handLetter(volts + ' VOLTS', 540, 1150, 90, { face: 'marker', col: on >= 27 ? SK.red : SK.ink, key: 'vc' + volts });
  if (TT >= 24.6) gline(loopPts(780, 905, 130, 60, 0.12), { key: 'max', w: 5, col: SK.red, part: ev(24.6, 0.4) });
  // a hand reaching for the first switch on "press a switch" (20.3)
  if (TT >= 20.1 && TT < 21.58) { const k = EZ.io(ev(20.1, 0.5)); pencilTool(lerp(300, 190, k), lerp(1250, 830, k), -0.9, 1.2); }
  pageTag('the machine');
  say([[18.34, ['every wrong answer,', 'you press a switch.'], [[1, 'switch.']]], [21.58, ['15 volts.', 'then 30.'], [[0, '15 volts.']]],
       [23.52, ['all the way up', 'to 450.'], [[1, '450.']]]], S[2]);
},
// ---- 4. 150 volts (26.69 – 32.64) -----------------------------------------------------------
() => {
  sketchPage({ grid: 'dots' }); ground('g4', GY);
  gline([[560, 520], [560, GY]], { key: 'wall4', w: 7 });
  handLetter('150 VOLTS', 280, 600, 70, { face: 'marker', col: SK.red, key: 'v150', reveal: ev(27.18, 0.4) });
  const cry = TT >= 29.28;
  person(280, onGround(GY, 64), 64, { key: 'hero', mood: cry ? 'scared' : 'calm', look: [1, 0], arms: [0.1, -1.2] });
  learnerChair(820, GY, 56, cry ? 'scream' : 'scared', 'ln4', { shake: cry ? 6 : 0, look: [-1, 0] });
  if (cry) for (let i = 0; i < 3; i++) gline([[700 - i * 20, 760 - i * 26], [660 - i * 26, 740 - i * 30]], { key: 'cr' + i, w: 4, second: false });
  if (TT < 30.52) speech(510, 470, 410, 150, ['AAAH!'], [800, 720], ev(29.28, 0.3), 'b1', { face: 'marker', size: 70 });
  if (TT >= 30.52) speech(510, 470, 410, 150, ['STOP!', 'let me out!'], [800, 720], ev(30.52, 0.5), 'b2', { size: 56 });
  pageTag('150 volts');
  say([[26.69, ['at 150 volts,'], [[0, '150 volts,']]], [29.16, ['he cries out.'], [[0, 'cries out.']]], [30.52, ['he begs you', 'to stop.'], [[1, 'stop.']]]], S[3]);
},
// ---- 5. "the experiment requires that you continue" (32.64 – 40.95) ----------------------------
() => {
  sketchPage({ grid: 'ruled' }); ground('g5', GY);
  // "you turn around" (33.06): the hero looks back at the experimenter
  const turned = TT >= 33.06;
  person(300, onGround(GY, 62), 62, { key: 'hero', mood: 'scared', look: turned ? [1, -0.3] : [-1, 0], arms: [-1.2, -1.2], tag: 'TEACHER' });
  for (let i = 0; i < 2; i++) sweat(240 - i * 14, onGround(GY, 62) - 20 + i * 8, ((TT * 1.3 + i * 0.5) % 1), 'sw5' + i);
  // the experimenter, big and calm, clipboard in hand
  person(760, onGround(GY, 84), 84, { key: 'exp', outfit: 'coat', hair: 'short', hairCol: '#6b6b6b', glasses: true, mood: 'calm', look: [-1, 0], arms: [-1.2, 0.2] });
  gline(sketchBox(870, 860, 90, 120, 6), { key: 'clip', w: 4 });
  for (let i = 0; i < 3; i++) gline([[885, 900 + i * 22], [945, 900 + i * 22]], { key: 'cl' + i, w: 2.5, col: SK.graph, second: false });
  speech(90, 430, 640, 230, ['"The experiment requires', 'that you continue."'], [720, 790], ev(37.22, 2.2), 'q', { size: 46 });
  pageTag('the lab coat');
  say([[32.96, ['you turn around.']], [34.36, ['the man in the coat', 'says calmly:'], [[1, 'calmly:']]],
       [37.22, ['"...that you', 'continue."'], [[1, 'continue."']]]], S[4]);
},
// ---- 6. 65 % (40.95 – 46.98) ------------------------------------------------------------------
() => {
  sketchPage({ grid: 'dots' });
  if (TT < 44.86) {
    // "experts expected almost no one" (41.28 – 43.14)
    ground('g6', GY);
    for (let i = 0; i < 3; i++) person(250 + i * 290, onGround(GY, 56), 56, { key: 'ex' + i, outfit: 'coat', hair: i === 1 ? 'mop' : 'short', hairCol: ['#555', '#7a5a3c', '#999'][i], glasses: i !== 1, mood: 'calm', look: [0, -0.4], arms: [-1.2, -1.2] });
    handLetter('EXPERTS', 540, 560, 60, { face: 'marker', col: SK.ink, key: 'exl', reveal: ev(41.28, 0.4) });
    speech(240, 620, 600, 170, ['"almost no one"'], [540, 860], ev(42.22, 0.8), 'exq', { size: 58 });
  } else {
    // "65 percent did" (44.86): 26 of 40 people light up
    iconPeople(200, 480, 8, 5, 97, 26, ev(44.86, 0.8), 'grid');
    stamp('65%', 540, 1150, 45.4, -0.08, 's65');
  }
  pageTag('the result');
  say([[41.28, ['experts expected', 'almost no one.'], [[1, 'no one.']]], [44.86, ['65% did.'], [[0, '65%']]]], S[5]);
},
// ---- 7. fake (46.98 – 54.37) -------------------------------------------------------------------
() => {
  sketchPage({ grid: 'dots' });
  if (TT < 49.08) {
    // "the shocks were fake" (47.38 / 48.1): the machine's plug isn't even in the wall
    shockMachine(100, 560, 820, 470, 47.0, 0, 'm7');
    gline([[540, 1030], [540, 1110], [420, 1160]], { key: 'cord', w: 5, second: false, part: ev(47.4, 0.3) });
    gline(sketchBox(380, 1150, 70, 40, 6), { key: 'plug', w: 4, part: ev(47.6, 0.2) });
    stamp('FAKE', 760, 1180, 48.1, -0.1, 'sfake');
  } else if (TT < 51.0) {
    // "the learner was an actor" (49.26 / 49.94): he stands up, smiles and takes a bow
    ground('g7', GY);
    person(540, onGround(GY, 80), 80, { key: 'ln7', shirt: LEARNER, mood: 'happy', hair: 'short', hairCol: '#3b3b3b', glasses: true, arms: [0.9, 0.9] });
    stamp('ACTOR', 540, 560, 49.94, 0.06, 'sact');
  } else {
    // "the only real thing in that room was you" (51.18 – 53.18): a spotlight on the teacher
    ground('g7b', GY);
    const spot = [[440, 420], [640, 420], [800, GY], [280, GY]];
    scribbleFill(spot, SK.hilite, { key: 'spot', gap: 14, w: 4, part: ev(51.2, 0.5), base: 0.2 });
    person(540, onGround(GY, 76), 76, { key: 'hero', mood: TT >= 53.18 ? 'wow' : 'puzzled', look: [0, 0], arms: [-1.2, -1.2], tag: 'TEACHER' });
    if (TT >= 52.62) { handLetter('real', 860, 760, 64, { face: 'marker', col: SK.red, key: 'real', reveal: ev(52.62, 0.3) }); gline([[810, 790], [650, 880]], { key: 'ra', w: 5, col: SK.red, second: false, part: ev(52.8, 0.3) }); }
  }
  pageTag('the truth');
  say([[47.38, ['the shocks', 'were fake.'], [[1, 'fake.']]], [49.08, ['the learner', 'was an actor.'], [[1, 'actor.']]],
       [51.0, ['the only real thing', 'was you.'], [[1, 'you.']]]], S[6]);
},
// ---- 8. two refuse (54.37 – 62.92) -------------------------------------------------------------
() => {
  sketchPage({ grid: 'ruled' });
  const gy8 = 1000, peersNo = TT >= 56.32, youNo = TT >= 58.28;
  for (const [i, x] of [[0, 210], [2, 870]]) {
    person(x, onGround(gy8, 50), 50, { key: 'peer' + i, mood: peersNo ? 'angry' : 'calm', hairCol: ['#2f2620', '', '#7a5a3c'][i], shirt: '#8fa7c2', arms: peersNo ? [-0.2, -0.2] : [-1.2, -1.2], look: [0, 0] });
    speech(x - 90, 470, 180, 110, ['NO.'], [x, 600], ev(56.32 + i * 0.1, 0.2), 'no' + i, { face: 'marker', size: 60, col: SK.red });
  }
  person(540, onGround(gy8, 54), 54, { key: 'hero', mood: youNo ? 'angry' : 'puzzled', look: youNo ? [0, 0] : [-1, 0], arms: youNo ? [-0.2, -0.2] : [-1.2, -1.2], tag: 'TEACHER' });
  speech(450, 470, 180, 110, ['NO.'], [540, 600], ev(58.28, 0.2), 'noy', { face: 'marker', size: 60, col: SK.red });
  gpencil([[110, gy8 + 2], [970, gy8 - 2]], { key: 'g8', w: 3, a: 0.7 });
  // "only about one in ten went all the way" (59.72 – 61.88)
  if (TT >= 59.72) { iconPeople(130, 1080, 10, 1, 92, 1, ev(60.22, 0.4), 'ten', SK.red); handLetter('1 in 10', 540, 1250, 60, { face: 'marker', col: SK.ink, key: 't10', reveal: ev(60.8, 0.3) }); }
  pageTag('the twist');
  say([[54.56, ['but when two other', 'teachers refused,'], [[1, 'refused,']]], [57.52, ['almost everyone', 'refused too.'], [[1, 'refused too.']]],
       [59.72, ['only 1 in 10', 'went all the way.'], [[0, '1 in 10']]]], S[7]);
},
// ---- 9. go first (62.92 – 75) -----------------------------------------------------------------
() => {
  sketchPage({ grid: 'dots' }); ground('g9', GY);
  if (TT < 66.58) {
    // "maybe it isn't about how strong you are" (63.44 - 65.84): a heavy dumbbell, then crossed out
    const bar = sketchBox(330, 790, 420, 34, 10);
    gline(bar, { closed: true, key: 'bar', w: 5, part: ev(63.44, 0.4) });
    for (const [i, x] of [[0, 300], [1, 750]]) for (let k = 0; k < 2; k++) {
      const plate = sketchBox(x + (i ? k * 34 : -k * 34) - 22, 700 - k * 20, 44, 214 + k * 40, 10);
      gfill(plate, SK.graph, { key: 'pf' + i + k, a: 0.85 * clamp(ev(63.8 + k * 0.15, 0.2)), off: [0, 0] });
      gline(plate, { closed: true, key: 'pl' + i + k, w: 5, part: ev(63.7 + k * 0.15, 0.25) });
    }
    handLetter('100 kg', 540, 900, 48, { face: 'marker', col: SK.graph, key: 'kg', reveal: ev(64.3, 0.3) });
    handLetter('STRONG?', 540, 600, 72, { face: 'marker', col: SK.ink, key: 'str', reveal: ev(65.1, 0.3) });
    if (TT >= 65.5) { gline([[260, 540], [820, 1000]], { key: 'x1', w: 9, col: SK.red, second: false, part: ev(65.5, 0.2) }); gline([[820, 540], [260, 1000]], { key: 'x2', w: 9, col: SK.red, second: false, part: ev(65.7, 0.2) }); }
  } else {
    // "whether someone goes first" (67.46 – 68.28): a line of people; one steps forward and says no
    const step = EZ.io(ev(67.92, 0.5));
    for (let i = 0; i < 4; i++) person(300 + i * 160, onGround(GY - 160, 40), 40, { key: 'q' + i, hairCol: ['#2f2620', '#7a5a3c', '#555', '#3b3b3b'][i], shirt: ['#8fa7c2', LEARNER, '#c9b27c', '#9aa3ad'][i], mood: 'calm', look: [-1, 0] });
    person(lerp(300, 170, step), onGround(lerp(GY - 160, GY, step), lerp(40, 66, step)), lerp(40, 66, step), { key: 'hero', mood: step >= 1 ? 'angry' : 'calm', arms: step >= 1 ? [1.3, -1.2] : [-1.2, -1.2], look: [1, 0] });
    if (TT >= 69.58) speech(330, 520, 380, 150, ['NO.'], [230, 860], ev(69.58, 0.3), 'nofirst', { face: 'marker', size: 80, col: SK.red });
  }
  pageTag('your turn');
  say([[63.22, ["maybe it isn't about", 'how strong you are.'], [[1, 'strong']]], [66.58, ["it's about whether", 'someone goes first.'], [[1, 'first.']]],
       [69.58, ['would YOU be', 'the first to say no?'], [[0, 'YOU']]]], S[8]);
},
];
