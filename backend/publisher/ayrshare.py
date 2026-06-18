# Ayrshare Publisher — Free tier fallback
# Publishes to multiple platforms with one API call
# Docs: https://docs.ayrshare.com/rest-api/endpoints/post

import httpx
import os

AYRSHARE_API = "https://app.ayrshare.com/api"

async def publish(content: str, image_url: str = None, platform: str = "all") -> dict:
    api_key = os.getenv("AYRSHARE_API_KEY")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type":  "application/json"
    }

    platforms = ["linkedin", "instagram", "facebook", "tiktok"]
    if platform != "all" and platform in platforms:
        platforms = [platform]

    payload = {
        "post":      content,
        "platforms": platforms,
    }
    if image_url:
        payload["mediaUrls"] = [image_url]

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{AYRSHARE_API}/post",
            json=payload,
            headers=headers
        )
        response.raise_for_status()

    return {"platform": "ayrshare", "result": response.json()}
