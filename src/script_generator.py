import json
import re
import random
import datetime
from groq import Groq
from config import GROQ_API_KEY, DAILY_TOPICS, REGULAR_VIDEO, SHORTS_VIDEO

_client = Groq(api_key=GROQ_API_KEY)
MODEL = "llama-3.3-70b-versatile"


def _sanitize_json(raw: str) -> str:
    """Escape literal control characters inside JSON string values.
    LLMs sometimes emit real newlines inside string values, which is invalid JSON.
    This walks the string character-by-character and escapes any control char
    that appears between unescaped double-quote delimiters.
    """
    out = []
    in_str = False
    skip = False
    for ch in raw:
        if skip:
            out.append(ch)
            skip = False
            continue
        if ch == "\\" and in_str:
            out.append(ch)
            skip = True
            continue
        if ch == '"':
            in_str = not in_str
            out.append(ch)
            continue
        if in_str and ord(ch) < 0x20:
            if ch == "\n":   out.append("\\n")
            elif ch == "\r": out.append("\\r")
            elif ch == "\t": out.append("\\t")
            else:            out.append(f"\\u{ord(ch):04x}")
        else:
            out.append(ch)
    return "".join(out)


def _parse_json(text: str) -> dict:
    text = re.sub(r"```json\s*", "", text)
    text = re.sub(r"```\s*", "", text)
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("No JSON found in response")
    return json.loads(_sanitize_json(match.group()))


_TITLE_FORMULAS = [
    ('WHY',      '"Why You [Search Keyword] — And What It Says About Your Brain"'),
    ('TRUTH',    '"The Real Reason You [Search Keyword] (It\'s Not What You Think)"'),
    ('BRAIN',    '"Your Brain Is [X] Right Now — Here Is Why You [Search Keyword]"'),
    ('SCIENCE',  '"The Psychology Behind Why You [Search Keyword] Explained"'),
    ('IDENTITY', '"If You [Search Keyword] Every Day, Read This"'),
    ('NUMBER',   '"7 Signs Your Brain Is [X] (And What To Do About It)"'),
    ('QUESTION', '"Do You [Search Keyword]? Here Is What Your Brain Is Actually Doing"'),
]

# Shorter, punchier formulas for Shorts — max ~40 chars, no em-dash, no parentheses
_SHORTS_TITLE_FORMULAS = [
    ('STOP',   '"Stop [Doing This] — Your Brain Needs You To"'),
    ('TRUTH',  '"The Real Reason You [Search Keyword]"'),
    ('SECRET', '"Nobody Tells You This About [Topic]"'),
    ('BRAIN',  '"Your Brain Does This Every [Time/Day] — Here\'s Why"'),
    ('TRAP',   '"The [Topic] Trap Nobody Talks About"'),
    ('HIDDEN', '"The Hidden Cost of [Painful Behavior]"'),
    ('FIX',    '"How to Actually Fix [Painful Problem]"'),
]

def _get_recent_titles(n: int = 8) -> list[str]:
    """Load last N uploaded video titles to avoid repeating them."""
    import os, json
    log_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "upload_log.json")
    try:
        with open(log_path) as f:
            log = json.load(f)
        return [v.get("title", "") for v in log[-n:] if v.get("title")]
    except Exception:
        return []


