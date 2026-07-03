"""
Agent 6: Quora Content Generator (runs Mon/Wed/Fri)
Searches DuckDuckGo for real Quora questions posted in the last week about our niche
→ generates short, punchy answers that naturally link to our latest video + short
→ sends 5 Q&A drafts to email for manual posting
"""
import os, sys, json, re, requests
from groq import Groq

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import GROQ_API_KEY, DAILY_TOPICS

CHANNEL_NAME = "MindShift Productivity"
CHANNEL_URL  = "https://youtube.com/@MindShiftProductivity"

SEARCH_TOPICS = [
    "psychology self improvement",
    "why people self sabotage",
    "procrastination motivation",
    "anxiety overthinking",
    "confidence habits mindset",
    "why can't i change my habits",
    "mental health productivity",
    "dopamine motivation stuck",
]


def _get_latest_urls() -> tuple[str, str, str]:
    """Returns (regular_video_url, regular_video_title, shorts_url)."""
    try:
        with open("upload_log.json") as f:
            log = json.load(f)
        regulars = sorted(
            [v for v in log if v.get("type") == "regular"],
            key=lambda x: x.get("uploaded_at", ""), reverse=True
        )
        shorts = sorted(
            [v for v in log if v.get("type") == "shorts"],
            key=lambda x: x.get("uploaded_at", ""), reverse=True
        )
        reg_url   = f"https://youtu.be/{regulars[0]['video_id']}" if regulars else CHANNEL_URL
        reg_title = regulars[0].get("title", "") if regulars else ""
        short_url = f"https://youtu.be/{shorts[0]['video_id']}" if shorts else ""
        return reg_url, reg_title, short_url
    except Exception:
        return CHANNEL_URL, "", ""


def _search_quora_questions(topic: str, max_results: int = 8) -> list[str]:
    """Search DuckDuckGo Lite for recent Quora questions. Returns list of question strings."""
    try:
        resp = requests.post(
            "https://lite.duckduckgo.com/lite/",
            data={"q": f"site:quora.com {topic}", "df": "w"},
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            timeout=20,
        )
        if resp.status_code != 200:
            return []

        # Extract link text from DDG lite results — these are the Quora question titles
        # DDG lite uses <a> tags inside <td class="result-link">
        titles = re.findall(r'<a[^>]+href="https://(?:www\.)?quora\.com/[^"]*"[^>]*>([^<]{15,})</a>', resp.text)
        # Also try broader pattern for plain links
        if not titles:
            titles = re.findall(r'<a[^>]+>([A-Z][^<]{20,}(?:\?|why|how|what|when|is |are |do |does )[^<]*)</a>', resp.text, re.IGNORECASE)

        # Clean up HTML entities
        clean = []
        for t in titles:
            t = re.sub(r'&amp;', '&', t)
            t = re.sub(r'&[a-z]+;', '', t)
            t = t.strip()
            if len(t) > 15 and t not in clean:
                clean.append(t)

        return clean[:max_results]
    except Exception as e:
        print(f"  [Quora] DDG search failed for '{topic}': {e}")
        return []


def _gather_real_questions(limit: int = 10) -> list[str]:
    """Try multiple search topics, collect real Quora questions."""
    import random
    # Rotate 3 random topics each run to avoid redundancy over the week
    topics = random.sample(SEARCH_TOPICS, min(3, len(SEARCH_TOPICS)))
    questions = []
    seen = set()
    for topic in topics:
        found = _search_quora_questions(topic)
        print(f"  [Quora] '{topic}': {len(found)} questions found")
        for q in found:
            if q.lower() not in seen and len(questions) < limit:
                seen.add(q.lower())
                questions.append(q)
    return questions


