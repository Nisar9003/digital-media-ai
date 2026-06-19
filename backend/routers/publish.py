from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from db.connection import get_pool

router = APIRouter()

SUPPORTED_PLATFORMS = ["linkedin", "instagram", "facebook", "tiktok"]


class PublishRequest(BaseModel):
    post_id:  str
    platform: str


@router.post("/")
async def publish_post(req: PublishRequest):
    """Publish an approved post to the specified platform"""
    pool = get_pool()
    async with pool.acquire() as conn:
        post = await conn.fetchrow("SELECT * FROM posts WHERE id=$1", req.post_id)

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if post["status"] not in ("approved", "publishing"):
        raise HTTPException(
            status_code=400,
            detail=f"Post must be approved before publishing. Current status: {post['status']}"
        )

    platform = req.platform.lower()

    try:
        if platform == "linkedin":
            from publisher.linkedin import publish
        elif platform == "instagram":
            from publisher.instagram import publish
        elif platform == "facebook":
            from publisher.facebook import publish
        elif platform == "tiktok":
            from publisher.tiktok import publish
        else:
            from publisher.ayrshare import publish

        result = await publish(
            content=post["content"] or "",
            image_url=post["image_url"] or "",
            platform=platform
        )

        async with pool.acquire() as conn:
            await conn.execute(
                "UPDATE posts SET status='published', published_at=NOW() WHERE id=$1",
                req.post_id
            )

        return {"status": "published", "platform": platform, "result": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Publishing failed: {str(e)}")


@router.get("/platforms")
async def list_platforms():
    """List all supported publishing platforms"""
    return {"platforms": SUPPORTED_PLATFORMS}