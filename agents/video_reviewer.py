"""
Agent 11: Advanced Video Reviewer + Competitor Intelligence
- Analyzes our content for variety, title patterns, visual sameness
- Checks competitors (Productive Peter, Trust Me Bro, etc.) — latest videos + view counts
- Finds trending psychology/productivity topics via web search
- Deep AI analysis via GLM or Groq — specific actions to grow views + subs
- Saves video_review_report.json → Head Agent reads this for daily recommendations
Runs every Sunday.
"""
import os, sys, json, re, time
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

UPLOAD_LOG   = "upload_log.json"
REPORT_FILE  = "video_review_report.json"
GLM_BASE     = "https://open.bigmodel.cn/api/paas/v4/"
GLM_MODEL    = os.getenv("GLM_MODEL", "glm-4-flash")

# Competitors to track — name used for YouTube search
COMPETITORS = [
    "Productive Peter",
    "Trust Me Bro",
    "Charisma on Command",
    "Improvement Pill",
    "Better Ideas",
    "Sprouts",
]


# ── Helpers ───────────────────────────────────────────────────────────────────

def _load_json(path, default):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return default


def _save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def _ai_call(prompt: str) -> str:
    """Try GLM first, fall back to Groq."""
    glm_key = os.getenv("GLM_API_KEY")
    if glm_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=glm_key, base_url=GLM_BASE)
            resp = client.chat.completions.create(
                model=GLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2500,
                temperature=0.3,
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            print(f"  [Reviewer] GLM failed ({e}), falling back to Groq")

    import groq
    client = groq.Groq(api_key=os.getenv("GROQ_API_KEY"))
    resp = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2500,
        temperature=0.3,
    )
    return resp.choices[0].message.content.strip()


def _parse_json_from_response(raw: str) -> dict:
    match = re.search(r'\{[\s\S]*\}', raw)
    if match:
        try:
            return json.loads(match.group())
        except Exception:
            pass
    return {"raw": raw}


# ── Our channel analysis ──────────────────────────────────────────────────────

def _check_title_overlap(videos: list) -> list:
    STOPS = {"the","a","an","is","are","you","your","why","how","what","when","to",
             "and","or","of","in","for","that","this","it","with","can","do","not",
             "be","have","has","will","just","from","on","at","by","but","more","all",
             "its","our","we","i","my","they","them","their","about","if","so","no"}
    flagged = []
    for i in range(len(videos)):
        for j in range(i + 1, len(videos)):
            w1 = set(videos[i].get("title","").lower().split()) - STOPS
            w2 = set(videos[j].get("title","").lower().split()) - STOPS
            if len(w1) < 3 or len(w2) < 3:
                continue
            overlap = len(w1 & w2) / min(len(w1), len(w2))
            if overlap > 0.5:
                flagged.append({
                    "title_a": videos[i].get("title",""),
                    "title_b": videos[j].get("title",""),
                    "overlap_pct": round(overlap * 100),
                })
    return flagged


def _analyze_our_content(regulars: list, shorts: list) -> dict:
    all_titles = [v.get("title","") for v in (regulars + shorts)]
    titles_str = "\n".join(f"- {t}" for t in all_titles)
    similar_pairs = _check_title_overlap(regulars + shorts)

    prompt = f"""Analyze these YouTube titles from a psychology/motivation channel (MindShift Productivity).

TITLES:
{titles_str}

KNOWN ISSUES:
- Stick figures used for animation — viewer said "all videos look the same"
- Need more visual and content variety

Respond in JSON only:
{{
  "variety_score": <1-10>,
  "title_formula_used": "describe the dominant pattern",
  "overused_words": ["word1", "word2", "word3"],
  "topics_overused": ["topic1", "topic2"],
  "emotion_range": "are the topics covering the full emotion spectrum or just one zone?",
  "missing_angles": ["angle 1", "angle 2", "angle 3"],
  "visual_variety_verdict": "based on animation style, what should change visually?",
  "recommended_next_titles": [
    "complete title 1 — different formula",
    "complete title 2",
    "complete title 3",
    "complete title 4",
    "complete title 5"
  ]
}}"""

    analysis = _parse_json_from_response(_ai_call(prompt))
    analysis["similar_pairs"] = similar_pairs
    analysis["total_videos"] = len(all_titles)
    return analysis


# ── Competitor intelligence ───────────────────────────────────────────────────

