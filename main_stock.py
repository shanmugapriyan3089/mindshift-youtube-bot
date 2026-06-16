"""
Stock Footage Pipeline — Pexels video + bold captions.
Style: Alux.com / top faceless motivational channels ($5K-20K/month).

Usage:
  python main_stock.py --type regular   # 8-10 min with stock footage
  python main_stock.py --type shorts    # 58 sec with stock footage
  python main_stock.py --type both
"""
import os
import sys
import argparse
import tempfile

sys.path.insert(0, os.path.dirname(__file__))

from config import REGULAR_OUTPUT_DIR, SHORTS_OUTPUT_DIR
from src.script_generator import generate_script, pick_topic
from src.stock_animator import create_all_scenes_stock
from src.voice_generator import generate_scene_voiceovers
from src.video_assembler import assemble_video, generate_thumbnail
from src.youtube_uploader import upload_video, save_upload_log


def run_pipeline(video_type: str = "regular"):
    print(f"\n{'='*55}")
    print(f"  STOCK FOOTAGE PIPELINE — {video_type.upper()}")
    print(f"  Style: Pexels footage + bold captions ($10-14 RPM)")
    print(f"{'='*55}\n")

    output_dir = REGULAR_OUTPUT_DIR if video_type == "regular" else SHORTS_OUTPUT_DIR

    # 1. Pick topic — slot 2/3 reserved for stock pipelines
    slot = int(os.getenv("PIPELINE_SLOT", "2"))
    topic = pick_topic(slot)
    print(f"[1/6] Topic: {topic}\n")

    # 2. Generate script
    print("[2/6] Generating script with Groq (Llama 3.3 70B)...")
    script = generate_script(topic, video_type)
    print(f"      Title: {script['title']}")
    print(f"      Scenes: {len(script['scenes'])}\n")

    tmp_dir = tempfile.mkdtemp(prefix=f"stock_{video_type}_")
    clips_dir = os.path.join(tmp_dir, "clips")
    voices_dir = os.path.join(tmp_dir, "voices")

    # 3. Fetch stock footage + overlay captions
    print(f"[3/6] Fetching Pexels stock footage for {len(script['scenes'])} scenes...")
    clip_paths = create_all_scenes_stock(script["scenes"], clips_dir, video_type)
    print()

    # 4. Generate voiceovers
    print("[4/6] Generating voiceovers (edge-tts)...")
    voice_paths = generate_scene_voiceovers(script["scenes"], voices_dir)
    print()

    # 5. Assemble
    print("[5/6] Assembling final video...")
    os.makedirs(output_dir, exist_ok=True)
    safe_title = "".join(c for c in script["title"][:50] if c.isalnum() or c in " _-").strip()
    video_path = os.path.join(output_dir, f"stock_{safe_title}.mp4")
    thumbnail_path = os.path.join(output_dir, f"stock_{safe_title}_thumb.jpg")

    assemble_video(clip_paths, voice_paths, video_path, video_type, tmp_dir)
    generate_thumbnail(script.get("thumbnail_text", script["title"]), thumbnail_path, video_type)
    print()

    # 6. Upload
    print("[6/6] Uploading to YouTube...")
    video_id = upload_video(
        video_path=video_path,
        thumbnail_path=thumbnail_path,
        title=script["title"],
        description=script["description"],
        tags=script["tags"],
        video_type=video_type,
    )

    save_upload_log(video_id, script["title"], topic, f"stock_{video_type}")

    print(f"\n{'='*55}")
    print(f"  DONE! https://youtube.com/watch?v={video_id}")
    print(f"{'='*55}\n")
    return video_id


def main():
    parser = argparse.ArgumentParser(description="Stock Footage YouTube Automation")
    parser.add_argument("--type", choices=["regular", "shorts", "both"], default="regular")
    args = parser.parse_args()

    if args.type == "both":
        run_pipeline("regular")
        run_pipeline("shorts")
    else:
        run_pipeline(args.type)


if __name__ == "__main__":
    main()
