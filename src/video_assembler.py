"""
Simple, reliable video assembly using FFmpeg.
All subprocess calls have timeouts to prevent hanging.
"""
import os
import subprocess
import shutil
import glob
from config import REGULAR_VIDEO, SHORTS_VIDEO, MUSIC_DIR


def _ffmpeg():
    if shutil.which("ffmpeg"):
        return "ffmpeg"
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"


def _run(cmd, timeout=120):
    """Run FFmpeg command with timeout. Prints error if fails."""
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if result.returncode != 0:
        print(f"  [FFmpeg warn]: {result.stderr[-300:]}")
    return result.returncode == 0


def _get_random_music() -> str | None:
    for pat in ["*.mp3", "*.wav", "*.m4a"]:
        files = glob.glob(os.path.join(MUSIC_DIR, pat))
        if files:
            import random
            return random.choice(files)
    return None


def assemble_video(
    clip_paths: list,
    voice_paths: list,
    output_path: str,
    video_type: str = "regular",
    tmp_dir: str = None,
) -> str:
    import tempfile
    if tmp_dir is None:
        tmp_dir = tempfile.mkdtemp(prefix="yt_assemble_")

    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    ff = _ffmpeg()

    # Step 1: Concat all video clips
    print("  [Assemble] Concatenating video clips...")
    concat_v_txt = os.path.join(tmp_dir, "concat_v.txt")
    with open(concat_v_txt, "w") as f:
        for p in clip_paths:
            f.write(f"file '{p}'\n")

    concat_video = os.path.join(tmp_dir, "concat_video.mp4")
    # Try fast stream-copy first (all clips are already H.264 — no re-encode needed)
    ok = _run([ff, "-y", "-f", "concat", "-safe", "0",
               "-i", concat_v_txt, "-c", "copy", concat_video], timeout=120)
    if not ok or not os.path.exists(concat_video) or os.path.getsize(concat_video) < 1000:
        print("  [Assemble] copy failed, re-encoding with ultrafast preset...")
        _run([ff, "-y", "-f", "concat", "-safe", "0",
              "-i", concat_v_txt, "-c:v", "libx264", "-preset", "ultrafast",
              "-pix_fmt", "yuv420p", concat_video], timeout=600)

    # Step 2: Concat all voice clips
    print("  [Assemble] Concatenating audio...")
    concat_a_txt = os.path.join(tmp_dir, "concat_a.txt")
    with open(concat_a_txt, "w") as f:
        for p in voice_paths:
            f.write(f"file '{p}'\n")

    concat_audio = os.path.join(tmp_dir, "concat_audio.mp3")
    _run([ff, "-y", "-f", "concat", "-safe", "0",
          "-i", concat_a_txt, "-c", "copy",
          concat_audio], timeout=120)

    # Step 3: Mix background music if available
    music_path = _get_random_music()
    if music_path and os.path.exists(concat_audio):
        print(f"  [Assemble] Mixing background music...")
        mixed_audio = os.path.join(tmp_dir, "mixed_audio.mp3")
        success = _run([
            ff, "-y",
            "-i", concat_audio,
            "-stream_loop", "-1", "-i", music_path,
            "-filter_complex",
            "[0:a]volume=1.0[v];[1:a]volume=0.12[m];[v][m]amix=inputs=2:duration=first[out]",
            "-map", "[out]",
            "-c:a", "libmp3lame",
            mixed_audio
        ], timeout=60)
        if success and os.path.exists(mixed_audio):
            concat_audio = mixed_audio

    # Step 4: Merge video + audio
    print("  [Assemble] Merging video and audio...")
    _run([
        ff, "-y",
        "-i", concat_video,
        "-i", concat_audio,
        "-c:v", "copy",
        "-c:a", "aac",
        "-shortest",
        "-map", "0:v:0",
        "-map", "1:a:0",
        output_path
    ], timeout=300)

    # If merge failed, try video-only
    if not os.path.exists(output_path) or os.path.getsize(output_path) < 1000:
        print("  [Assemble] Fallback: video only (no audio)")
        shutil.copy(concat_video, output_path)

    print(f"  [Assemble] Done: {output_path}")
    return output_path


def generate_thumbnail(title: str, output_path: str, video_type: str = "regular") -> str:
    spec = REGULAR_VIDEO if video_type == "regular" else SHORTS_VIDEO
    w, h = spec["width"], spec["height"]
    short_title = title[:35].replace("'", "").replace(":", " ")

    font_file = ""
    for path in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                 "C:/Windows/Fonts/arialbd.ttf"]:
        if os.path.exists(path):
            font_file = f":fontfile={path}"
            break

    try:
        _run([
            _ffmpeg(), "-y",
            "-f", "lavfi",
            "-i", f"color=c=0x1a1a2e:size={w}x{h}:duration=1:rate=1",
            "-vf", (
                f"drawtext=text='{short_title}'"
                f"{font_file}"
                f":fontsize={w//18}"
                f":fontcolor=white"
                f":x=(w-text_w)/2:y=(h-text_h)/2"
                f":shadowcolor=black:shadowx=3:shadowy=3"
            ),
            "-frames:v", "1",
            output_path
        ], timeout=30)
    except Exception:
        pass

    return output_path
