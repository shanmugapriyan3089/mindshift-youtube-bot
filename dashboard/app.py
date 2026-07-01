"""
MindShift Productivity — Channel Dashboard
"""
import streamlit as st
import requests, json, hashlib
from datetime import datetime, timezone

REPO_OWNER  = "shanmugapriyan3089"
REPO_NAME   = "mindshift-youtube-bot"
BRANCH      = "main"
CHANNEL_URL = "https://youtube.com/@MindShiftProductivity"

st.set_page_config(
    page_title="MindShift Dashboard",
    page_icon="https://raw.githubusercontent.com/shanmugapriyan3089/mindshift-youtube-bot/main/assets/branding/logo.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS + Icon Font ────────────────────────────────────────────────────
st.markdown("""
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" />
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"/>
<style>
  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

  .material-symbols-rounded {
    font-variation-settings: 'FILL' 1, 'wght' 400, 'GRAD' 0, 'opsz' 24;
    vertical-align: middle;
    font-size: 20px;
    line-height: 1;
  }

  /* Login card */
  .login-card {
    background: #1A1D2E;
    border: 1px solid #2D3148;
    border-radius: 16px;
    padding: 48px 40px;
    max-width: 420px;
    margin: 60px auto 0;
  }
  .login-logo {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 32px;
  }
  .login-logo-icon {
    width: 48px; height: 48px;
    background: linear-gradient(135deg, #6C63FF 0%, #A78BFA 100%);
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
  }
  .login-title { font-size: 22px; font-weight: 700; color: #FAFAFA; margin: 0; }
  .login-sub   { font-size: 13px; color: #9CA3AF; margin: 4px 0 0; }

  /* Stat cards */
  .stat-card {
    background: #1A1D2E;
    border: 1px solid #2D3148;
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 4px;
  }
  .stat-label { font-size: 12px; color: #9CA3AF; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em; }
  .stat-value { font-size: 28px; font-weight: 700; color: #FAFAFA; margin: 6px 0 0; }
  .stat-icon  { float: right; color: #6C63FF; font-size: 28px; margin-top: -4px; }

  /* Agent status pills */
  .pill-ok      { background: #14532D; color: #4ADE80; border-radius: 6px; padding: 3px 10px; font-size: 12px; font-weight: 600; }
  .pill-fail    { background: #450A0A; color: #F87171; border-radius: 6px; padding: 3px 10px; font-size: 12px; font-weight: 600; }
  .pill-warn    { background: #422006; color: #FB923C; border-radius: 6px; padding: 3px 10px; font-size: 12px; font-weight: 600; }
  .pill-neutral { background: #1F2937; color: #9CA3AF; border-radius: 6px; padding: 3px 10px; font-size: 12px; font-weight: 600; }

  /* Section headers */
  .section-header {
    display: flex; align-items: center; gap: 10px;
    font-size: 18px; font-weight: 700; color: #FAFAFA;
    margin: 28px 0 16px;
    padding-bottom: 10px;
    border-bottom: 1px solid #2D3148;
  }
  .section-header .material-symbols-rounded { color: #6C63FF; font-size: 22px; }

  /* Agent row */
  .agent-row {
    display: flex; align-items: center; justify-content: space-between;
    background: #1A1D2E; border: 1px solid #2D3148;
    border-radius: 10px; padding: 14px 18px; margin-bottom: 8px;
  }
  .agent-name  { font-size: 14px; font-weight: 600; color: #FAFAFA; }
  .agent-time  { font-size: 12px; color: #9CA3AF; margin-top: 2px; }

  /* Video row */
  .video-row {
    display: flex; align-items: center; gap: 16px;
    background: #1A1D2E; border: 1px solid #2D3148;
    border-radius: 10px; padding: 14px 18px; margin-bottom: 8px;
  }
  .video-type-badge-r { background: #312E81; color: #A5B4FC; border-radius: 6px; padding: 3px 10px; font-size: 11px; font-weight: 600; flex-shrink: 0; }
  .video-type-badge-s { background: #1A2E1A; color: #4ADE80;  border-radius: 6px; padding: 3px 10px; font-size: 11px; font-weight: 600; flex-shrink: 0; }
  .video-title   { font-size: 14px; font-weight: 600; color: #FAFAFA; flex: 1; }
  .video-stat    { font-size: 13px; color: #9CA3AF; white-space: nowrap; }

  /* Urgent banner */
  .urgent-banner {
    background: #450A0A; border: 1px solid #7F1D1D;
    border-radius: 10px; padding: 14px 18px; margin-bottom: 8px;
    display: flex; align-items: center; gap: 12px;
  }
  .urgent-banner .material-symbols-rounded { color: #F87171; }
  .urgent-text { font-size: 14px; color: #FCA5A5; }

  /* Insight cards */
  .insight-card {
    background: #1A1D2E; border: 1px solid #2D3148;
    border-left: 3px solid #6C63FF;
    border-radius: 10px; padding: 14px 18px; margin-bottom: 8px;
    font-size: 14px; color: #E5E7EB;
  }
  .insight-card.green { border-left-color: #4ADE80; }
  .insight-card.amber { border-left-color: #FB923C; }
  .insight-card.blue  { border-left-color: #38BDF8; }

  /* Hide Streamlit default elements */
  #MainMenu, footer, header { visibility: hidden; }
  .stDeployButton { display: none; }
  [data-testid="stSidebarNav"] { display: none; }
</style>
""", unsafe_allow_html=True)


# ── Icon helper ───────────────────────────────────────────────────────────────

def icon(name: str, cls: str = "") -> str:
    return f'<span class="material-symbols-rounded {cls}">{name}</span>'


# ── Auth ──────────────────────────────────────────────────────────────────────

def _check_password() -> bool:
    stored = st.secrets.get("DASHBOARD_PASSWORD", "mindshift2026")
    if st.session_state.get("authenticated"):
        return True

    st.markdown(f"""
    <div class="login-card">
      <div class="login-logo">
        <div class="login-logo-icon">
          {icon('psychology', '')}
        </div>
        <div>
          <p class="login-title">MindShift</p>
          <p class="login-sub">Channel Dashboard</p>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.4, 1])
    with col2:
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        pw = st.text_input("Password", type="password", label_visibility="collapsed",
                           placeholder="Enter your password")
        if st.button("Sign in", use_container_width=True, type="primary"):
            if hashlib.sha256(pw.encode()).hexdigest() == \
               hashlib.sha256(stored.encode()).hexdigest():
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("Incorrect password")
    return False


# ── Data Loading ──────────────────────────────────────────────────────────────

@st.cache_data(ttl=300)
def _fetch(filename: str):
    token = st.secrets.get("GITHUB_TOKEN", "")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    url = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/{BRANCH}/{filename}"
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.ok:
            return r.json()
    except Exception:
        pass
    return None


def _time_ago(iso_str: str) -> str:
    if not iso_str:
        return "Never"
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        h  = int((datetime.now(timezone.utc) - dt).total_seconds() / 3600)
        if h < 1:   return "Just now"
        if h < 24:  return f"{h}h ago"
        return f"{h // 24}d ago"
    except Exception:
        return iso_str[:10]


def _pill(conclusion: str) -> str:
    c = str(conclusion).lower()
    if c == "success":     return '<span class="pill-ok">Healthy</span>'
    if c in ("failure", "error", "timed_out"): return '<span class="pill-fail">Failed</span>'
    if c == "in_progress": return '<span class="pill-warn">Running</span>'
    if c == "never_run":   return '<span class="pill-neutral">Never run</span>'
    return f'<span class="pill-neutral">{conclusion}</span>'


# ── Sidebar ───────────────────────────────────────────────────────────────────

def _sidebar():
    with st.sidebar:
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:10px;padding:8px 0 20px;">
          <div style="background:linear-gradient(135deg,#6C63FF,#A78BFA);
                      border-radius:10px;width:38px;height:38px;
                      display:flex;align-items:center;justify-content:center;">
            {icon('psychology')}
          </div>
          <div>
            <div style="font-size:15px;font-weight:700;color:#FAFAFA;">MindShift</div>
            <div style="font-size:11px;color:#9CA3AF;">Productivity Channel</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        page = st.radio("", [
            "Overview",
            "Agents",
            "Videos",
            "Competitors",
            "Recommendations",
        ], label_visibility="collapsed")

        st.markdown("<div style='margin-top:20px'></div>", unsafe_allow_html=True)

        nav_icons = {
            "Overview":       "dashboard",
            "Agents":         "smart_toy",
            "Videos":         "play_circle",
            "Competitors":    "group",
            "Recommendations":"trending_up",
        }

        if st.button(f"Refresh data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

        st.markdown("---")
        st.markdown(f"<a href='{CHANNEL_URL}' target='_blank' style='color:#6C63FF;font-size:13px;text-decoration:none;'>{icon('open_in_new')} YouTube Channel</a>", unsafe_allow_html=True)
        st.markdown("<div style='margin-top:8px'></div>", unsafe_allow_html=True)

        if st.button("Sign out", use_container_width=True):
            st.session_state["authenticated"] = False
            st.rerun()

        st.caption("Auto-refreshes every 5 min")
    return page


# ── Pages ─────────────────────────────────────────────────────────────────────

def page_overview(report, upload_log):
    analysis  = report.get("analysis", {})
    ch        = report.get("channel_stats", {})
    health    = report.get("agent_health_summary", {})
    score     = analysis.get("channel_health_score", 0)
    upload_s  = report.get("upload_stats", {})

    # Stats row
    cols = st.columns(5)
    stats = [
        ("analytics",    "Health Score",     f"{score}/10",
          f"{health.get('healthy',0)}/{health.get('total',0)} agents OK"),
        ("group",        "Subscribers",
          f"{ch.get('subscribers',0):,}" if ch.get("subscribers") else "—", "total followers"),
        ("visibility",   "Total Views",
          f"{ch.get('total_views',0):,}"  if ch.get("total_views")  else "—", "lifetime"),
        ("movie",        "Videos Uploaded",
          str(upload_s.get("total_uploaded", 0)),
          f"{upload_s.get('regular_count',0)} regular · {upload_s.get('shorts_count',0)} shorts"),
        ("schedule",     "Last Report",
          _time_ago(report.get("generated_at","")), "head agent ran"),
    ]
    for col, (ic, label, val, sub) in zip(cols, stats):
        with col:
            st.markdown(f"""
            <div class="stat-card">
              <span class="stat-icon">{icon(ic)}</span>
              <div class="stat-label">{label}</div>
              <div class="stat-value">{val}</div>
              <div style="font-size:12px;color:#6B7280;margin-top:4px">{sub}</div>
            </div>""", unsafe_allow_html=True)

    # Urgent
    urgent = analysis.get("urgent_actions", [])
    if urgent:
        st.markdown(f'<div class="section-header">{icon("warning")} Urgent Actions</div>', unsafe_allow_html=True)
        for a in urgent:
            st.markdown(f'<div class="urgent-banner">{icon("error")}<span class="urgent-text">{a}</span></div>', unsafe_allow_html=True)

    # Last uploads
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(f'<div class="section-header">{icon("movie")} Last Regular Video</div>', unsafe_allow_html=True)
        lr = upload_s.get("last_regular")
        if lr:
            st.markdown(f"""
            <div class="video-row">
              <span class="video-type-badge-r">Regular</span>
              <a href="{lr.get('url','#')}" target="_blank" style="text-decoration:none">
                <div class="video-title">{lr.get('title','—')}</div>
              </a>
              <span class="video-stat">{_time_ago(lr.get('uploaded_at',''))}</span>
            </div>""", unsafe_allow_html=True)
        else:
            st.info("No regular video yet")

    with col_b:
        st.markdown(f'<div class="section-header">{icon("bolt")} Last Short</div>', unsafe_allow_html=True)
        ls = upload_s.get("last_short")
        if ls:
            st.markdown(f"""
            <div class="video-row">
              <span class="video-type-badge-s">Short</span>
              <a href="{ls.get('url','#')}" target="_blank" style="text-decoration:none">
                <div class="video-title">{ls.get('title','—')}</div>
              </a>
              <span class="video-stat">{_time_ago(ls.get('uploaded_at',''))}</span>
            </div>""", unsafe_allow_html=True)
        else:
            st.info("No Short yet")

    # Working / Needs improvement
    col_c, col_d = st.columns(2)
    with col_c:
        st.markdown(f'<div class="section-header">{icon("check_circle")} What\'s Working</div>', unsafe_allow_html=True)
        for item in analysis.get("what_is_working", []):
            st.markdown(f'<div class="insight-card green">{icon("check")} &nbsp;{item}</div>', unsafe_allow_html=True)
    with col_d:
        st.markdown(f'<div class="section-header">{icon("build")} Needs Improvement</div>', unsafe_allow_html=True)
        for item in analysis.get("what_needs_improvement", []):
            st.markdown(f'<div class="insight-card amber">{icon("arrow_forward")} &nbsp;{item}</div>', unsafe_allow_html=True)


def page_agents(report):
    statuses = report.get("agent_statuses", {})
    fixes    = report.get("agent_improvement_tips", {})
    health   = report.get("agent_health_summary", {})

    st.markdown(f'<div class="section-header">{icon("smart_toy")} Agent Monitor</div>', unsafe_allow_html=True)

    failed  = health.get("failed", 0)
    total   = health.get("total", 0)
    if failed == 0:
        st.markdown(f'<div class="insight-card green">{icon("verified")} &nbsp;All {total} agents are healthy</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="urgent-banner">{icon("error")}<span class="urgent-text">{failed} of {total} agents need attention</span></div>', unsafe_allow_html=True)

    broken  = [(n, s) for n, s in statuses.items() if s.get("conclusion") not in ("success", "in_progress", "never_run")]
    healthy = [(n, s) for n, s in statuses.items() if s not in [s2 for _, s2 in broken]]

    if broken:
        st.markdown(f'<div class="section-header">{icon("error")} Failed Agents</div>', unsafe_allow_html=True)
        for name, s in broken:
            fix = fixes.get(name, "Check GitHub Actions logs for details.")
            run_url = s.get("run_url", "")
            link = f' &nbsp;<a href="{run_url}" target="_blank" style="color:#6C63FF;font-size:12px">View logs</a>' if run_url else ""
            st.markdown(f"""
            <div class="agent-row">
              <div>
                <div class="agent-name">{icon("smart_toy")} &nbsp;{name}</div>
                <div class="agent-time">{fix}</div>
              </div>
              <div>{_pill(s.get('conclusion',''))}{link}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown(f'<div class="section-header">{icon("check_circle")} Healthy Agents</div>', unsafe_allow_html=True)
    for name, s in healthy:
        st.markdown(f"""
        <div class="agent-row">
          <div>
            <div class="agent-name">{icon("smart_toy")} &nbsp;{name}</div>
            <div class="agent-time">Last run: {_time_ago(s.get('last_run_at',''))}</div>
          </div>
          {_pill(s.get('conclusion',''))}
        </div>""", unsafe_allow_html=True)


def page_videos(report, upload_log):
    video_stats = report.get("video_stats", [])
    st.markdown(f'<div class="section-header">{icon("play_circle")} Video Analytics</div>', unsafe_allow_html=True)

    if video_stats:
        sorted_vids = sorted(video_stats, key=lambda x: x.get("views", 0), reverse=True)
        total_views = sum(v.get("views", 0) for v in video_stats)
        total_likes = sum(v.get("likes", 0) for v in video_stats)

        c1, c2, c3 = st.columns(3)
        for col, ic, label, val in [
            (c1, "visibility", "Total Views (tracked)", f"{total_views:,}"),
            (c2, "thumb_up",   "Total Likes",           f"{total_likes:,}"),
            (c3, "bar_chart",  "Avg Views / Video",     f"{total_views // max(len(video_stats),1):,}"),
        ]:
            with col:
                st.markdown(f'<div class="stat-card"><span class="stat-icon">{icon(ic)}</span><div class="stat-label">{label}</div><div class="stat-value">{val}</div></div>', unsafe_allow_html=True)

        try:
            import plotly.graph_objects as go
            top10 = sorted_vids[:10]
            titles = [v["title"][:38] + "…" if len(v["title"]) > 38 else v["title"] for v in top10]
            fig = go.Figure(go.Bar(
                x=[v["views"] for v in top10], y=titles, orientation="h",
                marker=dict(color="#6C63FF", line=dict(color="#A78BFA", width=0)),
            ))
            fig.update_layout(
                title=dict(text="Top 10 Videos by Views", font=dict(color="#FAFAFA", size=15)),
                height=360, margin=dict(l=0, r=20, t=40, b=20),
                xaxis=dict(title="Views", color="#9CA3AF", gridcolor="#2D3148"),
                yaxis=dict(color="#FAFAFA"),
                plot_bgcolor="#1A1D2E", paper_bgcolor="#0E1117",
                font=dict(color="#9CA3AF"),
            )
            st.plotly_chart(fig, use_container_width=True)
        except ImportError:
            pass

        st.markdown(f'<div class="section-header">{icon("list")} All Tracked Videos</div>', unsafe_allow_html=True)
        for v in sorted_vids:
            st.markdown(f"""
            <div class="video-row">
              <a href="{v.get('url','#')}" target="_blank" style="text-decoration:none;flex:1">
                <div class="video-title">{v['title']}</div>
              </a>
              <span class="video-stat">{icon('visibility')} {v.get('views',0):,}</span>
              &nbsp;&nbsp;
              <span class="video-stat">{icon('thumb_up')} {v.get('likes',0)}</span>
              &nbsp;&nbsp;
              <span class="video-stat">{icon('chat_bubble')} {v.get('comments',0)}</span>
            </div>""", unsafe_allow_html=True)

    elif upload_log:
        st.info("Live view counts not available yet — add YOUTUBE_API_KEY to GitHub Secrets for real-time stats.")
        for v in reversed(upload_log[-20:]):
            badge = '<span class="video-type-badge-s">Short</span>' if v.get("type") == "shorts" else '<span class="video-type-badge-r">Regular</span>'
            url   = v.get("url", f"https://youtu.be/{v.get('video_id','')}")
            st.markdown(f"""
            <div class="video-row">
              {badge}
              <a href="{url}" target="_blank" style="text-decoration:none;flex:1">
                <div class="video-title">{v.get('title','—')}</div>
              </a>
              <span class="video-stat">{_time_ago(v.get('uploaded_at',''))}</span>
            </div>""", unsafe_allow_html=True)
    else:
        st.warning("No video data yet.")


def page_competitors(report):
    competitors = report.get("competitors", [])
    ch          = report.get("channel_stats", {})
    analysis    = report.get("analysis", {})
    our_subs    = ch.get("subscribers", 0)

    st.markdown(f'<div class="section-header">{icon("group")} Competitor Analysis</div>', unsafe_allow_html=True)

    if competitors:
        all_ch = sorted(
            competitors + ([{"name": "MindShift (Us)", "subscribers": our_subs,
                             "total_views": ch.get("total_views",0),
                             "video_count": ch.get("video_count",0)}] if our_subs else []),
            key=lambda x: x.get("subscribers", 0), reverse=True,
        )
        try:
            import plotly.graph_objects as go
            names  = [c["name"] for c in all_ch]
            subs   = [c.get("subscribers", 0) for c in all_ch]
            colors = ["#FFD700" if "Us" in c["name"] else "#6C63FF" for c in all_ch]
            fig = go.Figure(go.Bar(x=names, y=subs, marker_color=colors,
                                   text=[f"{s:,}" for s in subs], textposition="outside"))
            fig.update_layout(
                title=dict(text="Subscriber Count vs Competitors", font=dict(color="#FAFAFA", size=15)),
                height=380, margin=dict(l=20, r=20, t=50, b=20),
                yaxis=dict(title="Subscribers", color="#9CA3AF", gridcolor="#2D3148"),
                xaxis=dict(color="#FAFAFA"),
                plot_bgcolor="#1A1D2E", paper_bgcolor="#0E1117",
                font=dict(color="#9CA3AF"),
            )
            st.plotly_chart(fig, use_container_width=True)
        except ImportError:
            pass

        for c in all_ch:
            is_us = "Us" in c.get("name","")
            border = "border-left: 3px solid #FFD700;" if is_us else ""
            st.markdown(f"""
            <div class="agent-row" style="{border}">
              <div>
                <div class="agent-name">{icon('channel')} &nbsp;{c['name']}</div>
                <div class="agent-time">{c.get('video_count',0)} videos · {c.get('total_views',0):,} total views</div>
              </div>
              <div style="font-size:20px;font-weight:700;color:#FAFAFA">{c.get('subscribers',0):,} <span style="font-size:12px;color:#9CA3AF">subs</span></div>
            </div>""", unsafe_allow_html=True)

        st.markdown(f'<div class="section-header">{icon("lightbulb")} AI Competitor Insights</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="insight-card blue">{icon("psychology")} &nbsp;{analysis.get("competitor_insights","No analysis yet.")}</div>', unsafe_allow_html=True)

    else:
        st.warning("Competitor data not available. Add YOUTUBE_API_KEY to GitHub Secrets.")
        st.markdown("""
        <div class="insight-card">Competitors we track: Productive Peter · Trust Me Bro · Charisma on Command · Sprouts · Better Ideas · Improvement Pill</div>
        """, unsafe_allow_html=True)


def page_recommendations(report):
    analysis = report.get("analysis", {})
    fixes    = report.get("agent_improvement_tips", {})

    st.markdown(f'<div class="section-header">{icon("trending_up")} Growth Recommendations</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f'<div class="section-header" style="margin-top:4px">{icon("rocket_launch")} Growth Tactics This Week</div>', unsafe_allow_html=True)
        for t in analysis.get("growth_tactics", ["Run head agent for analysis"]):
            st.markdown(f'<div class="insight-card blue">{icon("star")} &nbsp;{t}</div>', unsafe_allow_html=True)

        st.markdown(f'<div class="section-header">{icon("person_add")} Subscriber Growth Tips</div>', unsafe_allow_html=True)
        for t in analysis.get("follower_growth_tips", []):
            st.markdown(f'<div class="insight-card green">{icon("check")} &nbsp;{t}</div>', unsafe_allow_html=True)

    with col2:
        st.markdown(f'<div class="section-header" style="margin-top:4px">{icon("bar_chart")} View Drop Analysis</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="insight-card">{analysis.get("view_drop_analysis","No data yet — run head agent.")}</div>', unsafe_allow_html=True)

        if fixes:
            st.markdown(f'<div class="section-header">{icon("build")} Agent Fix Suggestions</div>', unsafe_allow_html=True)
            for agent, tip in fixes.items():
                st.markdown(f'<div class="insight-card amber">{icon("smart_toy")} &nbsp;<strong>{agent}:</strong> {tip}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="section-header">{icon("build")} Agent Fix Suggestions</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="insight-card green">{icon("verified")} &nbsp;All agents healthy — no fixes needed</div>', unsafe_allow_html=True)

    with st.expander("View raw JSON report"):
        st.json(report)


# ── Entry ─────────────────────────────────────────────────────────────────────

def main():
    if not _check_password():
        return

    page       = _sidebar()
    report     = _fetch("head_agent_report.json") or {}
    upload_log = _fetch("upload_log.json")        or []

    if not report:
        st.markdown(f'<div class="section-header">{icon("info")} No Report Yet</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="insight-card amber">
          Head agent has not run yet. Go to <strong>GitHub → Actions → Agent 0 — Head Agent → Run workflow</strong> to generate the first report.
        </div>
        """, unsafe_allow_html=True)
        return

    if   page == "Overview":        page_overview(report, upload_log)
    elif page == "Agents":          page_agents(report)
    elif page == "Videos":          page_videos(report, upload_log)
    elif page == "Competitors":     page_competitors(report)
    elif page == "Recommendations": page_recommendations(report)


if __name__ == "__main__":
    main()
