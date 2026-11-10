"""
Get a fresh YouTube token and push it to the YOUTUBE_TOKEN GitHub secret.

Usage:
  python reauth_youtube.py

If tokens die every 7 days, the OAuth app is in "Testing" mode. Fix once:
  Google Cloud Console > Google Auth Platform > Audience > Publish app
then run this script one more time.
"""
import os, pickle, base64, shutil, subprocess
from google_auth_oauthlib.flow import InstalledAppFlow
from config import YOUTUBE_CLIENT_SECRETS_PATH

SCOPES = ["https://www.googleapis.com/auth/youtube"]
TOKEN_FILE = "youtube_token.pickle"

# Delete old token so we force a fresh login
if os.path.exists(TOKEN_FILE):
    os.remove(TOKEN_FILE)
    print("Old token deleted.")

flow = InstalledAppFlow.from_client_secrets_file(YOUTUBE_CLIENT_SECRETS_PATH, SCOPES)
# prompt=consent guarantees Google returns a refresh token
creds = flow.run_local_server(port=0, prompt="consent", access_type="offline")

with open(TOKEN_FILE, "wb") as f:
    pickle.dump(creds, f)
print("\n✅ New token saved to youtube_token.pickle")

with open(TOKEN_FILE, "rb") as f:
    encoded = base64.b64encode(f.read()).decode()

# Push straight to GitHub if the gh CLI is installed + logged in
if shutil.which("gh"):
    r = subprocess.run(["gh", "secret", "set", "YOUTUBE_TOKEN"], input=encoded, text=True)
    if r.returncode == 0:
        print("✅ GitHub secret YOUTUBE_TOKEN updated — done.")
        raise SystemExit(0)
    print("⚠️  gh secret set failed — falling back to manual paste.")

# Manual fallback: copy to clipboard (token is never printed)
try:
    subprocess.run("clip" if os.name == "nt" else ["pbcopy"], input=encoded, text=True, check=True)
    print("📋 Token copied to clipboard.")
except Exception:
    with open("youtube_token_b64.txt", "w") as f:
        f.write(encoded)
    print("📄 Token written to youtube_token_b64.txt (delete after use, never commit).")
print("Paste it at: GitHub repo > Settings > Secrets and variables > Actions > YOUTUBE_TOKEN > Update")
