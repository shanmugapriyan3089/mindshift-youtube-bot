  // SCORE BODY — generic (sketch_kit). A quiet, steady bed under the voice; no effects in the pauses.
  // Optional HITS = [t, ...] from scenes.js: a low thump on each big word (they land under speech).
  to = 'm';
  const q = Math.floor((S.length - 1) / 3), CH = [['D3', 'A3', 'E4'], ['D2', 'A2', 'F3'], ['F2', 'C4', 'A3'], ['D2', 'A2', 'D3', 'E4']];
  const marks = [0, S[q], S[2 * q], S[S.length - 2], DURATION];
  for (let i = 0; i < 4; i++) pad(marks[i], Math.min(DURATION, marks[i + 1] + 0.5), CH[i], i === 3 ? 0.035 : 0.03, { type: i ? undefined : 'triangle', cut: 700, att: 1.5, rel: i === 3 ? 2.0 : 1.0 });
  to = 's';
  if (typeof HITS !== 'undefined') HITS.forEach((t) => sub(t, 0.35));