def generate_script(topic: str, video_type: str = "regular") -> dict:
    """
    Generate a motivational/psychology YouTube script.
    Returns: title, description, tags, scenes
    Each scene: scene_number, duration_seconds, narration, text_overlay, bg_color
    """
    spec = REGULAR_VIDEO if video_type == "regular" else SHORTS_VIDEO
    num_scenes = spec["scenes"]

    # Rotate title formula by day — Shorts use a shorter punchier formula set
    day_of_year = datetime.date.today().timetuple().tm_yday
    if video_type == "shorts":
        formula_tag, formula_template = _SHORTS_TITLE_FORMULAS[day_of_year % len(_SHORTS_TITLE_FORMULAS)]
    else:
        formula_tag, formula_template = _TITLE_FORMULAS[day_of_year % len(_TITLE_FORMULAS)]

    # Load recent titles so the prompt can avoid repeating them
    recent_titles = _get_recent_titles(8)
    avoid_block = ""
    if recent_titles:
        avoid_list = "\n".join(f"  - {t}" for t in recent_titles)
        avoid_block = f"""
═══ AVOID REPEATING — DO NOT use titles similar to any of these recent uploads ═══
{avoid_list}
Your title MUST differ in both formula AND keyword from all of the above.
"""

    if video_type == "regular":
        duration_label = "8-10 minutes"
        scene_guide = f"""Exactly {num_scenes} scenes following this NARRATIVE ARC:
Scenes 1-2   → CHAPTER 1 — THE HOOK: Shocking question or bold claim. Viewer MUST keep watching.
Scenes 3-7   → CHAPTER 2 — THE SCIENCE: Psychology/science behind the topic. One key insight per scene. Reference real studies.
Scenes 8-12  → CHAPTER 3 — REAL STORIES: Relatable everyday stories that make the science concrete. "Have you ever..." or "Think about when..."
Scenes 13-17 → CHAPTER 4 — THE FIX: 5 specific actionable steps the viewer can start TODAY. Precise and implementable.
Scenes 18-20 → CHAPTER 5 — NEW LIFE: What life looks like after applying this. End with strong call to subscribe and comment.

CRITICAL: Each scene narration must be EXACTLY 55-60 words. Not 45, not 65 — 55 to 60.
Count them. This fills the full 27 seconds at our deliberate voice pace (127 WPM) and eliminates dead air.
If your scene narration is under 55 words, add a concrete example, a statistic, or a visceral detail.
Speak like a smart, direct friend — not a robot or professor. Use "you" throughout.
duration_seconds for each scene: 27"""
    else:
        duration_label = "40-50 seconds"
        scene_guide = f"""Exactly {num_scenes} scenes. ULTRA fast-paced. Total runtime ~45 seconds.
Each scene narration: EXACTLY 36-40 words. Two to three punchy sentences. One idea per scene.
This fills exactly 15 seconds at our voice pace (127 WPM, deliberate and authoritative).
COUNT THE WORDS. Do NOT go below 36 or above 40 — too short leaves silence, too long gets cut off.
Example (38 words): "You open your phone to check one thing. Forty minutes later you are still there. Your brain did not fail you. It was designed to keep you scrolling. That is the trap. And you can break it."

Scene 1 (the HOOK — stops the scroll in 1 second):
  Open mid-scene in the exact moment of pain. No setup. Pure sensation. Make them feel caught.
  Start with one of: "You...", "Your brain...", "Right now...", "Every time you...", "That feeling when..."
  End with a cliffhanger that makes scene 2 feel necessary.

Scene 2 (the SCIENCE — the surprising reason):
  One unexpected psychological fact that reframes the problem. Reference a real mechanism (dopamine, cortisol, amygdala, etc.).
  End with: "And there is a way out."

Scene 3 (the PAYOFF — what to actually do + CTA):
  One specific, actionable thing they can do TODAY. Make it feel easy and immediate.
  End with: "The full breakdown is on the channel — search MindShiftProductivity right now."

duration_seconds for each scene: 15

POLL QUESTION: Also write one interactive poll_question for the end card.
Format: "Question? A: [option1] B: [option2]"
The question must be YES/NO or A/B style to drive comments.
Examples:
  "Does your brain do this too? A: Every single day B: Only sometimes"
  "Has this ever cost you? A: Yes, badly B: Not yet but close"
  "Are you in this loop right now? A: Trapped in it B: Just got out"
Make it feel personal and urgent — viewers must feel compelled to answer."""

    prompt = f"""You are a top YouTube scriptwriter for a viral psychology/motivation channel like Jamie Social, Trust Me Bro, or Productive Peter. You have helped channels go from 0 to 500k subscribers.

Write a complete, deeply engaging script for a {video_type} YouTube video about:
"{topic}"

Target audience: 18-35 year olds interested in self-improvement, psychology, money, success.
Duration: {duration_label}
{scene_guide}

═══ TITLE RULES (this is the #1 subscriber driver) ═══
EVERY title MUST contain two things:
A) A SEARCH KEYWORD — a phrase someone in pain actually types into YouTube search
B) A CURIOSITY GAP — something that makes them feel they are missing something critical

SEARCH KEYWORD examples (pick whichever fits the topic — do NOT default to overthinking/procrastination):
  "why you self sabotage"         |  "why you can't change"
  "how to break bad habits"       |  "why your brain keeps you stuck"
  "stop negative thoughts"        |  "why you feel empty inside"
  "how to rewire your brain"      |  "why motivation never works"
  "why you feel drained"          |  "how to build self discipline"
  "why you can't focus"           |  "why you overthink decisions"
  "imposter syndrome"             |  "decision fatigue"
  "why you people please"         |  "why you feel behind in life"

TODAY'S REQUIRED TITLE FORMULA — THIS IS MANDATORY, NOT OPTIONAL:
  Formula code: {formula_tag}
  Template:     {formula_template}

You MUST use exactly this formula structure. Replace the placeholders ([Search Keyword], [X], [Benefit], etc.) with topic-specific words.
VIOLATION EXAMPLES (wrong formula — will be rejected):
  "Why You Can't Stop Overthinking..." when formula is SCIENCE → REJECTED
  "7 Signs Your Brain Is..." when formula is TRUTH → REJECTED
CORRECT: match the template above exactly, with topic-specific fill-ins.

GOOD: "The Real Reason You Keep Losing Motivation (It's Not Laziness)" (searchable + curiosity)
BAD:  "YOUR BRAIN IS LYING" (nobody searches this, no keyword anchor)
BAD:  "The Shocking Truth About Your Mind" (too vague, zero search volume)
{avoid_block}
{"Title must be 30-45 characters — SHORT AND PUNCHY. No em-dashes. No parentheses. No 'And How to Finally Fix It' padding. Lowercase except first word." if video_type == "shorts" else "Title must be 52-72 characters. Lowercase except first word and proper nouns — sounds more human, less clickbait."}

═══ HOOK RULES — SCENARIO DROP (decides 70% of watch time) ═══
Scene 1 MUST use the "scenario drop" technique — open MID-SCENE, with the viewer already IN the situation.
Do NOT start with the topic name. Do NOT summarize what the video is about. Do NOT say "today we're going to talk about..."
The viewer should feel like they were dropped into their own life.

BAD (announces topic): "Today we're talking about procrastination and why your brain..."
BAD (generic claim): "Most people will never reach their goals."
GOOD (scenario drop): "You're sitting at your desk. The task has been open for forty-five minutes. You've checked your phone four times. Your cursor hasn't moved. You know exactly what you need to do. And you still cannot make yourself do it."

SCENARIO DROP STRUCTURE (scene 1, exactly 70-75 words):
  - Sentences 1-3: Place the viewer IN the exact physical/mental moment — specific details (the desk, the cursor, the phone, the 2am ceiling stare, etc.)
  - Sentence 4: Name the MECHANISM — "this is not laziness. This is [specific brain phenomenon]."
  - Sentence 5: What this is costing them RIGHT NOW — concrete and personal.
  - Sentence 6: The promise — "In the next eight minutes you will learn exactly how to stop this."

Scene 2 (last scene of Chapter 1) MUST end with a tension statement that makes Chapter 2 feel necessary:
  "But here's what makes this so hard to fix — and why most advice about it actually makes it worse."
  "That alone might not surprise you. What will surprise you is WHY your brain does this — and it has nothing to do with willpower."

═══ REHOOK RULES — between every chapter ═══
The LAST scene of each chapter (scenes 2, 7, 12, 17) must END with a tension/cliffhanger sentence.
This makes the viewer feel the next chapter is necessary to resolve something unfinished.
BAD transition: "So now you know the science. Let's look at how to fix it."
GOOD transition: "But here's the uncomfortable part — knowing this is not the same as being able to stop it. And the reason you cannot just 'try harder' is something most people never learn."
The viewer must feel they NEED to keep watching to resolve the tension you just created.

═══ CONTENT RULES ═══
- Use "you" throughout — make it personal, not academic
- Each scene has a bold text overlay (max 5 words) shown on screen
- Reference real psychology (Pavlov, Kahneman, dopamine, cortisol, amygdala, prefrontal cortex) — sounds credible
- Use contrast: "Most people do X. Here is what actually works instead."
- IDENTITY-AFFIRMATION LINES (scenes 8-12, the Real Stories chapter): Start at least 3 scenes with phrases like:
    "If you are the person who always puts others first..."
    "If you have ever started something and quit right before it got good..."
    "If you have been stuck in this exact pattern for years..."
  These phrases trigger "this is literally me" comments — highest engagement signal.
- Include at least 3 scenes with a specific STAT or STUDY REFERENCE — a number, a percentage, or a named researcher.
  Example: "A 2019 study by Baumeister found that decision fatigue reduces willpower by 40% within four hours."
- STAT FORMAT: When you include a stat, state it as: [specific number/percent] + [what it means for the viewer personally].
- End regular videos with a SESSION-CONTINUATION CTA: "If you want to understand why [specific thing from this video] connects to [related topic], I have covered that exact link in another video — check it out next."
  Then: "Subscribe so you catch it."
- End shorts with: "The full breakdown is on the channel — search MindShiftProductivity right now."

═══ TEXT OVERLAY RULES ═══
- Max 5 words, ALL CAPS
- Must be the single most shocking/intriguing phrase from that scene
- Examples: "YOUR BRAIN IS LYING", "THIS REWIRES EVERYTHING", "MOST PEOPLE MISS THIS"

CRITICAL JSON RULE: Every string value in your JSON response must be on ONE LINE — no literal newline characters inside any string. Use \\n (backslash-n) if you need a line break inside a string value. Literal newlines inside JSON strings cause a parse error and the whole pipeline fails.

Respond ONLY with valid JSON, no markdown fences, no extra text:
{{
  "title": "{'SHORT punchy title using formula ' + formula_tag + ', MAX 40 chars, NO em-dashes, NO parentheses' if video_type == 'shorts' else 'viral title using ONLY formula ' + formula_tag + ', 52-72 chars'}",
  "description": "{'50-80 word punchy Shorts description. One paragraph: brutal 1-sentence pain hook, then 2-3 bullet lines of what viewer learns. End with: #Shorts #psychology #selfimprovement #motivation #mindset #MindShiftProductivity' if video_type == 'shorts' else 'SEO YouTube description, 200-220 words. Paragraph 1: open with the exact brutal pain statement from Scene 1 narration. Paragraph 2: 3-line bullet summary of what viewer will learn (use bullet character). Paragraph 3: weave in these keywords naturally: psychology, self improvement, motivation, mindset, productivity, success, habits, brain, mental health, personal development. Final section: BetterHelp link at https://betterhelp.com/mindshiftproductivity, Audible link at https://audible.com/mt/mindshiftproductivity, subscribe CTA, and the question: which part hit you hardest — comment below.'}",
  "tags": ["psychology", "motivation", "self improvement", "success mindset", "habits", "productivity", "mindset", "brain psychology", "life advice", "personal development", "how to focus", "stop procrastinating"],
  "thumbnail_text": "3-5 word ALL CAPS thumbnail text — most shocking phrase from the video",
  "poll_question": "for Shorts only — Question? A: option1 B: option2 (leave empty string for regular videos)",
  "scenes": [
    {{
      "scene_number": 1,
      "duration_seconds": 27,
      "narration": "Most people will never reach their goals — not because they lack talent, but because their brain is actively working against them. Right now, a hidden psychological trap is sabotaging every decision you make. Every day you don't know this, you're losing hours of productive potential. In the next few minutes, you'll learn exactly how to break free.",
      "text_overlay": "YOUR BRAIN FIGHTS YOU",
      "bullets": ["Brain works against you", "Hidden psychological trap", "You can fix this today"],
      "bg_color": "#1a1a2e"
    }}
  ]
}}"""

    def _call(temperature):
        r = _client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=4096,
        )
        return _parse_json(r.choices[0].message.content)

    data = _call(0.85)

    required = ["title", "description", "tags", "scenes"]
    for key in required:
        if key not in data:
            raise ValueError(f"Missing key in response: {key}")

    # Validate title formula — retry once if LLM ignored the required formula
    _FORMULA_STARTERS = {
        # Regular formulas
        'WHY':      ('why you ',),
        'TRUTH':    ('the real reason',),
        'BRAIN':    ('your brain is',),
        'SCIENCE':  ('the psychology behind',),
        'IDENTITY': ('if you ',),
        'NUMBER':   ('7 signs', '5 signs', '3 signs', '10 signs', '6 signs'),
        'QUESTION': ('do you ',),
        # Shorts formulas
        'STOP':     ('stop ',),
        'SECRET':   ('nobody tells you',),
        'TRAP':     ('the ',),
        'HIDDEN':   ('the hidden',),
        'FIX':      ('how to actually', 'how to '),
    }
    title_low = data.get("title", "").lower()
    expected_starters = _FORMULA_STARTERS.get(formula_tag, ())
    if expected_starters and not any(title_low.startswith(s) for s in expected_starters):
        print(f"  [Script] Title '{data['title']}' doesn't match {formula_tag} formula — retrying...")
        retry_prompt = prompt + f"\n\nWARNING: Your previous title did not follow the {formula_tag} formula. Try again. The title MUST start with one of: {expected_starters}"
        # one retry at lower temperature for more precise instruction-following
        r2 = _client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": retry_prompt}],
            temperature=0.55,
            max_tokens=4096,
        )
        data2 = _parse_json(r2.choices[0].message.content)
        if all(k in data2 for k in required):
            data = data2

    return data


def pick_topic(slot_index: int = 0) -> str:
    """Deterministically pick a topic by date + slot so all 6 daily workflows get different topics."""
    day = datetime.date.today().timetuple().tm_yday  # 1-365
    idx = (day * 6 + slot_index) % len(DAILY_TOPICS)
    return DAILY_TOPICS[idx]
