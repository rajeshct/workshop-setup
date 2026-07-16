"""
Pattern 6 — Loop Agent: Lab Report Evaluator
----------------------------------------------
New concept: LoopAgent — repeat until exit condition met.

LoopAgent runs its child agents in sequence every iteration.
It stops when: (a) an agent signals exit via CONTINUE: NO, or
               (b) max_iterations is reached (hard safety cap).

How the exit condition works:
  The ReportEvaluator outputs CONTINUE: YES or CONTINUE: NO.
  ADK checks this output — when it detects NO, it raises an escalation
  signal and the loop exits. max_iterations=4 is the hard cap regardless,
  preventing runaway API costs if the condition is never reached.

Why strict output format matters:
  "CONTINUE: NO" must match exactly. Wrong case, missing space, or extra
  text can cause exit detection to fail and the loop to continue longer
  than needed. Always test the exit condition before deploying.

What OPIK shows:
  Each iteration appears as a group of spans. Watch the score climb across
  iterations — CONTINUE: YES then YES then NO. The exact score and missing
  sections are visible in each ReportEvaluator span's output. Total token
  cost across all iterations is visible at the trace level.

Security — Runaway Loops:
  Always set max_iterations as a hard safety cap. An uncapped loop hitting
  the LLM repeatedly consumes tokens and API cost with every iteration.
  Use strict CONTINUE: YES/NO format so exit detection is reliable.
"""

import asyncio
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import re
from opik import track
from google.adk.agents import LoopAgent, LlmAgent
from google.genai import types

from agent_config import get_model, setup_opik, build_runner

setup_opik()

# --- Weak student lab report ---

WEAK_REPORT = """
Lab Experiment: Ohm's Law

We did an experiment with a resistor and battery. We connected them with wires.
We measured voltage and current. The results showed they are related.
Ohm's law says V = IR. Our experiment proved this is correct.
"""

# --- Agents ---
# ReportImprover: rewrites the report adding missing sections and improving language
# ReportEvaluator: scores 1-10, checks sections, outputs CONTINUE: YES/NO
# The evaluator's output drives the loop — must use exact format for reliable exit detection

report_improver = LlmAgent(
    name="ReportImprover",
    model=get_model(),
    instruction="""You are an engineering lab report writing coach.
    Improve the lab report to include all required sections:
    - Aim: clear objective of the experiment
    - Apparatus: list of equipment used with specifications
    - Theory: explain Ohm's Law (V=IR) with relevant formulas
    - Procedure: step-by-step method followed
    - Observations: table with voltage and current readings
    - Conclusion: what was verified and sources of error

    Improve the scientific language and technical accuracy.
    Return the complete improved report.""",
    description="Improves lab report quality and completeness.",
)

report_evaluator = LlmAgent(
    name="ReportEvaluator",
    model=get_model(),
    instruction="""You are a lab report examiner at an engineering college.
    Evaluate the report and respond in EXACTLY this format:
    SCORE: X
    MISSING_SECTIONS: list any of (Aim/Apparatus/Theory/Procedure/Observations/Conclusion) that are missing or incomplete
    FEEDBACK: one sentence on what needs most improvement
    CONTINUE: YES or NO  (YES if score < 8 or any section is missing, NO if score >= 8 and all sections present)""",
    description="Evaluates lab report completeness and quality, decides whether to loop.",
)

loop_agent = LoopAgent(
    name="LabReportRefinementLoop",
    sub_agents=[report_improver, report_evaluator],
    max_iterations=4,   # hard safety cap — stops even if CONTINUE: NO never fires
)

runner, session_service = build_runner(loop_agent, app_name="loop-agent")


@track(name="loop_agent", entrypoint=True)
async def refine(report: str) -> str:
    session = await session_service.create_session(
        app_name="loop-agent", user_id="student-1"
    )
    final_text = ""
    iteration = 0
    async for event in runner.run_async(
        user_id="student-1",
        session_id=session.id,
        new_message=types.Content(role="user", parts=[types.Part(text=report)]),
    ):
        if event.content and event.content.parts:
            text = event.content.parts[0].text
            if "Evaluator" in str(event.author):
                iteration += 1
                score = re.search(r"SCORE:\s*(\d+)", text)
                missing = re.search(r"MISSING_SECTIONS:\s*(.+)", text)
                print(f"  Iteration {iteration}: Score = {score.group(1) if score else '?'}/10 "
                      f"| Missing: {missing.group(1).strip() if missing else 'none'}")
            if event.is_final_response():
                final_text = text
    return final_text


if __name__ == "__main__":
    print("Original weak lab report:")
    print("-" * 40)
    print(WEAK_REPORT)
    print("\nImproving automatically until all sections present and score >= 8/10...")
    print("Try this with an AI assistant — you would manually paste and re-paste each iteration.\n")
    print("=" * 60)
    result = asyncio.run(refine(WEAK_REPORT))
    print("\nFinal Report:")
    print("-" * 40)
    print(result)
    import opik; opik.flush_tracker()
    print("\n[OPIK] Open the 'loop_agent' trace → see iteration span groups")
    print("       Each ReportEvaluator span shows the score and CONTINUE decision")
    print("       Total cost across all iterations visible at the trace level")
