# Planner Agent — Claude Sonnet
# Creates a detailed content brief from the supervisor's output

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage
import os

llm = ChatAnthropic(model="claude-sonnet-4-6", api_key=os.getenv("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """
You are the Planner Agent. You receive a goal and create a detailed content brief.
The brief must include:
- Tone of voice
- Key message
- Platform-specific guidelines (LinkedIn: professional, TikTok: snappy/fun, Instagram: visual-first, Facebook: community-focused)
- Image style description
- Hashtag strategy

Respond in JSON format only.
"""

async def run_planner(state: dict) -> dict:
    supervisor_out = state.get("supervisor_output", "")
    goal = state["goal"]

    response = await llm.ainvoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"Goal: {goal}\nSupervisor analysis: {supervisor_out}")
    ])

    state["brief"] = response.content
    return state
