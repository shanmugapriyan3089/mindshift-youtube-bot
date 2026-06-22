"""
Agent 7: SEO Optimizer (runs daily after uploads)
Fetches recent channel videos → Groq generates better titles, tags, descriptions
→ AUTO-APPLIES tags to YouTube videos via API
→ emails only the title options for you to pick (the only part needing your decision)
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


def _optimize(client: Groq, title: str, views: int) -> dict:
    prompt = f"""You are a YouTube SEO expert for a psychology/motivation channel.

Current video title: "{title}"
Current views: {views:,}

Generate SEO improvements:
1. Three alternative titles — each must be 45-70 characters, punchy, clickbait-style like:
   "7 Psychology Tricks That Make People Like You Instantly"
   "Why 99% of People Stay Broke (The Uncomfortable Truth)"
   "Stop Doing This If You Want to Be Confident"
2. 12 optimized tags (mix broad + specific, all lowercase)
3. One thumbnail text idea (4-6 words, ALL CAPS)

Respond ONLY with JSON, no markdown:
{{
  "alt_titles": ["Full title 1 between 45-70 chars", "Full title 2", "Full title 3"],
  "tags": ["tag1", "tag2", "tag3", "tag4", "tag5", "tag6", "tag7", "tag8", "tag9", "tag10", "tag11", "tag12"],
  "thumbnail_text": "THUMBNAIL TEXT"
}}"""

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


def _apply_tags(youtube, video: dict, new_tags: list) -> bool:
    """Auto-apply optimized tags to a YouTube video — fetches current snippet to avoid overwriting."""
    try:
        result = youtube.videos().list(part="snippet", id=video["video_id"]).execute()
        if not result["items"]:
            return False
        snippet = result["items"][0]["snippet"]
        snippet["tags"] = new_tags
        youtube.videos().update(
            part="snippet",
            body={"id": video["video_id"], "snippet": snippet}
        ).execute()
        print(f"  ✓ Tags applied: {video['title'][:50]}")
        return True
    except Exception as e:
        print(f"  ✗ Tag update failed ({video['video_id']}): {e}")
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

    print(f"  {len(videos)} videos found. Generating SEO improvements...")

    applied = 0
    message = "🔍 <b>Agent 7: SEO — Title Options</b>\n(Tags + SEO applied automatically. Just pick a title for each video if you want to update it)\n"

    for video in videos[:3]:
        seo = _optimize(client, video["title"], video["views"])
        if not seo:
            continue

        # Auto-apply tags silently
        new_tags = seo.get("tags", [])
        if new_tags:
            ok = _apply_tags(youtube, video, new_tags)
            if ok:
                applied += 1

        # Email only the title choices
        alts = "\n".join(f"  {i+1}. {t}" for i, t in enumerate(seo.get("alt_titles", [])))
        message += f"""
━━━━━━━━━━━━━━━━━━
🎬 <b>{video['title'][:55]}</b>
👁 {video['views']:,} views · youtube.com/watch?v={video['video_id']}

📝 <b>Pick a title (update in YouTube Studio):</b>
{alts}

🖼 <b>Thumbnail text:</b> {seo.get('thumbnail_text', '')}
🏷 Tags: ✅ Auto-applied ({len(new_tags)} tags)
"""

    message += f"\n\n✅ <b>{applied}/3 videos had tags auto-applied.</b>"
    message += "\n⚙️ To update title: YouTube Studio → Content → click video → Details"
    send(message, subject="Agent 7: Pick a Title (Tags Already Applied)")


if __name__ == "__main__":
    main()
