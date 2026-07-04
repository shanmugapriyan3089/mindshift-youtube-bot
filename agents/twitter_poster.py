"""
Agent 8: Twitter/X Content Poster

Posts every run (3x/day):
1. Latest SHORT promo  — once per day (first run)
2. Latest REGULAR video promo — once per day (first run)
3. Psychology insight — every run, in VIRAL FORMAT (thread / YES-NO / numbered / myth-buster)
4. Reply Drops — 3 paste-ready replies for big psychology accounts (drives profile clicks)

Why no links in tweet body: X suppresses tweets with external links by 60-90%.
Strategy: engaging tweet first → link in first reply (thread trick).

Why threads: X algorithm gives 3-5x more impressions to threads vs single tweets.
Why reply drops: Commenting on big accounts (100k+) shows your profile to their entire audience.
Why YES/NO format: Drives replies → algorithm reads replies as strong engagement signal.
"""
import os, sys, json, datetime, tempfile, subprocess
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

TWEET_LOG       = "tweet_log.json"
TWEET_COUNT_LOG = "tweet_count.json"
PROMO_LOG       = "twitter_promo_log.json"
DAILY_LOG       = "twitter_daily_log.json"
CHANNEL_URL     = "https://youtube.com/@MindShiftProductivity"

TOPICS = [
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
    "why emotional avoidance always makes the emotion stronger",
    "the real reason people pleasing feels impossible to stop",
    "why people catastrophise even when things are going well",
    "how hypervigilance becomes a personality trait",
    "why self-sabotage is actually a protection mechanism",
    "the neuroscience of why praise feels uncomfortable",
    "why your brain resists stillness and craves constant stimulation",
]


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
    log   = _load_json(DAILY_LOG, {})
    today = datetime.date.today().isoformat()
    if log.get("date") != today:
        return {"date": today, "short_done": False, "regular_done": False}
    return log

def _save_daily_status(status: dict):
    _save_json(DAILY_LOG, status)

def _get_latest_short() -> dict | None:
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
    all_log  = _load_json("upload_log.json", [])
    regulars = [v for v in all_log if v.get("type") == "regular"]
    if not regulars:
        return None
    promo_log = _load_json(PROMO_LOG, {})
    unpromoted = sorted(
        [v for v in regulars if v.get("video_id") not in promo_log],
        key=lambda x: x.get("uploaded_at", ""), reverse=True,
    )
    if unpromoted:
        return unpromoted[0]
    return min(regulars, key=lambda x: promo_log.get(x.get("video_id", ""), ""))

def _mark_regular_promoted(video_id: str):
    promo_log = _load_json(PROMO_LOG, {})
    promo_log[video_id] = datetime.datetime.utcnow().isoformat()
    _save_json(PROMO_LOG, promo_log)

def _pick_topic(offset: int = 0) -> str:
    import random
    seed = int(datetime.datetime.utcnow().strftime("%Y%m%d")) + offset
    random.seed(seed)
    return random.choice(TOPICS)


# ── Tweet generators ──────────────────────────────────────────────────────────

def _generate_short_hook(title: str) -> str:
    """
    Turn a Short video title into a curiosity-gap tweet hook.
    Bland title = 20 views. Curiosity hook = algorithm starts distributing it.
    """
    try:
        from groq import Groq
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        prompt = f"""Write ONE tweet hook for a psychology/mindset Short video titled: "{title}"

Rules:
- Under 200 characters
- Create a curiosity gap — the reader feels COMPELLED to watch the answer
- Do NOT copy the title word-for-word
- Do NOT start with "Watch:", "New:", "Check out", "In this video"
- No hashtags (they go in the reply). No emojis. No exclamation marks.
- Sounds like a smart, blunt person making an observation — not marketing

Good examples:
"Your brain physically changes shape when you learn something new — but only under one condition."
"There's a name for why you remember your worst moments more clearly than your best ones."
"The 3-second rule for stopping overthinking isn't about motivation. It's about how your brainstem fires."

Write only the hook line. Nothing else."""
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.9,
            max_tokens=80,
        )
        return resp.choices[0].message.content.strip()[:200]
    except Exception as e:
        print(f"[Twitter] Short hook generation failed: {e}")
        return title[:200]


