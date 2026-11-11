// =====================================================================
//  CAMERA — generic: a slow lean-in on every scene; optional PUNCHES = [[t0, t1, zoom, [x, y]], ...] from scenes.js.
// =====================================================================
const ERA_BG = ERA_LIST.map(() => '#f2ead8');
function pieceCam(era, t) {
  const [t0, t1] = ERA_LIST[era];
  if (typeof PUNCHES !== 'undefined') for (const [a, b, z, p] of PUNCHES) if (t >= a && t < b) return camOf({ z, p, to: p });
  return push(t, t0, t1, { z: 1.06, p: [540, 950], to: [540, 950] });
}
const BRIDGES = [];
