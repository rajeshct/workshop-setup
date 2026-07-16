import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from google.adk.agents import LlmAgent
from agent_config import ProxyGemini, GEMINI_MODEL, setup_opik
from opik.integrations.adk import OpikTracer, track_adk_agent_recursive

setup_opik()

# Pattern 1A — single turn, no memory between sessions
root_agent = LlmAgent(
    name="HelloAgent",
    model=ProxyGemini(model=GEMINI_MODEL),
    instruction="When the conversation starts, greet the user with: 'Hi! I am the GAT Assistant. How can I help you today?' Then proceed to answer their questions. You are a helpful assistant for engineering students and faculty. "
                "Answer questions clearly and concisely.",
    description="Pattern 1A — Ask me any question. One question, one answer.",
)

_tracer = OpikTracer()
track_adk_agent_recursive(root_agent, _tracer)
