"""
Agent 8: Twitter/X Auto-Poster
Auto-tweets every new video upload with hashtags.
Tracks posted videos so the same video is never tweeted twice.

Setup:
1. Create a Twitter/X account for the channel (@MindShiftProd or similar)
2. Go to developer.twitter.com → Create app (need Elevated access for v2 write)
3. Add to GitHub Secrets:
   TWITTER_API_KEY, TWITTER_API_SECRET,
   TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET
"""
import os, sys, json

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

CHANNEL_URL = "https://youtube.com/@MindShiftProductivity"
TWEET_LOG = "tweet_log.json"


def _load_tweet_log() -> set:
    if not os.path.exists(TWEET_LOG):
        return set()
    try:
        with open(TWEET_LOG) as f:
            return set(json.load(f))
    except Exception:
        return set()


def _save_tweet_log(tweeted_ids: set):
    with open(TWEET_LOG, "w") as f:
        json.dump(list(tweeted_ids), f)


def _get_unposted_uploads() -> list:
    log_file = "upload_log.json"
    if not os.path.exists(log_file):
        print("[Twitter] No upload_log.json found")
        return []
    try:
        with open(log_file) as f:
            log = json.load(f)
    except Exception:
        return []

    tweeted = _load_tweet_log()
    return [v for v in log if v.get("video_id") not in tweeted]


def _build_tweet(title: str, video_id: str, video_type: str) -> str:
    short_url = f"https://youtu.be/{video_id}"

    if video_type == "shorts":
        # Shorts tweet: punchy hook + link + watch CTA
        # Strip "#Shorts" suffix from title for cleaner tweet
        clean_title = title.replace(" #Shorts", "").replace("#Shorts", "").strip()
        hook = clean_title[:100]
        tweet = (
            f"🧠 {hook}\n\n"
            f"Watch → {short_url}\n\n"
            f"#psychology #mindset #selfimprovement #Shorts #motivation"
        )
    else:
        # Regular video: 3-line hook format
        tweet = (
            f"🔥 {title[:90]}\n\n"
            f"Most people never learn this. Full breakdown:\n"
            f"{short_url}\n\n"
            f"#psychology #motivation #selfimprovement #mindset #success #productivity"
        )

    return tweet[:280]


def main():
    api_key      = os.getenv("TWITTER_API_KEY")
    api_secret   = os.getenv("TWITTER_API_SECRET")
    access_token = os.getenv("TWITTER_ACCESS_TOKEN")
    access_secret = os.getenv("TWITTER_ACCESS_SECRET")

    if not all([api_key, api_secret, access_token, access_secret]):
        print("[Agent 8: Twitter] Credentials not set — skipping")
        print("[Twitter] Add TWITTER_API_KEY, TWITTER_API_SECRET,")
        print("[Twitter] TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET to GitHub Secrets")
        return

    unposted = _get_unposted_uploads()
    if not unposted:
        print("[Twitter] No new uploads to tweet — all caught up")
        return

    print(f"[Twitter] {len(unposted)} new video(s) to tweet")

    try:
        import tweepy
    except ImportError:
        print("[Twitter] tweepy not installed. Run: pip install tweepy")
        return

    client = tweepy.Client(
        consumer_key=api_key,
        consumer_secret=api_secret,
        access_token=access_token,
        access_token_secret=access_secret,
    )

    tweeted_ids = _load_tweet_log()
    posted_this_run = []

    for upload in unposted:
        title    = upload.get("title", "")
        video_id = upload.get("video_id", "")
        vtype    = upload.get("type", "regular")
        tweet    = _build_tweet(title, video_id, vtype)

        try:
            response = client.create_tweet(text=tweet)
            tweet_id  = response.data["id"]
            tweet_url = f"https://twitter.com/i/web/status/{tweet_id}"
            print(f"[Twitter] Posted ({vtype}): {tweet_url}")
            tweeted_ids.add(video_id)
            posted_this_run.append((tweet[:120], tweet_url))
        except Exception as e:
            print(f"[Twitter] Post failed for {video_id}: {e}")

    _save_tweet_log(tweeted_ids)

    if posted_this_run:
        from agents.notifier import send
        lines = "\n".join(
            f"🐦 <a href='{url}'>{text}...</a>"
            for text, url in posted_this_run
        )
        send(f"🐦 <b>Agent 8: Twitter Posted</b>\n{lines}",
             subject="Agent 8: Tweeted")


if __name__ == "__main__":
    main()
