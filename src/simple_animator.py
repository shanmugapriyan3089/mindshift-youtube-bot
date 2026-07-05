"""
Productive Peter style — TWO stick figures interacting like a cartoon.
Figure A explains/teaches, Figure B reacts (shocked/curious/excited).
Large figures, speech bubbles between them, props as context.
"""
import os, math, subprocess, shutil, textwrap, random
from PIL import Image, ImageDraw, ImageFont


# ── Scene gradient backgrounds (clean, no API) ────────────────────────────────
# Soft pastel top → white bottom, one per scene type (hook/problem/solution/result)
_SCENE_GRADIENTS = [
    ((255, 243, 228), (255, 255, 255)),  # hook     — warm cream
    ((228, 240, 255), (255, 255, 255)),  # problem  — cool sky blue
    ((228, 255, 242), (255, 255, 255)),  # solution — fresh mint
    ((255, 252, 228), (255, 255, 255)),  # result   — soft gold
]


def _make_gradient_bg(w: int, h: int, scene_type: int) -> "Image.Image":
    """Instant clean gradient — no network call, consistent, professional."""
    c1, c2 = _SCENE_GRADIENTS[scene_type % 4]
    col = Image.new("RGB", (1, h))
    pix = col.load()
    for y in range(h):
        t = y / max(1, h - 1)
        pix[0, y] = (
            int(c1[0] + (c2[0] - c1[0]) * t),
            int(c1[1] + (c2[1] - c1[1]) * t),
            int(c1[2] + (c2[2] - c1[2]) * t),
        )
    return col.resize((w, h), Image.NEAREST)


# ── Environment backgrounds (Trust Me Bro style — world matches narration) ────
# Each scene gets a fully illustrated environment instead of a flat gradient.
# The correct env is detected from narration keywords so the world around the
# characters reflects what the narrator is saying at every moment.

def _grad_band(draw, w, y1, y2, c1, c2):
    """Fill a horizontal band with a linear gradient from c1 (top) to c2 (bottom)."""
    for y in range(y1, y2):
        t = (y - y1) / max(1, y2 - y1)
        draw.line([(0, y), (w, y)], fill=(
            int(c1[0] + (c2[0]-c1[0])*t),
            int(c1[1] + (c2[1]-c1[1])*t),
            int(c1[2] + (c2[2]-c1[2])*t),
        ))


def _cloud(draw, cx, cy, r):
    """Fluffy white cloud cluster centred at (cx, cy) with approximate radius r."""
    for dx, dy, cr in [(-int(r*.45), int(r*.15), int(r*.62)),
                       (0, 0, r),
                       (int(r*.45), int(r*.1), int(r*.68)),
                       (-int(r*.2), -int(r*.3), int(r*.48)),
                       (int(r*.2), -int(r*.25), int(r*.45))]:
        draw.ellipse([cx+dx-cr, cy+dy-int(cr*.65), cx+dx+cr, cy+dy+int(cr*.65)],
                     fill=(255, 255, 255))


def _sine_hill(draw, w, h, y_frac, color, amp=0.04, phase=0.0):
    """Rolling hill polygon using a sine curve."""
    y0 = int(h * y_frac)
    pts = [(0, h)]
    for i in range(41):
        x = int(w * i / 40)
        y = y0 + int(h * amp * math.sin(math.pi * 2.1 * i / 40 + phase))
        pts.append((x, y))
    pts.append((w, h))
    draw.polygon(pts, fill=color)


def _env_sky_hills(draw, w, h):
    """Default: sunny day with rolling green hills — positive/motivational content."""
    _grad_band(draw, w, 0, int(h*.60), (168, 218, 245), (220, 240, 255))
    _cloud(draw, int(w*.18), int(h*.10), int(w*.07))
    _cloud(draw, int(w*.62), int(h*.07), int(w*.06))
    _cloud(draw, int(w*.82), int(h*.15), int(w*.05))
    _sine_hill(draw, w, h, .50, (145, 190, 145), .05, 0.0)
    _sine_hill(draw, w, h, .60, (95, 170, 100),  .04, 1.2)
    _grad_band(draw, w, int(h*.67), h, (85, 165, 90), (65, 140, 70))


