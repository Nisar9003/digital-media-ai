# Quality Checker Agent — Groq (LLaMA 3) — free tier speed
# Checks brand tone, platform rules, content quality

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
import os

# Groq uses OpenAI-compatible API
llm = ChatOpenAI(
    model="llama3-8b-8192",
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

SYSTEM_PROMPT = """
You are a Quality Checker for social media content.
Check the content for:
1. Brand tone consistency
2. Platform-specific rules (character limits, hashtag limits)
3. Spelling and grammar
4. Engagement potential

Return JSON: {passed: bool, score: 1-10, issues: [], suggestions: []}
"""

async def run_quality_checker(state: dict) -> dict:
    content  = state.get("content", "")
    platform = state.get("platform", "linkedin")

    response = await llm.ainvoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"Platform: {platform}\nContent: {content}")
    ])

    state["quality_report"] = response.content
    return state
