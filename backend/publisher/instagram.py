# Instagram Publisher (via Meta Graph API)
# Docs: https://developers.facebook.com/docs/instagram-api/guides/content-publishing

import httpx
import os

GRAPH_API = "https://graph.facebook.com/v19.0"

async def publish(content: str, image_url: str = None, platform: str = "instagram") -> dict:
    token      = os.getenv("INSTAGRAM_ACCESS_TOKEN")
    account_id = os.getenv("INSTAGRAM_ACCOUNT_ID")

    async with httpx.AsyncClient() as client:
        # Step 1: Create media container
        container_res = await client.post(
            f"{GRAPH_API}/{account_id}/media",
            params={
                "image_url":   image_url,
                "caption":     content,
                "access_token": token
            }
        )
        container_res.raise_for_status()
        container_id = container_res.json()["id"]

        # Step 2: Publish the container
        publish_res = await client.post(
            f"{GRAPH_API}/{account_id}/media_publish",
            params={"creation_id": container_id, "access_token": token}
        )
        publish_res.raise_for_status()

    return {"platform": "instagram", "post_id": publish_res.json()["id"]}
