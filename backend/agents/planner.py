# Planner Agent — Claude Sonnet
# Creates a detailed content brief using company brand context
# DEBUG MODE: prints real error instead of silently falling back

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage
from brand.loader import get_brand_context_string
import os
import traceback

llm = ChatAnthropic(
    model="claude-sonnet-4-6",
    api_key=os.getenv("ANTHROPIC_API_KEY", "dummy")
)

def build_system_prompt() -> str:
    brand = get_brand_context_string()
    return f"""You are the Planner Agent for a company's social media content system.

{brand}

Using the above company context, create a content brief in JSON format only:
{{
  "tone": "professional",
  "key_message": "main point, aligned with company identity",
  "platform_guidelines": "specific tips",
  "image_style": "visual description matching brand colors/style",
  "hashtag_strategy": "approach"
}}
"""

async def run_planner(state: dict) -> dict:
    goal       = state.get("goal", "")
    supervisor = state.get("supervisor_output", "")

    try:
        response = await llm.ainvoke([
            SystemMessage(content=build_system_prompt()),
            HumanMessage(content=f"Goal: {goal}\nSupervisor: {supervisor}")
        ])
        state["brief"] = response.content
    except Exception as e:
        print("=" * 60)
        print("PLANNER ERROR (real cause):")
        print(repr(e))
        traceback.print_exc()
        print("=" * 60)
        state["brief"] = f'{{"tone": "professional", "key_message": "{goal}", "platform_guidelines": "Keep it concise", "image_style": "modern tech, teal accents", "hashtag_strategy": "5 relevant tags"}}'

    return state