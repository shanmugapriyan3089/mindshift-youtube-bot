"""
Stock footage + bold captions style (Alux.com / top faceless channels).
Fetches relevant Pexels videos per scene, overlays bold captions with FFmpeg.
"""
import os
import random
import subprocess
import shutil
import requests
import tempfile
from config import PEXELS_API_KEY, REGULAR_VIDEO, SHORTS_VIDEO


def _ffmpeg():
    if shutil.which("ffmpeg"):
        return "ffmpeg"
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"


# ── Pexels API ────────────────────────────────────────────────────────────────

def _search_pexels_video(keyword: str, orientation: str = "landscape") -> str | None:
    """Search Pexels for a video clip matching the keyword. Returns download URL."""
    if not PEXELS_API_KEY:
        return None
    try:
        headers = {"Authorization": PEXELS_API_KEY}
        params = {
            "query": keyword,
            "orientation": orientation,
            "size": "medium",
            "per_page": 10,
        }
        r = requests.get("https://api.pexels.com/videos/search",
                         headers=headers, params=params, timeout=15)
        r.raise_for_status()
        videos = r.json().get("videos", [])
        if not videos:
            return None

        video = random.choice(videos[:5])
        # Pick HD file
        files = sorted(video["video_files"],
                       key=lambda x: x.get("width", 0), reverse=True)
        for f in files:
            if f.get("width", 0) >= 1280:
                return f["link"]
        return files[0]["link"] if files else None
    except Exception as e:
        print(f"  [Pexels] Error for '{keyword}': {e}")
        return None


def _download_video(url: str, output_path: str) -> str:
    r = requests.get(url, stream=True, timeout=60)
    r.raise_for_status()
    with open(output_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
    return output_path


# ── Caption Overlay ───────────────────────────────────────────────────────────

def _overlay_caption(
    input_path: str,
    output_path: str,
    caption: str,
    narration: str,
    duration: int,
    w: int, h: int,
) -> str:
    """
    Overlay bold white caption + dark semi-transparent background on video.
    Style: Bold white text, dark gradient at bottom (like viral motivational channels).
    """
    safe_caption = (caption.replace("'", "")
                           .replace('"', "")
                           .replace(":", " ")
                           .replace("\\", "")
                           .replace("%", "pct")
                           .replace("\n", " "))

    font_size = max(48, w // 16)
    bar_h = int(font_size * 2.2)
    bar_y = h - bar_h - int(h * 0.04)

    font_file = ""
    for path in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ]:
        if os.path.exists(path):
            font_file = f":fontfile={path}"
            break

    vf = (
        # Trim/loop source video to exact duration
        f"trim=duration={duration},setpts=PTS-STARTPTS,"
        # Dark semi-transparent bar at bottom
        f"drawbox=x=0:y={bar_y}:w={w}:h={bar_h}:color=black@0.7:t=fill,"
        # Bold white caption
        f"drawtext=text='{safe_caption}'"
        f"{font_file}"
        f":fontsize={font_size}"
        f":fontcolor=white"
        f":x=(w-text_w)/2:y={bar_y}+(({bar_h}-text_h)/2)"
        f":shadowcolor=black:shadowx=2:shadowy=2"
    )

    result = subprocess.run([
        _ffmpeg(), "-y",
        "-i", input_path,
        "-vf", vf,
        "-t", str(duration),
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-crf", "22",
        "-an",
        output_path
    ], capture_output=True, text=True)

    if result.returncode != 0:
        print(f"  [FFmpeg caption error]: {result.stderr[-500:]}")
        raise subprocess.CalledProcessError(result.returncode, result.args)

    return output_path


def _resize_clip(input_path: str, output_path: str, w: int, h: int, duration: int):
    """Resize and crop video to exact dimensions."""
    subprocess.run([
        _ffmpeg(), "-y",
        "-i", input_path,
        "-t", str(duration),
        "-vf", (
            f"scale={w}:{h}:force_original_aspect_ratio=increase,"
            f"crop={w}:{h}"
        ),
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-crf", "22",
        "-an",
        output_path
    ], check=True, capture_output=True)


def _fallback_clip(output_path: str, caption: str, duration: int, w: int, h: int):
    """Generate a gradient background clip when Pexels is unavailable."""
    safe = caption.replace("'", "").replace(":", " ")[:40]
    font_size = max(48, w // 14)
    font_file = ""
    for path in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]:
        if os.path.exists(path):
            font_file = f":fontfile={path}"
            break

    subprocess.run([
        _ffmpeg(), "-y",
        "-f", "lavfi",
        "-i", f"color=c=0x1a1a2e:size={w}x{h}:duration={duration}:rate=24",
        "-vf", (
            f"drawtext=text='{safe}'"
            f"{font_file}"
            f":fontsize={font_size}"
            f":fontcolor=white"
            f":x=(w-text_w)/2:y=(h-text_h)/2"
            f":shadowcolor=black:shadowx=4:shadowy=4"
        ),
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-crf", "22",
        output_path
    ], check=True, capture_output=True)


# ── Main entry ────────────────────────────────────────────────────────────────

def create_scene_video_stock(
    caption: str,
    keyword: str,
    duration: int,
    output_path: str,
    video_type: str = "regular",
) -> str:
    spec = REGULAR_VIDEO if video_type == "regular" else SHORTS_VIDEO
    w, h = spec["width"], spec["height"]
    orientation = "landscape" if video_type == "regular" else "portrait"

    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    tmp = tempfile.mkdtemp(prefix="stock_")

    try:
        raw_path = os.path.join(tmp, "raw.mp4")
        resized_path = os.path.join(tmp, "resized.mp4")

        # Try Pexels
        video_url = _search_pexels_video(keyword, orientation)
        if video_url:
            print(f"    Downloading Pexels clip for '{keyword}'...")
            _download_video(video_url, raw_path)
            _resize_clip(raw_path, resized_path, w, h, duration)
            _overlay_caption(resized_path, output_path, caption, caption, duration, w, h)
        else:
            print(f"    No Pexels result — using fallback background")
            _fallback_clip(output_path, caption, duration, w, h)

    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    return output_path


def create_all_scenes_stock(scenes: list, output_dir: str, video_type: str = "regular") -> list:
    os.makedirs(output_dir, exist_ok=True)
    paths = []
    for scene in scenes:
        out = os.path.join(output_dir, f"scene_{scene['scene_number']:02d}.mp4")
        keyword = scene.get("keyword", scene.get("text_overlay", "motivation success"))
        caption = scene.get("text_overlay", "")
        print(f"  [Stock] Scene {scene['scene_number']}: '{caption}' | keyword: '{keyword}'")
        create_scene_video_stock(
            caption=caption,
            keyword=keyword,
            duration=scene["duration_seconds"],
            output_path=out,
            video_type=video_type,
        )
        paths.append(out)
    return paths
