"""
Voiceover using espeak (offline, no network, never hangs).
Fallback: silent audio via FFmpeg.
"""
import os
import subprocess
import shutil


def _ffmpeg():
    if shutil.which("ffmpeg"):
        return "ffmpeg"
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"


def _espeak_available() -> bool:
    return shutil.which("espeak") is not None


def _generate_espeak(text: str, output_path: str) -> bool:
    """Use espeak (offline) to generate WAV, convert to MP3 with FFmpeg."""
    try:
        wav_path = output_path.replace(".mp3", ".wav")
        result = subprocess.run([
            "espeak",
            "-v", "en-us+f3",   # female voice variant
            "-s", "150",         # speed (words per minute)
            "-a", "150",         # amplitude/volume
            "-w", wav_path,
            text[:500]           # limit text length
        ], capture_output=True, timeout=30)

        if result.returncode != 0 or not os.path.exists(wav_path):
            return False

        # Convert WAV to MP3
        subprocess.run([
            _ffmpeg(), "-y", "-i", wav_path,
            "-c:a", "libmp3lame", "-q:a", "4",
            output_path
        ], check=True, capture_output=True, timeout=30)

        if os.path.exists(wav_path):
            os.remove(wav_path)

        return os.path.exists(output_path) and os.path.getsize(output_path) > 0
    except Exception as e:
        print(f"  [espeak] Error: {e}")
        return False


def _generate_silence(duration: int, output_path: str) -> bool:
    """Generate silent MP3 using FFmpeg — never fails."""
    try:
        subprocess.run([
            _ffmpeg(), "-y",
            "-f", "lavfi",
            "-i", f"anullsrc=r=44100:cl=stereo:duration={duration}",
            "-c:a", "libmp3lame",
            output_path
        ], check=True, capture_output=True, timeout=30)
        return True
    except Exception as e:
        print(f"  [Silence] Error: {e}")
        return False


def generate_voiceover(text: str, output_path: str, duration_hint: int = 15) -> str:
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)

    if _espeak_available():
        print(f"  [Voice] espeak...")
        if _generate_espeak(text, output_path):
            return output_path

    print(f"  [Voice] Using silence fallback")
    _generate_silence(duration_hint, output_path)
    return output_path


def generate_scene_voiceovers(scenes: list, output_dir: str) -> list:
    os.makedirs(output_dir, exist_ok=True)
    paths = []
    for scene in scenes:
        path = os.path.join(output_dir, f"voice_{scene['scene_number']:02d}.mp3")
        duration = scene.get("duration_seconds", 15)
        print(f"  [Voice] Scene {scene['scene_number']}...")
        generate_voiceover(scene["narration"], path, duration_hint=duration)
        paths.append(path)
    return paths
