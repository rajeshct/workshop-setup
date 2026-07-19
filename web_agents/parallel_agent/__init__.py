import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from google.adk.agents import ParallelAgent, LlmAgent
from agent_config import ProxyGemini, GEMINI_MODEL, setup_opik
from opik.integrations.adk import OpikTracer, track_adk_agent_recursive

setup_opik()

SUBMISSIONS = [
    ("Arun",
     "BFS uses a queue and explores level by level. DFS uses a stack and goes deep first. "
     "BFS time complexity is O(V+E), DFS is also O(V+E) where V is vertices and E is edges. "
     "BFS is good for shortest path, DFS for detecting cycles."),
    ("Priya",
     "BFS stands for Breadth First Search. It goes wide. DFS is Depth First Search, it goes deep. "
     "They are both graph algorithms. BFS uses queue data structure and DFS uses stack."),
    ("Rahul",
     "BFS: visits all neighbours before going deeper. Uses queue. Time: O(V+E), Space: O(V). "
     "DFS: goes as deep as possible before backtracking. Uses stack (or recursion). Time: O(V+E), Space: O(h) where h is max depth. "
     "BFS → shortest path in unweighted graphs. DFS → topological sort, cycle detection, connected components."),
    ("Sneha",
     "Both BFS and DFS are graph traversal methods. BFS explores neighbours first using a queue "
     "with O(V+E) complexity. DFS explores depth-first using a stack with O(V+E) complexity. "
     "BFS finds shortest paths while DFS is used in maze solving."),
    ("Vikram",
     "DFS goes deep using recursion. BFS goes wide using a queue. "
     "Time complexity is same for both. Used in different scenarios."),
]

graders = [
    LlmAgent(
        name=f"Grader_{name}",
        model=ProxyGemini(model=GEMINI_MODEL),
        instruction=f"""You are grading a student answer for a CS exam.

Question: Explain the difference between BFS and DFS with time complexity.

Student: {name}
Answer: {answer}

Grade against this rubric (10 marks total):
- Correctness of BFS explanation (2 marks)
- Correctness of DFS explanation (2 marks)
- Time complexity stated correctly (2 marks)
- Use cases mentioned (2 marks)
- Clarity and completeness (2 marks)

Respond in this format:
**{name}**: X/10
- Strengths: ...
- Improvements: ...""",
        description=f"Grades {name}'s BFS/DFS answer.",
    )
    for name, answer in SUBMISSIONS
]

root_agent = ParallelAgent(
    name="ParallelGrader",
    description="Pattern 6 — I grade all 5 student submissions simultaneously. Just send any message to trigger grading. Try: 'Grade all submitted assignments.'",
    sub_agents=graders,
)

_tracer = OpikTracer()
track_adk_agent_recursive(root_agent, _tracer)
