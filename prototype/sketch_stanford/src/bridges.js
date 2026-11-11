// =====================================================================
//  ERAS, CAMERAS, BRIDGES — Prisoner 8612 (read by kit/morph.js). Hard cuts between eras (no bridges).
// =====================================================================
const ERA_BG = ERA_LIST.map(() => '#f2ead8');
function pieceCam(era, t) {
  const [t0, t1] = ERA_LIST[era];
  if (era === 4) {   // the riot: hand-held shake on 2s
    const jx = 10 * Math.sin(B * 2.3), jy = 8 * Math.cos(B * 1.9);
    return camOf({ z: 1.06, p: [540 + jx, 960 + jy], to: [540, 960] });
  }
  if (era === 2 && t >= CUE.n8612) return camOf({ z: 1.12, p: [540, 900], to: [540, 900] });   // punch in on 8612
  return push(t, t0, t1, { z: 1.07, p: [540, 950], to: [540, 950] });                          // slow lean-in each scene
}
const BRIDGES = [];
