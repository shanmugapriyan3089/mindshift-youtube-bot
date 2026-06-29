"""
Agent 10: Instagram Reels Auto-Poster
Downloads latest Shorts from YouTube → posts to Instagram Reels via Graph API.

Setup (one-time):
1. Go to developers.facebook.com → Create App → type: Business
2. Add "Instagram Graph API" product
3. Connect your Instagram Creator/Business account to a Facebook Page
4. Get a long-lived access token (valid 60 days):
   - Short-lived token: GET https://graph.facebook.com/oauth/authorize (from Meta's Token Debugger)
   - Exchange: GET https://graph.facebook.com/oauth/access_token
     ?grant_type=fb_exchange_token&client_id=APP_ID&client_secret=APP_SECRET&fb_exchange_token=SHORT_TOKEN
5. Get your Instagram Account ID:
   - GET https://graph.facebook.com/me/accounts?access_token=TOKEN
   - Then GET https://graph.facebook.com/{page_id}?fields=instagram_business_account&access_token=TOKEN
6. Add to GitHub Secrets:
   INSTAGRAM_ACCOUNT_ID  — numeric ID (e.g. 17841400123456789)
   INSTAGRAM_ACCESS_TOKEN — long-lived token (refresh every 50 days)

Token refresh (add to a monthly cron):
  GET https://graph.facebook.com/oauth/access_token
  ?grant_type=fb_exchange_token&client_id=APP_ID&client_secret=APP_SECRET&fb_exchange_token=CURRENT_TOKEN
"""
import os, sys, json, time, subprocess, tempfile, re
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

CHANNEL_HANDLE = "@MindShiftProductivity"
IG_LOG         = "instagram_log.json"
GRAPH_BASE     = "https://graph.facebook.com/v21.0"


# ── Helpers ───────────────────────────────────────────────────────────────────

def _load_posted() -> set:
    if not os.path.exists(IG_LOG):
        return set()
    try:
        with open(IG_LOG) as f:
            return set(json.load(f))
    except Exception:
        return set()


def _save_posted(posted: set):
    with open(IG_LOG, "w") as f:
        json.dump(list(posted), f)


def _get_unposted_shorts() -> list:
    if not os.path.exists("upload_log.json"):
        return []
    try:
        with open("upload_log.json") as f:
            log = json.load(f)
    except Exception:
        return []
    posted = _load_posted()
    return [v for v in log if v.get("type") == "shorts" and v.get("video_id") not in posted]


def _download_short(video_url: str, out_dir: str) -> str | None:
    """Download YouTube Short using yt-dlp. Returns local file path."""
    out_path = os.path.join(out_dir, "short.mp4")
    try:
        result = subprocess.run(
            [
                "yt-dlp",
                "-f", "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
                "--merge-output-format", "mp4",
                "--no-playlist",
                "-o", out_path,
                video_url,
            ],
            capture_output=True, text=True, timeout=120,
        )
        if result.returncode == 0 and os.path.exists(out_path) and os.path.getsize(out_path) > 10_000:
            print(f"  [Instagram] Downloaded: {os.path.getsize(out_path) // 1024} KB")
            return out_path
        print(f"  [Instagram] yt-dlp failed: {result.stderr[-200:]}")
    except FileNotFoundError:
        print("  [Instagram] yt-dlp not installed. Run: pip install yt-dlp")
    except Exception as e:
        print(f"  [Instagram] Download error: {e}")
    return None


def _upload_to_catbox(video_path: str) -> str | None:
    """Upload video to catbox.moe → returns permanent public URL."""
    print("  [Instagram] Uploading to catbox.moe for public URL...")
    try:
        with open(video_path, "rb") as f:
            resp = requests.post(
                "https://catbox.moe/user.php",
                data={"reqtype": "fileupload"},
                files={"fileToUpload": ("short.mp4", f, "video/mp4")},
                timeout=180,
            )
        url = resp.text.strip()
        if url.startswith("https://files.catbox.moe/"):
            print(f"  [Instagram] Public URL: {url}")
            return url
        print(f"  [Instagram] catbox.moe error: {resp.text[:200]}")
    except Exception as e:
        print(f"  [Instagram] catbox.moe upload failed: {e}")
    return None


def _build_caption(title: str, poll_question: str = "") -> str:
    clean = title.replace(" #Shorts", "").replace("#Shorts", "").strip()
    lines = [clean, ""]
    if poll_question and " A: " in poll_question:
        lines += [f"🗳️ {poll_question}", "Comment A or B below 👇", ""]
    lines += [
        "Follow for daily psychology drops 🧠",
        "",
        "#psychology #mindset #selfimprovement #motivation #mentalhealth",
        "#selfhelp #personaldevelopment #success #habits #productivity",
        "#mindshiftproductivity",
    ]
    return "\n".join(lines)[:2200]


