// =====================================================================
//  SCENES — The Line Test (Asch, 1951), sketchbook. Every time comes from the narration: when('word', n).
//  Shared helpers (person, say, speech, iconPeople, stamp, ...) live in ../sketch_kit/people.js.
//  Cast: YOU (terracotta t-shirt, right end of the table) · seven other "students" (actors, blue/green/khaki).
// =====================================================================

const GY = 1235;
const HITS = [when('obvious'), when('every', 1), when('actors'), when('private')];
const SEATS = [120, 235, 350, 465, 580, 695, 810];            // the seven actors; you sit at 930
const SHIRTS = ['#8fa7c2', '#7fa77a', '#c9b27c', '#9aa3ad', '#b48ead', '#8fa7c2', '#7fa77a'];
const HAIRS = ['#2f2620', '#7a5a3c', '#555', '#3b3b3b', '#a0703c', '#222', '#6b4a2b'];

// the table with everyone behind it; `look` for the actors, `say` = how many have said "A" by now
function tableRow(t0, o = {}) {
  const r = 42, ty = 1080;
  SEATS.forEach((x, i) => person(x, ty - 3.6 * r + 46, r, { key: 'a' + i, shirt: SHIRTS[i], hairCol: HAIRS[i], hair: i % 3 === 1 ? 'short' : 'mop',
                                                         mood: o.moodOthers ?? 'calm', look: o.look ?? [0, 0], glasses: i === 3, arms: [-1.2, -1.2] }));
  person(940, ty - 3.6 * 46 + 46, 46, { key: 'hero', mood: o.moodYou ?? 'calm', look: o.lookYou ?? [-1, 0], arms: [-1.2, -1.2] });
  const T = [[60, ty], [1020, ty], [1000, ty + 90], [80, ty + 90]];
  gfill(T, '#ecc995', { key: 'tbl', off: [4, 4] });
  gline(T, { closed: true, key: 'tblo', w: 5, part: ev(t0, 0.5) });
  for (const x of [120, 960]) gline([[x, ty + 90], [x, ty + 200]], { key: 'leg' + x, w: 5, second: false, part: ev(t0 + 0.3, 0.2) });
  return ty;
}
// the cards: the standard line on the left, lines A, B, C on the right (C matches)
function cards(t0, o = {}) {
  const L = sketchBox(110, 500, 330, 420, 10, 0.03), R = sketchBox(500, 500, 470, 420, 10, 0.03);
  for (const [P, k, d] of [[L, 'cl', 0], [R, 'cr', 0.3]]) { gfill(P, '#fffdf6', { key: k + 'f', off: [5, 5], a: clamp(ev(t0 + d, 0.3)) }); gline(P, { closed: true, key: k, w: 5, part: ev(t0 + d, 0.4) }); }
  gline([[275, 580], [275, 840]], { key: 'std', w: 12, second: false, part: ev(o.std ?? t0 + 0.4, 0.3) });
  const cmp = [['A', 600, 640, 800], ['B', 735, 560, 880], ['C', 870, 580, 840]];
  cmp.forEach(([lab, x, y0, y1], i) => {
    gline([[x, y0], [x, y1]], { key: 'cmp' + lab, w: 12, second: false, part: ev((o.cmp ?? t0 + 0.7) + i * 0.15, 0.25) });
    handLetter(lab, x, 900, 48, { face: 'marker', col: SK.ink, key: 'lab' + lab, reveal: ev((o.cmp ?? t0 + 0.7) + i * 0.15 + 0.1, 0.2) });
  });
  if (o.guide) { ctx.save(); ctx.setLineDash([12, 12]); gpencil([[275, 580], [870, 580]], { key: 'gd1', w: 3, a: 0.7, part: o.guide }); gpencil([[275, 840], [870, 840]], { key: 'gd2', w: 3, a: 0.7, part: o.guide }); ctx.restore(); }
}

