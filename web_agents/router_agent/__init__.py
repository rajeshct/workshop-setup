import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from google.adk.agents import LlmAgent
from agent_config import ProxyGemini, GEMINI_MODEL, setup_opik
from opik.integrations.adk import OpikTracer, track_adk_agent_recursive

setup_opik()

cse_expert = LlmAgent(
    name="CSE_Expert",
    model=ProxyGemini(model=GEMINI_MODEL),
    instruction="You are a Computer Science professor at GAT. "
                "Answer questions on algorithms, data structures, programming, "
                "operating systems, computer networks, databases, and AI/ML. "
                "Give precise technical answers with examples.",
    description="Handles CS questions: algorithms, programming, OS, networks, AI/ML.",
)

ece_expert = LlmAgent(
    name="ECE_Expert",
    model=ProxyGemini(model=GEMINI_MODEL),
    instruction="You are an Electronics & Communication professor at GAT. "
                "Answer questions on circuits, signals, embedded systems, VLSI, "
                "microprocessors, communication systems, and control systems. "
                "Use diagrams described in text where helpful.",
    description="Handles ECE questions: circuits, signals, VLSI, embedded systems.",
)

mechanical_expert = LlmAgent(
    name="Mechanical_Expert",
    model=ProxyGemini(model=GEMINI_MODEL),
    instruction="You are a Mechanical Engineering professor at GAT. "
                "Answer questions on thermodynamics, fluid mechanics, machine design, "
                "manufacturing processes, CAD/CAM, and heat transfer. "
                "Include relevant formulas and real-world applications.",
    description="Handles Mechanical questions: thermodynamics, fluid mechanics, design.",
)

civil_expert = LlmAgent(
    name="Civil_Expert",
    model=ProxyGemini(model=GEMINI_MODEL),
    instruction="You are a Civil Engineering professor at GAT. "
                "Answer questions on structural analysis, concrete technology, "
                "surveying, geotechnical engineering, transportation, and water resources. "
                "Refer to IS codes where relevant.",
    description="Handles Civil questions: structures, concrete, surveying, geotechnical.",
)

root_agent = LlmAgent(
    name="GAT_HelpDesk",
    model=ProxyGemini(model=GEMINI_MODEL),
    instruction="You are the GAT (Global Academy of Technology) Student Help Desk. "
                "Read the student's question and route it to the right department:\n"
                "- CSE_Expert      → programming, algorithms, OS, networks, AI/ML\n"
                "- ECE_Expert      → circuits, electronics, signals, embedded, VLSI\n"
                "- Mechanical_Expert → thermodynamics, fluids, machines, manufacturing\n"
                "- Civil_Expert    → structures, concrete, surveying, geotechnical\n"
                "Do not answer yourself — always delegate to the right specialist.",
    description="Pattern 5 — I route your question to the right department. Try: 'What is the time complexity of quicksort?' or 'How does a JK flip-flop differ from a D flip-flop?' or 'Explain the Rankine cycle.' or 'What is the difference between one-way and two-way slab design?'",
    sub_agents=[cse_expert, ece_expert, mechanical_expert, civil_expert],
)

_tracer = OpikTracer()
track_adk_agent_recursive(root_agent, _tracer)
