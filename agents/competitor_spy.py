"""
Agent 2: Competitor Spy (runs every Monday)
Searches YouTube for top-performing videos in our niche → analyzes title/tag patterns with Groq
→ sends weekly intelligence report to Telegram
"""
import os, sys, pickle
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from groq import Groq

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import GROQ_API_KEY

TOKEN_FILE = "youtube_token.pickle"

QUERIES = [
    "psychology facts motivation",
    "self improvement success mindset",
    "habits of successful people",
    "how to stop procrastinating science",
    "body language tricks confidence",
    "why you are not successful",
    "dark psychology manipulation",
    "morning routine millionaire habits",
]


def _get_youtube():
    with open(TOKEN_FILE, "rb") as f:
        creds = pickle.load(f)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return build("youtube", "v3", credentials=creds)


def _search_top_videos(youtube, query: str) -> list:
    try:
        result = youtube.search().list(
            q=query,
            type="video",
            part="snippet",
            order="viewCount",
            publishedAfter="2024-01-01T00:00:00Z",
            videoDuration="medium",
            maxResults=5,
            relevanceLanguage="en",
        ).execute()
        ids = [item["id"]["videoId"] for item in result.get("items", [])]
        if not ids:
            return []
        stats = youtube.videos().list(part="statistics,snippet", id=",".join(ids)).execute()
        videos = []
        for item in stats.get("items", []):
            s = item["statistics"]
            videos.append({
                "title": item["snippet"]["title"],
                "channel": item["snippet"]["channelTitle"],
                "video_id": item["id"],
                "views": int(s.get("viewCount", 0)),
                "likes": int(s.get("likeCount", 0)),
                "tags": item["snippet"].get("tags", [])[:8],
            })
        return videos
    except Exception as e:
        print(f"  [CompetitorSpy] Search error for '{query}': {e}")
        return []


def _analyze_patterns(videos: list, client: Groq) -> str:
    video_data = "\n".join([
        f"Title: {v['title']} | Views: {v.get('views', 0):,} | Tags: {', '.join(v.get('tags', []))}"
        for v in videos[:12]
    ])
    prompt = f"""Analyze these top-performing YouTube videos in psychology/motivation:

{video_data}

Provide a concise analysis (max 400 words):
1. Top 5 TITLE FORMULAS that work (e.g., "X [Noun] That Will [Benefit]")
2. Power words that appear repeatedly in titles
3. Top 8 tags/keywords to always include
4. 3 content angles we should copy (what psychological trigger each uses)
5. One clear gap in the market we can fill

Format as plain text, be specific and actionable."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=800,
    )
    return response.choices[0].message.content.strip()


def main():
    from agents.notifier import send

    print("[Agent 2: Competitor Spy] Searching YouTube for top competitor videos...")
    youtube = _get_youtube()
    client = Groq(api_key=GROQ_API_KEY)

    all_videos = []
    for q in QUERIES[:5]:
        vids = _search_top_videos(youtube, q)
        all_videos.extend(vids)
        print(f"  '{q}': {len(vids)} videos")

    # Deduplicate + sort by views
    seen = set()
    unique = []
    for v in sorted(all_videos, key=lambda x: x.get("views", 0), reverse=True):
        if v["video_id"] not in seen:
            seen.add(v["video_id"])
            unique.append(v)

    print(f"  {len(unique)} unique competitor videos found")
    print("[Competitor Spy] Analyzing patterns with Groq...")
    analysis = _analyze_patterns(unique, client)

    top3 = "\n".join([
        f"  {i+1}. <b>{v['title'][:58]}</b>\n     └ {v.get('views', 0):,} views — {v['channel']}"
        for i, v in enumerate(unique[:3])
    ])

    send(f"""🕵️ <b>Agent 2: Competitor Spy — Weekly Report</b>

<b>Top 3 Videos in Your Niche This Week:</b>
{top3}

<b>AI Pattern Analysis:</b>
{analysis[:900]}

🎯 Use these patterns in your next scripts!""")


if __name__ == "__main__":
    main()
