"""
Assembles scene clips + voiceovers + background music into final video.
Handles both regular (16:9, 1920x1080) and Shorts (9:16, 1080x1920).
"""
import os
import subprocess
import glob
from config import REGULAR_VIDEO, SHORTS_VIDEO, MUSIC_DIR


def _ffmpeg():
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"


def _get_random_music() -> str | None:
    patterns = ["*.mp3", "*.wav", "*.m4a"]
    for pat in patterns:
        files = glob.glob(os.path.join(MUSIC_DIR, pat))
        if files:
            import random
            return random.choice(files)
    return None


def _build_ffmpeg_concat_list(clip_paths: list, voice_paths: list, tmp_dir: str) -> str:
    """Merge each video clip with its voiceover, write concat list."""
    merged_clips = []
    for i, (clip, voice) in enumerate(zip(clip_paths, voice_paths)):
        out = os.path.join(tmp_dir, f"merged_{i:02d}.mp4")
        # Merge video + audio, extend/trim video to match audio length
        subprocess.run([
            _ffmpeg(), "-y",
            "-i", clip,
            "-i", voice,
            "-filter_complex",
            "[0:v]setpts=PTS/TB[v];[1:a]aformat=sample_rates=44100:channel_layouts=stereo[a]",
            "-map", "[v]", "-map", "[a]",
            "-shortest",
            "-c:v", "libx264", "-c:a", "aac",
            out
        ], check=True, capture_output=True)
        merged_clips.append(out)

    concat_file = os.path.join(tmp_dir, "concat.txt")
    with open(concat_file, "w") as f:
        for clip in merged_clips:
            f.write(f"file '{clip}'\n")
    return concat_file


def _resize_for_format(input_path: str, output_path: str, video_type: str):
    """Resize/crop to correct aspect ratio."""
    spec = REGULAR_VIDEO if video_type == "regular" else SHORTS_VIDEO
    w, h = spec["width"], spec["height"]
    subprocess.run([
        _ffmpeg(), "-y", "-i", input_path,
        "-vf", f"scale={w}:{h}:force_original_aspect_ratio=decrease,"
               f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:color=0xFFD6E0",
        "-c:v", "libx264", "-c:a", "aac",
        "-r", str(spec["fps"]),
        output_path
    ], check=True, capture_output=True)


def assemble_video(
    clip_paths: list,
    voice_paths: list,
    output_path: str,
    video_type: str = "regular",
    tmp_dir: str = None,
) -> str:
    """
    Full assembly pipeline:
    1. Merge each clip with its voiceover
    2. Concatenate all scenes
    3. Resize to correct format
    4. Mix in background music at low volume
    5. Add captions overlay (scene titles)
    """
    import tempfile
    if tmp_dir is None:
        tmp_dir = tempfile.mkdtemp(prefix="yt_assemble_")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    print("  [Assemble] Merging clips with voiceovers...")
    concat_file = _build_ffmpeg_concat_list(clip_paths, voice_paths, tmp_dir)

    # Concatenate all scenes
    concat_out = os.path.join(tmp_dir, "concat_out.mp4")
    subprocess.run([
        _ffmpeg(), "-y",
        "-f", "concat", "-safe", "0",
        "-i", concat_file,
        "-c", "copy",
        concat_out
    ], check=True, capture_output=True)

    print("  [Assemble] Resizing for format...")
    resized = os.path.join(tmp_dir, "resized.mp4")
    _resize_for_format(concat_out, resized, video_type)

    # Mix background music if available
    music_path = _get_random_music()
    if music_path:
        print(f"  [Assemble] Adding background music: {os.path.basename(music_path)}")
        final = output_path
        subprocess.run([
            _ffmpeg(), "-y",
            "-i", resized,
            "-stream_loop", "-1", "-i", music_path,
            "-filter_complex",
            "[1:a]volume=0.15[music];[0:a][music]amix=inputs=2:duration=first[aout]",
            "-map", "0:v", "-map", "[aout]",
            "-c:v", "copy", "-c:a", "aac",
            "-shortest",
            final
        ], check=True, capture_output=True)
    else:
        import shutil
        shutil.copy(resized, output_path)

    print(f"  [Assemble] Final video: {output_path}")
    return output_path


def generate_thumbnail(title: str, output_path: str, video_type: str = "regular") -> str:
    """Generate a simple thumbnail using FFmpeg drawtext."""
    spec = REGULAR_VIDEO if video_type == "regular" else SHORTS_VIDEO
    w, h = spec["width"], spec["height"]
    short_title = title[:40] + "..." if len(title) > 40 else title

    subprocess.run([
        _ffmpeg(), "-y",
        "-f", "lavfi",
        "-i", f"color=c=0xFFB3C6:size={w}x{h}:duration=1:rate=1",
        "-vf", (
            f"drawtext=text='{short_title}':fontsize={w//20}:fontcolor=white:"
            f"x=(w-text_w)/2:y=(h-text_h)/2:shadowcolor=black:shadowx=3:shadowy=3"
        ),
        "-frames:v", "1",
        output_path
    ], check=True, capture_output=True)
    return output_path
