# Planner Agent — Claude Sonnet (Anthropic)

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage
import os

llm = ChatAnthropic(
    model="claude-sonnet-4-6",
    api_key=os.getenv("ANTHROPIC_API_KEY", "dummy")
)

SYSTEM_PROMPT = """
You are the Planner Agent. Create a content brief in JSON format only:
{
  "tone": "professional",
  "key_message": "main point",
  "platform_guidelines": "specific tips",
  "image_style": "visual description",
  "hashtag_strategy": "approach"
}
"""

async def run_planner(state: dict) -> dict:
    goal         = state.get("goal", "")
    supervisor   = state.get("supervisor_output", "")

    try:
        response = await llm.ainvoke([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=f"Goal: {goal}\nSupervisor: {supervisor}")
        ])
        state["brief"] = response.content
    except Exception as e:
        state["brief"] = f'{{"tone": "professional", "key_message": "{goal}", "platform_guidelines": "Keep it concise", "image_style": "modern tech", "hashtag_strategy": "5 relevant tags"}}'

    return state