# Content Doer Agent — Claude 3.5 Sonnet
# Writes caption, hooks, hashtags, and CTA based on the brief

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage
import os

llm = ChatAnthropic(model="claude-sonnet-4-6", api_key=os.getenv("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """
You are a social media content writer. Based on the provided brief, write:
1. A strong hook (first line that stops the scroll)
2. Main caption body
3. Call-to-action
4. 5-10 relevant hashtags

Adapt tone strictly to the platform specified in the brief.
Respond in JSON format: {hook, body, cta, hashtags}
"""

async def run_content_doer(state: dict) -> dict:
    brief = state.get("brief", "")
    feedback = state.get("content_feedback", "")

    prompt = f"Brief: {brief}"
    if feedback:
        prompt += f"\n\nPrevious content was rejected. Feedback: {feedback}\nPlease revise."

    response = await llm.ainvoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=prompt)
    ])

    state["content"] = response.content
    return state
