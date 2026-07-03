"""
Agent 4: Revenue Tracker (runs every Sunday)
Estimates earnings based on views × RPM, tracks YPP progress with detailed milestones
→ sends weekly "money report" to Telegram
"""
import os, sys, pickle
from datetime import datetime
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

TOKEN_FILE = "youtube_token.pickle"
CHANNEL_ID = "UCZSdar2nKSxkxX3b5vgYGIg"

# Conservative RPM estimates for psychology/motivation niche
RPM_LOW = 3.0    # $3 (India/developing-country audience heavy)
RPM_MID = 6.0    # $6 (mixed audience)
RPM_HIGH = 12.0  # $12 (US/UK heavy, once channel grows)
AVG_WATCH_MIN = 3.5  # estimated minutes watched per view


def _get_youtube():
    with open(TOKEN_FILE, "rb") as f:
        creds = pickle.load(f)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return build("youtube", "v3", credentials=creds)


def _bar(pct: float, width: int = 12) -> str:
    filled = int(min(pct, 100) / 100 * width)
    return "█" * filled + "░" * (width - filled)


def main():
    from agents.notifier import send

    print("[Agent 4: Revenue Tracker] Generating weekly revenue report...")
    youtube = _get_youtube()

    result = youtube.channels().list(part="statistics", id=CHANNEL_ID).execute()
    if not result["items"]:
        send("⚠️ Revenue Tracker: Could not get channel stats")
        return

    s = result["items"][0]["statistics"]
    subs = int(s.get("subscriberCount", 0))
    total_views = int(s.get("viewCount", 0))
    video_count = int(s.get("videoCount", 0))

    est_watch_hours = (total_views * AVG_WATCH_MIN) / 60
    earnings_low = (total_views / 1000) * RPM_LOW
    earnings_mid = (total_views / 1000) * RPM_MID
    earnings_high = (total_views / 1000) * RPM_HIGH

    subs_pct = min(100, (subs / 1000) * 100)
    watch_pct = min(100, (est_watch_hours / 4000) * 100)

    views_per_vid = total_views / max(video_count, 1)
    subs_per_vid = subs / max(video_count, 1)
    # At 10 videos/week pace
    videos_to_subs = max(0, (1000 - subs) / max(subs_per_vid, 0.01))
    videos_to_watch = max(0, (4000 - est_watch_hours) / max((views_per_vid * AVG_WATCH_MIN / 60), 0.01))
    videos_needed = max(videos_to_subs, videos_to_watch)
    weeks_to_ypp = videos_needed / 10  # 10 videos/week

    if subs >= 1000 and est_watch_hours >= 4000:
        ypp_msg = "🎉 <b>YOU QUALIFY FOR MONETIZATION!</b>\nGo to YouTube Studio → Earn → Apply now!"
        monthly_est = f"${(total_views/video_count/1000*RPM_MID*30):.0f}–${(total_views/video_count/1000*RPM_HIGH*30):.0f}/month"
    else:
        ypp_msg = f"⏳ ~<b>{weeks_to_ypp:.0f} weeks</b> at current posting rate (10 videos/week)"
        # Show realistic projection assuming 1000 views/video once channel grows
        monthly_est = f"${int(1000 * 30 * RPM_MID / 1000)}–${int(1000 * 30 * RPM_HIGH / 1000)}/month (at 1K views/video after YPP)"

    from agents.notifier import write_agent_report
    write_agent_report("revenue_tracker", {
        "status":           "ok",
        "subscribers":      subs,
        "total_views":      total_views,
        "est_watch_hours":  round(est_watch_hours, 1),
        "earnings_mid_usd": round(earnings_mid, 2),
        "ypp_subs_pct":     round(subs_pct, 1),
        "ypp_watch_pct":    round(watch_pct, 1),
        "weeks_to_ypp":     round(weeks_to_ypp, 1),
        "summary":          f"{subs:,} subs ({subs_pct:.0f}% to YPP), ${earnings_mid:.2f} earned so far, ~{weeks_to_ypp:.0f} weeks to monetization",
        "errors":           [],
    })

    send(f"""💰 <b>Agent 4: Weekly Revenue Report</b>
{datetime.now().strftime('%B %d, %Y')}

━━━ 💵 EARNINGS ESTIMATE ━━━
Total Views: <b>{total_views:,}</b>
Conservative (${RPM_LOW} RPM): <b>${earnings_low:.2f}</b>
Realistic (${RPM_MID} RPM): <b>${earnings_mid:.2f}</b>
Optimistic (${RPM_HIGH} RPM): <b>${earnings_high:.2f}</b>

Monthly after monetization: <b>{monthly_est}</b>

━━━ 🎯 YPP PROGRESS ━━━
👥 Subscribers: <b>{subs:,} / 1,000</b>
{_bar(subs_pct)} {subs_pct:.0f}%

⏱ Watch Hours: <b>{est_watch_hours:,.0f} / 4,000</b>
{_bar(watch_pct)} {watch_pct:.0f}%

🎬 Videos uploaded: <b>{video_count}</b>
📊 Avg views/video: <b>{views_per_vid:,.0f}</b>

━━━ 🚀 TIME TO MONEY ━━━
{ypp_msg}

💡 <b>Tip:</b> Share videos on WhatsApp groups daily to boost views!""")


if __name__ == "__main__":
    main()
