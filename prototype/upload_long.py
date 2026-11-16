"""
Upload a finished LONG video to YouTube, scheduled (private until publishAt), with chapters, thumbnail and playlist.

Usage:  python prototype/upload_long.py prototype/long_stanford 2026-11-22T12:30:00Z "<chapters text>"
Reads   <piece>/story.json ("youtube": {title, description with {chapters}, tags}), <piece>/renders/share.mp4, <piece>/thumbnail.jpg
Writes  <piece>/upload.json
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(__file__))
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from src.youtube_uploader import _get_credentials
from upload_short import add_to_playlist

PLAYLIST = "Psychology Stories (Full Length)"
PLAYLIST_DESC = ("The full story behind famous psychology experiments, 8-10 minutes, hand-drawn. "
                 "Stanford Prison Experiment, Milgram and more. What was claimed, what the archives show, what it means for you.")


def main(piece, publish_at, chapters=""):
    story = json.load(open(os.path.join(piece, "story.json"), encoding="utf-8"))
    meta = story["youtube"]
    desc = meta["description"].replace("{chapters}", chapters).strip()
    video = os.path.join(piece, "renders", "share.mp4")
    yt = build("youtube", "v3", credentials=_get_credentials())
    body = {
        "snippet": {"title": meta["title"][:100], "description": desc[:5000], "tags": meta["tags"],
                    "categoryId": "27", "defaultLanguage": "en", "defaultAudioLanguage": "en"},
        "status": {"privacyStatus": "private", "publishAt": publish_at, "selfDeclaredMadeForKids": False,
                   "containsSyntheticMedia": False},
    }
    print(f"Uploading {video} -> publishes at {publish_at}", flush=True)
    req = yt.videos().insert(part="snippet,status", body=body,
                             media_body=MediaFileUpload(video, mimetype="video/mp4", resumable=True, chunksize=8 * 1024 * 1024))
    resp, last = None, -1
    while resp is None:
        status, resp = req.next_chunk()
        if status and int(status.progress() * 100) // 10 != last:
            last = int(status.progress() * 100) // 10; print(f"  {last * 10}%", flush=True)
    vid = resp["id"]
    print(f"  uploaded: https://youtu.be/{vid}")

    thumb = os.path.join(piece, "thumbnail.jpg")
    try:   # custom thumbnails need a verified channel
        yt.thumbnails().set(videoId=vid, media_body=MediaFileUpload(thumb, mimetype="image/jpeg")).execute()
        print("  thumbnail set")
    except Exception as e:
        print(f"  thumbnail skipped ({str(e)[:100]})")

    add_to_playlist(yt, vid, PLAYLIST, PLAYLIST_DESC)
    check = yt.videos().list(part="status,snippet", id=vid).execute()["items"][0]
    rec = {"video_id": vid, "url": f"https://youtu.be/{vid}", "title": check["snippet"]["title"],
           "privacy": check["status"]["privacyStatus"], "publish_at": check["status"].get("publishAt")}
    json.dump(rec, open(os.path.join(piece, "upload.json"), "w"), indent=2)
    print(json.dumps(rec, indent=2))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "")