def _build_youtube(api_key: str):
    from googleapiclient.discovery import build
    return build("youtube", "v3", developerKey=api_key)


def _get_competitor_videos(youtube, channel_name: str) -> dict:
    """Get latest 8 videos + stats for a competitor channel."""
    try:
        # Find channel by name search
        s = youtube.search().list(
            q=channel_name, type="channel", maxResults=1, part="id,snippet"
        ).execute()
        if not s.get("items"):
            return {}

        channel_id    = s["items"][0]["id"]["channelId"]
        channel_title = s["items"][0]["snippet"]["title"]

        # Channel stats + uploads playlist
        ch = youtube.channels().list(
            part="contentDetails,statistics", id=channel_id
        ).execute()
        if not ch.get("items"):
            return {}

        ch_item    = ch["items"][0]
        uploads_id = ch_item["contentDetails"]["relatedPlaylists"]["uploads"]
        ch_stats   = ch_item.get("statistics", {})

        # Recent videos
        pl = youtube.playlistItems().list(
            playlistId=uploads_id, part="snippet", maxResults=8
        ).execute()
        video_ids = [i["snippet"]["resourceId"]["videoId"] for i in pl.get("items", [])]
        if not video_ids:
            return {}

        # Per-video stats
        vs = youtube.videos().list(
            part="statistics,snippet", id=",".join(video_ids)
        ).execute()

        videos = []
        for item in vs.get("items", []):
            sn = item["snippet"]
            st = item["statistics"]
            published = sn.get("publishedAt", "")[:10]
            videos.append({
                "title":        sn["title"],
                "video_id":     item["id"],
                "published":    published,
                "views":        int(st.get("viewCount", 0)),
                "likes":        int(st.get("likeCount", 0)),
                "comments":     int(st.get("commentCount", 0)),
            })

        videos.sort(key=lambda x: x["views"], reverse=True)

        return {
            "channel_name": channel_title,
            "subscribers":  int(ch_stats.get("subscriberCount", 0)),
            "total_views":  int(ch_stats.get("viewCount", 0)),
            "recent_videos": videos,
            "avg_views_recent": int(sum(v["views"] for v in videos) / max(1, len(videos))),
        }
    except Exception as e:
        print(f"  [Reviewer] Competitor '{channel_name}' fetch failed: {e}")
        return {}


def _fetch_all_competitors(api_key: str) -> dict:
    if not api_key:
        print("  [Reviewer] No YOUTUBE_API_KEY — skipping competitor fetch")
        return {}

    youtube = _build_youtube(api_key)
    results = {}
    for name in COMPETITORS:
        print(f"  [Reviewer] Fetching competitor: {name}...")
        data = _get_competitor_videos(youtube, name)
        if data:
            results[name] = data
        time.sleep(0.5)   # be polite to the API
    return results


# ── Trending topics ───────────────────────────────────────────────────────────

def _get_trending_topics() -> list:
    """Search DuckDuckGo for trending psychology/productivity topics."""
    import requests
    queries = [
        "trending psychology self improvement YouTube topics 2025",
        "viral motivation mindset video topics this month",
    ]
    topics = []
    for q in queries:
        try:
            resp = requests.post(
                "https://lite.duckduckgo.com/lite/",
                data={"q": q, "df": "m"},
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
                timeout=15,
            )
            titles = re.findall(r'<a[^>]+class="result-link"[^>]*>([^<]{25,120})</a>', resp.text)
            topics.extend(t.strip() for t in titles[:6])
        except Exception as e:
            print(f"  [Reviewer] Trending search failed: {e}")
    return list(dict.fromkeys(topics))[:12]   # deduplicate, keep top 12


# ── Deep AI strategic analysis ────────────────────────────────────────────────

