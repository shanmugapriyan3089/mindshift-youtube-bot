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
    "Video Reviewer":            "agent_video_reviewer.yml",
}

# Maps workflow name → agents_state report key
AGENT_REPORT_KEYS = {
    "Twitter":        "twitter",
    "Instagram":      "instagram",
    "Reddit":         "reddit",
    "Quora":          "quora",
    "Analytics":      "analytics",
    "Revenue Tracker":"revenue_tracker",
    "Trend Scout":    "trend_scout",
    "Competitor Spy": "competitor_spy",
    "SEO Optimizer":  "seo_optimizer",
    "Video Reviewer": "video_reviewer",
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


# ── Agent State Reports ───────────────────────────────────────────────────────

def _read_all_agent_reports() -> dict:
    """Read every agent's self-reported state from agents_state/*.json."""
    reports = {}
    state_dir = "agents_state"
    if not os.path.exists(state_dir):
        return reports
    for fname in os.listdir(state_dir):
        if fname.endswith("_report.json"):
            key = fname.replace("_report.json", "")
            try:
                with open(os.path.join(state_dir, fname)) as f:
                    reports[key] = json.load(f)
            except Exception:
                pass
    return reports


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


def _analyze_all(upload_stats: dict, yt_stats: dict, workflow_statuses: dict,
                  competitors: list, agent_reports: dict, video_review: dict) -> dict:
    """Comprehensive AI analysis across all agents + channel. Returns fix plan + growth strategy."""

    failed  = [n for n, s in workflow_statuses.items() if s.get("conclusion") in ("failure", "error", "timed_out")]
    success = [n for n, s in workflow_statuses.items() if s.get("conclusion") == "success"]
    our_subs = yt_stats.get("subscribers", 0)

    video_perf = "No video data yet"
    if yt_stats.get("video_stats"):
        top = sorted(yt_stats["video_stats"], key=lambda x: x["views"], reverse=True)[:5]
        video_perf = "\n".join(f"  {v['title'][:55]}: {v['views']:,} views" for v in top)

    comp_lines = "No competitor data" if not competitors else "\n".join(
        f"  {c['name']}: {c.get('subscribers',0):,} subs"
        for c in competitors
    )

    # Build per-agent report block
    agent_block = ""
    for wf_name, report_key in AGENT_REPORT_KEYS.items():
        wf_status  = workflow_statuses.get(wf_name, {})
        conclusion = wf_status.get("conclusion", "never_run")
        report     = agent_reports.get(report_key, {})
        summary    = report.get("summary", "no report yet")
        errors     = report.get("errors", [])
        err_str    = f" | ERRORS: {'; '.join(errors[:2])}" if errors else ""
        agent_block += f"  {wf_name} [{conclusion}]: {summary}{err_str}\n"

    # Video reviewer insights
    vr = video_review.get("strategy", {})
    vr_block = ""
    if vr:
        vr_block = f"""
VIDEO REVIEWER SAYS (weekly deep analysis):
- Content variety score: {video_review.get('our_channel', {}).get('variety_score','?')}/10
- Change urgency: {vr.get('urgency_score','?')}/10
- What competitors do that works: {vr.get('competitor_insights', {}).get('what_works_for_them','N/A')}
- Trending opportunity: {vr.get('trending_opportunity','N/A')}
- 30-day strategy: {vr.get('30_day_strategy','N/A')}"""

    prompt = f"""You are the master controller of a fully-automated YouTube channel "MindShift Productivity".
Psychology/motivation niche, stick figure animation, daily uploads. Goal: reach 1,000 subscribers fast.

CHANNEL STATS:
- Subscribers: {our_subs:,}
- Total views: {yt_stats.get('total_views', 0):,}
- Videos: {upload_stats.get('regular_count', 0)} regular + {upload_stats.get('shorts_count', 0)} shorts

TOP VIDEOS:
{video_perf}

COMPETITORS:
{comp_lines}

ALL AGENT STATUS (what each agent last did and any errors):
{agent_block}
WORKFLOW HEALTH: {len(success)}/{len(workflow_statuses)} agents healthy, {len(failed)} failed
{vr_block}

Your job: produce a complete control-panel JSON.
For "fix_instructions", give SPECIFIC actionable instructions — not vague advice.
Example of bad fix: "Fix the Instagram agent"
Example of good fix: "Instagram agent is missing INSTAGRAM_ACCESS_TOKEN in GitHub Secrets → go to Settings → Secrets → add it"

Respond ONLY in valid JSON:
{{
  "channel_health_score": <1-10>,
  "what_is_working": ["3 specific things that ARE working"],
  "what_needs_improvement": ["3 things holding us back"],
  "urgent_actions": ["things that MUST be fixed today — empty list if all healthy"],
  "fix_instructions": {{
    "AgentName": "specific step-by-step fix for THIS agent's reported error"
  }},
  "growth_tactics": ["3 specific tactics to gain subscribers THIS week"],
  "next_video_topics": ["3 specific video topic suggestions based on trends + gaps"],
  "view_drop_analysis": "why views might be low and what to do — or 'Views look healthy'",
  "follower_growth_tips": ["3 concrete sub-growth tactics"]
}}"""

    try:
        text  = _ai_call(prompt)
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception as e:
        print(f"  [Head] Analysis parse error: {e}")

    return {
        "channel_health_score": 5,
        "what_is_working":       ["Content pipeline active"],
        "what_needs_improvement":["Need more data"],
        "urgent_actions":        [f"Fix failed: {', '.join(failed)}"] if failed else [],
        "fix_instructions":      {n: "Check GitHub Actions logs" for n in failed},
        "growth_tactics":        ["Post consistently", "Engage with comments", "SEO titles"],
        "next_video_topics":     ["Check video_review_report.json for suggestions"],
        "view_drop_analysis":    "Not enough data yet.",
        "follower_growth_tips":  ["Reply to every comment", "Post Shorts daily", "Share on WhatsApp"],
    }


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

    # 4b. All agent self-reports
    print("[Head] Reading all agent reports...")
    agent_reports = _read_all_agent_reports()
    print(f"  Found reports from: {', '.join(agent_reports.keys()) or 'none yet'}")

    # 4c. Video Reviewer report (generated by Agent 11 weekly)
    video_review = {}
    try:
        with open(VIDEO_REVIEW_FILE) as f:
            video_review = json.load(f)
        age_hours = (datetime.now(timezone.utc) - datetime.fromisoformat(
            video_review.get("generated_at", "2000-01-01T00:00:00+00:00")
        )).total_seconds() / 3600
        if age_hours < 200:
            print(f"[Head] Video review loaded (age: {age_hours:.0f}h)")
        else:
            video_review = {}
    except Exception:
        pass

    # 5. Comprehensive AI analysis
    print("[Head] Running comprehensive AI analysis...")
    analysis = _analyze_all(upload_stats, yt_stats, workflow_statuses,
                            competitors, agent_reports, video_review)

    # 6. Build and save report
    report = {
        "generated_at":        datetime.now(timezone.utc).isoformat(),
        "agent_statuses":      workflow_statuses,
        "agent_reports":       agent_reports,
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
        "video_review":        video_review.get("strategy", {}),
    }

    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"[Head] Report saved → {REPORT_FILE}")

    # 7. Build control-panel email
    score    = analysis.get("channel_health_score", "?")
    urgent   = analysis.get("urgent_actions", [])
    fixes    = analysis.get("fix_instructions", {})
    working  = analysis.get("what_is_working", [])
    improve  = analysis.get("what_needs_improvement", [])
    tactics  = analysis.get("growth_tactics", [])
    sub_tips = analysis.get("follower_growth_tips", [])
    next_vids= analysis.get("next_video_topics", [])

    subs_str = f"{yt_stats['subscribers']:,}" if yt_stats.get('subscribers') else "(add YOUTUBE_API_KEY)"

    lines = [
        "═"*60,
        "MINDSHIFT — DAILY CONTROL PANEL",
        f"{datetime.now().strftime('%A, %B %d %Y')}",
        "═"*60,
        "",
        f"Health Score : {score}/10",
        f"Subscribers  : {subs_str}",
        f"Total Views  : {yt_stats.get('total_views', 0):,}",
        f"Videos       : {upload_stats.get('regular_count',0)} regular + {upload_stats.get('shorts_count',0)} shorts",
        f"Agents       : {success_count}/{len(workflow_statuses)} healthy  |  {failed_count} failed",
        "",
    ]

    # Urgent actions first
    if urgent:
        lines += ["━"*60, "!! URGENT — FIX TODAY !!", "━"*60]
        for a in urgent:
            lines.append(f"  !! {a}")
        lines.append("")

    # Per-agent status table
    lines += ["━"*60, "ALL AGENT STATUS", "━"*60]
    STATUS_ICON = {"success": "✅", "failure": "❌", "error": "❌",
                   "timed_out": "⏱", "in_progress": "⏳", "never_run": "⬜"}
    for wf_name in WORKFLOWS:
        wf  = workflow_statuses.get(wf_name, {})
        con = wf.get("conclusion", "never_run")
        icon = STATUS_ICON.get(con, "❓")
        rkey = AGENT_REPORT_KEYS.get(wf_name, "")
        rep  = agent_reports.get(rkey, {})
        summary = rep.get("summary", "no report yet")
        lines.append(f"  {icon} {wf_name:<26} {summary[:55]}")
    lines.append("")

    # Fix instructions for any agent with errors or failures
    broken = {n for n, s in workflow_statuses.items()
              if s.get("conclusion") in ("failure", "error", "timed_out")}
    broken |= {wf for wf, rk in AGENT_REPORT_KEYS.items()
               if agent_reports.get(rk, {}).get("errors")}
    if broken or fixes:
        lines += ["━"*60, "HOW TO FIX EACH BROKEN AGENT", "━"*60]
        for agent_name, fix in fixes.items():
            lines.append(f"  >> {agent_name}:")
            lines.append(f"     {fix}")
            lines.append("")
        # Also show raw errors for agents with errors but not in AI fixes
        for wf_name in broken:
            if wf_name not in fixes:
                rkey = AGENT_REPORT_KEYS.get(wf_name, "")
                errs = agent_reports.get(rkey, {}).get("errors", [])
                run_url = workflow_statuses.get(wf_name, {}).get("run_url", "")
                lines.append(f"  >> {wf_name}: {'; '.join(errs) or 'check logs'}")
                if run_url:
                    lines.append(f"     Logs: {run_url}")
                lines.append("")

    # Channel performance
    lines += ["━"*60, "CHANNEL PERFORMANCE", "━"*60]
    lines += ["WORKING WELL:", *[f"  + {w}" for w in working], ""]
    lines += ["NEEDS WORK:",  *[f"  → {i}" for i in improve], ""]
    lines.append(f"Views: {analysis.get('view_drop_analysis','')}")
    lines.append("")

    # Growth plan
    lines += ["━"*60, "GROWTH PLAN THIS WEEK", "━"*60]
    lines += ["TACTICS:", *[f"  * {t}" for t in tactics], ""]
    lines += ["SUBSCRIBER TIPS:", *[f"  * {t}" for t in sub_tips], ""]
    if next_vids:
        lines += ["NEXT VIDEO TOPICS:", *[f"  → {v}" for v in next_vids], ""]

    # Video reviewer intelligence
    vr = video_review.get("strategy", {})
    if vr:
        lines += ["━"*60, "VIDEO REVIEWER INTEL (Agent 11 — weekly)", "━"*60]
        if vr.get("urgency_score"):
            lines.append(f"Content Change Urgency: {vr['urgency_score']}/10")
        if vr.get("trending_opportunity"):
            lines.append(f"Trending Now: {vr['trending_opportunity']}")
        next_t = vr.get("next_5_video_titles", [])
        if next_t:
            lines.append("Suggested Titles:")
            for i, t in enumerate(next_t[:3], 1):
                lines.append(f"  {i}. {t}")
        if vr.get("hook_advice"):
            lines.append(f"Hook: {vr['hook_advice']}")
        if vr.get("subscribe_growth_tactic"):
            lines.append(f"Sub Tactic: {vr['subscribe_growth_tactic']}")
        if vr.get("30_day_strategy"):
            lines.append(f"30-Day Plan: {vr['30_day_strategy']}")
        lines.append("")

    lines += ["═"*60, "Full report: head_agent_report.json committed to repo", "═"*60]

    body = "\n".join(lines)
    send(body, subject=f"MindShift Control Panel: {score}/10 health | {success_count}/{len(workflow_statuses)} agents OK | {failed_count} need fix")
    print("[Agent 0: Head] Done.")


if __name__ == "__main__":
    main()