def _generate_answers(client: Groq, questions: list[str],
                       video_url: str, video_title: str, short_url: str) -> list[dict]:
    """Generate Quora answers for the given questions (real or AI-generated)."""
    questions_str = "\n".join(f'{i+1}. "{q}"' for i, q in enumerate(questions[:5]))
    links_note = f"Regular video: {video_url}"
    if video_title:
        links_note += f' ("{video_title[:60]}")'
    if short_url:
        links_note += f"\nShorts clip: {short_url}"

    prompt = f"""You write Quora answers for a psychology/motivation channel "{CHANNEL_NAME}".

Answer EACH of these questions:
{questions_str}

Our latest content — link naturally when directly relevant:
{links_note}

Rules for each answer:
- 60-80 words maximum
- Sound like a knowledgeable person sharing real experience, not a content creator
- If our video topic closely matches the question, end with one of:
    "I went deep on this: {video_url}"
    "Made a 60-sec breakdown: {short_url}"  (only if short_url is set AND it's a quick insight)
- If neither matches well, don't force a link — a great answer with no link beats a forced plug
- No hashtags, no "great question!", no corporate tone
- No answer should start with "The answer is" or "Simply put"

Respond with ONLY a JSON array:
[
  {{
    "question": "exact question text",
    "answer": "your answer here"
  }}
]"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.85,
        max_tokens=2500,
    )
    text = response.choices[0].message.content.strip()
    match = re.search(r'\[.*\]', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except Exception:
            pass
    return []


def _generate_fallback_questions(client: Groq, video_title: str) -> list[str]:
    """When DDG fails, ask Groq to invent likely Quora questions for our niche."""
    topic_hint = f'Our latest video: "{video_title}"' if video_title else f"Topics: {', '.join(DAILY_TOPICS[:5])}"
    prompt = f"""Generate 5 Quora questions that real people post about psychology, self-improvement, and why people get stuck.

{topic_hint}

Rules:
- Questions must sound like genuine Quora searches (not textbook headings)
- Mix: some start with "Why do I...", "How do I stop...", "Is it normal to..."
- All must relate to: self-sabotage, procrastination, anxiety, habits, or motivation

Return only a JSON array of strings:
["question 1", "question 2", ...]"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8, max_tokens=400,
    )
    text = response.choices[0].message.content.strip()
    match = re.search(r'\[.*\]', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except Exception:
            pass
    return DAILY_TOPICS[:5]


def main():
    from agents.notifier import send

    client   = Groq(api_key=GROQ_API_KEY)
    video_url, video_title, short_url = _get_latest_urls()

    print(f"[Agent 6: Quora] Video: {video_url} — {video_title[:50]}")
    print(f"[Agent 6: Quora] Short: {short_url or 'none'}")

    # Step 1: try to find real recent Quora questions via DuckDuckGo
    print("[Agent 6: Quora] Searching for real questions (past week)...")
    questions = _gather_real_questions(limit=10)

    if questions:
        print(f"  Found {len(questions)} real questions — generating answers...")
        source_label = "REAL questions found on Quora this week"
    else:
        print("  No real questions found — generating topic-based questions...")
        questions = _generate_fallback_questions(client, video_title)
        source_label = "AI-generated questions based on latest video topic"

    pairs = _generate_answers(client, questions, video_url, video_title, short_url)

    if not pairs:
        send("Quora Agent: Could not generate Q&A pairs. Groq may be busy.",
             subject="Agent 6: Quora Answers")
        return

    lines = [
        "Agent 6: Quora Answers Ready to Post",
        f"Source: {source_label}",
        f"Latest video: {video_url}",
        f"Latest short: {short_url or 'none yet'}",
        "",
        "HOW TO POST (step by step):",
        "1. Go to quora.com → search the question topic in the search bar",
        "2. Click 'Questions' tab → sort by 'Most Recent'",
        "3. Pick a question posted 1d-7d ago (NOT '10y' or '5y')",
        "4. Click the question → click 'Answer' → paste the answer → Submit",
        "",
        "IMPORTANT: Only answer questions posted within the last 7 days.",
        "",
    ]

    for i, pair in enumerate(pairs[:5], 1):
        q = pair.get("question", "")
        a = pair.get("answer", "")
        lines += [
            "─" * 40,
            f"Answer {i}",
            f"Search Quora for: {q}",
            "",
            "Paste this answer:",
            a,
            "",
        ]

    lines += [
        "─" * 40,
        "Tip: 5 answers = 10 minutes = traffic for years.",
        "Prioritise questions with 0-2 existing answers — yours gets seen immediately.",
    ]
    send("\n".join(lines), subject="Agent 6: Quora Answers Ready to Post")

    from agents.notifier import write_agent_report
    write_agent_report("quora", {
        "status":           "ok",
        "questions_found":  len(questions),
        "answers_drafted":  len(pairs[:5]),
        "source":           source_label,
        "summary":          f"{len(pairs[:5])} Quora answer drafts sent to email ({source_label})",
        "errors":           [],
    })


if __name__ == "__main__":
    main()