def _deep_strategic_analysis(our_analysis: dict, competitors: dict, trending: list) -> dict:
    """Full strategic analysis — what to do to grow views and subs."""

    # Build competitor summary
    comp_block = ""
    for name, data in competitors.items():
        if not data or not data.get("recent_videos"):
            continue
        subs = data.get("subscribers", 0)
        avg  = data.get("avg_views_recent", 0)
        comp_block += f"\n{name} ({subs:,} subs, avg {avg:,} views/video):\n"
        for v in data["recent_videos"][:5]:
            comp_block += f"  - [{v['views']:,} views] {v['title']}\n"

    our_titles = "\n".join(
        f"  - {p['title_a'][:60]} vs {p['title_b'][:60]} ({p['overlap_pct']}% same)"
        for p in our_analysis.get("similar_pairs", [])[:5]
    ) or "  (no duplicates found)"

    trending_block = "\n".join(f"  - {t}" for t in trending) if trending else "  (no data)"

    prompt = f"""You are a senior YouTube growth strategist. A psychology/motivation channel (MindShift Productivity) has ~50-100 subscribers and wants to grow fast.

OUR CONTENT PROBLEMS:
- Title variety score: {our_analysis.get('variety_score','?')}/10
- Dominant formula: {our_analysis.get('title_formula_used','?')}
- Overused topics: {', '.join(our_analysis.get('topics_overused', []))}
- Similar title pairs found:
{our_titles}

WHAT COMPETITORS ARE POSTING (and getting views):
{comp_block if comp_block else "  (no competitor data available)"}

TRENDING TOPICS RIGHT NOW:
{trending_block}

Our channel uses stick figure animation (2 characters, speech bubbles). We post daily.
Main problem: all videos look and sound similar. Viewer said "all same sticks just moving hands."

Respond ONLY in valid JSON — no markdown, no text outside the JSON:
{{
  "urgency_score": <1-10, how badly we need to change>,
  "competitor_insights": {{
    "what_works_for_them": "specific pattern in their top-performing videos",
    "title_formula_they_use": "describe their approach",
    "topics_crushing_it_now": ["topic 1", "topic 2", "topic 3"],
    "gap_we_can_exploit": "specific content angle nobody is covering well right now"
  }},
  "trending_opportunity": "single best trending topic we should cover this week",
  "next_5_video_titles": [
    "complete ready-to-use title 1 — totally different formula from our recent ones",
    "complete ready-to-use title 2",
    "complete ready-to-use title 3",
    "complete ready-to-use title 4",
    "complete ready-to-use title 5"
  ],
  "what_to_change_immediately": [
    "change 1 — specific and actionable",
    "change 2",
    "change 3"
  ],
  "visual_improvement": "one specific visual change to make videos look more varied",
  "hook_advice": "what type of opening hook is performing best in this niche right now",
  "thumbnail_advice": "what thumbnail style is getting clicks for competitors",
  "subscribe_growth_tactic": "one specific tactic to convert more viewers into subscribers",
  "first_48h_tactic": "what to do in first 48 hours after upload to maximize algorithm push",
  "30_day_strategy": "2-3 sentence strategic direction for the next 30 days to hit 1000 subs"
}}"""

    raw = _ai_call(prompt)
    return _parse_json_from_response(raw)


# ── Report formatter ──────────────────────────────────────────────────────────

