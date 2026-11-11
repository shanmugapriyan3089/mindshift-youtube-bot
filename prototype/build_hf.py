"""
Build a HyperFrames composition (index.html) for a story-POV Short.

Inputs (in the HyperFrames project dir):
  assets/img_XX.png   scene stills (from story_pov.py)
  narration.wav       full narration
  words.json          word timings [{text,start,end}] (faster-whisper)
  assets/drone.wav, hit.wav, whoosh.wav  sound design

Usage:  python prototype/build_hf.py prototype/hf_stanford
Then:   cd prototype/hf_stanford && npm run check && npm run render
"""
import json, os, sys, html

PROJ = sys.argv[1] if len(sys.argv) > 1 else "prototype/hf_stanford"

# [start, duration] per scene — from narration wav lengths (+0.35 pad)
SCENES = [[0, 9.64], [9.64, 6.16], [15.79, 11.52], [27.31, 8.6], [35.91, 5.88],
          [41.79, 6.36], [48.14, 6.2], [54.34, 13.16], [67.5, 7.24]]
TOTAL = 78.0          # narration 74.74s + end-card tail
XFADE = 0.35

# Camera move per scene: (scale_from, scale_to, x_from, x_to, y_from, y_to)
MOVES = [
    (1.02, 1.14, 0, -20, 30, -20),     # kitchen — push in
    (1.18, 1.10, 50, -50, 0, 0),       # arrest — lateral pan
    (1.00, 1.12, 0, 0, 0, -30),        # corridor — slow push (punch-in added at "8612")
    (1.22, 1.05, 0, 0, -40, 20),       # guard — pull out, looming
    (1.10, 1.22, 0, 0, 0, 0),          # smoke — push + shake
    (1.00, 1.28, 0, 0, 20, -30),       # breakdown — strong push in
    (1.00, 1.20, 0, 0, 40, -10),       # empty corridor — dolly
    (1.15, 1.15, 0, 0, -70, 70),       # tape recorder — tilt down
    (1.00, 1.12, 0, 0, 0, -15),        # final portrait — slow push
]

# Documentary stamps: (start, duration, text)
STAMPS = [
    (1.3, 4.0, "AUGUST 1971 · PALO ALTO"),        # after the cold open
    (16.0, 4.8, "STANFORD · JORDAN HALL"),
    (36.0, 3.6, "DAY 2"),
    (41.9, 3.6, "HOUR 36"),
    (48.3, 4.6, "DAY 6 · SHUT DOWN"),
    (54.5, 4.2, "THE ARCHIVE TAPES"),
]

HITS = [1.15, 25.42, 51.84, 59.1, 74.75]  # cold-open cut, "8612", "shut down", twist, end card
PUNCH = 25.42                            # snap zoom on "You're 8612"
FLASHES = [1.15, 25.42]

ACCENT_WORDS = {"8612", "8612.", "arrested", "rebel.", "rebel", "coached", "faked", "six", "days.", "uniform"}


def caption_groups(words):
    groups, cur = [], []
    for w in words:
        cur.append(w)
        if len(cur) == 3 or w["text"][-1:] in ".,?!":
            groups.append(cur); cur = []
    if cur:
        groups.append(cur)
    out = []
    for i, g in enumerate(groups):
        start = g[0]["start"]
        nxt = groups[i + 1][0]["start"] if i + 1 < len(groups) else g[-1]["end"] + 0.4
        end = min(nxt, g[-1]["end"] + 0.6)
        out.append((start, max(end - start, 0.25), g))
    return out


