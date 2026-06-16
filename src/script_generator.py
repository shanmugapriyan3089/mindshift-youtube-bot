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
    duration_label = "8-10 minutes" if video_type == "regular" else "55-58 seconds"
    num_scenes = spec["scenes"]

    prompt = f"""You are a top YouTube scriptwriter for a viral motivational/psychology channel.

Write a complete, highly engaging script for a {video_type} YouTube video about:
"{topic}"

Target audience: 18-35 year olds interested in self-improvement, psychology, money, success.
Duration: {duration_label}
Scenes: exactly {num_scenes} scenes
Style: Direct, punchy, slightly controversial to hook viewers. Like Productive Peter or Alux.com.

Rules:
- Hook the viewer in the FIRST 5 seconds (make them NEED to watch)
- Use "you" to speak directly to the viewer
- Each scene has a bold text overlay (max 6 words) shown on screen
- Alternate background colors between: #1a1a2e (dark navy), #16213e (dark blue), #0f3460 (blue), #533483 (purple)
- End with a strong call to action (like, subscribe, comment)

Respond ONLY with valid JSON, no markdown fences, no extra text:
{{
  "title": "clickbait but honest YouTube title (max 60 chars)",
  "description": "SEO YouTube description 200 words with keywords for self-improvement, psychology, motivation, success mindset",
  "tags": ["psychology", "motivation", "self improvement", "success mindset", "habits", "productivity", "mindset", "success tips", "life advice", "personal development"],
  "thumbnail_text": "bold 4-word thumbnail text",
  "scenes": [
    {{
      "scene_number": 1,
      "keyword": "busy office people",
      "duration_seconds": 12,
      "narration": "What if I told you that 95% of your decisions are made subconsciously? That means you're not as in control as you think...",
      "text_overlay": "YOU ARE NOT IN CONTROL",
      "keyword": "human brain psychology",
      "bullets": ["Fact or stat about this scene", "Key insight", "Action step"],
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
