"""
MindShift Productivity — Channel Dashboard
Reads head_agent_report.json + log files from GitHub repo → displays live channel health.
Deploy free on Streamlit Community Cloud: https://share.streamlit.io
"""
import streamlit as st
import requests, json, hashlib
from datetime import datetime, timezone, timedelta

# ── Config ────────────────────────────────────────────────────────────────────
REPO_OWNER = "shanmugapriyan3089"
REPO_NAME  = "mindshift-youtube-bot"
BRANCH     = "main"
CHANNEL_URL = "https://youtube.com/@MindShiftProductivity"

st.set_page_config(
    page_title="MindShift Dashboard",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ── Auth ──────────────────────────────────────────────────────────────────────

def _check_password() -> bool:
    stored = st.secrets.get("DASHBOARD_PASSWORD", "mindshift2026")
    if st.session_state.get("authenticated"):
        return True
    with st.container():
        st.title("🧠 MindShift Dashboard")
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 1.5, 1])
        with col2:
            password = st.text_input("Password", type="password", key="pw_input",
                                      placeholder="Enter dashboard password")
            if st.button("Login", use_container_width=True):
                if hashlib.sha256(password.encode()).hexdigest() == \
                   hashlib.sha256(stored.encode()).hexdigest():
                    st.session_state["authenticated"] = True
                    st.rerun()
                else:
                    st.error("Wrong password")
    return False


# ── Data Loading ──────────────────────────────────────────────────────────────

@st.cache_data(ttl=300)  # cache 5 minutes
def _fetch(filename: str) -> dict | list | None:
    """Fetch a JSON file from the GitHub repo (always latest committed version)."""
    token = st.secrets.get("GITHUB_TOKEN", "")
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    # Try raw content first (public repo, no auth needed)
    url = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/{BRANCH}/{filename}"
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.ok:
            return r.json()
    except Exception:
        pass

    # Fall back to GitHub API (works for private repos with token)
    if token:
        api_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{filename}"
        try:
            r = requests.get(api_url, headers=headers, timeout=10)
            if r.ok:
                import base64
                content = base64.b64decode(r.json()["content"]).decode()
                return json.loads(content)
        except Exception:
            pass
    return None


def _time_ago(iso_str: str) -> str:
    if not iso_str:
        return "never"
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        delta = datetime.now(timezone.utc) - dt
        hours = int(delta.total_seconds() / 3600)
        if hours < 1:
            return "< 1h ago"
        if hours < 24:
            return f"{hours}h ago"
        return f"{hours // 24}d ago"
    except Exception:
        return iso_str[:10]


def _status_badge(conclusion: str) -> str:
    mapping = {
        "success":     "🟢 OK",
        "failure":     "🔴 FAILED",
        "in_progress": "🟡 Running",
        "cancelled":   "⚪ Cancelled",
        "skipped":     "⚪ Skipped",
        "timed_out":   "🔴 Timed out",
        "never_run":   "⚫ Never run",
        "error":       "🔴 Error",
    }
    for key, badge in mapping.items():
        if key in str(conclusion).lower():
            return badge
    return f"❓ {conclusion}"


# ── Pages ─────────────────────────────────────────────────────────────────────

def page_overview(report: dict, upload_log: list):
    st.header("📊 Channel Overview")

    analysis = report.get("analysis", {})
    ch_stats  = report.get("channel_stats", {})
    health    = report.get("agent_health_summary", {})
    score     = analysis.get("channel_health_score", 0)

    # Top metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Health Score",   f"{score}/10")
    col2.metric("Subscribers",    f"{ch_stats.get('subscribers', 0):,}" if ch_stats.get('subscribers') else "—")
    col3.metric("Total Views",    f"{ch_stats.get('total_views', 0):,}"  if ch_stats.get('total_views')  else "—")
    col4.metric("Agents Healthy", f"{health.get('healthy',0)}/{health.get('total',0)}")
    col5.metric("Videos Uploaded", report.get("upload_stats", {}).get("total_uploaded", 0))

    st.markdown("---")

    # Recent uploads
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("🎬 Last Regular Video")
        last_reg = report.get("upload_stats", {}).get("last_regular")
        if last_reg:
            st.markdown(f"**{last_reg.get('title','—')}**")
            st.caption(f"Uploaded: {_time_ago(last_reg.get('uploaded_at',''))}")
            st.markdown(f"[Watch on YouTube]({last_reg.get('url', CHANNEL_URL)})")
        else:
            st.info("No regular video uploaded yet")

    with col_b:
        st.subheader("⚡ Last Short")
        last_short = report.get("upload_stats", {}).get("last_short")
        if last_short:
            st.markdown(f"**{last_short.get('title','—')}**")
            st.caption(f"Uploaded: {_time_ago(last_short.get('uploaded_at',''))}")
            st.markdown(f"[Watch on YouTube]({last_short.get('url', CHANNEL_URL)})")
        else:
            st.info("No Short uploaded yet")

    st.markdown("---")

    # Urgent actions
    urgent = analysis.get("urgent_actions", [])
    if urgent:
        st.subheader("🚨 Urgent Actions")
        for action in urgent:
            st.error(f"• {action}")
        st.markdown("---")

    # Top recommendations
    col_x, col_y = st.columns(2)
    with col_x:
        st.subheader("✅ What's Working")
        for item in analysis.get("what_is_working", []):
            st.success(f"• {item}")

    with col_y:
        st.subheader("🔧 Needs Improvement")
        for item in analysis.get("what_needs_improvement", []):
            st.warning(f"• {item}")

    st.markdown("---")
    st.caption(f"Report generated: {_time_ago(report.get('generated_at',''))} | [YouTube Channel]({CHANNEL_URL})")


