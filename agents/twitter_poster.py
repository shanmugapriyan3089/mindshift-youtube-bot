"""
Agent 8: Twitter/X Content + Video Poster

Posts 3 types of content:
1. Psychology insight tweets (2-3 lines) — builds audience
2. Every 5th tweet: promotes latest regular video (2-3 lines + link)
3. Shorts: uploaded as native X video (no link — native video gets 3-5x more reach)

Secrets needed: TWITTER_API_KEY, TWITTER_API_SECRET,
                TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET
"""
import os, sys, json, tempfile, subprocess
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

TWEET_LOG      = "tweet_log.json"
TWEET_COUNT_LOG = "tweet_count.json"
CHANNEL_URL    = "https://youtube.com/@MindShiftProductivity"


# ── Helpers ───────────────────────────────────────────────────────────────────

def _load_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return default

def _save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def _get_tweet_count() -> int:
    return _load_json(TWEET_COUNT_LOG, {"count": 0}).get("count", 0)

def _increment_tweet_count():
    count = _get_tweet_count() + 1
    _save_json(TWEET_COUNT_LOG, {"count": count})
    return count

def _get_unposted_uploads() -> list:
    log = _load_json("upload_log.json", [])
    tweeted = set(_load_json(TWEET_LOG, []))
    return [v for v in log if v.get("video_id") not in tweeted]

def _mark_tweeted(video_id: str):
    tweeted = list(set(_load_json(TWEET_LOG, [])))
    tweeted.append(video_id)
    _save_json(TWEET_LOG, tweeted)


# ── Tweet generators ──────────────────────────────────────────────────────────

def _generate_psychology_tweet() -> str:
    """Use Groq to write a 2-3 line psychology insight tweet."""
    try:
        from groq import Groq
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        prompt = """Write ONE psychology insight tweet for a self-improvement account.

Rules:
- EXACTLY 2-3 lines. No more.
- Line 1: A relatable observation or shocking fact (under 70 chars)
- Line 2: The science/reason why (under 70 chars)
- Line 3 (optional): The reframe or takeaway (under 60 chars)
- End with 2-3 hashtags: pick from #psychology #mindset #selfimprovement #mentalhealth #motivation #habits #brain
- DO NOT start with "Did you know" or "Fun fact"
- Sound like a smart friend texting you, not a textbook
- Topic: something about being stuck, overthinking, self-sabotage, procrastination, or emotional patterns

Example format:
Your brain treats social rejection the same as physical pain.
That's why being left out hurts — literally.
You're not too sensitive. You're wired that way.
#psychology #mindset

Write only the tweet. No intro, no explanation."""

        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.9,
            max_tokens=120,
        )
        tweet = resp.choices[0].message.content.strip()
        return tweet[:280]
    except Exception as e:
        print(f"[Twitter] Groq failed: {e}")
        # Fallback hardcoded insight
        fallbacks = [
            "Your brain releases the same stress hormones for imagined threats as real ones.\nThat meeting you keep dreading? Already hurting you.\nWorry is suffering twice.\n#psychology #mindset",
            "Procrastination is not laziness.\nIt's your nervous system avoiding a task it has linked to pain or failure.\nThe block is emotional, not logical.\n#psychology #brain",
            "Most people do not change because change requires admitting the old version of you was wrong.\nThe ego resists that more than the discomfort does.\n#mindset #selfimprovement",
            "You do not remember events accurately.\nYou remember how you felt during them — and reconstruct the rest.\nMemory is a story, not a recording.\n#psychology #brain",
            "The inner critic in your head is not yours.\nIt was someone else's voice so long ago you forgot it ever came from outside.\n#psychology #mentalhealth",
        ]
        import random, datetime
        random.seed(datetime.date.today().isoformat())
        return random.choice(fallbacks)


def _build_promo_tweet(title: str, video_id: str) -> str:
    """2-3 line video promo tweet for regular videos."""
    clean = title.replace(" #Shorts", "").strip()
    url   = f"https://youtu.be/{video_id}"
    # Keep it short — hook + link + 1 hashtag line
    hook = clean[:90]
    return f"{hook}\n\nFull breakdown → {url}\n#psychology #mindset #selfimprovement"


# ── Native video upload (Shorts only) ────────────────────────────────────────

def _download_short(video_id: str, out_dir: str) -> str | None:
    """Download a YouTube Short with yt-dlp."""
    out = os.path.join(out_dir, f"{video_id}.mp4")
    try:
        r = subprocess.run(
            ["yt-dlp", "-f", "mp4", "-o", out,
             f"https://youtu.be/{video_id}"],
            capture_output=True, timeout=120
        )
        if r.returncode == 0 and os.path.exists(out) and os.path.getsize(out) > 1000:
            return out
        print(f"[Twitter] yt-dlp failed: {r.stderr[-200:]}")
    except Exception as e:
        print(f"[Twitter] Download error: {e}")
    return None


