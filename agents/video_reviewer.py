"""
Agent 11: Video Quality Reviewer
Analyzes recent uploads for content variety, topic repetition, and visual sameness.
Uses GLM (ZhipuAI) for analysis — falls back to Groq.
Runs weekly. Catches "all videos look the same" problems before viewers do.
"""
import os, sys, json, re
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

UPLOAD_LOG = "upload_log.json"
GLM_BASE   = "https://open.bigmodel.cn/api/paas/v4/"
GLM_MODEL  = os.getenv("GLM_MODEL", "glm-4-flash")   # free tier — change to glm-4-plus for better quality


def _load_json(path, default):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return default


def _ai_call(prompt: str) -> str:
    """Try GLM first (ZhipuAI), fall back to Groq."""
    glm_key = os.getenv("GLM_API_KEY")
    if glm_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=glm_key, base_url=GLM_BASE)
            resp = client.chat.completions.create(
                model=GLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1800,
                temperature=0.3,
            )
            result = resp.choices[0].message.content.strip()
            print(f"  [Reviewer] GLM response received ({len(result)} chars)")
            return result
        except Exception as e:
            print(f"  [Reviewer] GLM failed ({e}), falling back to Groq")

    import groq
    client = groq.Groq(api_key=os.getenv("GROQ_API_KEY"))
    resp = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1800,
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
    return {"overall_verdict": raw}


def _check_title_overlap(videos: list) -> list:
    """Flag pairs of videos with >50% word overlap in titles."""
    STOPS = {
        "the","a","an","is","are","you","your","why","how","what","when","to",
        "and","or","of","in","for","that","this","it","with","can","do","not",
        "be","have","has","will","just","from","on","at","by","but","more","all",
        "its","our","we","i","my","they","them","their","about","if","so","no",
    }
    flagged = []
    for i in range(len(videos)):
        for j in range(i + 1, len(videos)):
            w1 = set(videos[i].get("title","").lower().split()) - STOPS
            w2 = set(videos[j].get("title","").lower().split()) - STOPS
            if len(w1) < 3 or len(w2) < 3:
                continue
            overlap = len(w1 & w2) / min(len(w1), len(w2))
            if overlap > 0.5:
                flagged.append((
                    videos[i].get("title","")[:60],
                    videos[j].get("title","")[:60],
                    f"{overlap*100:.0f}% overlap",
                ))
    return flagged


def _analyze_variety(videos: list, video_type: str) -> dict:
    titles_str = "\n".join(
        f"{i+1}. {v.get('title','')}" for i, v in enumerate(videos)
    )

    prompt = f"""You are a brutal-honest YouTube content strategist reviewing {video_type} for a psychology/motivation channel called MindShift Productivity.

Last {len(videos)} {video_type} titles:
{titles_str}

Psychology niche context: The channel covers habits, mindset, brain science, productivity, emotional patterns, confidence, focus. Target audience: 18–35, Indian and global.

Respond ONLY in valid JSON (no markdown, no explanation outside the JSON):
{{
  "variety_score": <integer 1-10>,
  "repetitive_patterns": ["pattern 1", "pattern 2"],
  "too_similar_pairs": [["title A", "title B", "reason"]],
  "overused_words": ["word1", "word2"],
  "missing_sub_niches": ["sub-topic we haven't touched", "another gap"],
  "title_formula_verdict": "are titles using the same formula? be specific",
  "recommended_next_topics": ["specific topic 1", "specific topic 2", "specific topic 3", "specific topic 4", "specific topic 5"],
  "hook_variety_tip": "one concrete tip to make the first 5 seconds more varied",
  "visual_variety_tip": "one concrete suggestion to make videos look more different",
  "overall_verdict": "2-3 sentences honest assessment for the channel owner"
}}"""

    raw = _ai_call(prompt)
    return _parse_json_from_response(raw)


