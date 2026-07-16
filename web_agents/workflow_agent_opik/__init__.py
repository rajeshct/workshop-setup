import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from google.adk.agents import SequentialAgent, LlmAgent
from agent_config import ProxyGemini, GEMINI_MODEL, setup_opik, load_config
from opik.integrations.adk import OpikTracer, track_adk_agent_recursive

setup_opik()

cfg    = load_config("03_workflow_agent_config.yaml")
r_cfg  = cfg["agents"]["content_researcher"]
lp_cfg = cfg["agents"]["lecture_planner"]

researcher = LlmAgent(
    name="ContentResearcher",
    model=ProxyGemini(model=GEMINI_MODEL),
    instruction=r_cfg["instruction"],
    description=r_cfg["description"],
)

lecture_planner = LlmAgent(
    name="LecturePlanner",
    model=ProxyGemini(model=GEMINI_MODEL),
    instruction=lp_cfg["instruction"],
    description=lp_cfg["description"],
)

root_agent = SequentialAgent(
    name="LecturePrepPipeline",
    description="Hi! I am the Lecture Prep Pipeline. Enter an engineering topic and I will research it and generate a structured lecture plan.",
    sub_agents=[researcher, lecture_planner],
)

_tracer = OpikTracer()
track_adk_agent_recursive(root_agent, _tracer)
