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

# Video topics — NICHE: psychology of being stuck / why you cannot change even when you want to.
# All topics must relate to one core feeling: "I know what I should do and I still cannot do it."
# Tight niche = algorithm clusters us correctly = higher recommendation frequency.
DAILY_TOPICS = [
    # ── Core stuck-loop topics ───────────────────────────────────────────────────
    "You Keep Replaying That Conversation and Cannot Stop — Here Is Why",
    "Why You Quit on Day Four Every Single Time You Try to Change",
    "The Loop in Your Head at 2am Is Not Anxiety — It Is This",
    "You Know Exactly What to Do and Still Cannot Make Yourself Do It",
    "You Are Not Lazy — Your Nervous System Is Stuck in Survival Mode",
    "The Reason You Are Always Waiting for the Right Time That Never Comes",
    "Why You Feel Guilty When You Rest Even After Working All Day",
    "The Comparison Trap Your Brain Falls Into Thirty Times a Day",
    "The Invisible Script Running in Your Head Since You Were Eight",
    "Why You Cannot Accept Compliments and What It Is Actually Costing You",

    # ── Self-sabotage & the internal critic ──────────────────────────────────────
    "The Exact Moment Your Brain Decides to Sabotage Your Own Success",
    "Why Intelligent People Talk Themselves Out of Every Opportunity",
    "The Real Reason You Apologize When You Have Done Nothing Wrong",
    "Why Your Brain Treats Criticism From Strangers Like a Physical Threat",
    "The Reason You Self-Sabotage Every Time You Get Close to Success",
    "Why You Freeze When You Finally Get What You Were Working For",
    "The Part of You That Does Not Believe You Deserve Good Things",
    "Why Your Brain Panics the Moment Things Start Going Well",

    # ── Overthinking & anxiety loops ─────────────────────────────────────────────
    "Why You Cannot Stop Overthinking No Matter How Hard You Try",
    "The Real Reason You Cannot Stop Negative Thoughts",
    "How Your Childhood Is Still Running Your Life in the Background",
    "Why Your Brain Refuses to Let Go of Something That Happened Years Ago",
    "The Exact Pattern That Keeps You Stuck in the Same Year Over and Over",
    "The Science Behind Why You Cannot Stop Overthinking at Night",
    "Why Trying Harder Always Makes Overthinking Worse — The Paradox Explained",

    # ── Procrastination & decision paralysis ─────────────────────────────────────
    "The Psychology Behind Why You Procrastinate and Cannot Stop",
    "The One Cognitive Bias Keeping You Stuck in the Same Place",
    "Why Your Brain Craves Distraction and How to Break the Loop",
    "The Hidden Reason You Keep Starting Over Instead of Finishing",
    "Why Intelligent People Procrastinate More Than Everyone Else",
    "What Actually Happens in Your Brain the Moment You Avoid a Task",
    "Why You Lose Energy Around Certain People Without Knowing Why",

    # ── Emotional regulation & the stuck nervous system ──────────────────────────
    "Your Dopamine System Is Broken — Here Is How to Fix It",
    "Why Motivation Always Fails You and What Actually Works",
    "The Silent Habit That Is Destroying Your Focus Every Single Day",
    "Your Subconscious Mind Makes 95 Percent of Your Decisions",
    "How Your Environment Controls Your Willpower Without You Knowing",
    "The Reason Intelligent People Struggle More With Anxiety",
    "The Body Keeps the Score — How Past Stress Lives in Your Physical Reactions",

    # ── Breaking the cycle (solution-focused) ────────────────────────────────────
    "Why Discipline Is a Myth and What High Performers Actually Do",
    "How to Rewire Your Brain After Years of Negative Thinking",
    "Why the Comfort Zone Is Not Safe — It Is Just Familiar",
    "The Hidden Cost of Being Too Nice to Everyone Around You",
    "Why Saying No Is Not Selfishness — It Is a Survival Mechanism",
    "How to Stop the Thought Loop Before It Becomes a Spiral",
    "The Pattern Interrupt That Actually Works When Anxiety Spikes",

    # ── Identity & self-worth ─────────────────────────────────────────────────────
    "Why You Feel Like a Fraud Even When You Are Actually Good at Things",
    "The Psychological Reason You Cannot Stop People Pleasing",
    "Why You Keep Shrinking Yourself to Make Others Comfortable",
    "The Real Cost of Needing Everyone to Like You",
    "Why Highly Sensitive People Feel Everything So Much More Intensely",
    "The Science of Why You Feel Behind Everyone Else Your Age",
    "Why You Are Hardest on Yourself at 3am and What to Do About It",

    # ── Focus & digital age psychology ───────────────────────────────────────────
    "Why Your Phone Is Physically Rewiring Your Ability to Focus",
    "The Attention Residue Effect — Why Multitasking Is Destroying Your Brain",
    "Why You Cannot Read a Book Anymore and What Social Media Did to You",
    "Decision Fatigue — Why You Make Terrible Choices After 3pm",
    "Why Boredom Is the Most Productive State Your Brain Can Be In",
    "The Science of Deep Work — Why Most People Will Never Focus Again",
    "How Notification Culture Has Shortened Your Attention Span by 40 Percent",

    # ── Relationships & social psychology ────────────────────────────────────────
    "The Spotlight Effect — Nobody Is Watching You as Much as You Think",
    "Why You Replay Arguments in Your Head Instead of Sleeping",
    "The Psychological Reason You Attract the Same Type of Person",
    "Why Loneliness Feels Like a Physical Pain — The Science Explained",
    "How to Stop Absorbing Other People's Emotions Like a Sponge",
    "The Real Reason You Cannot Set Boundaries With Certain People",
    "Why Your Brain Confuses Being Busy With Being Important",

    # ── Growth mindset & high performance ────────────────────────────────────────
    "Why Most Advice About Building Habits Is Completely Wrong",
    "The Two-Minute Rule That Rewired How High Performers Work",
    "Why You Are More Creative When You Are Slightly Bored",
    "The Morning Routine Science — What Actually Matters Before 9am",
    "Why Sleep Deprivation Makes You Overconfident and Dangerously Wrong",
    "How to Build Self-Discipline When You Have Zero Motivation",
    "The Growth Mindset Trap — Why Believing in Yourself Is Not Enough",
    "Why Journaling Works When Nothing Else Does — The Neuroscience",
]

# Auto-updated by Agent 2 every Monday — winning tags + title formulas from competitor intel
WINNING_TAGS = [
    "motivation",
    "productivity",
    "success",
    "confidence",
    "happiness",
    "wealth",
    "psychology",
    "self improvement",
    "personal development",
    "entrepreneurship",
    "business",
]

TITLE_FORMULAS = [
    "X [Topic] to [Result] in X Minutes",
    "The X [Topic] to [Result] in X Steps",
    "X [Benefit] by [Topic] | [Result]",
    "The [Topic] That Will Make You [Benefit]",
    "X [Topic] Hacks to [Result] | [Benefit]",
] to [Result] in X Minutes",
    "The [Adjective] [Topic] to [Result]",
    "X Ways to [Result] with [Topic]",
    "[Topic] Will Make You [Result]",
    "How to [Result] with [Topic] in X Steps",
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