def build():
    words = json.load(open(os.path.join(PROJ, "words.json")))
    el, js = [], []

    # Scenes
    for i, ((st, du), mv) in enumerate(zip(SCENES, MOVES)):
        s0 = max(st - (XFADE if i else 0), 0)
        d0 = du + (st - s0) + (XFADE if i < len(SCENES) - 1 else 0)
        el.append(f'<div id="sc{i}" class="clip scene" data-start="{s0:.2f}" data-duration="{d0:.2f}" '
                  f'data-track-index="1" style="z-index:{10+i}"><img id="im{i}" class="still" '
                  f'src="assets/img_{i:02d}.png"/></div>')
        sf, stt, xf, xt, yf, yt = mv
        js.append(f'tl.fromTo("#im{i}",{{scale:{sf},x:{xf},y:{yf}}},{{scale:{stt},x:{xt},y:{yt},duration:{d0:.2f},ease:"none"}},{s0:.2f});')
        if i:
            js.append(f'tl.fromTo("#sc{i}",{{opacity:0}},{{opacity:1,duration:{XFADE},ease:"none"}},{s0:.2f});')

    # Smoke scene shake (deterministic)
    st, du = SCENES[4]
    for k in range(int(du * 12)):
        dx = ((k * 37) % 13) - 6; dy = ((k * 53) % 11) - 5
        js.append(f'tl.set("#sc4",{{x:{dx},y:{dy}}},{st + k/12:.3f});')
    js.append(f'tl.set("#sc4",{{x:0,y:0}},{st+du:.2f});')

    # Punch-in on "8612"
    js.append(f'tl.to("#sc2",{{scale:1.22,duration:0.18,ease:"power3.out"}},{PUNCH:.2f});')

    # Cold open: 8612 still + stamp for first 1.15s
    el.append('<div id="cold" class="clip scene" data-start="0" data-duration="1.15" style="z-index:40">'
              '<img id="coldim" class="still" src="assets/cold.png"/>'
              '<div class="coldtag">PRISONER 8612</div></div>')
    js.append('tl.fromTo("#coldim",{scale:1.3},{scale:1.18,duration:1.15,ease:"power2.out"},0);')
    js.append('tl.from(".coldtag",{opacity:0,scale:1.4,duration:0.25,ease:"power3.out"},0.1);')

    # Flashes
    for i, t in enumerate(FLASHES):
        el.append(f'<div id="fl{i}" class="clip flash" data-start="{t-0.05:.2f}" data-duration="0.5" style="z-index:80"></div>')
        js.append(f'tl.fromTo("#fl{i}",{{opacity:0.85}},{{opacity:0,duration:0.45,ease:"power2.out"}},{t-0.05:.2f});')

    # Stamps (typewriter)
    for i, (st, du, text) in enumerate(STAMPS):
        spans = "".join(f'<span class="ch">{html.escape(c) if c != " " else "&nbsp;"}</span>' for c in text)
        el.append(f'<div id="stp{i}" class="clip stamp" data-start="{st:.2f}" data-duration="{du:.2f}" '
                  f'style="z-index:60"><div class="stampbox">{spans}</div></div>')
        for k in range(len(text)):
            js.append(f'tl.fromTo("#stp{i} .ch:nth-child({k+1})",{{opacity:0}},{{opacity:1,duration:0.01}},{st + 0.035*k:.3f});')
        js.append(f'tl.to("#stp{i}",{{opacity:0,duration:0.3}},{st+du-0.3:.2f});')

    # Captions — karaoke highlight
    for gi, (st, du, g) in enumerate(caption_groups(words)):
        ws = "".join(f'<span class="w{" acc" if w["text"] in ACCENT_WORDS else ""}" id="w{gi}_{k}">'
                     f'{html.escape(w["text"].upper())}</span> ' for k, w in enumerate(g))
        el.append(f'<div id="cap{gi}" class="clip cap" data-start="{st:.2f}" data-duration="{du:.2f}" '
                  f'style="z-index:70"><div class="capline">{ws}</div></div>')
        js.append(f'tl.fromTo("#cap{gi} .capline",{{scale:0.82,opacity:0}},{{scale:1,opacity:1,duration:0.12,ease:"back.out(2)"}},{st:.2f});')
        for k, w in enumerate(g):
            js.append(f'tl.set("#w{gi}_{k}",{{opacity:1}},{w["start"]:.2f});')

    # Final title card
    el.append('<div id="endcard" class="clip endcard" data-start="74.6" data-duration="3.4" style="z-index:65">'
              '<div class="endsmall">THE</div><div class="endbig">STANFORD PRISON<br/>EXPERIMENT</div>'
              '<div class="endq">Would you obey?</div></div>')
    js.append('tl.from("#endcard .endsmall",{opacity:0,y:20,duration:0.5},74.65);')
    js.append('tl.from("#endcard .endbig",{opacity:0,scale:1.15,duration:0.8,ease:"power3.out"},74.85);')
    js.append('tl.from("#endcard .endq",{opacity:0,duration:0.6},75.5);')

    # Grain — deterministic jitter
    el.append('<div id="grain" class="clip grain" data-start="0" data-duration="78.0" style="z-index:90"></div>')
    for k in range(int(TOTAL * 12)):
        js.append(f'tl.set("#grain",{{x:{-((k*97)%180)},y:{-((k*131)%320)}}},{k/12:.3f});')

    # Audio
    au = ['<audio id="narr" src="narration.wav" data-start="0" data-duration="74.74" data-volume="1"></audio>',
          '<audio id="drone" src="assets/drone.wav" data-start="0" data-duration="76" data-volume="0.45"></audio>']
    for i, t in enumerate(HITS):
        au.append(f'<audio id="hit{i}" src="assets/hit.wav" data-start="{t-0.05:.2f}" data-duration="2.4" data-volume="0.7"></audio>')
    for i, (st, _) in enumerate(SCENES[1:], 1):
        au.append(f'<audio id="wh{i}" src="assets/whoosh.wav" data-start="{max(st-0.6,0):.2f}" data-duration="0.9" data-volume="0.5"></audio>')

    css = """
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1080px;height:1920px;overflow:hidden;background:#000}
body{font-family:"Anton",sans-serif}
.clip{position:absolute;inset:0;width:1080px;height:1920px}
.scene{overflow:hidden;background:#000}
.still{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;filter:contrast(1.08) saturate(0.82) sepia(0.12) brightness(0.95)}
.scene::after{content:"";position:absolute;inset:0;background:radial-gradient(ellipse at center,rgba(0,0,0,0) 45%,rgba(0,0,0,0.75) 100%),linear-gradient(to bottom,rgba(0,0,0,0.35) 0%,rgba(0,0,0,0) 18%,rgba(0,0,0,0) 55%,rgba(0,0,0,0.65) 100%)}
.flash{background:#fff}
.grain{width:1300px;height:2300px;background:url(assets/grain.png);background-size:650px 1150px;opacity:0.16;mix-blend-mode:overlay;pointer-events:none}
.stamp{display:flex;justify-content:center;align-items:flex-start;padding-top:190px}
.stampbox{font-family:"Courier Prime",monospace;font-weight:700;font-size:42px;letter-spacing:3px;max-width:960px;color:#f2e6c9;background:rgba(0,0,0,0.55);padding:14px 26px;border-left:6px solid #d9372b}
.cap{display:flex;justify-content:center;align-items:flex-start;padding-top:1240px}
.capline{font-size:104px;line-height:1.05;text-align:center;color:#fff;max-width:960px;text-shadow:0 6px 0 rgba(0,0,0,0.9),0 0 30px rgba(0,0,0,0.8);letter-spacing:1px}
.capline .w{opacity:0.45}
.capline .acc{color:#ffcf3a}
.coldtag{position:absolute;left:0;right:0;top:820px;text-align:center;font-size:150px;color:#fff;letter-spacing:6px;text-shadow:0 8px 0 #000}
.endcard{display:flex;flex-direction:column;justify-content:center;align-items:center;background:rgba(0,0,0,0.55);text-align:center;padding-bottom:300px}
.endsmall{font-family:"Courier Prime",monospace;font-size:44px;color:#d9372b;letter-spacing:12px}
.endbig{font-size:132px;line-height:1.0;color:#fff;letter-spacing:2px;margin-top:10px}
.endq{font-family:"Courier Prime",monospace;font-size:52px;color:#ffcf3a;margin-top:40px}
"""
    doc = f"""<!doctype html>
<html lang="en" data-resolution="portrait">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=1080, height=1920"/>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Anton&family=Courier+Prime:wght@700&display=block"/>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
<style>{css}</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="1080" data-height="1920">
{chr(10).join(el)}
{chr(10).join(au)}
</div>
<script>
const tl = gsap.timeline({{ paused: true }});
{chr(10).join(js)}
window.__timelines = window.__timelines || {{}};
window.__timelines["main"] = tl;
</script>
</body>
</html>
"""
    with open(os.path.join(PROJ, "index.html"), "w", encoding="utf-8") as f:
        f.write(doc)
    print(f"index.html written: {len(el)} elements, {len(js)} timeline ops")


if __name__ == "__main__":
    build()
