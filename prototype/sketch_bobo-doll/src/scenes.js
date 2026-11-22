// =====================================================================
//  SCENES — The Bobo Doll (Bandura, 1961), sketchbook. Every time comes from the narration: when('word', n).
//  Shared helpers (person, say, speech, iconPeople, stamp, ...) live in ../sketch_kit/people.js.
//  Cast: YOU (a small child, terracotta t-shirt) · the adult model (blue) · the Bobo doll (an inflatable clown).
// =====================================================================

const GY = 1235;
const HITS = [when('punching'), when('mallet'), when('sock'), when('copied'), when('rewarded')];
const MODEL = '#8fa7c2', WOOD = '#b98a5a';

// the inflatable clown, pivoting on its weighted bottom at (x, gy); s = body half-height
function bobo(x, gy, s, rot, key, part = 1) {
  if (part <= 0) return;
  const a = clamp(part * 2);
  ctx.save(); ctx.translate(x, gy); ctx.rotate(rot);
  const body = loopPts(0, -s * 0.95, s * 0.62, s * 0.95, 0, 0, 40);
  gfill(body, '#fffdf6', { key: key + 'bf', off: [5, 5], a });
  ctx.save(); gclip(body);
  for (let i = 0; i < 3; i++) gfill(sketchBox(-s, -s * (0.45 + i * 0.55), 2 * s, s * 0.2, 0, 0), '#ef9aa6', { key: key + 'st' + i, off: [0, 0], a });
  ctx.restore();
  gline(body, { closed: true, key: key + 'bo', w: 5, part });
  const hy = -s * 2.2, hr = s * 0.48, head = loopPts(0, hy, hr, hr, 0, 0, 30);
  gfill(head, '#fffdf6', { key: key + 'hf', off: [4, 4], a });
  for (const sd of [-1, 1]) gfill(loopPts(sd * hr * 0.95, hy - hr * 0.2, hr * 0.35, hr * 0.3, 0, 0, 16), '#f1bf2c', { key: key + 'tuft' + sd, off: [0, 0], a });
  gline(head, { closed: true, key: key + 'ho', w: 5, part });
  if (part >= 1) {
    for (const sd of [-1, 1]) { ctx.fillStyle = SK.ink; ctx.beginPath(); ctx.arc(sd * hr * 0.35, hy - hr * 0.2, hr * 0.09, 0, TAU); ctx.fill(); }
    gfill(loopPts(0, hy + hr * 0.12, hr * 0.17, hr * 0.17, 0, 0, 14), '#e07a6a', { key: key + 'nose', off: [0, 0] });
    gline(arcPts(0, hy + hr * 0.1, hr * 0.55, Math.PI * 0.2, Math.PI * 0.8, 10), { key: key + 'sm', w: 4, second: false });
  }
  ctx.restore();
}
// where a person's hand ends up: (x, y) head centre, r head radius, ang arm angle, side -1 left / +1 right
function hand(x, y, r, ang, side) { const L = r * 1.45; return [x + side * r * 0.62 + side * L * Math.cos(ang), y + r * 1.3 - L * Math.sin(ang)]; }
// a wooden mallet held at p, handle pointing along the unit vector d
function mallet(p, d, len, key, part = 1) {
  const e = [p[0] + d[0] * len, p[1] + d[1] * len], n = [-d[1], d[0]];
  gline([[p[0] - d[0] * 12, p[1] - d[1] * 12], e], { key: key + 'h', w: 8, col: '#a0703c', second: false, part });
  const H = [[e[0] - n[0] * len * 0.32, e[1] - n[1] * len * 0.32], [e[0] + n[0] * len * 0.32, e[1] + n[1] * len * 0.32]];
  gline(H, { key: key + 'o', w: 30, col: SK.ink, second: false, part });
  gline(H, { key: key + 'f', w: 22, col: WOOD, second: false, part });
}
// the adult model, facing left, swinging the left arm; `beat` 0..1 = how hard the swing is
function model(x, r, beat, o = {}) {
  const y = onGround(GY, r), ang = beat > 0 ? lerp(-0.1, 1.1, 0.5 + 0.5 * Math.sin(TT * 9)) : -1.2;
  person(x, y, r, { key: o.key ?? 'model', shirt: MODEL, hair: 'short', hairCol: '#3b3b3b', mood: beat > 0 ? 'angry' : 'calm', look: [-1, 0], arms: [ang, -1.2] });
  if (o.mallet) { const h = hand(x, y, r, ang, -1); mallet(h, [-Math.cos(ang + 0.5), -Math.sin(ang + 0.5)], r * 1.4, (o.key ?? 'model') + 'ml', o.mallet); }
  return ang;
}
// the doll rocks back when hit
const rock = (on, dir = -1) => on ? dir * 0.16 * Math.abs(Math.sin(TT * 9)) : 0;

