"""
Agent 8: Twitter/X Auto-Poster
Auto-tweets every new video upload with hashtags.

Setup (when ready):
1. Create @MindShiftProd (or similar) Twitter account for the channel
2. Go to developer.twitter.com → Create app → Get API keys
3. Add to GitHub Secrets: TWITTER_API_KEY, TWITTER_API_SECRET,
   TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET
"""
import os, sys, json, pickle

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

CHANNEL_URL = "https://youtube.com/@mindshift-productive"


def _get_latest_upload() -> dict | None:
    log_file = "upload_log.json"
    if not os.path.exists(log_file):
        print("[Twitter] No upload_log.json found")
        return None
    with open(log_file) as f:
        log = json.load(f)
    return log[-1] if log else None


def _build_tweet(title: str, video_id: str) -> str:
    short_url = f"https://youtu.be/{video_id}"
    hashtags = "#psychology #motivation #selfimprovement #mindset #success #productivity"
    base = f"🧠 {title}\n\nWatch now: {short_url}\n\n{hashtags}"
    return base[:280]


def main():
    api_key = os.getenv("TWITTER_API_KEY")
    api_secret = os.getenv("TWITTER_API_SECRET")
    access_token = os.getenv("TWITTER_ACCESS_TOKEN")
    access_secret = os.getenv("TWITTER_ACCESS_SECRET")

    if not all([api_key, api_secret, access_token, access_secret]):
        print("[Agent 8: Twitter] Credentials not set — skipping")
        print("[Twitter] To activate: create @MindShiftProd on Twitter, get API keys,")
        print("[Twitter] then add TWITTER_API_KEY, TWITTER_API_SECRET,")
        print("[Twitter] TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET to GitHub Secrets")
        return

    latest = _get_latest_upload()
    if not latest:
        return

    tweet = _build_tweet(latest.get("title", ""), latest.get("video_id", ""))

    try:
        import tweepy
        client = tweepy.Client(
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_secret,
        )
        response = client.create_tweet(text=tweet)
        tweet_id = response.data["id"]
        tweet_url = f"https://twitter.com/i/web/status/{tweet_id}"
        print(f"[Twitter] Posted: {tweet_url}")

        from agents.notifier import send
        send(f"🐦 <b>Tweeted!</b>\n{tweet[:200]}\n{tweet_url}")

    except ImportError:
        print("[Twitter] tweepy not installed. Run: pip install tweepy")
    except Exception as e:
        print(f"[Twitter] Post failed: {e}")


if __name__ == "__main__":
    main()
