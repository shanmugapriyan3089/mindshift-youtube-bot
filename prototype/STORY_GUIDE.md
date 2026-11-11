# Story Shorts — writer's guide

How to write one psychology story Short for the MindShift Productivity channel. The weekly cloud writer and
any human/agent session follow this. **Template to copy: `prototype/sketch_asch/`.**

## The format (do not change)
- Niche: real psychology experiments and cases, told in the **second person** ("You answer an ad…").
- Style: hand-drawn **sketchbook** (cth9191/animate skill, copied in `tools/animate`), one doodle *person* per role
  (`person()` in `prototype/sketch_kit/people.js`). Never use the kit's ball-with-asterisk `doodleHero`.
- 9 scenes, ~55–75 s of narration, vertical 1080×1920. Every object and caption appears **on the word that names it**.
- Structure: hook in the first sentence → the setup → the shocking moment → the result (a number) → **the twist**
  (what most people don't know) → a closing question to the viewer ("Would YOU…?").
- Facts: only use facts from `prototype/topics.json` or ones you verify with a web search. Hedge numbers
  ("about", "far fewer") when sources differ. List every source in `story.json` → `sources` and in the description.

## Files you write (only these two)
`prototype/sketch_<slug>/story.json`
```json
{
  "title": "…",
  "youtube": {"title": "≤ 70 chars, a question or hook, ends with #Shorts",
              "description": "2-line hook, 1-line summary, 'Would YOU…? Tell me in the comments.', Sources:, hashtags",
              "tags": ["…10 tags…", "mindshift productivity"]},
  "sources": ["…"],
  "shots": ["9 short scene names"],
  "lines": ["9 narration lines, one per scene"]
}
```
`prototype/sketch_<slug>/src/scenes.js` → `const SCENES = [ () => { … }, … 9 … ];` (+ optional `const HITS = [when('word'), …]`
for a low thump on big words, `const PUNCHES = [[t0, t1, zoom, [x, y]]]` for a camera punch-in).

## Narration lines (TTS)
- Plain spoken text only. **Never** put style instructions in a line (the TTS reads them aloud).
- Write numbers in words when spoken ("four hundred and fifty", "Nineteen fifty-one").
- 10–25 words per line. Short sentences. ~153 words/min.

## Timing: `when('word', n)`
- `when('switch')` = start time (s) of the first spoken "switch"; `when('the', 3)` = the third "the".
- The real timings come from a speech-to-text pass on the generated voice, which writes **numbers as digits**
  ("1951", "65 %", "$4"). So only call `when()` on **plain words with no digits/hyphens** — anchor numbers to a
  neighbouring word (`when('percent')`, `when('volts')`). Count repeats carefully (`n`).
- Never name a variable `when` or `W` (W is the canvas width). Scene start times: `S[i]`.
- `say([[t, ['line 1', 'line 2'], [[lineIdx, 'word to highlight']]], …], S[i])` — captions follow the narration
  phrase by phrase; ≤ 20 characters per caption line, max 2 lines; default y 1375.

## Layout rules (learned the hard way)
- Canvas 1080×1920. **Safe area x 60–940, y 250–1500** (YouTube's buttons cover the right edge and the bottom).
  Keep labels, bubbles and machines inside it; right-edge objects end before x ≈ 920.
- Ground line `GY = 1235`; stand people with `person(x, onGround(GY, r), r, {...})` (height ≈ 4.6 r).
  Main character r 60–85; groups of 7–8 people r ≈ 42 spaced ~115 px.
- Page tag (top-left) via `pageTag('two words')`; captions at y 1375; nothing else below y ≈ 1300.
- Only one speech bubble per position at a time (hide the previous one when the next appears) — overlapping text fails review.
- Hero = terracotta t-shirt (`SK.terra`); others blue/green/khaki; red (`SK.red`) only for stamps/danger; yellow
  highlighter for one word.
- No camera punch-ins on scenes with text near the edges (zoom pushes it off-frame).

## Kit API (prototype/sketch_kit/people.js + the sketchbook style kit)
- `person(x, y, r, {key, mood: calm|happy|wow|puzzled|scared|angry|scream, outfit: tee|smock|coat, shirt, hair: mop|short,
  hairCol, glasses, shades, tag:'TEACHER', num, look:[x,y], arms:[left,right] (0 = out, + up, − down), shake, baton})`
- `speech(x, y, w, h, ['line'], [tailX, tailY], reveal0to1, key, {face:'marker', size, col})`
- `iconPeople(x0, y0, cols, rows, gap, nFill, fill0to1, key, col)` — stats like "3 out of 4"
- `stamp('TEXT', x, y, t, rot, key)` — red rubber stamp landing at time t
- `cellBars(...)`, `drawPencil(points, t0, d)`, `ground(key, y)`, `onGround(gy, r)`, `say(...)`
- Style kit: `sketchPage({grid:'dots'|'ruled'})`, `gline`, `gpencil`, `gfill`, `ghatch`, `gclip`, `scribbleFill`,
  `sketchBox`, `loopPts`, `arcPts`, `handLetter(str, x, y, size, {face:'marker'|'hand', col, reveal, key})`,
  `underline`, `checkMark`, `sweat`, `pencilTool`, `graphiteScribble`, `inkStamp`; timing helpers `ev(t, d)` (0→1),
  `seg`, `clamp`, `lerp`, `EZ.io`; current time `TT`, boil counter `B`. Colours `SK.ink/graph/terra/red/hilite/green/paper`.
  Read `tools/animate/styles/sketchbook/STYLE.md` once.

## Check before you commit (no TTS key needed)
```
python prototype/estimate_timing.py prototype/sketch_<slug>      # provisional timings from the script
node tools/animate/tools/build.mjs prototype/sketch_<slug>       # must print "syntax ok"
# if Playwright/Chromium can be installed (cd tools/animate && npm ci && npx playwright install chromium):
node tools/animate/tools/still.mjs prototype/sketch_<slug> <9 times near each scene's end> prototype/sketch_<slug>/look.png --scale 0.3
```
Look at the stills: everyone on the ground, nothing cut off, no text over text, captions readable.
The daily GitHub Action (`.github/workflows/story_shorts.yml`) makes the real voice, re-checks every `when()`,
renders, runs the text review and schedules the upload. If it fails, it writes `failed.json` in the folder — read the
reason, fix the scenes, delete `failed.json`, commit.
