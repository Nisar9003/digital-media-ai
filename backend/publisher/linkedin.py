# LinkedIn Publisher
# Docs: https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/posts-api

import httpx
import os

LINKEDIN_API = "https://api.linkedin.com/v2"

async def publish(content: str, image_url: str = None, platform: str = "linkedin") -> dict:
    token   = os.getenv("LINKEDIN_ACCESS_TOKEN")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type":  "application/json",
        "X-Restli-Protocol-Version": "2.0.0"
    }

    # Get your own profile URN first
    async with httpx.AsyncClient() as client:
        me = await client.get(f"{LINKEDIN_API}/userinfo", headers=headers)
        author_urn = f"urn:li:person:{me.json()['sub']}"

        payload = {
            "author":          author_urn,
            "lifecycleState":  "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary":  {"text": content},
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
        }

        response = await client.post(
            f"{LINKEDIN_API}/ugcPosts",
            json=payload,
            headers=headers
        )
        response.raise_for_status()

    return {"platform": "linkedin", "post_id": response.headers.get("x-restli-id")}
