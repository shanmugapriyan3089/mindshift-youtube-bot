"""
Voiceover pipeline (best free quality):
1. Kokoro-82M   — near-ElevenLabs quality, open source, offline after first download
2. edge-tts     — Microsoft Jenny Neural, natural, free
3. gTTS         — Google HTTP TTS, decent fallback
4. espeak       — offline last resort
5. silence      — absolute fallback

All TTS runs in isolated subprocess with hard timeout — pipeline never hangs.
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


# ── 1. Kokoro-82M ─────────────────────────────────────────────────────────────

def _generate_kokoro(text: str, output_path: str, timeout: int = 60) -> bool:
    """
    Kokoro-82M — open source, near-ElevenLabs quality.
    Voice: af_nicole (American female, clear and natural).
    Model auto-downloads to ~/.cache/huggingface on first run (~300 MB).
    """
    wav_path = output_path.replace(".mp3", "_kok.wav")
    try:
        script = (
            "import sys, numpy as np, soundfile as sf\n"
            "from kokoro import KPipeline\n"
            "pipe = KPipeline(lang_code='a')\n"
            f"chunks = [a for _,_,a in pipe({repr(text)}, voice='af_nicole', speed=1.05)]\n"
            "if not chunks: sys.exit(1)\n"
            f"sf.write({repr(wav_path)}, np.concatenate(chunks), 24000)\n"
        )
        r = subprocess.run(
            [sys.executable, "-c", script],
            timeout=timeout, capture_output=True, text=True
        )
        if r.returncode != 0:
            print(f"  [Kokoro] stderr: {r.stderr[-300:]}")
            return False
        if not os.path.exists(wav_path) or os.path.getsize(wav_path) < 1000:
            return False
        # Convert wav → mp3
        subprocess.run(
            [_ffmpeg(), "-y", "-i", wav_path,
             "-c:a", "libmp3lame", "-q:a", "2", output_path],
            check=True, capture_output=True, timeout=30
        )
        return os.path.exists(output_path) and os.path.getsize(output_path) > 500
    except subprocess.TimeoutExpired:
        print(f"  [Kokoro] Timed out after {timeout}s")
        return False
    except Exception as e:
        print(f"  [Kokoro] Error: {e}")
        return False
    finally:
        if os.path.exists(wav_path):
            os.remove(wav_path)


# ── 2. edge-tts (Microsoft Jenny Neural) ─────────────────────────────────────

def _generate_edge_tts(text: str, output_path: str, timeout: int = 60) -> bool:
    """Microsoft Azure neural TTS via edge-tts — free, no API key. Retries 3×."""
    import time
    for attempt in range(3):
        if attempt > 0:
            wait = 4 + attempt * 3  # 7s, 10s between retries — avoid rate limit
            print(f"  [edge-tts] Retry {attempt}/2 after {wait}s...")
            time.sleep(wait)
        try:
            script = (
                "import asyncio, edge_tts\n"
                "async def run():\n"
                f"    c = edge_tts.Communicate({repr(text)}, "
                "'en-US-JennyNeural', rate='+5%', pitch='+0Hz')\n"
                f"    await c.save({repr(output_path)})\n"
                "asyncio.run(run())\n"
            )
            r = subprocess.run(
                [sys.executable, "-c", script],
                timeout=timeout, capture_output=True, text=True
            )
            if r.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 500:
                return True
            print(f"  [edge-tts] attempt {attempt+1} failed: {r.stderr[-150:]}")
        except subprocess.TimeoutExpired:
            print(f"  [edge-tts] Timed out after {timeout}s (attempt {attempt+1})")
        except Exception as e:
            print(f"  [edge-tts] Error: {e}")
    return False


# ── 3. gTTS ───────────────────────────────────────────────────────────────────

def _generate_gtts(text: str, output_path: str) -> bool:
    import time
    for attempt in range(2):
        if attempt > 0:
            time.sleep(5)
        try:
            script = (
                f"from gtts import gTTS\n"
                f"gTTS(text={repr(text)}, lang='en', slow=False).save({repr(output_path)})\n"
            )
            r = subprocess.run(
                [sys.executable, "-c", script],
                timeout=60, capture_output=True, text=True
            )
            if r.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 500:
                return True
            print(f"  [gTTS] attempt {attempt+1} failed: {r.stderr[-100:]}")
        except Exception as e:
            print(f"  [gTTS] Error: {e}")
    return False


# ── 4. espeak ─────────────────────────────────────────────────────────────────

def _generate_espeak(text: str, output_path: str) -> bool:
    if not shutil.which("espeak"):
        return False
    try:
        wav = output_path.replace(".mp3", "_esp.wav")
        r = subprocess.run(
            ["espeak", "-v", "en-us+f3", "-s", "155", "-a", "180",
             "-w", wav, text[:600]],
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


# ── 5. Silence ────────────────────────────────────────────────────────────────

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


# ── Main entry ────────────────────────────────────────────────────────────────

def generate_voiceover(text: str, output_path: str, duration_hint: int = 15) -> str:
    os.makedirs(
        os.path.dirname(output_path) if os.path.dirname(output_path) else ".",
        exist_ok=True
    )

    print("  [Voice] Kokoro-82M (best quality)...")
    if _generate_kokoro(text, output_path):
        print("  [Voice] Kokoro OK ✓")
        return output_path

    print("  [Voice] edge-tts (Jenny Neural)...")
    if _generate_edge_tts(text, output_path):
        print("  [Voice] edge-tts OK ✓")
        return output_path

    print("  [Voice] gTTS fallback...")
    if _generate_gtts(text, output_path):
        print("  [Voice] gTTS OK ✓")
        return output_path

    print("  [Voice] espeak fallback...")
    if _generate_espeak(text, output_path):
        print("  [Voice] espeak OK ✓")
        return output_path

    print("  [Voice] silence fallback")
    _generate_silence(duration_hint, output_path)
    return output_path


def _pad_audio_to_duration(audio_path: str, target_sec: int):
    """Pad audio with silence so it fills the full scene duration.

    This is critical for shorts: TTS for 10-15 words is only ~5s but the
    scene video is 13s. Without padding, FFmpeg's -shortest cuts the merged
    video to ~20s (4 scenes × 5s) leaving most of the short silent.

    Uses apad without -t so we never truncate audio that's already longer.
    """
    ff = _ffmpeg()
    tmp = audio_path + "_pad.mp3"
    try:
        r = subprocess.run([
            ff, "-y", "-i", audio_path,
            "-af", f"apad=whole_dur={target_sec}",
            "-c:a", "libmp3lame", "-q:a", "4", tmp
        ], capture_output=True, timeout=30)
        if r.returncode == 0 and os.path.exists(tmp) and os.path.getsize(tmp) > 100:
            os.replace(tmp, audio_path)
    except Exception as e:
        print(f"  [Voice] Pad failed: {e}")
    finally:
        if os.path.exists(tmp):
            try:
                os.remove(tmp)
            except Exception:
                pass


def generate_scene_voiceovers(scenes: list, output_dir: str) -> list:
    import time
    os.makedirs(output_dir, exist_ok=True)
    paths = []
    for i, scene in enumerate(scenes):
        path = os.path.join(output_dir, f"voice_{scene['scene_number']:02d}.mp3")
        duration = scene.get("duration_seconds", 15)
        print(f"  [Voice] Scene {scene['scene_number']}/{len(scenes)}...")
        generate_voiceover(scene["narration"], path, duration_hint=duration)
        # Pad voice to scene duration — ensures concat_audio matches concat_video
        # so -shortest in assembler doesn't cut the video short (critical for shorts)
        _pad_audio_to_duration(path, duration)
        paths.append(path)
        # Pause between scenes — prevents edge-tts rate limiting
        if i < len(scenes) - 1:
            time.sleep(1.5)
    return paths
