# Image Agent — Pollinations.ai (free, no key needed)
# Fal.ai fallback when FAL_KEY is set

import httpx
import os
import re

async def run_image_agent(state: dict) -> dict:
    brief    = state.get("brief", "")
    feedback = state.get("image_feedback", "")
    platform = state.get("platform", "linkedin")
    goal     = state.get("goal", "")

    # Clean prompt — remove all non-ASCII characters to avoid encoding errors
    raw_prompt = f"Professional social media graphic for {platform}. {goal}."
    if feedback:
        raw_prompt += f" Style adjustment: {feedback}."

    # Strip non-ASCII characters safely
    clean_prompt = raw_prompt.encode("ascii", errors="ignore").decode("ascii")
    # Remove extra spaces
    clean_prompt = re.sub(r'\s+', ' ', clean_prompt).strip()
    # URL-encode for Pollinations
    url_prompt = clean_prompt.replace(" ", "%20")

    fal_key = os.getenv("FAL_KEY", "")

    if fal_key and fal_key not in ("your-fal-key-here", ""):
        # Best tier: Fal.ai Flux
        try:
            import fal_client
            result = await fal_client.run_async(
                "fal-ai/flux/schnell",
                arguments={
                    "prompt":     clean_prompt,
                    "image_size": "square_hd"
                }
            )
            image_url = result["images"][0]["url"]
        except Exception as e:
            print(f"Fal.ai error: {e} — falling back to Pollinations")
            image_url = f"https://image.pollinations.ai/prompt/{url_prompt}?width=1024&height=1024&nologo=true"
    else:
        # Free tier: Pollinations.ai — no API key needed
        image_url = f"https://image.pollinations.ai/prompt/{url_prompt}?width=1024&height=1024&nologo=true"

    state["image_url"]    = image_url
    state["image_prompt"] = clean_prompt
    return state