"""
Agent 3: Daily Analytics (runs every morning)
Fetches channel + video stats from YouTube API → sends daily briefing to Telegram
Shows: subscribers, total views, top videos, YPP progress
"""
import os, sys, pickle
from datetime import datetime
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

TOKEN_FILE = "youtube_token.pickle"
CHANNEL_ID = "UCZSdar2nKSxkxX3b5vgYGIg"  # MindShift Productivity


def _get_youtube():
    with open(TOKEN_FILE, "rb") as f:
        creds = pickle.load(f)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return build("youtube", "v3", credentials=creds)


def _get_channel_stats(youtube) -> dict:
    result = youtube.channels().list(part="statistics", id=CHANNEL_ID).execute()
    if not result["items"]:
        return {}
    s = result["items"][0]["statistics"]
    return {
        "subscribers": int(s.get("subscriberCount", 0)),
        "total_views": int(s.get("viewCount", 0)),
        "video_count": int(s.get("videoCount", 0)),
    }


def _get_recent_videos(youtube, max_results: int = 20) -> list:
    ch = youtube.channels().list(part="contentDetails", id=CHANNEL_ID).execute()
    if not ch["items"]:
        return []
    playlist_id = ch["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

    playlist = youtube.playlistItems().list(
        playlistId=playlist_id, part="snippet", maxResults=max_results
    ).execute()

    video_ids = [item["snippet"]["resourceId"]["videoId"] for item in playlist.get("items", [])]
    if not video_ids:
        return []

    stats = youtube.videos().list(part="statistics,snippet", id=",".join(video_ids)).execute()
    videos = []
    for item in stats.get("items", []):
        s = item["statistics"]
        videos.append({
            "title": item["snippet"]["title"],
            "video_id": item["id"],
            "views": int(s.get("viewCount", 0)),
            "likes": int(s.get("likeCount", 0)),
            "comments": int(s.get("commentCount", 0)),
        })
    return sorted(videos, key=lambda x: x["views"], reverse=True)


def _bar(value, maximum, width=10) -> str:
    pct = min(1.0, value / maximum) if maximum > 0 else 0
    filled = int(pct * width)
    return "█" * filled + "░" * (width - filled) + f" {pct*100:.0f}%"


def main():
    from agents.notifier import send

    print("[Agent 3: Analytics] Fetching channel data...")
    youtube = _get_youtube()
    channel = _get_channel_stats(youtube)
    videos = _get_recent_videos(youtube, max_results=20)

    subs = channel.get("subscribers", 0)
    total_views = channel.get("total_views", 0)
    video_count = channel.get("video_count", 0)

    # Rough watch-hour estimate: avg 3 min watch time per view
    est_watch_hours = (total_views * 3) / 60

    top3 = "\n".join([
        f"  {i+1}. {v['title'][:48]}...\n     └ {v['views']:,} views · {v['likes']:,} likes"
        for i, v in enumerate(videos[:3])
    ]) if videos else "  No videos yet"

    if subs >= 1000 and est_watch_hours >= 4000:
        cta = "YPP THRESHOLD REACHED! Apply in YouTube Studio!"
    elif subs < 50:
        cta = "Share today's video on WhatsApp groups + Reddit to grow faster!"
    else:
        cta = f"{1000 - subs} more subscribers needed — keep sharing!"

    send(f"""📊 <b>Agent 3: Daily Analytics — MindShift Productivity</b>
{datetime.now().strftime('%A, %B %d %Y')}

━━━━━━━━━━━━━━━━━━━━
👥 <b>Subscribers:</b> {subs:,} / 1,000 needed
{_bar(subs, 1000)}

⏱ <b>Watch Hours:</b> {est_watch_hours:,.0f} / 4,000 needed
{_bar(est_watch_hours, 4000)}

👁 <b>Total Views:</b> {total_views:,}
🎬 <b>Videos Uploaded:</b> {video_count}
━━━━━━━━━━━━━━━━━━━━

🏆 <b>Top 3 Videos:</b>
{top3}

{cta}""")


if __name__ == "__main__":
    main()
