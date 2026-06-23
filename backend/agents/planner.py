# Planner Agent — Groq (LLaMA 3.3, free tier)
# Creates a detailed content brief using company brand context

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from brand.loader import get_brand_context_string
import os
import traceback

# Groq uses OpenAI-compatible API — completely free, no billing required
llm = ChatOpenAI(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY", "dummy"),
    base_url="https://api.groq.com/openai/v1"
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