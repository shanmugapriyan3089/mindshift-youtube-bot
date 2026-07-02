"""
Agent 8: Twitter/X Content Poster

Posts 2 types of content (all via email draft — you copy-paste to X manually):
1. Psychology insight tweets (2-3 lines, NO external link) — builds audience reach
2. Every 5th tweet: same insight + a REPLY suggestion with the YouTube link

Why no links in tweet body: X/Twitter suppresses tweets with external links by 60-90%.
Strategy: post the engaging tweet first, put the link in the first reply (thread trick).
Big accounts (Ali Abdaal, etc.) all do this.
"""
import os, sys, json, tempfile, subprocess
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

TWEET_LOG        = "tweet_log.json"
TWEET_COUNT_LOG  = "tweet_count.json"
PROMO_LOG        = "twitter_promo_log.json"   # tracks which regular videos were promoted
CHANNEL_URL      = "https://youtube.com/@MindShiftProductivity"


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

def _get_next_promo_video() -> dict | None:
    """Pick the next regular video to promote — rotates through all, never repeats back-to-back."""
    import datetime
    all_log  = _load_json("upload_log.json", [])
    regulars = [v for v in all_log if v.get("type") == "regular"]
    if not regulars:
        return None
    promo_log = _load_json(PROMO_LOG, {})  # {video_id: ISO timestamp of last promotion}
    # Prefer videos never promoted yet (sorted newest first)
    unpromoted = sorted(
        [v for v in regulars if v.get("video_id") not in promo_log],
        key=lambda x: x.get("uploaded_at", ""), reverse=True,
    )
    if unpromoted:
        return unpromoted[0]
    # All promoted — pick the one promoted longest ago
    return min(regulars, key=lambda x: promo_log.get(x.get("video_id", ""), ""))

def _mark_regular_promoted(video_id: str):
    import datetime
    promo_log = _load_json(PROMO_LOG, {})
    promo_log[video_id] = datetime.datetime.utcnow().isoformat()
    _save_json(PROMO_LOG, promo_log)


# ── Tweet generators ──────────────────────────────────────────────────────────