def _create_ig_container(ig_account_id: str, access_token: str,
                          video_url: str, caption: str) -> str | None:
    """Step 1: Create an Instagram media container for a Reel."""
    resp = requests.post(
        f"{GRAPH_BASE}/{ig_account_id}/media",
        data={
            "video_url":      video_url,
            "media_type":     "REELS",
            "caption":        caption,
            "share_to_feed":  "true",
            "access_token":   access_token,
        },
        timeout=60,
    )
    data = resp.json()
    if "id" in data:
        print(f"  [Instagram] Container created: {data['id']}")
        return data["id"]
    print(f"  [Instagram] Container creation failed: {data}")
    return None


def _wait_for_container(container_id: str, access_token: str, timeout: int = 300) -> bool:
    """Step 2: Wait until Instagram finishes processing the video."""
    print("  [Instagram] Waiting for video processing...")
    deadline = time.time() + timeout
    while time.time() < deadline:
        resp = requests.get(
            f"{GRAPH_BASE}/{container_id}",
            params={"fields": "status_code,status", "access_token": access_token},
            timeout=30,
        )
        data = resp.json()
        status = data.get("status_code", "")
        print(f"  [Instagram] Status: {status}")
        if status == "FINISHED":
            return True
        if status == "ERROR":
            print(f"  [Instagram] Processing error: {data}")
            return False
        time.sleep(15)
    print("  [Instagram] Timed out waiting for processing")
    return False


def _publish_container(ig_account_id: str, access_token: str, container_id: str) -> str | None:
    """Step 3: Publish the container as a live Reel."""
    resp = requests.post(
        f"{GRAPH_BASE}/{ig_account_id}/media_publish",
        data={"creation_id": container_id, "access_token": access_token},
        timeout=60,
    )
    data = resp.json()
    if "id" in data:
        media_id = data["id"]
        print(f"  [Instagram] Published Reel: {media_id}")
        return media_id
    print(f"  [Instagram] Publish failed: {data}")
    return None


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    from agents.notifier import send

    ig_account_id = os.getenv("INSTAGRAM_ACCOUNT_ID")
    access_token  = os.getenv("INSTAGRAM_ACCESS_TOKEN")

    if not ig_account_id or not access_token:
        print("[Agent 10: Instagram] Credentials not set — skipping")
        print("[Instagram] Add INSTAGRAM_ACCOUNT_ID + INSTAGRAM_ACCESS_TOKEN to GitHub Secrets")
        print("[Instagram] See setup instructions at top of this file")
        return

    unposted = _get_unposted_shorts()
    if not unposted:
        print("[Instagram] No new Shorts to post — all caught up")
        return

    print(f"[Agent 10: Instagram] {len(unposted)} Short(s) to post")

    posted = _load_posted()

    for upload in unposted[:2]:   # max 2 per run to respect rate limits
        video_id  = upload.get("video_id", "")
        title     = upload.get("title", "")
        video_url = upload.get("url", f"https://youtube.com/watch?v={video_id}")
        poll_q    = upload.get("poll_question", "")

        print(f"\n  Processing: {title[:60]}")

        with tempfile.TemporaryDirectory(prefix="ig_short_") as tmp:
            # 1. Download from YouTube
            local_path = _download_short(video_url, tmp)
            if not local_path:
                print(f"  [Instagram] Skipping {video_id} — download failed")
                continue

            # 2. Upload to catbox.moe for public URL
            public_url = _upload_to_catbox(local_path)
            if not public_url:
                print(f"  [Instagram] Skipping {video_id} — hosting upload failed")
                continue

        # 3. Build caption
        caption = _build_caption(title, poll_q)

        # 4. Create IG container
        container_id = _create_ig_container(ig_account_id, access_token, public_url, caption)
        if not container_id:
            continue

        # 5. Wait for processing
        ready = _wait_for_container(container_id, access_token)
        if not ready:
            continue

        # 6. Publish
        media_id = _publish_container(ig_account_id, access_token, container_id)
        if not media_id:
            continue

        # 7. Mark as posted
        posted.add(video_id)
        _save_posted(posted)

        ig_url = f"https://www.instagram.com/reel/{media_id}/"
        send(
            f"Instagram Reel Posted!\n\n"
            f"{title[:80]}\n\n"
            f"View: {ig_url}\n"
            f"Poll: {poll_q[:80] if poll_q else 'none'}",
            subject=f"Instagram Reel: {title[:50]}"
        )
        print(f"  [Instagram] Done: {ig_url}")

    print("\n[Instagram] Run complete")


if __name__ == "__main__":
    main()
