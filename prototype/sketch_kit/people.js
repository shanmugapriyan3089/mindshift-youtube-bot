// =====================================================================
//  SKETCH KIT — shared drawing helpers for the psychology story Shorts (sketchbook style, animate skill).
//  person(): doodle human with face, hair, mood brows/mouth, outfit. say(): captions that follow the voice.
//  Loaded before each piece's own scenes via piece.json "scenes": ["../sketch_kit/people.js", "src/scenes.js"].
// =====================================================================

const SKIN = '#f6dcc3', HAIR = '#5a4232', KHAKI = '#c9b27c', SMOCK = '#ebe1c6', COAT = '#cfd2d6';

// ---- a doodle person: face, 70s hair, mood-driven brows + mouth, outfit -----------------------
// (x, y) = head centre, r = head radius; total height ≈ 4.6 r (feet at y + 3.6 r)
function person(x, y, r, o = {}) {
  const key = o.key ?? 'p', mood = o.mood ?? 'calm', lw = Math.max(3, r * 0.08), outfit = o.outfit ?? 'tee';
  const shirt = o.shirt ?? (outfit === 'smock' ? SMOCK : SK.terra);
  ctx.save(); ctx.translate(x + (o.shake ? o.shake * Math.sin(B * 2.7) : 0), y); ctx.rotate(o.rot ?? 0);
  const hipY = r * 2.7, footY = r * 3.6;
  // legs + shoes
  for (const s of [-1, 1]) {
    gline([[s * r * 0.26, hipY - r * 0.1], [s * r * 0.36, footY]], { w: lw * 1.1, key: key + 'lg' + s, amp: 0.6, second: false, step: 8 });
    gline([[s * r * 0.36, footY], [s * r * 0.62, footY + 2]], { w: lw * 1.5, key: key + 'sh' + s, amp: 0.4, second: false, step: 6 });
  }
  // arms (angle 0 = straight out, + up, - down)
  for (const [i, s] of [[0, -1], [1, 1]]) {
    const ang = o.arms?.[i] ?? -1.2, sh = [s * r * 0.62, r * 1.3], L = r * 1.45;
    const el = [sh[0] + s * L * 0.5 * Math.cos(ang * 0.8), sh[1] - L * 0.5 * Math.sin(ang * 0.8)];
    const hd = [sh[0] + s * L * Math.cos(ang), sh[1] - L * Math.sin(ang)];
    gline([sh, el, hd], { w: lw * 1.1, key: key + 'ar' + s, amp: 0.7, second: false, step: 8 });
    gfill(loopPts(hd[0], hd[1], r * 0.14, r * 0.14, 0), SKIN, { key: key + 'hf' + s, off: [0, 0] });
    gline(loopPts(hd[0], hd[1], r * 0.14, r * 0.14, 0.1), { w: lw * 0.8, key: key + 'hd' + s, amp: 0.4, second: false, step: 5 });
    if (o.baton && s === 1) gline([[hd[0] - r * 0.1, hd[1] - r * 0.5], [hd[0] + r * 0.2, hd[1] + r * 1.1]], { w: lw * 2.2, key: key + 'bat', part: o.baton });
  }
  // torso
  const T = outfit === 'smock'
    ? [[-r * 0.62, r * 1.08], [r * 0.62, r * 1.08], [r * 0.9, r * 3.05], [-r * 0.9, r * 3.05]]
    : outfit === 'coat'   // long lab coat, to the knees
    ? [[-r * 0.7, r * 1.08], [r * 0.7, r * 1.08], [r * 0.82, r * 3.2], [-r * 0.82, r * 3.2]]
    : [[-r * 0.66, r * 1.08], [r * 0.66, r * 1.08], [r * 0.6, r * 2.72], [-r * 0.6, r * 2.72]];
  gfill(T, outfit === 'coat' ? (o.shirt ?? COAT) : shirt, { off: [r * 0.05, r * 0.04], key: key + 'tf' });
  if (outfit === 'smock') { ctx.save(); gclip(T); ghatch(-r, r, r, r * 3.1, { ang: -0.8, gap: r * 0.18, col: SK.graph, w: 1.6, a: 0.25, key: key + 'th' }); ctx.restore(); }
  gline(T, { closed: true, w: lw, key: key + 'to', amp: 0.6 });
  if (outfit === 'tee') gline([[-r * 0.2, r * 1.08], [0, r * 1.28], [r * 0.2, r * 1.08]], { w: lw * 0.8, key: key + 'nk', second: false });
  if (outfit === 'coat') {   // lapels, button line, a pocket with pens
    gline([[-r * 0.3, r * 1.08], [0, r * 1.7], [r * 0.3, r * 1.08]], { w: lw * 0.9, key: key + 'lap', second: false });
    gline([[0, r * 1.7], [0, r * 3.18]], { w: lw * 0.8, key: key + 'btn', second: false, col: SK.graph });
    gline(sketchBox(r * 0.22, r * 1.9, r * 0.36, r * 0.3, 3), { w: lw * 0.7, key: key + 'pk', second: false });
    gline([[r * 0.3, r * 1.9], [r * 0.3, r * 1.74]], { w: lw * 0.7, key: key + 'pen', second: false, col: SK.red });
  }
  if (o.tag) handLetter(o.tag, 0, r * 2.05, r * 0.3, { face: 'marker', col: SK.ink, key: key + 'tag' + o.tag, reveal: o.tagReveal ?? 1, jit: 0.4 });
  if (o.num) handLetter('8612', 0, r * 2.05, r * 0.62, { face: 'marker', col: SK.ink, key: key + 'num', reveal: o.num, jit: 0.4 });
  // neck + head
  gline([[0, r * 0.98], [0, r * 1.1]], { w: lw, key: key + 'ne', second: false });
  const face = loopPts(0, 0, r, r * 1.06, 0, 0, 40);
  gfill(face, SKIN, { off: [r * 0.04, r * 0.04], key: key + 'ff' });
  gline(loopPts(0, 0, r, r * 1.06, 0.06), { w: lw, key: key + 'fo', amp: 0.6 });
  // hair: a shaggy 70s mop with a fringe (short crop for guards)
  const short = o.hair === 'short';
  const hair = short
    ? [[-r * 1.02, r * 0.0], ...arcPts(0, -r * 0.05, r * 1.06, Math.PI, TAU, 14), [r * 1.02, r * 0.0], [r * 0.7, -r * 0.45], [-r * 0.7, -r * 0.45]]
    : [[-r * 1.12, r * 0.45], ...arcPts(0, -r * 0.05, r * 1.16, Math.PI * 1.0, Math.PI * 2.0, 16), [r * 1.12, r * 0.45], [r * 0.9, r * 0.12],
       [r * 0.62, -r * 0.34], [r * 0.32, -r * 0.18], [r * 0.04, -r * 0.4], [-r * 0.28, -r * 0.2], [-r * 0.6, -r * 0.38], [-r * 0.9, r * 0.12]];
  gfill(hair, o.hairCol ?? HAIR, { off: [0, 0], key: key + 'hrf' });
  gline(hair, { closed: true, w: lw * 0.9, key: key + 'hr', amp: 0.5 });
  // eyes (or sunglasses)
  const [lx, ly] = o.look ?? [0, 0], blink = !['wow', 'scream'].includes(mood) && (B + hash(key)) % 31 === 0;
  for (const s of [-1, 1]) {
    const ex = s * r * 0.36 + lx * r * 0.08, ey = r * 0.16 + ly * r * 0.07;
    if (o.shades) continue;
    if (blink || mood === 'scream') gline([[ex - r * 0.1, ey], [ex + r * 0.1, ey]], { w: lw * 0.9, key: key + 'bl' + s, amp: 0.3, second: false, step: 6 });
    else if (mood === 'happy') gline([[ex - r * 0.1, ey + r * 0.03], [ex, ey - r * 0.06], [ex + r * 0.1, ey + r * 0.03]], { w: lw * 0.9, key: key + 'hp' + s, amp: 0.3, second: false, step: 6 });
    else { ctx.fillStyle = SK.ink; ctx.beginPath(); ctx.ellipse(ex, ey, r * 0.085, r * (mood === 'wow' ? 0.15 : 0.11), 0, 0, TAU); ctx.fill();
           ctx.fillStyle = SK.cream; ctx.beginPath(); ctx.arc(ex - r * 0.025, ey - r * 0.04, r * 0.026, 0, TAU); ctx.fill(); }
  }
  if (o.shades) for (const s of [-1, 1]) {
    const L = loopPts(s * r * 0.38, r * 0.15, r * 0.3, r * 0.2, 0.04);
    gfill(L, SK.ink, { key: key + 'sg' + s, off: [0, 0], a: 0.95 * o.shades });
    gline([[s * r * 0.38 - r * 0.15, r * 0.06 + (B % 2) * 2], [s * r * 0.38 - r * 0.04, r * 0.02]], { w: lw * 0.9, col: '#ffffff', key: key + 'gl' + s, second: false, a: o.shades });
    gline([[-r * 0.1, r * 0.12], [r * 0.1, r * 0.12]], { w: lw * 0.8, key: key + 'sgb', second: false, a: o.shades });
  }
  if (o.glasses) {   // thin round rims over the eyes
    for (const s of [-1, 1]) gline(loopPts(s * r * 0.36, r * 0.16, r * 0.24, r * 0.2, 0.05), { w: lw * 0.7, key: key + 'gr' + s, amp: 0.3, second: false, step: 6 });
    gline([[-r * 0.12, r * 0.12], [r * 0.12, r * 0.12]], { w: lw * 0.7, key: key + 'grb', second: false });
  }
  // brows by mood (inner end raised for scared/sad, lowered for angry)
  const lift = { calm: 0, puzzled: 0, scared: -0.14, angry: 0.14, wow: -0.12, happy: -0.04, scream: -0.16 }[mood] ?? 0;
  const raise = mood === 'wow' ? -0.08 : 0;
  if (!o.shades) for (const s of [-1, 1]) {
    const inner = -r * 0.06 + r * lift + r * raise + (mood === 'puzzled' && s > 0 ? -r * 0.12 : 0);
    gline([[s * r * 0.52, -r * 0.06 + r * raise], [s * r * 0.18, inner]], { w: lw * 0.9, key: key + 'br' + s, amp: 0.3, second: false, step: 6 });
  }
  // nose
  gline([[r * 0.02, r * 0.28], [-r * 0.07, r * 0.42], [r * 0.03, r * 0.45]], { w: lw * 0.7, col: SK.graph, key: key + 'no', amp: 0.3, second: false, step: 5 });
  // mouth by mood
  const my = r * 0.64;
  ctx.fillStyle = SK.ink;
  if (mood === 'wow') { ctx.beginPath(); ctx.ellipse(0, my, r * 0.09, r * 0.12, 0, 0, TAU); ctx.fill(); }
  else if (mood === 'scream') { ctx.beginPath(); ctx.ellipse(0, my + r * 0.04, r * 0.2, r * 0.24, 0, 0, TAU); ctx.fill(); }
  else if (mood === 'happy') { ctx.beginPath(); ctx.moveTo(-r * 0.24, my - r * 0.06); ctx.quadraticCurveTo(0, my + r * 0.28, r * 0.24, my - r * 0.06); ctx.closePath(); ctx.fill(); }
  else if (mood === 'scared') gline([[-r * 0.2, my], [-r * 0.1, my - r * 0.05], [0, my + r * 0.02], [r * 0.1, my - r * 0.05], [r * 0.2, my]], { w: lw * 0.8, key: key + 'm', amp: 0.3, second: false, step: 5 });
  else if (mood === 'angry') gline([[-r * 0.2, my + r * 0.05], [-r * 0.12, my], [r * 0.12, my], [r * 0.2, my + r * 0.05]], { w: lw * 0.9, key: key + 'm', amp: 0.3, second: false, step: 5 });
  else if (mood === 'puzzled') gline([[-r * 0.18, my], [-r * 0.05, my - r * 0.04], [r * 0.08, my + r * 0.03], [r * 0.18, my - r * 0.02]], { w: lw * 0.8, key: key + 'm', amp: 0.4, second: false, step: 5 });
  else gline(arcPts(0, my - r * 0.14, r * 0.18, Math.PI * 0.2, Math.PI * 0.8, 8), { w: lw * 0.8, key: key + 'm', amp: 0.4, second: false, step: 5 });
  ctx.restore();
}

