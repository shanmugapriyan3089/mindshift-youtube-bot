"""
One command from story to scheduled Short.

  python prototype/make_short.py prototype/sketch_asch            # voice -> build -> stills -> export -> checks
  python prototype/make_short.py prototype/sketch_asch --upload   # ...then upload to the next free slot

A story folder needs only:
  story.json      {"youtube": {...}, "shots": [...], "lines": [...]}   (script, one line per scene)
  src/scenes.js   const SCENES = [ () => {...}, ... ]                    (drawings; times via W('word'))
Everything else (head, timeline, camera, score, kit) comes from prototype/sketch_kit.

Posting slots: Mon / Wed / Fri at 19:00 IST, the first free one after the latest scheduled Short.
"""
import os, sys, json, glob, shutil, subprocess, datetime as dt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL = os.environ.get("ANIMATE_SKILL", os.path.join(ROOT, "tools", "animate"))
KIT = "../sketch_kit"
BUILD = ["../sketch_kit/head.html", "src/timing.js", "../sketch_kit/timeline.js", "kit/core.js", "style",
         "../sketch_kit/people.js", "src/scenes.js", "../sketch_kit/bridges.js", "kit/morph.js", "kit/board.js",
         "kit/score-head.js", "../sketch_kit/score.js", "kit/score-tail.js"]
SLOT_DAYS = (0, 2, 4)          # Mon, Wed, Fri
SLOT_UTC = dt.time(13, 30)     # 19:00 IST


def run(cmd, **kw):
    print("  $", " ".join(str(c) for c in cmd)[:140])
    r = subprocess.run(cmd, text=True, capture_output=True, **kw)
    if r.returncode != 0:
        print(r.stdout[-2000:], r.stderr[-2000:]); sys.exit(f"step failed: {cmd[0]} {cmd[1] if len(cmd) > 1 else ''}")
    return r.stdout


def scaffold(piece):
    pj = os.path.join(piece, "piece.json")
    if os.path.exists(pj):
        meta = json.load(open(pj))
    else:
        story = json.load(open(os.path.join(piece, "story.json"), encoding="utf-8"))
        meta = {"name": os.path.basename(piece), "title": story.get("title", ""),
                "format": {"width": 1080, "height": 1920, "fps": 24, "bpm": 120, "duration": 60.0, "frames": 1440},
                "storyFormat": "fixed-hero journey (hard cuts, voice-led)", "style": "sketchbook",
                "voice": {"file": "voice/voice.wav", "music": -26, "gain": 0},
                "review": {"safe": {"top": 240, "bottom": 420, "right": 140}, "refs": {}}}
    meta["build"] = BUILD
    meta.pop("scenes", None)
    json.dump(meta, open(pj, "w"), indent=2)


def next_slot():
    taken = []
    for f in glob.glob(os.path.join(ROOT, "prototype", "*", "upload.json")):
        p = json.load(open(f)).get("publish_at")
        if p: taken.append(dt.datetime.fromisoformat(p.replace("Z", "+00:00")))
    after = max([dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=2)] + taken)
    d = after.date()
    while True:
        cand = dt.datetime.combine(d, SLOT_UTC, tzinfo=dt.timezone.utc)
        if d.weekday() in SLOT_DAYS and cand > after:
            return cand.strftime("%Y-%m-%dT%H:%M:%SZ")
        d += dt.timedelta(days=1)


def main(piece, upload=False):
    piece = os.path.abspath(piece)
    scaffold(piece)
    if not os.path.exists(os.path.join(piece, "src", "timing.js")):
        run([sys.executable, os.path.join(ROOT, "prototype", "make_voice.py"), piece])
    # every when('word', n) in the scenes must exist in the narration
    check = ("const fs=require('fs');eval(fs.readFileSync(process.argv[1],'utf8').replace(/^const /gm,'var '));"
             "const src=fs.readFileSync(process.argv[2],'utf8');let bad=[];"
             "for(const m of src.matchAll(/when\\('([^']+)'(?:,\\s*(\\d+))?\\)/g)){try{when(m[1],m[2]?+m[2]:1)}catch(e){bad.push(m[0])}}"
             "if(bad.length){console.log('missing words: '+bad.join(' '));process.exit(1)}")
    run(["node", "-e", check, os.path.join(piece, "src", "timing.js"), os.path.join(piece, "src", "scenes.js")])
    node = lambda tool, *a: run(["node", os.path.join(SKILL, "tools", tool), piece, *a])
    node("build.mjs")
    S = json.load(open(os.path.join(piece, "timing.json")))["S"]
    mids = ",".join(f"{(a + b) / 2:.2f}" for a, b in zip(S[:-1], S[1:]))
    node("still.mjs", mids, os.path.join(piece, "look.png"), "--scale", "0.25")
    node("export.mjs", "--share")
    review = node("review.mjs")
    text = [l for l in review.splitlines() if l.startswith("text:")]
    print("  " + (text[0] if text else "text: (no verdict)"))
    if text and "FAIL" in text[0]:
        sys.exit("text check failed — fix the overlaps listed by review.mjs before uploading")
    out = os.path.join(ROOT, "prototype", f"SHORT_{os.path.basename(piece)}.mp4")
    shutil.copy(os.path.join(piece, "renders", "share.mp4"), out)
    print(f"  video: {out}\n  contact sheet: {os.path.join(piece, 'look.png')}")
    if upload:
        if os.path.exists(os.path.join(piece, "upload.json")):
            sys.exit("already uploaded (upload.json exists)")
        slot = next_slot()
        print(f"  uploading, scheduled for {slot}")
        print(run([sys.executable, os.path.join(ROOT, "prototype", "upload_short.py"), piece, slot], cwd=ROOT))


if __name__ == "__main__":
    main(sys.argv[1], "--upload" in sys.argv)
