from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from db.connection import get_pool
from publisher import linkedin, instagram, facebook, tiktok, ayrshare

router = APIRouter()

class PublishRequest(BaseModel):
    post_id:  str
    platform: str

PUBLISHERS = {
    "linkedin":  linkedin.publish,
    "instagram": instagram.publish,
    "facebook":  facebook.publish,
    "tiktok":    tiktok.publish,
}

@router.post("/")
async def publish_post(req: PublishRequest):
    pool = get_pool()
    async with pool.acquire() as conn:
        post = await conn.fetchrow("SELECT * FROM posts WHERE id=$1", req.post_id)

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    publisher_fn = PUBLISHERS.get(req.platform, ayrshare.publish)

    result = await publisher_fn(
        content=post["content"],
        image_url=post["image_url"],
        platform=req.platform
    )

    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE posts SET status='published', published_at=NOW() WHERE id=$1",
            req.post_id
        )

    return {"status": "published", "result": result}
