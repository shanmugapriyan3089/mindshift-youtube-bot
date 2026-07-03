"""
Agent 8: Twitter/X Content Poster

Posts 3 pieces of content every day (email draft — you copy-paste to X manually):
1. Latest SHORT promo  — once per day (first run that day)
2. Latest REGULAR video promo — once per day (first run that day)
3. Psychology insight tweet — every run (3x/day), question mode every 3rd

Why no links in tweet body: X/Twitter suppresses tweets with external links by 60-90%.
Strategy: post the engaging tweet, put the link in the FIRST REPLY (thread trick).
"""
import os, sys, json, datetime, tempfile, subprocess
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

TWEET_LOG        = "tweet_log.json"       # historical record (kept for reference)
TWEET_COUNT_LOG  = "tweet_count.json"
PROMO_LOG        = "twitter_promo_log.json"   # rotates which regular video to promote
DAILY_LOG        = "twitter_daily_log.json"   # tracks what was posted TODAY
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

def _get_daily_status() -> dict:
    """Returns today's posting status — resets each day."""
    log   = _load_json(DAILY_LOG, {})
    today = datetime.date.today().isoformat()
    if log.get("date") != today:
        return {"date": today, "short_done": False, "regular_done": False}
    return log

def _save_daily_status(status: dict):
    _save_json(DAILY_LOG, status)

def _get_latest_short() -> dict | None:
    """Return the most recently uploaded Short."""
    all_log = _load_json("upload_log.json", [])
    shorts  = sorted([v for v in all_log if v.get("type") == "shorts"],
                     key=lambda x: x.get("uploaded_at", ""), reverse=True)
    return shorts[0] if shorts else None

def _mark_tweeted(video_id: str):
    tweeted = list(set(_load_json(TWEET_LOG, [])))
    if video_id not in tweeted:
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
    from agents.notifier import send, write_agent_report

    tweet_count = _get_tweet_count()
    daily       = _get_daily_status()
    today_str   = datetime.date.today().strftime("%A %d %b")

    # tweets_to_send: list of (label, tweet_body, reply_text_or_None)
    tweets_to_send = []
    promo_video_id = None
    short_vid_id   = None
    errors         = []

    # ── DAILY SHORT PROMO (once per day — first run that day) ────────────────
    if not daily["short_done"]:
        short = _get_latest_short()
        if short:
            short_vid_id = short.get("video_id", "")
            title = short.get("title", "").replace(" #Shorts", "").strip()
            tweet = f"{title}\n\n#psychology #mindset"
            reply = f"Watch now → https://youtu.be/{short_vid_id}"
            tweets_to_send.append(("TODAY'S SHORT", tweet, reply))
            daily["short_done"] = True
            print(f"[Twitter] Short added: {title[:50]}")
        else:
            errors.append("No Shorts found in upload_log.json")

    # ── DAILY REGULAR VIDEO PROMO (once per day — first run that day) ────────
    if not daily["regular_done"]:
        video = _get_next_promo_video()
        if video:
            promo_video_id = video["video_id"]
            vid_title      = video.get("title", "")
            # Psychology hook tweet + regular video link in reply
            reg_tweet = _generate_psychology_tweet(question_mode=False)
            reg_reply = f"Full breakdown → https://youtu.be/{promo_video_id}"
            tweets_to_send.append((f"TODAY'S REGULAR VIDEO — {vid_title[:45]}", reg_tweet, reg_reply))
            daily["regular_done"] = True
            print(f"[Twitter] Regular added: {vid_title[:50]}")
        else:
            errors.append("No regular videos found in upload_log.json")

    # ── PSYCHOLOGY INSIGHT (every run, 3x/day — question mode every 3rd) ─────
    question_mode = (tweet_count + 1) % 3 == 0
    insight_tweet = _generate_psychology_tweet(question_mode=question_mode)
    mode_tag = " [question — drives replies]" if question_mode else ""
    tweets_to_send.append((f"PSYCHOLOGY INSIGHT{mode_tag}", insight_tweet, None))

    # ── Build email ───────────────────────────────────────────────────────────
    body_lines = [
        f"X (Twitter) — {today_str}  |  Run #{tweet_count + 1}",
        "═" * 50,
        "NOTE: NEVER paste YouTube links in the tweet body — X suppresses reach by 60-90%.",
        "Always put the link in STEP 2 (your reply to your own tweet).",
        "",
    ]

    for i, (label, tweet_text, reply_text) in enumerate(tweets_to_send, 1):
        body_lines += [
            f"{'─'*50}",
            f"TWEET {i}  ·  {label}",
            f"{'─'*50}",
        ]
        if reply_text:
            body_lines += [
                "STEP 1 — Post this tweet:",
                tweet_text,
                "",
                "STEP 2 — Immediately reply to YOUR OWN tweet with:",
                reply_text,
            ]
        else:
            body_lines += [
                "Post this tweet:",
                tweet_text,
            ]
        body_lines.append("")

    body_lines += [
        "─" * 50,
        f"Short posted today: {'✅ YES' if daily['short_done'] else '⬜ NO — no Shorts in log'}",
        f"Regular video posted today: {'✅ YES' if daily['regular_done'] else '⬜ NO — no regulars in log'}",
        f"Run #{tweet_count + 1} of the day",
    ]

    body = "\n".join(body_lines)

    try:
        short_label = "Short + Regular + Insight" if (daily["short_done"] and daily["regular_done"]) \
                      else "Insight only (Short/Regular already sent today)"
        send(body, subject=f"Agent 8 Twitter — {short_label} | {today_str}")
        print("[Twitter] Email sent")
    except Exception as e:
        print(f"[Twitter] Email failed: {e}")
        errors.append(f"Email failed: {e}")
        print(body)

    # ── Mark & save ───────────────────────────────────────────────────────────
    if short_vid_id:
        _mark_tweeted(short_vid_id)   # keep historical log
    if promo_video_id:
        _mark_regular_promoted(promo_video_id)
    _save_daily_status(daily)
    _increment_tweet_count()

    write_agent_report("twitter", {
        "status":           "ok" if not errors else "partial",
        "tweets_drafted":   len(tweets_to_send),
        "short_posted_today":   daily["short_done"],
        "regular_posted_today": daily["regular_done"],
        "short_video_id":   short_vid_id or "",
        "promo_video_id":   promo_video_id or "",
        "question_mode":    question_mode,
        "tweet_count":      tweet_count + 1,
        "summary":          f"{len(tweets_to_send)} tweet(s) — Short: {'✅' if daily['short_done'] else '❌'}, Regular: {'✅' if daily['regular_done'] else '❌'}, Insight: ✅",
        "errors":           errors,
    })


if __name__ == "__main__":
    main()
