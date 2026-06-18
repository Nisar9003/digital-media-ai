from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from db.connection import get_pool

router = APIRouter()

class CreateCampaignRequest(BaseModel):
    goal:  str
    brief: dict = {}

@router.post("/")
async def create_campaign(req: CreateCampaignRequest):
    pool = get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "INSERT INTO campaigns (goal, brief) VALUES ($1, $2) RETURNING id",
            req.goal, str(req.brief)
        )
    return {"campaign_id": str(row["id"])}

@router.get("/{campaign_id}")
async def get_campaign(campaign_id: str):
    pool = get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM campaigns WHERE id=$1", campaign_id)
    if not row:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return dict(row)

@router.get("/")
async def list_campaigns():
    pool = get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM campaigns ORDER BY created_at DESC")
    return [dict(r) for r in rows]
