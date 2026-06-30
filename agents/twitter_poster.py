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
    import random, datetime
    topics = [
        "why people self-sabotage right before success",
        "how dopamine makes you chase but never feel satisfied",
        "why trauma keeps you stuck in old patterns",
        "the psychology of why validation feels addictive",
        "why your identity resists change even when you want it",
        "how childhood wounds show up in adult relationships",
        "why people stay in situations that hurt them",
        "the science of why willpower always fails eventually",
        "how social comparison quietly destroys confidence",
        "why your brain replays embarrassing memories at 3am",
        "the real reason people can't take compliments",
        "why being busy feels safer than being still",
        "how people mistake anxiety for excitement",
        "why some people attract chaos without realising it",
        "the psychology behind never feeling good enough",
        "why humans fear success more than failure",
        "how unmet childhood needs drive adult behavior",
        "why people push away the things they want most",
        "the neuroscience of why habits are so hard to break",
        "why some people can't stop apologising for everything",
    ]
    # Rotate topics by date + time of day so no two consecutive tweets repeat
    seed = int(datetime.datetime.utcnow().strftime("%Y%m%d%H"))
    random.seed(seed)
    topic = random.choice(topics)

    try:
        from groq import Groq
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        prompt = f"""Write ONE psychology insight tweet about: "{topic}"

Rules:
- EXACTLY 2-3 lines. No more.
- Line 1: A bold, specific observation (under 70 chars) — DO NOT start with "You're stuck"
- Line 2: The science or reason why (under 70 chars)
- Line 3 (optional): A reframe or takeaway (under 60 chars)
- End with 2-3 hashtags from: #psychology #mindset #selfimprovement #mentalhealth #motivation #habits #brain
- Sound like a smart friend texting you, not a textbook
- DO NOT start with "Did you know", "Fun fact", "You're stuck in a loop", or "Overthinking"

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
    tweet_count = _get_tweet_count()

    tweets_to_send = []

    # ── Step 1: Shorts promo for any new uploads ─────────────────────────────
    unposted = _get_unposted_uploads()
    shorts   = [v for v in unposted if v.get("type") == "shorts"]

    for upload in shorts[:2]:
        vid   = upload.get("video_id", "")
        title = upload.get("title", "").replace(" #Shorts", "").strip()
        tweet = f"{title[:120]}\n\nhttps://youtu.be/{vid}\n#psychology #mindset #Shorts"
        tweets_to_send.append(("Short promo", tweet, vid))

    # ── Step 2: Psychology insight — only every 5th tweet promotes the video ─
    tweet = _generate_psychology_tweet()

    is_promo_tweet = (tweet_count + 1) % 5 == 0
    if is_promo_tweet:
        all_log  = _load_json("upload_log.json", [])
        regulars = sorted(
            [v for v in all_log if v.get("type") == "regular"],
            key=lambda x: x.get("uploaded_at", ""), reverse=True
        )
        latest_video = regulars[0] if regulars else None
        if latest_video:
            video_url = f"https://youtu.be/{latest_video['video_id']}"
            tweet = tweet[:240] + f"\n\n{video_url}"

    label = "Psychology insight (+ video promo)" if is_promo_tweet else "Psychology insight"
    tweets_to_send.append((label, tweet, None))

    # ── Email all tweets to user ─────────────────────────────────────────────
    if not tweets_to_send:
        print("[Agent 8: Twitter] Nothing to send today")
        return

    body_lines = ["Post these tweets on X today:\n"]
    for label, tweet, vid in tweets_to_send:
        body_lines.append(f"[ {label} ]")
        body_lines.append("Copy from here:")
        body_lines.append("─" * 30)
        body_lines.append(tweet)
        body_lines.append("─" * 30)
        body_lines.append("")

    body_lines.append("─" * 40)
    body_lines.append(f"Total tweets posted so far: {tweet_count}")
    body = "\n".join(body_lines)

    try:
        from agents.notifier import send
        send(body, subject="Agent 8: Post these tweets on X today")
        print("[Agent 8: Twitter] Tweet drafts emailed")
    except Exception as e:
        print(f"[Agent 8: Twitter] Email failed: {e}")
        print(body)

    # Mark shorts as handled so they don't repeat tomorrow
    for label, tweet, vid in tweets_to_send:
        if vid:
            _mark_tweeted(vid)
    _increment_tweet_count()


if __name__ == "__main__":
    main()
