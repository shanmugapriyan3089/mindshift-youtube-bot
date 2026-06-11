"""
Fast scene video generation using pure FFmpeg drawtext filter.
No frame-by-frame rendering — generates each scene in 2-3 seconds.
"""
import os
import subprocess


def _ffmpeg():
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"


def _hex_to_ffmpeg_color(hex_color: str) -> str:
    return hex_color.replace("#", "0x")


def create_scene_video(
    text: str,
    bg_color: str,
    duration: int,
    output_path: str,
    video_type: str = "regular",
) -> str:
    """Generate a scene video using FFmpeg drawtext — fast, no Pillow needed."""
    from config import REGULAR_VIDEO, SHORTS_VIDEO
    spec = REGULAR_VIDEO if video_type == "regular" else SHORTS_VIDEO
    w, h = spec["width"], spec["height"]
    fps = spec["fps"]

    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)

    bg = _hex_to_ffmpeg_color(bg_color)
    accent = "0x6366f1"

    # Clean text for FFmpeg (escape special chars)
    safe_text = text.replace("'", "\\'").replace(":", "\\:").replace("\\", "\\\\")

    font_size = w // 10
    bar_h = 8

    # Use drawtext filter — generates video directly without frame rendering
    vf = (
        f"drawbox=x=0:y=0:w={w}:h={bar_h}:color={accent}:t=fill,"
        f"drawbox=x=0:y={h-bar_h}:w={w}:h={bar_h}:color={accent}:t=fill,"
        f"drawtext=text='{safe_text}'"
        f":fontsize={font_size}"
        f":fontcolor=white"
        f":x=(w-text_w)/2:y=(h-text_h)/2"
        f":shadowcolor=black:shadowx=4:shadowy=4"
        f":line_spacing=20"
        f":font=Arial"
    )

    subprocess.run([
        _ffmpeg(), "-y",
        "-f", "lavfi",
        "-i", f"color=c={bg}:size={w}x{h}:duration={duration}:rate={fps}",
        "-vf", vf,
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-crf", "23",
        output_path
    ], check=True, capture_output=True)

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
