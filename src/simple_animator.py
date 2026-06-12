"""
Productive Peter style — scene-based visual storytelling.
Stick figure IN a scene with contextual objects, speech bubbles,
floating labels. NO bullet points. Pure visual narrative.
"""
import os, math, subprocess, shutil, random
from PIL import Image, ImageDraw, ImageFont

BG      = (245, 248, 252)   # Near-white (PP uses very light background)
LINE    = (20,  20,  20)    # Hand-drawn black
YELLOW  = (255, 214,   0)
RED     = (220,  50,  50)
BLUE    = ( 41, 128, 185)
GREEN   = ( 39, 174,  96)
ORANGE  = (230, 126,  34)
PURPLE  = (142,  68, 173)


def _ffmpeg():
    if shutil.which("ffmpeg"): return "ffmpeg"
    try:
        import imageio_ffmpeg; return imageio_ffmpeg.get_ffmpeg_exe()
    except: return "ffmpeg"


def _font(size):
    for p in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
              "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
              "C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/Arial.ttf"]:
        try: return ImageFont.truetype(p, size)
        except: pass
    return ImageFont.load_default()

def _font_r(size):
    for p in ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
              "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
              "C:/Windows/Fonts/arial.ttf"]:
        try: return ImageFont.truetype(p, size)
        except: pass
    return ImageFont.load_default()


# ── Core stick figure ─────────────────────────────────────────────────────────

def _figure(draw, cx, cy, s, pose="idle", emotion="happy"):
    lw = max(3, int(5*s))
    hr = int(26*s)
    ht = cy - int(110*s); hb = cy - int(58*s)

    draw.ellipse([cx-hr,ht,cx+hr,hb], outline=LINE, width=lw, fill=(255,245,235))

    ey = cy - int(93*s)
    for ex in [cx-int(10*s), cx+int(10*s)]:
        draw.ellipse([ex-int(4*s),ey-int(4*s),ex+int(4*s),ey+int(4*s)], fill=LINE)

    my = cy-int(75*s)
    if emotion=="happy":
        draw.arc([cx-int(12*s),my-int(7*s),cx+int(12*s),my+int(6*s)], 0,180, fill=LINE, width=lw-1)
    elif emotion=="shocked":
        draw.ellipse([cx-int(6*s),my-int(8*s),cx+int(6*s),my+int(4*s)], outline=LINE, width=lw-1)
        # Raised eyebrows
        draw.arc([cx-int(24*s),ht+int(4*s),cx-int(4*s),ht+int(18*s)], 200,340, fill=LINE, width=lw-1)
        draw.arc([cx+int(4*s), ht+int(4*s),cx+int(24*s),ht+int(18*s)], 200,340, fill=LINE, width=lw-1)
    elif emotion=="thinking":
        draw.line([cx-int(10*s),my,cx+int(10*s),my], fill=LINE, width=lw-1)
    elif emotion=="excited":
        draw.arc([cx-int(14*s),my-int(11*s),cx+int(14*s),my+int(7*s)], 0,180, fill=LINE, width=lw)
    elif emotion=="sad":
        draw.arc([cx-int(12*s),my-int(4*s),cx+int(12*s),my+int(9*s)], 180,360, fill=LINE, width=lw-1)

    bb = cy+int(28*s)
    draw.line([cx,hb,cx,bb], fill=LINE, width=lw)
    sy = cy-int(36*s)

    if pose=="idle":
        draw.line([cx,sy,cx-int(48*s),cy], fill=LINE, width=lw)
        draw.line([cx,sy,cx+int(48*s),cy], fill=LINE, width=lw)
    elif pose=="pointing_right":
        draw.line([cx,sy,cx-int(48*s),cy+int(8*s)], fill=LINE, width=lw)
        draw.line([cx,sy,cx+int(72*s),cy-int(28*s)], fill=LINE, width=lw+1)
    elif pose=="pointing_up":
        draw.line([cx,sy,cx-int(48*s),cy], fill=LINE, width=lw)
        draw.line([cx,sy,cx+int(20*s),cy-int(80*s)], fill=LINE, width=lw+1)
    elif pose=="excited":
        draw.line([cx,sy,cx-int(58*s),cy-int(58*s)], fill=LINE, width=lw)
        draw.line([cx,sy,cx+int(58*s),cy-int(58*s)], fill=LINE, width=lw)
    elif pose=="sitting":
        draw.line([cx,sy,cx-int(48*s),cy+int(8*s)], fill=LINE, width=lw)
        draw.line([cx,sy,cx+int(48*s),cy+int(8*s)], fill=LINE, width=lw)
        draw.line([cx,bb,cx-int(50*s),bb], fill=LINE, width=lw)
        draw.line([cx-int(50*s),bb,cx-int(50*s),bb+int(50*s)], fill=LINE, width=lw)
        draw.line([cx,bb,cx+int(50*s),bb], fill=LINE, width=lw)
        draw.line([cx+int(50*s),bb,cx+int(50*s),bb+int(50*s)], fill=LINE, width=lw)
        return
    elif pose=="running":
        draw.line([cx,sy,cx-int(30*s),cy-int(20*s)], fill=LINE, width=lw)
        draw.line([cx,sy,cx+int(60*s),cy-int(40*s)], fill=LINE, width=lw)

    draw.line([cx,bb,cx-int(30*s),cy+int(88*s)], fill=LINE, width=lw)
    draw.line([cx,bb,cx+int(30*s),cy+int(88*s)], fill=LINE, width=lw)
    draw.line([cx-int(30*s),cy+int(88*s),cx-int(50*s),cy+int(88*s)], fill=LINE, width=lw)
    draw.line([cx+int(30*s),cy+int(88*s),cx+int(52*s),cy+int(88*s)], fill=LINE, width=lw)


