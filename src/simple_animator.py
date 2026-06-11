"""
Productive Peter style animator:
- Light blue background
- Animated stick figure with poses & emotions
- Scene-relevant props
- Bold text at bottom (yellow banner style)
- Smooth frame animation compiled with FFmpeg
"""
import os
import math
import subprocess
import shutil
import tempfile
from PIL import Image, ImageDraw, ImageFont

# ── Constants ────────────────────────────────────────────────────────────────
BG_COLOR = (214, 234, 248)       # Light blue (Productive Peter signature)
STICK_COLOR = (30, 30, 30)       # Near black
BANNER_COLOR = (255, 214, 0)     # Yellow banner (PP style)
BANNER_TEXT_COLOR = (20, 20, 20) # Dark text on yellow
ACCENT_COLOR = (41, 128, 185)    # Blue accent
FPS = 12  # 12fps is smooth enough and renders fast


def _ffmpeg():
    import shutil as sh
    if sh.which("ffmpeg"):
        return "ffmpeg"
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"


def _get_font(size: int, bold: bool = False):
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/Arial.ttf",
    ]
    for path in font_paths:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()


# ── Stick Figure Drawing ──────────────────────────────────────────────────────

def _draw_stick_figure(draw, cx, cy, scale=1.0, pose="idle", emotion="happy"):
    """Draw a stick figure at (cx, cy) with given pose and emotion."""
    s = scale
    lw = max(2, int(4 * s))

    # Head
    hr = int(35 * s)
    head_top = cy - int(130 * s)
    head_bot = cy - int(60 * s)
    draw.ellipse([cx - hr, head_top, cx + hr, head_bot],
                 outline=STICK_COLOR, width=lw, fill=(255, 245, 235))

    # Face emotion
    ey = cy - int(105 * s)
    ex_off = int(13 * s)
    eye_r = int(4 * s)
    # Eyes
    draw.ellipse([cx - ex_off - eye_r, ey - eye_r, cx - ex_off + eye_r, ey + eye_r],
                 fill=STICK_COLOR)
    draw.ellipse([cx + ex_off - eye_r, ey - eye_r, cx + ex_off + eye_r, ey + eye_r],
                 fill=STICK_COLOR)

    mouth_y = cy - int(78 * s)
    if emotion == "happy":
        draw.arc([cx - int(15*s), mouth_y - int(10*s),
                  cx + int(15*s), mouth_y + int(10*s)],
                 0, 180, fill=STICK_COLOR, width=lw - 1)
    elif emotion == "shocked":
        draw.ellipse([cx - int(8*s), mouth_y - int(8*s),
                      cx + int(8*s), mouth_y + int(8*s)],
                     outline=STICK_COLOR, width=lw - 1)
        # Raised eyebrows
        draw.arc([cx - int(25*s), head_top - int(5*s),
                  cx, head_top + int(10*s)], 30, 150, fill=STICK_COLOR, width=lw - 1)
        draw.arc([cx, head_top - int(5*s),
                  cx + int(25*s), head_top + int(10*s)], 30, 150, fill=STICK_COLOR, width=lw - 1)
    elif emotion == "thinking":
        draw.line([cx - int(12*s), mouth_y, cx + int(12*s), mouth_y],
                  fill=STICK_COLOR, width=lw - 1)
    elif emotion == "excited":
        draw.arc([cx - int(18*s), mouth_y - int(12*s),
                  cx + int(18*s), mouth_y + int(12*s)],
                 0, 180, fill=STICK_COLOR, width=lw)

    # Neck + Body
    neck_y = head_bot
    body_bot = cy + int(30 * s)
    draw.line([cx, neck_y, cx, body_bot], fill=STICK_COLOR, width=lw)

    # Arms based on pose
    shoulder_y = cy - int(40 * s)
    if pose == "idle":
        draw.line([cx, shoulder_y, cx - int(55*s), cy - int(5*s)],
                  fill=STICK_COLOR, width=lw)
        draw.line([cx, shoulder_y, cx + int(55*s), cy - int(5*s)],
                  fill=STICK_COLOR, width=lw)
    elif pose == "thinking":
        # One hand on chin
        draw.line([cx, shoulder_y, cx - int(55*s), cy - int(5*s)],
                  fill=STICK_COLOR, width=lw)
        draw.line([cx, shoulder_y, cx + int(40*s), cy - int(40*s)],
                  fill=STICK_COLOR, width=lw)
        draw.line([cx + int(40*s), cy - int(40*s),
                   cx + int(20*s), cy - int(70*s)],
                  fill=STICK_COLOR, width=lw)
    elif pose == "excited":
        draw.line([cx, shoulder_y, cx - int(60*s), cy - int(60*s)],
                  fill=STICK_COLOR, width=lw)
        draw.line([cx, shoulder_y, cx + int(60*s), cy - int(60*s)],
                  fill=STICK_COLOR, width=lw)
    elif pose == "pointing":
        draw.line([cx, shoulder_y, cx - int(55*s), cy - int(5*s)],
                  fill=STICK_COLOR, width=lw)
        draw.line([cx, shoulder_y, cx + int(70*s), cy - int(35*s)],
                  fill=STICK_COLOR, width=lw)
    elif pose == "reading":
        # Both arms forward holding book
        draw.line([cx, shoulder_y, cx - int(45*s), cy - int(20*s)],
                  fill=STICK_COLOR, width=lw)
        draw.line([cx, shoulder_y, cx + int(45*s), cy - int(20*s)],
                  fill=STICK_COLOR, width=lw)

    # Legs
    draw.line([cx, body_bot, cx - int(35*s), cy + int(90*s)],
              fill=STICK_COLOR, width=lw)
    draw.line([cx, body_bot, cx + int(35*s), cy + int(90*s)],
              fill=STICK_COLOR, width=lw)
    # Feet
    draw.line([cx - int(35*s), cy + int(90*s),
               cx - int(55*s), cy + int(90*s)],
              fill=STICK_COLOR, width=lw)
    draw.line([cx + int(35*s), cy + int(90*s),
               cx + int(55*s), cy + int(90*s)],
              fill=STICK_COLOR, width=lw)


