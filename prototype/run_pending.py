"""
Make + schedule the next pending story Short (used by the daily GitHub Action).

A story is pending when prototype/sketch_<slug>/ has story.json and src/scenes.js but no upload.json.
Processes ONE story per run (the free TTS quota is ~10 lines/day; a story is ~9 lines).
Order: the order of prototype/topics.json "queue", then any other pending folders alphabetically.
Exit code 0 also when nothing is pending.
"""
import os, sys, json, glob, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROTO = os.path.join(ROOT, "prototype")


def pending():
    order = []
    tq = os.path.join(PROTO, "topics.json")
    if os.path.exists(tq):
        order = [t["slug"] for t in json.load(open(tq, encoding="utf-8")).get("queue", [])]
    folders = sorted(glob.glob(os.path.join(PROTO, "sketch_*")))
    ready = [f for f in folders
             if os.path.exists(os.path.join(f, "story.json")) and os.path.exists(os.path.join(f, "src", "scenes.js"))
             and not os.path.exists(os.path.join(f, "upload.json")) and not os.path.exists(os.path.join(f, "failed.json"))]
    rank = {s: i for i, s in enumerate(order)}
    return sorted(ready, key=lambda f: (rank.get(os.path.basename(f).replace("sketch_", ""), 10**6), f))


def main():
    todo = pending()
    print(f"pending stories: {[os.path.basename(f) for f in todo]}")
    if not todo:
        return
    piece = todo[0]
    print(f"making: {os.path.basename(piece)}")
    # real timings replace any provisional ones made without the TTS key
    tj = os.path.join(piece, "timing.json")
    if os.path.exists(tj) and json.load(open(tj)).get("estimated"):
        os.remove(tj); os.remove(os.path.join(piece, "src", "timing.js"))
    r = subprocess.run([sys.executable, "-u", os.path.join(PROTO, "make_short.py"), piece, "--upload"],
                       capture_output=True, text=True)
    print(r.stdout[-6000:]); print(r.stderr[-3000:])
    if r.returncode != 0:
        quota = "quota" in (r.stdout + r.stderr).lower()
        if not quota:   # park the story so tomorrow's run moves on; the Sunday writer repairs it
            json.dump({"reason": (r.stdout + r.stderr)[-1500:]}, open(os.path.join(piece, "failed.json"), "w"), indent=1)
        sys.exit(r.returncode)


if __name__ == "__main__":
    main()
