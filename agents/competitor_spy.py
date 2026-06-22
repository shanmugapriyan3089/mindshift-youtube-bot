"""
Agent 2: Competitor Spy (runs every Monday)
Searches YouTube for top-performing videos in our niche → analyzes title/tag patterns with Groq
→ auto-updates WINNING_TAGS + TITLE_FORMULAS in config.py → sends summary email
"""
import os, sys, re, json, pickle
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


def _analyze_patterns(videos: list, client: Groq) -> dict:
    video_data = "\n".join([
        f"Title: {v['title']} | Views: {v.get('views', 0):,} | Tags: {', '.join(v.get('tags', []))}"
        for v in videos[:12]
    ])
    prompt = f"""Analyze these top-performing YouTube videos in psychology/motivation niche:

{video_data}

Extract the patterns and respond ONLY with JSON, no markdown:
{{
  "title_formulas": [
    "5 exact reusable title templates (use X as placeholder for numbers, [Topic]/[Result]/[Benefit] as placeholders)"
  ],
  "power_words": ["8 words that appear repeatedly in high-view titles"],
  "tags": ["12 optimized tags, all lowercase, most important first"],
  "content_angles": ["3 psychological triggers used (e.g. fear, curiosity, social proof)"],
  "market_gap": "One specific underserved topic in this niche right now"
}}

Analyze the actual video data above — be specific and data-driven."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=900,
    )
    text = response.choices[0].message.content
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except Exception:
            pass
    return {}


def _update_config_patterns(tags: list, title_formulas: list):
    """Auto-update WINNING_TAGS and TITLE_FORMULAS in config.py."""
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.py")
    with open(config_path, "r") as f:
        content = f.read()

    tags_repr = "[\n" + "".join(f'    "{t}",\n' for t in tags[:12]) + "]"
    content = re.sub(
        r'WINNING_TAGS\s*=\s*\[.*?\]',
        f'WINNING_TAGS = {tags_repr}',
        content, flags=re.DOTALL
    )

    formulas_repr = "[\n" + "".join(f'    "{f}",\n' for f in title_formulas[:5]) + "]"
    content = re.sub(
        r'TITLE_FORMULAS\s*=\s*\[.*?\]',
        f'TITLE_FORMULAS = {formulas_repr}',
        content, flags=re.DOTALL
    )

    with open(config_path, "w") as f:
        f.write(content)
    print(f"  config.py updated: {len(tags[:12])} tags, {len(title_formulas[:5])} formulas")


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

    seen = set()
    unique = []
    for v in sorted(all_videos, key=lambda x: x.get("views", 0), reverse=True):
        if v["video_id"] not in seen:
            seen.add(v["video_id"])
            unique.append(v)

    print(f"  {len(unique)} unique competitor videos found. Analyzing patterns...")
    analysis = _analyze_patterns(unique, client)

    # Auto-update config.py with winning patterns
    tags = analysis.get("tags", [])
    formulas = analysis.get("title_formulas", [])
    if tags and formulas:
        _update_config_patterns(tags, formulas)
        config_status = f"✅ Auto-updated config.py with {len(tags)} tags + {len(formulas)} title formulas"
    else:
        config_status = "⚠️ Could not parse patterns — config.py unchanged"

    top3 = "\n".join([
        f"  {i+1}. <b>{v['title'][:58]}</b>\n     └ {v.get('views', 0):,} views — {v['channel']}"
        for i, v in enumerate(unique[:3])
    ])

    power_words = ", ".join(analysis.get("power_words", []))
    angles = "\n".join(f"  • {a}" for a in analysis.get("content_angles", []))
    gap = analysis.get("market_gap", "N/A")
    formula_list = "\n".join(f"  {i+1}. {f}" for i, f in enumerate(formulas))
    tag_list = ", ".join(tags)

    send(f"""🕵️ <b>Agent 2: Competitor Spy — Weekly Report</b>

<b>Top 3 Videos in Your Niche This Week:</b>
{top3}

━━━ 📝 TITLE FORMULAS (auto-saved) ━━━
{formula_list}

━━━ ⚡ POWER WORDS ━━━
{power_words}

━━━ 🏷 WINNING TAGS (auto-saved) ━━━
{tag_list}

━━━ 🧠 CONTENT ANGLES ━━━
{angles}

━━━ 🎯 MARKET GAP ━━━
{gap}

{config_status}
🤖 These patterns are now live in your pipeline — next videos will use them automatically!""")


if __name__ == "__main__":
    main()
