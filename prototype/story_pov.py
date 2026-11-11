"""
Story-POV prototype — cinematic Short from a real psychology story.

Pipeline:
  1. Hand-written, fact-checked script (scenes below)
  2. Gemini image model -> consistent-character cinematic stills (scene 1 = reference)
  3. Gemini TTS -> narration per scene
  4. FFmpeg -> Ken Burns motion, film grain, vignette, burned captions, music bed

Usage:
  python prototype/story_pov.py            # full render
  python prototype/story_pov.py --voice    # narration only (free tier OK)

Needs GEMINI_API_KEY in .env (narration, free). Images: set CLOUDFLARE_ACCOUNT_ID +
CLOUDFLARE_API_TOKEN for free FLUX.2 via Workers AI, otherwise Gemini (needs billing).
"""
import os, sys, json, time, base64, wave, argparse, subprocess, random
import requests
from dotenv import load_dotenv

load_dotenv()
KEY = os.getenv("GEMINI_API_KEY")
API = "https://generativelanguage.googleapis.com/v1beta/models"
IMAGE_MODEL = "gemini-3.1-flash-image"
TTS_MODEL = os.getenv("STORY_TTS_MODEL", "gemini-3.1-flash-tts-preview")  # channel voice; free tier: 10 req/day
VOICE = "Charon"
# Free image backend (used when set): Cloudflare Workers AI
CF_ACCOUNT = os.getenv("CLOUDFLARE_ACCOUNT_ID")
CF_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")
CF_MODEL = os.getenv("CLOUDFLARE_IMAGE_MODEL", "flux-2-klein-9b")
OUT = os.path.join(os.path.dirname(__file__), "out_stanford")
W, H, FPS = 1080, 1920, 30
MUSIC = "assets/music/fassounds-good-night-lofi-cozy-chill-music-160166.mp3"

STYLE = ("Cinematic film still, shot on 35mm Kodak film in 1971, muted 70s colour palette, "
         "soft film grain, shallow depth of field, moody practical lighting, photorealistic, "
         "vertical 9:16 composition, no text, no watermark.")
# Face/hair only — outfit is set per scene so the smock doesn't leak into street scenes
HERO = ("a 21-year-old American young man with shaggy brown hair, thin face, light stubble")
SMOCK = ("wearing a loose knee-length beige muslin prison smock with the number \"8612\" "
         "stencilled in large black digits on the chest")

# Facts: Stanford Prison Experiment, Aug 1971 (Zimbardo). Prisoner 8612 = Douglas Korpi,
# released ~36h in; in 2017 he said he partly faked the breakdown. Guard coaching shown
# in recordings published by Thibault Le Texier (2018).
SCENES = [
    {"say": "August, 1971. You answer a newspaper ad. Fifteen dollars a day, to live in a fake prison for two weeks.",
     "hero": True,
     "img": f"{HERO}, wearing a faded blue 1970s t-shirt and jeans, reading a newspaper classified ad at a sunny 1970s kitchen table, curious expression"},
    {"say": "Sunday morning, a real police car pulls up. You're arrested, in front of your neighbours.",
     "hero": True,
     "img": f"{HERO}, wearing a faded blue 1970s t-shirt and jeans, hands cuffed behind his back, being led by a 1970s police officer to a black-and-white police car on a suburban street, neighbours watching from their lawns"},
    {"say": "In a basement at Stanford, they take your clothes. You get a smock, a chain on your ankle, and a number. You're not you anymore. You're 8612.",
     "hero": True,
     "img": f"{HERO}, {SMOCK}, standing in a narrow basement corridor converted into a jail, a small chain around his ankle, harsh fluorescent light, blank stare"},
    {"say": "The guards are students, just like you. Khaki uniforms. Mirrored sunglasses. Wooden batons.",
     "img": "a young 1970s college student wearing a khaki uniform shirt and mirrored aviator sunglasses, arms crossed, leaning against a painted cinderblock wall in a dim basement hallway, low angle, serious expression"},
    {"say": "On day two, the prisoners rebel. The guards fight back with fire extinguishers.",
     "img": "a thick white cloud of fire extinguisher powder filling a makeshift basement jail corridor in a 1970s university building, blurred silhouettes of long-haired college students in short-sleeve khaki shirts and beige smocks in the haze, red fire extinguisher in the foreground, dramatic chaos"},
    {"say": "Thirty-six hours in, you start screaming that you want out. And they let you go.",
     "hero": True,
     "img": f"{HERO}, {SMOCK}, in extreme distress, face in his hands, sitting on a cot in a tiny dark cell, single light from the door"},
    {"say": "The study was supposed to last two weeks. It was shut down after six days.",
     "img": "an empty makeshift basement jail corridor at night, cell doors open, a handwritten sign reading THE HOLE on a closet door, eerie silence"},
    {"say": "For fifty years, it was proof that good people turn cruel. But recordings later showed the guards were coached to be tough. And 8612 said he faked part of his breakdown.",
     "img": "close-up of a 1970s reel-to-reel tape recorder playing on a desk with scattered typed research papers and a mirrored pair of aviator sunglasses, warm lamp light"},
    {"say": "So the real question isn't what a uniform does to you. It's what you'll do, when someone in charge tells you to.",
     "hero": True,
     "img": f"{HERO}, wearing a dark grey wool sweater, looking directly into the camera in a dim room, calm and haunted, intimate portrait"},
]