def _generate_viral_content(tweet_count: int) -> dict:
    """
    Generate psychology content in a viral X format — rotates each run.

    Format rotation (by tweet_count mod 3):
    - 0 → THREAD (3 connected tweets — X gives 3-5x more reach to threads)
    - 1 → YES/NO (drives replies — algorithm ranks replies > likes > retweets)
    - 2 → NUMBERED or MYTH-BUSTER (highly shareable, saves get reach too)

    Returns {"format": str, "tweets": list[str], "topic": str}
    """
    import random

    fmt_slot = tweet_count % 3
    topic = _pick_topic(offset=tweet_count)

    try:
        from groq import Groq
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        if fmt_slot == 0:
            # ── THREAD ────────────────────────────────────────────────────────
            prompt = f"""Write a 3-tweet X/Twitter THREAD about: "{topic}"

TWEET 1 — Hook (under 220 chars):
- A specific, surprising observation or counter-intuitive fact
- Do NOT start with "Did you know", "Fun fact", "Thread:", numbers, or bullet points
- Feels like a blunt insight from a smart friend, not a textbook
- No hashtags

TWEET 2 — The science (under 250 chars):
- Explain the mechanism: use one specific term (e.g. "prefrontal cortex", "cortisol", "cognitive dissonance")
- Still sounds like a knowledgeable friend, not a researcher
- No hashtags

TWEET 3 — Takeaway + engagement (under 220 chars):
- ONE practical shift they can make with this information (concrete, not "just try harder")
- End with: "Drop a YES if you've felt this."
- 1-2 hashtags from: #psychology #mindset #mentalhealth #brain #selfawareness

Output ONLY in this exact format (no other text):
TWEET1: [tweet 1 text]
TWEET2: [tweet 2 text]
TWEET3: [tweet 3 text]"""
            max_tok = 300

        elif fmt_slot == 1:
            # ── YES/NO ────────────────────────────────────────────────────────
            prompt = f"""Write a "YES or NO" style tweet about: "{topic}"

Rules:
- Start with "YES or NO:" (capital)
- Describe a very specific, relatable experience most people feel but rarely admit aloud
- End with "Be honest." or "Drop your answer below."
- Under 240 chars total. No hashtags. No emojis.
- The situation should be almost painfully specific — not generic

Strong examples:
"YES or NO: You replay one embarrassing thing you said 8 years ago in vivid detail but forget what you had for dinner last night. Be honest."
"YES or NO: You feel genuinely guilty resting, even when you're sick, even when you've worked all week. Be honest."
"YES or NO: You prepare for every good thing to fall apart before it actually does, because you don't fully trust that you're allowed to keep it. Be honest."

Write only the tweet. Nothing else."""
            max_tok = 120

        else:
            # ── NUMBERED or MYTH-BUSTER (alternates) ─────────────────────────
            use_numbered = (tweet_count // 3) % 2 == 0

            if use_numbered:
                prompt = f"""Write a numbered list tweet about: "{topic}"

Rules:
- Line 1: "[3 or 4] signs/reasons/things [specific claim]:" (under 65 chars)
- Then 3-4 numbered bullet points, each under 60 chars
- Last line: 1-2 relevant hashtags
- Total under 280 chars
- Sound direct and specific — not vague life-coach platitudes
- Avoid using "just" "simply" "you need to"

Example:
"3 signs you grew up somewhere that didn't feel safe:
1. You over-explain yourself constantly
2. Silence feels threatening, not peaceful
3. You apologise before you've done anything wrong

#psychology #mentalhealth"

Write only the tweet. Nothing else."""
            else:
                prompt = f"""Write a MYTH vs REALITY tweet about: "{topic}"

Rules:
- Line 1: "MYTH: [widely held wrong belief]" (under 65 chars)
- Line 2: "REALITY: [the actual truth]" (under 70 chars)
- Line 3: One line on the science or implication (under 70 chars)
- Last line: 1-2 hashtags
- Sound confident and specific

Example:
"MYTH: Willpower is a personality trait.
REALITY: It's a finite resource that depletes with every decision made.
This is why your choices get worse as the day goes on.

#psychology #brain"

Write only the tweet. Nothing else."""
            max_tok = 180

        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.9,
            max_tokens=max_tok,
        )
        raw = resp.choices[0].message.content.strip()

        if fmt_slot == 0:
            # Parse TWEET1:/TWEET2:/TWEET3: format
            tweets = []
            for i, key in enumerate(["TWEET1:", "TWEET2:", "TWEET3:"]):
                if key in raw:
                    after = raw.split(key, 1)[1]
                    next_keys = ["TWEET2:", "TWEET3:", "TWEET4:"][i:]
                    for nk in next_keys[1:]:
                        if nk in after:
                            after = after.split(nk, 1)[0]
                    tweets.append(after.strip()[:280])
            if len(tweets) == 3:
                return {"format": "thread", "tweets": tweets, "topic": topic}
            # Fallback: treat whole output as single tweet
            return {"format": "bold", "tweets": [raw[:280]], "topic": topic}

        fmt_name = "yesno" if fmt_slot == 1 else ("numbered" if use_numbered else "mythbuster")
        return {"format": fmt_name, "tweets": [raw[:280]], "topic": topic}

    except Exception as e:
        print(f"[Twitter] Viral content generation failed: {e}")

    # Static fallbacks — one per format slot
    fallbacks = {
        0: {  # thread fallback
            "format": "thread",
            "tweets": [
                "Your brain can't tell the difference between a real threat and an imagined one.",
                "Every time you rehearse a worst-case scenario, your amygdala fires cortisol as if the event is happening right now. Your heart rate rises. Your jaw tightens. You suffer through something that hasn't occurred.",
                "The fix isn't positive thinking. It's learning to notice the signal, name it, and redirect attention deliberately.\n\nDrop a YES if you've felt this. #psychology #brain",
            ],
            "topic": topic,
        },
        1: {  # yes/no fallback
            "format": "yesno",
            "tweets": ["YES or NO: You prepare for every good thing to fall apart before it does, because somewhere deep down you don't fully trust that you're allowed to keep it. Be honest."],
            "topic": topic,
        },
        2: {  # numbered/mythbuster fallback
            "format": "numbered",
            "tweets": ["3 signs your nervous system is still stuck in survival mode:\n1. Rest feels irresponsible\n2. Good news triggers dread instead of relief\n3. You're always waiting for the other shoe to drop\n\n#psychology #mentalhealth"],
            "topic": topic,
        },
    }
    return fallbacks[fmt_slot % 3]