def _post_video_tweet(api, client, video_path: str, caption: str):
    """Upload video to X and post tweet with it."""
    print("[Twitter] Uploading video to X...")
    media = api.media_upload(
        filename=video_path,
        media_category="tweet_video",
        chunked=True
    )
    # Wait for processing
    import time
    for _ in range(20):
        info = api.get_media_upload_status(media.media_id)
        state = info.processing_info.state if hasattr(info, 'processing_info') else 'succeeded'
        if state == 'succeeded':
            break
        if state == 'failed':
            print("[Twitter] Video processing failed")
            return None
        time.sleep(3)

    resp = client.create_tweet(text=caption[:280], media_ids=[media.media_id_string])
    return resp.data["id"] if resp and resp.data else None


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    api_key        = os.getenv("TWITTER_API_KEY")
    api_secret     = os.getenv("TWITTER_API_SECRET")
    access_token   = os.getenv("TWITTER_ACCESS_TOKEN")
    access_secret  = os.getenv("TWITTER_ACCESS_SECRET")

    if not all([api_key, api_secret, access_token, access_secret]):
        print("[Agent 8: Twitter] Credentials not set — skipping")
        return

    try:
        import tweepy
    except ImportError:
        print("[Twitter] tweepy not installed")
        return

    # v2 client for text tweets
    client = tweepy.Client(
        consumer_key=api_key,
        consumer_secret=api_secret,
        access_token=access_token,
        access_token_secret=access_secret,
    )

    # v1.1 API for media uploads
    auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_secret)
    api  = tweepy.API(auth)

    posted_this_run = []
    tweet_count = _get_tweet_count()

    # ── Step 1: Post any new Shorts as native video ──────────────────────────
    unposted = _get_unposted_uploads()
    shorts   = [v for v in unposted if v.get("type") == "shorts"]

    for upload in shorts[:2]:  # max 2 per run
        vid   = upload.get("video_id", "")
        title = upload.get("title", "").replace(" #Shorts", "").strip()
        caption = f"{title[:120]}\n\n#psychology #mindset #Shorts"

        with tempfile.TemporaryDirectory() as tmpdir:
            video_path = _download_short(vid, tmpdir)
            if video_path:
                try:
                    tweet_id = _post_video_tweet(api, client, video_path, caption)
                    if tweet_id:
                        _mark_tweeted(vid)
                        tweet_count = _increment_tweet_count()
                        posted_this_run.append(("video", caption[:80], f"https://x.com/i/web/status/{tweet_id}"))
                        print(f"[Twitter] Short posted as native video: {title[:50]}")
                except Exception as e:
                    print(f"[Twitter] Video upload failed: {e}")
                    # Fallback to link tweet
                    try:
                        tweet = f"{title[:120]}\n\nhttps://youtu.be/{vid}\n#psychology #Shorts"
                        resp = client.create_tweet(text=tweet)
                        _mark_tweeted(vid)
                        tweet_count = _increment_tweet_count()
                        posted_this_run.append(("link", tweet[:80], ""))
                    except Exception as e2:
                        print(f"[Twitter] Fallback tweet failed: {e2}")
            else:
                # yt-dlp failed, post link instead
                try:
                    tweet = f"{title[:120]}\n\nhttps://youtu.be/{vid}\n#psychology #Shorts"
                    resp  = client.create_tweet(text=tweet)
                    _mark_tweeted(vid)
                    tweet_count = _increment_tweet_count()
                    posted_this_run.append(("link", tweet[:80], ""))
                except Exception as e:
                    print(f"[Twitter] Link tweet failed: {e}")

    # ── Step 2: Post psychology insight OR video promo ───────────────────────
    tweet_count = _get_tweet_count()

    if tweet_count % 5 == 4:
        # Every 5th tweet = promote latest regular video
        regulars = [v for v in _get_unposted_uploads() if v.get("type") == "regular"]
        if not regulars:
            # All promoted already — pick most recent from full log
            all_log  = _load_json("upload_log.json", [])
            regulars = [v for v in all_log if v.get("type") == "regular"]

        if regulars:
            latest = sorted(regulars, key=lambda x: x.get("uploaded_at",""), reverse=True)[0]
            tweet  = _build_promo_tweet(latest["title"], latest["video_id"])
            try:
                resp = client.create_tweet(text=tweet)
                tweet_count = _increment_tweet_count()
                posted_this_run.append(("promo", tweet[:80], ""))
                print(f"[Twitter] Video promo posted")
            except Exception as e:
                print(f"[Twitter] Promo failed: {e}")
    else:
        # Psychology insight tweet
        tweet = _generate_psychology_tweet()
        try:
            resp = client.create_tweet(text=tweet)
            tweet_count = _increment_tweet_count()
            posted_this_run.append(("insight", tweet[:80], ""))
            print(f"[Twitter] Psychology tweet posted")
        except Exception as e:
            print(f"[Twitter] Insight tweet failed: {e}")

    # ── Notify ───────────────────────────────────────────────────────────────
    if posted_this_run:
        try:
            from agents.notifier import send
            lines = "\n".join(
                f"{'📹' if t=='video' else '🎯' if t=='promo' else '🧠'} {text}..."
                for t, text, _ in posted_this_run
            )
            send(f"Agent 8: Twitter\n{lines}\nTotal tweets: {tweet_count}",
                 subject="Agent 8: Twitter posted")
        except Exception:
            pass
    else:
        print("[Twitter] Nothing posted this run")


if __name__ == "__main__":
    main()
