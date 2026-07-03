"""
Agent 5: Reddit Outreach (runs daily)
Finds Reddit posts < 7 days old about psychology/motivation → Groq drafts helpful comments
→ sends drafts to email for manual posting (never auto-posts — stays within Reddit ToS)
"""
import os, sys, re, json, time as _time, requests
from groq import Groq

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import GROQ_API_KEY, DAILY_TOPICS

CHANNEL_URL = "https://youtube.com/@MindShiftProductivity"
MAX_AGE_DAYS = 7       # hard cutoff
PREFER_AGE_DAYS = 3    # preferred: posts ≤ 3 days old first

SUBREDDITS = [
    "GetMotivated",
    "selfimprovement",
    "psychology",
    "productivity",
    "Entrepreneur",
    "LifeAdvice",
    "decidingtobebetter",
    "mentalhealth",
    "getdisciplined",
    "ChangeMyView",
]

_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; research-bot/1.0)"}


def _get_latest_urls() -> tuple[str, str]:
    """Returns (regular_video_url, shorts_url) from upload_log.json."""
    try:
        with open("upload_log.json") as f:
            log = json.load(f)
        regulars = sorted(
            [v for v in log if v.get("type") == "regular"],
            key=lambda x: x.get("uploaded_at", ""), reverse=True
        )
        shorts = sorted(
            [v for v in log if v.get("type") == "shorts"],
            key=lambda x: x.get("uploaded_at", ""), reverse=True
        )
        reg_url = f"https://youtu.be/{regulars[0]['video_id']}" if regulars else CHANNEL_URL
        short_url = f"https://youtu.be/{shorts[0]['video_id']}" if shorts else ""
        return reg_url, short_url
    except Exception:
        return CHANNEL_URL, ""


def _fetch_recent_posts(subreddit: str) -> list:
    """Fetch posts from the past week via top/week then new, filter by created_utc."""
    cutoff = _time.time() - MAX_AGE_DAYS * 86400
    seen = set()
    posts = []

    endpoints = [
        f"https://www.reddit.com/r/{subreddit}/top.json?t=week&limit=25",
        f"https://www.reddit.com/r/{subreddit}/new.json?limit=25",
    ]

    for url in endpoints:
        try:
            r = requests.get(url, headers=_HEADERS, timeout=20)
            if r.status_code != 200:
                continue
            for item in r.json()["data"]["children"]:
                d = item["data"]
                if d.get("stickied") or d.get("is_video"):
                    continue
                if d.get("created_utc", 0) < cutoff:
                    continue
                permalink = d["permalink"]
                if permalink in seen:
                    continue
                seen.add(permalink)
                age_days = (_time.time() - d.get("created_utc", _time.time())) / 86400
                posts.append({
                    "title": d["title"],
                    "url": f"https://reddit.com{permalink}",
                    "score": d.get("score", 0),
                    "subreddit": f"r/{subreddit}",
                    "num_comments": d.get("num_comments", 0),
                    "selftext": d.get("selftext", "")[:300],
                    "age_days": age_days,
                })
        except Exception as e:
            print(f"  [Reddit] r/{subreddit} ({url.split('/')[-1].split('?')[0]}) error: {e}")

    return posts


def _draft_comment(post: dict, client: Groq, video_url: str, short_url: str) -> str:
    context = post["selftext"] if post["selftext"] else post["title"]
    links_note = f"Regular video: {video_url}"
    if short_url:
        links_note += f"\nShorts clip: {short_url}"

    prompt = f"""A Reddit post in {post['subreddit']} is getting traction right now:

Title: "{post['title']}"
Context: "{context[:200]}"

You run "MindShift Productivity" — a YouTube psychology/motivation channel.
Our recent video topics: {', '.join(DAILY_TOPICS[:6])}
{links_note}

Write a Reddit comment (3-5 sentences) that:
1. Opens with a SPECIFIC, genuinely insightful observation about this exact post
2. Sounds like a real person sharing lived experience, not a content creator
3. ONE natural sentence at the very end ONLY if our video or short is directly relevant:
   - For a full breakdown: "I went deep on this recently: {video_url}"
   - For a quick insight: "Made a 60-second breakdown on this: {short_url}" (only if short_url is set)
4. If neither matches well, skip the link entirely — helpful comment > forced plug
5. No hashtags, no "check out my channel", no "great post!"
6. Must be helpful enough that people would upvote it on merit alone

Write ONLY the comment. No preamble."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.85,
        max_tokens=250,
    )
    return response.choices[0].message.content.strip()


def _send_groq_fallback(client: Groq, video_url: str, short_url: str):
    from agents.notifier import send
    links = f"Regular video: {video_url}"
    if short_url:
        links += f"\nShorts clip: {short_url}"

    prompt = f"""Generate 5 Reddit outreach opportunities for a YouTube psychology/motivation channel "MindShift Productivity".