def _generate_reply_drops() -> list[str]:
    """
    Generate 3 short, intelligent replies you can paste on big psychology accounts' tweets.
    Their audience (100k+) sees the reply → clicks your profile → views spike.
    This is the fastest free reach strategy on X.
    """
    import random
    seed = int(datetime.datetime.utcnow().strftime("%Y%m%d")) + 77
    random.seed(seed)

    contexts = [
        "someone tweets about why changing habits is so hard",
        "someone tweets about overcoming anxiety and fear",
        "someone tweets about self-sabotage before success",
        "someone tweets about perfectionism and procrastination",
        "someone tweets about childhood trauma affecting adult life",
        "someone tweets about why self-improvement advice often fails",
        "someone tweets about morning routines and discipline",
        "someone tweets about not feeling good enough",
    ]
    context = random.choice(contexts)

    try:
        from groq import Groq
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        prompt = f"""Generate 3 intelligent Twitter replies for when {context}.

Rules for EACH reply:
- 1-2 lines only, under 200 chars
- Adds a genuinely interesting perspective the original tweet didn't cover
- Makes readers think "who is this person? I want to see more"
- Sounds like a knowledgeable, curious mind — NOT a brand or content creator
- No self-promotion. No hashtags. No emojis. No "great point!" type openers.
- Be specific, not generic

Output ONLY in this format:
REPLY1: [reply text]
REPLY2: [reply text]
REPLY3: [reply text]"""
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.85,
            max_tokens=220,
        )
        raw = resp.choices[0].message.content.strip()

        replies = []
        for i, key in enumerate(["REPLY1:", "REPLY2:", "REPLY3:"]):
            if key in raw:
                after = raw.split(key, 1)[1]
                for nk in ["REPLY2:", "REPLY3:", "REPLY4:"][i:][1:]:
                    if nk in after:
                        after = after.split(nk, 1)[0]
                r = after.strip()[:200]
                if r:
                    replies.append(r)
        if replies:
            return replies[:3]
    except Exception as e:
        print(f"[Twitter] Reply drops failed: {e}")

    return [
        "The underrated part: it's not about the behavior itself — it's about what the behavior is protecting you from.",
        "People treat this as a mindset problem. Most of the time it's a nervous system problem. The body has to learn safety before the mind can follow.",
        "The most honest sign of real progress isn't feeling better. It's being less afraid of feeling bad.",
    ]


