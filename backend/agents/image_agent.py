# Image Agent — Hugging Face Inference (Stable Diffusion XL / FLUX, free tier) is PRIMARY
# Pollinations.ai is the fallback if HF key is missing or the call fails
# Generates clean branded-template style graphics (solid backgrounds, simple shapes)
# Logo position is controlled by the human via logo_position in state (set from frontend)

import httpx
import os
import re
import uuid
import traceback
from PIL import Image
from io import BytesIO

BRAND_DIR  = os.path.join(os.path.dirname(os.path.dirname(__file__)), "brand", "assets")
STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "generated")
LOGO_PATH  = os.path.join(BRAND_DIR, "logo.png")

os.makedirs(STATIC_DIR, exist_ok=True)


def add_logo_watermark(base_image_bytes: bytes, position: dict = None) -> bytes:
    """
    Overlay the company logo at a human-chosen position.
    position = {"x": 0.0-1.0, "y": 0.0-1.0, "scale": 0.05-0.3}
    """
    if not os.path.exists(LOGO_PATH):
        return base_image_bytes

    try:
        base = Image.open(BytesIO(base_image_bytes)).convert("RGBA")
        logo = Image.open(LOGO_PATH).convert("RGBA")

        position = position or {}
        scale = float(position.get("scale", 0.16))
        x_frac = position.get("x")
        y_frac = position.get("y")

        target_w = int(base.width * scale)
        ratio    = target_w / logo.width
        target_h = int(logo.height * ratio)
        logo     = logo.resize((target_w, target_h), Image.LANCZOS)

        padding = int(base.width * 0.03)

        if x_frac is None or y_frac is None:
            pos_x = base.width  - target_w - padding
            pos_y = base.height - target_h - padding
        else:
            pos_x = int(x_frac * base.width)
            pos_y = int(y_frac * base.height)
            pos_x = max(0, min(pos_x, base.width  - target_w))
            pos_y = max(0, min(pos_y, base.height - target_h))

        base.paste(logo, (pos_x, pos_y), logo)

        out = BytesIO()
        base.convert("RGB").save(out, format="JPEG", quality=92)
        return out.getvalue()

    except Exception as e:
        print(f"Watermark error: {e} — returning original image")
        return base_image_bytes


def build_prompt(platform: str, goal: str, feedback: str) -> str:
    """This generates ONLY the background artwork — no text, no UI mockups,
    no icons. Headlines/highlights/CTA are rendered separately by
    poster_composer.py using Pillow, since AI image models cannot reliably
    render readable text or complex multi-element layouts.

    IMPORTANT: when human feedback is given (e.g. "make it white"), that
    instruction must take priority over the default styling — otherwise the
    hardcoded default color fights with the feedback and the model ignores
    what the human actually asked for."""

    default_style = (
        "with a deep navy blue gradient, subtle glowing abstract technology "
        "shapes and soft light particles, darker toward the bottom half"
    )

    prompt = (
        f"A premium corporate background image {default_style if not feedback else ''}. "
        f"Minimalist, elegant, high-end software company aesthetic. "
        f"The mood reflects: {goal}. "
        f"No text, no words, no letters, no UI screens, no icons, no people. "
        f"Single smooth cohesive background, leaving clear empty space in the "
        f"lower half for text overlay, suitable for a {platform} post."
    )
    if feedback:
        # The human's instruction is now the PRIMARY style directive, not an
        # afterthought appended to a conflicting default.
        prompt += f" Required style: {feedback}. This instruction overrides any other color or mood description."
    return prompt


def build_contact_footer() -> str:
    """Pulls contact info straight from profile.json — same data the
    content_doer caption footer uses — formatted as a single thin line
    for the bottom strip of the poster image itself."""
    from brand.loader import load_brand_profile

    profile = load_brand_profile()
    contact = profile.get("contact", {})
    website = profile.get("website", "").replace("https://", "").replace("http://", "")

    parts = []
    if website:
        parts.append(website)
    if contact.get("email"):
        parts.append(contact["email"])
    if contact.get("phone"):
        parts.append(contact["phone"])

    return "   |   ".join(parts)