# ── Gemini helpers ────────────────────────────────────────────────────────────

def _post(model, body, tries=5):
    for i in range(tries):
        r = requests.post(f"{API}/{model}:generateContent", params={"key": KEY}, json=body, timeout=300)
        if r.status_code == 200:
            return r.json()
        msg = r.json().get("error", {}).get("message", r.text)[:200]
        full = r.text
        if r.status_code == 429 and "free_tier" in full and ("limit: 0" in full or "per day" in full.lower() or "PerDay" in full):
            sys.exit(f"[{model}] Free-tier daily quota used up (or none) — enable billing on the Gemini key, or retry tomorrow.")
        if r.status_code in (429, 500, 503):
            wait = 15 * (i + 1)
            print(f"  [{model}] {r.status_code}, retrying in {wait}s")
            time.sleep(wait)
            continue
        sys.exit(f"[{model}] {r.status_code}: {msg}")
    sys.exit(f"[{model}] gave up after {tries} tries")


def gen_image(prompt, path, ref_path=None):
    if CF_ACCOUNT and CF_TOKEN:
        return gen_image_cloudflare(prompt, path, ref_path)
    return gen_image_gemini(prompt, path, ref_path)


def gen_image_cloudflare(prompt, path, ref_path=None):
    """Cloudflare Workers AI FLUX.2 — free tier (10k neurons/day), multipart, ref image supported."""
    if ref_path:
        prompt = "Same young man as the reference image: keep his exact face, hair and build, but dress him only as described here. " + prompt
    form = {"prompt": (None, f"{prompt}. {STYLE}"), "width": (None, "768"), "height": (None, "1344")}
    url = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT}/ai/run/@cf/black-forest-labs/{CF_MODEL}"
    for i in range(4):
        form["seed"] = (None, str(random.randint(1, 2**31 - 1)))
        if ref_path:
            form["input_image_0"] = ("ref.png", open(ref_path, "rb"), "image/png")
        r = requests.post(url, headers={"Authorization": f"Bearer {CF_TOKEN}"}, files=form, timeout=300)
        if '"code":4006' in r.text:
            sys.exit("[cloudflare] Daily free allowance (10k neurons) used up — resets 00:00 UTC (5:30 AM IST). "
                     "Rerun then; finished images are reused.")
        if r.status_code == 400 and '"code":3030' in r.text and i < 3:
            print("  [cloudflare] output flagged by safety filter, retrying with new seed"); continue
        if r.status_code == 200:
            data = r.json().get("result", {}).get("image")
            if data:
                with open(path, "wb") as f:
                    f.write(base64.b64decode(data))
                return path
        if r.status_code in (429, 500, 503) and i < 3:
            print(f"  [cloudflare] {r.status_code}, retrying"); time.sleep(10 * (i + 1)); continue
        sys.exit(f"[cloudflare] {r.status_code}: {r.text[:300]}")