def _speech_bubble(draw, cx, cy, text, w_max, fs, fill=(255,255,255), tail_dir="left"):
    font = _font(fs)
    lines = []
    words = text.split()
    cur = ""
    for word in words:
        test = (cur+" "+word).strip()
        bb = draw.textbbox((0,0), test, font=font)
        if bb[2]-bb[0] > w_max and cur:
            lines.append(cur); cur = word
        else:
            cur = test
    if cur: lines.append(cur)

    lh = fs+8
    tw = max(draw.textbbox((0,0),l,font=font)[2] for l in lines)
    th = len(lines)*lh
    pad = int(fs*0.5)
    bw = tw+pad*2; bh = th+pad*2
    bx = cx-bw//2; by = cy-bh-int(fs*0.8)

    draw.rounded_rectangle([bx,by,bx+bw,by+bh], radius=int(fs*0.4),
                            fill=fill, outline=LINE, width=2)
    # Tail
    if tail_dir=="left":
        draw.polygon([(bx+int(bw*0.2),by+bh),(bx+int(bw*0.35),by+bh),(cx-int(fs*0.5),cy-int(fs*0.3))],
                     fill=fill)
        draw.line([(bx+int(bw*0.2),by+bh),(cx-int(fs*0.5),cy-int(fs*0.3))], fill=LINE, width=2)
        draw.line([(cx-int(fs*0.5),cy-int(fs*0.3)),(bx+int(bw*0.35),by+bh)], fill=LINE, width=2)

    for i,line in enumerate(lines):
        draw.text((bx+pad, by+pad+i*lh), line, fill=LINE, font=font)


