# Image Agent — Fal.ai (Flux) / Pollinations.ai fallback
# Crafts image prompt and generates the graphic

import fal_client
import httpx
import os

async def run_image_agent(state: dict) -> dict:
    brief   = state.get("brief", "")
    feedback = state.get("image_feedback", "")

    # Build image prompt from brief
    image_prompt = f"Professional social media graphic. {brief}"
    if feedback:
        image_prompt += f" Adjustments: {feedback}"

    fal_key = os.getenv("FAL_KEY")

    if fal_key and fal_key != "your-fal-key-here":
        # Best tier: Fal.ai Flux
        result = await fal_client.run_async(
            "fal-ai/flux/schnell",
            arguments={"prompt": image_prompt, "image_size": "square_hd"}
        )
        image_url = result["images"][0]["url"]
    else:
        # Free tier fallback: Pollinations.ai
        encoded = httpx.URL(image_prompt).path
        image_url = f"https://image.pollinations.ai/prompt/{encoded}"

    state["image_url"]    = image_url
    state["image_prompt"] = image_prompt
    return state
