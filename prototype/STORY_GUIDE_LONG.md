# Long videos — writer's guide

One long video per week (8-10 minutes, 16:9) for the MindShift Productivity channel. **Template: `prototype/long_stanford/story.json`.**
You write ONE file: `prototype/long_<slug>/story.json`. No JavaScript. The scenes are data; `prototype/sketch_kit/long.js` draws them.
A weekly GitHub Action (`.github/workflows/long_video.yml`, Saturday 17:00 IST) makes the voice, renders the video, builds a
thumbnail and chapters, and schedules it for Sunday 18:00 IST. If it fails it writes `failed.json` — read the reason, fix `story.json`, delete `failed.json`.

## The format
- Same niche as the Shorts: a real psychology experiment or case, told in the **second person** ("You answer an ad…").
- 8-10 minutes = **1,250-1,500 spoken words** in **38-50 scenes** (about 25-35 words, 8-14 seconds, each).
- Structure: hook in the first scene (the claim + that the real story is stranger) → the setup → the experiment, day by day / step by step →
  the shocking result (a number) → **the twist / what the archives or later studies show** → what it means → a question to the viewer
  and a "subscribe for the next experiment" line. Facts only from `prototype/topics.json` or verified by web search; hedge numbers; list sources.
- The long video is the FULL version of a topic that may also exist as a Short. Pick topics that have real depth (a timeline, a controversy).

## story.json
```json
{
  "title": "…", "kind": "long",
  "youtube": {"title": "≤ 100 chars: the question/claim + (Full Story)",
              "description": "hook paragraph, summary, question to the viewer, then the literal line {chapters}, then Sources: and hashtags",
              "tags": ["…10 tags…", "mindshift productivity"]},
  "sources": ["…"],
  "thumbnail": {"text": "3-4 WORDS IN CAPS", "scene": 3},
  "scenes": [ {"say": "narration for this scene", ...visuals...}, … ]
}
```
`thumbnail.scene` = the index of a scene with a person's face (the video frame behind the big text).
Chapters are built automatically from the scenes' `"tag"` fields (≥ 3 tags, the first at ≥ 12 s): give a tag to the first scene of each part.

## Narration (`say`)
Plain spoken text only (the TTS reads everything aloud; never put directions in it). Numbers as words ("nineteen seventy-one", "twenty-four").
Short sentences. Each scene's `say` is what is spoken while that scene is on screen; all scenes together are one continuous script.

## Scene types (every scene may also have `tag`, `grid` dots|ruled|plain, `tint` colour, `props`)
Layout area: 1920×1080; the bottom ~130 px is the live caption. Keep text short — it is drawn big.
- **person** (default): `who` = one person or a list of up to 5: `{mood: calm|happy|wow|puzzled|scared|angry|scream, outfit: tee|smock|coat, shirt: terra|blue|green|khaki|grey|red|yellow|white, hair: mop|short, glasses, shades, num (prisoner number on smock), tag (word on shirt), name (label under feet), say (speech bubble, ≤ 2 short lines), arms: [left,right] (0 out, + up, − down), shake, baton, flip: {at: "word", mood: "scared", arms: […]}}`.
  One person + `text` (list of ≤ 5 short lines, each ≤ 24 chars, written on one after another; `punch: true` makes the last line big with a red underline; `side: "left"` puts the person left and text right, `"right"` the reverse).
  Several people stand evenly spaced (no `text`). Use `name` labels for roles. The hero is `{"shirt": "terra"}`.
- **title**: `text` (≤ 3 lines), `sub`, optional `who`.
- **stat**: `big` ("24", "65%"), `label` (≤ 2 lines), `filled` (0-100: how many of the 70 little people turn coloured), `col: "red"`.
- **list**: `heading`, `items` (3-5, each ≤ 30 chars) — appear one by one.
- **quote**: `quote` (≤ 4 lines), `who` (attribution).
- **versus**: `left`/`right` = `{head, items[≤3]}`.
- **timeline**: `items` = `[{when: "Day 1", what: "≤ 32 chars"}, …]` (≤ 5).
- **bars**: `heading`, `unit` ("%"), `bars` = `[{label, value, hot}]` (≤ 6).
- **stamp**: `stamp` (a big red word, ≤ 8 chars), `text` (≤ 2 lines), `at: "word"` (spoken word that triggers the stamp).
- `props`: `clock | bulb | question | exclaim | dollar | eye | book | lock` — small doodles that pop in (`propAt: ["word"]`).
- Anything can appear **on a spoken word**: use `"at": "word"` (a plain word, no digits) on list/timeline items, bubbles, stamps, `bigAt`, `fillAt`.
  Without `at`, things appear evenly across the scene.
- Vary the scene types: never more than two `person` scenes in a row; use stats, lists, quotes, timelines, versus and stamps to carry facts.

## Check before you commit
```
python prototype/make_long.py prototype/long_<slug> --estimate --stills      # no TTS key needed; builds + a contact sheet
```
then render a few stills at readable size and LOOK at them with the Read tool:
`node tools/animate/tools/still.mjs prototype/long_<slug> <t1,t2,t3> prototype/long_<slug>/s.png --scale 0.45`
(times from `prototype/long_<slug>/timing.json` → "S"). Fix anything cut off, overlapping or unreadable.
Delete the provisional files (timing.json, src/, index.html, look.png, s*.png, piece.json) before committing — only `story.json` is committed.
