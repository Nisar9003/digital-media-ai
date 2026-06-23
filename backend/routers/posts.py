from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from uuid import uuid4
from db.connection import get_pool

router = APIRouter()

_workflow_states: dict = {}


class CreatePostRequest(BaseModel):
    goal:        str
    platform:    str
    campaign_id: str = "default"


class ImageFeedbackRequest(BaseModel):
    feedback: str
    approved: bool


class LogoPositionRequest(BaseModel):
    x:     float  # 0.0 - 1.0, fractional X of top-left corner
    y:     float  # 0.0 - 1.0, fractional Y of top-left corner
    scale: float = 0.16  # logo width as fraction of image width


class FinalApprovalRequest(BaseModel):
    approved:         bool
    content_feedback: str = ""


# ── POST /api/posts/create ────────────────────────────────────────────────────

@router.post("/create")
async def create_post(req: CreatePostRequest):
    from agents.supervisor      import run_supervisor
    from agents.planner         import run_planner
    from agents.content_doer    import run_content_doer
    from agents.image_agent     import run_image_agent
    from agents.quality_checker import run_quality_checker

    post_id = str(uuid4())

    state = {
        "goal":             req.goal,
        "platform":         req.platform,
        "campaign_id":      req.campaign_id,
        "post_id":          post_id,
        "iteration":        1,
        "human_approved":   False,
        "image_feedback":   "",
        "content_feedback": "",
        "supervisor_output": "",
        "brief":            "",
        "content":          "",
        "image_url":        "",
        "raw_image_url":    "",
        "composed_image_url": "",
        "image_prompt":     "",
        "quality_report":   "",
        "logo_position":    None,
        "poster_copy":      None,
    }

    state = await run_supervisor(state)
    state = await run_planner(state)
    state = await run_content_doer(state)
    state = await run_image_agent(state)
    state = await run_quality_checker(state)

    _workflow_states[post_id] = state

    pool = get_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO campaigns (id, goal, status)
            VALUES ('00000000-0000-0000-0000-000000000001', 'Default Campaign', 'active')
            ON CONFLICT (id) DO NOTHING
        """)
        await conn.execute("""
            INSERT INTO posts (id, campaign_id, platform, content, image_url, status)
            VALUES ($1, '00000000-0000-0000-0000-000000000001', $2, $3, $4, 'image_review')
        """, post_id, req.platform, state.get("content", ""), state.get("image_url", ""))

    return {
        "post_id":            post_id,
        "status":             "awaiting_image_review",
        "content":            state.get("content"),
        "image_url":          state.get("image_url"),
        "raw_image_url":      state.get("raw_image_url"),
        "composed_image_url": state.get("composed_image_url"),
        "quality_report":     state.get("quality_report"),
    }


# ── POST /api/posts/{post_id}/logo-position ───────────────────────────────────
# Re-applies the logo at a human-chosen position WITHOUT regenerating the image

@router.post("/{post_id}/logo-position")
async def set_logo_position(post_id: str, req: LogoPositionRequest):
    from agents.image_agent import add_logo_watermark
    import httpx, uuid, os

    state = _workflow_states.get(post_id)
    if not state:
        raise HTTPException(status_code=404, detail="Workflow state not found. Please create post again.")

    # Use the COMPOSED image (poster text included, no logo) as the base for
    # logo placement — this way the text stays visible while positioning.
    base_url = state.get("composed_image_url") or state.get("raw_image_url")
    if not base_url:
        raise HTTPException(status_code=400, detail="No base image available to reposition logo on.")

    # Download the composed (text included, logo-free) image
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(base_url)
        resp.raise_for_status()
        raw_bytes = resp.content

    position = {"x": req.x, "y": req.y, "scale": req.scale}
    final_bytes = add_logo_watermark(raw_bytes, position)

    STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "generated")
    filename   = f"{uuid.uuid4().hex}.jpg"
    file_path  = os.path.join(STATIC_DIR, filename)
    with open(file_path, "wb") as f:
        f.write(final_bytes)

    new_image_url = f"http://localhost:8000/static/generated/{filename}"
    state["image_url"]     = new_image_url
    state["logo_position"] = position
    _workflow_states[post_id] = state

    pool = get_pool()
    async with pool.acquire() as conn:
        await conn.execute("UPDATE posts SET image_url=$1 WHERE id=$2", new_image_url, post_id)

    return {"image_url": new_image_url}


# ── POST /api/posts/{post_id}/image-feedback ──────────────────────────────────

@router.post("/{post_id}/image-feedback")
async def submit_image_feedback(post_id: str, req: ImageFeedbackRequest):
    from agents.image_agent import run_image_agent

    state = _workflow_states.get(post_id)
    if not state:
        raise HTTPException(status_code=404, detail="Workflow state not found. Please create post again.")

    state["image_feedback"] = req.feedback
    state["human_approved"] = req.approved

    if not req.approved:
        state["iteration"] += 1
        state = await run_image_agent(state)
        _workflow_states[post_id] = state

        pool = get_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                "UPDATE posts SET image_url=$1, status='image_review' WHERE id=$2",
                state.get("image_url"), post_id
            )

        return {
            "status":             "image_regenerated",
            "image_url":          state.get("image_url"),
            "raw_image_url":      state.get("raw_image_url"),
            "composed_image_url": state.get("composed_image_url"),
            "iteration":          state.get("iteration"),
        }

    pool = get_pool()
    async with pool.acquire() as conn:
        await conn.execute("UPDATE posts SET status='final_review' WHERE id=$1", post_id)

    return {"status": "final_review", "image_url": state.get("image_url")}


# ── POST /api/posts/{post_id}/approve ────────────────────────────────────────

@router.post("/{post_id}/approve")
async def final_approve(post_id: str, req: FinalApprovalRequest):
    from agents.content_doer import run_content_doer

    state = _workflow_states.get(post_id)
    if not state:
        raise HTTPException(status_code=404, detail="Workflow state not found.")

    if not req.approved:
        state["content_feedback"] = req.content_feedback
        state["human_approved"]   = False
        state = await run_content_doer(state)
        _workflow_states[post_id] = state

        pool = get_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                "UPDATE posts SET content=$1, status='content_revision' WHERE id=$2",
                state.get("content"), post_id
            )

        return {"status": "content_revised", "content": state.get("content")}

    pool = get_pool()
    async with pool.acquire() as conn:
        await conn.execute("UPDATE posts SET status='approved' WHERE id=$1", post_id)

    _workflow_states.pop(post_id, None)
    return {"status": "approved", "message": "Post approved and ready to publish"}


# ── GET /api/posts/ ───────────────────────────────────────────────────────────

@router.get("/")
async def list_posts(status: str = None):
    pool = get_pool()
    async with pool.acquire() as conn:
        if status:
            rows = await conn.fetch("SELECT * FROM posts WHERE status=$1 ORDER BY created_at DESC", status)
        else:
            rows = await conn.fetch("SELECT * FROM posts ORDER BY created_at DESC")
    return [dict(r) for r in rows]


# ── GET /api/posts/{post_id} ──────────────────────────────────────────────────

@router.get("/{post_id}")
async def get_post(post_id: str):
    pool = get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM posts WHERE id=$1", post_id)
    if not row:
        raise HTTPException(status_code=404, detail="Post not found")
    result = dict(row)
    state = _workflow_states.get(post_id)
    if state:
        result["raw_image_url"]      = state.get("raw_image_url")
        result["composed_image_url"] = state.get("composed_image_url")
    return result


# ── DELETE /api/posts/{post_id} ───────────────────────────────────────────────

@router.delete("/{post_id}")
async def delete_post(post_id: str):
    pool = get_pool()
    async with pool.acquire() as conn:
        result = await conn.execute("DELETE FROM posts WHERE id=$1", post_id)
    if result == "DELETE 0":
        raise HTTPException(status_code=404, detail="Post not found")
    _workflow_states.pop(post_id, None)
    return {"status": "deleted"}