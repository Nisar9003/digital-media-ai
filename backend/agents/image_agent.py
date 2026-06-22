# Image Agent — Google Gemini (Nano Banana, free tier) is PRIMARY generator
# Pollinations.ai is the fallback if Gemini key is missing or the call fails
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
    """Branded template style: solid/gradient background, simple flat shapes,
    no photo-realism, no text (even Gemini's text rendering isn't reliable
    enough for small logo-less brand templates at this stage)."""
    prompt = (
        f"Flat design branded social media template for {platform}. "
        f"Solid teal and dark navy color background, simple minimal geometric shapes, "
        f"clean corporate tech aesthetic, flat vector illustration style, no text, no words, no letters, "
        f"no photorealism, plenty of empty negative space, modern SaaS branding style. "
        f"Theme: {goal}."
    )
    if feedback:
        prompt += f" Adjust: {feedback}, keep it flat design, no text."
    return prompt


async def generate_with_gemini(prompt: str) -> bytes:
    """Primary generator: Google Gemini (gemini-2.5-flash-image / Nano Banana).
    Free tier: ~500 requests/day via API key from aistudio.google.com/apikey"""
    from google import genai
    from google.genai import types

    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key or api_key in ("your-gemini-key-here", ""):
        raise RuntimeError("GEMINI_API_KEY not set")

    client = genai.Client(api_key=api_key)

    response = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE"],
            image_config=types.ImageConfig(aspect_ratio="1:1"),
        ),
    )

    for part in response.candidates[0].content.parts:
        if getattr(part, "inline_data", None) is not None:
            return part.inline_data.data

    raise RuntimeError("Gemini returned no image data")


async def generate_with_pollinations(clean_prompt: str) -> bytes:
    """Fallback generator: Pollinations.ai — free, no key required."""
    url_prompt = clean_prompt.replace(" ", "%20")
    remote_url = f"https://image.pollinations.ai/prompt/{url_prompt}?width=1024&height=1024&nologo=true"
    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.get(remote_url)
        resp.raise_for_status()
        return resp.content


async def run_image_agent(state: dict) -> dict:
    feedback = state.get("image_feedback", "")
    platform = state.get("platform", "linkedin")
    goal     = state.get("goal", "")

    raw_prompt   = build_prompt(platform, goal, feedback)
    clean_prompt = raw_prompt.encode("ascii", errors="ignore").decode("ascii")
    clean_prompt = re.sub(r'\s+', ' ', clean_prompt).strip()

    image_bytes = None

    # Try Gemini first (best quality, free tier)
    try:
        image_bytes = await generate_with_gemini(clean_prompt)
    except Exception as e:
        print("=" * 60)
        print("GEMINI IMAGE ERROR (falling back to Pollinations):")
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

    # Store the RAW (un-watermarked) image so the frontend can let the
    # human reposition the logo without regenerating the whole image.
    raw_filename = f"raw_{uuid.uuid4().hex}.jpg"
    raw_path     = os.path.join(STATIC_DIR, raw_filename)
    with open(raw_path, "wb") as f:
        f.write(image_bytes)

    logo_position = state.get("logo_position")
    final_bytes   = add_logo_watermark(image_bytes, logo_position)

    filename  = f"{uuid.uuid4().hex}.jpg"
    file_path = os.path.join(STATIC_DIR, filename)
    with open(file_path, "wb") as f:
        f.write(final_bytes)

    state["raw_image_url"] = f"http://localhost:8000/static/generated/{raw_filename}"
    state["image_url"]     = f"http://localhost:8000/static/generated/{filename}"
    state["image_prompt"]  = clean_prompt
    return state