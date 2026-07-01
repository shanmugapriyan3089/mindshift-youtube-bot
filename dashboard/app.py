"""
MindShift Productivity — Channel Dashboard
"""
import streamlit as st
import requests, json, hashlib, base64
from datetime import datetime, timezone

REPO_OWNER  = "shanmugapriyan3089"
REPO_NAME   = "mindshift-youtube-bot"
BRANCH      = "main"
CHANNEL_URL = "https://youtube.com/@MindShiftProductivity"

st.set_page_config(
    page_title="MindShift Dashboard",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS injection (base64 data-URI bypasses Streamlit's <style> sanitiser) ────

_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200');

html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }

.material-symbols-rounded {
  font-family: 'Material Symbols Rounded' !important;
  font-variation-settings: 'FILL' 1,'wght' 400,'GRAD' 0,'opsz' 24;
  font-size: 20px; vertical-align: middle; line-height: 1; display: inline-block;
}

/* Stat cards */
.stat-card {
  background: #1A1D2E; border: 1px solid #2D3148; border-radius: 12px;
  padding: 20px 22px; margin-bottom: 6px; position: relative;
}
.stat-label { font-size: 11px; color: #9CA3AF; font-weight: 600;
  text-transform: uppercase; letter-spacing: .06em; }
.stat-value { font-size: 26px; font-weight: 700; color: #FAFAFA; margin: 6px 0 0; }
.stat-sub   { font-size: 12px; color: #6B7280; margin: 4px 0 0; }
.stat-icon  { position: absolute; top: 18px; right: 18px;
  color: #6C63FF; font-size: 26px !important; }

/* Status pills */
.pill-ok      { background:#14532D; color:#4ADE80; border-radius:6px;
  padding:3px 10px; font-size:12px; font-weight:600; display:inline-block; }
.pill-fail    { background:#450A0A; color:#F87171; border-radius:6px;
  padding:3px 10px; font-size:12px; font-weight:600; display:inline-block; }
.pill-warn    { background:#422006; color:#FB923C; border-radius:6px;
  padding:3px 10px; font-size:12px; font-weight:600; display:inline-block; }
.pill-neutral { background:#1F2937; color:#9CA3AF; border-radius:6px;
  padding:3px 10px; font-size:12px; font-weight:600; display:inline-block; }

/* Section headers */
.sec-hdr {
  display:flex; align-items:center; gap:10px;
  font-size:16px; font-weight:700; color:#FAFAFA;
  margin:24px 0 14px; padding-bottom:10px; border-bottom:1px solid #2D3148;
}
.sec-hdr .material-symbols-rounded { color:#6C63FF; }

/* Cards */
.card {
  background:#1A1D2E; border:1px solid #2D3148; border-radius:10px;
  padding:14px 18px; margin-bottom:8px; display:flex;
  align-items:center; justify-content:space-between;
}
.card-title { font-size:14px; font-weight:600; color:#FAFAFA; }
.card-sub   { font-size:12px; color:#9CA3AF; margin-top:2px; }

/* Insight cards */
.ic { background:#1A1D2E; border:1px solid #2D3148;
  border-left:3px solid #6C63FF; border-radius:10px;
  padding:12px 16px; margin-bottom:8px; font-size:14px; color:#E5E7EB; }
.ic.g { border-left-color:#4ADE80; }
.ic.a { border-left-color:#FB923C; }
.ic.b { border-left-color:#38BDF8; }
.ic.r { border-left-color:#F87171; }

/* Video badge */
.vbr { background:#312E81; color:#A5B4FC; border-radius:5px;
  padding:2px 9px; font-size:11px; font-weight:600; white-space:nowrap; }
.vbs { background:#1A2E1A; color:#4ADE80; border-radius:5px;
  padding:2px 9px; font-size:11px; font-weight:600; white-space:nowrap; }

/* Sidebar brand */
.brand { display:flex; align-items:center; gap:10px; padding:6px 0 22px; }
.brand-icon { background:linear-gradient(135deg,#6C63FF,#A78BFA);
  border-radius:10px; width:38px; height:38px;
  display:flex; align-items:center; justify-content:center; flex-shrink:0; }
.brand-name { font-size:15px; font-weight:700; color:#FAFAFA; }
.brand-sub  { font-size:11px; color:#9CA3AF; }

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility:hidden; }
.stDeployButton { display:none !important; }
[data-testid="stSidebarNav"] { display:none !important; }
"""

def _inject_css():
    b64 = base64.b64encode(_CSS.encode()).decode()
    st.markdown(
        f'<link rel="stylesheet" href="data:text/css;base64,{b64}">',
        unsafe_allow_html=True,
    )

_inject_css()


# ── Icon helper ───────────────────────────────────────────────────────────────

def ic(name: str) -> str:
    return f'<span class="material-symbols-rounded">{name}</span>'


# ── Auth ──────────────────────────────────────────────────────────────────────

def _check_password() -> bool:
    stored = st.secrets.get("DASHBOARD_PASSWORD", "mindshift2026")
    if st.session_state.get("authenticated"):
        return True

    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown(f"""
        <div style="text-align:center;padding:48px 0 28px">
          <div style="background:linear-gradient(135deg,#6C63FF,#A78BFA);
                      border-radius:16px;width:60px;height:60px;
                      display:inline-flex;align-items:center;justify-content:center;
                      margin-bottom:16px;">
            <span class="material-symbols-rounded" style="font-size:32px;color:#fff">psychology</span>
          </div>
          <div style="font-size:22px;font-weight:700;color:#FAFAFA">MindShift</div>
          <div style="font-size:13px;color:#9CA3AF;margin-top:4px">Channel Dashboard</div>
        </div>
        """, unsafe_allow_html=True)
        pw = st.text_input("Password", type="password",
                           label_visibility="collapsed", placeholder="Password")
        if st.button("Sign in", use_container_width=True, type="primary"):
            if hashlib.sha256(pw.encode()).hexdigest() == \
               hashlib.sha256(stored.encode()).hexdigest():
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("Incorrect password")
    return False


# ── Data ──────────────────────────────────────────────────────────────────────

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


def _ago(iso: str) -> str:
    if not iso:
        return "Never"
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        h  = int((datetime.now(timezone.utc) - dt).total_seconds() / 3600)
        if h < 1:  return "Just now"
        if h < 24: return f"{h}h ago"
        return f"{h // 24}d ago"
    except Exception:
        return iso[:10]


def _pill(c: str) -> str:
    c = str(c).lower()
    if c == "success":                       return '<span class="pill-ok">Healthy</span>'
    if c in ("failure","error","timed_out"): return '<span class="pill-fail">Failed</span>'
    if c == "in_progress":                   return '<span class="pill-warn">Running</span>'
    return '<span class="pill-neutral">Inactive</span>'


# ── Sidebar ───────────────────────────────────────────────────────────────────

def _sidebar():
    with st.sidebar:
        st.markdown(f"""
        <div class="brand">
          <div class="brand-icon">{ic("psychology")}</div>
          <div><div class="brand-name">MindShift</div>
               <div class="brand-sub">Productivity</div></div>
        </div>""", unsafe_allow_html=True)

        page = st.radio("", ["Overview","Agents","Videos","Competitors","Recommendations"],
                        label_visibility="collapsed")
        st.markdown("---")
        if st.button("Refresh", use_container_width=True):
            st.cache_data.clear(); st.rerun()
        st.markdown(f'<a href="{CHANNEL_URL}" target="_blank" style="color:#6C63FF;font-size:13px;text-decoration:none;">{ic("open_in_new")} YouTube Channel</a>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Sign out", use_container_width=True):
            st.session_state["authenticated"] = False; st.rerun()
        st.caption("Refreshes every 5 min")
    return page


# ── Pages ─────────────────────────────────────────────────────────────────────

def page_overview(report, upload_log):
    analysis = report.get("analysis", {})
    ch       = report.get("channel_stats", {})
    health   = report.get("agent_health_summary", {})
    score    = analysis.get("channel_health_score", 0)
    ups      = report.get("upload_stats", {})

    # Stat cards
    cols = st.columns(5)
    for col, (icon_name, label, val, sub) in zip(cols, [
        ("analytics",  "Health Score",    f"{score}/10",
         f"{health.get('healthy',0)}/{health.get('total',0)} agents OK"),
        ("group",      "Subscribers",
         f"{ch.get('subscribers',0):,}" if ch.get("subscribers") else "—",
         "total followers"),
        ("visibility", "Total Views",
         f"{ch.get('total_views',0):,}" if ch.get("total_views") else "—",
         "lifetime"),
        ("movie",      "Videos",          str(ups.get("total_uploaded",0)),
         f"{ups.get('regular_count',0)} regular · {ups.get('shorts_count',0)} shorts"),
        ("schedule",   "Last Report",     _ago(report.get("generated_at","")),
         "head agent"),
    ]):
        with col:
            st.markdown(f"""
            <div class="stat-card">
              <span class="material-symbols-rounded stat-icon">{icon_name}</span>
              <div class="stat-label">{label}</div>
              <div class="stat-value">{val}</div>
              <div class="stat-sub">{sub}</div>
            </div>""", unsafe_allow_html=True)

    # Urgent
    for a in analysis.get("urgent_actions", []):
        st.markdown(f'<div class="ic r">{ic("warning")} &nbsp;{a}</div>', unsafe_allow_html=True)

    # Last uploads
    col_a, col_b = st.columns(2)
    for col, label, icon_n, entry, badge_cls, badge_txt in [
        (col_a, "Last Regular Video", "movie",  ups.get("last_regular"), "vbr", "Regular"),
        (col_b, "Last Short",         "bolt",   ups.get("last_short"),   "vbs", "Short"),
    ]:
        with col:
            st.markdown(f'<div class="sec-hdr">{ic(icon_n)} {label}</div>', unsafe_allow_html=True)
            if entry:
                url = entry.get("url", "#")
                st.markdown(f"""
                <div class="card">
                  <div>
                    <span class="{badge_cls}">{badge_txt}</span>&nbsp;
                    <a href="{url}" target="_blank" style="color:#FAFAFA;text-decoration:none;font-size:14px;font-weight:600">{entry.get('title','—')[:60]}</a>
                    <div class="card-sub">{_ago(entry.get('uploaded_at',''))}</div>
                  </div>
                  {ic("open_in_new")}
                </div>""", unsafe_allow_html=True)

    # Working / Needs improvement
    col_c, col_d = st.columns(2)
    with col_c:
        st.markdown(f'<div class="sec-hdr">{ic("check_circle")} What\'s Working</div>', unsafe_allow_html=True)
        for item in analysis.get("what_is_working", ["Run head agent for analysis"]):
            st.markdown(f'<div class="ic g">{ic("check")} &nbsp;{item}</div>', unsafe_allow_html=True)
    with col_d:
        st.markdown(f'<div class="sec-hdr">{ic("build")} Needs Improvement</div>', unsafe_allow_html=True)
        for item in analysis.get("what_needs_improvement", ["Run head agent for analysis"]):
            st.markdown(f'<div class="ic a">{ic("arrow_forward")} &nbsp;{item}</div>', unsafe_allow_html=True)


def page_agents(report):
    statuses = report.get("agent_statuses", {})
    fixes    = report.get("agent_improvement_tips", {})
    health   = report.get("agent_health_summary", {})
    failed   = health.get("failed", 0)
    total    = health.get("total", 0)

    st.markdown(f'<div class="sec-hdr">{ic("smart_toy")} Agent Monitor — {total} Agents</div>', unsafe_allow_html=True)

    if failed == 0:
        st.markdown(f'<div class="ic g">{ic("verified")} All {total} agents healthy</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="ic r">{ic("error")} {failed}/{total} agents need attention</div>', unsafe_allow_html=True)

    broken  = [(n, s) for n, s in statuses.items()
               if s.get("conclusion") not in ("success","in_progress","never_run","cancelled","skipped")]
    healthy = [(n, s) for n, s in statuses.items() if (n, s) not in broken]

    if broken:
        st.markdown(f'<div class="sec-hdr">{ic("error")} Failed</div>', unsafe_allow_html=True)
        for name, s in broken:
            fix = fixes.get(name, "Check GitHub Actions logs.")
            run_url = s.get("run_url","")
            link_html = f'&nbsp;<a href="{run_url}" target="_blank" style="color:#6C63FF;font-size:12px">View logs</a>' if run_url else ""
            st.markdown(f"""
            <div class="card">
              <div>
                <div class="card-title">{ic("smart_toy")} &nbsp;{name}</div>
                <div class="card-sub">{fix}</div>
              </div>
              <div>{_pill(s.get('conclusion',''))}{link_html}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown(f'<div class="sec-hdr">{ic("check_circle")} Healthy</div>', unsafe_allow_html=True)
    for name, s in healthy:
        st.markdown(f"""
        <div class="card">
          <div class="card-title">{ic("smart_toy")} &nbsp;{name}
            <span class="card-sub" style="font-weight:400;margin-left:8px">{_ago(s.get('last_run_at',''))}</span>
          </div>
          {_pill(s.get('conclusion',''))}
        </div>""", unsafe_allow_html=True)


def page_videos(report, upload_log):
    video_stats = report.get("video_stats", [])
    st.markdown(f'<div class="sec-hdr">{ic("play_circle")} Video Analytics</div>', unsafe_allow_html=True)

    if video_stats:
        sorted_vids = sorted(video_stats, key=lambda x: x.get("views",0), reverse=True)
        tv = sum(v.get("views",0) for v in video_stats)
        tl = sum(v.get("likes",0) for v in video_stats)

        c1, c2, c3 = st.columns(3)
        for col, icon_n, label, val in [
            (c1,"visibility","Total Views (tracked)",f"{tv:,}"),
            (c2,"thumb_up",  "Total Likes",          f"{tl:,}"),
            (c3,"bar_chart", "Avg Views / Video",    f"{tv//max(len(video_stats),1):,}"),
        ]:
            with col:
                st.markdown(f'<div class="stat-card"><span class="material-symbols-rounded stat-icon">{icon_n}</span><div class="stat-label">{label}</div><div class="stat-value">{val}</div></div>', unsafe_allow_html=True)

        try:
            import plotly.graph_objects as go
            top10  = sorted_vids[:10]
            titles = [v["title"][:40]+"…" if len(v["title"])>40 else v["title"] for v in top10]
            fig = go.Figure(go.Bar(x=[v["views"] for v in top10], y=titles, orientation="h",
                                   marker=dict(color="#6C63FF")))
            fig.update_layout(height=360, margin=dict(l=0,r=20,t=40,b=20),
                              title=dict(text="Top 10 Videos by Views",font=dict(color="#FAFAFA",size=14)),
                              xaxis=dict(color="#9CA3AF",gridcolor="#2D3148"),
                              yaxis=dict(color="#FAFAFA"),
                              plot_bgcolor="#1A1D2E", paper_bgcolor="#0E1117",
                              font=dict(color="#9CA3AF"))
            st.plotly_chart(fig, use_container_width=True)
        except ImportError:
            pass

        for v in sorted_vids:
            st.markdown(f"""
            <div class="card">
              <a href="{v.get('url','#')}" target="_blank" style="color:#FAFAFA;text-decoration:none;font-size:14px;font-weight:600;flex:1">{v['title']}</a>
              <span style="font-size:13px;color:#9CA3AF;white-space:nowrap;margin-left:16px">{ic("visibility")} {v.get('views',0):,} &nbsp; {ic("thumb_up")} {v.get('likes',0)} &nbsp; {ic("chat_bubble")} {v.get('comments',0)}</span>
            </div>""", unsafe_allow_html=True)

    elif upload_log:
        st.info("Add YOUTUBE_API_KEY to GitHub Secrets for live view counts.")
        for v in reversed(upload_log[-20:]):
            badge = '<span class="vbs">Short</span>' if v.get("type")=="shorts" else '<span class="vbr">Regular</span>'
            url   = v.get("url", f"https://youtu.be/{v.get('video_id','')}")
            st.markdown(f"""
            <div class="card">
              {badge}&nbsp;
              <a href="{url}" target="_blank" style="color:#FAFAFA;text-decoration:none;font-size:14px;font-weight:600;flex:1">{v.get('title','—')}</a>
              <span style="font-size:12px;color:#9CA3AF">{_ago(v.get('uploaded_at',''))}</span>
            </div>""", unsafe_allow_html=True)


def page_competitors(report):
    competitors = report.get("competitors", [])
    ch          = report.get("channel_stats", {})
    analysis    = report.get("analysis", {})
    our_subs    = ch.get("subscribers", 0)

    st.markdown(f'<div class="sec-hdr">{ic("group")} Competitor Analysis</div>', unsafe_allow_html=True)

    if competitors:
        all_ch = sorted(
            competitors + ([{"name":"MindShift (Us)","subscribers":our_subs,
                             "total_views":ch.get("total_views",0),
                             "video_count":ch.get("video_count",0)}] if our_subs else []),
            key=lambda x: x.get("subscribers",0), reverse=True,
        )
        try:
            import plotly.graph_objects as go
            names  = [c["name"] for c in all_ch]
            subs   = [c.get("subscribers",0) for c in all_ch]
            colors = ["#FFD700" if "Us" in c["name"] else "#6C63FF" for c in all_ch]
            fig = go.Figure(go.Bar(x=names, y=subs, marker_color=colors,
                                   text=[f"{s:,}" for s in subs], textposition="outside"))
            fig.update_layout(height=360, margin=dict(l=20,r=20,t=50,b=20),
                              title=dict(text="Subscribers vs Competitors",font=dict(color="#FAFAFA",size=14)),
                              yaxis=dict(title="Subscribers",color="#9CA3AF",gridcolor="#2D3148"),
                              xaxis=dict(color="#FAFAFA"),
                              plot_bgcolor="#1A1D2E", paper_bgcolor="#0E1117",
                              font=dict(color="#9CA3AF"))
            st.plotly_chart(fig, use_container_width=True)
        except ImportError:
            pass

        for c in all_ch:
            border = "border-left:3px solid #FFD700" if "Us" in c.get("name","") else ""
            st.markdown(f"""
            <div class="card" style="{border}">
              <div>
                <div class="card-title">{ic("person")} &nbsp;{c['name']}</div>
                <div class="card-sub">{c.get('video_count',0)} videos · {c.get('total_views',0):,} views</div>
              </div>
              <div style="font-size:20px;font-weight:700;color:#FAFAFA">{c.get('subscribers',0):,} <span style="font-size:12px;color:#9CA3AF">subs</span></div>
            </div>""", unsafe_allow_html=True)

        st.markdown(f'<div class="sec-hdr">{ic("lightbulb")} AI Insights</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="ic b">{ic("psychology")} &nbsp;{analysis.get("competitor_insights","No analysis yet.")}</div>', unsafe_allow_html=True)

    else:
        st.warning("Add YOUTUBE_API_KEY to GitHub Secrets to enable competitor tracking.")


def page_recommendations(report):
    analysis = report.get("analysis", {})
    fixes    = report.get("agent_improvement_tips", {})

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f'<div class="sec-hdr">{ic("rocket_launch")} Growth Tactics</div>', unsafe_allow_html=True)
        for t in analysis.get("growth_tactics", ["Run head agent for analysis"]):
            st.markdown(f'<div class="ic b">{ic("star")} &nbsp;{t}</div>', unsafe_allow_html=True)

        st.markdown(f'<div class="sec-hdr">{ic("person_add")} Subscriber Tips</div>', unsafe_allow_html=True)
        for t in analysis.get("follower_growth_tips", []):
            st.markdown(f'<div class="ic g">{ic("check")} &nbsp;{t}</div>', unsafe_allow_html=True)

    with col2:
        st.markdown(f'<div class="sec-hdr">{ic("bar_chart")} View Drop Analysis</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="ic">{analysis.get("view_drop_analysis","Run head agent for analysis.")}</div>', unsafe_allow_html=True)

        st.markdown(f'<div class="sec-hdr">{ic("build")} Agent Fixes</div>', unsafe_allow_html=True)
        if fixes:
            for agent, tip in fixes.items():
                st.markdown(f'<div class="ic a">{ic("smart_toy")} &nbsp;<b>{agent}:</b> {tip}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="ic g">{ic("verified")} All agents healthy</div>', unsafe_allow_html=True)

    with st.expander("Raw JSON report"):
        st.json(report)


# ── Entry ─────────────────────────────────────────────────────────────────────

def main():
    if not _check_password():
        return

    page       = _sidebar()
    report     = _fetch("head_agent_report.json") or {}
    upload_log = _fetch("upload_log.json")        or []

    if not report:
        st.markdown(f'<div class="ic a">{ic("info")} Head agent has not run yet. Go to <b>GitHub → Actions → Agent 0 — Head Agent → Run workflow</b></div>', unsafe_allow_html=True)
        return

    if   page == "Overview":        page_overview(report, upload_log)
    elif page == "Agents":          page_agents(report)
    elif page == "Videos":          page_videos(report, upload_log)
    elif page == "Competitors":     page_competitors(report)
    elif page == "Recommendations": page_recommendations(report)


if __name__ == "__main__":
    main()
