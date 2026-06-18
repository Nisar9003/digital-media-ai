# Content Doer Agent — Claude Sonnet

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage
import os

llm = ChatAnthropic(
    model="claude-sonnet-4-6",
    api_key=os.getenv("ANTHROPIC_API_KEY", "dummy")
)

SYSTEM_PROMPT = """
You are a social media content writer. Write engaging content in JSON format only:
{
  "hook": "attention-grabbing first line",
  "body": "main caption text",
  "cta": "call to action",
  "hashtags": ["#tag1", "#tag2"]
}
"""

async def run_content_doer(state: dict) -> dict:
    brief    = state.get("brief", "")
    feedback = state.get("content_feedback", "")

    prompt = f"Brief: {brief}"
    if feedback:
        prompt += f"\n\nRevision needed. Feedback: {feedback}"

    try:
        response = await llm.ainvoke([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=prompt)
        ])
        state["content"] = response.content
    except Exception as e:
        state["content"] = '{"hook": "Draft hook", "body": "Draft content", "cta": "Learn more", "hashtags": ["#ai", "#socialmedia"]}'

    return state