"""
Creates animated scene videos locally using Pillow + FFmpeg.
No external AI API needed — 100% free, runs on any machine.

Style: Dark background + bold white text + animated reveal (like Productive Peter)
"""
import os
import subprocess
import textwrap
from PIL import Image, ImageDraw, ImageFont
from config import REGULAR_VIDEO, SHORTS_VIDEO


def _ffmpeg():
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"

FONT_PATH = os.path.join(os.path.dirname(__file__), "..", "assets", "fonts", "bold.ttf")
FALLBACK_FONT_SIZE = 72


def _get_font(size: int):
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except Exception:
        try:
            # Try system fonts on Windows
            return ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", size)
        except Exception:
            return ImageFont.load_default()


def _hex_to_rgb(hex_color: str) -> tuple:
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def _create_frame(
    text: str,
    bg_color: str,
    width: int,
    height: int,
    progress: float,  # 0.0 to 1.0 — used for text reveal animation
) -> Image.Image:
    """Create a single frame with animated text reveal."""
    img = Image.new("RGB", (width, height), _hex_to_rgb(bg_color))
    draw = ImageDraw.Draw(img)

    # Accent line at top
    accent_color = (99, 102, 241)  # indigo
    draw.rectangle([0, 0, width, 8], fill=accent_color)
    draw.rectangle([0, height - 8, width, height], fill=accent_color)

    # Main text
    font_size = width // 12
    font = _get_font(font_size)

    # Wrap text to fit width
    wrapped = textwrap.fill(text, width=18)
    lines = wrapped.split("\n")

    # Reveal characters based on progress
    visible_chars = int(len(text) * min(progress * 3, 1.0))
    revealed_text = text[:visible_chars]
    wrapped_revealed = textwrap.fill(revealed_text, width=18)

    # Calculate total text height
    line_height = font_size + 20
    total_h = len(lines) * line_height
    y_start = (height - total_h) // 2

    # Draw shadow first
    shadow_offset = 4
    rev_lines = wrapped_revealed.split("\n")
    for i, line in enumerate(rev_lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        text_w = bbox[2] - bbox[0]
        x = (width - text_w) // 2
        y = y_start + i * line_height
        draw.text((x + shadow_offset, y + shadow_offset), line, font=font, fill=(0, 0, 0, 128))
        draw.text((x, y), line, font=font, fill=(255, 255, 255))

    # Progress bar at bottom
    bar_h = 6
    bar_y = height - bar_h - 20
    draw.rectangle([40, bar_y, width - 40, bar_y + bar_h], fill=(50, 50, 80))
    draw.rectangle([40, bar_y, int(40 + (width - 80) * progress), bar_y + bar_h], fill=accent_color)

    return img


def create_scene_video(
    text: str,
    bg_color: str,
    duration: int,
    output_path: str,
    video_type: str = "regular",
) -> str:
    """
    Generate a single scene video as .mp4
    Uses frame-by-frame Pillow rendering → FFmpeg encodes to video
    """
    spec = REGULAR_VIDEO if video_type == "regular" else SHORTS_VIDEO
    w, h = spec["width"], spec["height"]
    fps = spec["fps"]
    total_frames = duration * fps

    frames_dir = output_path.replace(".mp4", "_frames")
    os.makedirs(frames_dir, exist_ok=True)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    print(f"    Rendering {total_frames} frames...")
    for i in range(total_frames):
        progress = i / total_frames
        frame = _create_frame(text, bg_color, w, h, progress)
        frame.save(os.path.join(frames_dir, f"frame_{i:05d}.png"))

    # Encode frames to video with FFmpeg
    subprocess.run([
        _ffmpeg(), "-y",
        "-framerate", str(fps),
        "-i", os.path.join(frames_dir, "frame_%05d.png"),
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-crf", "23",
        output_path
    ], check=True, capture_output=True)

    # Cleanup frames
    import shutil
    shutil.rmtree(frames_dir, ignore_errors=True)

    return output_path


def create_all_scenes(scenes: list, output_dir: str, video_type: str = "regular") -> list:
    """Generate all scene videos, return list of paths."""
    os.makedirs(output_dir, exist_ok=True)
    paths = []
    for scene in scenes:
        out = os.path.join(output_dir, f"scene_{scene['scene_number']:02d}.mp4")
        print(f"  [Animate] Scene {scene['scene_number']}: {scene['text_overlay']}")
        create_scene_video(
            text=scene["text_overlay"],
            bg_color=scene.get("bg_color", "#1a1a2e"),
            duration=scene["duration_seconds"],
            output_path=out,
            video_type=video_type,
        )
        paths.append(out)
    return paths
