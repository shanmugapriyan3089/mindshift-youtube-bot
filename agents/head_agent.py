"""
Agent 0: Head Agent — Master Orchestrator
Runs daily, checks every agent, analyzes channel performance, writes head_agent_report.json.
Sends a summary email/Telegram. Dashboard reads this report file.

Free AI stack: Groq (primary) + DeepSeek (deeper analysis, add DEEPSEEK_API_KEY to secrets)
"""
import os, sys, re, json, pickle, requests
from datetime import datetime, timezone
from groq import Groq

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import GROQ_API_KEY, DAILY_TOPICS

REPO_OWNER  = "shanmugapriyan3089"
REPO_NAME   = "mindshift-youtube-bot"
REPORT_FILE        = "head_agent_report.json"
VIDEO_REVIEW_FILE  = "video_review_report.json"
CHANNEL_URL = "https://youtube.com/@MindShiftProductivity"

WORKFLOWS = {
    "Regular Video (standard)":  "daily_regular.yml",
    "Regular Video (mixed)":     "daily_mixed_regular.yml",
    "Regular Video (stock)":     "daily_stock_regular.yml",
    "Shorts (standard)":         "daily_shorts.yml",
    "Shorts (mixed)":            "daily_mixed_shorts.yml",
    "Shorts (stock)":            "daily_stock_shorts.yml",
    "Twitter":                   "agent_twitter.yml",
    "Instagram":                 "agent_instagram.yml",
    "Reddit":                    "agent_reddit.yml",
    "Quora":                     "agent_quora.yml",
    "Trend Scout":               "agent_trend_scout.yml",
    "Competitor Spy":            "agent_competitor_spy.yml",
    "SEO Optimizer":             "agent_seo.yml",
    "Analytics":                 "agent_analytics.yml",
    "Revenue Tracker":           "agent_revenue.yml",
}

COMPETITORS = [
    {"name": "Productive Peter",    "search": "Productive Peter"},
    {"name": "Trust Me Bro",        "search": "Trust Me Bro psychology"},
    {"name": "Charisma on Command", "search": "Charisma on Command"},
    {"name": "Sprouts",             "search": "Sprouts psychology animation"},
    {"name": "Better Ideas",        "search": "Better Ideas philosophy motivation"},
    {"name": "Improvement Pill",    "search": "Improvement Pill psychology"},
]


# ── GitHub Actions Status ─────────────────────────────────────────────────────

def _check_workflow_statuses(github_token: str) -> dict:
    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    statuses = {}
    for name, workflow_file in WORKFLOWS.items():
        try:
            url = (f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}"
                   f"/actions/workflows/{workflow_file}/runs?per_page=1")
            r = requests.get(url, headers=headers, timeout=15)
            if r.status_code == 200:
                runs = r.json().get("workflow_runs", [])
                if runs:
                    run = runs[0]
                    statuses[name] = {
                        "last_run_at": run.get("created_at", ""),
                        "conclusion":  run.get("conclusion") or run.get("status", "in_progress"),
                        "run_url":     run.get("html_url", ""),
                    }
                else:
                    statuses[name] = {"last_run_at": None, "conclusion": "never_run", "run_url": ""}
            else:
                statuses[name] = {"last_run_at": None, "conclusion": f"http_{r.status_code}", "run_url": ""}
        except Exception as e:
            statuses[name] = {"last_run_at": None, "conclusion": "error", "run_url": ""}
            print(f"  [Head] Workflow status error for {name}: {e}")
    return statuses


# ── Upload Log Stats ──────────────────────────────────────────────────────────

def _get_upload_stats() -> dict:
    try:
        with open("upload_log.json") as f:
            log = json.load(f)
    except Exception:
        return {"total_uploaded": 0, "regular_count": 0, "shorts_count": 0}

    regulars = sorted([v for v in log if v.get("type") == "regular"],
                      key=lambda x: x.get("uploaded_at", ""), reverse=True)
    shorts   = sorted([v for v in log if v.get("type") == "shorts"],
                      key=lambda x: x.get("uploaded_at", ""), reverse=True)
    return {
        "total_uploaded": len(log),
        "regular_count":  len(regulars),
        "shorts_count":   len(shorts),
        "last_regular":   regulars[0] if regulars else None,
        "last_short":     shorts[0]   if shorts   else None,
        "all_videos":     log,
    }


# ── YouTube Data API ──────────────────────────────────────────────────────────

