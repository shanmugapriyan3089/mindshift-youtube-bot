// =====================================================================
//  SCENES — Robbers Cave (Sherif, 1954), sketchbook. Every time comes from the narration: when('word', n).
//  Shared helpers (person, say, speech, iconPeople, stamp, ...) live in ../sketch_kit/people.js.
//  Cast: YOU (terracotta t-shirt, an Eagle) · other Eagles (green) · the Rattlers (blue/khaki).
// =====================================================================

const GY = 1235;
const HITS = [when('ugly'), when('enemy'), when('worse'), when('bus')];
const EAG = '#7fa77a', RAT = '#8fa7c2';
const HAIRS = ['#2f2620', '#7a5a3c', '#555', '#a0703c', '#222', '#6b4a2b'];

// a pine tree standing on y
function pine(x, y, s, key, part = 1) {
  gline([[x, y], [x, y - 60 * s]], { key: key + 't', w: 5, second: false, part });
  const P = [[x - 70 * s, y - 60 * s], [x, y - 260 * s], [x + 70 * s, y - 60 * s]];
  gfill(P, '#a9c49a', { key: key + 'f', off: [4, 4], a: clamp(part) });
  gline(P, { closed: true, key: key + 'o', w: 4, part });
}
// a pennant on a pole; `letter` on the cloth
function pennant(x, y0, y1, col, letter, key, part = 1) {
  gline([[x, y1], [x, y0]], { key: key + 'p', w: 6, second: false, part });
  const F = [[x, y0], [x + 190, y0 + 55], [x, y0 + 110]];
  gfill(F, col, { key: key + 'f', off: [3, 3], a: clamp(part) });
  gline(F, { closed: true, key: key + 'o', w: 4, part });
  handLetter(letter, x + 62, y0 + 74, 50, { face: 'marker', col: SK.ink, key: key + 'l', reveal: clamp(part) });
}
// flames: flickering red / yellow tongues around (x, y)
function flames(x, y, w, k, key) {
  if (k <= 0) return;
  for (let i = 0; i < 4; i++) {
    const fx = x - w / 2 + (i + 0.5) * w / 4, h = (70 + 40 * Math.sin(B * 1.9 + i * 2)) * k;
    const P = [[fx - 26, y], [fx - 10, y - h * 0.5], [fx + 4 * Math.sin(B + i), y - h], [fx + 12, y - h * 0.45], [fx + 26, y]];
    gfill(P, i % 2 ? SK.hilite : SK.red, { key: key + 'f' + i, off: [0, 0], a: 0.85 });
    gline(P, { key: key + 'o' + i, w: 3, second: false });
  }
}
// a log cabin: walls x0..x1 on the ground, a roof
function cabin(x0, x1, top, key, part = 1) {
  const W = [[x0, GY], [x0, top], [x1, top], [x1, GY]];
  gfill(W, '#ecc995', { key: key + 'wf', off: [5, 5], a: clamp(part) });
  gline(W, { key: key + 'w', w: 5, part });
  const R = [[x0 - 40, top], [(x0 + x1) / 2, top - 130], [x1 + 30, top]];
  gfill(R, '#b98a5a', { key: key + 'rf', off: [4, 4], a: clamp(part) });
  gline(R, { closed: true, key: key + 'r', w: 5, part });
  for (let i = 1; i < 5; i++) gpencil([[x0 + 6, top + i * (GY - top) / 5], [x1 - 6, top + i * (GY - top) / 5]], { key: key + 'lg' + i, w: 2.5, a: 0.5, part });
}
// a small camper standing on a ground line
function camper(x, gy, r, i, o = {}) {
  person(x, onGround(gy, r), r, { key: (o.key ?? 'cp') + i, shirt: o.hero ? SK.terra : (o.col ?? EAG), hairCol: HAIRS[i % 6], hair: i % 2 ? 'short' : 'mop',
                                  mood: o.mood ?? 'calm', look: o.look ?? [0, 0], arms: o.arms ?? [-1.2, -1.2], shake: o.shake });
}
// a supply truck facing right: cargo box from x, cab, two wheels; `sink` pushes the wheels into mud
function truck(x, y, key, part = 1, sink = 0) {
  const C = sketchBox(x, y, 280, 200, 8, 0.03), K = [[x + 280, y + 70], [x + 360, y + 70], [x + 410, y + 130], [x + 410, y + 200], [x + 280, y + 200]];
  gfill(C, '#e6dcc2', { key: key + 'cf', off: [5, 5], a: clamp(part) });
  gline(C, { closed: true, key: key + 'c', w: 5, part });
  gfill(K, '#c9b27c', { key: key + 'kf', off: [4, 4], a: clamp(part) });
  gline(K, { closed: true, key: key + 'k', w: 5, part });
  gline([[x + 300, y + 85], [x + 350, y + 85], [x + 385, y + 125], [x + 300, y + 125]], { key: key + 'win', closed: true, w: 3, second: false, part });
  handLetter('FOOD', x + 140, y + 125, 58, { face: 'marker', col: SK.ink, key: key + 'fd', reveal: clamp(part) });
  for (const [i, wx] of [[0, x + 70], [1, x + 340]]) {
    const R = loopPts(wx, y + 220 + sink, 36, 36, 0.06);
    gfill(R, SK.ink, { key: key + 'wf' + i, off: [0, 0], a: 0.9 * clamp(part) });
    gline(R, { key: key + 'w' + i, w: 4, part });
  }
}

