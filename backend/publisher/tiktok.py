# TikTok Publisher (via TikTok Content Posting API)
# Docs: https://developers.tiktok.com/doc/content-posting-api-get-started

import httpx
import os

TIKTOK_API = "https://open.tiktokapis.com/v2"

async def publish(content: str, image_url: str = None, platform: str = "tiktok") -> dict:
    token   = os.getenv("TIKTOK_ACCESS_TOKEN")
    open_id = os.getenv("TIKTOK_OPEN_ID")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type":  "application/json; charset=UTF-8"
    }

    # TikTok supports photo posts (carousel) via Content Posting API
    payload = {
        "post_info": {
            "title":         content[:150],   # TikTok title limit
            "privacy_level": "PUBLIC_TO_EVERYONE",
            "disable_duet":  False,
            "disable_comment": False,
            "disable_stitch": False,
        },
        "source_info": {
            "source":      "PULL_FROM_URL",
            "photo_cover_index": 0,
            "photo_images": [image_url] if image_url else []
        },
        "post_mode": "DIRECT_POST",
        "media_type": "PHOTO"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{TIKTOK_API}/post/publish/content/init/",
            json=payload,
            headers=headers
        )
        response.raise_for_status()

    return {"platform": "tiktok", "publish_id": response.json().get("data", {}).get("publish_id")}
