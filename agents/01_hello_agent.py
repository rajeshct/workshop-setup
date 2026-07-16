"""
Pattern 1A — Hello Agent
-------------------------
New concept: LlmAgent — the baseline single-turn agent.

An LlmAgent is the core building block of every ADK application. It holds:
  • name        — unique identifier for this agent
  • model       — which LLM to use (from .env — Gemini or Ollama)
  • instruction — the system prompt: who the agent is and what it does

The Runner manages the turn loop automatically:
  send message → LLM reasons → if tool call, execute it → feed result back → repeat → final answer
You never write this loop yourself.

Security — API Key Safety:
  Never hardcode API keys in code. Store in .env, add .env to .gitignore,
  and set spending limits on your API key to prevent unexpected charges.
"""

import asyncio
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from google.adk.agents import LlmAgent

from agent_config import get_model, build_runner, run_agent

# --- Agent ---
# instruction = system prompt: defines the agent's role, scope, and behaviour
agent = LlmAgent(
    name="HelloAgent",
    model=get_model(),                  # gemini-2.0-flash or ollama/llama3.2 from .env
    instruction="You are a helpful assistant for engineering students and faculty. "
                "Answer questions clearly and concisely.",
    description="A simple single-turn agent — the baseline for all other patterns.",
)

# build_runner creates: Runner + InMemorySessionService
runner, session_service = build_runner(agent, app_name="hello-agent")


# --- Entrypoint ---
async def ask(question: str) -> str:
    return await run_agent(runner, session_service, question, app_name="hello-agent")


if __name__ == "__main__":
    question = "What are good learning outcomes for a Data Structures and Algorithms course?"
    print(f"Question: {question}\n")
    print("=" * 60)
    print(asyncio.run(ask(question)))
