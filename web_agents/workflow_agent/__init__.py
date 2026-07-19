import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from google.adk.agents import SequentialAgent, LlmAgent
from agent_config import ProxyGemini, GEMINI_MODEL

concept_analyser = LlmAgent(
    name="ConceptAnalyser",
    model=ProxyGemini(model=GEMINI_MODEL),
    instruction="""You are a senior engineering professor and curriculum expert.
    Given a topic, identify:
    - 3-4 core concepts students must understand
    - Common misconceptions or tricky areas
    - What easy, medium, and hard questions would test for this topic
    Be concise — this output feeds directly into the exam generator.""",
    description="Analyses a topic and identifies key concepts and difficulty levels.",
)

exam_generator = LlmAgent(
    name="ExamGenerator",
    model=ProxyGemini(model=GEMINI_MODEL),
    instruction="""You are an experienced engineering exam setter.
    Given a concept analysis of a topic, generate a complete exam paper with:

    ## Multiple Choice Questions (5 questions)
    - 2 easy, 2 medium, 1 hard
    - 4 options each (A/B/C/D)
    - Mark the correct answer

    ## Descriptive Questions (2 questions)
    - 1 medium (5 marks): tests understanding
    - 1 hard (10 marks): tests application/analysis

    ## Answer Key
    - MCQ answers with brief explanation
    - Descriptive answer guidelines (key points to award marks)

    Format it cleanly — ready to print and distribute.""",
    description="Generates a complete exam paper with answer keys from concept analysis.",
)

root_agent = SequentialAgent(
    name="ExamPaperPipeline",
    description="Pattern 3 — I generate a complete exam paper from a topic. Try: 'Binary Search Trees — insertion, deletion, and traversal algorithms'",
    sub_agents=[concept_analyser, exam_generator],
)