def _floating_label(draw, cx, cy, text, fs, color=BLUE):
    font = _font(fs)
    bb = draw.textbbox((0,0),text,font=font)
    tw,th = bb[2]-bb[0], bb[3]-bb[1]
    pad = int(fs*0.35)
    draw.rounded_rectangle([cx-tw//2-pad, cy-th//2-pad, cx+tw//2+pad, cy+th//2+pad],
                            radius=int(fs*0.3), fill=color, outline=LINE, width=2)
    draw.text((cx-tw//2, cy-th//2), text, fill="white", font=font)


def _question_marks(draw, cx, cy, s):
    font = _font(int(36*s))
    for i,(dx,dy,col) in enumerate([(-int(60*s),-int(80*s),RED),
                                     (int(40*s),-int(110*s),ORANGE),
                                     (int(80*s),-int(60*s),PURPLE)]):
        draw.text((cx+dx,cy+dy), "?", fill=col, font=font)


def _draw_desk(draw, cx, cy, s):
    lw = max(2,int(4*s))
    dw = int(160*s); dh = int(20*s)
    draw.rectangle([cx-dw//2,cy,cx+dw//2,cy+dh], fill=(180,140,100), outline=LINE, width=lw)
    draw.line([cx-dw//3,cy+dh,cx-dw//3,cy+dh+int(50*s)], fill=LINE, width=lw)
    draw.line([cx+dw//3,cy+dh,cx+dw//3,cy+dh+int(50*s)], fill=LINE, width=lw)
    # Laptop
    draw.rectangle([cx-int(35*s),cy-int(40*s),cx+int(35*s),cy], fill=(80,80,90), outline=LINE, width=max(1,lw-1))
    draw.rectangle([cx-int(30*s),cy-int(36*s),cx+int(30*s),cy-int(4*s)], fill=(120,200,255))


def _draw_clock(draw, cx, cy, s, hour=2):
    lw = max(2,int(3*s))
    r = int(30*s)
    draw.ellipse([cx-r,cy-r,cx+r,cy+r], fill="white", outline=LINE, width=lw)
    # Hour hand
    angle = math.radians(hour*30 - 90)
    draw.line([cx,cy,cx+int(r*0.5*math.cos(angle)),cy+int(r*0.5*math.sin(angle))],
              fill=LINE, width=max(2,lw-1))
    # Minute hand
    angle2 = math.radians(-90)
    draw.line([cx,cy,cx+int(r*0.75*math.cos(angle2)),cy+int(r*0.75*math.sin(angle2))],
              fill=RED, width=max(1,lw-1))
    draw.ellipse([cx-int(3*s),cy-int(3*s),cx+int(3*s),cy+int(3*s)], fill=LINE)


def _draw_brain(draw, cx, cy, s):
    r = int(38*s)
    draw.ellipse([cx-r,cy-int(r*0.8),cx+r,cy+int(r*0.8)],
                 fill=(255,180,200), outline=LINE, width=max(2,int(3*s)))
    for i in range(3):
        draw.arc([cx-int(30*s),cy-int(24*s)+i*int(18*s),
                  cx+int(30*s),cy-int(6*s)+i*int(18*s)],
                 180,360, fill=LINE, width=max(1,int(2*s)))
    draw.line([cx,cy-int(r*0.8),cx,cy+int(r*0.8)], fill=LINE, width=max(1,int(2*s)))


def _draw_money_bag(draw, cx, cy, s):
    lw = max(2,int(3*s))
    draw.ellipse([cx-int(32*s),cy-int(22*s),cx+int(32*s),cy+int(32*s)],
                 fill=(46,204,113), outline=LINE, width=lw)
    draw.ellipse([cx-int(14*s),cy-int(36*s),cx+int(14*s),cy-int(18*s)],
                 fill=(46,204,113), outline=LINE, width=lw)
    font = _font(int(28*s))
    draw.text((cx-int(9*s),cy-int(8*s)), "$", fill="white", font=font)


def _draw_trophy(draw, cx, cy, s):
    lw = max(2,int(3*s))
    draw.polygon([(cx-int(28*s),cy-int(38*s)),(cx+int(28*s),cy-int(38*s)),
                  (cx+int(18*s),cy),(cx-int(18*s),cy)], fill=YELLOW, outline=LINE)
    draw.rectangle([cx-int(7*s),cy,cx+int(7*s),cy+int(22*s)], fill=(200,160,0), outline=LINE)
    draw.rectangle([cx-int(20*s),cy+int(20*s),cx+int(20*s),cy+int(32*s)], fill=YELLOW, outline=LINE)
    draw.arc([cx-int(28*s),cy-int(38*s),cx-int(8*s),cy], 90,270, fill=LINE, width=lw)
    draw.arc([cx+int(8*s),cy-int(38*s),cx+int(28*s),cy], 270,90, fill=LINE, width=lw)


def _draw_lightbulb(draw, cx, cy, s, lit=True):
    r = int(24*s); lw = max(2,int(3*s))
    fill = (255,230,50) if lit else (220,220,220)
    draw.ellipse([cx-r,cy-r,cx+r,cy+r], fill=fill, outline=LINE, width=lw)
    draw.rectangle([cx-int(9*s),cy+r-int(2*s),cx+int(9*s),cy+r+int(16*s)],
                   fill=(180,180,180), outline=LINE, width=max(1,lw-1))
    if lit:
        for a in range(0,360,45):
            rad=math.radians(a)
            x1=cx+int((r+5*s)*math.cos(rad)); y1=cy+int((r+5*s)*math.sin(rad))
            x2=cx+int((r+15*s)*math.cos(rad)); y2=cy+int((r+15*s)*math.sin(rad))
            draw.line([x1,y1,x2,y2], fill=ORANGE, width=max(1,lw-1))


def _draw_arrow(draw, x1,y1,x2,y2, color=LINE, lw=3):
    draw.line([x1,y1,x2,y2], fill=color, width=lw)
    angle=math.atan2(y2-y1,x2-x1)
    for side in [0.45,-0.45]:
        ax=x2-int(16*math.cos(angle+side)); ay=y2-int(16*math.sin(angle+side))
        draw.line([x2,y2,ax,ay], fill=color, width=lw)


def _draw_stars(draw, cx, cy, s, n=5):
    for i in range(n):
        angle = math.radians(i * (360/n))
        r = random.randint(int(60*s), int(120*s))
        sx = cx + int(r*math.cos(angle))
        sy = cy + int(r*math.sin(angle))
        draw.text((sx,sy), "★", fill=YELLOW, font=_font(int(22*s)))


# ── Scene builders ────────────────────────────────────────────────────────────

def _scene_hook(draw, w, h, s, text, narration):
    """Opening hook — shocked figure, big clock, question marks, floating fact."""
    cx, cy = int(w*0.30), int(h*0.58)
    _figure(draw, cx, cy, s, "idle", "shocked")
    _question_marks(draw, cx, cy, s)
    _speech_bubble(draw, cx, cy-int(90*s), "Wait... WHAT?!", int(w*0.40), int(22*s))
    # Large clock top-right
    _draw_clock(draw, int(w*0.72), int(h*0.25), s*1.3, hour=2)
    _floating_label(draw, int(w*0.72), int(h*0.40), "2 AM", int(20*s), RED)
    _draw_arrow(draw, int(w*0.60), int(h*0.28), int(w*0.46), int(h*0.46), BLUE, max(2,int(3*s)))
    # Big stat lower-right
    _floating_label(draw, int(w*0.72), int(h*0.68), "95% SUBCONSCIOUS", int(16*s), PURPLE)
    _draw_arrow(draw, int(w*0.72), int(h*0.72), int(w*0.55), int(h*0.78), ORANGE, max(2,int(2*s)))
    _floating_label(draw, int(w*0.60), int(h*0.80), "every decision", int(14*s), ORANGE)


def _scene_problem(draw, w, h, s, text, narration):
    """Problem scene — figure at desk, stressed, multiple worry labels."""
    cx, cy = int(w*0.28), int(h*0.56)
    _figure(draw, cx, cy, s, "sitting", "sad")
    _draw_desk(draw, cx, cy+int(28*s), s*1.2)
    _speech_bubble(draw, cx, cy-int(90*s), "Why can't I change?!", int(w*0.40), int(20*s))
    # Clock top-right
    _draw_clock(draw, int(w*0.72), int(h*0.22), s*1.1, hour=12)
    _floating_label(draw, int(w*0.72), int(h*0.37), "DAY 30", int(18*s), RED)
    _floating_label(draw, int(w*0.72), int(h*0.47), "NO CHANGE", int(16*s), ORANGE)
    _draw_arrow(draw, cx+int(60*s), cy-int(20*s), int(w*0.56), int(h*0.40), LINE, max(2,int(2*s)))
    # Lower frustration labels
    _floating_label(draw, int(w*0.65), int(h*0.68), "SAME HABITS", int(16*s), RED)
    _floating_label(draw, int(w*0.65), int(h*0.78), "STUCK LOOP", int(14*s), PURPLE)
    _draw_arrow(draw, int(w*0.65), int(h*0.63), int(w*0.65), int(h*0.73), RED, max(2,int(2*s)))


def _scene_solution(draw, w, h, s, text, narration):
    """Solution — figure points at lit bulb, brain + rewire labels fill screen."""
    cx, cy = int(w*0.28), int(h*0.56)
    _figure(draw, cx, cy, s, "pointing_right", "excited")
    _speech_bubble(draw, cx, cy-int(95*s), "THIS changes everything!", int(w*0.42), int(20*s))
    # Large lightbulb top-right
    _draw_lightbulb(draw, int(w*0.70), int(h*0.24), s*1.3, lit=True)
    _floating_label(draw, int(w*0.70), int(h*0.40), "THE KEY", int(18*s), GREEN)
    _draw_arrow(draw, int(w*0.70), int(h*0.44), int(w*0.70), int(h*0.52), GREEN, max(2,int(3*s)))
    # Brain lower-right
    _draw_brain(draw, int(w*0.70), int(h*0.65), s*1.1)
    _floating_label(draw, int(w*0.70), int(h*0.79), "NEUROPLASTICITY", int(14*s), PURPLE)
    _draw_arrow(draw, cx+int(65*s), cy-int(10*s), int(w*0.54), int(h*0.38), BLUE, max(2,int(2*s)))


def _scene_result(draw, w, h, s, text, narration):
    """Result/CTA — celebrating figure, trophy top, money bag bottom, stars."""
    cx, cy = int(w*0.30), int(h*0.56)
    _figure(draw, cx, cy, s, "excited", "excited")
    _draw_stars(draw, cx, cy, s*0.9, n=7)
    _speech_bubble(draw, cx, cy-int(100*s), "Subscribe for more!", int(w*0.42), int(20*s))
    # Trophy top-right
    _draw_trophy(draw, int(w*0.70), int(h*0.26), s*1.3)
    _floating_label(draw, int(w*0.70), int(h*0.42), "SUCCESS", int(18*s), GREEN)
    # Money bag lower-right
    _draw_money_bag(draw, int(w*0.70), int(h*0.65), s*1.1)
    _floating_label(draw, int(w*0.70), int(h*0.79), "NEW LIFE", int(16*s), BLUE)
    _draw_arrow(draw, int(w*0.70), int(h*0.46), int(w*0.70), int(h*0.56), ORANGE, max(2,int(3*s)))


SCENE_FNS = [_scene_hook, _scene_problem, _scene_solution, _scene_result]


# ── Full frame ────────────────────────────────────────────────────────────────

def _create_frame(text, narration, w, h, scene_idx):
    img = Image.new("RGB", (w, h), BG)
    draw = ImageDraw.Draw(img)

    # Faint grid (PP style notebook look)
    gc = (230, 238, 248)
    for i in range(0,w,max(1,w//16)): draw.line([i,0,i,h], fill=gc, width=1)
    for i in range(0,h,max(1,h//22)): draw.line([0,i,w,i], fill=gc, width=1)

    s = 2.6 if h > w else 1.3

    # Draw scene content
    SCENE_FNS[scene_idx % 4](draw, w, h, s, text, narration)

    # Yellow banner at bottom
    fs = max(34, w//18)
    font = _font(fs)
    bh = int(fs*2.1)
    by = h - bh - int(h*0.02)
    draw.rectangle([int(w*0.03),by,int(w*0.97),by+bh], fill=YELLOW, outline=LINE, width=3)
    safe = text[:35]
    bb = draw.textbbox((0,0),safe,font=font)
    tx = max(int(w*0.05),(w-(bb[2]-bb[0]))//2)
    ty = by+(bh-(bb[3]-bb[1]))//2
    draw.text((tx+2,ty+2),safe,fill=(120,120,120),font=font)
    draw.text((tx,ty),safe,fill=(15,15,15),font=font)

    # @MindShift top-right
    draw.text((int(w*0.76),int(h*0.012)),"@MindShift",fill=(150,170,200),font=_font_r(max(16,w//52)))

    return img


# ── Video generation ──────────────────────────────────────────────────────────

def create_scene_video(text, bg_color, duration, output_path,
                       video_type="regular", scene_idx=0, bullets=None, narration=""):
    from config import REGULAR_VIDEO, SHORTS_VIDEO
    spec = REGULAR_VIDEO if video_type=="regular" else SHORTS_VIDEO
    w,h = spec["width"], spec["height"]
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)

    frame = _create_frame(text[:40].upper(), narration, w, h, scene_idx)
    tmp = output_path.replace(".mp4","_f.png")
    frame.save(tmp)

    result = subprocess.run([
        _ffmpeg(),"-y","-loop","1","-i",tmp,
        "-t",str(duration),"-c:v","libx264",
        "-pix_fmt","yuv420p","-r","24","-crf","18",output_path
    ], capture_output=True, text=True, timeout=60)

    if os.path.exists(tmp): os.remove(tmp)
    if result.returncode != 0: print(f"  [FFmpeg]: {result.stderr[-300:]}")
    return output_path


def create_all_scenes(scenes, output_dir, video_type="regular"):
    os.makedirs(output_dir, exist_ok=True)
    paths = []
    for i,scene in enumerate(scenes):
        out = os.path.join(output_dir, f"scene_{scene['scene_number']:02d}.mp4")
        print(f"  [Animate] Scene {scene['scene_number']}: {scene['text_overlay']}")
        create_scene_video(
            text=scene["text_overlay"], bg_color="#F5F8FC",
            duration=scene["duration_seconds"], output_path=out,
            video_type=video_type, scene_idx=i,
            narration=scene.get("narration",""),
        )
        paths.append(out)
    return paths
