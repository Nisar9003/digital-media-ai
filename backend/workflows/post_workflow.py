# LangGraph Workflow — Complete Post Creation Pipeline
from langgraph.graph import StateGraph, END
from typing import TypedDict
from agents.supervisor     import run_supervisor
from agents.planner        import run_planner
from agents.content_doer   import run_content_doer
from agents.image_agent    import run_image_agent
from agents.quality_checker import run_quality_checker

class PostState(TypedDict):
    campaign_id:      str
    post_id:          str
    goal:             str
    platform:         str
    supervisor_output: str
    brief:            dict
    content:          str
    image_url:        str
    image_prompt:     str
    image_feedback:   str
    content_feedback: str
    quality_report:   dict
    human_approved:   bool
    iteration:        int

def route_image_review(state: PostState) -> str:
    """After human reviews image: approve or regenerate"""
    return "approved" if state.get("human_approved") else "regenerate"

def route_final_approval(state: PostState) -> str:
    """After human final approval: publish or redo content"""
    return "publish" if state.get("human_approved") else "redo_content"

def build_workflow():
    graph = StateGraph(PostState)

    # Register all nodes
    graph.add_node("supervisor",           run_supervisor)
    graph.add_node("planner",              run_planner)
    graph.add_node("content_doer",         run_content_doer)
    graph.add_node("image_agent",          run_image_agent)
    graph.add_node("quality_check",        run_quality_checker)
    graph.add_node("human_image_review",   lambda s: s)   # PAUSE — frontend resumes
    graph.add_node("human_final_approval", lambda s: s)   # PAUSE — frontend resumes
    graph.add_node("auto_publish",         lambda s: s)   # Publisher router calls this

    # Flow
    graph.set_entry_point("supervisor")
    graph.add_edge("supervisor",   "planner")
    graph.add_edge("planner",      "content_doer")
    graph.add_edge("planner",      "image_agent")
    graph.add_edge("content_doer", "quality_check")
    graph.add_edge("quality_check","human_image_review")
    graph.add_edge("image_agent",  "human_image_review")

    # After image review
    graph.add_conditional_edges(
        "human_image_review",
        route_image_review,
        {"approved": "human_final_approval", "regenerate": "image_agent"}
    )

    # After final approval
    graph.add_conditional_edges(
        "human_final_approval",
        route_final_approval,
        {"publish": "auto_publish", "redo_content": "content_doer"}
    )

    graph.add_edge("auto_publish", END)

    return graph.compile(
        interrupt_before=["human_image_review", "human_final_approval"]
    )
