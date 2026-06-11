"""
Upload videos to YouTube using the Data API v3.
Handles OAuth2 token caching so you only auth once.
"""
import os
import json
import pickle
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from config import YOUTUBE_CLIENT_SECRETS_PATH, MADE_FOR_KIDS

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
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


def upload_video(
    video_path: str,
    thumbnail_path: str,
    title: str,
    description: str,
    tags: list,
    video_type: str = "regular",
) -> str:
    """Upload video, set thumbnail, return YouTube video ID."""
    creds = _get_credentials()
    youtube = build("youtube", "v3", credentials=creds)

    category_id = "20"  # Gaming=20, Education=27, Entertainment=24 — kids channels use 20 or 24
    is_short = video_type == "shorts"

    # YouTube Shorts: add #Shorts to title if not already there
    if is_short and "#Shorts" not in title:
        title = title + " #Shorts"

    body = {
        "snippet": {
            "title": title[:100],
            "description": description[:5000],
            "tags": tags[:500],
            "categoryId": category_id,
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
            pct = int(status.progress() * 100)
            print(f"  [YouTube] Upload progress: {pct}%")

    video_id = response["id"]
    print(f"  [YouTube] Uploaded: https://youtube.com/watch?v={video_id}")

    # Set thumbnail
    if os.path.exists(thumbnail_path):
        youtube.thumbnails().set(
            videoId=video_id,
            media_body=MediaFileUpload(thumbnail_path, mimetype="image/jpeg")
        ).execute()
        print(f"  [YouTube] Thumbnail set")

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
