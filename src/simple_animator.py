"""
Productive Peter style — TWO stick figures interacting like a cartoon.
Figure A explains/teaches, Figure B reacts (shocked/curious/excited).
Large figures, speech bubbles between them, props as context.
"""
import os, math, subprocess, shutil, textwrap, random
from PIL import Image, ImageDraw, ImageFont


# ── Pollinations.ai background ────────────────────────────────────────────────

def _fetch_bg(topic: str, w: int, h: int, seed: int) -> "Image.Image | None":
    """Fetch a free AI-generated background from Pollinations.ai (no API key).
    Returns a PIL Image blended 55% with white so stick figures stay readable.
    Falls back to None on any network error — caller uses plain white grid.
    """
    import urllib.request, urllib.parse
    from io import BytesIO

    # Build a clean scene-relevant prompt from the text overlay
    keywords = " ".join(topic.lower().replace("'", "").split()[:7])
    prompt = (f"minimalist abstract poster background, soft pastel gradient, "
              f"{keywords}, psychology motivation, no text, no people, "
              f"clean professional, dreamy light")
    url = (f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}"
           f"?width={w}&height={h}&nologo=true&seed={seed}&model=flux")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=25) as r:
            data = r.read()
        img = Image.open(BytesIO(data)).convert("RGB").resize((w, h))
        # Blend heavily with white so figures stand out clearly (Productive Peter style)
        white = Image.new("RGB", (w, h), (255, 255, 255))
        return Image.blend(img, white, 0.72)
    except Exception as e:
        print(f"  [BG] Pollinations failed ({e}), using plain background")
        return None

# Varied B-figure reactions per scene type (hook/problem/solution/result)
_REACTIONS = [
    ["Wait... seriously?!", "That's unreal!", "I had no idea!", "No way...", "Whoa, really?!"],
    ["Why does this happen?", "This is my life...", "I feel this so much!", "Makes sense now...", "Been there..."],
    ["This changes everything!", "So simple!", "Game changer!", "I need this now!", "Why didn't I know?!"],
    ["It actually works!", "Life changed!", "I'm doing this!", "Starting today!", "Thank you!!"],
]

# Label pools per scene type — slot+day combo picks which label so different pipelines differ visually
_HOOK_LABELS    = ["WAKE UP CALL", "REALITY CHECK", "MIND THIS", "DID YOU KNOW?", "2 AM TRUTH", "FACT BOMB"]
_PROBLEM_LABELS = ["THE BLOCK", "WHY WE FAIL", "OLD PATTERN", "STUCK IN LOOP", "THE TRAP", "ROOT CAUSE"]
_SOLUTION_LABELS= ["THE FIX", "GAME CHANGER", "KEY INSIGHT", "BREAKTHROUGH", "THE SECRET", "UNLOCK IT"]
_RESULT_LABELS  = ["LEVEL UP", "NEW YOU", "SUCCESS MODE", "TRANSFORMATION", "YOU GOT THIS", "THE PAYOFF"]
_LABEL_POOLS    = [_HOOK_LABELS, _PROBLEM_LABELS, _SOLUTION_LABELS, _RESULT_LABELS]

BG     = (245, 248, 252)
LINE   = (15,  15,  15)
YELLOW = (255, 214,   0)
RED    = (220,  50,  50)
BLUE   = ( 41, 128, 185)
GREEN  = ( 39, 174,  96)
ORANGE = (230, 126,  34)
PURPLE = (142,  68, 173)
WHITE  = (255, 255, 255)


def _ffmpeg():
    if shutil.which("ffmpeg"): return "ffmpeg"
    try:
        import imageio_ffmpeg; return imageio_ffmpeg.get_ffmpeg_exe()
    except: return "ffmpeg"


def _font(size):
    for p in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/Arial.ttf",
    ]:
        try: return ImageFont.truetype(p, max(8, size))
        except: pass
    return ImageFont.load_default()

def _font_r(size):
    for p in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "C:/Windows/Fonts/arial.ttf",
    ]:
        try: return ImageFont.truetype(p, max(8, size))
        except: pass
    return ImageFont.load_default()


# ── Stick figure ──────────────────────────────────────────────────────────────
# pose: idle | talking | shocked | pointing_r | pointing_l | excited | thinking
# emotion: happy | shocked | sad | excited | thinking