def _draw_lightbulb(draw, x, y, s=1.0):
    """Draw a lightbulb prop."""
    r = int(30 * s)
    draw.ellipse([x - r, y - r, x + r, y + r],
                 fill=(255, 235, 59), outline=STICK_COLOR, width=int(3*s))
    draw.rectangle([x - int(12*s), y + r - int(5*s),
                    x + int(12*s), y + r + int(20*s)],
                   fill=(200, 200, 200), outline=STICK_COLOR, width=int(2*s))
    # Rays
    for angle in range(0, 360, 45):
        rad = math.radians(angle)
        x1 = x + int((r + 8*s) * math.cos(rad))
        y1 = y + int((r + 8*s) * math.sin(rad))
        x2 = x + int((r + 18*s) * math.cos(rad))
        y2 = y + int((r + 18*s) * math.sin(rad))
        draw.line([x1, y1, x2, y2], fill=(255, 200, 0), width=int(2*s))


def _draw_brain(draw, x, y, s=1.0):
    """Draw a simple brain icon."""
    draw.ellipse([x - int(40*s), y - int(30*s),
                  x + int(40*s), y + int(30*s)],
                 fill=(255, 182, 193), outline=STICK_COLOR, width=int(3*s))
    # Brain wrinkles
    for i in range(3):
        draw.arc([x - int(30*s), y - int(20*s) + i*int(15*s),
                  x + int(30*s), y - int(5*s) + i*int(15*s)],
                 180, 360, fill=STICK_COLOR, width=int(2*s))


def _draw_money(draw, x, y, s=1.0):
    """Draw a money bag."""
    draw.ellipse([x - int(35*s), y - int(25*s),
                  x + int(35*s), y + int(35*s)],
                 fill=(46, 204, 113), outline=STICK_COLOR, width=int(3*s))
    draw.ellipse([x - int(15*s), y - int(40*s),
                  x + int(15*s), y - int(20*s)],
                 fill=(46, 204, 113), outline=STICK_COLOR, width=int(3*s))
    # $ sign
    font = _get_font(int(30*s), bold=True)
    draw.text((x - int(10*s), y - int(15*s)), "$", fill="white", font=font)


def _draw_chart(draw, x, y, s=1.0):
    """Draw an upward chart."""
    points = [
        (x - int(40*s), y + int(30*s)),
        (x - int(20*s), y + int(10*s)),
        (x, y - int(10*s)),
        (x + int(20*s), y - int(25*s)),
        (x + int(40*s), y - int(40*s)),
    ]
    draw.line(points, fill=(231, 76, 60), width=int(4*s))
    for px, py in points:
        r = int(5*s)
        draw.ellipse([px-r, py-r, px+r, py+r], fill=(231, 76, 60))
    # Axes
    draw.line([x - int(45*s), y + int(35*s),
               x + int(45*s), y + int(35*s)], fill=STICK_COLOR, width=int(2*s))
    draw.line([x - int(45*s), y - int(45*s),
               x - int(45*s), y + int(35*s)], fill=STICK_COLOR, width=int(2*s))


PROP_FUNCS = {
    "lightbulb": _draw_lightbulb,
    "brain": _draw_brain,
    "money": _draw_money,
    "chart": _draw_chart,
}

SCENE_PROPS = {
    0: "lightbulb",  # Opening hook
    1: "brain",      # Problem/concept
    2: "chart",      # Solution/growth
    3: "money",      # Result/CTA
}

SCENE_POSES = {
    0: ("shocked", "shocked"),
    1: ("thinking", "thinking"),
    2: ("pointing", "excited"),
    3: ("excited", "excited"),
}


