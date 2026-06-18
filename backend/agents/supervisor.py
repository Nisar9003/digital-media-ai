# Supervisor Agent — Groq (LLaMA 3) free tier
# OpenAI key ki zaroorat nahi

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
import os

# Groq OpenAI-compatible API use karta hai — bilkul free
llm = ChatOpenAI(
    model="llama3-8b-8192",
    api_key=os.getenv("GROQ_API_KEY", "dummy"),
    base_url="https://api.groq.com/openai/v1"
)

SYSTEM_PROMPT = """
You are the Supervisor Agent for a digital media AI system.
Analyze the user's goal and respond in JSON format only:
{
  "platforms": ["linkedin"],
  "tone": "professional",
  "content_type": "announcement",
  "strategy": "brief description"
}
"""

async def run_supervisor(state: dict) -> dict:
    goal     = state.get("goal", "")
    platform = state.get("platform", "linkedin")

    try:
        response = await llm.ainvoke([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=f"Goal: {goal}\nPlatform: {platform}")
        ])
        state["supervisor_output"] = response.content
    except Exception as e:
        # Fallback if Groq key not set yet
        state["supervisor_output"] = f'{{"platforms": ["{platform}"], "tone": "professional", "strategy": "{goal}"}}'

    return state