const SCENES = [
// ---- 1. you are watching ------------------------------------------------------------------------
() => {
  sketchPage({ grid: 'dots' }); ground('g1', GY);
  const hit = TT >= when('punching');
  if (TT >= when('adult') - 0.2) model(790, 60, hit ? 1 : 0);
  bobo(570, GY, 100, rock(hit), 'bb1', ev(when('clown') - 0.3, 0.5));
  if (TT >= when('clown')) handLetter('a giant clown', 520, 640, 52, { face: 'marker', col: SK.ink, key: 'gc', reveal: ev(when('clown'), 0.4) });
  if (hit) handLetter('POW!', 420, 820, 64, { face: 'marker', col: SK.red, key: 'pow1', reveal: ev(when('punching') + 0.2, 0.2), rot: -0.15 });
  const w = TT >= when('watching');
  person(210, onGround(GY, 44), 44, { key: 'hero', mood: w ? 'wow' : 'calm', look: [1, 0], arms: [-1.2, -1.2] });
  if (w) handLetter('watching', 210, 900, 46, { col: SK.terra, key: 'wt', reveal: ev(when('watching'), 0.4) });
  pageTag('you');
  say([[S[0], ["you're a", 'small child.'], [[1, 'small child.']]], [when('adult'), ['an adult punches', 'a giant clown.'], [[1, 'clown.']]],
       [when('and', 1), ['and you watch', 'every move.'], [[1, 'every move.']]]], S[0]);
},
// ---- 2. 1961, Stanford: stickers, and the attack starts ----------------------------------------
() => {
  sketchPage({ grid: 'ruled' }); ground('g2', GY);
  handLetter('STANFORD, 1961', 540, 470, 64, { face: 'marker', col: SK.ink, key: 'st2', reveal: ev(S[1] + 0.2, 0.5) });
  // a little table with stickers
  person(240, onGround(GY, 40), 40, { key: 'hero', mood: TT >= when('beating') ? 'wow' : 'happy', look: TT >= when('across') ? [1, 0] : [0, 1], arms: [-0.3, -0.3] });
  const tp = ev(when('table') - 0.4, 0.4), TB = sketchBox(90, 1120, 300, 26, 4, 0.02);
  gfill(TB, '#ecc995', { key: 'tbf', off: [3, 3], a: clamp(tp) }); gline(TB, { closed: true, key: 'tb', w: 5, part: tp });
  for (const x of [110, 370]) gline([[x, 1146], [x, GY]], { key: 'tl' + x, w: 5, second: false, part: tp });
  if (TT >= when('stickers')) [[140, 0], [190, 1], [300, 2], [345, 3]].forEach(([x, i]) => doodleStar(x, 1108, 14, 'stk' + i, { col: ['#f1bf2c', '#ef9aa6', '#7fa77a', '#8fa7c2'][i], part: ev(when('stickers') + i * 0.1, 0.2), w: 5, a: 1 }));
  if (TT >= when('stickers')) handLetter('stickers', 240, 1000, 40, { col: SK.graph, key: 'stl', reveal: ev(when('stickers'), 0.3) });
  // across the room: the adult and the clown
  const beat = TT >= when('beating');
  if (TT >= when('across')) { ctx.save(); ctx.setLineDash([12, 12]); gpencil([[330, 980], [530, 980]], { key: 'acr', w: 3, a: 0.8, part: ev(when('across'), 0.4) }); ctx.restore(); }
  model(820, 58, beat ? 1 : 0);
  bobo(640, GY, 95, rock(beat), 'bb2');
  pageTag('1961');
  say([[S[1], ['1961, Stanford.'], [[0, 'Stanford.']]], [when('you'), ['you play with', 'stickers.'], [[1, 'stickers.']]],
       [when('across'), ['an adult starts', 'beating the clown.'], [[1, 'beating']]]], S[1]);
},
// ---- 3. sit, punch, mallet, "sock him!" ----------------------------------------------------------
() => {
  sketchPage({ grid: 'dots' }); ground('g3', GY);
  // the script, ticked off as it happens
  const NB = sketchBox(130, 400, 420, 250, 8, 0.03);
  gfill(NB, '#fffdf6', { key: 'nbf', off: [5, 5], a: clamp(ev(S[2], 0.3)) }); gline(NB, { closed: true, key: 'nb', w: 5, part: ev(S[2], 0.4) });
  [['sits on it', 'sit'], ['punches its nose', 'nose'], ['hits with a mallet', 'mallet']].forEach(([s, wd], i) => {
    if (TT < when(wd)) return;
    handLetter(s, 160, 470 + i * 70, 40, { col: SK.ink, key: 'li' + i, align: 'left', reveal: ev(when(wd), 0.4) });
    checkMark(510, 455 + i * 70, 0.6, ev(when(wd) + 0.3, 0.2), SK.ink, 'ck' + i);
  });
  const ml = TT >= when('mallet'), hit = TT >= when('punch');
  model(760, 66, hit ? 1 : 0, { mallet: ml ? ev(when('mallet'), 0.3) : 0 });
  bobo(470, GY, 112, TT < when('punch') && TT >= when('sit') ? -0.35 : rock(hit), 'bb3');
  speech(560, 560, 360, 140, ['"Sock him!"'], [740, 900], ev(when('sock'), 0.3), 'sock', { face: 'marker', size: 58, col: SK.red });
  pageTag('the attack');
  say([[S[2], ['they sit on it.', 'they punch its nose.'], [[1, 'nose.']]], [when('they', 3), ['they hit it', 'with a mallet...'], [[1, 'mallet...']]],
       [when('shout'), ['...and shout:', '"sock him!"'], [[1, '"sock him!"']]]], S[2]);
},
// ---- 4. a room full of toys, and the same clown --------------------------------------------------
() => {
  sketchPage({ grid: 'dots' }); ground('g4', GY);
  gpencil([[860, 380], [860, GY - 10]], { key: 'wall', w: 3, a: 0.6 });
  // a shelf of toys
  const tp = ev(when('toys') - 0.2, 0.5);
  gline([[100, 700], [520, 700]], { key: 'shelf', w: 6, part: tp });
  if (TT >= when('toys') - 0.2) {
    const BL = loopPts(160, 652, 42, 42, 0.05); gfill(BL, '#8fa7c2', { key: 'ball', off: [3, 3], a: clamp(tp) }); gline(BL, { key: 'ballo', w: 4, part: tp });
    [[230, 0], [290, 1], [260, 2]].forEach(([x, i]) => { const y = i === 2 ? 560 : 612; const P = sketchBox(x, y, 58, 52, 4, 0.02);
      gfill(P, ['#f1bf2c', '#ef9aa6', '#7fa77a'][i], { key: 'blk' + i, off: [3, 3], a: clamp(tp) }); gline(P, { closed: true, key: 'blko' + i, w: 4, part: tp }); });
    const TR = sketchBox(370, 620, 130, 54, 6, 0.02); gfill(TR, '#c9b27c', { key: 'trk', off: [3, 3], a: clamp(tp) }); gline(TR, { closed: true, key: 'trko', w: 4, part: tp });
    for (const wx of [395, 475]) gline(loopPts(wx, 680, 16, 16, 0.05), { key: 'tw' + wx, w: 4, part: tp });
    handLetter('toys', 310, 790, 50, { face: 'marker', col: SK.ink, key: 'toys', reveal: ev(when('toys'), 0.3) });
  }
  const seen = TT >= when('clown', 3);
  person(250, onGround(GY, 46), 46, { key: 'hero', mood: seen ? 'wow' : 'happy', look: [seen ? 1 : -0.5, 0], arms: [-1.2, -1.2] });
  bobo(720, GY, 100, 0, 'bb4', ev(when('corner'), 0.6));
  if (TT >= when('same')) handLetter('the same clown', 640, 860, 50, { face: 'marker', col: SK.red, key: 'same', reveal: ev(when('same'), 0.4) });
  pageTag('the toy room');
  say([[S[3], ['a room full', 'of toys.'], [[1, 'toys.']]], [when('and', 1), ['and in the corner...'], [[0, 'corner...']]],
       [when('stands'), ['...the same clown.'], [[0, 'clown.']]]], S[3]);
},
// ---- 5. alone, watched through a mirror ---------------------------------------------------------
() => {
  sketchPage({ grid: 'ruled' }); ground('g5', GY);
  // the one-way mirror on the wall, with a quiet researcher behind it
  const mp = ev(when('mirror') - 0.6, 0.5), MR = sketchBox(540, 400, 360, 250, 6, 0.02);
  if (TT >= when('researcher') - 0.2) {
    gfill(MR, '#dfe8ee', { key: 'mrf', off: [4, 4], a: clamp(ev(when('researcher') - 0.2, 0.3)) });
    gline(MR, { closed: true, key: 'mr', w: 5, part: ev(when('researcher') - 0.2, 0.4) });
    ctx.save(); gclip(MR);
    gpencil(loopPts(720, 500, 38, 42, 0.05), { key: 'obh', w: 3, a: 0.7 * clamp(mp) });
    gpencil([[650, 650], [670, 570], [770, 570], [790, 650]], { key: 'obb', w: 3, a: 0.7 * clamp(mp) });
    for (const g of [0, 1]) gline([[580 + g * 180, 640], [660 + g * 180, 420]], { key: 'gl' + g, w: 3, col: '#ffffff', second: false, a: 0.8 });
    ctx.restore();
    handLetter('mirror', 720, 700, 40, { col: SK.graph, key: 'mrl', reveal: ev(when('mirror'), 0.3) });
  }
  if (TT >= when('nobody')) handLetter('no instructions', 280, 520, 46, { face: 'marker', col: SK.ink, key: 'noi', reveal: ev(when('nobody'), 0.4) });
  bobo(760, GY, 95, 0, 'bb5');
  const r = 46, y = onGround(GY, r), up = TT >= when('mallet', 2), ang = up ? 0.6 : -1.2;
  person(330, y, r, { key: 'hero', mood: up ? 'puzzled' : 'calm', look: [1, up ? -0.5 : 0.6], arms: [-1.2, ang] });
  if (up) mallet(hand(330, y, r, ang, 1), [Math.cos(ang + 0.4), -Math.sin(ang + 0.4)], 70, 'hm');
  else mallet([440, GY - 8], [1, 0], 70, 'hm', ev(S[4], 0.3));
  pageTag('alone');
  say([[S[4], ['nobody tells you', 'what to do.'], [[0, 'nobody']]], [when('a', 1), ['someone watches', 'behind a mirror.'], [[1, 'mirror.']]],
       [when('pick'), ['you pick up', 'the mallet.'], [[1, 'mallet.']]]], S[4]);
},
// ---- 6. 72 children: they copied it ---------------------------------------------------------------
() => {
  sketchPage({ grid: 'dots' }); ground('g6', GY);
  handLetter('72 children', 540, 470, 76, { face: 'marker', col: SK.ink, key: 'n72', reveal: ev(S[5] + 0.2, 0.5) });
  const r = 46, x = 270, y = onGround(GY, r), go = TT >= when('copied');
  const ang = go ? lerp(-0.1, 1.1, 0.5 + 0.5 * Math.sin(TT * 9)) : 0.6;
  person(x, y, r, { key: 'hero', mood: go ? 'angry' : 'calm', look: [1, 0], arms: [-1.2, ang] });
  mallet(hand(x, y, r, ang, 1), [Math.cos(ang + 0.5), -Math.sin(ang + 0.5)], 70, 'km');
  bobo(510, GY, 95, rock(go, 1), 'bb6');
  stamp('COPIED', 760, 640, when('copied'), -0.1, 'scp');
  speech(110, 600, 340, 130, ['"Sock him!"'], [270, 960], ev(when('words'), 0.3), 'ks', { face: 'marker', size: 54, col: SK.red });
  if (TT >= when('punches')) handLetter('same punches', 770, 860, 44, { col: SK.ink, key: 'sp', reveal: ev(when('punches'), 0.3) });
  if (TT >= when('words')) handLetter('same words', 770, 940, 44, { col: SK.ink, key: 'sw', reveal: ev(when('words'), 0.3) });
  pageTag('the result');
  say([[S[5], ['72 children', 'took part.'], [[0, '72 children']]], [when('the', 1), ['those who saw it', 'copied it...'], [[1, 'copied']]],
       [when('often'), ['...the exact punches', 'and exact words.'], [[0, 'exact']]]], S[5]);
},
// ---- 7. calm adult or none: far less -------------------------------------------------------------
() => {
  sketchPage({ grid: 'dots' });
  handLetter('aggression', 540, 500, 60, { face: 'marker', col: SK.ink, key: 'agg', reveal: ev(S[6], 0.4) });
  const base = 1120;
  gline([[110, base], [960 - 30, base]], { key: 'ax', w: 5, part: ev(S[6], 0.4) });
  [[230, 1, 'saw attack', SK.red, S[6]], [540, 0.3, 'calm adult', '#8fa7c2', when('calm')], [830, 0.35, 'no adult', '#8fa7c2', when('no')]].forEach(([x, h, lab, col, t], i) => {
    if (TT < t - 0.1) return;
    const k = EZ.io(ev(t, 0.6)), top = base - 480 * h * k, P = [[x - 80, base], [x - 80, top], [x + 80, top], [x + 80, base]];
    scribbleFill(P, col, { key: 'bar' + i, gap: 14, w: 4, base: 0.25 });
    gline(P, { key: 'baro' + i, w: 5 });
    handLetter(lab, x, base + 60, 40, { col: SK.ink, key: 'bl' + i, reveal: ev(t, 0.3) });
  });
  if (TT >= when('less')) handLetter('far less', 690, 860, 56, { face: 'marker', col: SK.green, key: 'fl', reveal: ev(when('less') - 0.3, 0.4) });
  pageTag('the others');
  say([[S[6], ['a calm adult,', 'or no adult at all?'], [[0, 'calm']]], [when('were'), ['far less', 'aggressive.'], [[0, 'far less']]]], S[6]);
},
// ---- 8. just by watching --------------------------------------------------------------------------
() => {
  sketchPage({ grid: 'ruled' });
  [['rewards', 'rewarded', 460], ['told to hit', 'told', 560]].forEach(([s, wd, y], i) => {
    if (TT < when(wd) - 0.2) return;
    const [x0, x1] = handLetter(s, 540, y, 58, { face: 'marker', col: SK.ink, key: 'no' + i, reveal: ev(when(wd) - 0.2, 0.4) });
    gline([[x0 - 10, y - 18], [x1 + 10, y - 22]], { key: 'x' + i, w: 7, col: SK.red, second: false, part: ev(when(wd) + 0.4, 0.25) });
  });
  if (TT >= when('learned') - 0.2) {
    const p = ev(when('learned') - 0.2, 0.5), EY = [...arcPts(540, 1010, 260, Math.PI * 1.22, Math.PI * 1.78, 14), ...arcPts(540, 700, 260, Math.PI * 0.22, Math.PI * 0.78, 14)];
    gfill(EY, '#fffdf6', { key: 'eyf', off: [5, 5], a: clamp(p) });
    gline(EY, { closed: true, key: 'ey', w: 6, part: p });
    if (p >= 1) { const IR = loopPts(540, 855, 70, 70, 0.04); gfill(IR, '#8fa7c2', { key: 'iris', off: [0, 0] }); gline(IR, { key: 'iro', w: 5 });
      ctx.fillStyle = SK.ink; ctx.beginPath(); ctx.arc(540, 855, 30, 0, TAU); ctx.fill(); }
  }
  if (TT >= when('watching', 2)) handLetter('just by watching', 540, 1150, 64, { face: 'marker', col: SK.green, key: 'jbw', reveal: ev(when('watching', 2), 0.4) });
  pageTag('the twist');
  say([[S[7], ['nobody rewarded them.'], [[0, 'rewarded']]], [when('nobody', 3), ['nobody told', 'them to hit.'], [[1, 'hit.']]],
       [when('learned'), ['they learned it', 'just by watching.'], [[1, 'watching.']]]], S[7]);
},
// ---- 9. who is watching you? ---------------------------------------------------------------------
() => {
  sketchPage({ grid: 'dots' }); ground('g9', GY);
  const pose = TT >= when('teaching') ? [0.5, -1.2] : [-1.2, -1.2];
  person(380, onGround(GY, 70), 70, { key: 'you9', mood: TT >= when('who') ? 'puzzled' : 'calm', look: [1, 0.4], arms: pose });
  person(680, onGround(GY, 40), 40, { key: 'kid9', shirt: '#7fa77a', hair: 'mop', hairCol: '#7a5a3c', mood: 'wow', look: [-1, -0.6], arms: TT >= when('teaching') + 0.4 ? [-1.2, 0.5] : [-1.2, -1.2] });
  if (TT >= when('teaching') && TT < when('who')) handLetter('they copy you', 600, 620, 56, { face: 'marker', col: SK.ink, key: 'cpy', reveal: ev(when('teaching'), 0.4) });
  speech(150, 440, 780, 260, ['who is', 'watching YOU?'], [600, 900], ev(when('who'), 0.5), 'q9', { face: 'marker', size: 70 });
  pageTag('your turn');
  say([[S[8], ["they're not just", 'acting.'], [[1, 'acting.']]], [when('teaching'), ["they're teaching."], [[0, 'teaching.']]],
       [when('who'), ['who is watching you?'], [[0, 'you?']]], [when('what', 2), ['and what are they', 'learning?'], [[1, 'learning?']]]], S[8]);
},
];
