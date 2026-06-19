# Brand Context Loader
# Reads company profile + past posts so agents stay on-brand.
# Safe to use even with placeholder/empty data — won't crash if fields are missing.

import json
import os

BRAND_DIR = os.path.dirname(__file__)

def load_brand_profile() -> dict:
    path = os.path.join(BRAND_DIR, "profile.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def load_previous_posts() -> list:
    path = os.path.join(BRAND_DIR, "previous_posts.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("posts", [])
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def get_brand_context_string() -> str:
    """Returns a compact text block to inject into agent prompts.
    Falls back gracefully if no real company data has been added yet."""
    profile = load_brand_profile()
    posts   = load_previous_posts()

    if not profile:
        return "No company brand profile set yet. Write generic professional social media content."

    services = ", ".join(profile.get("services", [])[:5]) or "Not specified"
    voice    = profile.get("brand_voice", {})

    context = f"""COMPANY: {profile.get('company_name', 'Not specified')}
TAGLINE: {profile.get('tagline', '')}
WHAT WE DO: {profile.get('what_we_do', 'Not specified')}
KEY SERVICES: {services}
BRAND TONE: {voice.get('tone', 'professional')}
STYLE NOTES: {voice.get('style_notes', '')}
KEYWORDS TO USE: {', '.join(voice.get('keywords_to_use', []) or [])}
AVOID: {', '.join(voice.get('avoid', []) or [])}
TARGET AUDIENCE: {profile.get('target_audience', '')}
"""

    if posts:
        context += "\nEXAMPLE PAST POSTS (match this tone/style):\n"
        for p in posts[:3]:
            context += f"- [{p.get('platform','')}] {p.get('content','')[:140]}...\n"

    return context