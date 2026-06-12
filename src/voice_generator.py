"""
Voiceover using edge-tts in isolated subprocess (prevents hanging).
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


def _generate_edge_tts(text: str, output_path: str, timeout: int = 40) -> bool:
    """
    Run edge-tts in a child subprocess with hard kill timeout.
    If it hangs, the subprocess is killed after timeout seconds.
    """
    try:
        # Escape text for safe shell passing
        safe_text = text[:400].replace('"', "'").replace('\n', ' ')
        script = (
            f"import asyncio, edge_tts\n"
            f"async def run():\n"
            f"    c = edge_tts.Communicate({repr(safe_text)}, 'en-US-JennyNeural', rate='+5%', pitch='+0Hz')\n"
            f"    await c.save({repr(output_path)})\n"
            f"asyncio.run(run())\n"
        )
        result = subprocess.run(
            [sys.executable, "-c", script],
            timeout=timeout,
            capture_output=True,
            text=True
        )
        return result.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 500
    except subprocess.TimeoutExpired:
        print(f"  [edge-tts] Timed out after {timeout}s")
        return False
    except Exception as e:
        print(f"  [edge-tts] Error: {e}")
        return False


def _generate_espeak(text: str, output_path: str) -> bool:
    """Offline fallback using espeak."""
    if not shutil.which("espeak"):
        return False
    try:
        wav = output_path.replace(".mp3", ".wav")
        r1 = subprocess.run(
            ["espeak", "-v", "en-us+f3", "-s", "155", "-a", "160", "-w", wav, text[:500]],
            capture_output=True, timeout=20
        )
        if r1.returncode != 0 or not os.path.exists(wav):
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
            "-i", f"anullsrc=r=44100:cl=stereo:duration={duration}",
            "-c:a", "libmp3lame", output_path
        ], check=True, capture_output=True, timeout=30)
        return True
    except Exception:
        return False


def generate_voiceover(text: str, output_path: str, duration_hint: int = 15) -> str:
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)

    # Try edge-tts first (best quality, runs in subprocess)
    print(f"  [Voice] edge-tts...")
    if _generate_edge_tts(text, output_path):
        print(f"  [Voice] edge-tts success")
        return output_path

    # Try espeak (offline)
    print(f"  [Voice] espeak fallback...")
    if _generate_espeak(text, output_path):
        return output_path

    # Silent fallback
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
