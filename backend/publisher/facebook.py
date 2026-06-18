# Facebook Page Publisher (via Meta Graph API)
# Docs: https://developers.facebook.com/docs/pages-api/posts

import httpx
import os

GRAPH_API = "https://graph.facebook.com/v19.0"

async def publish(content: str, image_url: str = None, platform: str = "facebook") -> dict:
    token   = os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN")
    page_id = os.getenv("FACEBOOK_PAGE_ID")

    async with httpx.AsyncClient() as client:
        if image_url:
            # Post with photo
            response = await client.post(
                f"{GRAPH_API}/{page_id}/photos",
                params={
                    "url":          image_url,
                    "message":      content,
                    "access_token": token
                }
            )
        else:
            # Text-only post
            response = await client.post(
                f"{GRAPH_API}/{page_id}/feed",
                params={
                    "message":      content,
                    "access_token": token
                }
            )
        response.raise_for_status()

    return {"platform": "facebook", "post_id": response.json().get("id")}
