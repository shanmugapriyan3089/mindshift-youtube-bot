"""
Productive Peter style — TWO stick figures interacting like a cartoon.
Figure A explains/teaches, Figure B reacts (shocked/curious/excited).
Large figures, speech bubbles between them, props as context.
"""
import os, math, subprocess, shutil, textwrap, random
from PIL import Image, ImageDraw, ImageFont

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

    ps = s * (1.0 + 0.06 * phase)  # prop pulses slightly on phase 1
    _clock(draw, w//2, prop_y, ps * 0.95, hour=2)
    _label(draw, w//2, label_y, label_text, int(bubble_fs*0.9), RED)

    _figure(draw, ax, ay,  s, pose="pointing_r", emotion="excited", phase=phase)
    _figure(draw, bx, by_, s, pose="shocked",    emotion="shocked", flip=True, phase=phase)

    _bubble(draw, ax, ay - int(100*s), bubble_a,
            hw, bubble_fs, tail="left", anchor="right")
    _bubble(draw, bx, by_ - int(100*s), bubble_b,
            hw, bubble_fs, tail="right", fill=(255,240,240), anchor="left")

    _arrow(draw, w//2, label_y + int(bubble_fs*0.8),
           int(w*0.40), int(h*0.52), BLUE, max(2, int(3*s)))


def _scene_problem(draw, w, h, s, bubble_fs, bubble_a, bubble_b, phase=0, label_text="THE BLOCK"):
    ax, ay, bx, by_, prop_y, label_y = _scene_positions(w, h, s)
    hw = _half_w(w)

    ps = s * (1.0 + 0.06 * phase)
    _brain(draw, w//2, prop_y, ps * 0.9)
    _label(draw, w//2, label_y, label_text, int(bubble_fs*0.9), PURPLE)

    _figure(draw, ax, ay,  s, pose="talking",  emotion="thinking", phase=phase)
    _figure(draw, bx, by_, s, pose="thinking", emotion="sad", flip=True, phase=phase)

    _bubble(draw, ax, ay - int(100*s), bubble_a,
            hw, bubble_fs, tail="left", anchor="right")
    _thought_bubble(draw, bx, by_ - int(100*s), bubble_b, w, bubble_fs)

    _arrow(draw, w//2, label_y + int(bubble_fs*0.8),
           int(w*0.60), int(h*0.52), PURPLE, max(2, int(3*s)))


def _scene_solution(draw, w, h, s, bubble_fs, bubble_a, bubble_b, phase=0, label_text="THE FIX"):
    ax, ay, bx, by_, prop_y, label_y = _scene_positions(w, h, s)
    hw = _half_w(w)

    ps = s * (1.0 + 0.06 * phase)
    _lightbulb(draw, w//2, prop_y, ps * 1.0)
    _label(draw, w//2, label_y, label_text, int(bubble_fs*0.9), GREEN)

    _figure(draw, ax, ay,  s, pose="excited",    emotion="excited", phase=phase)
    _figure(draw, bx, by_, s, pose="pointing_l", emotion="happy",   flip=True, phase=phase)

    _bubble(draw, ax, ay - int(100*s), bubble_a,
            hw, bubble_fs, tail="left", anchor="right")
    _bubble(draw, bx, by_ - int(100*s), bubble_b,
            hw, bubble_fs, tail="right", fill=(240,255,240), anchor="left")

    _arrow(draw, w//2, label_y + int(bubble_fs*0.8),
           int(w*0.40), int(h*0.52), GREEN, max(2, int(3*s)))


def _scene_result(draw, w, h, s, bubble_fs, bubble_a, bubble_b, phase=0, label_text="LEVEL UP"):
    ax, ay, bx, by_, prop_y, label_y = _scene_positions(w, h, s)
    hw = _half_w(w)

    ps = s * (1.0 + 0.06 * phase)
    _trophy(draw, w//2, prop_y, ps * 0.95)
    _label(draw, w//2, label_y, label_text, int(bubble_fs*0.9), GREEN)

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


SCENE_FNS = [_scene_hook, _scene_problem, _scene_solution, _scene_result]


# ── Full frame ────────────────────────────────────────────────────────────────

def _create_frame(text, narration, w, h, scene_idx, phase=0, slot=0):
    img = Image.new("RGB", (w, h), BG)
    draw = ImageDraw.Draw(img)

    # Notebook grid lines
    gc = (228, 236, 248)
    for i in range(0, w, max(1, w//16)): draw.line([i,0,i,h], fill=gc, width=1)
    for i in range(0, h, max(1, h//22)): draw.line([0,i,w,i], fill=gc, width=1)

    s = 2.5 if h > w else 1.9
    bubble_fs = max(28, w // 28) if h > w else max(22, h // 26)

    # Dynamic bubble text from actual script narration
    words = narration.split() if narration else text.split()
    bubble_a = " ".join(words[:9]) if words else text[:40]
    scene_type = scene_idx % 4
    # Seed reactions/labels consistently per scene so they don't flicker between frames
    rng = random.Random(scene_idx * 100 + slot)
    bubble_b = rng.choice(_REACTIONS[scene_type])
    label_text = _LABEL_POOLS[scene_type][(slot + scene_idx) % len(_LABEL_POOLS[scene_type])]

    SCENE_FNS[scene_type](draw, w, h, s, bubble_fs, bubble_a, bubble_b, phase, label_text)

    # Yellow banner
    bfs = max(36, w // 17)
    bfont = _font(bfs)
    bh = int(bfs * 2.1)
    by = h - bh - int(h * 0.018)
    draw.rectangle([int(w*0.03), by, int(w*0.97), by+bh], fill=YELLOW, outline=LINE, width=3)
    safe = text[:32]
    bb = draw.textbbox((0,0), safe, font=bfont)
    tx = max(int(w*0.05), (w - (bb[2]-bb[0])) // 2)
    ty = by + (bh - (bb[3]-bb[1])) // 2
    draw.text((tx+2, ty+2), safe, fill=(100,100,100), font=bfont)
    draw.text((tx,   ty),   safe, fill=(15,15,15),    font=bfont)

    # Watermark — kept in safe zone (top-left, away from Shorts action buttons)
    draw.text((int(w*0.04), int(h*0.012)), "@MindShiftProductivity",
              fill=(160, 180, 210), font=_font_r(max(20, w//46)))

    return img


# ── Video generation ──────────────────────────────────────────────────────────

def create_scene_video(text, bg_color, duration, output_path,
                       video_type="regular", scene_idx=0, bullets=None, narration="", slot=0):
    from config import REGULAR_VIDEO, SHORTS_VIDEO
    spec = REGULAR_VIDEO if video_type == "regular" else SHORTS_VIDEO
    w, h = spec["width"], spec["height"]
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)

    label = text[:40].upper()
    frames_dir = output_path.replace(".mp4", "_frames")
    os.makedirs(frames_dir, exist_ok=True)

    # 4 animation frames: arm down, arm up, arm down, arm up (2 fps cycle → 2s loop)
    phases = [0, 1, 0, 1]
    for fi, phase in enumerate(phases):
        frame = _create_frame(label, narration, w, h, scene_idx, phase, slot)
        frame.save(os.path.join(frames_dir, f"f{fi:03d}.png"))

    # Loop the 4-frame animation for the full scene duration at 24fps output
    result = subprocess.run([
        _ffmpeg(), "-y", "-framerate", "2",
        "-i", os.path.join(frames_dir, "f%03d.png"),
        "-vf", f"loop=-1:size=4:start=0",
        "-t", str(duration),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "24", "-crf", "18", output_path
    ], capture_output=True, text=True, timeout=90)

    # Cleanup temp frames
    for fi in range(len(phases)):
        fp = os.path.join(frames_dir, f"f{fi:03d}.png")
        if os.path.exists(fp): os.remove(fp)
    try: os.rmdir(frames_dir)
    except: pass

    if result.returncode != 0: print(f"  [FFmpeg]: {result.stderr[-300:]}")
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
