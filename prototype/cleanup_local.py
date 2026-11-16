"""
Free disk space on THIS machine: delete the rendered media of every video that is already public on YouTube.

  python prototype/cleanup_local.py            # delete
  python prototype/cleanup_local.py --dry-run  # only list

A story counts as released when its upload.json "publish_at" has passed. Kept: story.json, scenes, timing, upload.json, instagram.json
(everything tracked in git). Deleted: renders/, frames/, voice/, look.png, index.html, review/, SHORT_*.mp4 / LONG_*.mp4 / LONGTEASER_*.mp4.
The videos themselves live on YouTube, Instagram and the GitHub Release, and the cloud pipeline re-renders from the story files if ever needed.
"""
import os, sys, json, glob, shutil, datetime as dt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROTO = os.path.join(ROOT, "prototype")
DRY = "--dry-run" in sys.argv


def size(path):
    if os.path.isfile(path): return os.path.getsize(path)
    return sum(os.path.getsize(os.path.join(d, f)) for d, _, fs in os.walk(path) for f in fs)


def main():
    now = dt.datetime.now(dt.timezone.utc)
    freed = 0
    for up in sorted(glob.glob(os.path.join(PROTO, "*_*", "upload.json"))):
        folder = os.path.dirname(up); name = os.path.basename(folder)
        if not (name.startswith("sketch_") or name.startswith("long_")): continue
        p = json.load(open(up)).get("publish_at")
        if not p or dt.datetime.fromisoformat(p.replace("Z", "+00:00")) > now:
            print(f"keep   {name} (not public yet: {p})"); continue
        targets = [os.path.join(folder, x) for x in ("renders", "frames", "voice", "review", "look.png", "index.html", "thumbnail.jpg")]
        targets += [os.path.join(PROTO, f"{pre}_{name}.mp4") for pre in ("SHORT", "LONG", "LONGTEASER")]
        for t in targets:
            if os.path.exists(t):
                n = size(t); freed += n
                print(f"{'would delete' if DRY else 'delete'} {os.path.relpath(t, ROOT)} ({n / 1e6:.0f} MB)")
                if not DRY: shutil.rmtree(t) if os.path.isdir(t) else os.remove(t)
    print(f"{'would free' if DRY else 'freed'} {freed / 1e9:.2f} GB")


if __name__ == "__main__":
    main()
