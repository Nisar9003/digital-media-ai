# LangGraph Workflow — Complete Post Creation Pipeline
# Python 3.10 compatible

from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional
import asyncpg
import os

from agents.supervisor       import run_supervisor
from agents.planner          import run_planner
from agents.content_doer     import run_content_doer
from agents.image_agent      import run_image_agent
from agents.quality_checker  import run_quality_checker


# ── State ─────────────────────────────────────────────────────────────────────

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


# ── Routing ───────────────────────────────────────────────────────────────────

def route_image_review(state: PostState) -> str:
    return "approved" if state.get("human_approved") else "regenerate"

def route_final_approval(state: PostState) -> str:
    return "publish" if state.get("human_approved") else "redo_content"


# ── Pause nodes (LangGraph interrupts here) ───────────────────────────────────

async def human_pause(state: PostState) -> PostState:
    return state

async def auto_publish_node(state: PostState) -> PostState:
    return {**state, "human_approved": True}


# ── Build graph (no checkpointer — state stored in PostgreSQL posts table) ────

def build_workflow():
    graph = StateGraph(PostState)

    graph.add_node("supervisor",           run_supervisor)
    graph.add_node("planner",              run_planner)
    graph.add_node("content_doer",         run_content_doer)
    graph.add_node("image_agent",          run_image_agent)
    graph.add_node("quality_check",        run_quality_checker)
    graph.add_node("human_image_review",   human_pause)
    graph.add_node("human_final_approval", human_pause)
    graph.add_node("auto_publish",         auto_publish_node)

    graph.set_entry_point("supervisor")
    graph.add_edge("supervisor",    "planner")
    graph.add_edge("planner",       "content_doer")
    graph.add_edge("planner",       "image_agent")
    graph.add_edge("content_doer",  "quality_check")
    graph.add_edge("quality_check", "human_image_review")
    graph.add_edge("image_agent",   "human_image_review")

    graph.add_conditional_edges(
        "human_image_review",
        route_image_review,
        {"approved": "human_final_approval", "regenerate": "image_agent"}
    )

    graph.add_conditional_edges(
        "human_final_approval",
        route_final_approval,
        {"publish": "auto_publish", "redo_content": "content_doer"}
    )

    graph.add_edge("auto_publish", END)

    # Compile with interrupt points (no postgres checkpointer needed for now)
    return graph.compile(
        interrupt_before=["human_image_review", "human_final_approval"]
    )