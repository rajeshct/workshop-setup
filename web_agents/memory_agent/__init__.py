import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from google.adk.agents import LlmAgent
from agent_config import ProxyGemini, GEMINI_MODEL

root_agent = LlmAgent(
    name="StudentProgressAdvisor",
    model=ProxyGemini(model=GEMINI_MODEL),
    instruction="You are an academic advisor at GAT helping faculty track student progress. "
                "Remember everything the faculty tells you about a student in this session — "
                "scores, struggles, improvements, and observations. "
                "Use the full conversation history to give personalised, specific recommendations. "
                "When asked for advice, synthesise everything you know about the student.",
    description="Pattern 1B — I remember our full conversation. Try turn 1: 'Student Priya scored 4/10 on Arrays. She struggles with pointer arithmetic.' Turn 2: 'She scored 7/10 on Linked Lists but struggled with reversal.' Turn 3: 'What 2-week study plan do you recommend for Priya?'",
)
