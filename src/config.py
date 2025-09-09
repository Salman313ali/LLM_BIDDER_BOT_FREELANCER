"""
Configuration settings for the Freelancer Bot
"""
import os
from typing import List, Set

# API Configuration
OAUTH_TOKEN = os.getenv('FREELANCER_OAUTH_TOKEN', '')
GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')

# Bot Configuration
BID_LIMIT = int(os.getenv('BID_LIMIT', '75'))
PROJECT_SEARCH_LIMIT = int(os.getenv('PROJECT_SEARCH_LIMIT', '10'))
MIN_WAIT_TIME = int(os.getenv('MIN_WAIT_TIME', '32'))
RETRY_COUNT = int(os.getenv('RETRY_COUNT', '3'))
RETRY_WAIT_SECONDS = int(os.getenv('RETRY_WAIT_SECONDS', '5'))

# Skill IDs for project filtering
SKILL_IDS = [
    3, 9, 13, 15, 17, 20, 21, 26, 32, 38, 44, 57, 69, 70, 77, 106, 107, 115, 116, 127, 137, 168, 170, 174, 196, 197, 204, 229, 232, 234, 247, 250, 262, 264, 277, 278, 284, 305, 310, 323, 324, 335, 359, 365, 368, 369, 371, 375, 408, 412, 433, 436, 444, 445, 482, 502, 564, 624, 662, 710, 759, 878, 950, 953, 959, 1063, 1185, 1314, 1623, 2071, 2128, 2222, 2245, 2338, 2342, 2507, 2586, 2587, 2589, 2605, 2625, 2645, 2673, 2698, 2717, 2745
]

# Language codes
LANGUAGE_CODES = ['en']

# Unwanted currencies and countries
UNWANTED_CURRENCIES: Set[str] = {"INR", "PKR", "BDT"}
UNWANTED_COUNTRIES: Set[str] = {
    "india", "bangladesh", "pakistan", "jamaica", "srilanka", "sri lanka", "nepal",
    "south africa", "kenya", "uganda", "egypt", "indonesia", "philippines", "afganistan"
}

# Portfolio links
PORTFOLIO_LINKS = {
    "sticker_designs": "https://www.pinterest.com/parsantal/premium-stickers/",
    "ui_ux": "https://www.pinterest.com/parsantal/premium-ui-ux-design/",
    "packaging_design": "https://www.pinterest.com/parsantal/premium-packaging-branding/",
    "menu_design": "https://www.pinterest.com/parsantal/premium-menu-designs/",
    "logo_design": "https://www.pinterest.com/parsantal/premium-logo/",
    "illustrations": "https://www.pinterest.com/parsantal/premium-illustrations/"
}

# Base project components with budget and timeline
BASE_PROJECT_COMPONENTS = {
    "website_design_development": {"budget": 1500, "timeline": 14},
    "website_development_only": {"budget": 850, "timeline": 12},
    "logo_design": {"budget": 50, "timeline": 2},
    "custom_artwork": {"budget": 120, "timeline": 2},
    "ecommerce_development": {"budget": 1750, "timeline": 20},
    "ui_ux_design": {"budget": 350, "timeline": 7},
    "vector_illustration": {"budget": 150, "timeline": 5}
}

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./freelancer_bot.db')

# Logging configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'bot.log')

# User Configuration (can be overridden via dashboard)
SERVICE_OFFERINGS = os.getenv('SERVICE_OFFERINGS', """1. Website Development:
   - We specialize exclusively in website development projects using CMS platforms. Supported CMS platforms include WordPress, E-Commerce platforms, GoDaddy, Wix, Shopify, and similar systems, for the custom technology, we only work on ReactJS
   - We do not provide custom development services using frameworks such as, Laravel, etc.
   - We only work on projects that require building a website from scratch. If the project is solely about fixing or maintaining an existing website, it should be considered 'NO MATCH'.

2. Graphic Design:
   - We provide all types of graphic design services (e.g., vector illustrations, logo design,branding, brochures, flyers, banners, etc.).
   - PPT & Logo design is also a part of our service.""")

BID_WRITING_STYLE = os.getenv('BID_WRITING_STYLE', """Write a professional freelance proposal/bid for the given project. Follow this specific format and quality level:

⸻

✅ STRUCTURE & FLOW
	1.	Start immediately with a strong, natural-sounding sentence that connects with the client's main goal (skip all greetings and intros).
	2.	Demonstrate relevant experience, referencing similar past work with measurable or outcome-based results.
	3.	Show understanding of the client's needs and hint at key deliverables without listing them.
	4.	End with a confident, reassuring promise, tied to their end goal — include a subtle risk reversal (e.g., revisions offered, collaboration-friendly, client satisfaction focus).
    5.  Ask two most relevant and mandatory questions about the project to show your interest and understanding of the project.
	6.	After the main bid, write:
Here's my previous related work according to your needs:
And then insert 1 or 2 portfolio links that are directly relevant to the project.
	7.	Finish with this signature:
Regards,
{signature}

⸻

🎯 TONE & STYLE
	•	Human, confident, but not robotic or over-polished.
	•	No hype or dramatic exaggeration — just clarity, warmth, and a clear understanding of the client's pain points.
	•	Keep it results-focused and outcome-oriented, not feature-dumping.
	•	Make it sound like a real person who cares, not a sales pitch.

⸻

IMPORTANT NOTE!
: Keep it within 80 words, using a conversational, Spartan tone in Pakistani English with clear, short paragraphs for easy readability. Avoid corporate jargon
•⁠  ⁠Drop the link as it is. Don't add markdown to make it clickable
•⁠  ⁠Don't use boldface for anything.
•⁠  ⁠as I'm copy pasting the text and bullet points come under text markdown which is not supported where I'm using
•⁠  ⁠FORAMTE TEXT AND LINKS properly so I can just copy-paste it and it's easy to read
•⁠  ⁠⁠If the project is in a specific industry (e.g. dental, fashion, B2B, tech), use language that aligns with that niche.
•⁠  ⁠Don't ever start with "Hi" or "Dear" — go straight into value.
•⁠  ⁠Don't use '—' use ',' instead.""")

PORTFOLIO_LINKS_TEXT = os.getenv('PORTFOLIO_LINKS', """1. premium sticker designs : https://www.pinterest.com/parsantal/premium-stickers/
2. for premium  UI/UX: https://www.pinterest.com/parsantal/premium-ui-ux-design/
3. for premium packaging design : https://www.pinterest.com/parsantal/premium-packaging-branding/
4. for premiuim menu design : https://www.pinterest.com/parsantal/premium-menu-designs/
5. for premium logo design : https://www.pinterest.com/parsantal/premium-logo/
6. for premium illustration designs : https://www.pinterest.com/parsantal/premium-illustrations/""")

SIGNATURE = os.getenv('SIGNATURE', 'Parsanta Lal')