def page_agents(report: dict):
    st.header("🤖 Agent Monitor")

    statuses = report.get("agent_statuses", {})
    fixes    = report.get("agent_improvement_tips", {})
    health   = report.get("agent_health_summary", {})

    failed = health.get("failed", 0)
    if failed == 0:
        st.success(f"All {health.get('total',0)} agents healthy ✅")
    else:
        st.error(f"{failed} agent(s) need attention")

    st.markdown("---")

    rows = []
    for name, s in statuses.items():
        rows.append({
            "Agent":      name,
            "Status":     _status_badge(s.get("conclusion", "")),
            "Last Run":   _time_ago(s.get("last_run_at", "")),
            "Fix / Note": fixes.get(name, "—"),
        })

    # Separate into healthy and broken
    broken  = [r for r in rows if "🔴" in r["Status"] or "❓" in r["Status"]]
    healthy = [r for r in rows if r not in broken]

    if broken:
        st.subheader("🔴 Needs Attention")
        for row in broken:
            with st.expander(f"{row['Status']} — {row['Agent']} (last run: {row['Last Run']})"):
                st.markdown(f"**AI Suggestion:** {row['Fix / Note']}")
                agent_name = statuses.get(row['Agent'], {})
                if agent_name.get("run_url"):
                    st.markdown(f"[View GitHub Actions Run]({agent_name['run_url']})")

    st.subheader("🟢 Healthy Agents")
    for row in healthy:
        st.markdown(f"**{row['Status']} {row['Agent']}** — last run: {row['Last Run']}")


def page_videos(report: dict, upload_log: list):
    st.header("🎬 Videos & Analytics")

    video_stats = report.get("video_stats", [])

    if video_stats:
        st.subheader("Video Performance (from YouTube API)")
        sorted_vids = sorted(video_stats, key=lambda x: x.get("views", 0), reverse=True)

        col1, col2, col3 = st.columns(3)
        total_views = sum(v.get("views", 0) for v in video_stats)
        total_likes = sum(v.get("likes", 0) for v in video_stats)
        col1.metric("Total Views (tracked)", f"{total_views:,}")
        col2.metric("Total Likes",           f"{total_likes:,}")
        col3.metric("Avg Views/Video",       f"{total_views // max(len(video_stats),1):,}")

        st.markdown("---")

        # Top videos bar chart
        try:
            import plotly.graph_objects as go
            top10 = sorted_vids[:10]
            titles = [v["title"][:40] + "…" if len(v["title"]) > 40 else v["title"] for v in top10]
            views  = [v["views"] for v in top10]
            fig = go.Figure(go.Bar(x=views, y=titles, orientation="h",
                                   marker_color="#6C63FF"))
            fig.update_layout(title="Top 10 Videos by Views", height=400,
                               xaxis_title="Views", yaxis_title="",
                               plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                               font_color="#FAFAFA")
            st.plotly_chart(fig, use_container_width=True)
        except ImportError:
            pass

        st.subheader("All Tracked Videos")
        for v in sorted_vids:
            st.markdown(
                f"**[{v['title']}]({v.get('url','#')})** — "
                f"{v.get('views',0):,} views · {v.get('likes',0)} likes · {v.get('comments',0)} comments"
            )

    elif upload_log:
        st.info("YouTube API stats not configured — showing upload log only. Add YOUTUBE_API_KEY to head agent secrets for live view counts.")
        st.subheader("Uploaded Videos")
        for v in reversed(upload_log[-20:]):
            icon = "⚡" if v.get("type") == "shorts" else "🎬"
            url  = v.get("url", f"https://youtu.be/{v.get('video_id','')}")
            st.markdown(f"{icon} **[{v.get('title','—')}]({url})** — {_time_ago(v.get('uploaded_at',''))}")

    else:
        st.warning("No video data available yet.")


