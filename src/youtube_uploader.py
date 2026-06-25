"""
Upload videos to YouTube using the Data API v3.
Handles OAuth2 token caching so you only auth once.
"""
import os
import json
import pickle
import tempfile
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from config import YOUTUBE_CLIENT_SECRETS_PATH, MADE_FOR_KIDS

SCOPES = ["https://www.googleapis.com/auth/youtube"]
TOKEN_FILE = "youtube_token.pickle"


def _get_credentials():
    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as f:
            creds = pickle.load(f)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                YOUTUBE_CLIENT_SECRETS_PATH, SCOPES
            )
            # In GitHub Actions: use run_local_server=False and provide auth_code via env
            if os.getenv("GITHUB_ACTIONS"):
                auth_url, _ = flow.authorization_url(prompt="consent")
                print(f"[YouTube] Visit this URL to authorize:\n{auth_url}")
                code = os.getenv("YOUTUBE_AUTH_CODE", "")
                flow.fetch_token(code=code)
                creds = flow.credentials
            else:
                creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, "wb") as f:
            pickle.dump(creds, f)

    return creds


def _generate_srt(scenes: list, video_type: str) -> str:
    """Estimate SRT captions from script scenes at ~155 WPM. Words per caption line = 8."""
    WPM = 155
    LINE_WORDS = 8
    lines = []
    idx = 1
    t = 0.0

    def _ts(s: float) -> str:
        h = int(s // 3600)
        m = int((s % 3600) // 60)
        sec = s % 60
        return f"{h:02d}:{m:02d}:{int(sec):02d},{int((sec % 1) * 1000):03d}"

    for scene in scenes:
        words = scene.get("narration", "").split()
        if not words:
            continue
        total_dur = len(words) / WPM * 60
        chunks = [words[i:i + LINE_WORDS] for i in range(0, len(words), LINE_WORDS)]
        chunk_dur = total_dur / len(chunks)
        for chunk in chunks:
            lines += [str(idx), f"{_ts(t)} --> {_ts(t + chunk_dur)}", " ".join(chunk), ""]
            t += chunk_dur
            idx += 1
        t += 0.3  # brief inter-scene gap
    return "\n".join(lines)


def _upload_captions(youtube, video_id: str, srt_content: str):
    """Upload SRT captions to a video. Non-critical — errors are logged, not raised."""
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".srt", delete=False, encoding="utf-8") as f:
            f.write(srt_content)
            tmp = f.name
        youtube.captions().insert(
            part="snippet",
            body={"snippet": {
                "videoId": video_id, "language": "en",
                "name": "English (auto)", "isDraft": False,
            }},
            media_body=MediaFileUpload(tmp, mimetype="text/plain"),
        ).execute()
        print("  [YouTube] Captions uploaded")
        os.unlink(tmp)
    except Exception as e:
        print(f"  [YouTube] Captions skipped ({e})")


_PLAYLIST_TITLES = {
    "regular": "Psychology & Mindset | Full Episodes",
    "shorts":  "Psychology Shorts | Mind Hacks",
}


def _get_or_create_playlist(youtube, video_type: str) -> str:
    """Return playlist ID, finding existing playlist first, creating if missing."""
    title = _PLAYLIST_TITLES.get(video_type, "MindShiftProductivity")
    try:
        resp = youtube.playlists().list(part="snippet,id", mine=True, maxResults=50).execute()
        for item in resp.get("items", []):
            if item["snippet"]["title"] == title:
                return item["id"]
    except Exception:
        pass
    resp = youtube.playlists().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": f"Psychology, mindset, and self-improvement — @MindShiftProductivity",
                "defaultLanguage": "en",
            },
            "status": {"privacyStatus": "public"},
        },
    ).execute()
    print(f"  [YouTube] Playlist created: {title}")
    return resp["id"]


def _add_to_playlist(youtube, video_id: str, video_type: str):
    """Add video to the themed playlist. Non-critical."""
    try:
        playlist_id = _get_or_create_playlist(youtube, video_type)
        youtube.playlistItems().insert(
            part="snippet",
            body={"snippet": {
                "playlistId": playlist_id,
                "resourceId": {"kind": "youtube#video", "videoId": video_id},
            }},
        ).execute()
        print(f"  [YouTube] Added to playlist: {_PLAYLIST_TITLES.get(video_type)}")
    except Exception as e:
        print(f"  [YouTube] Playlist add skipped ({e})")


def upload_video(
    video_path: str,
    thumbnail_path: str,
    title: str,
    description: str,
    tags: list,
    video_type: str = "regular",
    scenes: list = None,
) -> str:
    """Upload video, set thumbnail, upload captions, add to playlist. Returns video ID."""
    creds = _get_credentials()
    youtube = build("youtube", "v3", credentials=creds)

    is_short = video_type == "shorts"
    if is_short and "#Shorts" not in title:
        title = title + " #Shorts"

    body = {
        "snippet": {
            "title": title[:100],
            "description": description[:5000],
            "tags": tags[:500],
            "categoryId": "27",   # Education — correct niche signal for psychology/motivation
            "defaultLanguage": "en",
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": MADE_FOR_KIDS,
            "madeForKids": MADE_FOR_KIDS,
        },
    }

    media = MediaFileUpload(video_path, mimetype="video/mp4", resumable=True, chunksize=1024 * 1024 * 5)

    print(f"  [YouTube] Uploading: {title}")
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"  [YouTube] Upload progress: {int(status.progress() * 100)}%")

    video_id = response["id"]
    print(f"  [YouTube] Uploaded: https://youtube.com/watch?v={video_id}")

    # Set thumbnail (requires verified channel)
    if os.path.exists(thumbnail_path):
        try:
            youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(thumbnail_path, mimetype="image/jpeg"),
            ).execute()
            print("  [YouTube] Thumbnail set")
        except Exception as e:
            print(f"  [YouTube] Thumbnail skipped (verify at youtube.com/verify): {e}")

    # Upload SRT captions
    if scenes:
        srt = _generate_srt(scenes, video_type)
        _upload_captions(youtube, video_id, srt)

    # Add to themed playlist (drives session time)
    _add_to_playlist(youtube, video_id, video_type)

    return video_id


def save_upload_log(video_id: str, title: str, topic: str, video_type: str, log_file: str = "upload_log.json"):
    """Append upload record to log file."""
    from datetime import datetime
    record = {
        "video_id": video_id,
        "title": title,
        "topic": topic,
        "type": video_type,
        "url": f"https://youtube.com/watch?v={video_id}",
        "uploaded_at": datetime.utcnow().isoformat(),
    }
    log = []
    if os.path.exists(log_file):
        with open(log_file) as f:
            log = json.load(f)
    log.append(record)
    with open(log_file, "w") as f:
        json.dump(log, f, indent=2)
