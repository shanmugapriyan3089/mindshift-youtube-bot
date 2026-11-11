"""
Upload a finished sketchbook Short to YouTube, scheduled (private until publishAt), with exact captions.

Usage:  python prototype/upload_short.py prototype/sketch_milgram 2026-11-11T13:30:00Z
Reads   <piece>/story.json  ("youtube": {title, description, tags}), <piece>/timing.json (word times),
        <piece>/renders/share.mp4
Writes  <piece>/upload.json (video id, url, publish time)
"""
import os, sys, json, pickle, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from src.youtube_uploader import _get_credentials


def srt_from_words(words, max_words=6):
    """Caption cues from word timings: break on punctuation or every max_words."""
    def ts(t):
        h, r = divmod(t, 3600); m, s = divmod(r, 60)
        return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int((s % 1) * 1000):03d}"
    cues, cur = [], []
    for w in words:
        cur.append(w)
        if len(cur) >= max_words or w["text"][-1:] in ".,?!:":
            cues.append(cur); cur = []
    if cur: cues.append(cur)
    out = []
    for i, c in enumerate(cues, 1):
        end = c[-1]["end"] + 0.15
        if i < len(cues): end = min(end, cues[i][0]["start"])
        out += [str(i), f"{ts(c[0]['start'])} --> {ts(end)}", " ".join(w["text"] for w in c), ""]
    return "\n".join(out)


def main(piece, publish_at):
    story = json.load(open(os.path.join(piece, "story.json"), encoding="utf-8"))
    meta = story["youtube"]
    words = json.load(open(os.path.join(piece, "timing.json")))["words"]
    video = os.path.join(piece, "renders", "share.mp4")
    yt = build("youtube", "v3", credentials=_get_credentials())

    body = {
        "snippet": {"title": meta["title"][:100], "description": meta["description"][:5000],
                    "tags": meta["tags"], "categoryId": "27", "defaultLanguage": "en", "defaultAudioLanguage": "en"},
        "status": {"privacyStatus": "private", "publishAt": publish_at, "selfDeclaredMadeForKids": False,
                   "containsSyntheticMedia": False},   # hand-drawn animation, not realistic footage
    }
    print(f"Uploading {video} -> publishes at {publish_at}")
    req = yt.videos().insert(part="snippet,status", body=body,
                             media_body=MediaFileUpload(video, mimetype="video/mp4", resumable=True, chunksize=5 * 1024 * 1024))
    resp = None
    while resp is None:
        status, resp = req.next_chunk()
        if status: print(f"  {int(status.progress() * 100)}%")
    vid = resp["id"]
    print(f"  uploaded: https://youtube.com/shorts/{vid}")

    with tempfile.NamedTemporaryFile("w", suffix=".srt", delete=False, encoding="utf-8") as f:
        f.write(srt_from_words(words)); srt = f.name
    try:   # needs the youtube.force-ssl scope; captions are burned into the video anyway
        yt.captions().insert(part="snippet", body={"snippet": {"videoId": vid, "language": "en", "name": "English", "isDraft": False}},
                             media_body=MediaFileUpload(srt, mimetype="application/x-subrip")).execute()
        print("  captions uploaded")
    except Exception as e:
        print(f"  captions skipped ({str(e)[:80]})")
    os.unlink(srt)

    check = yt.videos().list(part="status,snippet", id=vid).execute()["items"][0]
    rec = {"video_id": vid, "url": f"https://youtube.com/shorts/{vid}", "title": check["snippet"]["title"],
           "privacy": check["status"]["privacyStatus"], "publish_at": check["status"].get("publishAt")}
    json.dump(rec, open(os.path.join(piece, "upload.json"), "w"), indent=2)
    print(json.dumps(rec, indent=2))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
