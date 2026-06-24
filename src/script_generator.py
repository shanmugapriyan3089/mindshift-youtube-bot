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

CRITICAL: Each scene narration must be 60-75 words. This is how you hit 8-10 minutes.
Speak like a smart, direct friend — not a robot or professor. Use "you" throughout.
duration_seconds for each scene: 27"""
    else:
        duration_label = "55-58 seconds"
        scene_guide = f"""Exactly {num_scenes} scenes. Ultra fast-paced. Hook in first 3 seconds.
Each scene narration: 10-15 words max. Punchy. One idea per scene.
duration_seconds for each scene: 13"""

    prompt = f"""You are a top YouTube scriptwriter for a viral psychology/motivation channel like Jamie Social, Trust Me Bro, or EverythingProfessor.

Write a complete, deeply engaging script for a {video_type} YouTube video about:
"{topic}"

Target audience: 18-35 year olds interested in self-improvement, psychology, money, success.
Duration: {duration_label}
{scene_guide}

Rules:
- Hook viewer in FIRST 5 seconds — ask a question they can't ignore
- Use "you" to speak directly to the viewer throughout
- Each scene has a bold text overlay (max 6 words) shown on screen
- Alternate background colors: #1a1a2e (dark navy), #16213e (dark blue), #0f3460 (blue), #533483 (purple)
- End with a strong CTA: "Subscribe for more psychology secrets" + ask them to comment

Respond ONLY with valid JSON, no markdown fences, no extra text:
{{
  "title": "clickbait but honest YouTube title 45-65 chars — like: '7 Psychology Tricks That Make People Like You Instantly'",
  "description": "SEO YouTube description 200 words with keywords for self-improvement, psychology, motivation, success mindset",
  "tags": ["psychology", "motivation", "self improvement", "success mindset", "habits", "productivity", "mindset", "success tips", "life advice", "personal development"],
  "thumbnail_text": "bold 4-6 word ALL CAPS thumbnail text",
  "scenes": [
    {{
      "scene_number": 1,
      "duration_seconds": 27,
      "narration": "What if I told you that 95 percent of your daily decisions are made subconsciously? That means right now, invisible forces are controlling your choices, your habits, and your future — and you have no idea. By the end of this video, you will understand exactly how this works and how to take back control of your own mind.",
      "text_overlay": "YOU ARE NOT IN CONTROL",
      "bullets": ["95% of decisions are subconscious", "Your brain runs on autopilot", "You can rewire this"],
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