async def generate_with_huggingface(prompt: str) -> bytes:
    """Primary generator: Hugging Face Inference API (Stable Diffusion XL).
    Free tier: rate-limited (a few hundred requests/hour), no billing required.
    Get a free token at https://huggingface.co/settings/tokens"""
    from huggingface_hub import InferenceClient

    api_key = os.getenv("HUGGINGFACE_API_KEY", "")
    if not api_key or api_key in ("your-huggingface-key-here", ""):
        raise RuntimeError("HUGGINGFACE_API_KEY not set")

    client = InferenceClient(api_key=api_key)

    # Run the blocking HF call in a thread so it doesn't block the event loop
    import asyncio
    loop = asyncio.get_event_loop()

    def _generate():
        image = client.text_to_image(
            prompt,
            model="black-forest-labs/FLUX.1-schnell",
        )
        buf = BytesIO()
        image.save(buf, format="JPEG", quality=92)
        return buf.getvalue()

    return await loop.run_in_executor(None, _generate)


async def generate_with_pollinations(clean_prompt: str) -> bytes:
    """Fallback generator: Pollinations.ai — free, no key required."""
    url_prompt = clean_prompt.replace(" ", "%20")
    remote_url = f"https://image.pollinations.ai/prompt/{url_prompt}?width=1024&height=1024&nologo=true"
    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.get(remote_url)
        resp.raise_for_status()
        return resp.content


async def run_image_agent(state: dict) -> dict:
    feedback     = state.get("image_feedback", "")
    platform     = state.get("platform", "linkedin")
    goal         = state.get("goal", "")
    poster_copy  = state.get("poster_copy")  # set by content_doer, may be None

    raw_prompt   = build_prompt(platform, goal, feedback)
    clean_prompt = raw_prompt.encode("ascii", errors="ignore").decode("ascii")
    clean_prompt = re.sub(r'\s+', ' ', clean_prompt).strip()

    image_bytes = None

    # Try Hugging Face first (best quality, free tier)
    try:
        image_bytes = await generate_with_huggingface(clean_prompt)
    except Exception as e:
        print("=" * 60)
        print("HUGGING FACE IMAGE ERROR (falling back to Pollinations):")
        print(repr(e))
        traceback.print_exc()
        print("=" * 60)

    # Fallback: Pollinations.ai
    if image_bytes is None:
        try:
            image_bytes = await generate_with_pollinations(clean_prompt)
        except Exception as e:
            print(f"Pollinations fallback also failed: {e}")
            raise

    # Store the RAW background (no poster text, no logo) so the frontend can
    # let the human reposition the logo without regenerating the artwork.
    raw_filename = f"raw_{uuid.uuid4().hex}.jpg"
    raw_path     = os.path.join(STATIC_DIR, raw_filename)
    with open(raw_path, "wb") as f:
        f.write(image_bytes)

    # If we have structured poster copy (headline/sub_headline/highlights/cta),
    # render it onto the background BEFORE applying the logo watermark.
    composed_bytes = image_bytes
    if poster_copy and any(poster_copy.get(k) for k in ("headline", "sub_headline", "highlights", "cta")):
        try:
            from agents.poster_composer import compose_poster
            contact_footer = build_contact_footer()
            composed_bytes = compose_poster(image_bytes, poster_copy, contact_footer=contact_footer)
        except Exception as e:
            print(f"Poster composition error: {e} — using background without text overlay")
            composed_bytes = image_bytes

    # Save the COMPOSED version (poster text included, no logo yet) — this is
    # what the frontend should show during logo repositioning, so the text
    # stays visible while the human drags the logo around.
    composed_filename = f"composed_{uuid.uuid4().hex}.jpg"
    composed_path      = os.path.join(STATIC_DIR, composed_filename)
    with open(composed_path, "wb") as f:
        f.write(composed_bytes)

    logo_position = state.get("logo_position")
    final_bytes   = add_logo_watermark(composed_bytes, logo_position)

    filename  = f"{uuid.uuid4().hex}.jpg"
    file_path = os.path.join(STATIC_DIR, filename)
    with open(file_path, "wb") as f:
        f.write(final_bytes)

    state["raw_image_url"]      = f"http://localhost:8000/static/generated/{raw_filename}"
    state["composed_image_url"] = f"http://localhost:8000/static/generated/{composed_filename}"
    state["image_url"]          = f"http://localhost:8000/static/generated/{filename}"
    state["image_prompt"]       = clean_prompt
    return state