def _generate_psychology_tweet(question_mode: bool = False) -> str:
    """Legacy fallback — used only when viral content generation is unavailable."""
    import random
    fallbacks = [
        "Your brain releases the same stress hormones for imagined threats as real ones.\nThat meeting you keep dreading? Already hurting you.\nWorry is suffering twice.\n\n#psychology #brain",
        "Procrastination is not laziness.\nIt's your nervous system avoiding a task it links to pain or failure.\nThe block is emotional, not logical.\n\n#psychology #mindset",
        "Change requires admitting the old version of you was wrong.\nThe ego resists that more than the discomfort does.\n\n#mindset #selfawareness",
        "You don't remember events accurately.\nYou remember how you felt — and reconstruct the rest.\nMemory is a story, not a recording.\n\n#psychology #brain",
        "The inner critic in your head is not yours.\nIt was someone else's voice, so long ago you forgot it ever came from outside.\n\n#psychology #mentalhealth",
    ]
    random.seed(datetime.date.today().isoformat())
    return random.choice(fallbacks)


# ── Native video upload (Shorts only) ────────────────────────────────────────

def _download_short(video_id: str, out_dir: str) -> str | None:
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
    print("[Twitter] Uploading video to X...")
    media = api.media_upload(
        filename=video_path,
        media_category="tweet_video",
        chunked=True
    )
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

    tweets_to_send = []   # list of {"label": str, "tweets": list[str], "reply": str|None}
    promo_video_id = None
    short_vid_id   = None
    errors         = []

    # ── DAILY SHORT PROMO (once per day — first run) ──────────────────────────
    if not daily["short_done"]:
        short = _get_latest_short()
        if short:
            short_vid_id = short.get("video_id", "")
            title = short.get("title", "").replace(" #Shorts", "").strip()
            hook  = _generate_short_hook(title)
            reply = f"Watch the full thing → https://youtu.be/{short_vid_id}\n\n#psychology #mindset"
            tweets_to_send.append({
                "label":  "TODAY'S SHORT",
                "tweets": [hook],
                "reply":  reply,
            })
            daily["short_done"] = True
            print(f"[Twitter] Short added: {title[:50]}")
        else:
            errors.append("No Shorts found in upload_log.json")

    # ── DAILY REGULAR VIDEO PROMO (once per day — first run) ─────────────────
    if not daily["regular_done"]:
        video = _get_next_promo_video()
        if video:
            promo_video_id = video["video_id"]
            vid_title      = video.get("title", "")
            hook           = _generate_short_hook(vid_title)
            reg_reply      = f"Full breakdown → https://youtu.be/{promo_video_id}\n\n#psychology #mindset"
            tweets_to_send.append({
                "label":  f"TODAY'S VIDEO — {vid_title[:40]}",
                "tweets": [hook],
                "reply":  reg_reply,
            })
            daily["regular_done"] = True
            print(f"[Twitter] Regular added: {vid_title[:50]}")
        else:
            errors.append("No regular videos found in upload_log.json")

    # ── VIRAL PSYCHOLOGY CONTENT (every run, 3x/day) ─────────────────────────
    content   = _generate_viral_content(tweet_count)
    fmt       = content["format"]
    fmt_labels = {
        "thread":     "PSYCHOLOGY THREAD (3 tweets — 3-5x more reach than single tweet)",
        "yesno":      "YES/NO TWEET (drives replies → boosts algorithm reach)",
        "numbered":   "NUMBERED INSIGHT (highly shareable format)",
        "mythbuster": "MYTH vs REALITY (high saves = high reach)",
        "bold":       "PSYCHOLOGY INSIGHT",
    }
    tweets_to_send.append({
        "label":  fmt_labels.get(fmt, "PSYCHOLOGY INSIGHT"),
        "tweets": content["tweets"],
        "reply":  None,
    })

    # ── REPLY DROPS (every run — paste on big accounts manually) ─────────────
    reply_drops = _generate_reply_drops()

    # ── Build email ───────────────────────────────────────────────────────────
    body_lines = [
        f"X (Twitter) — {today_str}  |  Run #{tweet_count + 1}",
        "═" * 55,
        "",
        "CRITICAL: Never paste YouTube links in tweet body — X suppresses by 60-90%.",
        "Always put links in STEP 2 (your reply to your own tweet).",
        "",
    ]

    for i, item in enumerate(tweets_to_send, 1):
        label      = item["label"]
        tw_list    = item["tweets"]
        reply_text = item["reply"]
        is_thread  = len(tw_list) > 1

        body_lines += [
            f"{'━'*55}",
            f"TWEET {i}  ·  {label}",
            f"{'━'*55}",
        ]

        if is_thread:
            body_lines += [
                "POST AS A THREAD — post tweet 1, then reply to yourself with tweets 2 and 3:",
                "",
                "TWEET 1/3 — Post this first:",
                tw_list[0],
                "",
                "TWEET 2/3 — Reply to your own tweet 1:",
                tw_list[1],
                "",
                "TWEET 3/3 — Reply to your own tweet 2:",
                tw_list[2],
            ]
        elif reply_text:
            body_lines += [
                "STEP 1 — Post this tweet:",
                tw_list[0],
                "",
                "STEP 2 — Immediately reply to YOUR OWN tweet with:",
                reply_text,
            ]
        else:
            body_lines += [
                "Post this tweet:",
                tw_list[0],
            ]
        body_lines.append("")

    # ── Reply drops section ───────────────────────────────────────────────────
    body_lines += [
        "━" * 55,
        "REPLY DROPS — paste these on tweets from big psychology accounts",
        "(Accounts with 50k+ followers: @PsychologyFacts @DailyStoic @naval @JamesClear)",
        "Their audience sees your reply → clicks your profile → your views climb.",
        "━" * 55,
        "",
    ]
    for j, drop in enumerate(reply_drops, 1):
        body_lines += [f"DROP {j}:", drop, ""]

    # ── Growth action checklist ───────────────────────────────────────────────
    body_lines += [
        "━" * 55,
        "GROWTH ACTIONS — do these right after posting (takes 3 minutes):",
        "━" * 55,
        "1. Like 5-7 recent psychology tweets in your feed",
        "   (signals active account → algorithm gives more distribution)",
        "2. Paste one Reply Drop on any big psychology post you see",
        "3. If you posted a thread: quote-tweet your own thread 2-3 hours later",
        "   with: 'Adding to this thread —' (reactivates distribution window)",
        "4. Check your last tweet — if it got ANY reply, reply back within 1 hour",
        "   (reply chains are the strongest engagement signal on X)",
        "",
        "━" * 55,
        f"Short posted today:   {'✅ YES' if daily['short_done'] else '⬜ NO — no Shorts in log'}",
        f"Regular posted today: {'✅ YES' if daily['regular_done'] else '⬜ NO — no regulars in log'}",
        f"Content format:       {fmt.upper()}",
        f"Run #{tweet_count + 1} of the day",
    ]

    body = "\n".join(body_lines)

    try:
        short_label = "Short + Regular + " if (daily["short_done"] and daily["regular_done"]) else ""
        send(body, subject=f"Agent 8 Twitter — {short_label}{fmt.upper()} | {today_str}")
        print("[Twitter] Email sent")
    except Exception as e:
        print(f"[Twitter] Email failed: {e}")
        errors.append(f"Email failed: {e}")
        print(body)

    # ── Mark & save ───────────────────────────────────────────────────────────
    if short_vid_id:
        _mark_tweeted(short_vid_id)
    if promo_video_id:
        _mark_regular_promoted(promo_video_id)
    _save_daily_status(daily)
    _increment_tweet_count()

    write_agent_report("twitter", {
        "status":               "ok" if not errors else "partial",
        "tweets_drafted":       sum(len(i["tweets"]) for i in tweets_to_send),
        "content_format":       fmt,
        "short_posted_today":   daily["short_done"],
        "regular_posted_today": daily["regular_done"],
        "short_video_id":       short_vid_id or "",
        "promo_video_id":       promo_video_id or "",
        "tweet_count":          tweet_count + 1,
        "summary": (
            f"Format: {fmt.upper()} | "
            f"Short: {'✅' if daily['short_done'] else '❌'} | "
            f"Regular: {'✅' if daily['regular_done'] else '❌'} | "
            f"Insight: ✅ | Reply drops: {len(reply_drops)}"
        ),
        "errors": errors,
    })


if __name__ == "__main__":
    main()
