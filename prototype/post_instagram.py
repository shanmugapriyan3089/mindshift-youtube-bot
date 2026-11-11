"""
Cross-post story Shorts to Instagram Reels, after they go public on YouTube.

  python prototype/post_instagram.py --check    # verify the Instagram token + account
  python prototype/post_instagram.py            # post the next Short whose YouTube publish time has passed

Video source: the GitHub Release "short-<slug>" asset (<slug>.mp4) created by the story_shorts workflow.
Writes prototype/sketch_<slug>/instagram.json after a successful post. Posts at most one Reel per run.
Env: INSTAGRAM_ACCOUNT_ID, INSTAGRAM_ACCESS_TOKEN (Instagram Graph API via a Facebook Page), GITHUB_REPOSITORY.
"""
import os, sys, json, glob, time, datetime as dt
import requests

GRAPH = "https://graph.facebook.com/v21.0"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.environ.get("GITHUB_REPOSITORY", "shanmugapriyan3089/mindshift-youtube-bot")
IG_ID = os.environ.get("INSTAGRAM_ACCOUNT_ID", "").strip()
TOKEN = os.environ.get("INSTAGRAM_ACCESS_TOKEN", "").strip()
TAGS = "#psychology #psychologyfacts #socialpsychology #humanbehavior #mindset #education #reels"


def graph(method, path, **params):
    params["access_token"] = TOKEN
    r = requests.request(method, f"{GRAPH}/{path}", params=params if method == "GET" else None,
                         data=params if method != "GET" else None, timeout=60)
    j = r.json()
    if "error" in j:
        raise RuntimeError(f"{j['error'].get('type')}: {j['error'].get('message')}")
    return j


def check():
    if not IG_ID or not TOKEN:
        sys.exit("INSTAGRAM_ACCOUNT_ID / INSTAGRAM_ACCESS_TOKEN not set")
    try:
        me = graph("GET", IG_ID, fields="username,media_count")
        print(f"INSTAGRAM OK - @{me.get('username')} ({me.get('media_count')} posts)")
    except Exception as e:
        sys.exit(f"INSTAGRAM TOKEN NOT WORKING - {e}")


def caption(piece):
    story = json.load(open(os.path.join(piece, "story.json"), encoding="utf-8"))
    yt = story["youtube"]
    title = yt["title"].replace("#Shorts", "").strip()
    hook = yt["description"].split("\n\n")[0].strip()
    return (f"{title}\n\n{hook}\n\nWould YOU? Tell me below 👇\n\n"
            f"More psychology stories on YouTube: @MindShiftProductivity\n\n{TAGS}")[:2200]


def video_url(slug):
    """Public URL of the release asset (follow GitHub's redirect to the direct file URL)."""
    url = f"https://github.com/{REPO}/releases/download/short-{slug}/{slug}.mp4"
    r = requests.head(url, allow_redirects=True, timeout=60)
    if r.status_code != 200:
        raise RuntimeError(f"release asset missing: {url} ({r.status_code})")
    return r.url


def post(piece):
    slug = os.path.basename(piece).replace("sketch_", "")
    print(f"posting {slug} to Instagram")
    container = graph("POST", f"{IG_ID}/media", media_type="REELS", video_url=video_url(slug),
                      caption=caption(piece), share_to_feed="true")["id"]
    for _ in range(60):   # Instagram processes the video first (usually < 2 min)
        time.sleep(10)
        st = graph("GET", container, fields="status_code,status")
        if st["status_code"] == "FINISHED":
            break
        if st["status_code"] == "ERROR":
            raise RuntimeError(f"Instagram could not process the video: {st.get('status')}")
    else:
        raise RuntimeError("Instagram processing timed out")
    media = graph("POST", f"{IG_ID}/media_publish", creation_id=container)["id"]
    link = graph("GET", media, fields="permalink").get("permalink")
    rec = {"media_id": media, "permalink": link, "posted_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    json.dump(rec, open(os.path.join(piece, "instagram.json"), "w"), indent=2)
    print(f"posted: {link}")


def due():
    now = dt.datetime.now(dt.timezone.utc)
    out = []
    for up in sorted(glob.glob(os.path.join(ROOT, "prototype", "sketch_*", "upload.json"))):
        piece = os.path.dirname(up)
        p = json.load(open(up)).get("publish_at")
        if p and dt.datetime.fromisoformat(p.replace("Z", "+00:00")) <= now and not os.path.exists(os.path.join(piece, "instagram.json")):
            out.append((p, piece))
    return [piece for _, piece in sorted(out)]


def main():
    if "--check" in sys.argv:
        return check()
    check()
    todo = due()
    print(f"due for Instagram: {[os.path.basename(p) for p in todo]}")
    if todo:
        post(todo[0])


if __name__ == "__main__":
    main()
