import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from google.adk.agents import LoopAgent, LlmAgent
from agent_config import ProxyGemini, GEMINI_MODEL, setup_opik
from opik.integrations.adk import OpikTracer, track_adk_agent_recursive

setup_opik()

report_improver = LlmAgent(
    name="ReportImprover",
    model=ProxyGemini(model=GEMINI_MODEL),
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
    model=ProxyGemini(model=GEMINI_MODEL),
    instruction="""You are a lab report examiner at an engineering college.
    Evaluate the report and respond in EXACTLY this format:
    SCORE: X
    MISSING_SECTIONS: list any of (Aim/Apparatus/Theory/Procedure/Observations/Conclusion) that are missing or incomplete
    FEEDBACK: one sentence on what needs most improvement
    CONTINUE: YES or NO  (YES if score < 8 or any section is missing, NO if score >= 8 and all sections present)""",
    description="Evaluates lab report completeness and quality, decides whether to loop.",
)

root_agent = LoopAgent(
    name="LabReportRefinementLoop",
    description="Pattern 7 — I improve a lab report automatically until score >= 8/10. Paste the weak report below:\n\nLab Experiment: Ohm's Law\n\nWe did an experiment with a resistor and battery. We connected them with wires. We measured voltage and current. The results showed they are related. Ohm's law says V = IR. Our experiment proved this is correct.",
    sub_agents=[report_improver, report_evaluator],
    max_iterations=4,
)

_tracer = OpikTracer()
track_adk_agent_recursive(root_agent, _tracer)
