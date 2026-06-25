"""
Agent 5: Reddit Outreach (runs daily)
Finds hot Reddit posts about psychology/motivation → Groq drafts helpful comments
→ sends drafts to Telegram for manual posting (never auto-posts — stays within Reddit ToS)
"""
import os, sys, re, requests
from groq import Groq

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import GROQ_API_KEY, DAILY_TOPICS

CHANNEL_URL = "https://youtube.com/@MindShiftProductivity"

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

KEYWORDS = ["motivation", "habits", "procrastination", "confidence", "success", "anxiety",
            "psychology", "mindset", "productivity", "self improvement"]

_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; research-bot/1.0)"}


def _fetch_hot_posts(subreddit: str, limit: int = 25) -> list:
    """Fetch hot posts directly — no keyword filter, Groq decides relevance."""
    url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit={limit}"
    try:
        r = requests.get(url, headers=_HEADERS, timeout=20)
        print(f"  [Reddit] r/{subreddit} status: {r.status_code}")
        if r.status_code != 200:
            return []
        items = r.json()["data"]["children"]
        posts = []
        for item in items:
            d = item["data"]
            if d.get("stickied"):
                continue
            posts.append({
                "title": d["title"],
                "url": f"https://reddit.com{d['permalink']}",
                "score": d.get("score", 0),
                "subreddit": f"r/{subreddit}",
                "num_comments": d.get("num_comments", 0),
                "selftext": d.get("selftext", "")[:300],
            })
        return posts
    except Exception as e:
        print(f"  [Reddit] r/{subreddit} error: {e}")
        return []


def _draft_comment(post: dict, client: Groq) -> str:
    context = post["selftext"] if post["selftext"] else post["title"]
    prompt = f"""A Reddit post in {post['subreddit']} has gotten lots of attention:

Title: "{post['title']}"
Context: "{context[:200]}"

You run "MindShift Productivity" — a YouTube psychology/motivation channel.
Our recent video topics: {', '.join(DAILY_TOPICS[:6])}

Write a Reddit comment (3-5 sentences) that:
1. Opens with a SPECIFIC, genuinely insightful observation about this exact post — something most people wouldn't say
2. Sounds like a real person sharing lived experience, not a content creator promoting anything
3. ONE natural sentence at the very end ONLY if the video topic is directly related: "I went deep on this recently: {CHANNEL_URL}"
4. If the topic is only loosely related, skip the channel mention entirely — a helpful comment with no link is better than a forced plug
5. No hashtags, no "check out my channel", no "great post!", no sycophantic openers
6. Must be helpful enough that people would upvote it on its own merit

Write ONLY the comment. No preamble, no quotes."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.85,
        max_tokens=250,
    )
    return response.choices[0].message.content.strip()


def _send_groq_fallback(client: Groq):
    """When Reddit blocks us, generate search targets + comment templates with Groq."""
    from agents.notifier import send
    prompt = f"""Generate 5 Reddit outreach opportunities for a YouTube psychology/motivation channel "MindShift Productivity".

For each opportunity provide:
1. Which subreddit to search (from: r/GetMotivated, r/selfimprovement, r/psychology, r/productivity, r/LifeAdvice)
2. What search term to use on reddit.com to find relevant posts
3. A ready-to-post comment template (3-4 sentences, helpful, ends with "I made a video on this: {CHANNEL_URL}")

Topics we cover: {', '.join(DAILY_TOPICS[:8])}

Format as plain text, 5 entries numbered 1-5."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8, max_tokens=1000,
    )
    content = response.choices[0].message.content.strip()
    send(f"""💬 <b>Agent 5: Reddit Outreach Guide</b>
(Reddit API unavailable today — use these manual targets)

{content}

🔍 <b>How to use:</b> Go to reddit.com → search each term → find a post with 50+ upvotes → post the comment template""")


def main():
    from agents.notifier import send

    client = Groq(api_key=GROQ_API_KEY)
    print("[Agent 5: Reddit] Searching for relevant posts...")

    all_posts = []
    for sub in SUBREDDITS:
        posts = _fetch_hot_posts(sub, limit=25)
        print(f"  r/{sub}: {len(posts)} relevant posts")
        all_posts.extend(posts)

    # Deduplicate + sort by score
    seen = set()
    unique = []
    for p in sorted(all_posts, key=lambda x: x["score"], reverse=True):
        if p["url"] not in seen and len(unique) < 10:
            seen.add(p["url"])
            unique.append(p)

    if not unique:
        # Reddit blocked us — generate synthetic outreach targets using Groq instead
        print("  Reddit blocked. Generating manual outreach targets with Groq...")
        _send_groq_fallback(client)
        return

    print(f"  {len(unique)} posts found. Drafting comments for top 5...")
    message = (
        "💬 <b>Agent 5: Reddit Outreach — Daily Targets</b>\n"
        "Open each link → find the post → tap Reply → paste the comment\n"
        "⚡ Takes 5 mins. Each comment = potential viral traffic.\n"
    )

    for i, post in enumerate(unique[:5], 1):
        try:
            comment = _draft_comment(post, client)
        except Exception as e:
            comment = f"[Error: {e}]"

        message += f"""
━━━━━━━━━━━━━━━━━━
<b>{i}.</b> {post['subreddit']} · 👍 {post['score']:,} upvotes · 💬 {post['num_comments']} comments
<b>{post['title'][:70]}</b>
👉 <a href="{post['url']}">Open post on Reddit</a>

📝 <b>Paste this comment:</b>
<code>{comment}</code>
"""

    message += (
        "\n━━━━━━━━━━━━━━━━━━\n"
        "🎯 <b>Best subreddits to search manually:</b>\n"
        "• r/selfimprovement — search: procrastination / anxiety / habits\n"
        "• r/psychology — search: motivation / decision making\n"
        "• r/GetMotivated — any hot post with 500+ upvotes\n\n"
        f"🔗 Our channel: {CHANNEL_URL}"
    )
    send(message, subject="Agent 5: Reddit Outreach Targets")


if __name__ == "__main__":
    main()
