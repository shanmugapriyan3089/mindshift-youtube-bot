"""
Agent 7: SEO Optimizer (runs daily after uploads)
Fetches recent channel videos → Groq generates + picks best title, tags
→ AUTO-APPLIES title + tags to YouTube videos via API
→ sends a brief "applied" summary email (no action needed from you)
"""
import os, sys, pickle, json, re
from groq import Groq
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import GROQ_API_KEY

TOKEN_FILE = "youtube_token.pickle"
CHANNEL_ID = "UCZSdar2nKSxkxX3b5vgYGIg"


def _get_youtube():
    with open(TOKEN_FILE, "rb") as f:
        creds = pickle.load(f)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return build("youtube", "v3", credentials=creds)


def _get_recent_videos(youtube, max_results: int = 5) -> list:
    ch = youtube.channels().list(part="contentDetails", id=CHANNEL_ID).execute()
    if not ch["items"]:
        return []
    playlist_id = ch["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    playlist = youtube.playlistItems().list(
        playlistId=playlist_id, part="snippet", maxResults=max_results
    ).execute()
    ids = [item["snippet"]["resourceId"]["videoId"] for item in playlist.get("items", [])]
    if not ids:
        return []
    result = youtube.videos().list(part="snippet,statistics", id=",".join(ids)).execute()
    videos = []
    for item in result.get("items", []):
        s = item["statistics"]
        sn = item["snippet"]
        videos.append({
            "video_id": item["id"],
            "title": sn["title"],
            "description": sn.get("description", ""),
            "tags": sn.get("tags", []),
            "category_id": sn.get("categoryId", "22"),
            "views": int(s.get("viewCount", 0)),
            "likes": int(s.get("likeCount", 0)),
        })
    return sorted(videos, key=lambda x: x["views"])  # lowest views first


def _generate_seo(client: Groq, title: str, views: int) -> dict:
    prompt = f"""You are a YouTube SEO expert for a psychology/motivation channel.

Current video title: "{title}"
Current views: {views:,}

Generate SEO improvements. Respond ONLY with JSON, no markdown:
{{
  "alt_titles": [
    "Title option 1 — 45-70 chars, punchy, clickbait-style",
    "Title option 2 — 45-70 chars, different angle",
    "Title option 3 — 45-70 chars, different angle"
  ],
  "tags": ["tag1","tag2","tag3","tag4","tag5","tag6","tag7","tag8","tag9","tag10","tag11","tag12"],
  "thumbnail_text": "4-6 WORDS ALL CAPS"
}}

Examples of great titles:
"7 Psychology Tricks That Make People Like You Instantly"
"Why 99% of People Stay Broke (The Uncomfortable Truth)"
"Stop Doing This If You Want to Be Confident"
"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=500,
    )
    text = response.choices[0].message.content
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except Exception:
            pass
    return {}


def _pick_best_title(client: Groq, titles: list, current_title: str) -> str:
    """Ask Groq to score the 3 titles and return the best one."""
    numbered = "\n".join(f"{i+1}. {t}" for i, t in enumerate(titles))
    prompt = f"""You are a YouTube CTR expert. A psychology/motivation channel needs to pick the best title.

Current title: "{current_title}"

Three options:
{numbered}

Which title will get the MOST clicks? Consider: curiosity gap, power words, specificity, emotional trigger, length.
Respond with ONLY the number: 1, 2, or 3."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=10,
    )
    text = response.choices[0].message.content.strip()
    match = re.search(r'[123]', text)
    idx = int(match.group()) - 1 if match else 0
    return titles[idx]


def _apply_seo(youtube, video_id: str, new_title: str, new_tags: list) -> bool:
    """Auto-apply title + tags to a YouTube video."""
    try:
        result = youtube.videos().list(part="snippet", id=video_id).execute()
        if not result["items"]:
            return False
        snippet = result["items"][0]["snippet"]
        snippet["title"] = new_title
        snippet["tags"] = new_tags
        youtube.videos().update(
            part="snippet",
            body={"id": video_id, "snippet": snippet}
        ).execute()
        print(f"  ✓ Applied: {new_title[:60]}")
        return True
    except Exception as e:
        print(f"  ✗ Failed ({video_id}): {e}")
        return False


def main():
    from agents.notifier import send

    client = Groq(api_key=GROQ_API_KEY)
    print("[Agent 7: SEO Optimizer] Fetching recent videos...")
    youtube = _get_youtube()
    videos = _get_recent_videos(youtube, max_results=5)

    if not videos:
        send("📭 <b>SEO Optimizer</b>: No videos found to optimize")
        return

    print(f"  {len(videos)} videos found. Generating + applying SEO improvements...")

    applied_lines = []
    skipped = []

    for video in videos[:3]:
        seo = _generate_seo(client, video["title"], video["views"])
        if not seo:
            skipped.append(video["title"][:50])
            continue

        alt_titles = seo.get("alt_titles", [])
        new_tags = seo.get("tags", [])

        # Pick best title automatically
        best_title = _pick_best_title(client, alt_titles, video["title"]) if alt_titles else video["title"]

        ok = _apply_seo(youtube, video["video_id"], best_title, new_tags)

        status = "✅ Applied" if ok else "⚠️ Failed (no write scope — update manually)"
        applied_lines.append(
            f"{status}\n"
            f"  Was: <i>{video['title'][:60]}</i>\n"
            f"  Now: <b>{best_title[:60]}</b>\n"
            f"  Tags: {len(new_tags)} applied · {video['views']:,} views\n"
            f"  🖼 Thumbnail: {seo.get('thumbnail_text', '')}"
        )

    applied_count = sum(1 for l in applied_lines if l.startswith("✅"))
    failed_count  = len(applied_lines) - applied_count

    from agents.notifier import write_agent_report
    write_agent_report("seo_optimizer", {
        "status":            "ok" if not failed_count else "partial",
        "videos_found":      len(videos),
        "seo_applied":       applied_count,
        "seo_failed":        failed_count,
        "skipped":           len(skipped),
        "summary":           f"{applied_count}/{len(videos[:3])} SEO updates applied, {len(skipped)} skipped",
        "errors":            [f"SEO failed for: {t}" for t in skipped],
    })

    updates = "\n\n━━━━━━━━━━━━━━━━━━\n".join(applied_lines)
    send(
        f"🔍 <b>Agent 7: SEO Auto-Applied</b>\n\n{updates}\n\n"
        f"🤖 No action needed — everything was applied automatically.",
        subject="Agent 7: SEO Applied Automatically"
    )


if __name__ == "__main__":
    main()
