"""
Pattern 2 — Tool Agent: Live Website Fetch
-------------------------------------------
New concept: Tool use — give the agent access to live data.

A tool is any plain Python function. ADK reads its name, docstring, and
type hints to auto-generate the function-call schema for the LLM.
No @tool decorator or subclassing required.

How tool calling works:
  1. LLM decides to call a tool → returns a FunctionCall with name + args
  2. ADK executes the Python function
  3. ADK feeds the result back to the LLM as a FunctionResponse
  4. LLM uses the result to compose its final answer

Note — pre-fetching pattern used here:
  The local Gemini proxy does not support tool declarations in API requests.
  So fetch_college_info() is called in Python first and the result is injected
  into the message before sending to the LLM. This is a valid production
  pattern too — it gives you more control over what data is sent.

Security — Input Validation:
  Validate input before fetching any external URL. Whitelist allowed pages
  and domains — a malicious user could pass unexpected values to redirect
  the tool to unintended endpoints.
"""

import asyncio
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import requests
from html.parser import HTMLParser

from google.adk.agents import LlmAgent

from agent_config import get_model, build_runner_no_opik, run_agent


# --- Tool ---
def fetch_college_info(page: str = "contact") -> str:
    """Fetch information from the Global Academy of Technology (GAT) website."""
    urls = {"contact": "https://www.gat.ac.in/contact-us.html"}
    url = urls.get(page, urls["contact"])
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; educational-demo/1.0)"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        class TextExtractor(HTMLParser):
            def __init__(self):
                super().__init__()
                self.text_parts = []
                self._skip = False
            def handle_starttag(self, tag, attrs):
                if tag in ("script", "style", "nav", "header", "footer"):
                    self._skip = True
            def handle_endtag(self, tag):
                if tag in ("script", "style", "nav", "header", "footer"):
                    self._skip = False
            def handle_data(self, data):
                if not self._skip:
                    cleaned = data.strip()
                    if cleaned:
                        self.text_parts.append(cleaned)

        parser = TextExtractor()
        parser.feed(response.text)
        text = "\n".join(parser.text_parts)
        return text[:2000] if text else "No content found."
    except Exception as e:
        return f"Failed to fetch page: {e}"


# --- Agent ---
agent = LlmAgent(
    name="GATInfoAgent",
    model=get_model(),
    instruction="You are a helpful information assistant for Global Academy of Technology (GAT), "
                "Bengaluru. The user's message contains a question followed by live data fetched "
                "from the GAT website. Answer the question using that data. Be concise and helpful.",
    description="Answers questions about GAT college using live data from the website.",
)

runner, session_service = build_runner_no_opik(agent, app_name="tool-agent")


# --- Entrypoint ---
async def ask(question: str) -> str:
    college_data = fetch_college_info("contact")
    enriched = (
        f"Question: {question}\n\n"
        f"Live data from GAT website (gat.ac.in):\n{college_data}\n\n"
        f"Please answer the question using the data above."
    )
    return await run_agent(runner, session_service, enriched, app_name="tool-agent")


if __name__ == "__main__":
    question = "What is the contact number and email address for GAT admissions?"
    print(f"Question: {question}\n")
    print("=" * 60)
    print(asyncio.run(ask(question)))
