"""
Voiceover using gTTS (Google TTS - simple HTTP, most reliable on GitHub Actions).
Falls back to espeak, then silence.
"""
import os
import sys
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


def _generate_gtts(text: str, output_path: str) -> bool:
    """gTTS in subprocess with hard timeout — simple HTTP, no WebSocket issues."""
    try:
        script = (
            f"from gtts import gTTS\n"
            f"tts = gTTS(text={repr(text[:400])}, lang='en', slow=False, tld='com')\n"
            f"tts.save({repr(output_path)})\n"
        )
        result = subprocess.run(
            [sys.executable, "-c", script],
            timeout=45,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"  [gTTS stderr]: {result.stderr[-200:]}")
        return result.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 500
    except subprocess.TimeoutExpired:
        print(f"  [gTTS] Timed out")
        return False
    except Exception as e:
        print(f"  [gTTS] Error: {e}")
        return False


def _generate_espeak(text: str, output_path: str) -> bool:
    """Offline fallback using espeak."""
    if not shutil.which("espeak"):
        return False
    try:
        wav = output_path.replace(".mp3", "_esp.wav")
        r = subprocess.run(
            ["espeak", "-v", "en-us+f3", "-s", "155", "-a", "180", "-w", wav, text[:400]],
            capture_output=True, timeout=20
        )
        if r.returncode != 0 or not os.path.exists(wav):
            return False
        subprocess.run(
            [_ffmpeg(), "-y", "-i", wav, "-c:a", "libmp3lame", "-q:a", "3", output_path],
            check=True, capture_output=True, timeout=20
        )
        if os.path.exists(wav):
            os.remove(wav)
        return os.path.exists(output_path) and os.path.getsize(output_path) > 0
    except Exception as e:
        print(f"  [espeak] Error: {e}")
        return False


def _generate_silence(duration: int, output_path: str) -> bool:
    try:
        subprocess.run([
            _ffmpeg(), "-y", "-f", "lavfi",
            "-i", f"anullsrc=r=44100:cl=stereo",
            "-t", str(duration),
            "-c:a", "libmp3lame", "-q:a", "9", output_path
        ], check=True, capture_output=True, timeout=30)
        return True
    except Exception:
        return False


def generate_voiceover(text: str, output_path: str, duration_hint: int = 15) -> str:
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)

    print(f"  [Voice] gTTS...")
    if _generate_gtts(text, output_path):
        print(f"  [Voice] gTTS OK")
        return output_path

    print(f"  [Voice] espeak fallback...")
    if _generate_espeak(text, output_path):
        print(f"  [Voice] espeak OK")
        return output_path

    print(f"  [Voice] silence fallback")
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