def _format_section(label: str, videos: list) -> list:
    lines = [f"{'━'*52}", f"  {label}  ({len(videos)} videos reviewed)", f"{'━'*52}", ""]

    if not videos:
        lines += ["  No uploads found.", ""]
        return lines

    # Simple overlap check
    flagged = _check_title_overlap(videos)
    if flagged:
        lines.append(f"⚠️  SIMILAR TITLE PAIRS ({len(flagged)} found):")
        for t1, t2, reason in flagged[:5]:
            lines.append(f"  • \"{t1}\"")
            lines.append(f"    vs \"{t2}\"")
            lines.append(f"    → {reason}")
        lines.append("")

    if len(videos) < 3:
        lines.append("  Need at least 3 videos for AI variety analysis.")
        lines.append("")
        return lines

    print(f"  [Reviewer] Calling AI for {label}...")
    analysis = _analyze_variety(videos, label)

    score = analysis.get("variety_score", "?")
    score_bar = ("█" * int(score) + "░" * (10 - int(score))) if isinstance(score, int) else "?"
    lines.append(f"VARIETY SCORE: {score}/10  {score_bar}")
    lines.append("")

    if analysis.get("repetitive_patterns"):
        lines.append("REPETITIVE PATTERNS:")
        for p in analysis["repetitive_patterns"]:
            lines.append(f"  • {p}")
        lines.append("")

    if analysis.get("overused_words"):
        words = ", ".join(analysis["overused_words"])
        lines.append(f"OVERUSED WORDS: {words}")
        lines.append("")

    if analysis.get("title_formula_verdict"):
        lines.append(f"TITLE FORMULA: {analysis['title_formula_verdict']}")
        lines.append("")

    if analysis.get("missing_sub_niches"):
        lines.append("TOPICS WE'VE NEVER COVERED:")
        for m in analysis["missing_sub_niches"]:
            lines.append(f"  • {m}")
        lines.append("")

    if analysis.get("recommended_next_topics"):
        lines.append("RECOMMENDED NEXT TOPICS:")
        for t in analysis["recommended_next_topics"]:
            lines.append(f"  → {t}")
        lines.append("")

    if analysis.get("hook_variety_tip"):
        lines.append(f"HOOK TIP: {analysis['hook_variety_tip']}")
        lines.append("")

    if analysis.get("visual_variety_tip"):
        lines.append(f"VISUAL TIP: {analysis['visual_variety_tip']}")
        lines.append("")

    if analysis.get("overall_verdict"):
        lines.append(f"VERDICT: {analysis['overall_verdict']}")
        lines.append("")

    return lines


def main():
    from agents.notifier import send

    print("[Agent 11: Video Reviewer] Starting variety analysis...")

    log = _load_json(UPLOAD_LOG, [])
    if not log:
        print("[Reviewer] No uploads found in upload_log.json")
        return

    regulars = [v for v in log if v.get("type") == "regular"][-15:]
    shorts   = [v for v in log if v.get("type") == "shorts"][-15:]

    total = len(regulars) + len(shorts)
    print(f"  [Reviewer] Found {len(regulars)} regular + {len(shorts)} Shorts")

    lines = [
        "AGENT 11: VIDEO VARIETY REVIEW",
        f"Date: {datetime.now().strftime('%A, %B %d %Y')}",
        f"Scope: Last {len(regulars)} regular + last {len(shorts)} Shorts",
        f"AI: {GLM_MODEL} (ZhipuAI GLM)",
        "",
    ]

    lines += _format_section("REGULAR VIDEOS", regulars)
    lines += _format_section("SHORTS", shorts)

    # Recent titles list for reference
    lines += ["━"*52, "ALL RECENT TITLES:", ""]
    for v in sorted(log, key=lambda x: x.get("uploaded_at",""), reverse=True)[:20]:
        tag = "[REG]" if v.get("type") == "regular" else "[SHT]"
        lines.append(f"  {tag} {v.get('title','')[:72]}")

    lines += [
        "",
        "━"*52,
        "HOW TO FIX VISUAL SAMENESS:",
        "  1. Run daily_mixed_regular.yml (cartoon + stock combo) more often",
        "  2. Change PIPELINE_SLOT in the workflow (0-9) for different color schemes",
        "  3. Vary the script structure — not every video needs Hook/Problem/Solution/Result",
        "  4. Mix in a 'list format' video: '7 Signs Your Brain Is Overloaded'",
        "",
    ]

    body = "\n".join(lines)
    print(body[:500] + "...")

    send(body, subject=f"Agent 11: Video Variety Review — {total} videos analyzed")
    print("[Reviewer] Report emailed.")


if __name__ == "__main__":
    main()