def _generate_psychology_tweet(question_mode: bool = False) -> str:
    """Use Groq to write a 2-3 line psychology insight tweet — NO external links, max 2 hashtags.
    question_mode=True: ends with a reflective question instead of hashtags (drives replies)."""
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
        "how the brain confuses familiarity with safety",
        "why people repeat the same relationship patterns",
        "the link between perfectionism and low self-worth",
        "why rest feels wrong when you grew up in survival mode",
        "how avoidance makes anxiety permanently worse",
        "why people feel guilty for setting boundaries",
        "the psychology of why you can't accept good things",
        "how your nervous system stays stuck in the past",
    ]
    # Rotate topics by date + time-of-day seed so runs within same day pick different topics
    seed = int(datetime.datetime.utcnow().strftime("%Y%m%d%H"))
    random.seed(seed)
    topic = random.choice(topics)

    try:
        from groq import Groq
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        if question_mode:
            ending_rule = (
                "- Last line: end with ONE short reflective question (under 55 chars) "
                "that makes the reader think about themselves. No hashtags."
            )
        else:
            ending_rule = (
                "- Last line: end with EXACTLY 1-2 hashtags — pick the most relevant from: "
                "#psychology #mindset #mentalhealth #brain #habits #selfawareness"
            )

        prompt = f"""Write ONE psychology insight tweet about: "{topic}"

Rules:
- EXACTLY 2-3 lines. No more, no less.
- Line 1: A bold, specific observation (under 70 chars)
- Line 2: The science or reason why (under 70 chars)
{ending_rule}
- Sound like a smart, blunt friend — NOT a textbook or a life coach
- DO NOT start with: "Did you know", "Fun fact", "You're stuck", "Overthinking", "Most people"
- NO external links. NO emojis.

Write only the tweet text. Nothing else."""

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
            "Your brain releases the same stress hormones for imagined threats as real ones.\nThat meeting you keep dreading? Already hurting you.\nWorry is suffering twice.\n\n#psychology #brain",
            "Procrastination is not laziness.\nIt's your nervous system avoiding a task it links to pain or failure.\nThe block is emotional, not logical.\n\n#psychology #mindset",
            "Change requires admitting the old version of you was wrong.\nThe ego resists that more than the discomfort does.\n\n#mindset #selfawareness",
            "You don't remember events accurately.\nYou remember how you felt — and reconstruct the rest.\nMemory is a story, not a recording.\n\n#psychology #brain",
            "The inner critic in your head is not yours.\nIt was someone else's voice, so long ago you forgot it ever came from outside.\n\n#psychology #mentalhealth",
            "Guilt after setting a boundary means the boundary was necessary.\nHealthy people don't make you feel guilty for having limits.\n\n#psychology #mindset",
            "Your body keeps score of everything your mind tries to forget.\nUnprocessed stress doesn't disappear — it relocates.\n\n#psychology #brain",
        ]
        import random, datetime
        random.seed(datetime.date.today().isoformat())
        return random.choice(fallbacks)



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

    # tweets_to_send: list of (label, tweet_body, vid_to_mark, reply_text_or_None)
    # reply_text: put the YouTube link here — post as a reply to your own tweet, NOT in the tweet body
    tweets_to_send = []

    # ── Step 1: Shorts promo for any new uploads ─────────────────────────────
    unposted = _get_unposted_uploads()
    shorts   = [v for v in unposted if v.get("type") == "shorts"]

    for upload in shorts[:2]:
        vid   = upload.get("video_id", "")
        title = upload.get("title", "").replace(" #Shorts", "").strip()
        # Tweet body: title as hook, no link — link goes in reply to avoid X suppression
        tweet = f"{title}\n\n#psychology #mindset"
        reply = f"Watch it here → https://youtu.be/{vid}"
        tweets_to_send.append(("Short promo", tweet, vid, reply))

    # ── Step 2: Psychology insight — question mode every 3rd run, link every 5th ──
    question_mode = (tweet_count + 1) % 3 == 0
    tweet = _generate_psychology_tweet(question_mode=question_mode)
    reply = None
    promo_video_id = None

    is_promo_tweet = (tweet_count + 1) % 5 == 0
    if is_promo_tweet:
        video = _get_next_promo_video()
        if video:
            promo_video_id = video["video_id"]
            vid_title = video.get("title", "")[:60]
            reply = f"Full breakdown → https://youtu.be/{promo_video_id}"

    promo_in = 5 - ((tweet_count + 1) % 5)
    mode_tag = " [question]" if question_mode else ""
    if is_promo_tweet:
        vid_label = f" — {vid_title}" if promo_video_id else ""
        label = f"Psychology insight{mode_tag} (promo run{vid_label})"
    else:
        label = f"Psychology insight{mode_tag} (next promo in {promo_in} tweet{'s' if promo_in != 1 else ''})"
    tweets_to_send.append((label, tweet, None, reply))

    # ── Email all tweets to user ─────────────────────────────────────────────
    if not tweets_to_send:
        print("[Agent 8: Twitter] Nothing to send today")
        return

    body_lines = [
        "X (Twitter) drafts for today:",
        "NOTE: NEVER put YouTube links in the tweet body — X suppresses them.",
        "Put links in your REPLY to your own tweet instead (see STEP 2 below).",
        "",
    ]
    for label, tweet, vid, reply in tweets_to_send:
        body_lines.append(f"┌── {label} ──")
        if reply:
            body_lines.append("STEP 1 — Post this tweet on X:")
        else:
            body_lines.append("Post this tweet on X:")
        body_lines.append("─" * 40)
        body_lines.append(tweet)
        body_lines.append("─" * 40)
        if reply:
            body_lines.append("")
            body_lines.append("STEP 2 — Immediately reply to your OWN tweet above with this:")
            body_lines.append("(tap Reply on your tweet, paste this, post)")
            body_lines.append("─" * 40)
            body_lines.append(reply)
            body_lines.append("─" * 40)
        body_lines.append("")

    body_lines.append(f"Total tweet runs so far: {tweet_count + 1}")
    body = "\n".join(body_lines)

    try:
        from agents.notifier import send
        send(body, subject="Agent 8: Post these tweets on X today")
        print("[Agent 8: Twitter] Tweet drafts emailed")
    except Exception as e:
        print(f"[Agent 8: Twitter] Email failed: {e}")
        print(body)

    # Mark shorts as handled so they don't repeat tomorrow
    for label, tweet, vid, reply in tweets_to_send:
        if vid:
            _mark_tweeted(vid)
    # Mark which regular video was promoted so we don't repeat it next run
    if promo_video_id:
        _mark_regular_promoted(promo_video_id)
    _increment_tweet_count()


if __name__ == "__main__":
    main()