def _env_forest(draw, w, h):
    """Forest/jungle clearing — for nature, outside, park, escape content."""
    _grad_band(draw, w, 0, int(h*.38), (175, 220, 240), (205, 235, 248))
    draw.rectangle([0, 0, w, int(h*.22)], fill=(55, 110, 55))
    _grad_band(draw, w, int(h*.20), int(h*.45), (190, 230, 190), (215, 245, 205))
    for frac in [.08, .20, .35, .65, .80, .93]:
        tx = int(w * frac)
        tw = max(18, int(w * .036))
        for di in range(-tw, tw+1):
            shade = max(0.0, 1.0 - (abs(di)/tw)**2 * .35)
            draw.line([(tx+di, 0), (tx+di, int(h*.72))],
                      fill=(int(185*shade), int(145*shade), int(90*shade)))
    _grad_band(draw, w, int(h*.62), h, (145, 200, 115), (90, 155, 70))
    for r_off, col in [(int(w*.22), (185, 225, 145)),
                       (int(w*.14), (200, 235, 160)),
                       (int(w*.08), (215, 242, 175))]:
        draw.ellipse([w//2-r_off, int(h*.68), w//2+r_off, int(h*.80)], fill=col)
    for bx, bw2 in [(int(w*.03), int(w*.14)), (int(w*.83), int(w*.16)), (int(w*.16), int(w*.10))]:
        by = int(h*.70)
        for dx, dy, br, col in [(0, 0, int(bw2*.5), (85, 165, 70)),
                                 (-int(bw2*.3), int(bw2*.15), int(bw2*.4), (100, 178, 85)),
                                 (int(bw2*.3), int(bw2*.1), int(bw2*.45), (75, 152, 62))]:
            draw.ellipse([bx+dx-br, by+dy-br, bx+dx+br, by+dy+br], fill=col)


def _env_night_room(draw, w, h):
    """Dark bedroom / 3am thoughts — insomnia, anxiety at night content."""
    _grad_band(draw, w, 0, h, (18, 22, 52), (28, 32, 72))
    wx1, wy1, wx2, wy2 = int(w*.72), int(h*.08), int(w*.92), int(h*.32)
    draw.rounded_rectangle([wx1, wy1, wx2, wy2], radius=4,
                            fill=(28, 40, 80), outline=(80, 95, 130), width=3)
    mx, my = (wx1+wx2)//2, wy1+int((wy2-wy1)*.35)
    mr = int((wx2-wx1)*.22)
    draw.ellipse([mx-mr, my-mr, mx+mr, my+mr], fill=(240, 235, 200))
    for gr, gc in [(mr+10, (225, 220, 190)), (mr+20, (195, 190, 162)), (mr+34, (155, 150, 125))]:
        draw.ellipse([mx-gr, my-gr, mx+gr, my+gr], outline=gc, width=2)
    rng2 = random.Random(7)
    for _ in range(22):
        sx = rng2.randint(0, max(1, wx1-10))
        sy = rng2.randint(0, int(h*.45))
        sr = rng2.randint(1, 3)
        br = rng2.randint(180, 240)
        draw.ellipse([sx-sr, sy-sr, sx+sr, sy+sr], fill=(br, br, br))
    _grad_band(draw, w, int(h*.80), h, (45, 32, 22), (35, 24, 15))
    for lx in range(0, w, max(1, w//8)):
        draw.line([(lx, int(h*.80)), (lx+w//16, h)], fill=(55, 40, 28), width=2)


def _env_brain_neural(draw, w, h):
    """Neural / brain space — dark purple with glowing network nodes.
    Used for: neuroscience, dopamine, cortisol, psychology research content."""
    _grad_band(draw, w, 0, h, (28, 18, 65), (42, 28, 95))
    nodes = [(int(w*.12), int(h*.18)), (int(w*.85), int(h*.22)),
             (int(w*.25), int(h*.45)), (int(w*.72), int(h*.38)),
             (int(w*.15), int(h*.72)), (int(w*.80), int(h*.68)),
             (int(w*.48), int(h*.15)), (int(w*.55), int(h*.80))]
    for ni, nj in [(0,2),(1,3),(2,4),(3,5),(0,6),(1,6),(4,7),(5,7),(2,3),(6,3)]:
        draw.line([nodes[ni], nodes[nj]], fill=(70, 50, 148), width=1)
    for i, (nx, ny) in enumerate(nodes):
        nr = max(7, int(min(w, h)*.020)) + (i%3)*3
        for gd, gc in [(nr+14, (55, 35, 130)), (nr+7, (75, 50, 155))]:
            draw.ellipse([nx-gd, ny-gd, nx+gd, ny+gd], outline=gc, width=2)
        nc = [(130, 100, 220), (150, 120, 240), (110, 85, 200)][i%3]
        draw.ellipse([nx-nr, ny-nr, nx+nr, ny+nr], fill=nc)
        cr2 = max(2, nr//3)
        draw.ellipse([nx-cr2, ny-cr2, nx+cr2, ny+cr2], fill=(200, 185, 255))
    for gr, gc in [(int(w*.30), (85, 55, 185)), (int(w*.18), (105, 70, 205)), (int(w*.10), (125, 85, 230))]:
        draw.ellipse([w//2-gr, int(h*.55), w//2+gr, int(h*.85)], outline=gc, width=3)


def _env_warm_indoor(draw, w, h):
    """Warm classroom / study room — teaching, learning, self-help content."""
    _grad_band(draw, w, 0, int(h*.72), (245, 235, 215), (230, 220, 200))
    _grad_band(draw, w, int(h*.72), h, (185, 145, 95), (165, 128, 80))
    for lx in range(0, w, max(1, w//10)):
        draw.line([(lx, int(h*.72)), (lx+w//16, h)], fill=(155, 118, 70), width=1)
    draw.rectangle([0, int(h*.72), w, int(h*.745)], fill=(200, 175, 140))
    wx1, wy1, wx2, wy2 = int(w*.05), int(h*.08), int(w*.25), int(h*.52)
    draw.rounded_rectangle([wx1, wy1, wx2, wy2], radius=6,
                            fill=(195, 225, 245), outline=(160, 145, 120), width=4)
    draw.line([(wx1, (wy1+wy2)//2), (wx2, (wy1+wy2)//2)], fill=(160, 145, 120), width=3)
    draw.line([(wx1+(wx2-wx1)//2, wy1), (wx1+(wx2-wx1)//2, wy2)], fill=(160, 145, 120), width=3)
    bx1, by1, bx2, by2 = int(w*.62), int(h*.06), int(w*.97), int(h*.50)
    draw.rounded_rectangle([bx1, by1, bx2, by2], radius=4,
                            fill=(48, 72, 52), outline=(80, 60, 40), width=5)
    for mk_y in [by1+int((by2-by1)*.3), by1+int((by2-by1)*.6)]:
        draw.line([(bx1+int((bx2-bx1)*.1), mk_y), (bx1+int((bx2-bx1)*.9), mk_y)],
                  fill=(190, 190, 185), width=max(1, int(h*.007)))


def _env_storm(draw, w, h):
    """Stormy dramatic sky — anxiety, fear, overwhelm, panic content."""
    _grad_band(draw, w, 0, int(h*.70), (55, 62, 88), (82, 89, 115))
    for cx_, cy_, cr_, col in [(int(w*.15), int(h*.12), int(w*.14), (72, 75, 95)),
                                (int(w*.45), int(h*.08), int(w*.18), (65, 69, 89)),
                                (int(w*.78), int(h*.14), int(w*.15), (70, 73, 93))]:
        for dx, dy, cr2 in [(-int(cr_*.4), int(cr_*.15), int(cr_*.6)),
                             (0, 0, cr_),
                             (int(cr_*.4), int(cr_*.08), int(cr_*.65))]:
            draw.ellipse([cx_+dx-cr2, cy_+dy-int(cr2*.6),
                          cx_+dx+cr2, cy_+dy+int(cr2*.6)], fill=col)
    _grad_band(draw, w, int(h*.68), h, (62, 67, 55), (48, 52, 42))
    for px in [int(w*.20), int(w*.55), int(w*.80)]:
        pw, ph = int(w*.11), int(h*.025)
        draw.ellipse([px-pw, int(h*.78), px+pw, int(h*.78)+ph], fill=(75, 82, 108))
    for ri in range(0, w, max(1, w//28)):
        draw.line([(ri, 0), (ri-int(h*.025), int(h*.65))], fill=(115, 125, 155), width=1)


def _env_desert(draw, w, h):
    """Desert / open isolation — alone, empty, lonely, disconnected content."""
    _grad_band(draw, w, 0, int(h*.52), (105, 185, 232), (162, 215, 245))
    _cloud(draw, int(w*.75), int(h*.12), int(w*.07))
    _grad_band(draw, w, int(h*.50), int(h*.54), (218, 208, 182), (192, 176, 140))
    _grad_band(draw, w, int(h*.52), h, (192, 175, 135), (172, 155, 115))
    _sine_hill(draw, w, h, .52, (185, 168, 130), .011, .5)


_ENV_FNS = {
    "sky_hills":    _env_sky_hills,
    "forest":       _env_forest,
    "night_room":   _env_night_room,
    "brain_neural": _env_brain_neural,
    "warm_indoor":  _env_warm_indoor,
    "storm":        _env_storm,
    "desert":       _env_desert,
}


def _detect_env(narration: str, scene_type: int) -> str:
    """Map narration keywords to the correct illustrated environment."""
    n = narration.lower()
    if any(k in n for k in ("night", "3am", "2am", "sleep", "bed", "insomnia",
                              "midnight", "awake", "lying", "restless", "can't sleep")):
        return "night_room"
    if any(k in n for k in ("forest", "jungle", "tree", "nature", "outside", "park",
                              "garden", "woods", "fresh air")):
        return "forest"
    if any(k in n for k in ("brain", "neuron", "cortisol", "dopamine", "amygdala",
                              "prefrontal", "neural", "neuroscience", "brain scan",
                              "neurons fire", "brain chemistry")):
        return "brain_neural"
    if any(k in n for k in ("anxiety", "panic", "fear", "overwhelm", "catastroph",
                              "spiral", "dread", "phobia", "terror", "worst case")):
        return "storm"
    if any(k in n for k in ("alone", "isolated", "empty", "hollow", "numb", "desert",
                              "barren", "disconnected", "lonely", "invisible")):
        return "desert"
    if any(k in n for k in ("work", "office", "job", "boss", "deadline", "meeting",
                              "teach", "learn", "class", "school", "explain", "student")):
        return "warm_indoor"
    return ("sky_hills", "brain_neural", "sky_hills", "sky_hills")[scene_type % 4]


def _make_environment_bg(narration: str, w: int, h: int, scene_type: int) -> "Image.Image":
    """Return a fully illustrated background whose world matches the narration.
    Replaces the old flat gradient — the environment changes every scene."""
    img = Image.new("RGB", (w, h), (200, 220, 240))
    draw = ImageDraw.Draw(img)
    _ENV_FNS.get(_detect_env(narration, scene_type), _env_sky_hills)(draw, w, h)
    return img


# ── Costume overlays (Trust Me Bro style: character outfit matches content) ───
# Called AFTER _figure() so the costume draws on top of the stick figure.

def _costume_explorer(draw, cx, cy, s):
    """Pith / explorer helmet — for journey, discover, history content."""
    hy = cy - int(s*125)
    brim_w, brim_h = int(s*46), int(s*9)
    draw.ellipse([cx-brim_w, hy-brim_h, cx+brim_w, hy+brim_h],
                 fill=(195, 162, 95), outline=LINE, width=max(2, int(2.5*s)))
    dome_w, dome_h = int(s*30), int(s*22)
    draw.ellipse([cx-dome_w, hy-dome_h-brim_h+int(s*2), cx+dome_w, hy+brim_h-int(s*2)],
                 fill=(210, 178, 108), outline=LINE, width=max(2, int(2.5*s)))
    draw.arc([cx-dome_w+int(s*4), hy-dome_h+int(s*8), cx+dome_w-int(s*4), hy+int(s*5)],
             200, 340, fill=(175, 145, 78), width=max(1, int(1.5*s)))


def _costume_teacher(draw, cx, cy, s):
    """Graduation mortarboard cap — for teaching, class, education content."""
    hy = cy - int(s*125)
    cap_w = int(s*36)
    draw.polygon([(cx-cap_w, hy), (cx+cap_w, hy),
                  (cx+int(cap_w*.82), hy-int(s*8)), (cx-int(cap_w*.82), hy-int(s*8))],
                 fill=(28, 28, 28), outline=LINE, width=max(1, int(2*s)))
    draw.rectangle([cx-int(s*13), hy-int(s*8)-int(s*14), cx+int(s*13), hy-int(s*8)],
                   fill=(28, 28, 28), outline=LINE, width=max(1, int(2*s)))
    draw.line([(cx+int(cap_w*.5), hy-int(s*4)), (cx+int(cap_w*.5)+int(s*8), hy+int(s*12))],
              fill=(220, 180, 30), width=max(2, int(2*s)))


def _costume_glasses(draw, cx, cy, s):
    """Round scientist glasses over the figure's eyes."""
    ey = cy - int(96*s)
    r = int(10*s)
    for ex in [cx-int(10*s), cx+int(10*s)]:
        draw.ellipse([ex-r, ey-r, ex+r, ey+r], outline=(40, 40, 40), width=max(2, int(2*s)))
    draw.line([(cx-int(10*s)+r, ey), (cx+int(10*s)-r, ey)],
              fill=(40, 40, 40), width=max(1, int(1.5*s)))


def _costume_suit(draw, cx, cy, s):
    """Suit collar + tie — for work, office, career content."""
    hb_y = cy - int(53*s)
    cy_ = hb_y + int(s*8)
    draw.polygon([(cx, cy_), (cx-int(s*12), cy_+int(s*10)), (cx, cy_+int(s*22))],
                 fill=(240, 240, 240), outline=LINE, width=max(1, int(1.5*s)))
    draw.polygon([(cx, cy_), (cx+int(s*12), cy_+int(s*10)), (cx, cy_+int(s*22))],
                 fill=(240, 240, 240), outline=LINE, width=max(1, int(1.5*s)))
    draw.polygon([(cx, cy_+int(s*15)), (cx-int(s*6), cy_+int(s*24)),
                  (cx, cy+int(s*20)), (cx+int(s*6), cy_+int(s*24))],
                 fill=RED, outline=LINE, width=max(1, int(1.5*s)))


_COSTUME_FNS = {
    "explorer": _costume_explorer,
    "teacher":  _costume_teacher,
    "glasses":  _costume_glasses,
    "suit":     _costume_suit,
}


def _detect_costume(narration: str) -> str:
    n = narration.lower()
    if any(k in n for k in ("research", "study", "experiment", "psychologist",
                              "scientist", "professor", "found that", "according to",
                              "clinical", "data", "proven", "survey", "neuroscience")):
        return "glasses"
    if any(k in n for k in ("teach", "lesson", "learn", "school", "class",
                              "education", "student", "explain", "understand", "knowledge")):
        return "teacher"
    if any(k in n for k in ("explore", "journey", "adventure", "discover",
                              "ancient", "history", "origin", "seek", "path", "map")):
        return "explorer"
    if any(k in n for k in ("work", "office", "career", "professional", "business",
                              "job", "boss", "corporate", "meeting", "deadline")):
        return "suit"
    return "default"


def _apply_costume(draw, cx, cy, s, narration: str):
    """Draw costume overlay on a figure at (cx, cy). Always call AFTER _figure()."""
    fn = _COSTUME_FNS.get(_detect_costume(narration))
    if fn:
        fn(draw, cx, cy, s)


def _draw_ground_shadow(draw, cx, cy, s):
    """Soft ellipse shadow on the ground beneath each character — adds depth."""
    foot_y = cy + int(96 * s)
    sw = int(52 * s)
    sh = int(10 * s)
    for i, (r_off, col) in enumerate([(sw, (0,0,0,45)), (int(sw*.7), (0,0,0,60)), (int(sw*.4), (0,0,0,75))]):
        # approximate alpha with grey blend — no RGBA needed
        grey = 180 + i * 22
        draw.ellipse([cx-r_off, foot_y-sh, cx+r_off, foot_y+sh], fill=(grey, grey, grey))


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

BG       = (245, 248, 252)
LINE     = (15,  15,  15)
YELLOW   = (255, 214,   0)
RED      = (220,  50,  50)
BLUE     = ( 41, 128, 185)
GREEN    = ( 39, 174,  96)
ORANGE   = (230, 126,  34)
PURPLE   = (142,  68, 173)
WHITE    = (255, 255, 255)
LAVENDER = (123, 104, 238)   # Wise Joe contemplation palette
SOFT_INDIGO = (100,  90, 200)

# ── Keyword-driven B-figure reaction pools ────────────────────────────────────
# Each pool maps to a SPECIFIC emotional experience, not generic reactions.
# Figure B mirrors the viewer's psychological state — they are the audience proxy.

# Viewer recognizes themselves in the struggle being described
_REACT_STRUGGLE   = ["I feel this...", "This is me every day...", "Why can't I stop?!",
                     "I hate this feeling", "This is exhausting...", "Every. Single. Time.",
                     "Why does this keep happening?", "I'm so tired of this"]

# Viewer is skeptical but the science is convincing them
_REACT_SKEPTICAL  = ["Wait... really?", "That can't be right...", "Hmm. Actually...",
                     "I never thought of it like that", "No way...", "Huh. Interesting.",
                     "That's... actually true", "Ok that makes sense"]

# Viewer has a sudden realization — the "aha" moment
_REACT_REALIZATION= ["OH. That's why!!", "This explains EVERYTHING!", "THAT'S what happens!",
                     "I never knew this!", "Wait — so THAT'S the reason?!",
                     "This changes everything!", "Oh my god...", "It all makes sense now"]

# Viewer sees themselves in a pattern ("this is literally me")
_REACT_MIRROR     = ["This is literally me", "I do this ALL the time", "I thought I was the only one",
                     "Me every single morning", "My whole life explained",
                     "I've done this SO many times", "This is uncomfortably accurate",
                     "How does this know me so well"]

# Viewer is motivated — ready to apply the fix
_REACT_TRANSFORM  = ["I'm trying this TODAY", "This actually works!", "Why didn't I know sooner?",
                     "Starting right now", "This is what I needed",
                     "Ok I'm doing this", "Finally an answer", "This is the one"]


def _pick_reaction(narration: str, scene_type: int, rng: random.Random) -> str:
    """Choose Figure B's reaction based on what the narration is describing.
    Research: reactions must mirror the viewer's emotional state — not react to audio timing."""
    n = narration.lower()

    # Struggle keywords → viewer in pain/stuck/frustrated
    if any(k in n for k in ("stuck", "can't stop", "loop", "trap", "fail", "quit", "struggle",
                             "anxiety", "stress", "cortisol", "exhausted", "procrastin",
                             "replay", "spiral", "overthink", "freeze", "paralyz")):
        return rng.choice(_REACT_STRUGGLE)

    # Science/stat keywords → skeptical viewer being convinced
    if any(k in n for k in ("studies show", "research", "percent", "scientists", "study",
                             "science", "data", "proven", "psychologist", "brain scan",
                             "neuroscience", "documented", "clinical")):
        return rng.choice(_REACT_SKEPTICAL)

    # Revelation keywords → the "aha" moment
    if any(k in n for k in ("the reason", "here's why", "this is because", "what actually",
                             "the truth", "what most people", "the real cause",
                             "not willpower", "not laziness", "not your fault", "it's not")):
        return rng.choice(_REACT_REALIZATION)

    # Relatable experience keywords → mirror the viewer's identity
    if any(k in n for k in ("most people", "everyone", "you've done", "have you ever",
                             "you know the feeling", "sound familiar", "you've been",
                             "you already know", "you do this", "if you're")):
        return rng.choice(_REACT_MIRROR)

    # Fix/solution keywords → viewer getting motivated
    if any(k in n for k in ("the fix", "solution", "step ", "instead", "try this",
                             "start ", "change ", "works", "effective", "you can",
                             "pattern interrupt", "here is how", "the way to")):
        return rng.choice(_REACT_TRANSFORM)

    # Fallback to scene_type pool
    return rng.choice(_REACTIONS[scene_type])


def _detect_content_emotion(narration: str) -> tuple:
    """Return (pose_A, emotion_A, pose_B, emotion_B) driven by narration keywords.
    Figure A = teacher/speaker. Figure B = viewer/reactor.
    This is what makes the figures visually react to the content instead of looping the same 4 poses."""
    n = narration.lower() if narration else ""

    # PAIN / STRUGGLE — viewer is stuck, suffering, exhausted
    if any(k in n for k in ("stuck", "can't stop", "loop", "trap", "fail", "quit",
                              "exhaust", "procrastin", "replay", "spiral", "overthink",
                              "freeze", "paralyze", "hurt", "pain", "empty", "alone",
                              "tired", "guilt", "shame", "worthless", "hopeless",
                              "dread", "miserable", "cry", "suffer", "drain")):
        return ("talking", "sad", "shocked", "sad")

    # FEAR / PANIC — high-arousal, threat response
    if any(k in n for k in ("fear", "panic", "scared", "threat", "danger", "alarm",
                              "fight or flight", "survival mode", "triggered", "nervous",
                              "amygdala", "cortisol spike", "stress response")):
        return ("shocked", "shocked", "shocked", "shocked")

    # REALIZATION / AHA — the hidden truth being revealed
    if any(k in n for k in ("the reason", "here's why", "this is because", "what actually",
                              "the truth is", "not willpower", "not laziness", "not your fault",
                              "turns out", "secretly", "hidden", "what nobody tells",
                              "what most people", "the real cause")):
        return ("pointing_r", "excited", "shocked", "shocked")

    # SCIENCE / TEACHING — explaining the mechanism
    if any(k in n for k in ("research", "percent", "study", "psychology", "neuroscience",
                              "dopamine", "cortisol", "prefrontal", "psychologist",
                              "studies show", "data", "proven", "clinical", "brain scan",
                              "experiment", "scientists", "according to")):
        return ("pointing_l", "happy", "thinking", "thinking")

    # SOLUTION / ACTION — steps, fixes, methods
    if any(k in n for k in ("step ", "the fix", "solution", "try this", "instead",
                              "here is how", "the way to", "method", "technique",
                              "pattern interrupt", "what works", "actually works",
                              "practice this", "do this", "start with")):
        return ("pointing_l", "happy", "excited", "excited")

    # MOTIVATION / RESULT — transformation, success
    if any(k in n for k in ("success", "achieve", "win", "free", "better", "transform",
                              "level up", "possible", "accomplish", "progress",
                              "finally", "proud", "changed", "rewire", "break free",
                              "new version", "subscribe", "life changes")):
        return ("excited", "excited", "excited", "excited")

    # THINKING / REFLECTIVE — questions, self-awareness
    if any(k in n for k in ("what if", "imagine", "think about", "have you ever",
                              "consider", "wonder", "reflect", "when was the last",
                              "how often", "ask yourself", "notice that", "pay attention")):
        return ("thinking", "thinking", "thinking", "thinking")

    # DEFAULT — general talking / engaging
    return ("talking", "happy", "shocked", "shocked")


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
    lw = max(4, int(6 * s))
    hr = int(34 * s)   # bigger rounder head — Trust Me Bro style
    ht = cy - int(121 * s)
    hb = cy - int(53  * s)
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
    """Wise Joe-style cloud thought bubble — soft lavender with growing dot trail."""
    CLOUD_FILL   = (235, 232, 255)   # soft lavender
    CLOUD_STROKE = (140, 120, 210)   # indigo outline
    TEXT_COLOR   = (55,  40, 130)    # deep indigo text

    # Growing dot trail leading to the cloud
    for i, r in enumerate([4, 6, 9, 13]):
        bx = cx + int((22 + i * 18))
        by = cy - int((42 + i * 19))
        draw.ellipse([bx-r, by-r, bx+r, by+r], fill=CLOUD_FILL, outline=CLOUD_STROKE, width=2)

    font = _font(fs)
    max_chars = max(8, int(w * 0.35 / (fs * 0.62)))
    lines = textwrap.wrap(text, width=max_chars)
    if not lines:
        return
    lh = fs + 8
    tw = max(draw.textbbox((0,0), l, font=font)[2] for l in lines)
    th = len(lines) * lh
    pad = int(fs * 0.6)
    bw = tw + pad * 2
    bh = th + pad * 2
    bx = cx + int(68)
    by = cy - int(165)
    bx = max(8, min(bx, w - bw - 8))

    # Main cloud body (rounded rectangle base)
    draw.rounded_rectangle([bx, by, bx+bw, by+bh],
                            radius=int(fs * 0.7), fill=CLOUD_FILL, outline=CLOUD_STROKE, width=3)
    # Cloud bumps along the top edge
    for bump_frac, bump_r in [(0.2, int(fs*0.55)), (0.5, int(fs*0.7)), (0.8, int(fs*0.5))]:
        bumpx = bx + int(bw * bump_frac)
        bumpy = by + int(fs * 0.35)
        draw.ellipse([bumpx-bump_r, bumpy-bump_r, bumpx+bump_r, bumpy+bump_r],
                     fill=CLOUD_FILL, outline=CLOUD_STROKE, width=2)

    # Text
    for i, line in enumerate(lines):
        lbb = draw.textbbox((0,0), line, font=font)
        lw2 = lbb[2] - lbb[0]
        draw.text((bx + pad + (tw - lw2)//2, by + pad + i*lh), line, fill=TEXT_COLOR, font=font)


# ── Floating label (coloured badge) ──────────────────────────────────────────

def _label(draw, cx, cy, text, fs, color=BLUE):
    font = _font(fs)
    bb = draw.textbbox((0,0), text, font=font)
    tw, th = bb[2]-bb[0], bb[3]-bb[1]
    pad = int(fs * 0.4)
    draw.rounded_rectangle([cx-tw//2-pad, cy-th//2-pad, cx+tw//2+pad, cy+th//2+pad],
                            radius=int(fs * 0.35), fill=color, outline=LINE, width=2)
    draw.text((cx - tw//2, cy - th//2), text, fill=WHITE, font=font)


# ── Wise Joe-style reflection aura ───────────────────────────────────────────
# Drawn around a figure in "thinking" pose. Rings go BEFORE the figure;
# floating ?-marks and dots go AFTER so they appear in front of the figure.

def _reflection_aura_rings(draw, cx, cy, s, phase):
    """Soft pulsing halo rings behind the figure's head — contemplation glow."""
    hx = cx
    hy = cy - int(s * 88)   # approximate head centre
    pulse = 1.0 + 0.07 * math.sin(phase * math.pi)
    for ring_r, ring_col in [
        (int(54*s*pulse), (215, 210, 255)),
        (int(70*s*pulse), (232, 228, 255)),
        (int(86*s*pulse), (242, 240, 255)),
    ]:
        draw.ellipse([hx-ring_r, hy-ring_r, hx+ring_r, hy+ring_r],
                     fill=None, outline=ring_col, width=max(2, int(2.5*s)))


def _reflection_aura_front(draw, cx, cy, s, phase, canvas_w):
    """Floating question marks + constellation dots in front of the thinking figure."""
    hx = cx
    hy = cy - int(s * 88)
    q_font_base = max(18, int(26 * s))

    # 3 orbiting question marks at different distances and sizes
    for i, (angle_offset, dist_mult, size_mult) in enumerate([
        (50,  1.0, 1.0),
        (125, 0.82, 0.72),
        (15,  1.15, 0.58),
    ]):
        angle = math.radians(angle_offset + phase * 12)   # slow orbit
        dist  = int(dist_mult * 68 * s)
        qx = hx + int(dist * math.cos(angle))
        qy = hy + int(dist * math.sin(angle))
        q_fs   = max(14, int(q_font_base * size_mult))
        q_font = _font(q_fs)
        dot_r  = int(q_fs * 0.78)
        # Soft indigo badge
        draw.ellipse([qx-dot_r, qy-dot_r, qx+dot_r, qy+dot_r],
                     fill=(220, 215, 252), outline=(160, 145, 220), width=max(1, int(1.5*s)))
        bb = draw.textbbox((0,0), "?", font=q_font)
        tw, th = bb[2]-bb[0], bb[3]-bb[1]
        draw.text((qx-tw//2, qy-th//2), "?", fill=(90, 65, 175), font=q_font)

    # Constellation dots — small circles around head at various positions
    for di, (dx_off, dy_off) in enumerate([
        (-int(40*s), -int(52*s)),
        ( int(34*s), -int(58*s)),
        (-int(24*s), -int(72*s)),
        ( int(22*s), -int(76*s)),
        (-int(58*s), -int(35*s)),
    ]):
        dot_r = max(3, int((4 + di % 3) * s * 0.45))
        col   = [(185, 175, 245), (205, 195, 255), (165, 155, 230),
                 (195, 185, 250), (175, 165, 240)][di]
        draw.ellipse([hx+dx_off-dot_r, hy+dy_off-dot_r,
                      hx+dx_off+dot_r, hy+dy_off+dot_r],
                     fill=col, outline=(140, 128, 210), width=1)


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


def _draw_stat_callout(draw, narration: str, w: int, h: int, scene_type: int, phase: float):
    """Detect a number/stat in narration and render an animated floating callout.
    Appears in bottom-left corner (landscape) — only when narration contains a concrete stat.
    The callout slides in slightly based on phase so it feels alive, not stamped on."""
    import re
    if h > w:
        return  # skip on Shorts — too cluttered

    n = narration
    stat_val = ""
    stat_label = ""

    # Extract the most compelling number from narration
    pct = re.search(r'(\d+)\s*percent|(\d+)%', n, re.IGNORECASE)
    ratio = re.search(r'(\d+)\s+(?:in|out of)\s+(\d+)', n, re.IGNORECASE)
    times = re.search(r'(\d+)\s+times', n, re.IGNORECASE)
    days  = re.search(r'(\d+)\s+days?', n, re.IGNORECASE)
    secs  = re.search(r'(\d+)\s+seconds?', n, re.IGNORECASE)
    study = re.search(r'stud(?:y|ies)\s+show', n, re.IGNORECASE)

    if pct:
        v = pct.group(1) or pct.group(2)
        stat_val = f"{v}%"
        # Find ~4 words after the match for context
        pos = pct.end()
        context_words = n[pos:pos+40].split()[:4]
        stat_label = " ".join(context_words).strip(".,")
    elif ratio:
        stat_val = f"{ratio.group(1)} in {ratio.group(2)}"
        stat_label = "people experience this"
    elif times:
        stat_val = f"×{times.group(1)}"
        stat_label = "more likely"
    elif days:
        stat_val = f"{days.group(1)}d"
        stat_label = "to form a habit"
    elif secs:
        stat_val = f"{secs.group(1)}s"
        stat_label = "is all it takes"
    elif study:
        stat_val = "STUDY"
        stat_label = "confirms this"
    else:
        return  # no stat found

    # Callout box — bottom-left, small and clean
    accent_colors = [RED, PURPLE, GREEN, ORANGE]
    accent = accent_colors[scene_type % 4]

    box_w = int(w * 0.18)
    box_h = int(h * 0.11)
    # Slight slide-in animation using phase
    slide_x = int((1.0 - min(1.0, phase * 3)) * box_w * 0.3)
    bx1 = int(w * 0.03) - slide_x
    by1 = int(h * 0.73)
    bx2 = bx1 + box_w
    by2 = by1 + box_h

    # Shadow
    draw.rounded_rectangle([bx1+3, by1+3, bx2+3, by2+3], radius=8, fill=(0, 0, 0, 80))
    # Background
    draw.rounded_rectangle([bx1, by1, bx2, by2], radius=8, fill=(18, 20, 45))
    # Left accent strip
    draw.rounded_rectangle([bx1, by1, bx1+5, by2], radius=3, fill=accent)

    # Stat value — large, bold
    fs_val = max(20, int(box_h * 0.46))
    fs_lbl = max(11, int(box_h * 0.22))
    font_val = _font(fs_val)
    font_lbl = _font_r(fs_lbl)

    inner_x = bx1 + 12
    inner_y = by1 + int(box_h * 0.10)
    draw.text((inner_x, inner_y), stat_val, fill=YELLOW, font=font_val)

    if stat_label:
        lbl = stat_label[:22]
        draw.text((inner_x, inner_y + int(box_h * 0.52)), lbl,
                  fill=(180, 190, 215), font=font_lbl)


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
    # Shorts layout zones (safe from YouTube UI overlays):
    #   0-14%  = YouTube header — avoid
    #   14-22% = kinetic text lives here
    #   27-35% = prop zone — pushed down to not clash with text
    #   35-42% = label badge
    #   42-88% = figures
    #   88-100%= yellow banner + watermark
    prop_y  = int(h * 0.32) if is_short else int(h * 0.13)
    label_y = int(h * 0.42) if is_short else int(h * 0.22)
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
    _draw_ground_shadow(draw, ax, ay, s)
    _draw_ground_shadow(draw, bx, by_, s)
    _figure(draw, ax, ay,  s, pose="pointing_r", emotion="excited", phase=phase)
    _figure(draw, bx, by_, s, pose="shocked",    emotion="shocked", flip=True, phase=phase)
    _bubble(draw, ax, ay - int(100*s), bubble_a,
            hw, bubble_fs, tail="left", anchor="right")
    _bubble(draw, bx, by_ - int(100*s), bubble_b,
            hw, bubble_fs, tail="right", fill=(255,240,240), anchor="left")
    _label(draw, w//2, label_y, label_text, int(bubble_fs*0.9), RED)


def _scene_problem(draw, w, h, s, bubble_fs, bubble_a, bubble_b, phase=0, label_text="THE BLOCK"):
    ax, ay, bx, by_, prop_y, label_y = _scene_positions(w, h, s)
    hw = _half_w(w)

    ps = s * (1.0 + 0.06 * phase)
    _brain(draw, w//2, prop_y, ps * 0.9)
    _reflection_aura_rings(draw, bx, by_, s, phase)
    _draw_ground_shadow(draw, ax, ay, s)
    _draw_ground_shadow(draw, bx, by_, s)
    _figure(draw, ax, ay,  s, pose="talking",  emotion="thinking", phase=phase)
    _figure(draw, bx, by_, s, pose="thinking", emotion="sad", flip=True, phase=phase)
    _bubble(draw, ax, ay - int(100*s), bubble_a,
            hw, bubble_fs, tail="left", anchor="right")
    _thought_bubble(draw, bx, by_ - int(100*s), bubble_b, w, bubble_fs)
    # Floating ?-marks and dots drawn AFTER figures so they appear in front
    _reflection_aura_front(draw, bx, by_, s, phase, w)
    _label(draw, w//2, label_y, label_text, int(bubble_fs*0.9), PURPLE)


def _scene_solution(draw, w, h, s, bubble_fs, bubble_a, bubble_b, phase=0, label_text="THE FIX"):
    ax, ay, bx, by_, prop_y, label_y = _scene_positions(w, h, s)
    hw = _half_w(w)

    ps = s * (1.0 + 0.06 * phase)
    _lightbulb(draw, w//2, prop_y, ps * 1.0)
    _draw_ground_shadow(draw, ax, ay, s)
    _draw_ground_shadow(draw, bx, by_, s)
    _figure(draw, ax, ay,  s, pose="excited",    emotion="excited", phase=phase)
    _figure(draw, bx, by_, s, pose="pointing_l", emotion="happy",   flip=True, phase=phase)
    _bubble(draw, ax, ay - int(100*s), bubble_a,
            hw, bubble_fs, tail="left", anchor="right")
    _bubble(draw, bx, by_ - int(100*s), bubble_b,
            hw, bubble_fs, tail="right", fill=(240,255,240), anchor="left")
    _label(draw, w//2, label_y, label_text, int(bubble_fs*0.9), GREEN)


def _scene_result(draw, w, h, s, bubble_fs, bubble_a, bubble_b, phase=0, label_text="LEVEL UP"):
    ax, ay, bx, by_, prop_y, label_y = _scene_positions(w, h, s)
    hw = _half_w(w)

    ps = s * (1.0 + 0.06 * phase)
    _trophy(draw, w//2, prop_y, ps * 0.95)
    _draw_ground_shadow(draw, ax, ay, s)
    _draw_ground_shadow(draw, bx, by_, s)
    _figure(draw, ax, ay,  s, pose="excited", emotion="excited", phase=phase)
    _figure(draw, bx, by_, s, pose="excited", emotion="excited", flip=True, phase=phase)
    _bubble(draw, ax, ay - int(100*s), bubble_a,
            hw, bubble_fs, tail="left", anchor="right")
    _bubble(draw, bx, by_ - int(100*s), bubble_b,
            hw, bubble_fs, tail="right", fill=(255,255,220), anchor="left")
    _label(draw, w//2, label_y, label_text, int(bubble_fs*0.9), GREEN)


SCENE_FNS = [_scene_hook, _scene_problem, _scene_solution, _scene_result]


# ── Narration subtitle strip ───────────────────────────────────────────────────

def _narration_strip(draw, narration, w, h, word_start, words_per_frame, fs_base):
    """Disabled — subtitles are now burned in via SRT at assembly time (regular) or
    handled by YouTube auto-captions (shorts). Proportional shot-word slicing caused
    captions to show different words than what the TTS voice was actually saying."""
    return
    words = narration.split() if narration else []
    if not words:
        return
    chunk = words[word_start : word_start + max(1, words_per_frame)]
    if not chunk:
        chunk = words[-min(8, len(words)):]

    # Wrap long chunks to 2 lines max
    import textwrap as _tw
    max_chars = max(12, int(w * 0.80 / (fs_base * 0.55)))
    wrapped = _tw.wrap(" ".join(chunk), width=max_chars)[:2]
    if not wrapped:
        return

    fs = max(24, int(fs_base * 0.68))
    font = _font(fs)
    pad_x, pad_y = int(w * 0.05), int(h * 0.008)
    lh = fs + int(fs * 0.35)

    # Total bar height for 1 or 2 lines
    bar_h = len(wrapped) * lh + pad_y * 2
    # Position at 86% height — below figure feet (which end at ~82%) for 1920x1080
    bar_y = int(h * 0.855)

    # Rounded pill background — semi-dark for contrast
    draw.rounded_rectangle([int(w * 0.03), bar_y,
                             int(w * 0.97), bar_y + bar_h],
                            radius=int(fs * 0.4),
                            fill=(15, 16, 32))

    for i, line in enumerate(wrapped):
        bb = draw.textbbox((0, 0), line, font=font)
        lw2 = bb[2] - bb[0]
        tx = max(pad_x, (w - lw2) // 2)
        ty = bar_y + pad_y + i * lh
        draw.text((tx + 2, ty + 2), line, fill=(0, 0, 0), font=font)
        draw.text((tx, ty), line, fill=(255, 255, 255), font=font)


# ── Shot-type frame renderers ─────────────────────────────────────────────────
# Each shot type produces a genuinely different visual composition.
# This is what Trust Me Bro / Productive Peter actually do — they don't zoom
# the same image; they switch to a different scene entirely.

def _draw_banner_and_watermark(draw, text, w, h):
    """Minimal branding — thin dark bottom bar + small top-left watermark.
    No yellow banner: research shows top channels (Productive Peter, Trust Me Bro)
    rely on voice + label badge for scene context, not a persistent bottom bar.
    """
    # Thin dark bottom strip — just enough to frame the canvas cleanly
    bar_h = max(5, int(h * 0.006))
    draw.rectangle([0, h - bar_h, w, h], fill=(22, 24, 55))
    # Small top-left watermark — subtle, non-distracting
    draw.text((int(w * 0.025), int(h * 0.012)), "@MindShiftProductivity",
              fill=(155, 170, 205), font=_font_r(max(16, w // 56)))


def _draw_grid(draw, w, h):
    gc = (228, 236, 248)
    for i in range(0, w, max(1, w//16)): draw.line([i, 0, i, h], fill=gc, width=1)
    for i in range(0, h, max(1, h//22)): draw.line([0, i, w, i], fill=gc, width=1)


def _draw_kinetic_text(draw, text: str, w: int, h: int):
    """Disabled — kinetic text crowds the frame in both orientations.
    Content is carried by voice narration + label badge.
    """
    return
    fs = max(36, w // 22) if is_short else max(40, w // 26)
    font = _font(fs)
    max_chars = max(8, int(w * 0.82 / (fs * 0.58)))
    max_lines = 1 if is_short else 2
    lines = textwrap.wrap(text.upper(), width=max_chars)[:max_lines]
    if not lines:
        return
    lh = int(fs * 1.30)
    # Safe zone top: shorts 21%, regular 5%
    base_y = int(h * 0.14) if is_short else int(h * 0.04)
    for i, line in enumerate(lines):
        bb = draw.textbbox((0, 0), line, font=font)
        lw2 = bb[2] - bb[0]
        tx = max(int(w * 0.04), (w - lw2) // 2)
        ty = base_y + i * lh
        # Subtle shadow — dark navy text on light background
        draw.text((tx + 2, ty + 2), line, fill=(180, 190, 210), font=font)
        draw.text((tx, ty), line, fill=(18, 20, 50), font=font)


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
    # Shorts: no B bubble in wide shot — it overlaps the label badge; close-ups keep bubbles
    bubble_b = "" if h > w else _pick_reaction(narration, scene_type, rng)
    label_text = _LABEL_POOLS[scene_type][(slot + scene_idx) % len(_LABEL_POOLS[scene_type])]

    SCENE_FNS[scene_type](draw, w, h, s, bubble_fs, bubble_a, bubble_b, phase, label_text)
    _draw_banner_and_watermark(draw, text, w, h)
    _narration_strip(draw, narration, w, h, word_start, wpf, max(22, h // 44))
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

    # Poses intentionally DIFFERENT from the wide shot to create visual escalation:
    # hook:     wide=pointing/excited  →  focus=shocked/shocked  (intensity up)
    # problem:  wide=talking/thinking  →  focus=thinking/sad     (empathy deepens)
    # solution: wide=excited/excited   →  focus=pointing_r/excited (directing viewer)
    # result:   wide=excited/excited   →  focus=excited/excited  (peak energy maintained)
    a_pose, a_emotion, _, _ = _detect_content_emotion(narration)
    if a_emotion == "thinking":
        _reflection_aura_rings(draw, cx, cy, s, phase)
    _draw_ground_shadow(draw, cx, cy, s)
    _figure(draw, cx, cy, s, pose=a_pose, emotion=a_emotion, phase=phase)
    _apply_costume(draw, cx, cy, s, narration)
    if a_emotion == "thinking":
        _reflection_aura_front(draw, cx, cy, s, phase, w)
    _bubble(draw, cx, cy - int(100*s), bubble_text, int(w*0.55), bubble_fs,
            tail="left", anchor="right")
    label_colors = [RED, PURPLE, GREEN, GREEN]
    _label(draw, int(w*0.72), int(h*0.22), label_text, int(bubble_fs*0.85), label_colors[scene_type])
    _draw_stat_callout(draw, narration, w, h, scene_type, phase)
    _draw_banner_and_watermark(draw, text, w, h)
    _narration_strip(draw, narration, w, h, word_start, wpf, max(22, h // 44))
    return img


def _pick_prop(narration: str, scene_type: int):
    """Choose a prop function based on keywords in the narration, falling back to scene-type default."""
    n = narration.lower()
    if any(k in n for k in ("brain", "cortisol", "dopamine", "neuron", "neural", "think", "mind", "mental")):
        return _brain
    if any(k in n for k in ("time", "minute", "hour", "day", "week", "clock", "late", "morning", "night")):
        return _clock
    if any(k in n for k in ("money", "rich", "wealth", "income", "earn", "pay", "afford", "broke", "dollar")):
        return _money
    if any(k in n for k in ("win", "success", "goal", "achieve", "trophy", "reward", "level", "accomplish")):
        return _trophy
    if any(k in n for k in ("idea", "solution", "discover", "realize", "insight", "answer", "key", "unlock")):
        return _lightbulb
    # Default per scene_type: hook→clock, problem→brain, solution→lightbulb, result→trophy
    return [_clock, _brain, _lightbulb, _trophy][scene_type % 4]


def _create_frame_focus_prop(text, narration, w, h, scene_idx, phase, slot, word_start, wpf, bg=None):
    """Concept card — bold text_overlay headline + prop + narration strip.
    Matches Psych2Go / Improvement Pill 'section header' technique:
    the text_overlay from the script appears large when this shot plays."""
    img = bg.copy() if bg else Image.new("RGB", (w, h), BG)
    draw = ImageDraw.Draw(img)
    if not bg:
        _draw_grid(draw, w, h)

    scene_type = scene_idx % 4
    label_colors = [RED, PURPLE, GREEN, ORANGE]
    accent = label_colors[scene_type]

    # ── Large headline text (script's text_overlay) ──────────────────────────
    # Landscape only — shorts rely on the narration strip instead
    if h <= w and text:
        hl_fs = max(38, w // 24)
        hl_font = _font(hl_fs)
        headline = text.upper()[:38]
        bb = draw.textbbox((0, 0), headline, font=hl_font)
        hl_w = bb[2] - bb[0]
        hx = max(int(w * 0.04), (w - hl_w) // 2)
        hy = int(h * 0.06)
        # Thick shadow → pop against gradient background
        draw.text((hx + 3, hy + 3), headline, fill=(0, 0, 0), font=hl_font)
        draw.text((hx, hy), headline, fill=accent, font=hl_font)

    # ── Prop (keyword-matched) ────────────────────────────────────────────────
    prop_s = 2.2 if h > w else 1.6
    prop_y = int(h * 0.42) if h > w else int(h * 0.36)
    prop_fn = _pick_prop(narration, scene_type)
    prop_fn(draw, w // 2, prop_y, prop_s * (1.0 + 0.04 * phase))

    # ── Small label badge below prop ─────────────────────────────────────────
    label_text = _LABEL_POOLS[scene_type][(slot + scene_idx) % len(_LABEL_POOLS[scene_type])]
    lfs = max(26, w // 30) if h > w else max(22, w // 34)
    _label(draw, w // 2, int(h * 0.62) if h > w else int(h * 0.56), label_text, lfs, accent)

    _draw_banner_and_watermark(draw, text, w, h)
    _narration_strip(draw, narration, w, h, word_start, wpf, max(22, h // 44))
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
    bubble_b = _pick_reaction(narration, scene_type, rng)
    label_text = _LABEL_POOLS[scene_type][(slot + scene_idx) % len(_LABEL_POOLS[scene_type])]

    _, _, b_pose, b_emotion = _detect_content_emotion(narration)
    # Wise Joe-style contemplation aura for thinking moments
    if b_emotion == "thinking":
        _reflection_aura_rings(draw, cx, cy, s, phase)
    _draw_ground_shadow(draw, cx, cy, s)
    _figure(draw, cx, cy, s, pose=b_pose, emotion=b_emotion,
            flip=True, phase=phase)
    _apply_costume(draw, cx, cy, s, narration)
    if b_emotion == "thinking":
        _reflection_aura_front(draw, cx, cy, s, phase, w)
    bubble_fill = [(255,240,240), (240,240,255), (240,255,240), (255,255,220)]
    if b_emotion == "thinking":
        # Use the cloud thought bubble instead of a speech bubble
        _thought_bubble(draw, cx, cy - int(100*s), bubble_b, w, bubble_fs)
    else:
        _bubble(draw, cx, cy - int(100*s), bubble_b, int(w*0.55), bubble_fs,
                tail="right", fill=bubble_fill[scene_type], anchor="left")
    label_colors = [RED, PURPLE, GREEN, ORANGE]
    _label(draw, int(w*0.28), int(h*0.22), label_text, int(bubble_fs*0.85), label_colors[scene_type])
    _draw_stat_callout(draw, narration, w, h, scene_type, phase)
    _draw_banner_and_watermark(draw, text, w, h)
    _narration_strip(draw, narration, w, h, word_start, wpf, max(22, h // 44))
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
    narration_words = narration.split() if narration else []
    total_words = len(narration_words)

    # Check if this scene opens a chapter (regular videos only)
    chapter_info = _CHAPTER_MAP.get(scene_idx) if video_type == "regular" else None

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
    else:  # Regular — first shot of chapter scenes = 2s title card + 3s wide
        if chapter_info:
            shots = [
                ("chapter_card", 2),
                ("wide",         3),
                ("focus_a",      5),
                ("focus_prop",   5),
                ("focus_b",      5),
                ("wide",         max(3, d - 20)),
            ]
        else:
            shots = [
                ("wide",       5),
                ("focus_a",    5),
                ("focus_prop", 5),
                ("focus_b",    5),
                ("wide",       max(3, d - 20)),
            ]

    # Illustrated environment background — world matches narration content (Trust Me Bro style)
    scene_type = scene_idx % 4
    scene_bg = _make_environment_bg(narration, w, h, scene_type)

    sub_clips = []
    # 8-frame smooth cycle: arm rises and falls fluidly (0 → peak → 0)
    phases = [0, 0.25, 0.5, 0.75, 1, 0.75, 0.5, 0.25]
    n_frames = len(phases)

    # Shot start times for kinetic text word-time sync
    shot_starts = []
    t = 0
    for _, sd in shots:
        shot_starts.append(t)
        t += sd

    for shot_idx, (shot_type, shot_dur) in enumerate(shots):
        # Slice narration words for this shot's time window → kinetic text
        if total_words > 0 and d > 0:
            wf = round(total_words * shot_starts[shot_idx] / d)
            wt = min(total_words, round(total_words * (shot_starts[shot_idx] + shot_dur) / d))
            kinetic_text = " ".join(narration_words[wf:wt])
        else:
            kinetic_text = label

        shot_frames_dir = output_path.replace(".mp4", f"_s{shot_idx}_frames")
        os.makedirs(shot_frames_dir, exist_ok=True)

        wpf = max(1, wt - wf)  # show all words for this shot's time slice

        if shot_type == "chapter_card" and chapter_info:
            ch_num, ch_name, ch_rehook = chapter_info
            for fi, phase in enumerate(phases):
                frame = _create_chapter_card_frame(ch_num, ch_name, w, h, scene_bg, rehook=ch_rehook)
                frame.save(os.path.join(shot_frames_dir, f"f{fi:03d}.png"))
        else:
            renderer = _SHOT_RENDERERS[shot_type]
            for fi, phase in enumerate(phases):
                frame = renderer(label, narration, w, h, scene_idx, phase, slot, wf, wpf, bg=scene_bg)
                frame.save(os.path.join(shot_frames_dir, f"f{fi:03d}.png"))

        sub_path = output_path.replace(".mp4", f"_shot{shot_idx}.mp4")
        result = subprocess.run([
            ff, "-y", "-framerate", "8",
            "-i", os.path.join(shot_frames_dir, "f%03d.png"),
            "-vf", f"loop=-1:size={n_frames}:start=0",  # no fade — no blank screens
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
            _draw_kinetic_text(ImageDraw.Draw(frame), label, w, h)
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


# ── Chapter map — scene index → (number, title, tension rehook line) ─────────
# The rehook line is shown below the chapter title and creates curiosity for what's next.
# It must feel like unfinished business — never a summary.
_CHAPTER_MAP = {
    0:  ("01", "THE HOOK",       "You already know this feeling."),
    2:  ("02", "THE SCIENCE",    "Here's what's actually happening inside your brain."),
    7:  ("03", "REAL STORIES",   "This is where you recognize yourself."),
    12: ("04", "THE FIX",        "This is the part most people never reach."),
    17: ("05", "YOUR NEW LIFE",  "What happens when you actually apply this."),
}


def _create_chapter_card_frame(chapter_num: str, chapter_name: str,
                                w: int, h: int, bg: "Image.Image",
                                rehook: str = "") -> "Image.Image":
    """Full-screen chapter title card — shown for first 2 seconds of a chapter's opening scene.
    Includes a rehook tension line below the title to pull the viewer into the next section."""
    img = bg.copy()
    draw = ImageDraw.Draw(img)

    # Dark translucent overlay so background shows through subtly
    overlay = Image.new("RGBA", (w, h), (10, 12, 38, 210))
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(img)

    fs_num  = max(24, w // 20)
    fs_name = max(36, w // 12)
    fs_hook = max(18, w // 38)   # rehook line — smaller, italic-style

    lx1, lx2 = int(w * 0.15), int(w * 0.85)

    # Top rule
    draw.line([lx1, int(h * 0.36), lx2, int(h * 0.36)],
              fill=(255, 214, 0), width=max(2, w // 320))

    # "CHAPTER XX" label
    num_font = _font(fs_num)
    label = f"CHAPTER  {chapter_num}"
    bb = draw.textbbox((0, 0), label, font=num_font)
    draw.text(((w - (bb[2]-bb[0])) // 2, int(h * 0.40)),
              label, fill=(200, 210, 230), font=num_font)

    # Chapter name — bold, large, white
    name_font = _font(fs_name)
    bb2 = draw.textbbox((0, 0), chapter_name, font=name_font)
    nx = (w - (bb2[2]-bb2[0])) // 2
    ny = int(h * 0.49)
    draw.text((nx + 3, ny + 3), chapter_name, fill=(0, 0, 30), font=name_font)
    draw.text((nx, ny), chapter_name, fill=(255, 255, 255), font=name_font)

    # Bottom rule
    draw.line([lx1, int(h * 0.66), lx2, int(h * 0.66)],
              fill=(255, 214, 0), width=max(2, w // 320))

    # Rehook tension line — creates curiosity for what's coming
    if rehook:
        hook_font = _font_r(fs_hook)
        bb3 = draw.textbbox((0, 0), rehook, font=hook_font)
        hx = (w - (bb3[2]-bb3[0])) // 2
        draw.text((hx, int(h * 0.70)), rehook, fill=(180, 195, 220), font=hook_font)

    return img


def _create_poll_card_frame(question: str, w: int, h: int, frame_idx: int = 0) -> "Image.Image":
    """Interactive A/B poll card shown at end of Shorts — drives comments.
    Parses: 'Question text? A: Option1 B: Option2'
    Alternates highlight on A/B each cycle to look interactive.
    """
    # Parse question + options
    parts = question.split(" A: ")
    q_text = parts[0].strip().rstrip("?") + "?"
    ab_raw = parts[1] if len(parts) > 1 else "Yes B: No"
    ab_parts = ab_raw.split(" B: ")
    opt_a = ab_parts[0].strip()
    opt_b = ab_parts[1].strip() if len(ab_parts) > 1 else "Sometimes"

    # Dark navy background
    img = Image.new("RGB", (w, h), (13, 15, 40))
    draw = ImageDraw.Draw(img)

    # Subtle radial glow behind text area
    for r_frac, alpha in [(0.95, 25), (0.65, 50), (0.38, 90)]:
        r = int(min(w, h) * r_frac * 0.52)
        cx_, cy_ = w // 2, int(h * 0.45)
        overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        od = ImageDraw.Draw(overlay)
        od.ellipse([cx_ - r, cy_ - r, cx_ + r, cy_ + r], fill=(60, 80, 200, alpha))
        img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
        draw = ImageDraw.Draw(img)

    # Font helpers
    def _font(size):
        for p in [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/Arial.ttf",
        ]:
            try:
                from PIL import ImageFont
                return ImageFont.truetype(p, size)
            except Exception:
                pass
        from PIL import ImageFont
        return ImageFont.load_default()

    fs_q  = max(28, w // 18)   # question font
    fs_o  = max(24, w // 22)   # option font
    fs_cta= max(18, w // 30)   # CTA font

    # "QUICK POLL" label at top
    label_font = _font(fs_cta)
    label = "QUICK POLL 📊"
    bbox = draw.textbbox((0, 0), label, font=label_font)
    lw = bbox[2] - bbox[0]
    draw.text(((w - lw) // 2, int(h * 0.10)), label, fill=(160, 180, 220), font=label_font)

    # Question text — wrapped
    q_font = _font(fs_q)
    max_chars = max(15, int(w * 0.80 / (fs_q * 0.55)))
    q_lines = textwrap.wrap(q_text, width=max_chars)
    q_start_y = int(h * 0.22)
    line_gap = int(fs_q * 1.35)
    for li, line in enumerate(q_lines[:3]):
        bbox = draw.textbbox((0, 0), line, font=q_font)
        lw_ = bbox[2] - bbox[0]
        x_ = (w - lw_) // 2
        draw.text((x_ + 2, q_start_y + li * line_gap + 2), line, fill=(20, 20, 60), font=q_font)
        draw.text((x_, q_start_y + li * line_gap), line, fill=(255, 255, 255), font=q_font)

    # Option buttons — alternate highlight each 2 frames for "tap" effect
    btn_h  = int(h * 0.10)
    btn_x  = int(w * 0.06)
    btn_w_ = int(w * 0.88)
    radius = btn_h // 2

    highlight_a = (frame_idx // 2) % 2 == 0
    col_a = (255, 214, 0)   if highlight_a else (40, 45, 90)
    col_b = (40, 45, 90)    if highlight_a else (255, 214, 0)
    txt_a = (20, 20, 50)    if highlight_a else (200, 210, 240)
    txt_b = (200, 210, 240) if highlight_a else (20, 20, 50)

    btn_y_a = int(h * 0.50)
    btn_y_b = int(h * 0.65)

    for (by, bc, tc, letter, opt_txt) in [
        (btn_y_a, col_a, txt_a, "A", opt_a),
        (btn_y_b, col_b, txt_b, "B", opt_b),
    ]:
        draw.rounded_rectangle([btn_x, by, btn_x + btn_w_, by + btn_h], radius=radius, fill=bc)
        o_font = _font(fs_o)
        full_label = f"  {letter}   {opt_txt}"
        bbox = draw.textbbox((0, 0), full_label, font=o_font)
        ty = by + (btn_h - (bbox[3] - bbox[1])) // 2
        draw.text((btn_x + int(w * 0.06), ty), full_label, fill=tc, font=o_font)

    # CTA at bottom
    cta_font = _font(fs_cta)
    cta = "Comment  A  or  B  below! 👇"
    bbox = draw.textbbox((0, 0), cta, font=cta_font)
    cta_x = (w - (bbox[2] - bbox[0])) // 2
    draw.text((cta_x, int(h * 0.82)), cta, fill=(255, 180, 0), font=cta_font)

    return img


def _create_poll_card_video(question: str, output_dir: str, w: int, h: int, duration: int = 4) -> str:
    """Render a 4-second animated poll card as a video clip for end of Shorts."""
    ff_path = shutil.which("ffmpeg") or "ffmpeg"
    try:
        import imageio_ffmpeg
        ff_path = imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        pass

    frames_dir = os.path.join(output_dir, "poll_frames")
    os.makedirs(frames_dir, exist_ok=True)

    n_frames = 8
    for fi in range(n_frames):
        frame = _create_poll_card_frame(question, w, h, frame_idx=fi)
        frame.save(os.path.join(frames_dir, f"f{fi:03d}.png"))

    out_path = os.path.join(output_dir, "scene_poll.mp4")
    subprocess.run([
        ff_path, "-y", "-framerate", "8",
        "-i", os.path.join(frames_dir, "f%03d.png"),
        "-vf", f"loop=-1:size={n_frames}:start=0",
        "-t", str(duration),
        "-c:v", "libx264", "-preset", "ultrafast",
        "-pix_fmt", "yuv420p", "-r", "24", "-crf", "18", out_path
    ], capture_output=True, text=True, timeout=60)

    for fi in range(n_frames):
        fp = os.path.join(frames_dir, f"f{fi:03d}.png")
        if os.path.exists(fp):
            os.remove(fp)
    try:
        os.rmdir(frames_dir)
    except Exception:
        pass

    print(f"  [Animate] Poll card: {question[:50]}")
    return out_path


def create_all_scenes(scenes, output_dir, video_type="regular", slot=0, poll_question: str = ""):
    from config import SHORTS_VIDEO
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

    # Append interactive poll card at end of Shorts to drive comments
    if video_type == "shorts" and poll_question and " A: " in poll_question:
        spec = SHORTS_VIDEO
        poll_path = _create_poll_card_video(
            poll_question, output_dir, spec["width"], spec["height"], duration=4
        )
        if os.path.exists(poll_path) and os.path.getsize(poll_path) > 500:
            paths.append(poll_path)

    return paths