def _get_youtube_stats(upload_log_ids: list) -> dict:
    """Get our channel stats + per-video stats using existing OAuth token."""
    try:
        from googleapiclient.discovery import build
        from google.auth.transport.requests import Request

        if not os.path.exists("youtube_token.pickle"):
            return {}
        with open("youtube_token.pickle", "rb") as f:
            creds = pickle.load(f)
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())

        yt = build("youtube", "v3", credentials=creds, cache_discovery=False)

        # Channel stats
        ch = yt.channels().list(mine=True, part="statistics,snippet").execute()
        ch_item = ch["items"][0] if ch.get("items") else {}
        stats    = ch_item.get("statistics", {})

        # Video-level stats for recent uploads
        video_stats = []
        if upload_log_ids:
            # Batch: max 50 per request
            for i in range(0, len(upload_log_ids), 50):
                batch = upload_log_ids[i:i+50]
                vr = yt.videos().list(id=",".join(batch), part="statistics,snippet").execute()
                for item in vr.get("items", []):
                    vs = item.get("statistics", {})
                    video_stats.append({
                        "video_id": item["id"],
                        "title":    item["snippet"]["title"][:70],
                        "views":    int(vs.get("viewCount",    0)),
                        "likes":    int(vs.get("likeCount",    0)),
                        "comments": int(vs.get("commentCount", 0)),
                        "url":      f"https://youtu.be/{item['id']}",
                    })

        return {
            "subscribers":   int(stats.get("subscriberCount", 0)),
            "total_views":   int(stats.get("viewCount", 0)),
            "video_count":   int(stats.get("videoCount", 0)),
            "channel_title": ch_item.get("snippet", {}).get("title", ""),
            "video_stats":   video_stats,
        }
    except Exception as e:
        print(f"  [Head] YouTube stats error: {e}")
        return {}


def _get_competitor_stats(api_key: str) -> list:
    """Get competitor channel stats via YouTube Data API (public, no OAuth needed)."""
    if not api_key:
        return []
    results = []
    for comp in COMPETITORS:
        try:
            # Search for channel by name
            r = requests.get(
                "https://www.googleapis.com/youtube/v3/search",
                params={"q": comp["search"], "type": "channel", "part": "snippet",
                        "maxResults": 1, "key": api_key},
                timeout=15,
            )
            items = r.json().get("items", []) if r.ok else []
            if not items:
                continue
            channel_id = items[0]["id"]["channelId"]

            # Get stats
            r2 = requests.get(
                "https://www.googleapis.com/youtube/v3/channels",
                params={"id": channel_id, "part": "statistics,snippet", "key": api_key},
                timeout=15,
            )
            ch_items = r2.json().get("items", []) if r2.ok else []
            if not ch_items:
                continue
            s = ch_items[0].get("statistics", {})
            results.append({
                "name":        comp["name"],
                "subscribers": int(s.get("subscriberCount", 0)),
                "total_views": int(s.get("viewCount",       0)),
                "video_count": int(s.get("videoCount",      0)),
            })
        except Exception as e:
            print(f"  [Head] Competitor {comp['name']}: {e}")
    return results


# ── AI Analysis ───────────────────────────────────────────────────────────────

def _ai_call(prompt: str) -> str:
    """Try DeepSeek first (better reasoning), fall back to Groq."""
    deepseek_key = os.getenv("DEEPSEEK_API_KEY")
    if deepseek_key:
        try:
            import openai
            client = openai.OpenAI(api_key=deepseek_key, base_url="https://api.deepseek.com")
            resp = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3, max_tokens=1000,
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            print(f"  [Head] DeepSeek fallback to Groq: {e}")

    client = Groq(api_key=GROQ_API_KEY)
    resp = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3, max_tokens=1000,
    )
    return resp.choices[0].message.content.strip()


