import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from google.adk.agents import LoopAgent, LlmAgent
from agent_config import ProxyGemini, GEMINI_MODEL, setup_opik
from opik.integrations.adk import OpikTracer, track_adk_agent_recursive

setup_opik()

improver = LlmAgent(
    name="EssayImprover",
    model=ProxyGemini(model=GEMINI_MODEL),
    instruction="You are an academic writing tutor. "
                "Improve the essay: add specific facts, strengthen arguments, "
                "improve vocabulary. Return only the improved essay.",
    description="Improves essay quality.",
)

evaluator = LlmAgent(
    name="QualityEvaluator",
    model=ProxyGemini(model=GEMINI_MODEL),
    instruction="You are an essay evaluator. Score the essay 1-10 and respond in "
                "EXACTLY this format:\n"
                "SCORE: X\n"
                "FEEDBACK: one sentence\n"
                "CONTINUE: YES or NO  (YES if score < 8, NO if score >= 8)",
    description="Scores the essay and decides whether to loop.",
)

root_agent = LoopAgent(
    name="EssayRefinementLoop",
    description="Hi! I am the GAT Lab Report Improver. Paste a weak lab report and I will automatically improve it until it meets the required standard (score >= 8/10).",
    sub_agents=[improver, evaluator],
    max_iterations=4,
)

_tracer = OpikTracer()
track_adk_agent_recursive(root_agent, _tracer)
