"""
YouTube Automation Pipeline — Motivational/Psychology Niche
High RPM ($10-14), 100% free, no external video APIs needed.

Usage:
  python main.py --type regular    # 8-10 min motivational video
  python main.py --type shorts     # 58 sec motivational short
  python main.py --type both
"""
import os
import sys
import argparse
import tempfile

sys.path.insert(0, os.path.dirname(__file__))

from config import REGULAR_OUTPUT_DIR, SHORTS_OUTPUT_DIR
from src.script_generator import generate_script, pick_topic
from src.simple_animator import create_all_scenes
from src.voice_generator import generate_scene_voiceovers
from src.video_assembler import assemble_video, generate_thumbnail
from src.youtube_uploader import upload_video, save_upload_log


def run_pipeline(video_type: str = "regular"):
    print(f"\n{'='*55}")
    print(f"  MOTIVATIONAL CHANNEL PIPELINE — {video_type.upper()}")
    print(f"  Niche: Psychology & Success Mindset ($10-14 RPM)")
    print(f"{'='*55}\n")

    output_dir = REGULAR_OUTPUT_DIR if video_type == "regular" else SHORTS_OUTPUT_DIR

    # 1. Pick topic — slot 0 reserved for this pipeline
    slot = int(os.getenv("PIPELINE_SLOT", "0"))
    topic = pick_topic(slot)
    print(f"[1/6] Topic: {topic}\n")

    # 2. Generate script with Groq (free, 14,400 req/day)
    print("[2/6] Generating script with Groq (Llama 3.3 70B)...")
    script = generate_script(topic, video_type)
    print(f"      Title: {script['title']}")
    print(f"      Scenes: {len(script['scenes'])}\n")

    tmp_dir = tempfile.mkdtemp(prefix=f"yt_{video_type}_")
    clips_dir = os.path.join(tmp_dir, "clips")
    voices_dir = os.path.join(tmp_dir, "voices")

    # 3. Animate scenes locally (free — no API)
    print(f"[3/6] Animating {len(script['scenes'])} scenes locally (Pillow + FFmpeg)...")
    clip_paths = create_all_scenes(script["scenes"], clips_dir, video_type, slot=slot)
    print()

    # 4. Generate voiceovers (edge-tts, free)
    print("[4/6] Generating voiceovers (edge-tts)...")
    voice_paths = generate_scene_voiceovers(script["scenes"], voices_dir)
    print()

    # 5. Assemble final video
    print("[5/6] Assembling final video...")
    os.makedirs(output_dir, exist_ok=True)
    safe_title = "".join(c for c in script["title"][:50] if c.isalnum() or c in " _-").strip()
    video_path = os.path.join(output_dir, f"{safe_title}.mp4")
    thumbnail_path = os.path.join(output_dir, f"{safe_title}_thumb.jpg")

    assemble_video(clip_paths, voice_paths, video_path, video_type, tmp_dir)
    generate_thumbnail(script.get("thumbnail_text", script["title"]), thumbnail_path, video_type)
    print()

    # 6. Upload to YouTube
    print("[6/6] Uploading to YouTube...")
    video_id = upload_video(
        video_path=video_path,
        thumbnail_path=thumbnail_path,
        title=script["title"],
        description=script["description"],
        tags=script["tags"],
        video_type=video_type,
    )

    save_upload_log(video_id, script["title"], topic, video_type)

    print(f"\n{'='*55}")
    print(f"  DONE! https://youtube.com/watch?v={video_id}")
    print(f"{'='*55}\n")
    return video_id


def main():
    parser = argparse.ArgumentParser(description="YouTube Motivation Channel Automation")
    parser.add_argument("--type", choices=["regular", "shorts", "both"], default="regular")
    args = parser.parse_args()

    if args.type == "both":
        run_pipeline("regular")
        run_pipeline("shorts")
    else:
        run_pipeline(args.type)


if __name__ == "__main__":
    main()