def _figure(draw, cx, cy, s, pose="idle", emotion="happy", flip=False, phase=0):
    """Draw one stick figure. phase=0/1 animates the active arm for talking motion."""
    lw = max(3, int(5 * s))
    hr = int(28 * s)
    ht = cy - int(115 * s)
    hb = cy - int(59  * s)
    asway = int(14 * s * phase)  # active arm lifts by this on phase 1

    # Head
    draw.ellipse([cx-hr, ht, cx+hr, hb], fill=(255, 235, 210), outline=LINE, width=lw)

    # Eyes
    ey = cy - int(96 * s)
    for ex in [cx - int(10*s), cx + int(10*s)]:
        draw.ellipse([ex-int(5*s), ey-int(5*s), ex+int(5*s), ey+int(5*s)], fill=LINE)

    # Eyebrows (raised = surprised, flat = normal)
    for ex in [cx - int(10*s), cx + int(10*s)]:
        if emotion in ("shocked", "excited"):
            draw.arc([ex-int(9*s), ey-int(20*s), ex+int(9*s), ey-int(8*s)], 200, 340, fill=LINE, width=max(1, lw-2))
        else:
            draw.line([ex-int(8*s), ey-int(13*s), ex+int(8*s), ey-int(13*s)], fill=LINE, width=max(1, lw-2))

    # Mouth
    my = cy - int(76 * s)
    if emotion == "happy":
        draw.arc([cx-int(13*s), my-int(7*s), cx+int(13*s), my+int(7*s)], 0, 180, fill=LINE, width=lw-1)
    elif emotion == "shocked":
        draw.ellipse([cx-int(8*s), my-int(9*s), cx+int(8*s), my+int(5*s)], outline=LINE, width=lw-1)
    elif emotion == "sad":
        draw.arc([cx-int(13*s), my-int(4*s), cx+int(13*s), my+int(10*s)], 180, 360, fill=LINE, width=lw-1)
    elif emotion == "excited":
        draw.arc([cx-int(15*s), my-int(12*s), cx+int(15*s), my+int(8*s)], 0, 180, fill=LINE, width=lw)
        # Teeth
        draw.arc([cx-int(12*s), my-int(8*s), cx+int(12*s), my+int(4*s)], 0, 180, fill=WHITE, width=lw-2)
    elif emotion == "thinking":
        draw.line([cx-int(10*s), my, cx+int(6*s), my], fill=LINE, width=lw-1)

    # Body
    bb = cy + int(32 * s)
    draw.line([cx, hb, cx, bb], fill=LINE, width=lw)
    sy = cy - int(40 * s)  # shoulder y

    # Direction sign: +1 = facing right, -1 = facing left
    d = -1 if flip else 1

    # Arms — phase animates the active/gesturing arm
    if pose == "idle":
        draw.line([cx, sy, cx - int(52*s), cy + int(10*s)], fill=LINE, width=lw)
        draw.line([cx, sy, cx + int(52*s), cy + int(10*s)], fill=LINE, width=lw)
    elif pose == "talking":
        draw.line([cx, sy, cx - int(52*s)*d, cy + int(10*s)], fill=LINE, width=lw)
        draw.line([cx, sy, cx + int(38*s)*d, cy - int(20*s) - asway], fill=LINE, width=lw)
    elif pose == "shocked":
        draw.line([cx, sy, cx - int(60*s), cy - int(50*s) - asway], fill=LINE, width=lw)
        draw.line([cx, sy, cx + int(60*s), cy - int(50*s) - asway], fill=LINE, width=lw)
    elif pose == "pointing_r":
        draw.line([cx, sy, cx - int(50*s), cy + int(15*s)], fill=LINE, width=lw)
        draw.line([cx, sy, cx + int(80*s), cy - int(30*s) - asway], fill=LINE, width=lw + 1)
    elif pose == "pointing_l":
        draw.line([cx, sy, cx - int(80*s), cy - int(30*s) - asway], fill=LINE, width=lw + 1)
        draw.line([cx, sy, cx + int(50*s), cy + int(15*s)], fill=LINE, width=lw)
    elif pose == "excited":
        draw.line([cx, sy, cx - int(62*s), cy - int(62*s) - asway], fill=LINE, width=lw)
        draw.line([cx, sy, cx + int(62*s), cy - int(62*s) + asway], fill=LINE, width=lw)
    elif pose == "thinking":
        draw.line([cx, sy, cx - int(52*s), cy + int(10*s)], fill=LINE, width=lw)
        draw.line([cx, sy, cx + int(44*s)*d, cy - int(32*s) - asway], fill=LINE, width=lw)
        draw.line([cx + int(44*s)*d, cy - int(32*s) - asway,
                   cx + int(22*s)*d, cy - int(60*s) - asway], fill=LINE, width=lw)

    # Legs
    draw.line([cx, bb, cx - int(32*s), cy + int(96*s)], fill=LINE, width=lw)
    draw.line([cx, bb, cx + int(32*s), cy + int(96*s)], fill=LINE, width=lw)
    # Feet
    draw.line([cx - int(32*s), cy + int(96*s), cx - int(54*s), cy + int(96*s)], fill=LINE, width=lw)
    draw.line([cx + int(32*s), cy + int(96*s), cx + int(54*s), cy + int(96*s)], fill=LINE, width=lw)


# ── Speech bubble ─────────────────────────────────────────────────────────────

