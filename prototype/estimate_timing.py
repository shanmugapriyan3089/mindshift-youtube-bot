"""
Provisional src/timing.js from the script alone (no TTS key needed), so a story can be built and its
stills checked before the real narration exists. The daily GitHub Action replaces it with real timings.

Usage:  python prototype/estimate_timing.py prototype/sketch_<slug>
"""
import os, sys, json, re
sys.path.insert(0, os.path.dirname(__file__))
from make_voice import write_timing_js, GAP

WPS = 2.55   # narration pace measured on the Milgram/Asch voices (~153 words/min)


def main(piece):
    lines = json.load(open(os.path.join(piece, "story.json"), encoding="utf-8"))["lines"]
    words, starts, t = [], [], 0.0
    for line in lines:
        starts.append(round(t, 3))
        toks = line.split()
        for w in toks:
            d = max(0.18, len(re.sub(r"[^A-Za-z0-9]", "", w)) * 0.065) if w else 0.2
            words.append({"text": w, "start": round(t, 2), "end": round(t + d, 2)})
            t += d + (0.25 if w[-1:] in ".,?!:" else 0.05)
        t += GAP
    json.dump({"S": starts + [round(t, 3)], "words": words, "estimated": True},
              open(os.path.join(piece, "timing.json"), "w"), indent=1)
    write_timing_js(piece, starts, t, words)
    print(f"estimated timing: {t:.1f}s, {len(words)} words (replaced by real timings when the voice is made)")


if __name__ == "__main__":
    main(sys.argv[1])