def gen_image_gemini(prompt, path, ref_path=None):
    parts = []
    if ref_path:
        with open(ref_path, "rb") as f:
            parts.append({"inlineData": {"mimeType": "image/png", "data": base64.b64encode(f.read()).decode()}})
        prompt = ("Same young man as the reference image: keep his exact face, hair and build, but dress him only as described here. " + prompt)
    parts.append({"text": f"{prompt}. {STYLE}"})
    j = _post(IMAGE_MODEL, {"contents": [{"parts": parts}],
                            "generationConfig": {"responseModalities": ["IMAGE"],
                                                 "imageConfig": {"aspectRatio": "9:16"}}})
    for p in j["candidates"][0]["content"]["parts"]:
        if "inlineData" in p:
            with open(path, "wb") as f:
                f.write(base64.b64decode(p["inlineData"]["data"]))
            return path
    sys.exit(f"[image] no image returned: {json.dumps(j)[:300]}")


def gen_voice(text, path):
    # Plain text only — style prefixes ("Say in a ... voice:") get read aloud by this model
    j = _post(TTS_MODEL, {"contents": [{"parts": [{"text": text}]}],
                          "generationConfig": {"responseModalities": ["AUDIO"],
                                               "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": VOICE}}}}})
    pcm = base64.b64decode(j["candidates"][0]["content"]["parts"][0]["inlineData"]["data"])
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(24000)
        w.writeframes(_mute_tail_click(pcm, 24000))
    return path


def _mute_tail_click(pcm, sr):
    """Gemini TTS ends each clip with a full-scale ~0.13s click after the last word.
    Mute everything after the final silence (length kept, so word timings don't move)."""
    import numpy as np
    a = np.frombuffer(pcm, dtype=np.int16).copy()
    win = int(0.01 * sr)
    rms = np.sqrt(np.convolve((a.astype(float) / 32768) ** 2, np.ones(win) / win, mode="same"))
    quiet = rms < 10 ** (-45 / 20)
    # walk back from the end: skip the click, then find the start of the silence before it
    i = len(a) - 1
    while i > 0 and quiet[i]: i -= 1          # trailing silence (if any)
    while i > 0 and not quiet[i]: i -= 1      # the click
    if len(a) - i > int(0.4 * sr):            # no short burst at the end: leave the clip alone
        return pcm
    while i > 0 and quiet[i]: i -= 1          # the pause before the click
    a[i + win:] = 0
    return a.tobytes()


def wav_len(path):
    with wave.open(path) as w:
        return w.getnframes() / w.getframerate()


# ── FFmpeg assembly ───────────────────────────────────────────────────────────

def _ff(args):
    subprocess.run(["ffmpeg", "-y", "-v", "error", *args], check=True)


