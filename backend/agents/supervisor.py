# Supervisor Agent — GPT-4o
# Analyzes the goal and routes tasks to Planner

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
import os

llm = ChatOpenAI(model="gpt-4o", api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are the Supervisor Agent for a digital media AI system.
Your job is to analyze the user's goal and decide:
1. What platforms to target
2. What tone to use
3. How to delegate to the Planner Agent

Respond in JSON format only.
"""

async def run_supervisor(state: dict) -> dict:
    goal = state["goal"]
    platform = state.get("platform", "linkedin")

    response = await llm.ainvoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"Goal: {goal}\nPlatform: {platform}")
    ])

    # TODO: Parse response and update state
    state["supervisor_output"] = response.content
    return state
