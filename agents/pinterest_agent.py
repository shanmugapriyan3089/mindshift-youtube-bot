"""
Agent 9: Pinterest Auto-Pinner
Creates Pinterest pins for each video — Pinterest drives evergreen traffic for months/years.

Setup (when ready):
1. Create Pinterest business account for MindShift Productivity
2. Go to developers.pinterest.com → Create app → Get access token
3. Create a board "Psychology & Motivation Tips" → get board ID
4. Add to GitHub Secrets: PINTEREST_ACCESS_TOKEN, PINTEREST_BOARD_ID
"""
import os, sys, json, requests

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


def _get_latest_upload() -> dict | None:
    log_file = "upload_log.json"
    if not os.path.exists(log_file):
        print("[Pinterest] No upload_log.json found")
        return None
    with open(log_file) as f:
        log = json.load(f)
    return log[-1] if log else None


def _create_pin(video_id: str, title: str, topic: str, access_token: str, board_id: str):
    description = (
        f"{topic}\n\nFull video: https://youtu.be/{video_id}\n\n"
        "Follow MindShift Productivity for daily psychology and self-improvement tips. "
        "#psychology #selfimprovement #motivation #mindset #success #productivity #habits"
    )
    pin_data = {
        "title": title[:100],
        "description": description[:500],
        "link": f"https://youtu.be/{video_id}",
        "board_id": board_id,
        "media_source": {
            "source_type": "url",
            "url": f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg",
        },
    }
    resp = requests.post(
        "https://api.pinterest.com/v5/pins",
        headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"},
        json=pin_data,
        timeout=30,
    )
    if resp.status_code == 201:
        pin_id = resp.json().get("id", "")
        print(f"[Pinterest] Pin created: https://www.pinterest.com/pin/{pin_id}/")
        from agents.notifier import send
        send(f"📌 <b>Pinterest pin created!</b>\n{title}\nhttps://www.pinterest.com/pin/{pin_id}/")
    else:
        print(f"[Pinterest] Error {resp.status_code}: {resp.text[:200]}")


def main():
    access_token = os.getenv("PINTEREST_ACCESS_TOKEN")
    board_id = os.getenv("PINTEREST_BOARD_ID")

    if not access_token or not board_id:
        print("[Agent 9: Pinterest] Credentials not set — skipping")
        print("[Pinterest] To activate:")
        print("[Pinterest]   1. Create Pinterest business account")
        print("[Pinterest]   2. Go to developers.pinterest.com → Create app")
        print("[Pinterest]   3. Add PINTEREST_ACCESS_TOKEN + PINTEREST_BOARD_ID to GitHub Secrets")
        return

    latest = _get_latest_upload()
    if not latest:
        return

    _create_pin(
        video_id=latest.get("video_id", ""),
        title=latest.get("title", ""),
        topic=latest.get("topic", latest.get("title", "")),
        access_token=access_token,
        board_id=board_id,
    )


if __name__ == "__main__":
    main()
