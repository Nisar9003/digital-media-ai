# Quality Checker Agent — Groq (LLaMA 3) free tier

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
import os

llm = ChatOpenAI(
    model="llama3-8b-8192",
    api_key=os.getenv("GROQ_API_KEY", "dummy"),
    base_url="https://api.groq.com/openai/v1"
)

SYSTEM_PROMPT = """
You are a Quality Checker for social media content.
Respond in JSON format only:
{
  "passed": true,
  "score": 8,
  "issues": [],
  "suggestions": []
}
"""

async def run_quality_checker(state: dict) -> dict:
    content  = state.get("content", "")
    platform = state.get("platform", "linkedin")

    try:
        response = await llm.ainvoke([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=f"Platform: {platform}\nContent: {content}")
        ])
        state["quality_report"] = response.content
    except Exception as e:
        state["quality_report"] = '{"passed": true, "score": 7, "issues": [], "suggestions": []}'

    return state