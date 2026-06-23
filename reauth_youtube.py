"""
Run this once to get a new YouTube token with full read+write scope.
This lets Agent 7 auto-update video titles and tags.

Usage:
  python reauth_youtube.py
"""
import os, pickle, base64
from google_auth_oauthlib.flow import InstalledAppFlow
from config import YOUTUBE_CLIENT_SECRETS_PATH

SCOPES = ["https://www.googleapis.com/auth/youtube"]
TOKEN_FILE = "youtube_token.pickle"

# Delete old token so we force a fresh login
if os.path.exists(TOKEN_FILE):
    os.remove(TOKEN_FILE)
    print("Old token deleted.")

flow = InstalledAppFlow.from_client_secrets_file(YOUTUBE_CLIENT_SECRETS_PATH, SCOPES)
creds = flow.run_local_server(port=0)

with open(TOKEN_FILE, "wb") as f:
    pickle.dump(creds, f)

print("\n✅ New token saved to youtube_token.pickle")
print("\nNow update your GitHub Secret YOUTUBE_TOKEN with this value:\n")
with open(TOKEN_FILE, "rb") as f:
    encoded = base64.b64encode(f.read()).decode()
print(encoded)
print("\nCopy the above → GitHub repo → Settings → Secrets → YOUTUBE_TOKEN → Update")