def _analyze(upload_stats: dict, yt_stats: dict, workflow_statuses: dict, competitors: list) -> dict:
    failed  = [n for n, s in workflow_statuses.items() if s.get("conclusion") in ("failure", "error", "timed_out")]
    success = [n for n, s in workflow_statuses.items() if s.get("conclusion") == "success"]

    video_perf = "No video data yet"
    if yt_stats.get("video_stats"):
        top = sorted(yt_stats["video_stats"], key=lambda x: x["views"], reverse=True)[:5]
        video_perf = "\n".join(f"  {v['title'][:55]}: {v['views']:,} views, {v['likes']} likes" for v in top)

    comp_lines = "No competitor data" if not competitors else "\n".join(
        f"  {c['name']}: {c['subscribers']:,} subs, {c['video_count']} videos, {c['total_views']:,} total views"
        for c in competitors
    )
    our_subs = yt_stats.get("subscribers", 0)

    prompt = f"""Analyze this YouTube channel "MindShift Productivity" (psychology/motivation, stick figure animation):

OUR STATS:
- Subscribers: {our_subs:,}
- Total views: {yt_stats.get('total_views', 0):,}
- Videos uploaded: {upload_stats.get('regular_count', 0)} regular + {upload_stats.get('shorts_count', 0)} shorts

TOP VIDEOS (by views):
{video_perf}

COMPETITORS:
{comp_lines}

AGENT HEALTH:
- Working agents ({len(success)}): {', '.join(success) or 'none'}
- Failed agents ({len(failed)}): {', '.join(failed) or 'none'}

TOPICS WE COVER: {', '.join(DAILY_TOPICS[:6])}

Produce a JSON analysis. Be SPECIFIC — reference actual numbers and competitor names:
{{
  "channel_health_score": <1-10 integer>,
  "what_is_working": ["3 specific things working well"],
  "what_needs_improvement": ["3 specific things to improve"],
  "growth_tactics": ["3 actionable tactics for this week"],
  "urgent_actions": ["things to fix immediately, empty list if none"],
  "competitor_insights": "2-3 sentences on what competitors do that we should learn from or avoid",
  "view_drop_analysis": "if views seem low, why and what to do — or 'Views look healthy' if fine",
  "follower_growth_tips": ["3 specific tactics to grow subscribers faster"]
}}

Output ONLY the JSON. No explanation."""

    try:
        text  = _ai_call(prompt)
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception as e:
        print(f"  [Head] Analysis parse error: {e}")

    # Safe fallback
    return {
        "channel_health_score": 5,
        "what_is_working": ["Content pipeline is active"],
        "what_needs_improvement": ["Need more data for full analysis"],
        "growth_tactics": ["Post consistently and engage with comments"],
        "urgent_actions": [f"Fix failed agents: {', '.join(failed)}"] if failed else [],
        "competitor_insights": "Continue monitoring Productive Peter and Trust Me Bro for upload frequency.",
        "view_drop_analysis": "Not enough data yet.",
        "follower_growth_tips": ["Respond to every comment in first 24h", "Post Shorts daily", "SEO-optimized titles"],
    }


# ── Per-Agent Improvement Suggestions ────────────────────────────────────────