// stand a person on a ground line: feet at gy
const onGround = (gy, r) => gy - 3.6 * r - 6;

// ---- captions follow the narration phrase by phrase ------------------------------------------
// list = [[t, [line1, line2?], [[lineIdx, 'word']]], ...]; each phrase writes on at its word
function say(list, e0, y = 1375) {
  let cur = null;
  for (const p of list) if (TT >= p[0] - 0.2) cur = p;
  if (cur) pageCaption(cur[1], cur[2] ?? [], { y, at: Math.max(0, cur[0] - 0.2 - e0) });
}

// ---- shared bits ----------------------------------------------------------------------------
function cellBars(x0, x1, y0, y1, n, t0, dt, key) {
  for (let i = 0; i < n; i++) gline([[lerp(x0, x1, i / (n - 1)), y0], [lerp(x0, x1, i / (n - 1)) + 2, y1]], { w: 7, key: key + i, part: ev(t0 + i * dt, 0.2), amp: 0.6 });
  gline([[x0 - 20, y0], [x1 + 20, y0 + 4]], { w: 8, key: key + 'top', part: ev(t0, 0.3) });
  gline([[x0 - 20, y1], [x1 + 20, y1 - 4]], { w: 8, key: key + 'bot', part: ev(t0 + n * dt, 0.3) });
}
function drawPencil(P, t0, d) {
  if (TT >= t0 && TT < t0 + d) { const tip = writeEnd(P, ev(t0, d)); pencilTool(tip[0], tip[1], -0.75 + 0.08 * Math.sin(B * 1.7), 1); }
}
function ground(key, y) { gpencil([[110, y + 2], [420, y - 4], [700, y + 4], [960, y - 2]], { key, w: 3, a: 0.75 }); }
function stamp(str, x, y, t, rot, key) { if (TT >= t) { const k = ev(t, 0.15); inkStamp(str, x, y, lerp(1.5, 0.88, k), rot, clamp(k * 2), key); } }


