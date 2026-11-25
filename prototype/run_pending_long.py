"""
Make + schedule the next pending LONG video (used by the weekly GitHub Action).

A long video is pending when prototype/long_<slug>/story.json exists but there is no upload.json / failed.json.
One per run. A quota shortage is transient (exit 0, retried next run); any other failure parks the story.
"""
import os, sys, json, glob, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROTO = os.path.join(ROOT, "prototype")


def pending():
    ready = [f for f in sorted(glob.glob(os.path.join(PROTO, "long_*")))
             if os.path.exists(os.path.join(f, "story.json"))
             and not os.path.exists(os.path.join(f, "upload.json")) and not os.path.exists(os.path.join(f, "failed.json"))]
    return ready


def main():
    todo = pending()
    print(f"pending long videos: {[os.path.basename(f) for f in todo]}")
    if not todo:
        return
    piece = todo[0]
    print(f"making: {os.path.basename(piece)}", flush=True)
    r = subprocess.run([sys.executable, "-u", os.path.join(PROTO, "make_long.py"), piece, "--upload"],
                       capture_output=True, encoding="utf-8", errors="replace")
    print((r.stdout or "")[-6000:]); print((r.stderr or "")[-3000:])
    if r.returncode != 0:
        out = (r.stdout or "") + (r.stderr or "")
        if "credits are depleted" in out:   # Gemini billing problem: fail visibly, keep the story queued
            sys.exit("Gemini API key has no credits left: replace GEMINI_API_KEY (or top up), then the next run continues")
        if "quota" in out.lower():
            print("::warning::TTS free quota used up — retrying at the next scheduled run")
            return
        json.dump({"reason": out[-1500:]}, open(os.path.join(piece, "failed.json"), "w"), indent=1)
        sys.exit(r.returncode)


if __name__ == "__main__":
    main()
