from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from db.connection import get_pool

router = APIRouter()


class CreateCampaignRequest(BaseModel):
    goal:  str
    brief: str = ""


@router.post("/")
async def create_campaign(req: CreateCampaignRequest):
    pool = get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "INSERT INTO campaigns (goal, brief) VALUES ($1, $2) RETURNING id, goal, status, created_at",
            req.goal, req.brief
        )
    return dict(row)


@router.get("/")
async def list_campaigns():
    pool = get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM campaigns ORDER BY created_at DESC")
    return [dict(r) for r in rows]


@router.get("/{campaign_id}")
async def get_campaign(campaign_id: str):
    pool = get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM campaigns WHERE id=$1", campaign_id)
    if not row:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return dict(row)


@router.delete("/{campaign_id}")
async def delete_campaign(campaign_id: str):
    pool = get_pool()
    async with pool.acquire() as conn:
        result = await conn.execute("DELETE FROM campaigns WHERE id=$1", campaign_id)
    if result == "DELETE 0":
        raise HTTPException(status_code=404, detail="Campaign not found")
    return {"status": "deleted"}