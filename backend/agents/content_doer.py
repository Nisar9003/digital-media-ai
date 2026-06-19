# Content Doer Agent — Claude Sonnet
# Writes caption, hooks, hashtags, CTA — using company brand voice

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage
from brand.loader import get_brand_context_string
import os

llm = ChatAnthropic(
    model="claude-sonnet-4-6",
    api_key=os.getenv("ANTHROPIC_API_KEY", "dummy")
)

def build_system_prompt() -> str:
    brand = get_brand_context_string()
    return f"""You are a social media content writer for this company.

{brand}

Write engaging content that sounds like it genuinely comes from this company —
match their tone, vocabulary, and the style of their past posts.
Respond in JSON format only:
{{
  "hook": "attention-grabbing first line",
  "body": "main caption text",
  "cta": "call to action",
  "hashtags": ["#tag1", "#tag2"]
}}
"""

async def run_content_doer(state: dict) -> dict:
    brief    = state.get("brief", "")
    feedback = state.get("content_feedback", "")

    prompt = f"Brief: {brief}"
    if feedback:
        prompt += f"\n\nRevision needed. Feedback: {feedback}"

    try:
        response = await llm.ainvoke([
            SystemMessage(content=build_system_prompt()),
            HumanMessage(content=prompt)
        ])
        state["content"] = response.content
    except Exception:
        state["content"] = '{"hook": "Draft hook", "body": "Draft content", "cta": "Learn more", "hashtags": ["#webdevelopment", "#KeyDevs"]}'

    return state