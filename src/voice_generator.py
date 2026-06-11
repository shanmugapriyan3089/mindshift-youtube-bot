"""
Voiceover generation using edge-tts (free, Microsoft neural voices).
Best voices for baby/kids content: warm, friendly, female.
"""
import asyncio
import os
import edge_tts

# Warm, friendly voice — great for baby content
DEFAULT_VOICE = "en-US-JennyNeural"
BABY_VOICE_OPTIONS = [
    "en-US-JennyNeural",    # Warm, friendly female
    "en-US-AriaNeural",     # Expressive female
    "en-GB-SoniaNeural",    # British female, clear
    "en-AU-NatashaNeural",  # Australian female, soft
]


async def _generate_async(text: str, output_path: str, voice: str, rate: str, pitch: str):
    communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
    await asyncio.wait_for(communicate.save(output_path), timeout=60)


def generate_voiceover(
    text: str,
    output_path: str,
    voice: str = DEFAULT_VOICE,
    rate: str = "+0%",
    pitch: str = "+5Hz",
) -> str:
    """
    Generate MP3 voiceover from text.
    rate: speaking speed e.g. "-10%" slower, "+10%" faster
    pitch: voice pitch e.g. "+5Hz" slightly higher (warmer for baby content)
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    asyncio.run(_generate_async(text, output_path, voice, rate, pitch))
    return output_path


def generate_scene_voiceovers(scenes: list, output_dir: str) -> list:
    """Generate one MP3 per scene, return list of paths."""
    os.makedirs(output_dir, exist_ok=True)
    paths = []
    for scene in scenes:
        path = os.path.join(output_dir, f"voice_{scene['scene_number']:02d}.mp3")
        print(f"  [Voice] Scene {scene['scene_number']}...")
        generate_voiceover(scene["narration"], path)
        paths.append(path)
    return paths
