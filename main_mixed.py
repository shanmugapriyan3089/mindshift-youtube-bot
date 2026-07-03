"""
Hybrid Pipeline — alternates cartoon (stick figures) + stock footage scenes.
Scene 1: cartoon hook  →  Scene 2: stock  →  Scene 3: cartoon  →  Scene 4: stock …
Last scene always cartoon CTA.

Usage:
  python main_mixed.py --type regular
  python main_mixed.py --type shorts
  python main_mixed.py --type both
"""
import os
import sys
import argparse
import tempfile

sys.path.insert(0, os.path.dirname(__file__))

from config import REGULAR_OUTPUT_DIR, SHORTS_OUTPUT_DIR
from src.script_generator import generate_script, pick_topic
from src.simple_animator import create_scene_video
from src.stock_animator import create_scene_video_stock
from src.voice_generator import generate_scene_voiceovers
from src.video_assembler import assemble_video, generate_thumbnail
from src.youtube_uploader import upload_video, save_upload_log

def _is_cartoon_scene(idx: int, total: int) -> bool:
    """
    Layout:
      - First scene  → cartoon (hook grabs attention)
      - Last scene   → cartoon (CTA with stick figures celebrating)
      - Even indexes → cartoon, Odd indexes → stock footage
    """
    if idx == 0 or idx == total - 1:
        return True
    return idx % 2 == 0


def run_pipeline(video_type: str = "regular"):
    print(f"\n{'='*55}")
    print(f"  HYBRID PIPELINE — {video_type.upper()}")
    print(f"  Style: Cartoon hook + Stock content + Cartoon CTA")
    print(f"{'='*55}\n")

    output_dir = REGULAR_OUTPUT_DIR if video_type == "regular" else SHORTS_OUTPUT_DIR

    # 1. Pick topic — slot 4/5 reserved for mixed pipelines
    slot = int(os.getenv("PIPELINE_SLOT", "4"))
    topic = pick_topic(slot)
    print(f"[1/6] Topic: {topic}\n")

    # 2. Generate script
    print("[2/6] Generating script with Groq (Llama 3.3 70B)...")
    script = generate_script(topic, video_type)
    print(f"      Title: {script['title']}")
    print(f"      Scenes: {len(script['scenes'])}\n")

    tmp_dir = tempfile.mkdtemp(prefix=f"mixed_{video_type}_")
    clips_dir = os.path.join(tmp_dir, "clips")
    voices_dir = os.path.join(tmp_dir, "voices")
    os.makedirs(clips_dir, exist_ok=True)

    scenes = script["scenes"]
    total = len(scenes)

    # 3. Render each scene — cartoon or stock
    print(f"[3/6] Rendering {total} scenes (cartoon + stock mix)...")
    clip_paths = []
    for i, scene in enumerate(scenes):
        out = os.path.join(clips_dir, f"scene_{scene['scene_number']:02d}.mp4")
        use_cartoon = _is_cartoon_scene(i, total)
        label = "cartoon" if use_cartoon else "stock  "
        print(f"  [{label}] Scene {scene['scene_number']}: {scene['text_overlay']}")

        if use_cartoon:
            create_scene_video(
                text=scene["text_overlay"],
                bg_color=scene.get("bg_color", "#F5F8FC"),
                duration=scene["duration_seconds"],
                output_path=out,
                video_type=video_type,
                scene_idx=i,
                narration=scene.get("narration", ""),
                slot=slot,
            )
        else:
            keyword = scene.get("keyword", scene.get("text_overlay", "motivation success"))
            create_scene_video_stock(
                caption=scene["text_overlay"],
                keyword=keyword,
                duration=scene["duration_seconds"],
                output_path=out,
                video_type=video_type,
            )
        clip_paths.append(out)
    print()

    # 4. Generate voiceovers
    print("[4/6] Generating voiceovers (edge-tts Jenny Neural)...")
    voice_paths = generate_scene_voiceovers(scenes, voices_dir)
    print()

    # 5. Assemble
    print("[5/6] Assembling final video...")
    os.makedirs(output_dir, exist_ok=True)
    safe_title = "".join(
        c for c in script["title"][:50] if c.isalnum() or c in " _-"
    ).strip()
    video_path = os.path.join(output_dir, f"mixed_{safe_title}.mp4")
    thumbnail_path = os.path.join(output_dir, f"mixed_{safe_title}_thumb.jpg")

    assemble_video(clip_paths, voice_paths, video_path, video_type, tmp_dir,
                   scenes=scenes if video_type == "regular" else None)
    generate_thumbnail(
        script.get("thumbnail_text", script["title"]), thumbnail_path, video_type
    )
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

    save_upload_log(video_id, script["title"], topic, f"mixed_{video_type}")

    print(f"\n{'='*55}")
    print(f"  DONE! https://youtube.com/watch?v={video_id}")
    print(f"{'='*55}\n")
    return video_id


def main():
    parser = argparse.ArgumentParser(description="Hybrid YouTube Automation")
    parser.add_argument(
        "--type", choices=["regular", "shorts", "both"], default="regular"
    )
    args = parser.parse_args()

    if args.type == "both":
        run_pipeline("regular")
        run_pipeline("shorts")
    else:
        run_pipeline(args.type)


if __name__ == "__main__":
    main()
