"""
One-time Instagram setup: turns a short-lived Meta token into a NEVER-EXPIRING Page token,
finds the Instagram business account, and stores both as GitHub secrets.

Put these three lines in .env (from developers.facebook.com), then run:  python prototype/instagram_setup.py
  META_APP_ID=...
  META_APP_SECRET=...
  META_USER_TOKEN=...   (Graph API Explorer token with instagram_basic, instagram_content_publish,
                         pages_show_list, pages_read_engagement, business_management)
"""
import os, sys, json, base64, subprocess, urllib.request
import requests
from dotenv import dotenv_values

GRAPH = "https://graph.facebook.com/v21.0"
REPO = "shanmugapriyan3089/mindshift-youtube-bot"


def g(path, **params):
    j = requests.get(f"{GRAPH}/{path}", params=params, timeout=60).json()
    if "error" in j:
        sys.exit(f"Meta API error on {path}: {j['error'].get('message')}")
    return j


def set_github_secret(name, value):
    from nacl import encoding, public
    tok = subprocess.run(["git", "credential", "fill"], input="protocol=https\nhost=github.com\n\n", capture_output=True, text=True,
                         env={**os.environ, "GCM_INTERACTIVE": "always", "GIT_TERMINAL_PROMPT": "1"}).stdout
    tok = [l.split("=", 1)[1] for l in tok.splitlines() if l.startswith("password=")][0]
    H = {"Authorization": "Bearer " + tok, "Accept": "application/vnd.github+json", "User-Agent": "mindshift-setup"}
    key = json.load(urllib.request.urlopen(urllib.request.Request(f"https://api.github.com/repos/{REPO}/actions/secrets/public-key", headers=H)))
    sealed = public.SealedBox(public.PublicKey(key["key"].encode(), encoding.Base64Encoder())).encrypt(value.encode())
    body = json.dumps({"encrypted_value": base64.b64encode(sealed).decode(), "key_id": key["key_id"]}).encode()
    urllib.request.urlopen(urllib.request.Request(f"https://api.github.com/repos/{REPO}/actions/secrets/{name}", data=body, method="PUT",
                                                  headers={**H, "Content-Type": "application/json"}))
    print(f"  GitHub secret {name} saved")


def main():
    env = dotenv_values(".env")
    app_id, secret, short = (env.get(k, "").strip() for k in ("META_APP_ID", "META_APP_SECRET", "META_USER_TOKEN"))
    if not (app_id and secret and short):
        sys.exit("Add META_APP_ID, META_APP_SECRET and META_USER_TOKEN to .env first.")
    long_user = g("oauth/access_token", grant_type="fb_exchange_token", client_id=app_id, client_secret=secret,
                  fb_exchange_token=short)["access_token"]
    print("  long-lived user token: ok")
    pages = g("me/accounts", access_token=long_user, fields="id,name,access_token,instagram_business_account").get("data", [])
    linked = [p for p in pages if p.get("instagram_business_account")]
    if not linked:
        names = ", ".join(p["name"] for p in pages) or "none"
        sys.exit(f"No Facebook Page with a linked Instagram professional account (pages found: {names}).")
    page = linked[0]
    ig_id, page_token = page["instagram_business_account"]["id"], page["access_token"]
    info = g("debug_token", input_token=page_token, access_token=f"{app_id}|{secret}")["data"]
    expires = "never" if not info.get("expires_at") else info["expires_at"]
    me = g(ig_id, fields="username", access_token=page_token)
    print(f"  page: {page['name']} | instagram: @{me['username']} | token expires: {expires}")
    set_github_secret("INSTAGRAM_ACCOUNT_ID", ig_id)
    set_github_secret("INSTAGRAM_ACCESS_TOKEN", page_token)
    print("Done. Instagram cross-posting is ready.")


if __name__ == "__main__":
    main()
