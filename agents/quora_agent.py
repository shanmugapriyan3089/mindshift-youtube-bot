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

CHANNEL_URL = "https://youtube.com/@mindshift-productive"
CHANNEL_NAME = "MindShift Productivity"


def _generate_qa_pairs(client: Groq, topics: list) -> list:
    topics_str = "\n".join(f"- {t}" for t in topics[:12])

    prompt = f"""You write Quora answers for a psychology/motivation YouTube channel called "{CHANNEL_NAME}".

Our video topics:
{topics_str}

Generate 5 Quora question + answer pairs where:
1. The question is something people genuinely search on Quora
2. The answer is detailed, practical, and 220-280 words
3. The answer ends naturally with: "I covered this topic in depth on my YouTube channel: {CHANNEL_URL}"
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
    print("[Agent 6: Quora] Generating Q&A pairs...")
    pairs = _generate_qa_pairs(client, DAILY_TOPICS)

    if not pairs:
        send("⚠️ <b>Quora Agent</b>: Could not generate Q&A pairs. Groq may be busy.")
        return

    message = "📝 <b>Agent 6: Quora Answers Ready to Post</b>\n(Go to Quora.com, search these questions)\n"

    for i, pair in enumerate(pairs[:5], 1):
        q = pair.get("question", "")
        a = pair.get("answer", "")

        # Cap to Telegram limit but show enough to copy
        preview_a = a[:600] + ("..." if len(a) > 600 else "")

        message += f"""
━━━━━━━━━━━━━━━━━━
<b>Q{i}:</b> {q}

<b>Answer:</b>
{preview_a}
"""

    message += f"\n\n🔍 <b>How to post:</b> Search each question on quora.com → Click 'Answer' → Paste your answer\n📈 Quora answers get views for years — worth the 5 minutes!"
    send(message)


if __name__ == "__main__":
    main()
