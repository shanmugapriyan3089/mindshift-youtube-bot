"""
Agent 5: Reddit Outreach (runs daily)
Finds hot Reddit posts about psychology/motivation → Groq drafts helpful comments
→ sends drafts to Telegram for manual posting (never auto-posts — stays within Reddit ToS)
"""
import os, sys, re, requests
from groq import Groq

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import GROQ_API_KEY, DAILY_TOPICS

CHANNEL_URL = "https://youtube.com/@mindshift-productive"

SUBREDDITS = [
    "GetMotivated",
    "selfimprovement",
    "psychology",
    "productivity",
    "Entrepreneur",
    "LifeAdvice",
    "decidingtobebetter",
]

KEYWORDS = ["motivation", "habits", "procrastination", "confidence", "success mindset", "anxiety"]

_HEADERS = {"User-Agent": "MindShiftProductivity-Bot/1.0 (youtube research)"}


def _search_posts(subreddit: str, keyword: str) -> list:
    url = f"https://www.reddit.com/r/{subreddit}/search.json"
    try:
        r = requests.get(url, params={"q": keyword, "sort": "hot", "limit": 8, "t": "week"},
                         headers=_HEADERS, timeout=15)
        if r.status_code != 200:
            return []
        items = r.json()["data"]["children"]
        return [
            {
                "title": item["data"]["title"],
                "url": f"https://reddit.com{item['data']['permalink']}",
                "score": item["data"]["score"],
                "subreddit": f"r/{subreddit}",
                "num_comments": item["data"]["num_comments"],
                "selftext": item["data"].get("selftext", "")[:300],
            }
            for item in items
            if item["data"]["score"] >= 30 and not item["data"].get("stickied")
        ]
    except Exception as e:
        print(f"  [Reddit] r/{subreddit} '{keyword}': {e}")
        return []


def _draft_comment(post: dict, client: Groq) -> str:
    context = post["selftext"] if post["selftext"] else post["title"]
    prompt = f"""A Reddit post in {post['subreddit']} has gotten lots of attention:

Title: "{post['title']}"
Context: "{context[:200]}"

You run "MindShift Productivity" — a YouTube psychology/motivation channel.
Our recent video topics: {', '.join(DAILY_TOPICS[:6])}

Write a Reddit comment (3-5 sentences) that:
1. Adds genuine insight relevant to this specific post
2. Sounds like a real person sharing experience, not a marketer
3. Naturally mentions our YouTube channel at the end with: "I actually made a video on this: {CHANNEL_URL}"
4. No hashtags, no "check out my channel", no sycophantic opener
5. Specific enough that it reads as helpful, not spam

Write ONLY the comment. Nothing else."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.85,
        max_tokens=250,
    )
    return response.choices[0].message.content.strip()


def main():
    from agents.notifier import send

    client = Groq(api_key=GROQ_API_KEY)
    print("[Agent 5: Reddit] Searching for relevant posts...")

    all_posts = []
    for sub in SUBREDDITS:
        for kw in KEYWORDS[:2]:
            posts = _search_posts(sub, kw)
            all_posts.extend(posts)

    # Deduplicate + sort by score
    seen = set()
    unique = []
    for p in sorted(all_posts, key=lambda x: x["score"], reverse=True):
        if p["url"] not in seen and len(unique) < 10:
            seen.add(p["url"])
            unique.append(p)

    if not unique:
        send("📭 <b>Reddit Agent</b>: No relevant posts found today (Reddit may be slow)")
        return

    print(f"  {len(unique)} posts found. Drafting comments for top 5...")
    message = "💬 <b>Agent 5: Reddit Outreach Drafts</b>\n(Post these manually to get views)\n"

    for post in unique[:5]:
        try:
            comment = _draft_comment(post, client)
        except Exception as e:
            comment = f"[Error generating draft: {e}]"

        message += f"""
━━━━━━━━━━━━━━━━━━
📌 <b>{post['subreddit']}</b> · {post['score']:,} upvotes
<b>{post['title'][:65]}</b>
🔗 {post['url']}

💬 <b>Your comment draft:</b>
{comment}
"""

    message += "\n\n✅ Copy &amp; paste these comments to get real traffic!"
    send(message)


if __name__ == "__main__":
    main()