def page_competitors(report: dict):
    st.header("🕵️ Competitor Analysis")

    competitors = report.get("competitors", [])
    ch_stats    = report.get("channel_stats", {})
    our_subs    = ch_stats.get("subscribers", 0)
    analysis    = report.get("analysis", {})

    if competitors:
        # Sort by subscribers
        all_channels = competitors + ([{"name": "🧠 US (MindShift)", "subscribers": our_subs,
                                         "total_views": ch_stats.get("total_views",0),
                                         "video_count": ch_stats.get("video_count",0)}]
                                       if our_subs else [])
        all_channels.sort(key=lambda x: x.get("subscribers", 0), reverse=True)

        st.subheader("Subscriber Comparison")
        try:
            import plotly.graph_objects as go
            names = [c["name"] for c in all_channels]
            subs  = [c.get("subscribers", 0) for c in all_channels]
            colors = ["#FFD700" if "US" in c["name"] else "#6C63FF" for c in all_channels]
            fig = go.Figure(go.Bar(x=names, y=subs, marker_color=colors))
            fig.update_layout(title="Subscribers vs Competitors", height=380,
                               yaxis_title="Subscribers",
                               plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                               font_color="#FAFAFA")
            st.plotly_chart(fig, use_container_width=True)
        except ImportError:
            for c in all_channels:
                st.markdown(f"**{c['name']}**: {c.get('subscribers',0):,} subs")

        st.subheader("Detailed Stats")
        for c in all_channels:
            col1, col2, col3 = st.columns(3)
            col1.metric(c["name"],           f"{c.get('subscribers',0):,} subs")
            col2.metric("Total Views",        f"{c.get('total_views',0):,}")
            col3.metric("Videos Uploaded",    str(c.get("video_count",0)))
            st.markdown("---")

        st.subheader("AI Competitor Insights")
        st.info(analysis.get("competitor_insights", "No competitor analysis available."))

    else:
        st.warning(
            "No competitor data. Add a YouTube Data API key as `YOUTUBE_API_KEY` in GitHub Secrets "
            "to enable automatic competitor tracking."
        )
        st.markdown("""
**Competitors we track:**
- Productive Peter
- Trust Me Bro
- Charisma on Command
- Sprouts
- Better Ideas
- Improvement Pill
        """)


def page_recommendations(report: dict):
    st.header("🚀 Growth Recommendations")

    analysis = report.get("analysis", {})
    fixes    = report.get("agent_improvement_tips", {})

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📈 Growth Tactics (This Week)")
        for t in analysis.get("growth_tactics", ["No data yet"]):
            st.info(f"★ {t}")

        st.subheader("👥 Subscriber Growth Tips")
        for t in analysis.get("follower_growth_tips", ["No data yet"]):
            st.success(f"• {t}")

    with col2:
        st.subheader("📉 View Drop Analysis")
        st.markdown(analysis.get("view_drop_analysis", "No view data available yet."))

        st.subheader("🛠 Agent Fix Suggestions")
        if fixes:
            for agent, tip in fixes.items():
                st.error(f"**{agent}:** {tip}")
        else:
            st.success("All agents healthy — no fixes needed!")

    st.markdown("---")
    st.subheader("📅 Full Analysis Report")
    st.markdown(f"*Generated: {_time_ago(report.get('generated_at',''))}*")

    with st.expander("View raw JSON report"):
        st.json(report)


# ── App Entry ─────────────────────────────────────────────────────────────────

def main():
    if not _check_password():
        return

    # Sidebar
    with st.sidebar:
        st.title("🧠 MindShift")
        st.markdown(f"[YouTube Channel]({CHANNEL_URL})")
        st.markdown("---")
        page = st.radio("Navigate", [
            "📊 Overview",
            "🤖 Agents",
            "🎬 Videos",
            "🕵️ Competitors",
            "🚀 Recommendations",
        ])
        st.markdown("---")
        if st.button("🔄 Refresh Data"):
            st.cache_data.clear()
            st.rerun()
        st.caption("Data refreshes every 5 min automatically")

        if st.button("🔓 Logout"):
            st.session_state["authenticated"] = False
            st.rerun()

    # Load data
    report     = _fetch("head_agent_report.json") or {}
    upload_log = _fetch("upload_log.json")        or []

    if not report:
        st.warning(
            "No head agent report found. "
            "Run the Head Agent workflow (Actions → Head Agent → Run workflow) to generate it."
        )
        st.stop()

    # Route
    if "Overview"        in page: page_overview(report, upload_log)
    elif "Agents"        in page: page_agents(report)
    elif "Videos"        in page: page_videos(report, upload_log)
    elif "Competitors"   in page: page_competitors(report)
    elif "Recommendations" in page: page_recommendations(report)


if __name__ == "__main__":
    main()
