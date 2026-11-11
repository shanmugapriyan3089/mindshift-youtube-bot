// =====================================================================
//  ERAS, CAMERAS, BRIDGES — The Shock Machine. Hard cuts; a slow lean-in per scene, a punch-in on the big moments.
// =====================================================================
const ERA_BG = ERA_LIST.map(() => '#f2ead8');
function pieceCam(era, t) {
  const [t0, t1] = ERA_LIST[era];
  if (era === 5 && t >= 44.86) return camOf({ z: 1.06, p: [540, 900], to: [540, 900] });  // "65 percent"
  return push(t, t0, t1, { z: 1.06, p: [540, 950], to: [540, 950] });
}
const BRIDGES = [];
