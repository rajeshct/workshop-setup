import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from google.adk.agents import ParallelAgent, LlmAgent
from agent_config import ProxyGemini, GEMINI_MODEL, setup_opik
from opik.integrations.adk import OpikTracer, track_adk_agent_recursive

setup_opik()

ASSIGNMENTS = [
    ("Alice", "The water cycle involves evaporation, condensation, and precipitation. "
              "Water evaporates from oceans due to solar energy, forms clouds, and falls as rain."),
    ("Bob",   "Water goes up and comes back down. The sun heats it and clouds form. It rains. Repeats."),
    ("Carol", "The hydrological cycle is driven by solar radiation. Key stages: evapotranspiration, "
              "condensation, precipitation, surface runoff, and groundwater recharge."),
]

graders = [
    LlmAgent(
        name=f"Grader_{name}",
        model=ProxyGemini(model=GEMINI_MODEL),
        instruction=f"You are a professor grading a student assignment.\n\n"
                    f"Student: {name}\nAnswer: {answer}\n\n"
                    f"Give a score out of 10, two strengths, and one improvement point.",
        description=f"Grades {name}'s assignment.",
    )
    for name, answer in ASSIGNMENTS
]

root_agent = ParallelAgent(
    name="ParallelGrader",
    description="Hi! I am the GAT Parallel Grader. Send any message to trigger simultaneous grading of all pre-loaded student assignments.",
    sub_agents=graders,
)

_tracer = OpikTracer()
track_adk_agent_recursive(root_agent, _tracer)