For each opportunity:
1. Which subreddit to check (from: r/GetMotivated, r/selfimprovement, r/psychology, r/productivity, r/LifeAdvice)
2. What to search on reddit.com to find posts from the last 3 days
3. A ready-to-post comment template (3-4 sentences, helpful, natural link mention)

Our links — use whichever fits best:
{links}

Topics we cover: {', '.join(DAILY_TOPICS[:8])}

Format as plain text, 5 entries numbered 1-5."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8, max_tokens=1000,
    )
    content = response.choices[0].message.content.strip()
    send(
        f"Agent 5: Reddit Outreach Guide\n"
        f"(Reddit unavailable — use these manual targets)\n\n"
        f"{content}\n\n"
        f"Tip: Filter by 'New' or 'Top — This Week' when searching each subreddit.",
        subject="Agent 5: Reddit Outreach Targets"
    )


def main():
    from agents.notifier import send

    client = Groq(api_key=GROQ_API_KEY)
    video_url, short_url = _get_latest_urls()
    print(f"[Agent 5: Reddit] Video: {video_url}")
    print(f"[Agent 5: Reddit] Short: {short_url or 'none'}")
    print("[Agent 5: Reddit] Fetching posts from the past 7 days...")

    all_posts = []
    for sub in SUBREDDITS:
        posts = _fetch_recent_posts(sub)
        print(f"  r/{sub}: {len(posts)} posts within {MAX_AGE_DAYS} days")
        all_posts.extend(posts)

    if not all_posts:
        print("  Reddit unavailable — generating manual outreach targets...")
        _send_groq_fallback(client, video_url, short_url)
        return

    # Dedup + sort: prefer fresh (≤3 days) then by score
    seen = set()
    unique = []
    for p in sorted(all_posts, key=lambda x: (x["age_days"] > PREFER_AGE_DAYS, -x["score"])):
        if p["url"] not in seen and len(unique) < 10:
            seen.add(p["url"])
            unique.append(p)

    print(f"  {len(unique)} unique posts found. Drafting comments for top 5...")

    lines = [
        "Agent 5: Reddit Outreach — Daily Targets",
        f"Latest video: {video_url}",
        f"Latest short: {short_url or 'none yet'}",
        "",
        "Open each link → find the post → tap Reply → paste the comment",
        "Prioritise posts marked [FRESH] — they're still rising.",
        "",
    ]

    for i, post in enumerate(unique[:5], 1):
        age_label = f"[FRESH — {post['age_days']:.0f}d old]" if post["age_days"] <= PREFER_AGE_DAYS else f"[{post['age_days']:.0f}d old]"
        try:
            comment = _draft_comment(post, client, video_url, short_url)
        except Exception as e:
            comment = f"[Error drafting comment: {e}]"

        lines += [
            "─" * 40,
            f"{i}. {post['subreddit']} — {age_label} — {post['score']:,} upvotes — {post['num_comments']} comments",
            post["title"][:80],
            f"Link: {post['url']}",
            "",
            "Paste this comment:",
            comment,
            "",
        ]

    lines += [
        "─" * 40,
        "Best subreddits (sort by New or Top-This-Week):",
        "  r/selfimprovement — procrastination / anxiety / habits",
        "  r/psychology — motivation / decision making",
        "  r/GetMotivated — any hot post with 500+ upvotes",
        "",
        f"Channel: {CHANNEL_URL}",
    ]
    send("\n".join(lines), subject="Agent 5: Reddit Outreach Targets")

    from agents.notifier import write_agent_report
    write_agent_report("reddit", {
        "status":           "ok",
        "posts_found":      len(unique),
        "comments_drafted": min(5, len(unique)),
        "subreddits":       SUBREDDITS,
        "summary":          f"{len(unique)} posts found, {min(5, len(unique))} comment drafts sent to email",
        "errors":           [],
    })


if __name__ == "__main__":
    main()
