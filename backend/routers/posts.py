from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from uuid import uuid4
from workflows.post_workflow import get_workflow
from db.connection import get_pool

router = APIRouter()


class CreatePostRequest(BaseModel):
    goal:        str
    platform:    str
    campaign_id: str


class ImageFeedbackRequest(BaseModel):
    feedback: str
    approved: bool


class FinalApprovalRequest(BaseModel):
    approved:         bool
    content_feedback: str = ""


@router.post("/create")
async def create_post(req: CreatePostRequest):
    """Start a new post workflow"""
    run_id   = str(uuid4())
    workflow = await get_workflow()

    initial_state = {
        "goal":        req.goal,
        "platform":    req.platform,
        "campaign_id": req.campaign_id,
        "post_id":     run_id,
        "iteration":   1,
        "human_approved": False,
        "image_feedback":   "",
        "content_feedback": "",
    }

    await workflow.ainvoke(
        initial_state,
        config={"configurable": {"thread_id": run_id}}
    )

    pool = get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO posts (id, campaign_id, platform, status) VALUES ($1, $2, $3, $4)",
            run_id, req.campaign_id, req.platform, "image_review"
        )

    return {"run_id": run_id, "status": "awaiting_image_review"}


@router.post("/{post_id}/image-feedback")
async def submit_image_feedback(post_id: str, req: ImageFeedbackRequest):
    """Resume workflow after human reviews the image"""
    workflow = await get_workflow()
    config   = {"configurable": {"thread_id": post_id}}

    await workflow.aupdate_state(
        config,
        {"image_feedback": req.feedback, "human_approved": req.approved}
    )
    await workflow.ainvoke(None, config=config)

    next_status = "final_review" if req.approved else "image_regenerating"
    pool = get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE posts SET status=$1, feedback=$2 WHERE id=$3",
            next_status, req.feedback, post_id
        )

    return {"status": next_status}


@router.post("/{post_id}/approve")
async def final_approve(post_id: str, req: FinalApprovalRequest):
    """Final human approval before publishing"""
    workflow = await get_workflow()
    config   = {"configurable": {"thread_id": post_id}}

    await workflow.aupdate_state(
        config,
        {"human_approved": req.approved, "content_feedback": req.content_feedback}
    )
    await workflow.ainvoke(None, config=config)

    next_status = "publishing" if req.approved else "content_revision"
    pool = get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE posts SET status=$1 WHERE id=$2",
            next_status, post_id
        )

    return {"status": next_status}


@router.get("/{post_id}")
async def get_post(post_id: str):
    pool = get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM posts WHERE id=$1", post_id)
    if not row:
        raise HTTPException(status_code=404, detail="Post not found")
    return dict(row)


@router.get("/")
async def list_posts(status: str = None):
    pool = get_pool()
    async with pool.acquire() as conn:
        if status:
            rows = await conn.fetch(
                "SELECT * FROM posts WHERE status=$1 ORDER BY created_at DESC", status
            )
        else:
            rows = await conn.fetch("SELECT * FROM posts ORDER BY created_at DESC")
    return [dict(r) for r in rows]