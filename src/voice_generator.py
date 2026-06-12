"""
Voiceover pipeline:
1. edge-tts  — Microsoft Jenny Neural (natural, en-US-JennyNeural)
2. gTTS      — Google HTTP TTS fallback
3. espeak    — offline fallback
4. silence   — last resort
All TTS runs in subprocess with hard timeout to prevent pipeline hanging.
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


def _generate_edge_tts(text: str, output_path: str, timeout: int = 45) -> bool:
    """edge-tts Jenny Neural — natural female voice, run in isolated subprocess."""
    try:
        script = (
            "import asyncio, edge_tts\n"
            "async def run():\n"
            f"    c = edge_tts.Communicate({repr(text[:500])}, "
            "'en-US-JennyNeural', rate='+5%', pitch='+0Hz')\n"
            f"    await c.save({repr(output_path)})\n"
            "asyncio.run(run())\n"
        )
        result = subprocess.run(
            [sys.executable, "-c", script],
            timeout=timeout,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"  [edge-tts] stderr: {result.stderr[-200:]}")
        return (result.returncode == 0
                and os.path.exists(output_path)
                and os.path.getsize(output_path) > 500)
    except subprocess.TimeoutExpired:
        print(f"  [edge-tts] Timed out after {timeout}s — killing")
        return False
    except Exception as e:
        print(f"  [edge-tts] Error: {e}")
        return False


def _generate_gtts(text: str, output_path: str) -> bool:
    """gTTS fallback — simple HTTP, no WebSocket."""
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
            print(f"  [gTTS] stderr: {result.stderr[-200:]}")
        return (result.returncode == 0
                and os.path.exists(output_path)
                and os.path.getsize(output_path) > 500)
    except subprocess.TimeoutExpired:
        print("  [gTTS] Timed out")
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
            ["espeak", "-v", "en-us+f3", "-s", "155", "-a", "180",
             "-w", wav, text[:400]],
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
            "-i", "anullsrc=r=44100:cl=stereo",
            "-t", str(duration),
            "-c:a", "libmp3lame", "-q:a", "9", output_path
        ], check=True, capture_output=True, timeout=30)
        return True
    except Exception:
        return False


def generate_voiceover(text: str, output_path: str, duration_hint: int = 15) -> str:
    os.makedirs(
        os.path.dirname(output_path) if os.path.dirname(output_path) else ".",
        exist_ok=True
    )

    print("  [Voice] edge-tts (Jenny Neural)...")
    if _generate_edge_tts(text, output_path):
        print("  [Voice] edge-tts OK")
        return output_path

    print("  [Voice] gTTS fallback...")
    if _generate_gtts(text, output_path):
        print("  [Voice] gTTS OK")
        return output_path

    print("  [Voice] espeak fallback...")
    if _generate_espeak(text, output_path):
        print("  [Voice] espeak OK")
        return output_path

    print("  [Voice] silence fallback")
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
