import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
KLING_ACCESS_KEY = os.getenv("KLING_ACCESS_KEY")
KLING_SECRET_KEY = os.getenv("KLING_SECRET_KEY")
PIKA_API_KEY = os.getenv("PIKA_API_KEY")
HAILUO_API_KEY = os.getenv("HAILUO_API_KEY")
HAILUO_GROUP_ID = os.getenv("HAILUO_GROUP_ID")
RUNWAY_API_KEY = os.getenv("RUNWAY_API_KEY")
YOUTUBE_CLIENT_SECRETS_PATH = os.getenv("YOUTUBE_CLIENT_SECRETS_PATH", "client_secrets.json")

# Channel settings
CHANNEL_NICHE = os.getenv("CHANNEL_NICHE", "psychology motivation self-improvement")
MADE_FOR_KIDS = False  # Adult audience = full monetization, no COPPA restrictions

# Animation style — clean minimal 2D like Productive Peter
ANIMATION_STYLE = "minimal 2D animation, clean white background, simple stick figures, bold text overlays, smooth transitions, professional motivational style"

# Video topics — psychology, habits, success mindset (HIGH RPM niche)
DAILY_TOPICS = [
    "5 Psychology Tricks That Make People Instantly Like You",
    "Why 99% of People Stay Broke (The Uncomfortable Truth)",
    "7 Habits of People Who Never Feel Stressed",
    "The Morning Routine That Separates Winners From Losers",
    "5 Signs You Are More Intelligent Than You Think",
    "How to Rewire Your Brain for Success in 21 Days",
    "The Dark Psychology Behind Why People Manipulate You",
    "5 Things Mentally Strong People Never Do",
    "Why Most People Never Achieve Their Goals (And How to Fix It)",
    "The Sleep Habit That Doubles Your Productivity",
    "7 Body Language Tricks That Make You Look Confident",
    "How Rich People Think Differently About Money",
    "The 5 AM Club — Why Waking Up Early Changes Everything",
    "5 Psychological Facts About Human Behavior That Will Blow Your Mind",
    "Why Smart People Stay Quiet (The Power of Silence)",
    "The One Habit That Changed Everything — Atomic Habits Explained",
    "How to Stop Procrastinating Forever (Backed by Science)",
    "5 Signs Someone Is Secretly Jealous of You",
    "The Millionaire Morning Routine Nobody Talks About",
    "How to Read Anyone's Mind Using Body Language",
    "Why Discipline Always Beats Motivation",
    "5 Lessons From The Richest People in History",
    "The Science of Getting Rich — What Schools Never Teach You",
    "How to Build Unshakeable Confidence From Zero",
    "7 Stoic Principles That Will Change Your Life",
    "Why Most Relationships Fail (Psychology Explained)",
    "The Power of Saying No — How Boundaries Change Your Life",
    "5 Daily Habits of Billionaires You Can Copy Today",
    "How to Become the Most Interesting Person in Any Room",
    "The Truth About Why Hard Work Alone Never Makes You Rich",
]

# Output paths
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
REGULAR_OUTPUT_DIR = os.path.join(OUTPUT_DIR, "regular")
SHORTS_OUTPUT_DIR = os.path.join(OUTPUT_DIR, "shorts")
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
MUSIC_DIR = os.path.join(ASSETS_DIR, "music")

# Video specs
REGULAR_VIDEO = {"width": 1920, "height": 1080, "duration": 120, "scenes": 8, "fps": 12}
SHORTS_VIDEO = {"width": 1080, "height": 1920, "duration": 58, "scenes": 4, "fps": 12}
