// =====================================================================
//  SCENES — The Seizure on the Intercom (Darley & Latane, 1968), sketchbook. Times come from the narration: when('word', n).
//  Shared helpers (person, say, speech, iconPeople, stamp, ...) live in ../sketch_kit/people.js.
//  Cast: YOU (terracotta t-shirt) · the other "students" (blue/green/khaki, only voices on a tape).
// =====================================================================

const GY = 1235;
const HITS = [when('choke'), when('die'), when('tape'), when('exaggerated')];
const SHIRTS = ['#8fa7c2', '#7fa77a', '#c9b27c', '#9aa3ad', '#b48ead'];
const HAIRS = ['#2f2620', '#7a5a3c', '#555', '#a0703c', '#222'];

// headphones over a person's head (head centre x, y, radius r)
function headset(x, y, r, key, part = 1) {
  gline(arcPts(x, y - r * 0.05, r * 1.18, Math.PI * 1.05, Math.PI * 1.95, 14), { key: key + 'hb', w: Math.max(4, r * 0.1), second: false, part });
  for (const s of [-1, 1]) {
    const C = loopPts(x + s * r * 1.08, y + r * 0.1, r * 0.2, r * 0.32, 0.05);
    gfill(C, SK.ink, { key: key + 'cf' + s, off: [0, 0], a: clamp(part) });
    gline(C, { key: key + 'c' + s, w: 3, second: false, part });
  }
}
// a wall intercom: box, speaker grille, a little light that blinks while someone talks
function intercomBox(x, y, w, h, t0, key, o = {}) {
  const P = sketchBox(x, y, w, h, 14, 0.03);
  gfill(P, '#e6dcc2', { key: key + 'f', a: clamp(ev(t0 + 0.2, 0.3)) });
  gline(P, { closed: true, key: key + 'o', w: 5, part: ev(t0, 0.4) });
  for (let i = 0; i < 5; i++) gline([[x + w * 0.18, y + h * 0.25 + i * h * 0.12], [x + w * 0.62, y + h * 0.25 + i * h * 0.12]], { key: key + 'g' + i, w: 4, second: false, part: ev(t0 + 0.3 + i * 0.05, 0.15) });
  const lit = o.talk && (B % 4 < 2);
  const L = loopPts(x + w * 0.8, y + h * 0.35, w * 0.06, w * 0.06, 0.05);
  gfill(L, lit ? SK.red : '#fffdf6', { key: key + 'lf', off: [0, 0], a: clamp(ev(t0 + 0.4, 0.2)) });
  gline(L, { key: key + 'l', w: 3, second: false, part: ev(t0 + 0.4, 0.2) });
  if (o.talk) for (let i = 0; i < 3; i++) {   // sound waves out of the side
    const k = ((TT * 1.6 + i / 3) % 1);
    gpencil(arcPts(x + w + 6, y + h * 0.5, 20 + k * 70, -0.7, 0.7, 8), { key: key + 'wv' + i, w: 3, a: 0.9 * (1 - k) });
  }
}
// a little booth: three walls and a floor line, one student inside wearing headphones
function booth(x, w, top, i, o = {}) {
  const r = o.r ?? 40, cx = x + w / 2, hy = onGround(GY, r);
  ctx.save(); gclip([[x, top], [x + w, top], [x + w, GY], [x, GY]]);
  ghatch(x, top, x + w, GY, { ang: -0.9, gap: 18, col: SK.graph, w: 1.6, a: 0.18, key: 'bh' + i });
  ctx.restore();
  gline([[x, GY], [x, top], [x + w, top], [x + w, GY]], { key: 'bw' + i, w: 5, part: o.part ?? 1 });
  person(cx, hy, r, { key: 'st' + i, shirt: o.hero ? SK.terra : SHIRTS[i % 5], hairCol: HAIRS[i % 5], hair: i % 2 ? 'short' : 'mop',
                      mood: o.mood ?? 'calm', look: o.look ?? [0, 0], arms: [-1.2, -1.2], glasses: i === 3 });
  headset(cx, hy, r, 'hs' + i);
}
// a clock face; `hand` 0..1 is one turn of the minute hand
function clockDial(cx, cy, r, hand, key, part = 1) {
  const C = loopPts(cx, cy, r, r, 0.06);
  gfill(C, '#fffdf6', { key: key + 'f', off: [4, 4], a: clamp(part) });
  gline(C, { key: key + 'o', w: 5, part });
  for (let i = 0; i < 12; i++) { const a = i * TAU / 12; gline([[cx + Math.cos(a) * r * 0.8, cy + Math.sin(a) * r * 0.8], [cx + Math.cos(a) * r * 0.92, cy + Math.sin(a) * r * 0.92]], { key: key + 't' + i, w: 3, second: false, a: clamp(part) }); }
  const a = -Math.PI / 2 + hand * TAU;
  gline([[cx, cy], [cx + Math.cos(a) * r * 0.75, cy + Math.sin(a) * r * 0.75]], { key: key + 'm', w: 5, second: false, a: clamp(part) });
  gline([[cx, cy], [cx + r * 0.35, cy - r * 0.2]], { key: key + 'h', w: 6, second: false, a: clamp(part) });
}
// a reel-to-reel tape recorder; reels turn while `spin`
function tapeDeck(x, y, w, h, t0, key, spin) {
  const P = sketchBox(x, y, w, h, 16, 0.03);
  gfill(P, '#d9d2c0', { key: key + 'f', a: clamp(ev(t0 + 0.2, 0.3)) });
  gline(P, { closed: true, key: key + 'o', w: 6, part: ev(t0, 0.4) });
  drawPencil(closeP(P), t0, 0.4);
  for (const [i, cx] of [[0, x + w * 0.28], [1, x + w * 0.72]]) {
    const cy = y + h * 0.42, rr = h * 0.3, R = loopPts(cx, cy, rr, rr, 0.06);
    gfill(R, '#fffdf6', { key: key + 'rf' + i, off: [3, 3], a: clamp(ev(t0 + 0.3, 0.3)) });
    gline(R, { key: key + 'r' + i, w: 5, part: ev(t0 + 0.3 + i * 0.1, 0.3) });
    const a0 = spin ? TT * 3 : 0;
    for (let k = 0; k < 3; k++) { const a = a0 + k * TAU / 3; gline([[cx, cy], [cx + Math.cos(a) * rr * 0.8, cy + Math.sin(a) * rr * 0.8]], { key: key + 'sp' + i + k, w: 4, second: false, a: clamp(ev(t0 + 0.5, 0.2)) }); }
  }
  gline([[x + w * 0.28, y + h * 0.72], [x + w * 0.72, y + h * 0.72]], { key: key + 'tp', w: 4, col: '#6b4a2b', second: false, part: ev(t0 + 0.6, 0.3) });
  for (let k = 0; k < 3; k++) gline(sketchBox(x + w * 0.3 + k * w * 0.15, y + h * 0.8, w * 0.1, h * 0.1, 4), { key: key + 'bt' + k, w: 3, second: false, a: clamp(ev(t0 + 0.7, 0.2)) });
}

