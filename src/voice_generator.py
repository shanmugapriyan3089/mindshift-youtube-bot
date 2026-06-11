"""
Voiceover generation with fallback chain:
  1. gTTS (Google TTS, simple HTTP, reliable on GitHub Actions)
  2. edge-tts (Microsoft neural, better quality)
  3. Silent audio (FFmpeg generated — never hangs)
"""
import os
import asyncio
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
    """Google TTS — simple HTTP, works reliably on GitHub Actions."""
    try:
        from gtts import gTTS
        tts = gTTS(text=text, lang="en", slow=False)
        tts.save(output_path)
        return os.path.exists(output_path) and os.path.getsize(output_path) > 0
    except Exception as e:
        print(f"  [gTTS] Failed: {e}")
        return False


def _generate_edge_tts(text: str, output_path: str) -> bool:
    """Microsoft edge-tts — higher quality neural voice."""
    try:
        import edge_tts

        async def _run():
            communicate = edge_tts.Communicate(text, "en-US-JennyNeural",
                                               rate="+0%", pitch="+5Hz")
            await asyncio.wait_for(communicate.save(output_path), timeout=45)

        asyncio.run(_run())
        return os.path.exists(output_path) and os.path.getsize(output_path) > 0
    except Exception as e:
        print(f"  [edge-tts] Failed: {e}")
        return False


def _generate_silence(duration_hint: int, output_path: str) -> bool:
    """FFmpeg silent audio — last resort, never fails."""
    try:
        subprocess.run([
            _ffmpeg(), "-y",
            "-f", "lavfi",
            "-i", f"anullsrc=r=44100:cl=stereo:duration={duration_hint}",
            "-c:a", "libmp3lame",
            output_path
        ], check=True, capture_output=True)
        return True
    except Exception as e:
        print(f"  [Silence fallback] Failed: {e}")
        return False


def generate_voiceover(text: str, output_path: str, duration_hint: int = 15) -> str:
    """Generate voiceover with fallback chain."""
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)

    # Try gTTS first (most reliable on GitHub Actions)
    if _generate_gtts(text, output_path):
        return output_path

    # Try edge-tts
    if _generate_edge_tts(text, output_path):
        return output_path

    # Silent fallback — never blocks the pipeline
    print(f"  [Voice] Using silent fallback for this scene")
    _generate_silence(duration_hint, output_path)
    return output_path


def generate_scene_voiceovers(scenes: list, output_dir: str) -> list:
    """Generate one MP3 per scene, return list of paths."""
    os.makedirs(output_dir, exist_ok=True)
    paths = []
    for scene in scenes:
        path = os.path.join(output_dir, f"voice_{scene['scene_number']:02d}.mp3")
        duration = scene.get("duration_seconds", 15)
        print(f"  [Voice] Scene {scene['scene_number']}...")
        generate_voiceover(scene["narration"], path, duration_hint=duration)
        paths.append(path)
    return paths
