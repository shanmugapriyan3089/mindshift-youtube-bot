// =====================================================================
//  TIMELINE — generic, built from src/timing.js (S, DURATION, SHOT_NAMES) and the piece's SCENES array.
// =====================================================================
const NFRAMES = Math.round(DURATION * FPS);
const LOOP_T = NFRAMES / FPS;
const ERA_LIST = S.slice(0, -1).map((t0, i) => [t0, S[i + 1], () => SCENES[i]()]);
const SHOTS = ERA_LIST.map(([t0, t1], i) => [SHOT_NAMES[i] ?? 'scene' + (i + 1), i, t0, t1, SHOT_NAMES[i] ?? 'scene' + (i + 1)]);
const n4 = Math.max(1, Math.floor((S.length - 1) / 4));
const TIMELINE = {
  width: W, height: H, fps: FPS, bpm: BPM, duration: DURATION, frames: NFRAMES, loop: LOOP_T, safe: SAFE,
  format: 'voice-led',
  shots: SHOTS.map(([key, era, t0, t1, title], i) => ({ id: i + 1, key, era, t0, t1, title })),
  cuts: S.slice(1, -1), morphs: [], cues: {},
  acts: [
    { name: '1 Setup', role: 'build', t0: 0, t1: S[n4] },
    { name: '2 Journey', role: 'journey', t0: S[n4], t1: S[2 * n4] },
    { name: '3 Twist', role: 'peak', t0: S[2 * n4], t1: S[S.length - 2] },
    { name: '4 You', role: 'gift', t0: S[S.length - 2], t1: DURATION },
  ],
  board: SHOTS.map(([key, , t0, t1]) => ({ t: (t0 + t1) / 2, title: key, sound: '', next: '' })),
  narration: [],
};
window.TIMELINE = TIMELINE;