def _ass_time(t):
    h, rem = divmod(t, 3600); m, s = divmod(rem, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


def write_captions(scenes, durs, path):
    """2-3 word caption chunks, timed proportionally to word length within each scene."""
    head = ("[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\n\n"
            "[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, "
            "Bold, BorderStyle, Outline, Shadow, Alignment, MarginV\n"
            "Style: Cap,Arial Black,96,&H00FFFFFF,&H00000000,&H64000000,1,1,6,2,2,560\n\n"
            "[Events]\nFormat: Layer, Start, End, Style, Text\n")
    lines, t0 = [], 0.0
    for sc, d in zip(scenes, durs):
        words = sc["say"].split()
        chunks, cur = [], []
        for w in words:
            cur.append(w)
            if len(cur) == 3 or w[-1] in ".,?!":
                chunks.append(cur); cur = []
        if cur: chunks.append(cur)
        speak = d - 0.35  # trailing pad
        total = sum(len(" ".join(c)) for c in chunks)
        t = t0 + 0.1
        for c in chunks:
            span = speak * len(" ".join(c)) / total
            text = " ".join(c).upper().replace("8612", r"{\c&H3CC8FF&}8612{\c&HFFFFFF&}")
            lines.append(f"Dialogue: 0,{_ass_time(t)},{_ass_time(t + span)},Cap,{text}")
            t += span
        t0 += d
    with open(path, "w", encoding="utf-8") as f:
        f.write(head + "\n".join(lines) + "\n")


def render_clip(img, dur, path, idx):
    """Slow Ken Burns push/pull + drift, alternating per scene."""
    frames = int(dur * FPS) + 1
    zin = idx % 2 == 0
    z = "1.0+0.12*on/{f}".format(f=frames) if zin else "1.12-0.12*on/{f}".format(f=frames)
    dx = random.Random(idx).choice([-1, 1])
    x = f"(iw-iw/zoom)/2 + {dx}*40*on/{frames}"
    _ff(["-loop", "1", "-i", img, "-t", f"{dur:.3f}",
         "-vf", (f"scale=2160:3840:force_original_aspect_ratio=increase,crop=2160:3840,"
                 f"zoompan=z='{z}':x='{x}':y='(ih-ih/zoom)/2':d={frames}:s={W}x{H}:fps={FPS},"
                 "eq=contrast=1.05:saturation=0.9,vignette=PI/5,noise=alls=10:allf=t,format=yuv420p"),
         "-c:v", "libx264", "-preset", "medium", "-crf", "18", path])


def assemble(scenes, imgs, wavs, out_path):
    durs = [wav_len(w) + 0.35 for w in wavs]
    clips = []
    for i, (img, d) in enumerate(zip(imgs, durs)):
        c = os.path.join(OUT, f"clip_{i:02d}.mp4")
        print(f"  [motion] scene {i+1}/{len(imgs)} ({d:.1f}s)")
        render_clip(img, d, c, i)
        clips.append(c)

    # Narration track: each wav + 0.35s silence
    padded = []
    for i, w in enumerate(wavs):
        p = os.path.join(OUT, f"pad_{i:02d}.wav")
        _ff(["-i", w, "-af", "apad=pad_dur=0.35", "-ar", "48000", "-ac", "2", p])
        padded.append(p)
    lst_a = os.path.join(OUT, "a.txt"); lst_v = os.path.join(OUT, "v.txt")
    with open(lst_a, "w") as f: f.writelines(f"file '{os.path.abspath(p)}'\n" for p in padded)
    with open(lst_v, "w") as f: f.writelines(f"file '{os.path.abspath(c)}'\n" for c in clips)
    narr = os.path.join(OUT, "narration.wav")
    _ff(["-f", "concat", "-safe", "0", "-i", lst_a, "-c", "copy", narr])
    video = os.path.join(OUT, "video_noaudio.mp4")
    _ff(["-f", "concat", "-safe", "0", "-i", lst_v, "-c", "copy", video])

    ass = os.path.join(OUT, "captions.ass")
    write_captions(scenes, durs, ass)
    ass_ff = ass.replace("\\", "/").replace(":", r"\:")
    total = sum(durs)
    _ff(["-i", video, "-i", narr, "-stream_loop", "-1", "-i", MUSIC,
         "-filter_complex",
         (f"[0:v]ass='{ass_ff}'[v];"
          f"[2:a]volume=0.07,afade=t=out:st={total-2:.2f}:d=2[m];"
          "[1:a][m]amix=inputs=2:duration=first:normalize=0[a]"),
         "-map", "[v]", "-map", "[a]", "-t", f"{total:.2f}",
         "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-c:a", "aac", "-b:a", "192k",
         "-movflags", "+faststart", out_path])
    print(f"\n✅ {out_path}  ({total:.1f}s)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--voice", action="store_true", help="narration only")
    ap.add_argument("--images", action="store_true", help="narration + images, skip FFmpeg render")
    args = ap.parse_args()
    if not KEY:
        sys.exit("GEMINI_API_KEY missing from .env")
    os.makedirs(OUT, exist_ok=True)

    wavs = []
    for i, sc in enumerate(SCENES):
        p = os.path.join(OUT, f"voice_{i:02d}.wav")
        if not os.path.exists(p):
            print(f"  [voice] scene {i+1}/{len(SCENES)}")
            gen_voice(sc["say"], p)
        wavs.append(p)
    print(f"  narration: {sum(wav_len(w) for w in wavs):.1f}s")
    if args.voice:
        return

    imgs, ref = [], None
    for i, sc in enumerate(SCENES):
        p = os.path.join(OUT, f"img_{i:02d}.png")
        if not os.path.exists(p):
            print(f"  [image] scene {i+1}/{len(SCENES)}")
            gen_image(sc["img"], p, ref if sc.get("hero") else None)
        if ref is None and i == 0:
            ref = p
        imgs.append(p)
    if args.images:
        return

    assemble(SCENES, imgs, wavs, os.path.join(OUT, "stanford_pov_short.mp4"))


if __name__ == "__main__":
    main()
