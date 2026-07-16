import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from google.adk.agents import LlmAgent
from agent_config import ProxyGemini, GEMINI_MODEL

root_agent = LlmAgent(
    name="HelloAgent",
    model=ProxyGemini(model=GEMINI_MODEL),
    instruction="You are a helpful assistant for engineering students and faculty. "
                "Answer questions clearly and concisely.",
    description="Pattern 1A — Ask me any question. Try: 'What are good learning outcomes for a DSA course?'",
)
