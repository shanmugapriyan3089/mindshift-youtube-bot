import json
import re
import random
import datetime
from groq import Groq
from config import GROQ_API_KEY, DAILY_TOPICS, REGULAR_VIDEO, SHORTS_VIDEO

_client = Groq(api_key=GROQ_API_KEY)
MODEL = "llama-3.3-70b-versatile"


def _parse_json(text: str) -> dict:
    text = re.sub(r"```json\s*", "", text)
    text = re.sub(r"```\s*", "", text)
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("No JSON found in response")
    return json.loads(match.group())


def generate_script(topic: str, video_type: str = "regular") -> dict:
    """
    Generate a motivational/psychology YouTube script.
    Returns: title, description, tags, scenes
    Each scene: scene_number, duration_seconds, narration, text_overlay, bg_color
    """
    spec = REGULAR_VIDEO if video_type == "regular" else SHORTS_VIDEO
    num_scenes = spec["scenes"]

    if video_type == "regular":
        duration_label = "8-10 minutes"
        scene_guide = f"""Exactly {num_scenes} scenes following this NARRATIVE ARC:
Scenes 1-2   → HOOK: Shocking question or bold claim. Make viewer feel they MUST keep watching. High stakes.
Scenes 3-7   → DEEP DIVE: The psychology/science behind the topic. One key insight per scene. Reference real studies or well-known facts.
Scenes 8-12  → REAL EXAMPLES: Relatable everyday stories that make the science concrete. Start with "Have you ever..." or "Think about when..."
Scenes 13-17 → THE FIX: 5 specific actionable steps the viewer can start TODAY. Not generic — precise and implementable.
Scenes 18-20 → TRANSFORMATION + CTA: What life looks like after applying this. End with strong call to subscribe and comment.

CRITICAL: Each scene narration must be 55-65 words. This is how you hit 8-10 minutes.
Speak like a smart, direct friend — not a robot or professor. Use "you" throughout.
duration_seconds for each scene: 27"""
    else:
        duration_label = "20-25 seconds"
        scene_guide = f"""Exactly {num_scenes} scenes. ULTRA fast-paced. Scene 1 = hook that stops the scroll in 2 seconds.
Each scene narration: 28-34 words. One single punchy idea, spoken fast.
This fills exactly 12 seconds at natural Kokoro TTS pace (155 wpm).
Do NOT go below 28 words — shorter narrations leave dead silence.
Scene 1: shocking hook. Scene 2: the payoff / what to do.
End scene 2 with: "Follow for more psychology secrets."
duration_seconds for each scene: 12"""

    prompt = f"""You are a top YouTube scriptwriter for a viral psychology/motivation channel like Jamie Social, Trust Me Bro, or Productive Peter. You have helped channels go from 0 to 500k subscribers.

Write a complete, deeply engaging script for a {video_type} YouTube video about:
"{topic}"

Target audience: 18-35 year olds interested in self-improvement, psychology, money, success.
Duration: {duration_label}
{scene_guide}

═══ TITLE RULES (this is the #1 subscriber driver) ═══
Pick ONE of these proven viral title formulas — do NOT use generic titles:
1. SHOCKING TRUTH:   "Your Brain Is [Doing X] Right Now And You Don't Know It"
2. THEY LIED TO YOU: "Why Everything You Know About [Topic] Is Wrong"
3. SECRET REVEALED:  "The [Topic] Secret [Authority] Never Told You"
4. CHALLENGE FORMAT: "I Tried [Method] For 30 Days — The Results Shocked Me"
5. FEAR + CURIOSITY: "Stop [Common Habit] Immediately — Here's Why"
6. NUMBER + TWIST:   "7 [Topic] Tricks That Sound Fake But Actually Work"
7. IDENTITY THREAT:  "If You Do This Every Day, Your Brain Is Already Damaged"
Title must be 50-65 characters. Must create a knowledge gap — make them feel they're missing something critical.

═══ HOOK RULES (decides 70% of watch time) ═══
Scene 1 narration MUST follow this exact structure:
  - Sentence 1: Shocking statement or uncomfortable truth (NOT a question)
  - Sentence 2: Make it personal — "right now, this is happening to YOU"
  - Sentence 3: Create dread or urgency — what they're losing by not knowing this
  - Sentence 4: Promise — "In the next [X] minutes/seconds, you'll learn exactly how to fix this"
Example: "Most people will never reach their goals — not because they lack talent, but because their brain is actively working against them. Right now, a hidden psychological trap is sabotaging every decision you make. Every day you don't know this, you're losing hours of productive potential. In the next few minutes, I'll show you exactly how to break free."

═══ CONTENT RULES ═══
- Use "you" throughout — make it personal, not academic
- Each scene has a bold text overlay (max 6 words) shown on screen
- Reference real psychology (Pavlov, Kahneman, dopamine, cortisol, etc.) — sounds credible
- Use contrast: "Most people do X. High performers do Y instead."
- End regular videos with: "If this helped you, subscribe — I drop psychology secrets every week. Comment below: which of these are you guilty of?"
- End shorts with: "Follow for more psychology tricks your school never taught you."

═══ TEXT OVERLAY RULES ═══
- Max 5 words, ALL CAPS
- Must be the single most shocking/intriguing phrase from that scene
- Examples: "YOUR BRAIN IS LYING", "THIS REWIRES EVERYTHING", "MOST PEOPLE MISS THIS"

Respond ONLY with valid JSON, no markdown fences, no extra text:
{{
  "title": "viral title using one of the 7 formulas above, 50-65 chars",
  "description": "SEO YouTube description 200 words — open with the hook, include keywords: psychology, self improvement, motivation, mindset, productivity, success, habits, brain, mental health, personal development",
  "tags": ["psychology", "motivation", "self improvement", "success mindset", "habits", "productivity", "mindset", "brain psychology", "life advice", "personal development", "how to focus", "stop procrastinating"],
  "thumbnail_text": "3-5 word ALL CAPS thumbnail text — most shocking phrase from the video",
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

    response = _client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.85,
        max_tokens=4096,
    )

    data = _parse_json(response.choices[0].message.content)

    required = ["title", "description", "tags", "scenes"]
    for key in required:
        if key not in data:
            raise ValueError(f"Missing key in response: {key}")

    return data


def pick_topic(slot_index: int = 0) -> str:
    """Deterministically pick a topic by date + slot so all 6 daily workflows get different topics."""
    day = datetime.date.today().timetuple().tm_yday  # 1-365
    idx = (day * 6 + slot_index) % len(DAILY_TOPICS)
    return DAILY_TOPICS[idx]
