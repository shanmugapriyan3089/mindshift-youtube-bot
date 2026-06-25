import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")
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
    # Curiosity gap — makes viewers feel they're missing critical info
    "Your Brain Is Lying to You Every Single Day — Here Is How",
    "Stop Checking Your Phone — It Is Rewiring Your Brain Right Now",
    "Why You Cannot Wake Up Early (It Is Not Laziness)",
    "The Reason You Self-Sabotage Every Time You Get Close to Success",
    "Your Dopamine System Is Broken — Here Is How to Fix It",
    "Why Smart People Stay Poor While Average People Get Rich",
    "The Silent Habit That Is Destroying Your Confidence Every Day",
    "Why You Feel Empty After Getting Everything You Wanted",
    "Your Subconscious Mind Makes 95 Percent of Your Decisions",
    "The Psychology Behind Why You Procrastinate and Cannot Stop",
    "Why People Who Talk Less Are Secretly More Powerful",
    "The Real Reason You Cannot Stop Negative Thoughts",
    "How Your Childhood Is Still Controlling You Right Now",
    "Why Motivation Always Fails You and What Actually Works",
    "The Dark Side of Social Media Your Brain Cannot Resist",
    "Why Most People Are Addicted to Being Busy But Never Productive",
    "The One Cognitive Bias Keeping You Stuck in the Same Place",
    "How Rich People Think Differently and Why Schools Never Teach It",
    "Why You Keep Attracting the Wrong People Into Your Life",
    "The Sleep Habit That Silently Doubles Your Intelligence",
    "Why Discipline Is a Myth and What High Performers Do Instead",
    "How to Make People Respect You Without Saying a Word",
    "The Manipulation Tactic Used on You Every Single Day",
    "Why Your Brain Craves Drama and How to Break the Addiction",
    "The Science of First Impressions — You Have 7 Seconds",
    "Why the People Who Read the Most Are Usually the Loneliest",
    "How to Stop Caring What People Think — The Psychology Behind It",
    "The Money Mindset Keeping 99 Percent of People Broke Forever",
    "Why High Achievers Are Almost Always Secretly Miserable",
    "How Your Environment Controls Your Willpower Without You Knowing",
    "The Body Language Trick That Makes Anyone Trust You Instantly",
    "Why Saying No Is the Most Powerful Word Successful People Use",
    "How to Rewire Your Brain After Years of Negative Thinking",
    "The Reason Intelligent People Struggle More With Anxiety",
    "Why Most Friendships Are Slowly Draining Your Energy",
    "How Billionaires Use Boredom as a Superpower",
    "The Psychological Reason You Cannot Finish What You Start",
    "Why the Comfort Zone Is Actually Killing Your Future",
    "How to Become Mentally Unbreakable in 30 Days",
    "The Hidden Cost of Being Too Nice to Everyone Around You",
    # Pain-naming topics — name the exact emotional moment (research-backed format)
    "You Keep Replaying That Conversation and Cannot Stop — Here Is Why",
    "Why You Quit on Day Four Every Single Time You Try to Change",
    "The Exact Moment Your Brain Decides to Sabotage Your Own Success",
    "Why You Feel Guilty When You Rest Even After Working All Day",
    "The Loop in Your Head at 2am Is Not Anxiety — It Is This",
    "Why Intelligent People Talk Themselves Out of Every Opportunity",
    "You Know Exactly What to Do and Still Cannot Make Yourself Do It",
    "The Real Reason You Apologize When You Have Done Nothing Wrong",
    "Why You Lose Energy Around Certain People Without Knowing Why",
    "The Invisible Script Running in Your Head Since You Were Eight",
    "Why You Cannot Accept Compliments and What It Is Actually Costing You",
    "The Reason You Are Always Waiting for the Right Time That Never Comes",
    "Why Your Brain Treats Criticism From Strangers Like a Physical Threat",
    "You Are Not Lazy — Your Nervous System Is Stuck in Survival Mode",
    "The Comparison Trap Your Brain Falls Into Thirty Times a Day",
]

# Auto-updated by Agent 2 every Monday — winning tags + title formulas from competitor intel
WINNING_TAGS = [
    "motivation", "psychology", "self improvement", "success", "confidence",
    "productivity", "personal development", "mindset", "habits", "self help",
    "inspiration", "mental health",
]

TITLE_FORMULAS = [
    "Give Me X Minutes and I'll Make You [Result]",
    "[Number] Psychology Tricks That [Benefit]",
    "Why 99% of People [Problem] (The Uncomfortable Truth)",
    "Stop Doing This If You Want to [Benefit]",
    "The [Adjective] Truth About [Topic] Nobody Tells You",
]

# Output paths
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
REGULAR_OUTPUT_DIR = os.path.join(OUTPUT_DIR, "regular")
SHORTS_OUTPUT_DIR = os.path.join(OUTPUT_DIR, "shorts")
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
MUSIC_DIR = os.path.join(ASSETS_DIR, "music")

# Video specs
REGULAR_VIDEO = {"width": 1920, "height": 1080, "duration": 540, "scenes": 20, "fps": 12}
SHORTS_VIDEO = {"width": 1080, "height": 1920, "duration": 24, "scenes": 2, "fps": 12}
