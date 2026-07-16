import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from google.adk.agents import LlmAgent
from agent_config import ProxyGemini, GEMINI_MODEL

# Pattern 1B — same LlmAgent as hello_agent but session memory is maintained
# across the conversation by ADK Web UI automatically
root_agent = LlmAgent(
    name="StudentProgressAdvisor",
    model=ProxyGemini(model=GEMINI_MODEL),
    instruction="When the conversation starts, greet the user with: 'Hi! I am the GAT Assistant. How can I help you today?' Then proceed to answer their questions. You are an academic advisor at GAT helping faculty track student progress. "
                "Remember everything the faculty tells you about a student in this conversation "
                "and use that context in every response.",
    description="Pattern 1B — I remember our full conversation. Tell me about a student's progress across multiple turns.",
)