def _format_email(our: dict, competitors: dict, trending: list, strategy: dict) -> str:
    lines = [
        "AGENT 11: ADVANCED VIDEO REVIEW + COMPETITOR INTELLIGENCE",
        f"Date: {datetime.now().strftime('%A, %B %d %Y')}",
        f"AI Engine: {GLM_MODEL}",
        "═"*60,
        "",
        f"URGENCY: {strategy.get('urgency_score','?')}/10 — change needed",
        "",
    ]

    # Our content
    lines += ["━"*60, "OUR CHANNEL HEALTH", "━"*60, ""]
    lines.append(f"Variety Score: {our.get('variety_score','?')}/10")
    lines.append(f"Dominant Title Formula: {our.get('title_formula_used','?')}")
    if our.get("overused_words"):
        lines.append(f"Overused Words: {', '.join(our['overused_words'])}")
    if our.get("topics_overused"):
        lines.append(f"Topics Overused: {', '.join(our['topics_overused'])}")
    if our.get("emotion_range"):
        lines.append(f"Emotion Range: {our['emotion_range']}")
    if our.get("similar_pairs"):
        lines.append(f"\n⚠️  {len(our['similar_pairs'])} NEAR-DUPLICATE TITLES:")
        for p in our["similar_pairs"][:4]:
            lines.append(f"  • \"{p['title_a'][:55]}\"")
            lines.append(f"    vs \"{p['title_b'][:55]}\" ({p['overlap_pct']}% same)")
    lines.append("")

    # Competitors
    if competitors:
        lines += ["━"*60, "COMPETITOR ANALYSIS", "━"*60, ""]
        for name, data in competitors.items():
            if not data:
                continue
            lines.append(f"📊 {name}  —  {data.get('subscribers',0):,} subs  |  avg {data.get('avg_views_recent',0):,} views/video")
            for v in data.get("recent_videos", [])[:4]:
                lines.append(f"   [{v['views']:,}] {v['title'][:70]}")
            lines.append("")

    # Trending
    if trending:
        lines += ["━"*60, "TRENDING RIGHT NOW", "━"*60, ""]
        for t in trending[:8]:
            lines.append(f"  → {t[:90]}")
        lines.append("")

    # Strategy
    ci = strategy.get("competitor_insights", {})
    lines += ["━"*60, "STRATEGIC ANALYSIS (AI)", "━"*60, ""]

    if ci.get("what_works_for_them"):
        lines.append(f"WHAT WORKS FOR COMPETITORS: {ci['what_works_for_them']}")
        lines.append("")
    if ci.get("topics_crushing_it_now"):
        lines.append("TOPICS GETTING VIEWS RIGHT NOW:")
        for t in ci["topics_crushing_it_now"]:
            lines.append(f"  → {t}")
        lines.append("")
    if ci.get("gap_we_can_exploit"):
        lines.append(f"GAP WE CAN EXPLOIT: {ci['gap_we_can_exploit']}")
        lines.append("")
    if strategy.get("trending_opportunity"):
        lines.append(f"🔥 TRENDING OPPORTUNITY THIS WEEK: {strategy['trending_opportunity']}")
        lines.append("")

    if strategy.get("next_5_video_titles"):
        lines.append("NEXT 5 VIDEO TITLES TO USE:")
        for i, t in enumerate(strategy["next_5_video_titles"], 1):
            lines.append(f"  {i}. {t}")
        lines.append("")

    if strategy.get("what_to_change_immediately"):
        lines.append("CHANGE IMMEDIATELY:")
        for c in strategy["what_to_change_immediately"]:
            lines.append(f"  ⚡ {c}")
        lines.append("")

    for key, label in [
        ("hook_advice",            "HOOK ADVICE"),
        ("thumbnail_advice",       "THUMBNAIL ADVICE"),
        ("visual_improvement",     "VISUAL IMPROVEMENT"),
        ("subscribe_growth_tactic","SUBSCRIBE GROWTH TACTIC"),
        ("first_48h_tactic",       "FIRST 48H AFTER UPLOAD"),
        ("30_day_strategy",        "30-DAY STRATEGY"),
    ]:
        if strategy.get(key):
            lines.append(f"{label}: {strategy[key]}")
            lines.append("")

    return "\n".join(lines)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    from agents.notifier import send

    print("[Agent 11: Video Reviewer] Starting advanced review...")

    # Load our uploads
    log      = _load_json(UPLOAD_LOG, [])
    regulars = [v for v in log if v.get("type") == "regular"][-15:]
    shorts   = [v for v in log if v.get("type") == "shorts"][-15:]
    print(f"  Found {len(regulars)} regular + {len(shorts)} Shorts")

    # Analyze our content
    print("  Analyzing our content variety...")
    our_analysis = _analyze_our_content(regulars, shorts)

    # Competitor intelligence
    print("  Fetching competitor data...")
    api_key     = os.getenv("YOUTUBE_API_KEY")
    competitors = _fetch_all_competitors(api_key)
    print(f"  Got data for {len(competitors)} competitors")

    # Trending topics
    print("  Searching trending topics...")
    trending = _get_trending_topics()
    print(f"  Found {len(trending)} trending topics")

    # Deep strategic analysis
    print("  Running deep AI strategic analysis...")
    strategy = _deep_strategic_analysis(our_analysis, competitors, trending)

    # Save report for Head Agent
    report = {
        "generated_at":      datetime.now(timezone.utc).isoformat(),
        "our_channel":       our_analysis,
        "competitors":       {k: {
            "subscribers":       v.get("subscribers", 0),
            "avg_views_recent":  v.get("avg_views_recent", 0),
            "top_videos":        v.get("recent_videos", [])[:5],
        } for k, v in competitors.items()},
        "trending_topics":   trending,
        "strategy":          strategy,
    }
    _save_json(REPORT_FILE, report)
    print(f"  Report saved to {REPORT_FILE}")

    # Format and send email
    body = _format_email(our_analysis, competitors, trending, strategy)
    print(body[:600] + "\n...")

    send(body, subject=f"Agent 11: Video Review + Competitor Intel — Urgency {strategy.get('urgency_score','?')}/10")
    print("[Reviewer] Done.")


if __name__ == "__main__":
    main()
