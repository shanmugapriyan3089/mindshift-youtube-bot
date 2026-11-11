  // SCORE BODY — Prisoner 8612 (inside buildScore(); see kit/score-head.js).
  // Kept deliberately quiet and steady under the voice (-26 dB): no pencil scratches, blips or hiss,
  // so nothing pops up in the pauses between sentences. Only a soft bed and a low thump on each stamp.
  to = 'm';
  pad(0.0, S[3] + 0.5, ['D3', 'A3', 'E4'], 0.03, { type: 'triangle', cut: 700, att: 2.0, rel: 1.0 });
  pad(S[3], S[6] + 0.5, ['D2', 'A2', 'F3'], 0.03, { cut: 600, att: 1.5, rel: 1.0 });
  pad(S[6], S[8] + 0.5, ['F2', 'C4', 'A3'], 0.03, { cut: 650, att: 1.5, rel: 1.0 });
  pad(S[8], DURATION, ['D2', 'A2', 'D3', 'E4'], 0.035, { cut: 800, att: 1.5, rel: 2.0 });
  to = 's';
  [13.08, 25.42, 51.56, 61.78].forEach((t) => sub(t, 0.35));   // arrested, 8612, shut down, coached — all land under speech
