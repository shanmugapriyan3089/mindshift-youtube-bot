"""
Agent 7: SEO Optimizer (runs daily after uploads)
Fetches recent channel videos → Groq generates better titles, tags, descriptions
→ sends recommendations to Telegram for manual update in YouTube Studio
"""
import os, sys, pickle, json
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
        videos.append({
            "video_id": item["id"],
            "title": item["snippet"]["title"],
            "description": item["snippet"].get("description", "")[:300],
            "tags": item["snippet"].get("tags", []),
            "views": int(s.get("viewCount", 0)),
            "likes": int(s.get("likeCount", 0)),
        })
    return sorted(videos, key=lambda x: x["views"])  # lowest views first (need most help)


def _optimize(client: Groq, title: str, views: int) -> dict:
    prompt = f"""YouTube SEO expert for psychology/motivation channel.

Current video title: "{title}"
Current views: {views:,}

Generate SEO improvements:
1. Three alternative titles (more clickable, better SEO, keep under 70 chars)
2. 12 optimized tags (mix broad + specific, all lowercase)
3. First 160 characters of improved description (open with strongest keyword)
4. One thumbnail text idea (4-6 words, ALL CAPS)

Respond ONLY with JSON:
{{
  "alt_titles": ["title1", "title2", "title3"],
  "tags": ["tag1", "tag2", ...],
  "description_start": "Optimized first 160 chars...",
  "thumbnail_text": "THUMBNAIL TEXT"
}}"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=600,
    )
    import re
    text = response.choices[0].message.content
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except Exception:
            pass
    return {}


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
    message = "🔍 <b>Agent 7: SEO Optimization Report</b>\n(Apply in YouTube Studio → Content → Edit video)\n"

    for video in videos[:3]:
        seo = _optimize(client, video["title"], video["views"])
        if not seo:
            continue

        alts = "\n".join(f"  {i+1}. {t}" for i, t in enumerate(seo.get("alt_titles", [])))
        tags = ", ".join(seo.get("tags", [])[:10])

        message += f"""
━━━━━━━━━━━━━━━━━━
🎬 <b>{video['title'][:55]}</b>
👁 {video['views']:,} views · youtube.com/watch?v={video['video_id']}

📝 <b>Better titles:</b>
{alts}

🏷 <b>Add tags:</b> {tags}

📄 <b>Start description with:</b>
{seo.get('description_start', '')[:160]}

🖼 <b>Thumbnail text:</b> {seo.get('thumbnail_text', '')}
"""

    message += "\n\n⚙️ <b>To update:</b> YouTube Studio → Content → click video → Details → Edit"
    send(message)


if __name__ == "__main__":
    main()
