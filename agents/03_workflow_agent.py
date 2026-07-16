"""
Pattern 3 — Workflow Agent: Sequential Pipeline (without Opik)
---------------------------------------------------------------
New concept: SequentialAgent — chain agents in a pipeline.

SequentialAgent runs child agents one after another. The output of each
agent is automatically passed as input to the next via session state.
No manual copy-pasting between steps, no human in the loop.

How output flows between steps:
  Each agent saves its response to session.state under its output_key.
  The next agent's prompt is automatically enriched with that value.
  ConceptAnalyser output → ExamGenerator input, automatically.

Instruction design for pipelines:
  First agent:  "Be concise — this output feeds directly into the next step."
  Second agent: "Given the analysis above, generate a complete exam paper."

Security — Instruction Hardening:
  Be explicit in every agent's instruction about what it should and should
  not do. Vague instructions produce off-topic or inappropriate content.
  Define the exact output format, scope, and content restrictions.
"""

import asyncio
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from google.adk.agents import SequentialAgent, LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from agent_config import get_model


# --- Agents ---

concept_analyser = LlmAgent(
    name="ConceptAnalyser",
    model=get_model(),
    instruction="""You are a senior engineering professor and curriculum expert.
    Given a topic, identify:
    - 3-4 core concepts students must understand
    - Common misconceptions or tricky areas
    - What easy, medium, and hard questions would test for this topic
    Be concise — this output feeds directly into the exam generator.""",
    description="Analyses a topic and identifies key concepts and difficulty levels.",
)

exam_generator = LlmAgent(
    name="ExamGenerator",
    model=get_model(),
    instruction="""You are an experienced engineering exam setter.
    Given a concept analysis of a topic, generate a complete exam paper with:

    ## Multiple Choice Questions (5 questions)
    - 2 easy, 2 medium, 1 hard
    - 4 options each (A/B/C/D)
    - Mark the correct answer

    ## Descriptive Questions (2 questions)
    - 1 medium (5 marks): tests understanding
    - 1 hard (10 marks): tests application/analysis

    ## Answer Key
    - MCQ answers with brief explanation
    - Descriptive answer guidelines (key points to award marks)

    Format it cleanly — ready to print and distribute.""",
    description="Generates a complete exam paper with answer keys from concept analysis.",
)

# SequentialAgent: ConceptAnalyser output automatically becomes ExamGenerator input
pipeline = SequentialAgent(
    name="ExamPaperPipeline",
    sub_agents=[concept_analyser, exam_generator],
)

session_service = InMemorySessionService()
runner = Runner(agent=pipeline, app_name="workflow-agent", session_service=session_service)


async def generate_exam(topic: str) -> str:
    session = await session_service.create_session(app_name="workflow-agent", user_id="user-1")
    result_text = ""
    async for event in runner.run_async(
        user_id="user-1",
        session_id=session.id,
        new_message=types.Content(role="user", parts=[types.Part(text=topic)]),
    ):
        if event.is_final_response() and event.content and event.content.parts:
            result_text = event.content.parts[0].text
    return result_text


if __name__ == "__main__":
    topic = "Binary Search Trees — insertion, deletion, and traversal algorithms"
    print(f"Topic: {topic}\n")
    print("Try doing this with an AI assistant — you would need to manually copy the")
    print("concept analysis and paste it back to get the exam questions.")
    print("This agent does both steps automatically.\n")
    print("=" * 60)
    print(asyncio.run(generate_exam(topic)))
