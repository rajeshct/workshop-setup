"""
Pattern 5 — Parallel Agent: Bulk Grader
-----------------------------------------
New concept: ParallelAgent — run all agents simultaneously.

ParallelAgent launches all child agents concurrently using Python asyncio.
Total time = slowest single grader, not the sum of all graders.
5 students each taking 3 seconds = ~3 seconds total, not 15.

How parallelism works:
  ParallelAgent uses asyncio.gather() to schedule all child agents at once.
  Each child agent gets its own copy of the session state. Results are
  collected when all children complete. If one grader fails, the others
  still complete — failures are isolated per student.

Each grader is a separate LlmAgent with the same rubric but a different
student's answer embedded in its instruction.

What OPIK shows:
  All 5 grader spans have the SAME start timestamp — visual proof of
  parallelism. Compare this to a sequential run where each span starts
  only after the previous finishes. Each span contains the individual
  grade, strengths, and feedback for that student.

Security — Output Validation:
  LLM grades are drafts for human review — not automated final grades.
  Do not write scores directly to a grade book without faculty review.
  LLM grading can be inconsistent or biased across runs.
"""

import asyncio
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from opik import track
from google.adk.agents import ParallelAgent, LlmAgent
from google.genai import types

from agent_config import get_model, setup_opik, build_runner

setup_opik()

# --- Student Submissions ---
# Topic: "Explain the difference between BFS and DFS with time complexity"

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


# Each student gets a dedicated LlmAgent with the same rubric
# The student's answer is embedded in the instruction at agent creation time
def make_grader(name: str, answer: str) -> LlmAgent:
    return LlmAgent(
        name=f"Grader_{name}",
        model=get_model(),
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


graders = [make_grader(name, answer) for name, answer in SUBMISSIONS]

# ParallelAgent uses asyncio.gather() internally — all graders start at once
parallel_grader = ParallelAgent(
    name="ParallelGrader",
    sub_agents=graders,
)

runner, session_service = build_runner(parallel_grader, app_name="parallel-agent")


@track(name="parallel_agent", entrypoint=True)
async def grade_all() -> str:
    session = await session_service.create_session(
        app_name="parallel-agent", user_id="professor-1"
    )
    results = []
    async for event in runner.run_async(
        user_id="professor-1",
        session_id=session.id,
        new_message=types.Content(
            role="user", parts=[types.Part(text="Grade all submitted assignments.")]
        ),
    ):
        if event.is_final_response() and event.content and event.content.parts:
            results.append(event.content.parts[0].text)
    return "\n\n---\n\n".join(results)


if __name__ == "__main__":
    print("Grading 5 student submissions IN PARALLEL...")
    print("Try this with an AI assistant — you would paste each answer one by one.")
    print("This agent grades all 5 simultaneously.\n")
    print("=" * 60)
    print(asyncio.run(grade_all()))
    import opik; opik.flush_tracker()
    print("\n[OPIK] Open the 'parallel_agent' trace → check all 5 grader spans")
    print("       All 5 should show the same start timestamp — proof of parallelism")
