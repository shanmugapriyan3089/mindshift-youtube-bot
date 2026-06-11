"""
Video generation with automatic fallback chain:
  Kling AI → Hailuo AI → Runway ML → Pika Labs → placeholder image
"""
import os
import time
import jwt
import requests
from config import (
    KLING_ACCESS_KEY, KLING_SECRET_KEY,
    HAILUO_API_KEY, HAILUO_GROUP_ID,
    RUNWAY_API_KEY, PIKA_API_KEY,
)

KLING_BASE = "https://api.klingai.com"
HAILUO_BASE = "https://api.minimaxi.chat/v1"
RUNWAY_BASE = "https://api.dev.runwayml.com/v1"


# ── Kling AI ─────────────────────────────────────────────────────────────────

def _kling_jwt() -> str:
    payload = {
        "iss": KLING_ACCESS_KEY,
        "exp": int(time.time()) + 1800,
        "nbf": int(time.time()) - 5,
    }
    return jwt.encode(payload, KLING_SECRET_KEY, algorithm="HS256")


def generate_with_kling(prompt: str, duration: int = 5, output_path: str = None) -> str | None:
    if not KLING_ACCESS_KEY or not KLING_SECRET_KEY:
        return None
    try:
        headers = {"Authorization": f"Bearer {_kling_jwt()}", "Content-Type": "application/json"}
        body = {
            "model": "kling-v1",
            "prompt": prompt,
            "negative_prompt": "blurry, ugly, deformed, scary, violent, adult content",
            "cfg_scale": 0.5,
            "mode": "std",
            "duration": duration,
            "aspect_ratio": "16:9",
        }
        r = requests.post(f"{KLING_BASE}/v1/videos/text2video", json=body, headers=headers, timeout=30)
        r.raise_for_status()
        task_id = r.json()["data"]["task_id"]

        # Poll for completion (max 3 min)
        for _ in range(36):
            time.sleep(5)
            poll = requests.get(
                f"{KLING_BASE}/v1/videos/text2video/{task_id}",
                headers=headers, timeout=15
            )
            poll.raise_for_status()
            data = poll.json()["data"]
            if data["task_status"] == "succeed":
                video_url = data["task_result"]["videos"][0]["url"]
                return _download_video(video_url, output_path)
            if data["task_status"] == "failed":
                print(f"[Kling] Task failed: {data.get('task_status_msg')}")
                return None
    except Exception as e:
        print(f"[Kling] Error: {e}")
    return None


# ── Hailuo AI (MiniMax) ───────────────────────────────────────────────────────

def generate_with_hailuo(prompt: str, output_path: str = None) -> str | None:
    if not HAILUO_API_KEY or not HAILUO_GROUP_ID:
        return None
    try:
        headers = {
            "Authorization": f"Bearer {HAILUO_API_KEY}",
            "Content-Type": "application/json",
        }
        body = {
            "model": "video-01",
            "prompt": prompt,
            "prompt_optimizer": True,
        }
        r = requests.post(
            f"{HAILUO_BASE}/video_generation?GroupId={HAILUO_GROUP_ID}",
            json=body, headers=headers, timeout=30
        )
        r.raise_for_status()
        task_id = r.json()["task_id"]

        for _ in range(60):
            time.sleep(5)
            poll = requests.get(
                f"{HAILUO_BASE}/query/video_generation?task_id={task_id}&GroupId={HAILUO_GROUP_ID}",
                headers=headers, timeout=15
            )
            poll.raise_for_status()
            data = poll.json()
            if data["status"] == "Success":
                return _download_video(data["file_id"], output_path)
            if data["status"] == "Fail":
                print(f"[Hailuo] Task failed")
                return None
    except Exception as e:
        print(f"[Hailuo] Error: {e}")
    return None


# ── Runway ML ─────────────────────────────────────────────────────────────────

def generate_with_runway(prompt: str, output_path: str = None) -> str | None:
    if not RUNWAY_API_KEY:
        return None
    try:
        headers = {
            "Authorization": f"Bearer {RUNWAY_API_KEY}",
            "Content-Type": "application/json",
            "X-Runway-Version": "2024-11-06",
        }
        body = {
            "promptText": prompt,
            "model": "gen3a_turbo",
            "duration": 5,
            "ratio": "1280:768",
        }
        r = requests.post(f"{RUNWAY_BASE}/image_to_video", json=body, headers=headers, timeout=30)
        r.raise_for_status()
        task_id = r.json()["id"]

        for _ in range(60):
            time.sleep(5)
            poll = requests.get(f"{RUNWAY_BASE}/tasks/{task_id}", headers=headers, timeout=15)
            poll.raise_for_status()
            data = poll.json()
            if data["status"] == "SUCCEEDED":
                return _download_video(data["output"][0], output_path)
            if data["status"] == "FAILED":
                print(f"[Runway] Task failed")
                return None
    except Exception as e:
        print(f"[Runway] Error: {e}")
    return None


# ── Placeholder fallback ──────────────────────────────────────────────────────

def _create_placeholder(output_path: str, duration: int = 5) -> str:
    """Create a solid-color placeholder video using FFmpeg when all APIs fail."""
    import subprocess
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    subprocess.run([
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", f"color=c=0xFFD6E0:size=1920x1080:duration={duration}:rate=24",
        "-vf", f"drawtext=text='Scene Loading...':fontsize=60:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2",
        output_path
    ], check=True, capture_output=True)
    return output_path


# ── Main entry point ──────────────────────────────────────────────────────────

def generate_scene_video(prompt: str, scene_num: int, output_dir: str, duration: int = 5) -> str:
    """Try each provider in order, return path to downloaded .mp4"""
    output_path = os.path.join(output_dir, f"scene_{scene_num:02d}.mp4")
    os.makedirs(output_dir, exist_ok=True)

    providers = [
        ("Kling AI",  lambda: generate_with_kling(prompt, duration, output_path)),
        ("Hailuo AI", lambda: generate_with_hailuo(prompt, output_path)),
        ("Runway ML", lambda: generate_with_runway(prompt, output_path)),
    ]

    for name, fn in providers:
        print(f"  [Scene {scene_num}] Trying {name}...")
        result = fn()
        if result:
            print(f"  [Scene {scene_num}] Done via {name}")
            return result

    print(f"  [Scene {scene_num}] All APIs failed — using placeholder")
    return _create_placeholder(output_path, duration)


def _download_video(url: str, output_path: str) -> str:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    r = requests.get(url, stream=True, timeout=120)
    r.raise_for_status()
    with open(output_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
    return output_path
