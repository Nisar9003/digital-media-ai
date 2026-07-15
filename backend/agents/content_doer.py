# Content Doer Agent — Groq (LLaMA 3.3, free tier)
# Writes BOTH the social caption (structured, platform-optimized, emoji-rich)
# AND structured poster copy (headline/sub_headline/highlights/cta) used by poster_composer.py

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from brand.loader import get_brand_context_string, load_brand_profile
import os
import json
import re
import traceback

llm = ChatOpenAI(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY", "dummy"),
    base_url="https://api.groq.com/openai/v1"
)


def build_caption_format_guide(platform: str) -> str:
    """Returns platform-specific caption structure guidelines."""
    guides = {
        "linkedin": """
LINKEDIN CAPTION FORMAT — Follow this structure exactly:

Line 1: Strong opening hook with 1 relevant emoji (make people stop scrolling)
[blank line]
Lines 2-4: Context / story / value (2-3 sentences max, conversational tone)
[blank line]
If the post has list items (jobs, services, features, benefits):
  Use this format for each item:
  🔹 **Item Name**
  📍 Detail or sub-info
  [blank line between items]
[blank line]
Call to action line with emoji
[blank line]
Contact info line:
📧 email | 🌐 website | 📞 phone
[blank line]
Tag line: "Tag someone who needs to see this! 👇" or similar
[blank line]
Hashtags: 10-15 hashtags, mix of broad + niche + company branded
Example: #WebDevelopment #MobileApps #KeyDevs #PakistanTech #Lahore #SoftwareHouse

IMPORTANT: Write naturally, like a real human professional — NOT like a marketing template.
Use line breaks exactly as shown above. Do NOT use markdown bold (**) except for item names in lists.
""",
        "instagram": """
INSTAGRAM CAPTION FORMAT:

Line 1: Bold hook — make it punchy, max 125 chars (visible before "more")
[blank line]
2-3 short paragraphs with emojis mixed in naturally
[blank line]
CTA line
[blank line]
. (dot on its own line — Instagram trick to push hashtags down)
.
.
Hashtags: 20-25 hashtags in first comment OR at bottom after dots
""",
        "facebook": """
FACEBOOK CAPTION FORMAT:

Conversational, story-telling style. 
Start with a question or statement that creates curiosity.
2-3 paragraphs, each 2-3 sentences.
End with a clear question or CTA to drive comments.
2-3 hashtags only (Facebook penalizes heavy hashtag use).
""",
        "tiktok": """
TIKTOK CAPTION FORMAT:

Ultra short — max 150 characters total.
First 3 words must be a STRONG hook.
1-2 emojis only.
3-5 hashtags including #fyp #foryoupage + niche tags.
"""
    }
    return guides.get(platform, guides["linkedin"])


def build_system_prompt(platform: str) -> str:
    brand = get_brand_context_string()
    profile = load_brand_profile()
    contact = profile.get("contact", {})
    website = profile.get("website", "").replace("https://", "")

    contact_line = " | ".join(filter(None, [
        f"📧 {contact.get('email', '')}" if contact.get('email') else "",
        f"🌐 {website}" if website else "",
        f"📞 {contact.get('phone', '')}" if contact.get('phone') else "",
    ]))

    caption_guide = build_caption_format_guide(platform)

    return f"""You are a professional social media content writer for this company.

{brand}

Company contact line to include in caption: {contact_line}

{caption_guide}

Write content that sounds like it comes from a real human at this company —
not a marketing robot. Match the company's tone: professional, confident,
results-driven, uses real stats and proof points.

Respond in JSON format only, with this EXACT structure:
{{
  "caption": "the FULL caption text, formatted exactly per the platform guidelines above, ready to copy-paste — including emojis, line breaks, hashtags, contact line",
  "hashtags": ["#tag1", "#tag2", "#tag3"],
  "poster_layout": "centered" or "split",
  "visual_concept": "abstract" or "device_mockup" or "workspace_photo" or "icons_grid",
  "visual_description": "1-2 sentence description of what should be IN the background image",
  "poster": {{
    "headline": "max 6 words, punchy headline for the IMAGE",
    "sub_headline": "max 12 words supporting line",
    "highlights": ["short phrase 1", "short phrase 2", "short phrase 3"],
    "cta": "max 4 words button text"
  }}
}}

RULES:
- "caption" must be the complete, ready-to-post text — no placeholders
- "hashtags" array should match what's in the caption (for display purposes)
- "poster" fields are SHORT (they appear as text overlaid ON the image)
- For "poster_layout": use "split" for greetings/occasions, "centered" for all business posts
- For "visual_concept":
    "device_mockup" → post is about a website, app, dashboard, digital product
    "workspace_photo" → post is about team, process, company culture, thought leadership
    "icons_grid" → post is about multiple platforms, channels, or a list of tools
    "abstract" → general branding, announcements, anything else
- Do NOT include contact details in "poster" fields — they're on the image footer already
"""


async def run_content_doer(state: dict) -> dict:
    brief    = state.get("brief", "")
    feedback = state.get("content_feedback", "")
    goal     = state.get("goal", "")
    platform = state.get("platform", "linkedin")

    prompt = f"Goal: {goal}\nPlatform: {platform}\nBrief: {brief}"
    if feedback:
        prompt += f"\n\nRevision needed. Feedback: {feedback}"

    try:
        response = await llm.ainvoke([
            SystemMessage(content=build_system_prompt(platform)),
            HumanMessage(content=prompt)
        ])
        raw = response.content.strip()
        raw = re.sub(r'^```(?:json)?\s*|\s*```$', '', raw.strip())

        parsed = json.loads(raw)
        state["content"] = json.dumps(parsed)
        state["poster_copy"] = parsed.get("poster", {})
        state["poster_layout"] = parsed.get("poster_layout", "centered")
        if state["poster_layout"] not in ("centered", "split"):
            state["poster_layout"] = "centered"
        state["visual_concept"] = parsed.get("visual_concept", "abstract")
        if state["visual_concept"] not in ("abstract", "device_mockup", "workspace_photo", "icons_grid"):
            state["visual_concept"] = "abstract"
        state["visual_description"] = parsed.get("visual_description", "")

    except Exception as e:
        print("=" * 60)
        print("CONTENT_DOER ERROR (real cause):")
        print(repr(e))
        traceback.print_exc()
        print("=" * 60)
        fallback_caption = f"🚀 {goal}\n\nKeyDevs Technologies — building digital solutions that deliver real results.\n\n📧 sales@keydevs.com | 🌐 keydevs.pk | 📞 +92 321 7851671\n\n#KeyDevs #WebDevelopment #MobileApps #Pakistan"
        fallback = {
            "caption": fallback_caption,
            "hashtags": ["#KeyDevs", "#WebDevelopment", "#MobileApps"],
            "poster_layout": "centered",
            "visual_concept": "abstract",
            "visual_description": "",
            "poster": {
                "headline": "Build Something Great",
                "sub_headline": "Tailored digital solutions for your business",
                "highlights": ["Custom Development", "Modern Design", "Proven Results"],
                "cta": "Contact Us Today"
            }
        }
        state["content"] = json.dumps(fallback)
        state["poster_copy"] = fallback["poster"]
        state["poster_layout"] = "centered"
        state["visual_concept"] = "abstract"
        state["visual_description"] = ""

    return state