def _draw_text_banner(draw, text: str, w: int, h: int, font_size: int):
    """Draw PP-style yellow text banner at bottom."""
    font = _get_font(font_size, bold=True)
    banner_h = int(font_size * 1.8)
    banner_y = h - banner_h - int(h * 0.05)

    # Yellow banner background
    draw.rectangle([int(w*0.05), banner_y, int(w*0.95), banner_y + banner_h],
                   fill=BANNER_COLOR, outline=STICK_COLOR, width=3)

    # Text centered on banner
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    tx = (w - tw) // 2
    ty = banner_y + (banner_h - (bbox[3] - bbox[1])) // 2
    draw.text((tx + 2, ty + 2), text, fill=(100, 100, 100), font=font)  # shadow
    draw.text((tx, ty), text, fill=BANNER_TEXT_COLOR, font=font)


def _create_frame(
    text: str,
    w: int, h: int,
    frame_idx: int,
    total_frames: int,
    scene_idx: int,
) -> Image.Image:
    img = Image.new("RGB", (w, h), BG_COLOR)
    draw = ImageDraw.Draw(img)

    progress = frame_idx / max(total_frames - 1, 1)

    # Subtle background gradient lines (PP style)
    for i in range(0, w, int(w * 0.08)):
        draw.line([i, 0, i, h], fill=(200, 220, 240), width=1)

    # Scale and position stick figure
    scale = 1.0 if w <= 1080 else 1.4
    fig_x = int(w * 0.35)
    fig_y = int(h * 0.52)

    # Subtle breathing animation
    breath = int(math.sin(progress * math.pi * 3) * 4 * scale)
    pose, emotion = SCENE_POSES.get(scene_idx % 4, ("idle", "happy"))

    _draw_stick_figure(draw, fig_x, fig_y + breath, scale=scale,
                       pose=pose, emotion=emotion)

    # Draw prop on the right side (appears after 20% progress)
    if progress > 0.2:
        prop_name = SCENE_PROPS.get(scene_idx % 4, "lightbulb")
        prop_fn = PROP_FUNCS[prop_name]
        prop_x = int(w * 0.68)
        prop_y = int(h * 0.40)
        prop_scale = min(1.0, (progress - 0.2) / 0.3) * scale
        if prop_scale > 0.1:
            prop_fn(draw, prop_x, prop_y, s=prop_scale)

    # Yellow text banner (PP style) — appears after 10% progress
    if progress > 0.1:
        font_size = max(28, w // 22)
        _draw_text_banner(draw, text, w, h, font_size)

    # Scene number indicator dots at top
    dot_y = int(h * 0.03)
    total_dots = 4
    for d in range(total_dots):
        dot_x = w // 2 + (d - total_dots // 2) * int(w * 0.04)
        color = ACCENT_COLOR if d == scene_idx % 4 else (180, 200, 220)
        r = int(w * 0.01)
        draw.ellipse([dot_x - r, dot_y - r, dot_x + r, dot_y + r], fill=color)

    return img


def create_scene_video(
    text: str,
    bg_color: str,  # kept for API compatibility, not used
    duration: int,
    output_path: str,
    video_type: str = "regular",
    scene_idx: int = 0,
) -> str:
    from config import REGULAR_VIDEO, SHORTS_VIDEO
    spec = REGULAR_VIDEO if video_type == "regular" else SHORTS_VIDEO
    w, h = spec["width"], spec["height"]
    total_frames = duration * FPS

    frames_dir = tempfile.mkdtemp(prefix="frames_")
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)

    # Truncate text if too long
    safe_text = text[:40].upper()

    print(f"    Rendering {total_frames} frames at {FPS}fps...")
    for i in range(total_frames):
        frame = _create_frame(safe_text, w, h, i, total_frames, scene_idx)
        frame.save(os.path.join(frames_dir, f"f{i:05d}.png"))

    result = subprocess.run([
        _ffmpeg(), "-y",
        "-framerate", str(FPS),
        "-i", os.path.join(frames_dir, "f%05d.png"),
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-crf", "20",
        output_path
    ], capture_output=True, text=True)

    shutil.rmtree(frames_dir, ignore_errors=True)

    if result.returncode != 0:
        print(f"FFmpeg error:\n{result.stderr[-1000:]}")
        raise subprocess.CalledProcessError(result.returncode, result.args)

    return output_path


def create_all_scenes(scenes: list, output_dir: str, video_type: str = "regular") -> list:
    os.makedirs(output_dir, exist_ok=True)
    paths = []
    for i, scene in enumerate(scenes):
        out = os.path.join(output_dir, f"scene_{scene['scene_number']:02d}.mp4")
        print(f"  [Animate] Scene {scene['scene_number']}: {scene['text_overlay']}")
        create_scene_video(
            text=scene["text_overlay"],
            bg_color=scene.get("bg_color", "#D6EAF8"),
            duration=scene["duration_seconds"],
            output_path=out,
            video_type=video_type,
            scene_idx=i,
        )
        paths.append(out)
    return paths