const SCENES = [
// ---- 1. a voice on the intercom ------------------------------------------------------------
() => {
  sketchPage({ grid: 'dots' }); ground('g1', GY);
  // "a small room": walls and a door
  gline([[90, GY], [90, 470], [950, 470], [950, GY]], { key: 'room', w: 5, part: ev(when('room') - 0.3, 0.5) });
  const D = sketchBox(130, 760, 170, 470, 6, 0.02);
  gline(D, { closed: true, key: 'door', w: 4, part: ev(when('room'), 0.4) });
  gline(loopPts(275, 1010, 9, 9, 0.05), { key: 'knob', w: 3, second: false, part: ev(when('room') + 0.3, 0.2) });
  const scared = TT >= when('choke');
  person(420, onGround(GY, 70), 70, { key: 'hero', mood: scared ? 'scared' : 'calm', look: TT >= when('intercom') ? [1, -0.6] : [0, 0], arms: [-1.2, -1.2] });
  if (scared) for (let i = 0; i < 2; i++) sweat(350 - i * 14, 960 + i * 10, ((TT * 1.3 + i * 0.5) % 1), 'sw1' + i);
  // "through an intercom": a box on the wall
  if (TT >= when('intercom') - 0.2) {
    intercomBox(620, 560, 240, 170, when('intercom') - 0.2, 'ic1', { talk: TT >= when('hear') });
    handLetter('INTERCOM', 740, 540, 40, { face: 'marker', col: SK.graph, key: 'icl', reveal: ev(when('intercom'), 0.3) });
  }
  if (TT < when('beg')) speech(570, 800, 340, 140, ['*gasp*'], [740, 735], ev(when('choke'), 0.3), 'b1a', { face: 'marker', size: 58 });
  else speech(570, 800, 340, 140, ['help me!'], [740, 735], ev(when('beg'), 0.3), 'b1b', { face: 'marker', size: 58, col: SK.red });
  pageTag('a small room');
  say([[S[0], ['you sit alone in', 'a small room.'], [[1, 'small room.']]], [when('through'), ['over the intercom,'], [[0, 'intercom,']]],
       [when('choke'), ['someone starts', 'to choke.'], [[1, 'choke.']]], [when('beg'), ['and begs', 'for help.'], [[1, 'help.']]]], S[0]);
},
// ---- 2. 1968: the setup ---------------------------------------------------------------------
() => {
  sketchPage({ grid: 'ruled' });
  // "New York": a skyline
  const sky = [[110, 700], [110, 560], [190, 560], [190, 610], [240, 610], [240, 470], [300, 470], [300, 600], [360, 600], [360, 520], [430, 520], [430, 640],
               [500, 640], [500, 500], [540, 450], [580, 500], [580, 620], [650, 620], [650, 540], [720, 540], [720, 650], [790, 650], [790, 500], [860, 500], [860, 700]];
  gline(sky, { key: 'sky', w: 4, part: ev(when('york') - 0.3, 0.8) });
  gpencil([[100, 700], [940, 700]], { key: 'skyg', w: 3, a: 0.7, part: ev(when('york'), 0.3) });
  // "talk about college life": a sign
  if (TT >= when('college') - 0.2) {
    handLetter('topic: college life', 520, 790, 50, { face: 'marker', col: SK.ink, key: 'topic', reveal: ev(when('college') - 0.2, 0.5) });
    underline(330, 710, 810, { col: SK.red, part: ev(when('college') + 0.4, 0.3), key: 'tu' });
  }
  // "everyone talks through headphones": four booths
  if (TT >= when('everyone')) for (let i = 0; i < 4; i++) {
    if (TT < when('everyone') + i * 0.2) continue;
    booth(100 + i * 212, 205, 880, i, { hero: i === 0, part: ev(when('everyone') + i * 0.2, 0.3), look: [i === 0 ? 1 : -1, 0] });
  }
  if (TT >= when('nobody')) for (let i = 0; i < 4; i++) handLetter('?', 202 + i * 212, 950, 60, { face: 'marker', col: SK.graph, key: 'q2' + i, reveal: ev(when('nobody') + i * 0.12, 0.2) });
  pageTag('new york, 1968');
  say([[S[1], ['new york, 1968.'], [[0, '1968.']]], [when('signed'), ['a talk about', 'college life.'], [[1, 'college life.']]],
       [when('everyone'), ['all through headphones.', 'nobody sees anyone.'], [[1, 'nobody']]]], S[1]);
},
// ---- 3. the seizure --------------------------------------------------------------------------
() => {
  sketchPage({ grid: 'dots' }); ground('g3', GY);
  const breaks = TT >= when('breaks');
  intercomBox(120, 640, 360, 240, S[2] - 2, 'ic3', { talk: true });
  // "his voice breaks": a calm wave that turns jagged
  const wave = [];
  for (let i = 0; i <= 40; i++) { const x = 120 + i * 9; const amp = breaks ? 38 * (0.5 + 0.5 * Math.sin(i * 1.7 + B)) : 10; wave.push([x, 980 + (i % 2 ? -amp : amp)]); }
  if (TT >= when('voice')) gline(wave, { key: 'wave' + (breaks ? 'j' : 'c'), w: 4, col: breaks ? SK.red : SK.ink, second: false, part: ev(when('voice'), 0.5) });
  if (TT < when('now')) speech(100, 400, 560, 160, ['"I get seizures', 'sometimes."'], [300, 640], ev(when('seizures') - 0.6, 0.5), 'b3a', { size: 46 });
  else if (TT < when('die')) speech(100, 400, 560, 160, ['"I... can\'t..."'], [300, 640], ev(when('now') + 0.3, 0.3), 'b3b', { size: 52 });
  else speech(100, 400, 560, 160, ['"I\'m going to die!', 'help!"'], [300, 640], ev(when('die'), 0.4), 'b3c', { size: 50, col: SK.red });
  person(770, onGround(GY, 64), 64, { key: 'hero', mood: TT >= when('die') ? 'scream' : breaks ? 'scared' : 'calm', look: [-1, -0.4], arms: [-1.2, -1.2], shake: TT >= when('die') ? 3 : 0 });
  headset(770, onGround(GY, 64), 64, 'hs3');
  if (breaks) handLetter('!', 880, 860, 90, { face: 'marker', col: SK.ink, key: 'ex3', reveal: ev(when('breaks'), 0.1) });
  pageTag('the voice');
  say([[S[2], ['one student said he', 'gets seizures.'], [[1, 'seizures.']]], [when('now'), ['now his voice', 'breaks.'], [[1, 'breaks.']]],
       [when('says'), ['"I\'m going to die."'], [[0, 'die.']]]], S[2]);
},
// ---- 4. someone else will go ----------------------------------------------------------------
() => {
  sketchPage({ grid: 'dots' }); ground('g4', GY);
  const waiting = TT >= when('sit');
  person(380, onGround(GY, 72), 72, { key: 'hero', mood: waiting ? 'puzzled' : 'calm', look: waiting ? [1, 0] : [0, -1], arms: [-1.2, -1.2] });
  headset(380, onGround(GY, 72), 72, 'hs4');
  // thought: "other students are listening too"
  if (TT < when('surely')) {
    speech(110, 400, 820, 330, [], [380, 860], ev(when('listening') - 0.4, 0.3), 'th4a');
    if (TT >= when('listening') - 0.3) { iconPeople(290, 460, 4, 1, 150, 4, ev(when('listening'), 0.8), 'oth', SK.graph); handLetter('listening too?', 520, 690, 46, { col: SK.ink, key: 'lt', reveal: ev(when('too'), 0.4) }); }
  } else speech(110, 400, 820, 330, ['"surely someone', 'else has gone."'], [380, 860], ev(when('surely'), 0.6), 'th4b', { size: 58 });
  // "so you sit there, and wait": the clock keeps going
  if (waiting) { clockDial(790, 940, 95, (TT - when('sit')) * 0.4, 'clk4', ev(when('sit'), 0.3)); handLetter('wait...', 790, 1110, 50, { col: SK.graph, key: 'wt', reveal: ev(when('wait'), 0.4) }); }
  pageTag('waiting');
  say([[S[3], ['others are', 'listening too...'], [[1, 'listening']]], [when('surely'), ['surely someone', 'else has gone.'], [[1, 'gone.']]],
       [when('so', 2), ['so you sit there,', 'and wait.'], [[1, 'wait.']]]], S[3]);
},
// ---- 5. alone: about 85% helped --------------------------------------------------------------
() => {
  sketchPage({ grid: 'dots' });
  handLetter('JUST YOU', 540, 520, 80, { face: 'marker', col: SK.ink, key: 'jy', reveal: ev(S[4] + 0.2, 0.4) });
  if (TT >= when('listener')) { const [a, b] = [380, 700]; underline(a, b, 545, { col: SK.red, part: ev(when('listener'), 0.3), key: 'jyu' }); }
  // twenty people, about seventeen of them run for help
  iconPeople(180, 640, 10, 2, 80, 17, ev(when('ran'), 1.0), 'i85', SK.green);
  if (TT >= when('about', 2)) handLetter('about 85%', 540, 1010, 110, { face: 'marker', col: SK.green, key: 'p85', reveal: ev(when('about', 2), 0.4) });
  if (TT >= when('ran')) handLetter('ran for help', 540, 1130, 58, { col: SK.ink, key: 'rfh', reveal: ev(when('ran'), 0.4) });
  if (TT >= when('ended')) checkMark(830, 1090, 1.0, ev(when('ended'), 0.3));
  pageTag('alone');
  say([[S[4], ['when you thought you', 'were the only one,'], [[1, 'only one,']]], [when('about', 2), ['about 85%', 'ran for help.'], [[0, '85%']]]], S[4]);
},
// ---- 6. with four others: about 31% --------------------------------------------------------
() => {
  sketchPage({ grid: 'dots' });
  // "four others could hear it": five little people in headphones
  const gy6 = 860;
  for (let i = 0; i < 5; i++) {
    if (TT < when('four') + i * 0.12 && i > 0) continue;
    const x = 180 + i * 180, r = 36, hy = onGround(gy6, r);
    person(x, hy, r, { key: 'c6' + i, shirt: i === 0 ? SK.terra : SHIRTS[i], hairCol: HAIRS[i], hair: i % 2 ? 'short' : 'mop', mood: TT >= when('only', 2) ? 'puzzled' : 'calm', look: [i < 2 ? 1 : -1, 0], arms: [-1.2, -1.2] });
    headset(x, hy, r, 'h6' + i);
  }
  gpencil([[120, gy6 + 2], [940, gy6 - 2]], { key: 'g6', w: 3, a: 0.7 });
  if (TT < when('more')) handLetter('+ 4 OTHERS', 540, 560, 70, { face: 'marker', col: SK.ink, key: 'p4', reveal: ev(when('four'), 0.4) });
  else stamp('LESS HELP', 540, 540, when('more'), -0.06, 'slh');
  // twenty people, only about six of them go
  if (TT >= when('only', 2) - 0.2) iconPeople(180, 930, 10, 2, 80, 6, ev(when('only', 2), 0.8), 'i31', SK.red);
  if (TT >= when('only', 2)) handLetter('only about 31%', 540, 1235, 80, { face: 'marker', col: SK.red, key: 'p31', reveal: ev(when('only', 2), 0.4) });
  pageTag('in a group');
  say([[S[5], ['with four others', 'listening,'], [[0, 'four others']]], [when('only', 2), ['only about 31%', 'went.'], [[0, '31%']]],
       [when('more'), ['more people,', 'less help.'], [[1, 'less help.']]]], S[5]);
},
// ---- 7. it was a tape ----------------------------------------------------------------------
() => {
  sketchPage({ grid: 'dots' }); ground('g7', GY);
  tapeDeck(200, 430, 680, 330, when('voice', 2) - 0.4, 'td', TT >= when('voice', 2));
  stamp('TAPE', 540, 820, when('tape'), -0.07, 'stape');
  if (TT >= when('only', 3)) { const spot = [[470, 870], [610, 870], [740, GY], [340, GY]]; scribbleFill(spot, SK.hilite, { key: 'spot7', gap: 14, w: 4, part: ev(when('only', 3), 0.4), base: 0.2 }); }
  const up = TT >= when('stand');
  person(540, onGround(GY, 64) + (up ? -10 : 0), 64, { key: 'hero', mood: up ? 'wow' : 'puzzled', look: [0, -0.5], arms: up ? [0.9, 0.9] : [-1.2, -1.2] });
  if (TT >= when('no') && TT < when('voice', 2)) handLetter('no seizure', 540, 600, 70, { face: 'marker', col: SK.red, key: 'nos', reveal: ev(when('no'), 0.3) });
  pageTag('the truth');
  say([[S[6], ['there was', 'no seizure.'], [[1, 'no seizure.']]], [when('voice', 2), ['the voice', 'was a tape.'], [[1, 'tape.']]],
       [when('only', 3), ['the real test: would', 'you stand up?'], [[1, 'stand up?']]]], S[6]);
},
// ---- 8. the 38 witnesses -----------------------------------------------------------------------
() => {
  sketchPage({ grid: 'ruled' });
  const t0 = when('newspaper') - 0.3;
  const NP = sketchBox(150, 430, 780, 500, 10, 0.04);
  gfill(NP, '#fffaf0', { key: 'npf', a: clamp(ev(t0 + 0.2, 0.3)) });
  gline(NP, { closed: true, key: 'np', w: 5, part: ev(t0, 0.4) });
  drawPencil(closeP(NP), t0, 0.4);
  handLetter('DAILY NEWS, 1964', 540, 500, 40, { face: 'marker', col: SK.graph, key: 'mast', reveal: ev(t0 + 0.3, 0.4) });
  gline([[180, 525], [900, 525]], { key: 'npr', w: 3, second: false, part: ev(t0 + 0.4, 0.2) });
  handLetter('38 WITNESSES', 540, 640, 84, { face: 'marker', col: SK.ink, key: 'h38', reveal: ev(when('people', 3) - 0.4, 0.4) });
  handLetter('did nothing', 540, 740, 60, { col: SK.ink, key: 'dn', reveal: ev(when('nothing'), 0.3) });
  for (let i = 0; i < 4; i++) gpencil([[200, 800 + i * 30], [i % 2 ? 700 : 880, 800 + i * 30]], { key: 'np' + i, w: 3, a: 0.6, part: ev(t0 + 0.5 + i * 0.1, 0.2) });
  if (TT >= when('exaggerated')) {
    gline([[260, 610], [820, 660]], { key: 'x38', w: 8, col: SK.red, second: false, part: ev(when('exaggerated'), 0.2) });
    stamp('EXAGGERATED', 540, 1040, when('exaggerated'), -0.05, 'sex');
  }
  if (TT >= when('result')) { handLetter('the lab result held', 500, 1230, 60, { face: 'marker', col: SK.green, key: 'held', reveal: ev(when('result'), 0.4) }); checkMark(870, 1205, 0.9, ev(when('result') + 0.4, 0.3)); }
  pageTag('the twist');
  say([[S[7], ['a newspaper said 38', 'people did nothing.'], [[1, 'did nothing.']]], [when('that'), ['that story was', 'exaggerated.'], [[1, 'exaggerated.']]],
       [when('this'), ['this result', 'was not.'], [[1, 'was not.']]]], S[7]);
},
// ---- 9. will you be the one who moves? -----------------------------------------------------------
() => {
  sketchPage({ grid: 'dots' }); ground('g9', GY);
  const step = EZ.io(ev(when('next'), 0.6)), backY = GY - 170;
  gpencil([[140, backY + 2], [940, backY - 2]], { key: 'g9b', w: 3, a: 0.6 });
  [220, 380, 700, 860].forEach((x, i) => person(x, onGround(backY, 40), 40, { key: 'cr' + i, shirt: SHIRTS[i], hairCol: HAIRS[i], hair: i % 2 ? 'short' : 'mop', mood: 'calm', look: [x < 540 ? 1 : -1, 0], arms: [-1.2, -1.2] }));
  const r = lerp(40, 68, step), gy = lerp(backY, GY, step);
  person(lerp(540, 520, step), onGround(gy, r), r, { key: 'hero', mood: step >= 1 ? 'angry' : 'puzzled', look: step >= 1 ? [0, 0] : [-1, 0], arms: step >= 1 ? [0.9, -1.2] : [-1.2, -1.2] });
  if (TT < when('next')) speech(170, 420, 740, 170, ['"someone else', 'will go..."'], [540, 860], ev(when('everyone', 2) - 0.2, 0.5), 'b9a', { size: 54 });
  else if (TT >= when('moves')) speech(330, 420, 420, 150, ['"I\'ll go."'], [520, 860], ev(when('moves'), 0.3), 'b9b', { face: 'marker', size: 70, col: SK.red });
  pageTag('your turn');
  say([[S[8], ['in a crowd, everyone', 'waits for someone else.'], [[1, 'someone else.']]],
       [when('next'), ['will YOU be the one', 'who moves?'], [[0, 'YOU']]]], S[8]);
},
];
