"""
Agent 6: Quora Content Generator (runs Mon/Wed/Fri)
Generates psychology/motivation Q&A pairs ready to copy-paste to Quora
Each answer naturally links back to the YouTube channel
→ sends 5 Q&A drafts to Telegram for manual posting
"""
import os, sys, json, re
from groq import Groq

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import GROQ_API_KEY, DAILY_TOPICS

CHANNEL_NAME = "MindShift Productivity"


def _get_latest_video_url() -> str:
    import json
    try:
        with open("upload_log.json") as f:
            log = json.load(f)
        regulars = sorted(
            [v for v in log if v.get("type") == "regular"],
            key=lambda x: x.get("uploaded_at", ""), reverse=True
        )
        if regulars:
            return f"https://youtu.be/{regulars[0]['video_id']}"
    except Exception:
        pass
    return "https://youtube.com/@MindShiftProductivity"


def _generate_qa_pairs(client: Groq, topics: list, video_url: str) -> list:
    topics_str = "\n".join(f"- {t}" for t in topics[:12])

    prompt = f"""You write Quora answers for a psychology/motivation YouTube channel called "{CHANNEL_NAME}".

Our video topics:
{topics_str}

Generate 5 Quora question + answer pairs where:
1. The question is something people genuinely search on Quora
2. The answer is detailed, practical, and 220-280 words
3. The answer ends naturally with: "I went deep on this recently: {video_url}"
4. Answers should sound like a knowledgeable person sharing real experience
5. No corporate tone, no hashtags, no "great question!"
6. Each question should be different — cover psychology, habits, mindset, confidence, productivity

Respond with ONLY a JSON array:
[
  {{
    "question": "Why do some people succeed at building good habits while others fail?",
    "answer": "The research on this is actually pretty clear... [full answer ending with channel link]"
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


def main():
    from agents.notifier import send

    client = Groq(api_key=GROQ_API_KEY)
    video_url = _get_latest_video_url()
    print(f"[Agent 6: Quora] Using video URL: {video_url}")
    pairs = _generate_qa_pairs(client, DAILY_TOPICS, video_url)

    if not pairs:
        send("Quora Agent: Could not generate Q&A pairs. Groq may be busy.",
             subject="Agent 6: Quora Answers")
        return

    lines = [
        "Agent 6: Quora Answers Ready to Post",
        "Go to Quora.com, search each question, click Answer, paste the full answer below.",
        "",
    ]

    for i, pair in enumerate(pairs[:5], 1):
        q = pair.get("question", "")
        a = pair.get("answer", "")
        lines += [
            "─" * 40,
            f"Q{i}: {q}",
            "",
            "Copy from here:",
            a,
            "",
        ]

    lines += [
        "─" * 40,
        "How to post: quora.com → search question → Answer → paste → Submit",
        "Quora answers get Google traffic for years — worth 10 minutes!",
    ]
    send("\n".join(lines), subject="Agent 6: Quora Answers Ready to Post")


if __name__ == "__main__":
    main()