const SCENES = [
// ---- 1. a simple vision test -----------------------------------------------------------------
() => {
  sketchPage({ grid: 'dots' });
  // "vision test": an eye chart on the wall
  const ch = sketchBox(360, 430, 360, 380, 8, 0.03);
  gfill(ch, '#fffdf6', { key: 'chf', a: clamp(ev(when('vision'), 0.3)), off: [5, 5] });
  gline(ch, { closed: true, key: 'ch', w: 5, part: ev(when('vision') - 0.2, 0.4) });
  [['E', 90, 520], ['F P', 60, 610], ['T O Z', 44, 685], ['L P E D', 32, 745]].forEach(([s, sz, y], i) => handLetter(s, 540, y, sz, { face: 'marker', col: SK.ink, key: 'eye' + i, reveal: ev(when('vision') + 0.1 + i * 0.12, 0.2) }));
  // "seven other students sit at the table with you"
  if (TT >= when('seven') - 0.2) tableRow(when('seven') - 0.2);
  else person(540, onGround(GY, 70), 70, { key: 'hero0', mood: 'calm', look: [0, -0.5], arms: [-1.2, -1.2] });
  pageTag('1951');
  say([[S[0], ['1951.']], [when('you'), ['a simple', 'vision test.'], [[1, 'vision test.']]], [when('seven'), ['seven other students', 'at the table.'], [[0, 'seven']]]], S[0]);
},
// ---- 2. the task ------------------------------------------------------------------------------
() => {
  sketchPage({ grid: 'dots' });
  cards(S[1], { std: when('line', 1), cmp: when('three'), guide: ev(when('same'), 0.5) });
  if (TT >= when('same')) handLetter('same length?', 540, 1040, 62, { face: 'marker', col: SK.red, key: 'same', reveal: ev(when('same'), 0.4) });
  pageTag('the task');
  say([[S[1], ['the task:', 'look at one line.'], [[1, 'one line.']]], [when('then'), ['which of three lines', 'is the same length?'], [[1, 'same length?']]]], S[1]);
},
// ---- 3. obvious: it's C -----------------------------------------------------------------------
() => {
  sketchPage({ grid: 'dots' });
  cards(S[2] - 3, { guide: 1 });
  if (TT >= when('c')) { gline(loopPts(870, 710, 70, 200, 0.12), { key: 'loopC', w: 6, col: SK.green, part: ev(when('c'), 0.4) }); checkMark(870, 1010, 1.4, ev(when('c') + 0.3, 0.3)); }
  // "a child could see it": a small kid points at C
  if (TT >= when('child')) person(250, onGround(GY, 40), 40, { key: 'kid', mood: 'happy', shirt: '#f1bf2c', look: [1, -1], arms: [-1.2, 0.6] });
  handLetter('OBVIOUS', 540, 1180, 72, { face: 'marker', col: SK.ink, key: 'obv', reveal: ev(when('obvious'), 0.4) });
  pageTag('easy');
  say([[S[2], ['the answer', 'is obvious.'], [[1, 'obvious.']]], [when('line', 2), ["it's line C."], [[0, 'C.']]], [when('child'), ['a child', 'could see it.'], [[0, 'child']]]], S[2], 1400);
},
// ---- 4. the others all say A ------------------------------------------------------------------
() => {
  sketchPage({ grid: 'ruled' });
  const ty = tableRow(S[3] - 3, { look: [1, 0], moodYou: TT >= when('every', 1) ? 'scared' : 'puzzled', lookYou: [-1, 0] });
  const saidAt = [when('first'), when('second'), when('third'), when('every', 1), when('every', 1) + 0.12, when('every', 1) + 0.24, when('every', 1) + 0.36];
  SEATS.forEach((x, i) => speech(x - 52, 560 + (i % 2) * 150, 104, 96, ['A'], [x, ty - 175], ev(saidAt[i], 0.15), 'sa' + i, { face: 'marker', size: 62, col: SK.red }));
  if (TT >= when('every', 1)) handLetter('?!', 940, 700, 90, { face: 'marker', col: SK.ink, key: 'q4', reveal: ev(when('every', 1) + 0.3, 0.1) });
  pageTag('the others');
  say([[S[3], ['but the first one', 'says: line A.'], [[1, 'line A.']]], [when('so'), ['so does the second.', 'and the third.'], [[1, 'third.']]],
       [when('every', 1), ['every single one.'], [[0, 'every single one.']]]], S[3]);
},
// ---- 5. your turn -----------------------------------------------------------------------------
() => {
  sketchPage({ grid: 'dots' });
  tableRow(S[4] - 3, { look: [1, 0], moodYou: 'scared', lookYou: [0, 0.3] });
  for (let i = 0; i < 3; i++) sweat(890 - i * 12, 880 + i * 10, ((TT * 1.4 + i * 0.33) % 1), 'sw5' + i);
  // "every face turns to you": arrows from every head to yours
  handLetter('YOUR TURN', 540, 560, 84, { face: 'marker', col: SK.red, key: 'yt', reveal: ev(when('turn'), 0.4) });
  pageTag('you');
  say([[S[4], ["now it's", 'your turn.'], [[1, 'your turn.']]], [when('every', 2), ['every face', 'turns to you.'], [[1, 'you.']]]], S[4]);
},
// ---- 6. the result ----------------------------------------------------------------------------
() => {
  sketchPage({ grid: 'dots' }); ground('g6', GY);
  // "alone ... less than one percent"
  person(250, onGround(GY, 56), 56, { key: 'alone', mood: 'happy', look: [0, 0], arms: [-1.2, -1.2] });
  handLetter('ALONE', 250, 560, 56, { face: 'marker', col: SK.ink, key: 'al', reveal: ev(S[5], 0.3) });
  handLetter('<1% wrong', 250, 660, 50, { face: 'marker', col: SK.green, key: 'pct1', reveal: ev(when('percent'), 0.4) });
  gline([[540, 520], [540, GY]], { key: 'div', w: 4, col: SK.graph, part: ev(when('in', 1), 0.4) });
  // "in the group, three out of four went along"
  if (TT >= when('group')) {
    handLetter('IN A GROUP', 790, 560, 56, { face: 'marker', col: SK.ink, key: 'gr', reveal: ev(when('group'), 0.3) });
    iconPeople(660, 720, 4, 1, 88, 3, ev(when('three', 2), 0.8), 'g34', SK.red);
    handLetter('3 out of 4', 790, 960, 62, { face: 'marker', col: SK.red, key: 'p34', reveal: ev(when('four'), 0.4) });
    if (TT >= when('least')) handLetter('went along', 790, 1050, 46, { col: SK.ink, key: 'wa', reveal: ev(when('least') - 0.6, 0.4) });
  }
  pageTag('the result');
  say([[S[5], ['alone: wrong less', 'than 1% of the time.'], [[1, '1%']]], [when('group'), ['in the group,', '3 out of 4 went along.'], [[1, '3 out of 4']]]], S[5]);
},
// ---- 7. they were actors ----------------------------------------------------------------------
() => {
  sketchPage({ grid: 'dots' });
  tableRow(S[6] - 3, { look: [1, 0], moodOthers: 'happy', moodYou: 'puzzled', lookYou: [-1, 0] });
  stamp('ACTORS', 470, 620, when('actors'), -0.08, 'sact');
  if (TT >= when('tested')) { const spot = [[880, 420], [1000, 420], [1040, 1100], [840, 1100]]; scribbleFill(spot, SK.hilite, { key: 'spot', gap: 14, w: 4, part: ev(when('tested'), 0.4), base: 0.2 }); }
  handLetter('the real test', 770, 1250, 54, { face: 'marker', col: SK.red, key: 'rt', reveal: ev(when('was'), 0.3) });
  pageTag('the truth');
  say([[S[6], ['the other seven', 'were actors.'], [[1, 'actors.']]], [when('only'), ['the only thing tested', 'was you.'], [[1, 'you.']]]], S[6]);
},
// ---- 8. in private ----------------------------------------------------------------------------
() => {
  sketchPage({ grid: 'ruled' }); ground('g8', GY);
  person(380, onGround(GY, 70), 70, { key: 'hero', mood: TT >= when('fewer') ? 'happy' : 'calm', look: [1, 0.5], arms: [-1.2, 0.1] });
  // a private note: "C", folded
  const card = sketchBox(560, 760, 300, 220, 8, 0.03);
  gfill(card, '#fffdf6', { key: 'pc', off: [5, 5], a: clamp(ev(when('write'), 0.3)) });
  gline(card, { closed: true, key: 'pco', w: 5, part: ev(when('write'), 0.4) });
  handLetter('C', 710, 900, 120, { face: 'marker', col: SK.ink, key: 'pC', reveal: ev(when('answer', 3), 0.3) });
  handLetter('PRIVATE', 710, 700, 54, { face: 'marker', col: SK.red, key: 'pv', reveal: ev(when('private'), 0.3) });
  if (TT >= when('fewer')) checkMark(830, 1040, 1.2, ev(when('fewer'), 0.3));
  pageTag('in private');
  say([[S[7], ['but when people could', 'answer in private,'], [[1, 'private,']]], [when('far'), ['far fewer', 'went along.'], [[0, 'far fewer']]]], S[7]);
},
// ---- 9. what you saw vs what you say ----------------------------------------------------------
() => {
  sketchPage({ grid: 'dots' }); ground('g9', GY);
  person(540, onGround(GY, 84), 84, { key: 'hero', mood: TT >= when('willing') ? 'scared' : 'calm', look: [0, -0.4], arms: [-1.2, -1.2] });
  // thought: what you saw (C) · speech: what you say out loud (A)
  speech(110, 400, 380, 240, ['saw:', 'C'], [450, 760], ev(when('saw'), 0.3), 'th', { face: 'marker', size: 80, col: SK.green });
  speech(560, 400, 380, 240, ['say:', 'A'], [620, 760], ev(when('say', 2), 0.3), 'sy', { face: 'marker', size: 80, col: SK.red });
  pageTag('your turn');
  say([[S[8], ["the group didn't change", 'what you saw.'], [[1, 'saw.']]], [when('changed'), ['it changed what', 'you dared to say.'], [[1, 'say.']]],
       [when('what', 3), ['what would YOU', 'have said?'], [[0, 'YOU']]]], S[8]);
},
];
