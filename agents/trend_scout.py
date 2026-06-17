"""
Agent 1: Trend Scout (runs every Monday)
Finds trending psychology/motivation topics on Reddit → generates new YouTube titles with Groq
→ auto-commits updated DAILY_TOPICS to config.py
"""
import os, sys, json, re, requests
from groq import Groq

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import GROQ_API_KEY, DAILY_TOPICS

SUBREDDITS = ["GetMotivated", "selfimprovement", "psychology", "productivity", "Entrepreneur", "LifeAdvice"]

_HEADERS = {"User-Agent": "MindShiftProductivity-Bot/1.0 (youtube automation research)"}


def _fetch_reddit_hot(subreddit: str, limit: int = 25) -> list:
    url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit={limit}"
    try:
        r = requests.get(url, headers=_HEADERS, timeout=15)
        if r.status_code != 200:
            return []
        posts = r.json()["data"]["children"]
        return [
            p["data"]["title"]
            for p in posts
            if p["data"]["score"] >= 80 and not p["data"].get("stickied", False)
        ]
    except Exception as e:
        print(f"  [TrendScout] Reddit r/{subreddit} error: {e}")
        return []


def _generate_new_topics(trending_titles: list) -> list:
    client = Groq(api_key=GROQ_API_KEY)
    examples = "\n".join(f"- {t}" for t in trending_titles[:35])
    existing = "\n".join(f"- {t}" for t in DAILY_TOPICS)

    prompt = f"""You analyze trending Reddit posts about psychology/motivation and create viral YouTube video titles.

Trending Reddit titles this week:
{examples}

Topics we already cover (do NOT repeat):
{existing}

Create 30 NEW YouTube video topic titles that:
1. Use viral formulas: "X Signs You...", "Why Most People...", "The Truth About...", "Stop Doing X"
2. Target 18-35 audience: psychology, money mindset, habits, confidence, relationships
3. Are NOT duplicates of our existing topics
4. Between 50-70 characters each
5. Promise a clear benefit or trigger curiosity

Respond ONLY with a JSON array of 30 strings. No markdown, no explanation:
["title1", "title2", ...]"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.9,
        max_tokens=2048,
    )
    text = response.choices[0].message.content.strip()
    match = re.search(r'\[.*\]', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except Exception:
            pass
    return []


def _update_config(new_topics: list):
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.py")
    with open(config_path, "r", encoding="utf-8") as f:
        content = f.read()

    topics_str = "DAILY_TOPICS = [\n"
    for t in new_topics[:30]:
        escaped = t.replace("\\", "\\\\").replace('"', '\\"')
        topics_str += f'    "{escaped}",\n'
    topics_str += "]"

    new_content = re.sub(r'DAILY_TOPICS = \[.*?\]', topics_str, content, flags=re.DOTALL)

    with open(config_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"  [TrendScout] config.py updated with {len(new_topics)} topics")


def main():
    from agents.notifier import send

    print("[Agent 1: Trend Scout] Fetching Reddit trending posts...")
    all_titles = []
    for sub in SUBREDDITS:
        titles = _fetch_reddit_hot(sub)
        print(f"  r/{sub}: {len(titles)} posts")
        all_titles.extend(titles)

    if len(all_titles) < 5:
        send("⚠️ <b>Trend Scout</b>: Could not fetch Reddit posts. Skipping update.")
        return

    print(f"  Total trending posts: {len(all_titles)}")
    print("[Trend Scout] Generating new topics with Groq (Llama 3.3 70B)...")
    new_topics = _generate_new_topics(all_titles)

    if len(new_topics) < 15:
        send(f"⚠️ <b>Trend Scout</b>: Only {len(new_topics)} topics generated. Keeping existing.")
        return

    # Pad to 30 with existing topics if needed
    if len(new_topics) < 30:
        extras = [t for t in DAILY_TOPICS if t not in new_topics]
        new_topics = new_topics + extras[:30 - len(new_topics)]

    _update_config(new_topics)

    preview = "\n".join(f"• {t}" for t in new_topics[:10])
    send(f"""🔥 <b>Agent 1: Trend Scout — Weekly Update</b>

Analyzed {len(all_titles)} trending Reddit posts across 6 subreddits.
Updated <b>{len(new_topics)} video topics</b> in config.py!

<b>Top 10 new topics:</b>
{preview}

✅ Committed to GitHub — next videos will use these fresh topics!""")


if __name__ == "__main__":
    main()