const SCENES = [
// ---- 1. summer camp, and something across the woods ------------------------------------------
() => {
  sketchPage({ grid: 'dots' }); ground('g1', GY);
  // "summer camp": a tent by the hero
  const T = [[110, GY], [230, 980], [350, GY]];
  gfill(T, '#efe2b4', { key: 'tentf', off: [4, 4], a: clamp(ev(when('camp'), 0.3)) });
  gline(T, { closed: true, key: 'tent', w: 5, part: ev(when('camp') - 0.2, 0.4) });
  gline([[230, 980], [230, GY]], { key: 'tentd', w: 3, second: false, part: ev(when('camp'), 0.3) });
  handLetter('CAMP', 230, 940, 46, { face: 'marker', col: SK.graph, key: 'campl', reveal: ev(when('camp') + 0.2, 0.3) });
  person(470, onGround(GY, 70), 70, { key: 'hero', mood: TT >= when('another') ? 'puzzled' : 'happy', look: TT >= when('another') ? [1, 0] : [0, -0.3], arms: [-1.2, -1.2] });
  // "across the woods": a row of pines, and eyes in the dark between them
  const tw = when('woods') - 0.3;
  [[640, 1.0], [760, 1.25], [880, 0.95]].forEach(([x, s], i) => { if (TT >= tw + i * 0.12) pine(x, GY, s, 'pn' + i, ev(tw + i * 0.12, 0.3)); });
  if (TT >= when('another')) {
    handLetter('?', 760, 690, 90, { face: 'marker', col: SK.ink, key: 'q1', reveal: ev(when('another'), 0.2) });
    if (TT >= when('woods')) for (let i = 0; i < 3; i++) {
      const ex = 700 + i * 70, ey = 1110 - (i % 2) * 40, op = (B + i * 5) % 23 !== 0;
      if (op) for (const s of [-1, 1]) { ctx.fillStyle = SK.ink; ctx.beginPath(); ctx.ellipse(ex + s * 10, ey, 5, 7, 0, 0, TAU); ctx.fill(); }
    }
  }
  pageTag('summer camp');
  say([[S[0], ["you're 11, at a", 'summer camp.'], [[1, 'summer camp.']]], [when('another'), ['other boys, just', 'across the woods.'], [[1, 'woods.']]]], S[0]);
},
// ---- 2. 1954: twenty-two boys, two groups -----------------------------------------------------
() => {
  sketchPage({ grid: 'ruled' });
  const sp = when('split');
  // all 22 boys as empty icons first, then each row takes its colour
  iconPeople(170, 560, 11, 1, 72, 11, ev(when('yours'), 0.9), 'ie', EAG);
  iconPeople(170, 900, 11, 1, 72, 11, ev(when('others'), 0.9), 'ir', RAT);
  if (TT < sp) handLetter('22 boys', 540, 800, 70, { face: 'marker', col: SK.ink, key: 'b22', reveal: ev(S[1] + 0.6, 0.4) });
  else { ctx.save(); ctx.setLineDash([16, 14]); gpencil([[120, 760], [940, 760]], { key: 'split', w: 4, a: 0.9, part: ev(sp, 0.5) }); ctx.restore(); }
  if (TT >= when('eagles')) handLetter('EAGLES', 540, 520, 64, { face: 'marker', col: SK.green, key: 'eag', reveal: ev(when('eagles'), 0.3) });
  if (TT >= when('rattlers')) handLetter('RATTLERS', 540, 860, 64, { face: 'marker', col: '#4f6f95', key: 'rat', reveal: ev(when('rattlers'), 0.3) });
  // you: the first Eagle, circled
  if (TT >= when('yours')) gline(loopPts(170, 590, 42, 56, 0.12), { key: 'you2', w: 5, col: SK.terra, part: ev(when('yours'), 0.4) });
  if (TT >= when('yours')) handLetter('you', 170, 690, 40, { col: SK.terra, key: 'you2l', reveal: ev(when('yours') + 0.2, 0.3) });
  pageTag('1954');
  say([[S[1], ['1954. 22 boys,', 'two groups.'], [[1, 'two groups.']]], [when('yours'), ['you are', 'the Eagles.'], [[1, 'Eagles.']]],
       [when('others'), ['they are', 'the Rattlers.'], [[1, 'Rattlers.']]]], S[1]);
},
// ---- 3. the contest -------------------------------------------------------------------------
() => {
  sketchPage({ grid: 'dots' }); ground('g3', GY);
  const t0 = when('contest') - 0.3, NB = sketchBox(150, 420, 740, 360, 10, 0.03);
  gfill(NB, '#fffdf6', { key: 'nbf', off: [5, 5], a: clamp(ev(t0, 0.3)) });
  gline(NB, { closed: true, key: 'nb', w: 5, part: ev(t0, 0.4) });
  drawPencil(closeP(NB), t0, 0.4);
  handLetter('CONTEST!', 520, 500, 66, { face: 'marker', col: SK.red, key: 'ct', reveal: ev(when('contest'), 0.3) });
  underline(370, 670, 520, { col: SK.red, part: ev(when('contest') + 0.3, 0.3), key: 'ctu' });
  [['baseball', 'baseball'], ['tug of war', 'tug'], ['treasure hunt', 'treasure']].forEach(([s, w], i) => {
    const t = w === 'tug' ? when('baseball') + 0.7 : when(w), y = 600 + i * 62;
    gline(sketchBox(220, y - 36, 38, 38, 4), { key: 'cb' + i, w: 3, second: false, part: ev(t, 0.2) });
    handLetter(s, 290, y, 46, { align: 'left', col: SK.ink, key: 'it' + i, reveal: ev(t, 0.3) });
  });
  // a counselor with a whistle-arm up
  person(230, onGround(GY, 56), 56, { key: 'cns', shirt: KHAKI, hair: 'short', hairCol: '#3b3b3b', mood: 'happy', look: [1, 0], arms: [-1.2, 0.9], tag: 'STAFF' });
  // "prizes for the winners": a trophy; "nothing for the losers": a crossed-out box
  if (TT >= when('prizes')) {
    const tp = ev(when('prizes'), 0.4), CUP = [[470, 860], [610, 860], [590, 960], [560, 990], [520, 990], [490, 960]];
    gfill(CUP, SK.hilite, { key: 'cupf', off: [4, 4], a: clamp(tp) });
    gline(CUP, { closed: true, key: 'cup', w: 5, part: tp });
    gline([[540, 990], [540, 1060]], { key: 'cups', w: 6, second: false, part: tp });
    gline([[490, 1070], [590, 1070]], { key: 'cupb', w: 7, second: false, part: tp });
    handLetter('winners', 540, 1150, 46, { col: SK.green, key: 'wn', reveal: ev(when('winners'), 0.3) });
  }
  if (TT >= when('nothing')) {
    const np = ev(when('nothing'), 0.3);
    gline(sketchBox(720, 880, 160, 160, 6), { key: 'nob', w: 5, part: np });
    gline([[730, 890], [870, 1030]], { key: 'nox1', w: 7, col: SK.red, second: false, part: ev(when('nothing') + 0.2, 0.2) });
    gline([[870, 890], [730, 1030]], { key: 'nox2', w: 7, col: SK.red, second: false, part: ev(when('nothing') + 0.3, 0.2) });
    handLetter('losers', 800, 1150, 46, { col: SK.red, key: 'ls', reveal: ev(when('losers'), 0.3) });
  }
  pageTag('the contest');
  say([[S[2], ['then: a contest.'], [[0, 'contest.']]], [when('prizes'), ['prizes for winners.'], [[0, 'prizes']]],
       [when('nothing'), ['nothing for', 'the losers.'], [[0, 'nothing']]]], S[2]);
},
// ---- 4. it turns ugly -------------------------------------------------------------------------
() => {
  sketchPage({ grid: 'dots' }); ground('g4', GY);
  handLetter('IT TURNS UGLY', 540, 470, 72, { face: 'marker', col: SK.ink, key: 'ugly', reveal: ev(when('ugly'), 0.4) });
  // "your group burns their flag"
  pennant(160, 620, GY, RAT, 'R', 'rf', ev(when('burns') - 0.3, 0.4));
  flames(255, 735, 200, ev(when('flag'), 0.4), 'fl');
  person(420, onGround(GY, 54), 54, { key: 'hero', mood: TT >= when('raid') ? 'angry' : 'happy', look: TT >= when('raid') ? [1, 0] : [-1, -0.5], arms: TT >= when('raid') ? [-1.2, -1.2] : [-1.2, 0.8] });
  // "they raid your cabin, flip your beds"
  if (TT >= when('raid') - 0.2) {
    cabin(560, 900, 760, 'cb', ev(when('raid') - 0.2, 0.4));
    if (TT >= when('beds')) {   // an upside-down bed: mattress with its legs in the air
      const bp = ev(when('beds'), 0.3);
      gfill(sketchBox(600, 1100, 260, 50, 6), '#fffdf6', { key: 'bedf', off: [3, 3], a: clamp(bp) });
      gline(sketchBox(600, 1100, 260, 50, 6), { closed: true, key: 'bed', w: 4, part: bp });
      for (const lx of [615, 845]) gline([[lx, 1100], [lx, 1040]], { key: 'bl' + lx, w: 5, second: false, part: bp });
    }
    if (TT >= when('steal')) for (let i = 0; i < 3; i++) graphiteScribble(640 + i * 100, 950 - (i % 2) * 40, 50, 36, 'mess' + i);
    stamp('RAIDED', 730, 560, when('raid') + 0.4, -0.07, 'srd');
  }
  pageTag('war');
  say([[S[3], ['within days,', 'it turns ugly.'], [[1, 'ugly.']]], [when('your'), ['you burn', 'their flag.'], [[1, 'flag.']]],
       [when('they', 1), ['they raid', 'your cabin.'], [[1, 'cabin.']]]], S[3]);
},
// ---- 5. about 93%: friends only on your own side ----------------------------------------------
() => {
  sketchPage({ grid: 'dots' }); ground('g5', GY);
  handLetter('about 93%', 540, 560, 110, { face: 'marker', col: SK.ink, key: 'p93', reveal: ev(when('about') + 0.2, 0.4) });
  handLetter('of friends: own group', 540, 650, 50, { col: SK.ink, key: 'own', reveal: ev(when('friends'), 0.4) });
  // the bar: 93 own group, 7 the others
  const bp = ev(when('friends'), 0.7), x0 = 160, x1 = 920, xm = lerp(x0, x1, 0.93);
  const BAR = sketchBox(x0, 700, x1 - x0, 70, 6, 0.02);
  gline(BAR, { closed: true, key: 'bar', w: 4, part: ev(when('about') + 0.4, 0.4) });
  if (bp > 0) scribbleFill([[x0, 700], [lerp(x0, xm, bp), 700], [lerp(x0, xm, bp), 770], [x0, 770]], EAG, { key: 'barf', gap: 12, w: 4, part: 1, base: 0.35 });
  if (TT >= when('friends') + 0.7) scribbleFill([[xm, 700], [x1, 700], [x1, 770], [xm, 770]], RAT, { key: 'barr', gap: 8, w: 3, part: ev(when('friends') + 0.7, 0.2), base: 0.35 });
  // "the other side was the enemy": two boys glaring across a crack
  const en = TT >= when('enemy');
  person(260, onGround(GY, 52), 52, { key: 'hero', mood: en ? 'angry' : 'calm', look: [1, 0], arms: [-1.2, -1.2] });
  camper(820, GY, 52, 2, { col: RAT, mood: en ? 'angry' : 'calm', look: [-1, 0], key: 'rt' });
  if (TT >= when('side')) gline([[540, 880], [520, 960], [560, 1040], [525, 1120], [550, GY]], { key: 'crack', w: 5, part: ev(when('side'), 0.4) });
  stamp('ENEMY', 540, 900, when('enemy'), -0.06, 'sen');
  pageTag('enemies');
  say([[S[4], ['at the worst point,'], [[0, 'worst']]], [when('about'), ['93% of friends:', 'own group only.'], [[0, '93%']]],
       [when('other', 1), ['the other side was', 'the enemy.'], [[1, 'enemy.']]]], S[4]);
},
// ---- 6. just meeting made it worse -----------------------------------------------------------
() => {
  sketchPage({ grid: 'ruled' });
  // "shared meals": one long table, Eagles left, Rattlers right
  const ty = 1080, r = 42, xs = [150, 260, 370, 710, 820, 930 - 20];
  const fight = TT >= when('food');
  xs.forEach((x, i) => person(x, ty - 3.6 * r + 46, r, { key: 'm' + i, shirt: i === 0 ? SK.terra : i < 3 ? EAG : RAT, hairCol: HAIRS[i], hair: i % 2 ? 'short' : 'mop',
                                                       mood: TT >= when('worse') ? 'angry' : 'calm', look: [i < 3 ? 1 : -1, 0], arms: fight && i % 2 ? [0.8, 0.8] : [-1.2, -1.2] }));
  const T = [[80, ty], [1000, ty], [980, ty + 90], [100, ty + 90]];
  gfill(T, '#ecc995', { key: 'tbl', off: [4, 4], a: clamp(ev(when('meals') - 0.3, 0.3)) });
  gline(T, { closed: true, key: 'tblo', w: 5, part: ev(when('meals') - 0.3, 0.4) });
  handLetter('together', 540, 1000, 50, { col: SK.graph, key: 'tog', reveal: ev(when('together'), 0.4) });
  // "movies": a little screen; "fireworks": bursts
  if (TT >= when('movies')) {
    const SC = sketchBox(110, 420, 320, 200, 6, 0.03);
    gfill(SC, '#fffdf6', { key: 'scf', off: [4, 4] }); gline(SC, { closed: true, key: 'sc', w: 5, part: ev(when('movies'), 0.3) });
    handLetter('MOVIE', 270, 540, 56, { face: 'marker', col: SK.graph, key: 'mv', reveal: ev(when('movies'), 0.3) });
  }
  if (TT >= when('fireworks')) for (let i = 0; i < 3; i++) {
    const fx = 620 + i * 120, fy = 480 + (i % 2) * 80, k = ev(when('fireworks') + i * 0.15, 0.4);
    for (let j = 0; j < 8; j++) { const a = j * TAU / 8; gline([[fx + Math.cos(a) * 14, fy + Math.sin(a) * 14], [fx + Math.cos(a) * (14 + 46 * k), fy + Math.sin(a) * (14 + 46 * k)]], { key: 'fw' + i + j, w: 3, col: j % 2 ? SK.red : SK.graph, second: false }); }
  }
  stamp('WORSE', 540, 740, when('worse'), -0.06, 'swr');
  // "food fights": crumbs flying over the table
  if (fight) for (let i = 0; i < 6; i++) {
    const k = ((TT * 0.9 + i / 6) % 1), x = lerp(i % 2 ? 760 : 320, i % 2 ? 320 : 760, k), y = 900 - Math.sin(k * Math.PI) * 120;
    gfill(loopPts(x, y, 14, 12, 0.05), i % 3 ? '#ecc995' : SK.red, { key: 'fd' + i, off: [0, 0] });
    gline(loopPts(x, y, 14, 12, 0.05), { key: 'fdo' + i, w: 3, second: false });
  }
  pageTag('contact');
  say([[S[5], ['just put them', 'together.'], [[1, 'together.']]], [when('shared'), ['meals, movies,', 'fireworks.'], [[0, 'meals,']]],
       [when('worse'), ['it got worse.'], [[0, 'worse.']]], [when('meals', 2), ['food fights.'], [[0, 'food fights.']]]], S[5]);
},
// ---- 7. a problem no group can solve alone ------------------------------------------------------
() => {
  sketchPage({ grid: 'dots' }); ground('g7', GY);
  // "the water supply breaks": a tank with a dry tap
  const wt = when('water') - 0.2, TK = sketchBox(110, 430, 230, 170, 10, 0.03);
  gfill(TK, '#cfe0ea', { key: 'tkf', off: [4, 4], a: clamp(ev(wt, 0.3)) });
  gline(TK, { closed: true, key: 'tk', w: 5, part: ev(wt, 0.4) });
  handLetter('WATER', 225, 535, 48, { face: 'marker', col: SK.ink, key: 'wtl', reveal: ev(wt + 0.2, 0.3) });
  gline([[340, 560], [390, 560], [390, 600]], { key: 'tap', w: 6, second: false, part: ev(wt + 0.3, 0.2) });
  if (TT >= when('breaks')) { gline([[360, 620], [420, 680]], { key: 'wx1', w: 6, col: SK.red, second: false, part: ev(when('breaks'), 0.2) }); gline([[420, 620], [360, 680]], { key: 'wx2', w: 6, col: SK.red, second: false, part: ev(when('breaks') + 0.1, 0.2) }); }
  // "the food truck gets stuck"
  const pulled = EZ.io(ev(when('pull'), 1.2)), tx = 500 - 60 * pulled, sink = TT >= when('stuck') ? 24 * (1 - pulled) : 0;
  if (TT >= when('truck') - 0.3) truck(tx, 930, 'tr', ev(when('truck') - 0.3, 0.5), sink);
  if (TT >= when('stuck')) {
    for (let i = 0; i < 2; i++) graphiteScribble(tx + 70 + i * 270, GY - 8, 70, 18, 'mud' + i, { n: 22 });
    if (TT < when('together', 2)) handLetter('STUCK', 700, 860, 64, { face: 'marker', col: SK.red, key: 'stk', reveal: ev(when('stuck'), 0.3) });
  }
  // "both groups grab the same rope and pull"
  if (TT >= when('rope') - 0.2) {
    const rp = ev(when('rope') - 0.2, 0.4), hy = onGround(GY, 40) + 40 * 1.3;
    gline([[tx, 1100], [lerp(tx, 80, rp), hy]], { key: 'rope', w: 6, col: '#a0703c', second: false });
    [[140, EAG, 0], [230, RAT, 1], [320, SK.terra, 2], [410, RAT, 3]].forEach(([x, c, i]) => { if (TT >= when('both') + i * 0.12)
      person(x - 16 * pulled, onGround(GY, 40), 40, { key: 'pl' + i, shirt: c, hairCol: HAIRS[i], hair: i % 2 ? 'short' : 'mop', mood: pulled > 0.6 ? 'happy' : 'angry', look: [-1, 0], arms: [0, 0], rot: -0.12 }); });
  }
  if (TT >= when('together', 2)) handLetter('TOGETHER', 640, 820, 72, { face: 'marker', col: SK.green, key: 'tg7', reveal: ev(when('together', 2), 0.4) });
  pageTag('a shared problem');
  say([[S[6], ['the water breaks.'], [[0, 'water']]], [when('food', 2), ['the food truck', 'gets stuck.'], [[1, 'stuck.']]],
       [when('so', 2), ['both groups pull', 'the same rope.'], [[1, 'same rope.']]]], S[6]);
},
// ---- 8. needing each other, and one bus home ---------------------------------------------------
() => {
  sketchPage({ grid: 'dots' }); ground('g8', GY);
  // two cards: just meeting (crossed out) vs needing each other (ticked)
  const A = sketchBox(110, 420, 380, 260, 10, 0.03), Bc = sketchBox(560, 420, 380, 260, 10, 0.03);
  gfill(A, '#fffdf6', { key: 'caf', off: [5, 5], a: clamp(ev(when('meeting'), 0.3)) });
  gline(A, { closed: true, key: 'ca', w: 5, part: ev(when('meeting'), 0.4) });
  handLetter('just meeting', 300, 540, 48, { col: SK.ink, key: 'jm', reveal: ev(when('meeting') + 0.2, 0.4) });
  if (TT >= when('hate')) { gline([[150, 460], [450, 640]], { key: 'xa1', w: 7, col: SK.red, second: false, part: ev(when('hate'), 0.2) }); gline([[450, 460], [150, 640]], { key: 'xa2', w: 7, col: SK.red, second: false, part: ev(when('hate') + 0.1, 0.2) }); }
  if (TT >= when('needing')) {
    gfill(Bc, '#fffdf6', { key: 'cbf', off: [5, 5] });
    gline(Bc, { closed: true, key: 'cb', w: 5, part: ev(when('needing'), 0.4) });
    handLetter('needing', 750, 520, 52, { face: 'marker', col: SK.ink, key: 'nd1', reveal: ev(when('needing'), 0.3) });
    handLetter('each other', 750, 590, 52, { face: 'marker', col: SK.ink, key: 'nd2', reveal: ev(when('needing') + 0.2, 0.3) });
    checkMark(880, 650, 0.9, ev(when('needing') + 0.5, 0.3));
  }
  // "ride home on one bus": Eagles and Rattlers in the same windows
  if (TT >= when('last') - 0.2) {
    const bp = ev(when('last') - 0.2, 0.5), BUS = sketchBox(130, 820, 780, 320, 24, 0.03);
    gfill(BUS, SK.hilite, { key: 'busf', off: [6, 6], a: 0.8 * clamp(bp) });
    gline(BUS, { closed: true, key: 'bus', w: 6, part: bp });
    drawPencil(closeP(BUS), when('last') - 0.2, 0.5);
    for (let i = 0; i < 5; i++) {
      const wx = 170 + i * 140, WN = sketchBox(wx, 860, 110, 120, 8, 0.02);
      gfill(WN, '#fffdf6', { key: 'bwf' + i, off: [0, 0], a: clamp(bp) });
      gline(WN, { closed: true, key: 'bw' + i, w: 4, part: bp });
      if (TT >= when('asked') + i * 0.12) person(wx + 55, 915, 26, { key: 'bp' + i, shirt: i === 2 ? SK.terra : i % 2 ? RAT : EAG, hairCol: HAIRS[i], hair: i % 2 ? 'short' : 'mop', mood: 'happy', look: [0, 0], arms: [-1.2, -1.2] });
      if (TT >= when('asked')) gfill([[wx + 2, 980], [wx + 108, 980], [wx + 108, 1060], [wx + 2, 1060]], SK.hilite, { key: 'bcv' + i, off: [0, 0], a: 0.95 });
    }
    gline([[130, 1040], [910, 1040]], { key: 'bstripe', w: 4, second: false, part: bp });
    for (const wx of [260, 780]) { const R = loopPts(wx, 1160, 46, 46, 0.06); gfill(R, SK.ink, { key: 'bwh' + wx, off: [0, 0], a: 0.9 }); gline(R, { key: 'bwo' + wx, w: 4 }); }
    handLetter('ONE BUS', 520, 1105, 56, { face: 'marker', col: SK.ink, key: 'ob', reveal: ev(when('ride'), 0.4) });
  }
  pageTag('the twist');
  say([[S[7], ["meeting didn't", 'end the hate.'], [[1, 'hate.']]], [when('needing'), ['needing them did.'], [[0, 'needing']]],
       [when('last'), ['they all rode home', 'on one bus.'], [[1, 'one bus.']]]], S[7]);
},
// ---- 9. your other group ---------------------------------------------------------------------
() => {
  sketchPage({ grid: 'dots' }); ground('g9', GY);
  const goal = TT >= when('goal');
  person(270, onGround(GY, 70), 70, { key: 'hero', mood: goal ? 'happy' : 'puzzled', look: goal ? [0.6, -1] : [1, 0], arms: goal ? [-1.2, 0.6] : [-1.2, -1.2] });
  person(810, onGround(GY, 70), 70, { key: 'oth', shirt: RAT, hair: 'short', hairCol: '#222', mood: goal ? 'happy' : 'puzzled', look: goal ? [-0.6, -1] : [-1, 0], arms: goal ? [0.6, -1.2] : [-1.2, -1.2] });
  ctx.save(); ctx.setLineDash([14, 14]); gpencil([[540, 760], [540, GY]], { key: 'line9', w: 4, a: 0.8, part: ev(S[8] + 0.3, 0.4) }); ctx.restore();
  if (TT < when('goal')) handLetter('us  |  them', 540, 620, 70, { face: 'marker', col: SK.graph, key: 'ut', reveal: ev(when('who') + 0.3, 0.4) });
  else {
    // a shared goal: a flag on a hill between you, arrows from both sides
    const gp = ev(when('goal'), 0.5), HL = [[330, 760], [540, 560], [750, 760]];
    gline(HL, { key: 'hill', w: 5, part: gp });
    gline([[540, 560], [540, 430]], { key: 'gpole', w: 5, second: false, part: gp });
    const F = [[540, 430], [650, 460], [540, 490]];
    gfill(F, SK.hilite, { key: 'gff', off: [3, 3], a: clamp(gp) }); gline(F, { closed: true, key: 'gf', w: 4, part: gp });
    arrowPencil([[320, 880], [430, 720]], ev(when('goal') + 0.4, 0.4), { key: 'ar1' });
    arrowPencil([[760, 880], [650, 720]], ev(when('goal') + 0.5, 0.4), { key: 'ar2' });
  }
  pageTag('your turn');
  say([[S[8], ['who is your', 'other group?'], [[1, 'other group?']]], [when('what'), ['what goal could', 'you share?'], [[1, 'share?']]]], S[8]);
},
];
