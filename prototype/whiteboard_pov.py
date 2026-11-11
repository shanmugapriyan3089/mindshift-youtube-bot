"""
Whiteboard / doodle version of the Stanford story-POV Short (Sprouts / Practical Psychology style).

  1. Cloudflare FLUX.2 -> minimal doodle stills (yangagent whiteboard prompt template)
  2. yangagent/whiteboard-animation-skill -> hand draws each still (line art, then colour)
  3. Reuses narration + word timings from the cinematic prototype

Usage:
  python prototype/whiteboard_pov.py images     # generate stills (uses Cloudflare free quota)
  python prototype/whiteboard_pov.py draw       # whiteboard-animate each still
"""
import os, sys, subprocess, glob, shutil
sys.path.insert(0, os.path.dirname(__file__))
import story_pov as sp
from PIL import Image

OUT = os.path.join(os.path.dirname(__file__), "out_whiteboard")
WB_SCRIPT = os.environ.get("WB_SCRIPT", "")  # path to generate_whiteboard.py

# From yangagent/whiteboard-video-workflow prompt_template.py
STYLE = ("Minimal hand-drawn illustration, pure illustration without any text, off-white paper "
         "background(#F6F1E3), dark gray sketch lines, orange as the only accent color(#CD6441), lots of "
         "negative space, Notion-like doodle aesthetic, faceless round-headed human figure, clean editorial "
         "composition, conceptual rather than literal, simple background. Absolutely no text, no words, no "
         "letters, no numbers, no typography, no realism, no 3D, no painterly texture, no high saturation, "
         "no complex scene, no photographic detail. Vertical composition with the subject in the upper two "
         "thirds and empty paper at the bottom.")

PROMPTS = [
    "a faceless round-headed young man sitting at a small kitchen table reading a newspaper, a coffee mug, curious posture",
    "a faceless round-headed young man with hands behind his back being led by a police officer toward a simple police car, two small neighbour figures watching from a doorway",
    "a faceless round-headed young man wearing a long plain smock, an orange chain around one ankle, standing alone in a narrow corridor of simple cell doors",
    "a faceless round-headed guard figure in a uniform shirt wearing dark mirrored sunglasses, arms crossed, standing tall, seen from a low angle",
    "a cloud of white spray filling a corridor of cell bars, small faceless figures behind the bars, an orange fire extinguisher in the foreground",
    "a faceless round-headed young man sitting on a narrow cot with his head in his hands inside a small cell, a single orange beam of light from the door",
    "an empty corridor with every cell door left open, a few calendar pages drifting in the air",
    "an old reel-to-reel tape recorder on a desk with scattered papers and a pair of sunglasses, orange tape reels",
    "a tiny faceless round-headed figure standing below a huge hand pointing down at him from the top of the frame",
]


def images():
    os.makedirs(OUT, exist_ok=True)
    sp.STYLE = STYLE  # gen_image_cloudflare appends sp.STYLE
    for i, p in enumerate(PROMPTS):
        path = os.path.join(OUT, f"img_{i:02d}.png")
        if os.path.exists(path):
            continue
        print(f"  [image] {i+1}/{len(PROMPTS)}")
        sp.gen_image_cloudflare(p, path)


def draw():
    if not os.path.exists(WB_SCRIPT):
        sys.exit("Set WB_SCRIPT to the whiteboard skill's generate_whiteboard.py")
    durs = [sp.wav_len(w) + 0.35 for w in sorted(glob.glob(os.path.join(sp.OUT, "voice_*.wav")))]
    for i, d in enumerate(durs):
        src = os.path.join(OUT, f"img_{i:02d}.png")
        big = os.path.join(OUT, f"big_{i:02d}.png")
        dst = os.path.join(OUT, f"wb_{i:02d}.mp4")
        if os.path.exists(dst):
            continue
        # Upscale to full 1080x1920 so the skill keeps vertical HD (its cap is 1080 on the long edge)
        Image.open(src).convert("RGB").resize((1080, 1920), Image.LANCZOS).save(big)
        tmp = os.path.join(OUT, f"tmp_{i:02d}")
        print(f"  [draw] scene {i+1}/{len(durs)} ({d:.1f}s)")
        subprocess.run([sys.executable, WB_SCRIPT, big, "--output-dir", tmp,
                        "--duration", str(int(d * 1000))], check=True, stdout=subprocess.DEVNULL)
        shutil.move(glob.glob(os.path.join(tmp, "*.mp4"))[0], dst)
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    {"images": images, "draw": draw}[sys.argv[1]]()