def _improve_agents(workflow_statuses: dict, upload_stats: dict) -> dict:
    """Generate specific improvement suggestions for each agent."""
    failed = [n for n, s in workflow_statuses.items() if s.get("conclusion") not in ("success", "in_progress", "never_run")]
    if not failed:
        return {}

    prompt = f"""These GitHub Actions agents for a YouTube automation pipeline are failing:
{chr(10).join(f"  - {name}" for name in failed)}

The pipeline makes psychology/motivation YouTube videos.
For each failed agent, suggest in 1-2 sentences what likely went wrong and how to fix it.

Return as JSON: {{"AgentName": "diagnosis + fix"}}"""

    try:
        text  = _ai_call(prompt)
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception:
        pass
    return {name: "Check GitHub Actions logs for details" for name in failed}


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    from agents.notifier import send

    github_token = os.getenv("GITHUB_TOKEN", "")
    yt_api_key   = os.getenv("YOUTUBE_API_KEY", "")

    print("[Agent 0: Head] Starting master analysis...")

    # 1. Workflow health
    print("[Head] Checking all agent statuses via GitHub API...")
    workflow_statuses = _check_workflow_statuses(github_token) if github_token else {}
    failed_count   = sum(1 for s in workflow_statuses.values() if s.get("conclusion") in ("failure", "error", "timed_out"))
    success_count  = sum(1 for s in workflow_statuses.values() if s.get("conclusion") == "success")

    # 2. Upload log
    print("[Head] Reading upload logs...")
    upload_stats = _get_upload_stats()
    video_ids    = [v["video_id"] for v in upload_stats.get("all_videos", []) if v.get("video_id")]

    # 3. YouTube stats (our channel + per-video)
    print("[Head] Fetching YouTube channel stats...")
    yt_stats = _get_youtube_stats(video_ids[-20:])  # last 20 videos

    # 4. Competitors
    print("[Head] Fetching competitor stats...")
    competitors = _get_competitor_stats(yt_api_key)

    # 4b. Video Reviewer report (generated by Agent 11 weekly)
    video_review = {}
    try:
        with open(VIDEO_REVIEW_FILE) as f:
            video_review = json.load(f)
        age_hours = (datetime.now(timezone.utc) - datetime.fromisoformat(
            video_review.get("generated_at", "2000-01-01T00:00:00+00:00")
        )).total_seconds() / 3600
        if age_hours < 200:   # use if less than ~8 days old
            print(f"[Head] Video review loaded (age: {age_hours:.0f}h)")
        else:
            video_review = {}
    except Exception:
        pass

    # 5. AI analysis
    print("[Head] Running AI analysis...")
    analysis        = _analyze(upload_stats, yt_stats, workflow_statuses, competitors)
    agent_fixes     = _improve_agents(workflow_statuses, upload_stats)

    # 6. Build and save report
    report = {
        "generated_at":        datetime.now(timezone.utc).isoformat(),
        "agent_statuses":      workflow_statuses,
        "agent_health_summary": {
            "total":   len(workflow_statuses),
            "healthy": success_count,
            "failed":  failed_count,
        },
        "upload_stats":        {k: v for k, v in upload_stats.items() if k != "all_videos"},
        "channel_stats":       {k: v for k, v in yt_stats.items() if k != "video_stats"},
        "video_stats":         yt_stats.get("video_stats", []),
        "competitors":         competitors,
        "analysis":            analysis,
        "agent_improvement_tips": agent_fixes,
        "video_review":        video_review.get("strategy", {}),
    }

    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"[Head] Report saved → {REPORT_FILE}")

    # 7. Send notification
    score    = analysis.get("channel_health_score", "?")
    urgent   = analysis.get("urgent_actions", [])
    working  = analysis.get("what_is_working", [])
    improve  = analysis.get("what_needs_improvement", [])
    tactics  = analysis.get("growth_tactics", [])
    sub_tips = analysis.get("follower_growth_tips", [])

    lines = [
        f"MINDSHIFT — Daily Channel Report",
        f"Health Score: {score}/10  |  Agents: {success_count}/{len(workflow_statuses)} healthy",
        f"Subscribers: {yt_stats.get('subscribers', 'n/a'):,}" if yt_stats.get('subscribers') else "Subscribers: (add YOUTUBE_API_KEY for live stats)",
        f"Videos uploaded: {upload_stats.get('regular_count',0)} regular + {upload_stats.get('shorts_count',0)} shorts",
        "",
    ]
    if urgent:
        lines += ["URGENT:", *[f"  !! {a}" for a in urgent], ""]
    if failed_count:
        lines += [f"FAILED AGENTS ({failed_count}):",
                  *[f"  x {n}" for n, s in workflow_statuses.items()
                    if s.get('conclusion') not in ('success','in_progress','never_run')], ""]
    lines += ["WHAT'S WORKING:",  *[f"  + {w}" for w in working],  ""]
    lines += ["NEEDS WORK:",       *[f"  -> {i}" for i in improve], ""]
    lines += ["GROWTH TACTICS:",   *[f"  * {t}" for t in tactics],  ""]
    lines += ["SUBSCRIBER TIPS:",  *[f"  * {t}" for t in sub_tips], ""]
    lines += ["", f"Competitor note: {analysis.get('competitor_insights', '')}"]
    lines += ["", f"View drop check: {analysis.get('view_drop_analysis', '')}"]

    # Video Reviewer intelligence (Agent 11 — runs weekly)
    vr = video_review.get("strategy", {})
    if vr:
        lines += ["", "─"*50, "VIDEO REVIEWER INTELLIGENCE (Agent 11)", "─"*50]
        urgency = vr.get("urgency_score")
        if urgency:
            lines.append(f"Change Urgency: {urgency}/10")
        trending = vr.get("trending_opportunity")
        if trending:
            lines.append(f"Trending Now: {trending}")
        next_titles = vr.get("next_5_video_titles", [])
        if next_titles:
            lines.append("Suggested Next Titles:")
            for i, t in enumerate(next_titles[:3], 1):
                lines.append(f"  {i}. {t}")
        hook = vr.get("hook_advice")
        if hook:
            lines.append(f"Hook Tip: {hook}")
        sub_tactic = vr.get("subscribe_growth_tactic")
        if sub_tactic:
            lines.append(f"Sub Tactic: {sub_tactic}")
        strategy_30 = vr.get("30_day_strategy")
        if strategy_30:
            lines.append(f"30-Day Strategy: {strategy_30}")

    lines += ["", "Full dashboard: deploy dashboard/app.py to Streamlit Cloud"]

    send("\n".join(lines), subject=f"MindShift Report: Health {score}/10, {success_count}/{len(workflow_statuses)} agents OK")
    print("[Agent 0: Head] Done.")


if __name__ == "__main__":
    main()