def _bubble(draw, cx, cy, text, w, fs, tail="left", fill=WHITE, anchor="center"):
    """
    Speech bubble. anchor = 'left' pins right edge near cx, 'right' pins left
    edge near cx, 'center' centres on cx. Prevents overlap between two figures.
    """
    font = _font(fs)
    max_chars = max(8, int((w * 0.42) / (fs * 0.60)))
    lines = textwrap.wrap(text, width=max_chars)
    if not lines:
        return
    lh = fs + 10
    tw = max(draw.textbbox((0,0), l, font=font)[2] for l in lines)
    th = len(lines) * lh
    pad = int(fs * 0.55)
    bw = tw + pad * 2
    bh = th + pad * 2

    if anchor == "left":        # bubble sits to the left of cx
        bx = max(8, cx - bw - int(fs * 0.3))
    elif anchor == "right":     # bubble sits to the right of cx
        bx = min(w - bw - 8, cx + int(fs * 0.3))
    else:
        bx = max(8, min(cx - bw // 2, w - bw - 8))

    by = cy - bh - int(fs * 0.8)

    draw.rounded_rectangle([bx, by, bx+bw, by+bh],
                            radius=int(fs * 0.45), fill=fill, outline=LINE, width=3)
    # Tail pointing down toward figure head
    if tail == "left":
        tx, ty = bx + int(bw * 0.25), by + bh
        draw.polygon([(tx, ty), (tx + int(fs*0.9), ty), (cx, cy - int(fs*0.2))], fill=fill)
        draw.line([(tx, ty), (cx, cy - int(fs*0.2))], fill=LINE, width=2)
        draw.line([(cx, cy - int(fs*0.2)), (tx + int(fs*0.9), ty)], fill=LINE, width=2)
    elif tail == "right":
        tx, ty = bx + int(bw * 0.75), by + bh
        draw.polygon([(tx - int(fs*0.9), ty), (tx, ty), (cx, cy - int(fs*0.2))], fill=fill)
        draw.line([(tx - int(fs*0.9), ty), (cx, cy - int(fs*0.2))], fill=LINE, width=2)
        draw.line([(cx, cy - int(fs*0.2)), (tx, ty)], fill=LINE, width=2)

    for i, line in enumerate(lines):
        lbb = draw.textbbox((0,0), line, font=font)
        lw2 = lbb[2] - lbb[0]
        draw.text((bx + pad + (tw - lw2)//2, by + pad + i*lh), line, fill=LINE, font=font)


# ── Thought bubble (for thinking pose) ───────────────────────────────────────

def _thought_bubble(draw, cx, cy, text, w, fs):
    # Dots trail
    for i, r in enumerate([5, 7, 10]):
        bx = cx + int((30 + i*20))
        by = cy - int((60 + i*22))
        draw.ellipse([bx-r, by-r, bx+r, by+r], fill=WHITE, outline=LINE, width=2)
    font = _font(fs)
    max_chars = max(8, int(w * 0.35 / (fs * 0.62)))
    lines = textwrap.wrap(text, width=max_chars)
    if not lines:
        return
    lh = fs + 8
    tw = max(draw.textbbox((0,0), l, font=font)[2] for l in lines)
    th = len(lines) * lh
    pad = int(fs * 0.5)
    bw = tw + pad * 2
    bh = th + pad * 2
    bx = cx + int(80)
    by = cy - int(160)
    bx = max(8, min(bx, w - bw - 8))
    draw.rounded_rectangle([bx, by, bx+bw, by+bh],
                            radius=int(fs * 0.5), fill=WHITE, outline=LINE, width=3)
    for i, line in enumerate(lines):
        lbb = draw.textbbox((0,0), line, font=font)
        lw2 = lbb[2] - lbb[0]
        draw.text((bx + pad + (tw - lw2)//2, by + pad + i*lh), line, fill=LINE, font=font)


# ── Floating label (coloured badge) ──────────────────────────────────────────

def _label(draw, cx, cy, text, fs, color=BLUE):
    font = _font(fs)
    bb = draw.textbbox((0,0), text, font=font)
    tw, th = bb[2]-bb[0], bb[3]-bb[1]
    pad = int(fs * 0.4)
    draw.rounded_rectangle([cx-tw//2-pad, cy-th//2-pad, cx+tw//2+pad, cy+th//2+pad],
                            radius=int(fs * 0.35), fill=color, outline=LINE, width=2)
    draw.text((cx - tw//2, cy - th//2), text, fill=WHITE, font=font)


# ── Arrow ─────────────────────────────────────────────────────────────────────

def _arrow(draw, x1, y1, x2, y2, color=LINE, lw=3):
    draw.line([x1,y1,x2,y2], fill=color, width=lw)
    angle = math.atan2(y2-y1, x2-x1)
    for side in [0.45, -0.45]:
        ax = x2 - int(18 * math.cos(angle + side))
        ay = y2 - int(18 * math.sin(angle + side))
        draw.line([x2,y2,ax,ay], fill=color, width=lw)


# ── Props ─────────────────────────────────────────────────────────────────────

def _lightbulb(draw, cx, cy, s):
    r = int(32*s); lw = max(2, int(3*s))
    draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(255,230,50), outline=LINE, width=lw)
    draw.rectangle([cx-int(11*s), cy+r-int(3*s), cx+int(11*s), cy+r+int(20*s)],
                   fill=(180,180,180), outline=LINE, width=max(1,lw-1))
    draw.line([cx-int(8*s), cy+r+int(8*s), cx+int(8*s), cy+r+int(8*s)], fill=LINE, width=max(1,lw-1))
    for a in range(0,360,45):
        rad = math.radians(a)
        x1=cx+int((r+6*s)*math.cos(rad)); y1=cy+int((r+6*s)*math.sin(rad))
        x2=cx+int((r+18*s)*math.cos(rad)); y2=cy+int((r+18*s)*math.sin(rad))
        draw.line([x1,y1,x2,y2], fill=ORANGE, width=max(1,lw-1))


def _brain(draw, cx, cy, s):
    r = int(40*s); lw = max(2, int(3*s))
    draw.ellipse([cx-r, cy-int(r*0.75), cx+r, cy+int(r*0.75)],
                 fill=(255,180,200), outline=LINE, width=lw)
    for i in range(3):
        draw.arc([cx-int(32*s), cy-int(26*s)+i*int(20*s),
                  cx+int(32*s), cy-int(6*s)+i*int(20*s)],
                 180, 360, fill=LINE, width=max(1, int(2*s)))
    draw.line([cx, cy-int(r*0.75), cx, cy+int(r*0.75)], fill=LINE, width=max(1, int(2*s)))


def _clock(draw, cx, cy, s, hour=2):
    r = int(36*s); lw = max(2, int(3*s))
    draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=WHITE, outline=LINE, width=lw)
    ang = math.radians(hour * 30 - 90)
    draw.line([cx, cy, cx+int(r*0.52*math.cos(ang)), cy+int(r*0.52*math.sin(ang))],
              fill=LINE, width=max(2, lw-1))
    draw.line([cx, cy, cx+int(r*0.75*math.cos(math.radians(-90))),
               cy+int(r*0.75*math.sin(math.radians(-90)))], fill=RED, width=max(1, lw-1))
    draw.ellipse([cx-int(4*s), cy-int(4*s), cx+int(4*s), cy+int(4*s)], fill=LINE)


def _trophy(draw, cx, cy, s):
    lw = max(2, int(3*s))
    draw.polygon([(cx-int(30*s),cy-int(42*s)), (cx+int(30*s),cy-int(42*s)),
                  (cx+int(20*s),cy), (cx-int(20*s),cy)], fill=YELLOW, outline=LINE, width=lw)
    draw.rectangle([cx-int(8*s),cy,cx+int(8*s),cy+int(24*s)], fill=(200,160,0), outline=LINE, width=lw)
    draw.rectangle([cx-int(22*s),cy+int(22*s),cx+int(22*s),cy+int(34*s)], fill=YELLOW, outline=LINE, width=lw)
    draw.arc([cx-int(30*s),cy-int(42*s),cx-int(10*s),cy], 90, 270, fill=LINE, width=lw)
    draw.arc([cx+int(10*s),cy-int(42*s),cx+int(30*s),cy], 270, 90, fill=LINE, width=lw)


def _money(draw, cx, cy, s):
    lw = max(2, int(3*s))
    draw.ellipse([cx-int(34*s), cy-int(24*s), cx+int(34*s), cy+int(34*s)],
                 fill=(46,204,113), outline=LINE, width=lw)
    draw.ellipse([cx-int(15*s), cy-int(40*s), cx+int(15*s), cy-int(20*s)],
                 fill=(46,204,113), outline=LINE, width=lw)
    draw.text((cx-int(12*s), cy-int(10*s)), "$", fill=WHITE, font=_font(int(30*s)))


# ── Scene layouts (two-figure interactions) ───────────────────────────────────
# Portrait 1080×1920: figure zone = top 12% is watermark strip, bottom 12% is banner
# Left figure A at ~25% width, Right figure B at ~75% width
# Both at same cy ~58% height so they're big and centred

def _scene_positions(w, h, s):
    """Return (ax, ay, bx, by, prop_y, label_y) that work for both orientations.

    Shorts (h>w) safe zones:
      Top 18%  — YouTube header + auto-captions area (avoid)
      Bottom 22% — YouTube title/description/audio bar (avoid)
      Right 18% — YouTube action buttons (like/share/remix) (avoid)
    """
    is_short = h > w
    cy      = int(h * 0.62)
    # Prop: below caption zone for shorts, near top for landscape
    prop_y  = int(h * 0.20) if is_short else int(h * 0.13)
    # Label: well below caption zone for shorts
    label_y = int(h * 0.32) if is_short else int(h * 0.22)
    # Right figure pulled left for shorts to avoid action buttons
    bx      = int(w * 0.70) if is_short else int(w * 0.75)
    return int(w * 0.25), cy, bx, cy, prop_y, label_y


def _half_w(w):
    """Max bubble width = 42% of canvas so two bubbles never collide."""
    return int(w * 0.42)


def _scene_hook(draw, w, h, s, bubble_fs, bubble_a, bubble_b, phase=0, label_text="WAKE UP CALL"):
    ax, ay, bx, by_, prop_y, label_y = _scene_positions(w, h, s)
    hw = _half_w(w)

    ps = s * (1.0 + 0.06 * phase)
    _clock(draw, w//2, prop_y, ps * 0.95, hour=2)
    _figure(draw, ax, ay,  s, pose="pointing_r", emotion="excited", phase=phase)
    _figure(draw, bx, by_, s, pose="shocked",    emotion="shocked", flip=True, phase=phase)
    _bubble(draw, ax, ay - int(100*s), bubble_a,
            hw, bubble_fs, tail="left", anchor="right")
    _bubble(draw, bx, by_ - int(100*s), bubble_b,
            hw, bubble_fs, tail="right", fill=(255,240,240), anchor="left")
    _arrow(draw, w//2, label_y + int(bubble_fs*0.8),
           int(w*0.40), int(h*0.52), BLUE, max(2, int(3*s)))
    _label(draw, w//2, label_y, label_text, int(bubble_fs*0.9), RED)  # draw last — always on top


def _scene_problem(draw, w, h, s, bubble_fs, bubble_a, bubble_b, phase=0, label_text="THE BLOCK"):
    ax, ay, bx, by_, prop_y, label_y = _scene_positions(w, h, s)
    hw = _half_w(w)

    ps = s * (1.0 + 0.06 * phase)
    _brain(draw, w//2, prop_y, ps * 0.9)
    _figure(draw, ax, ay,  s, pose="talking",  emotion="thinking", phase=phase)
    _figure(draw, bx, by_, s, pose="thinking", emotion="sad", flip=True, phase=phase)
    _bubble(draw, ax, ay - int(100*s), bubble_a,
            hw, bubble_fs, tail="left", anchor="right")
    _thought_bubble(draw, bx, by_ - int(100*s), bubble_b, w, bubble_fs)
    _arrow(draw, w//2, label_y + int(bubble_fs*0.8),
           int(w*0.60), int(h*0.52), PURPLE, max(2, int(3*s)))
    _label(draw, w//2, label_y, label_text, int(bubble_fs*0.9), PURPLE)  # draw last — always on top


def _scene_solution(draw, w, h, s, bubble_fs, bubble_a, bubble_b, phase=0, label_text="THE FIX"):
    ax, ay, bx, by_, prop_y, label_y = _scene_positions(w, h, s)
    hw = _half_w(w)

    ps = s * (1.0 + 0.06 * phase)
    _lightbulb(draw, w//2, prop_y, ps * 1.0)
    _figure(draw, ax, ay,  s, pose="excited",    emotion="excited", phase=phase)
    _figure(draw, bx, by_, s, pose="pointing_l", emotion="happy",   flip=True, phase=phase)
    _bubble(draw, ax, ay - int(100*s), bubble_a,
            hw, bubble_fs, tail="left", anchor="right")
    _bubble(draw, bx, by_ - int(100*s), bubble_b,
            hw, bubble_fs, tail="right", fill=(240,255,240), anchor="left")
    _arrow(draw, w//2, label_y + int(bubble_fs*0.8),
           int(w*0.40), int(h*0.52), GREEN, max(2, int(3*s)))
    _label(draw, w//2, label_y, label_text, int(bubble_fs*0.9), GREEN)  # draw last — always on top


def _scene_result(draw, w, h, s, bubble_fs, bubble_a, bubble_b, phase=0, label_text="LEVEL UP"):
    ax, ay, bx, by_, prop_y, label_y = _scene_positions(w, h, s)
    hw = _half_w(w)

    ps = s * (1.0 + 0.06 * phase)
    _trophy(draw, w//2, prop_y, ps * 0.95)
    _figure(draw, ax, ay,  s, pose="excited", emotion="excited", phase=phase)
    _figure(draw, bx, by_, s, pose="excited", emotion="excited", flip=True, phase=phase)
    _bubble(draw, ax, ay - int(100*s), bubble_a,
            hw, bubble_fs, tail="left", anchor="right")
    _bubble(draw, bx, by_ - int(100*s), bubble_b,
            hw, bubble_fs, tail="right", fill=(255,255,220), anchor="left")
    _arrow(draw, w//2, label_y + int(bubble_fs*0.8),
           int(w*0.38), int(h*0.52), ORANGE, max(2, int(3*s)))
    _arrow(draw, w//2, label_y + int(bubble_fs*0.8),
           int(w*0.62), int(h*0.52), ORANGE, max(2, int(3*s)))
    _label(draw, w//2, label_y, label_text, int(bubble_fs*0.9), GREEN)  # draw last — always on top


SCENE_FNS = [_scene_hook, _scene_problem, _scene_solution, _scene_result]


# ── Narration subtitle strip ───────────────────────────────────────────────────

def _narration_strip(draw, narration, w, h, word_start, words_per_frame, fs_base):
    """Subtitle strip showing the current narration words — only for landscape (regular) videos."""
    is_short = h > w
    if is_short:
        return  # shorts layout too dense for a subtitle strip
    words = narration.split() if narration else []
    if not words:
        return
    chunk = words[word_start : word_start + words_per_frame]
    if not chunk:
        chunk = words[-words_per_frame:]
    line = " ".join(chunk)

    fs = max(22, int(fs_base * 0.70))
    font = _font(fs)
    pad_x, pad_y = int(w * 0.04), int(h * 0.010)

    bb = draw.textbbox((0, 0), line, font=font)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]

    # Dark bar at ~72% down — below the speech bubbles, above the yellow banner (which is at ~76%)
    bar_h = th + pad_y * 2
    bar_y = int(h * 0.72)
    draw.rectangle([0, bar_y, w, bar_y + bar_h], fill=(18, 18, 30))

    # White text centred, with shadow
    tx = max(pad_x, (w - tw) // 2)
    ty = bar_y + pad_y
    draw.text((tx + 2, ty + 2), line, fill=(0, 0, 0), font=font)
    draw.text((tx, ty), line, fill=(255, 255, 255), font=font)


# ── Shot-type frame renderers ─────────────────────────────────────────────────
# Each shot type produces a genuinely different visual composition.
# This is what Trust Me Bro / Productive Peter actually do — they don't zoom
# the same image; they switch to a different scene entirely.

def _draw_banner_and_watermark(draw, text, w, h):
    bfs = max(36, w // 17)
    bfont = _font(bfs)
    bh = int(bfs * 2.1)
    by = h - bh - int(h * 0.018)
    draw.rectangle([int(w*0.03), by, int(w*0.97), by+bh], fill=YELLOW, outline=LINE, width=3)
    safe = text[:32]
    bb = draw.textbbox((0, 0), safe, font=bfont)
    tx = max(int(w*0.05), (w - (bb[2]-bb[0])) // 2)
    ty = by + (bh - (bb[3]-bb[1])) // 2
    draw.text((tx+2, ty+2), safe, fill=(100,100,100), font=bfont)
    draw.text((tx,   ty),   safe, fill=(15, 15, 15),  font=bfont)
    draw.text((int(w*0.04), int(h*0.012)), "@MindShiftProductivity",
              fill=(160, 180, 210), font=_font_r(max(20, w//46)))


def _draw_grid(draw, w, h):
    gc = (228, 236, 248)
    for i in range(0, w, max(1, w//16)): draw.line([i, 0, i, h], fill=gc, width=1)
    for i in range(0, h, max(1, h//22)): draw.line([0, i, w, i], fill=gc, width=1)


def _create_frame_wide(text, narration, w, h, scene_idx, phase, slot, word_start, wpf, bg=None):
    """Both figures — standard two-character scene."""
    img = bg.copy() if bg else Image.new("RGB", (w, h), BG)
    draw = ImageDraw.Draw(img)
    if not bg:
        _draw_grid(draw, w, h)

    s = 2.8 if h > w else 2.1
    bubble_fs = max(28, w // 28) if h > w else max(22, h // 26)
    bubble_a = ""  # voice narrates — no text bubble for speaker
    scene_type = scene_idx % 4
    rng = random.Random(scene_idx * 100 + slot)
    bubble_b = rng.choice(_REACTIONS[scene_type])
    label_text = _LABEL_POOLS[scene_type][(slot + scene_idx) % len(_LABEL_POOLS[scene_type])]

    SCENE_FNS[scene_type](draw, w, h, s, bubble_fs, bubble_a, bubble_b, phase, label_text)
    _draw_banner_and_watermark(draw, text, w, h)
    return img


def _create_frame_focus_a(text, narration, w, h, scene_idx, phase, slot, word_start, wpf, bg=None):
    """Figure A (speaker) solo — larger, left-centred. Figure B off screen."""
    img = bg.copy() if bg else Image.new("RGB", (w, h), BG)
    draw = ImageDraw.Draw(img)
    if not bg:
        _draw_grid(draw, w, h)

    s = 3.4 if h > w else 2.7
    bubble_fs = max(30, w // 24) if h > w else max(26, h // 22)
    cx = int(w * 0.38)
    cy = int(h * 0.62)
    scene_type = scene_idx % 4
    rng = random.Random(scene_idx * 100 + slot)
    label_text = _LABEL_POOLS[scene_type][(slot + scene_idx) % len(_LABEL_POOLS[scene_type])]

    bubble_text = ""  # voice narrates — figure A animates, no text bubble

    pose_map = ["pointing_r", "talking", "excited", "excited"]
    emotion_map = ["excited", "thinking", "excited", "excited"]
    _figure(draw, cx, cy, s, pose=pose_map[scene_type], emotion=emotion_map[scene_type], phase=phase)
    _bubble(draw, cx, cy - int(100*s), bubble_text, int(w*0.55), bubble_fs,
            tail="left", anchor="right")
    label_colors = [RED, PURPLE, GREEN, GREEN]
    _label(draw, int(w*0.72), int(h*0.22), label_text, int(bubble_fs*0.85), label_colors[scene_type])
    _draw_banner_and_watermark(draw, text, w, h)
    return img


def _create_frame_focus_prop(text, narration, w, h, scene_idx, phase, slot, word_start, wpf, bg=None):
    """Concept card — large prop centred + key words from narration as bold text."""
    img = bg.copy() if bg else Image.new("RGB", (w, h), BG)
    draw = ImageDraw.Draw(img)
    if not bg:
        _draw_grid(draw, w, h)

    scene_type = scene_idx % 4
    prop_s = 2.2 if h > w else 1.6
    prop_y = int(h * 0.30)
    prop_fns = [_clock, _brain, _lightbulb, _trophy]
    prop_fns[scene_type](draw, w // 2, prop_y, prop_s * (1.0 + 0.04 * phase))

    key_words = text  # text_overlay as the concept card headline
    kfs = max(44, w // 18) if h > w else max(34, h // 16)
    kfont = _font(kfs)
    max_chars = max(8, int(w * 0.70 / (kfs * 0.60)))
    lines = textwrap.wrap(key_words, width=max_chars)[:2]
    ty = int(h * 0.52)
    for line in lines:
        bb = draw.textbbox((0, 0), line, font=kfont)
        tx = max(int(w*0.04), (w - (bb[2]-bb[0])) // 2)
        for dx, dy in [(-3, 3), (3, 3), (-3, -3), (3, -3)]:
            draw.text((tx+dx, ty+dy), line, fill=(0, 0, 0), font=kfont)
        draw.text((tx, ty), line, fill=BLUE, font=kfont)
        ty += int(kfs * 1.35)

    _draw_banner_and_watermark(draw, text, w, h)
    return img


def _create_frame_focus_b(text, narration, w, h, scene_idx, phase, slot, word_start, wpf, bg=None):
    """Figure B (reactor) solo — larger, right-centred. Shows audience reaction."""
    img = bg.copy() if bg else Image.new("RGB", (w, h), BG)
    draw = ImageDraw.Draw(img)
    if not bg:
        _draw_grid(draw, w, h)

    s = 3.4 if h > w else 2.7
    bubble_fs = max(30, w // 24) if h > w else max(26, h // 22)
    cx = int(w * 0.62)
    cy = int(h * 0.62)
    scene_type = scene_idx % 4
    rng = random.Random(scene_idx * 100 + slot)
    bubble_b = rng.choice(_REACTIONS[scene_type])
    label_text = _LABEL_POOLS[scene_type][(slot + scene_idx) % len(_LABEL_POOLS[scene_type])]

    pose_map = ["shocked", "thinking", "pointing_l", "excited"]
    emotion_map = ["shocked", "sad", "happy", "excited"]
    _figure(draw, cx, cy, s, pose=pose_map[scene_type], emotion=emotion_map[scene_type],
            flip=True, phase=phase)
    bubble_fill = [(255,240,240), (240,240,255), (240,255,240), (255,255,220)]
    _bubble(draw, cx, cy - int(100*s), bubble_b, int(w*0.55), bubble_fs,
            tail="right", fill=bubble_fill[scene_type], anchor="left")
    label_colors = [RED, PURPLE, GREEN, ORANGE]
    _label(draw, int(w*0.28), int(h*0.22), label_text, int(bubble_fs*0.85), label_colors[scene_type])
    _draw_banner_and_watermark(draw, text, w, h)
    return img


_SHOT_RENDERERS = {
    "wide":       _create_frame_wide,
    "focus_a":    _create_frame_focus_a,
    "focus_prop": _create_frame_focus_prop,
    "focus_b":    _create_frame_focus_b,
}


# ── Video generation ──────────────────────────────────────────────────────────

def create_scene_video(text, bg_color, duration, output_path,
                       video_type="regular", scene_idx=0, bullets=None, narration="", slot=0):
    from config import REGULAR_VIDEO, SHORTS_VIDEO
    spec = REGULAR_VIDEO if video_type == "regular" else SHORTS_VIDEO
    w, h = spec["width"], spec["height"]
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)

    label = text[:40].upper()
    ff = _ffmpeg()
    d = duration

    # Shot sequence — genuine different compositions, not zoom tricks
    # Regular: wide → speaker solo → concept card → reactor solo → wide (27s total)
    # Shorts:  wide → speaker solo → reactor solo → wide       (14s total)
    if h > w:  # Shorts — 4 shots
        q = max(3, d // 4)
        shots = [
            ("wide",    q),
            ("focus_a", q),
            ("focus_b", q),
            ("wide",    d - 3 * q),
        ]
    else:  # Regular — 5 shots at 5-7s each
        shots = [
            ("wide",       5),
            ("focus_a",    5),
            ("focus_prop", 5),
            ("focus_b",    5),
            ("wide",       max(3, d - 20)),
        ]

    # Fetch one AI background per scene from Pollinations.ai (free, no key)
    # All 5 shots share the same background — visual consistency within a scene
    print(f"  [BG] Fetching AI background for scene {scene_idx + 1}...")
    scene_bg = _fetch_bg(text, w, h, seed=scene_idx * 7 + slot)

    sub_clips = []
    # 8-frame smooth cycle: arm rises and falls fluidly (0 → peak → 0)
    phases = [0, 0.25, 0.5, 0.75, 1, 0.75, 0.5, 0.25]
    n_frames = len(phases)

    for shot_idx, (shot_type, shot_dur) in enumerate(shots):
        shot_frames_dir = output_path.replace(".mp4", f"_s{shot_idx}_frames")
        os.makedirs(shot_frames_dir, exist_ok=True)

        renderer = _SHOT_RENDERERS[shot_type]
        for fi, phase in enumerate(phases):
            frame = renderer(label, narration, w, h, scene_idx, phase, slot, 0, 6, bg=scene_bg)
            frame.save(os.path.join(shot_frames_dir, f"f{fi:03d}.png"))

        sub_path = output_path.replace(".mp4", f"_shot{shot_idx}.mp4")
        result = subprocess.run([
            ff, "-y", "-framerate", "8",
            "-i", os.path.join(shot_frames_dir, "f%03d.png"),
            "-vf", f"loop=-1:size={n_frames}:start=0,fade=t=in:st=0:d=0.2",
            "-t", str(shot_dur),
            "-c:v", "libx264", "-preset", "ultrafast",
            "-pix_fmt", "yuv420p", "-r", "24", "-crf", "18", sub_path
        ], capture_output=True, text=True, timeout=60)

        # Cleanup shot frames immediately
        for fi in range(n_frames):
            fp = os.path.join(shot_frames_dir, f"f{fi:03d}.png")
            if os.path.exists(fp): os.remove(fp)
        try: os.rmdir(shot_frames_dir)
        except: pass

        if result.returncode == 0 and os.path.exists(sub_path) and os.path.getsize(sub_path) > 500:
            sub_clips.append(sub_path)
        else:
            print(f"  [Animate] shot {shot_idx} failed: {result.stderr[-150:]}")

    if not sub_clips:
        # Full fallback — simple single loop
        frames_dir = output_path.replace(".mp4", "_fallback_frames")
        os.makedirs(frames_dir, exist_ok=True)
        for fi, phase in enumerate(phases):
            frame = _create_frame_wide(label, narration, w, h, scene_idx, phase, slot, 0, 6, bg=scene_bg)
            frame.save(os.path.join(frames_dir, f"f{fi:03d}.png"))
        subprocess.run([
            ff, "-y", "-framerate", "8",
            "-i", os.path.join(frames_dir, "f%03d.png"),
            "-vf", f"loop=-1:size={n_frames}:start=0", "-t", str(d),
            "-c:v", "libx264", "-preset", "ultrafast",
            "-pix_fmt", "yuv420p", "-r", "24", "-crf", "18", output_path
        ], capture_output=True, text=True, timeout=120)
        for fi in range(n_frames):
            fp = os.path.join(frames_dir, f"f{fi:03d}.png")
            if os.path.exists(fp): os.remove(fp)
        try: os.rmdir(frames_dir)
        except: pass
        return output_path

    # Concatenate all shots into final scene video
    concat_txt = output_path.replace(".mp4", "_concat.txt")
    with open(concat_txt, "w") as f:
        for p in sub_clips:
            f.write(f"file '{p}'\n")
    subprocess.run([
        ff, "-y", "-f", "concat", "-safe", "0",
        "-i", concat_txt, "-c", "copy", output_path
    ], capture_output=True, text=True, timeout=60)

    # Cleanup sub-clips and concat list
    for p in sub_clips:
        if os.path.exists(p): os.remove(p)
    if os.path.exists(concat_txt): os.remove(concat_txt)

    return output_path


def create_all_scenes(scenes, output_dir, video_type="regular", slot=0):
    os.makedirs(output_dir, exist_ok=True)
    paths = []
    for i, scene in enumerate(scenes):
        out = os.path.join(output_dir, f"scene_{scene['scene_number']:02d}.mp4")
        print(f"  [Animate] Scene {scene['scene_number']}: {scene['text_overlay']}")
        create_scene_video(
            text=scene["text_overlay"], bg_color="#F5F8FC",
            duration=scene["duration_seconds"], output_path=out,
            video_type=video_type, scene_idx=i,
            narration=scene.get("narration", ""), slot=slot,
        )
        paths.append(out)
    return paths