// ---- speech bubble: hand-drawn box with a tail, lines written on ------------------------------
// (x, y) = top-left, tail = [tx, ty] point the tail reaches; reveal 0..1 writes the lines on
function speech(x, y, w, h, lines, tail, reveal, key, o = {}) {
  if (reveal <= 0) return;
  const P = sketchBox(x, y, w, h, 22, 0.03);
  const mx = clamp(tail[0], x + 50, x + w - 50), my = tail[1] > y ? y + h : y;
  const T = [[mx - 26, my], tail, [mx + 26, my]];
  gfill(P, '#fffdf6', { key: key + 'bf', off: [5, 5] });
  gfill(T, '#fffdf6', { key: key + 'tf', off: [0, 0] });
  gline(P, { closed: true, w: 5, key: key + 'b' });
  gline(T, { w: 5, key: key + 't', second: false });
  const size = o.size ?? 54, lh = size * 1.15, y0 = y + h / 2 - (lines.length - 1) * lh / 2 + size * 0.32;
  lines.forEach((ln, i) => handLetter(ln, x + w / 2, y0 + i * lh, size, { face: o.face ?? 'hand', col: o.col ?? SK.ink, key: key + 'l' + i,
                                                                        reveal: clamp(reveal * lines.length - i), jit: 0.6 }));
}

// ---- a grid of little people icons; the first nFill turn colour one by one ------------------------
function iconPeople(x0, y0, cols, rows, gap, nFill, fillPart, key, col = SK.terra) {
  const total = cols * rows, lit = Math.floor(nFill * clamp(fillPart));
  for (let i = 0; i < total; i++) {
    const cx = x0 + (i % cols) * gap, cy = y0 + Math.floor(i / cols) * gap * 1.25, s = gap * 0.3;
    const body = [[cx - s * 0.8, cy + s * 2.3], [cx - s * 0.75, cy + s * 0.9], [cx + s * 0.75, cy + s * 0.9], [cx + s * 0.8, cy + s * 2.3]];
    const head = loopPts(cx, cy, s * 0.55, s * 0.55, 0.06);
    if (i < lit) { gfill(head, col, { key: key + 'h' + i, off: [0, 0] }); gfill(body, col, { key: key + 'b' + i, off: [0, 0] }); }
    gline(head, { w: 2.5, key: key + 'ho' + i, second: false, col: i < lit ? SK.ink : SK.graph });
    gline(body, { w: 2.5, key: key + 'bo' + i, second: false, closed: true, col: i < lit ? SK.ink : SK.graph });
  }
}
