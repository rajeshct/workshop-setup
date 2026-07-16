"""
Pattern 4 — Workflow Agent: Sequential Pipeline (with Opik tracing)
--------------------------------------------------------------------
Same SequentialAgent pipeline as 03_workflow_agent.py, but now every
LLM call is captured in Opik so you can inspect the full trace.

What Opik adds:
  - One trace per run, with two child spans: ConceptAnalyser → ExamGenerator
  - Click ConceptAnalyser's output span to see exactly what text flows
    into ExamGenerator as input — the automatic handoff made visible.
  - Token counts, latency, and model name recorded per span.

How tracing is wired:
  build_runner() in agent_config wraps the agent with OpikTracer and
  calls track_adk_agent_recursive — no changes needed to the agent code.

Open your Opik dashboard after running this script and look for the
'workflow_agent_opik' project to see the trace.
"""

import asyncio
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from google.adk.agents import SequentialAgent, LlmAgent

from agent_config import get_model, build_runner, run_agent


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

# build_runner wires OpikTracer — this is the only difference from 03_workflow_agent.py
runner, session_service = build_runner(pipeline, app_name="workflow-agent-opik")


async def generate_exam(topic: str) -> str:
    return await run_agent(runner, session_service, topic, app_name="workflow-agent-opik")


if __name__ == "__main__":
    topic = "Binary Search Trees — insertion, deletion, and traversal algorithms"
    print(f"Topic: {topic}\n")
    print("=" * 60)
    print(asyncio.run(generate_exam(topic)))

    print("\n[OPIK] Open the 'workflow_agent_opik' project in your Opik dashboard.")
    print("       Expand the SequentialAgent span → ConceptAnalyser output flows")
    print("       directly into ExamGenerator as input — visible in the trace.")
