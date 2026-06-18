# LangGraph Workflow — Complete Post Creation Pipeline
# Python 3.10 compatible | LangGraph 1.2.5

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from typing import TypedDict, Optional
import os

from agents.supervisor      import run_supervisor
from agents.planner         import run_planner
from agents.content_doer    import run_content_doer
from agents.image_agent     import run_image_agent
from agents.quality_checker import run_quality_checker


# ── State Definition ──────────────────────────────────────────────────────────

class PostState(TypedDict):
    campaign_id:       str
    post_id:           str
    goal:              str
    platform:          str
    supervisor_output: str
    brief:             str
    content:           str
    image_url:         str
    image_prompt:      str
    image_feedback:    str
    content_feedback:  str
    quality_report:    str
    human_approved:    bool
    iteration:         int


# ── Routing Functions ─────────────────────────────────────────────────────────

def route_image_review(state: PostState) -> str:
    """After human reviews image: approve or regenerate"""
    return "approved" if state.get("human_approved") else "regenerate"


def route_final_approval(state: PostState) -> str:
    """After human final approval: publish or redo content"""
    return "publish" if state.get("human_approved") else "redo_content"


# ── Passthrough node (pause point) ───────────────────────────────────────────

async def human_pause(state: PostState) -> PostState:
    """LangGraph pauses here — frontend resumes via API"""
    return state


async def auto_publish_node(state: PostState) -> PostState:
    """Trigger publisher — actual publish call happens in router"""
    return {**state, "human_approved": True}


# ── Graph Builder ─────────────────────────────────────────────────────────────

def build_graph() -> StateGraph:
    graph = StateGraph(PostState)

    # Register nodes
    graph.add_node("supervisor",           run_supervisor)
    graph.add_node("planner",              run_planner)
    graph.add_node("content_doer",         run_content_doer)
    graph.add_node("image_agent",          run_image_agent)
    graph.add_node("quality_check",        run_quality_checker)
    graph.add_node("human_image_review",   human_pause)   # ← PAUSE 1
    graph.add_node("human_final_approval", human_pause)   # ← PAUSE 2
    graph.add_node("auto_publish",         auto_publish_node)

    # Flow
    graph.set_entry_point("supervisor")
    graph.add_edge("supervisor",    "planner")
    graph.add_edge("planner",       "content_doer")
    graph.add_edge("planner",       "image_agent")
    graph.add_edge("content_doer",  "quality_check")
    graph.add_edge("quality_check", "human_image_review")
    graph.add_edge("image_agent",   "human_image_review")

    # After image review: approve → final approval, reject → regenerate
    graph.add_conditional_edges(
        "human_image_review",
        route_image_review,
        {
            "approved":   "human_final_approval",
            "regenerate": "image_agent"
        }
    )

    # After final approval: publish → done, reject → redo content
    graph.add_conditional_edges(
        "human_final_approval",
        route_final_approval,
        {
            "publish":      "auto_publish",
            "redo_content": "content_doer"
        }
    )

    graph.add_edge("auto_publish", END)

    return graph


# ── Compiled Workflow Factory ─────────────────────────────────────────────────

async def get_workflow():
    """
    Returns compiled LangGraph workflow with PostgreSQL checkpointer.
    PostgreSQL saves state so workflow can PAUSE and RESUME across requests.
    """
    db_url = os.getenv("DATABASE_URL", "").replace(
        "postgresql://", "postgresql+psycopg://"
    )

    checkpointer = AsyncPostgresSaver.from_conn_string(db_url)
    await checkpointer.setup()   # creates langgraph checkpoint tables automatically

    graph = build_graph()

    return graph.compile(
        checkpointer=checkpointer,
        interrupt_before=["human_image_review", "human_final_approval"]
    )