"""
Pattern 1B — Memory Agent
--------------------------
New concept: session_id — the agent remembers across turns.

This is the same LlmAgent as Pattern 1A — with one new line.
Reusing the same session_id across calls gives the agent full memory of
everything said before. No re-pasting, no context lost.

A session is a named conversation thread identified by session_id.
The Runner prepends the full message history to every LLM call, so the
LLM sees the entire conversation as context on every turn.

run_agent_multiturn vs run_agent:
  The only difference is passing session_id and reusing an existing session
  instead of creating a new one each call.

Security — PII in Session History:
  The session stores student names, scores, and struggles — this is PII
  (Personally Identifiable Information). Consider using student IDs instead
  of names. In production, use a database-backed SessionService with proper
  access controls rather than the default in-memory store.
"""

import asyncio
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from agent_config import get_model

# --- Agent ---
# Identical to Pattern 1A — the only difference is HOW we call it (session_id reuse)
agent = LlmAgent(
    name="StudentProgressAdvisor",
    model=get_model(),
    instruction="You are an academic advisor at GAT helping faculty track student progress. "
                "Remember everything the faculty tells you about a student in this session — "
                "scores, struggles, improvements, and observations. "
                "Use the full conversation history to give personalised, specific recommendations. "
                "When asked for advice, synthesise everything you know about the student.",
    description="Tracks student progress across a conversation and gives personalised advice.",
)

# ... same Runner setup as Pattern 1A ...
session_service = InMemorySessionService()
runner = Runner(agent=agent, app_name="memory-agent", session_service=session_service)


# --- Entrypoint ---
# session_id is returned on the first call and reused on subsequent calls
# This threads all turns into a single shared conversation history
async def advise(message: str, session_id: str = None) -> tuple:
    if session_id:
        session = await session_service.get_session(
            app_name="memory-agent", user_id="user-1", session_id=session_id
        )
    else:
        session = await session_service.create_session(
            app_name="memory-agent", user_id="user-1"
        )
    result_text = ""
    async for event in runner.run_async(
        user_id="user-1",
        session_id=session.id,
        new_message=types.Content(role="user", parts=[types.Part(text=message)]),
    ):
        if event.is_final_response() and event.content and event.content.parts:
            result_text = event.content.parts[0].text
    return result_text, session.id


if __name__ == "__main__":
    print("Tracking student Priya's progress across 3 interactions...\n")
    print("=" * 60)

    async def main():
        # Turn 1 — new session created, session_id returned
        msg1 = ("Student Priya scored 4/10 on the Arrays assignment. "
                "She made mistakes in pointer arithmetic and off-by-one errors.")
        print(f"Faculty (Turn 1): {msg1}")
        response1, session_id = await advise(msg1)
        print(f"Advisor: {response1}\n")

        # Turn 2 — same session_id: agent has full history from Turn 1
        msg2 = ("Priya just submitted the Linked Lists assignment — scored 7/10. "
                "She implemented insertion and deletion correctly but struggled with reversal.")
        print(f"Faculty (Turn 2): {msg2}")
        response2, session_id = await advise(msg2, session_id=session_id)
        print(f"Advisor: {response2}\n")

        # Turn 3 — agent synthesises everything from Turns 1 and 2
        msg3 = ("We have a 1-on-1 session next week. Based on everything you know "
                "about Priya, what specific topics should I focus on?")
        print(f"Faculty (Turn 3): {msg3}")
        response3, _ = await advise(msg3, session_id=session_id)
        print(f"Advisor: {response3}")

    asyncio.run(main())
