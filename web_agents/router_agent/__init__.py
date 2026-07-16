import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from google.adk.agents import LlmAgent
from agent_config import ProxyGemini, GEMINI_MODEL, setup_opik
from opik.integrations.adk import OpikTracer, track_adk_agent_recursive

setup_opik()

maths_expert = LlmAgent(
    name="MathsExpert",
    model=ProxyGemini(model=GEMINI_MODEL),
    instruction="You are a university Maths professor. "
                "Answer maths questions with clear step-by-step workings.",
    description="Handles maths questions: algebra, calculus, statistics.",
)

science_expert = LlmAgent(
    name="ScienceExpert",
    model=ProxyGemini(model=GEMINI_MODEL),
    instruction="You are a university Science professor covering Physics, Chemistry, and Biology. "
                "Answer with accurate explanations and real-world examples.",
    description="Handles science questions: physics, chemistry, biology.",
)

general_advisor = LlmAgent(
    name="GeneralAdvisor",
    model=ProxyGemini(model=GEMINI_MODEL),
    instruction="You are a friendly academic advisor. "
                "Help with study tips, career guidance, and general questions.",
    description="Handles general academic queries.",
)

root_agent = LlmAgent(
    name="HelpDesk",
    model=ProxyGemini(model=GEMINI_MODEL),
    instruction="When the conversation starts, greet the user with: 'Hi! I am the GAT Help Desk. How can I help you today?' "
                "Then route questions to the right specialist:\n"
                "- MathsExpert   → maths, calculus, statistics\n"
                "- ScienceExpert → physics, chemistry, biology\n"
                "- GeneralAdvisor → study tips, career, general help\n"
                "Do not answer yourself — always delegate.",
    description="Ask me any academic question — I will route you to the right specialist.",
    sub_agents=[maths_expert, science_expert, general_advisor],
)

_tracer = OpikTracer()
track_adk_agent_recursive(root_agent, _tracer)
