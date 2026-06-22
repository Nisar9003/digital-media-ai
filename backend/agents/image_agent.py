# Image Agent — Pollinations.ai (free) / Fal.ai fallback
# Generates clean branded-template style graphics (solid backgrounds, simple shapes)
# Logo position is now controlled by the human via logo_position in state (set from frontend)

import httpx
import os
import re
import uuid
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
    x/y are fractional coordinates of the TOP-LEFT corner of the logo
    relative to image width/height. Defaults to bottom-right if not given.
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
            # Default fallback: bottom-right
            pos_x = base.width  - target_w - padding
            pos_y = base.height - target_h - padding
        else:
            pos_x = int(x_frac * base.width)
            pos_y = int(y_frac * base.height)
            # Clamp so logo stays fully inside the image
            pos_x = max(0, min(pos_x, base.width  - target_w))
            pos_y = max(0, min(pos_y, base.height - target_h))

        base.paste(logo, (pos_x, pos_y), logo)

        out = BytesIO()
        base.convert("RGB").save(out, format="JPEG", quality=92)
        return out.getvalue()

    except Exception as e:
        print(f"Watermark error: {e} — returning original image")
        return base_image_bytes


async def run_image_agent(state: dict) -> dict:
    feedback = state.get("image_feedback", "")
    platform = state.get("platform", "linkedin")
    goal     = state.get("goal", "")

    # Branded template style: solid/gradient background, simple flat shapes,
    # no photo-realism, no text (AI can't render readable text reliably).
    raw_prompt = (
        f"Flat design branded social media template for {platform}. "
        f"Solid teal and dark navy color background, simple minimal geometric shapes, "
        f"clean corporate tech aesthetic, flat vector illustration style, no text, no words, no letters, "
        f"no photorealism, plenty of empty negative space, modern SaaS branding style. "
        f"Theme: {goal}."
    )
    if feedback:
        raw_prompt += f" Adjust: {feedback}, keep it flat design, no text."

    clean_prompt = raw_prompt.encode("ascii", errors="ignore").decode("ascii")
    clean_prompt = re.sub(r'\s+', ' ', clean_prompt).strip()
    url_prompt   = clean_prompt.replace(" ", "%20")

    fal_key = os.getenv("FAL_KEY", "")
    image_bytes = None

    try:
        if fal_key and fal_key not in ("your-fal-key-here", ""):
            import fal_client
            result = await fal_client.run_async(
                "fal-ai/flux/schnell",
                arguments={"prompt": clean_prompt, "image_size": "square_hd"}
            )
            remote_url = result["images"][0]["url"]
        else:
            remote_url = f"https://image.pollinations.ai/prompt/{url_prompt}?width=1024&height=1024&nologo=true"

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.get(remote_url)
            resp.raise_for_status()
            image_bytes = resp.content

    except Exception as e:
        print(f"Image generation error: {e} — falling back to Pollinations")
        remote_url = f"https://image.pollinations.ai/prompt/{url_prompt}?width=1024&height=1024&nologo=true"
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.get(remote_url)
            image_bytes = resp.content

    # Store the RAW (un-watermarked) image too, so the frontend can let the
    # human reposition the logo without regenerating the whole image.
    raw_filename  = f"raw_{uuid.uuid4().hex}.jpg"
    raw_path      = os.path.join(STATIC_DIR, raw_filename)
    with open(raw_path, "wb") as f:
        f.write(image_bytes)

    # Apply logo at human-chosen position (or default bottom-right if none given yet)
    logo_position = state.get("logo_position")  # {"x":.., "y":.., "scale":..} or None
    final_bytes   = add_logo_watermark(image_bytes, logo_position)

    filename  = f"{uuid.uuid4().hex}.jpg"
    file_path = os.path.join(STATIC_DIR, filename)
    with open(file_path, "wb") as f:
        f.write(final_bytes)

    state["raw_image_url"] = f"http://localhost:8000/static/generated/{raw_filename}"
    state["image_url"]     = f"http://localhost:8000/static/generated/{filename}"
    state["image_prompt"]  = clean_prompt
    return state