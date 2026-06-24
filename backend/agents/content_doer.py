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

def build_system_prompt() -> str:
    brand = get_brand_context_string()
    return f"""You are a social media content writer for this company.

{brand}

Write engaging content that sounds like it genuinely comes from this company —
match their tone, vocabulary, and the style of their past posts.

Respond in JSON format only, with this exact structure:
{{
  "hook": "attention-grabbing first line for the caption",
  "body": "main caption text (2-4 sentences)",
  "cta": "call to action for the caption",
  "hashtags": ["#tag1", "#tag2", "#tag3"],
  "poster_layout": "centered" or "split",
  "visual_concept": "abstract" or "device_mockup" or "workspace_photo" or "icons_grid",
  "visual_description": "a short, specific description (1-2 sentences) of what should actually be IN the background image, based on the goal — see guidance below",
  "poster": {{
    "headline": "short punchy headline, max 6 words, for the IMAGE itself",
    "sub_headline": "one short supporting line, max 12 words",
    "highlights": ["short phrase 1", "short phrase 2", "short phrase 3"],
    "cta": "very short button text, max 4 words, e.g. 'Contact Us Today'"
  }}
}}

IMPORTANT: poster.headline, poster.sub_headline, poster.highlights, and poster.cta
will be rendered as actual text ON the image, so keep them SHORT and punchy —
this is not the same as the caption body.

For "poster_layout", choose:
- "split" — if the goal is a GREETING or OCCASION post (Eid, religious holidays,
  New Year, company anniversary, festive wishes, congratulatory messages).
  This layout keeps background art on one side and text on the other, like a
  greeting card.
- "centered" — for everything else (service promotion, product announcements,
  case studies, general marketing). This is the default for business content.

For "visual_concept", pick the option that best matches what the post is
actually about — this controls what the AI-generated background image will
contain:
- "device_mockup" — if the goal is about a website, app, dashboard, or any
  digital product/screen (e.g. "we redesigned a website", "new app launch").
  The background will show a laptop/phone/browser mockup displaying a clean
  modern interface.
- "workspace_photo" — if the goal is about a team, process, working style, or
  a relatable everyday business/professional moment (e.g. "our design
  process", "meet the team", general thought-leadership). The background
  will be a realistic photo-style scene (desk, laptop, people working,
  natural lighting).
- "icons_grid" — if the goal explicitly involves multiple platforms,
  channels, or a list of distinct tools/services (e.g. "we post on every
  social platform", "our tech stack"). The background will show small
  relevant icon-like shapes arranged around the edges.
- "abstract" — default fallback for general branding, announcements, or
  anything that doesn't fit the above (gradient background with soft
  geometric shapes, no concrete objects). Use this whenever you're unsure.

For "visual_description", write what the background should show in plain,
concrete language (e.g. "A laptop screen showing a clean, modern website
homepage with a navigation bar and hero image" or "A tidy desk with a laptop,
notebook, and coffee cup, shot from a slight angle, natural daylight").
Keep it to 1-2 sentences. This will be combined with style instructions
automatically — do not mention colors, branding, or text in this field.

Do NOT include contact details (email, phone, website) yourself —
that will be added automatically after your response.
"""


def build_contact_footer() -> str:
    """Pulls contact info straight from profile.json — never from the LLM,
    so the email/phone/website are always exactly correct."""
    profile = load_brand_profile()
    contact = profile.get("contact", {})
    website = profile.get("website", "")

    lines = []
    if website:
        lines.append(f"🌐 {website}")
    if contact.get("email"):
        lines.append(f"📧 {contact['email']}")
    if contact.get("phone"):
        lines.append(f"📞 {contact['phone']}")

    return "\n".join(lines)


async def run_content_doer(state: dict) -> dict:
    brief    = state.get("brief", "")
    feedback = state.get("content_feedback", "")
    goal     = state.get("goal", "")

    prompt = f"Goal: {goal}\nBrief: {brief}"
    if feedback:
        prompt += f"\n\nRevision needed. Feedback: {feedback}"

    contact_footer = build_contact_footer()

    try:
        response = await llm.ainvoke([
            SystemMessage(content=build_system_prompt()),
            HumanMessage(content=prompt)
        ])
        raw = response.content.strip()

        # Strip markdown code fences if the model added them
        raw = re.sub(r'^```(?:json)?\s*|\s*```$', '', raw.strip())

        parsed = json.loads(raw)

        # Append the deterministic contact footer to the caption body
        if contact_footer:
            parsed["body"] = f"{parsed.get('body', '')}\n\n{contact_footer}"

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
        fallback_body = "Draft content"
        if contact_footer:
            fallback_body += f"\n\n{contact_footer}"
        fallback = {
            "hook": "Draft hook", "body": fallback_body, "cta": "Learn more",
            "hashtags": ["#ai", "#socialmedia"],
            "poster": {
                "headline": "Need a Mobile App?",
                "sub_headline": "We design and develop your next big idea",
                "highlights": ["Custom Development", "Modern UI/UX", "Ongoing Support"],
                "cta": "Contact Us Today"
            }
        }
        state["content"] = json.dumps(fallback)
        state["poster_copy"] = fallback["poster"]
        state["poster_layout"] = "centered"
        state["visual_concept"] = "abstract"
        state["visual_description"] = ""

    return state